"""Audit exact cosine-band packets without modifying existing simulations.

Units: a = hbar = Jx = 1. The two-dimensional Hamiltonian and initial Gaussian
separate exactly. Large 1D periodic boxes keep the full physical trajectory
inside the box; representative products are checked against the project 2D FFT.
"""
from pathlib import Path
import csv
import json
import sys

import numpy as np
from scipy.optimize import brentq
from scipy.special import roots_hermitenorm
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT))
import common

CENTERS = {"A": (.7, .7), "B": (np.pi / 2, .7),
           "C": (np.pi / 2, np.pi / 2)}
COLORS = {"A": "#246B9A", "B": "#CF7048", "C": "#27816E"}


def dump(name, value):
    def convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.generic):
            return obj.item()
        raise TypeError(type(obj).__name__)
    (OUT / name).write_text(json.dumps(value, indent=2, default=convert),
                           encoding="utf-8")


def csv_rows(name, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class Packet:
    def __init__(self, sigma, q0, coupling=1., n=16384):
        self.n = n
        self.sigma = sigma
        self.q0 = q0
        self.j = coupling
        self.x = np.arange(n) - n // 2
        self.q = 2 * np.pi * np.fft.fftfreq(n)
        self.initial = np.exp(-self.x**2 / (4*sigma**2) + 1j*q0*self.x)
        self.initial /= np.linalg.norm(self.initial)
        self.a = np.fft.fft(self.initial)
        self.power = np.abs(self.a)**2 / n
        self.energy = coupling * (1 - np.cos(self.q))
        self.v = coupling * np.sin(self.q)
        self.mean_v = float(np.sum(self.power*self.v))
        dv = self.v - self.mean_v
        self.var_v = float(np.sum(self.power*dv**2))
        self.kappa3_v = float(np.sum(self.power*dv**3))
        self.kappa4_v = float(np.sum(self.power*dv**4) - 3*self.var_v**2)
        residual = self.energy - self.mean_v*self.q
        self.residual = residual - np.sum(self.power*residual)
        self.p0 = float(np.max(np.abs(self.initial)**2))

    def fidelity(self, t):
        return float(abs(np.sum(self.power*np.exp(-1j*self.residual*t)))**2)

    def state(self, t):
        return np.fft.ifft(self.a*np.exp(-1j*self.energy*t))

    def row(self, t, return_state=False):
        psi = self.state(t)
        p = np.abs(psi)**2
        norm = float(p.sum())
        mean = float(np.sum(p*self.x) / norm)
        z = self.x - mean
        m2 = float(np.sum(p*z**2) / norm)
        m3 = float(np.sum(p*z**3) / norm)
        m4 = float(np.sum(p*z**4) / norm)
        reference = np.fft.ifft(self.a*np.exp(-1j*self.mean_v*self.q*t))
        density_overlap = float(np.sum(np.abs(psi)*np.abs(reference))**2)
        # Symmetrically exclude sites within tolerance of the hard cutoff.
        # Without this, a roundoff-sized centroid offset assigns x=+/-2*sigma
        # inconsistently even for the exactly symmetric initial Gaussian.
        cutoff_tol = 1e-9
        left = float(p[z < -2*self.sigma-cutoff_tol].sum())
        right = float(p[z > 2*self.sigma+cutoff_tol].sum())
        row = dict(
            t=float(t), norm=norm, centroid=mean, width=np.sqrt(m2),
            m3=m3, skewness=m3/m2**1.5,
            kappa4=m4 - 3*m2**2, excess_kurtosis=m4/m2**2 - 3,
            peak=float(p.max()), peak_over_initial=float(p.max()/self.p0),
            left_tail_2_initial_sigma=left,
            right_tail_2_initial_sigma=right,
            tail_asymmetry=(right-left)/(right+left) if right+left else 0.,
            fidelity=self.fidelity(t), density_overlap=density_overlap,
            edge_mass=float(p[:32].sum() + p[-32:].sum()),
            mean_error=mean-self.mean_v*t,
            variance_identity_error=m2-self.sigma**2-t*t*self.var_v,
        )
        if return_state:
            return row, psi
        return row


def gaussian_velocity_moments(sigma, q0, coupling=1.):
    """Independent continuous-Gaussian spectral moments, valid here to roundoff."""
    d2 = 1/(4*sigma*sigma)
    mu = coupling*np.sin(q0)*np.exp(-d2/2)
    s2 = coupling**2*(1-np.cos(2*q0)*np.exp(-2*d2))/2
    s3 = coupling**3*(3*np.sin(q0)*np.exp(-d2/2)
                      - np.sin(3*q0)*np.exp(-9*d2/2))/4
    s4 = coupling**4*(3 - 4*np.cos(2*q0)*np.exp(-2*d2)
                      + np.cos(4*q0)*np.exp(-8*d2))/8
    var = s2-mu*mu
    k3 = s3-3*mu*s2+2*mu**3
    k4 = s4-4*mu*s3+6*mu*mu*s2-3*mu**4-3*var*var
    return dict(mean=mu, variance=var, kappa3=k3, kappa4=k4)


def first_crossing(fidelity, threshold, sigma):
    grid = np.geomspace(.01, 100*sigma**3, 450)
    old_t, old_f = 0., 1.
    for t in grid:
        value = fidelity(t)
        if value <= threshold:
            return float(brentq(lambda z: fidelity(z)-threshold, old_t, t,
                                xtol=1e-8, rtol=1e-12))
        old_t, old_f = t, value
    raise RuntimeError("No crossing within the stated search horizon")


def lifetime_study():
    records = []
    convergence = []
    for sigma in [4., 6., 8., 12.]:
        packets = {q: Packet(sigma, q, n=4096) for q in [.7, np.pi/2]}
        for name, centers in CENTERS.items():
            px, py = [packets[q] for q in centers]
            fidelity = lambda t: px.fidelity(t)*py.fidelity(t)
            record = dict(case=name, sigma_a=sigma, eta=1.)
            for threshold in [.9, .5]:
                key = "time_F_" + str(threshold)
                record[key] = first_crossing(fidelity, threshold, sigma)
            record["time_first_axis_width_doubles"] = (
                np.sqrt(3)*sigma / np.sqrt(max(px.var_v, py.var_v)))
            record["mean_speed"] = float(np.hypot(px.mean_v, py.mean_v))
            record["distance_at_F_0.9"] = record["mean_speed"]*record["time_F_0.9"]
            record["distance_at_F_0.5"] = record["mean_speed"]*record["time_F_0.5"]
            records.append(record)
            # This checks spectral resolution independently of propagation-box size.
            px2 = Packet(sigma, centers[0], n=8192)
            py2 = Packet(sigma, centers[1], n=8192)
            for threshold in [.9, .5]:
                t = record["time_F_"+str(threshold)]
                convergence.append(dict(
                    case=name, sigma_a=sigma, threshold=threshold, time=t,
                    spectral_N4096_vs8192_error=abs(
                        px2.fidelity(t)*py2.fidelity(t)-threshold)))
    fits = {}
    for name in CENTERS:
        rows = [r for r in records if r["case"] == name]
        fits[name] = {}
        for key in ["time_F_0.9", "time_F_0.5",
                    "time_first_axis_width_doubles"]:
            fits[name][key] = float(np.polyfit(
                np.log([r["sigma_a"] for r in rows]),
                np.log([r[key] for r in rows]), 1)[0])
    quadrature_checks = []
    for record in records:
        if record["case"] != "C":
            continue
        sigma = record["sigma_a"]
        d = 1/(2*sigma)
        t = record["time_F_0.5"]
        quadratures = []
        for order in [640, 1280]:
            nodes, weights = roots_hermitenorm(order)
            q = np.pi/2 + d*nodes
            velocity = np.exp(-d*d/2)
            residual = (1-np.cos(q))-velocity*q
            amplitude = np.sum(weights*np.exp(-1j*residual*t))/np.sqrt(2*np.pi)
            quadratures.append(float(abs(amplitude)**4))
        quadrature_checks.append(dict(
            sigma_a=sigma, time=t, threshold=.5, orders=[640, 1280],
            fidelities=quadratures,
            order_difference=abs(quadratures[1]-quadratures[0]),
            difference_from_exact_discrete_spectrum=abs(quadratures[1]-.5)))
    return records, fits, convergence, quadrature_checks


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sigma = 6.
    n = 16384
    special = [0, 180, 360, 720, 864, 869.2614001, 1080, 1440,
               1728, 2160, 2880, 3691.0589224, 4320]
    times = np.unique(np.r_[np.linspace(0, 180, 61),
                            np.linspace(180, 4320, 231), special])
    packets = {(q, j): Packet(sigma, q, j, n)
               for q in [.7, np.pi/2] for j in [1., .3]}
    one_d = {}
    all_rows = {}
    diagnostics = []
    for (q, j), packet in packets.items():
        rows = [packet.row(float(t)) for t in times]
        one_d[(q, j)] = rows
        independent = gaussian_velocity_moments(sigma, q, j)
        diagnostics.append(dict(
            q0=q, coupling=j,
            gaussian_mean_velocity_error=abs(packet.mean_v-independent["mean"]),
            gaussian_velocity_variance_error=abs(packet.var_v-independent["variance"]),
            max_norm_error=max(abs(r["norm"]-1) for r in rows),
            max_centroid_error=max(abs(r["mean_error"]) for r in rows),
            max_variance_identity_error=max(abs(r["variance_identity_error"]) for r in rows),
            max_edge_mass=max(r["edge_mass"] for r in rows)))

    for eta in [1., .3]:
        for name, (qx, qy) in CENTERS.items():
            key = f"{name}_eta{eta:g}"
            rows = []
            for rx, ry in zip(one_d[(qx, 1.)], one_d[(qy, eta)]):
                row = dict(t=rx["t"], norm=rx["norm"]*ry["norm"],
                           centroid_x=rx["centroid"], centroid_y=ry["centroid"],
                           width_x=rx["width"], width_y=ry["width"],
                           skewness_x=rx["skewness"], skewness_y=ry["skewness"],
                           excess_kurtosis_x=rx["excess_kurtosis"],
                           excess_kurtosis_y=ry["excess_kurtosis"],
                           peak_probability=rx["peak"]*ry["peak"],
                           peak_over_initial=rx["peak_over_initial"]*ry["peak_over_initial"],
                           fidelity=rx["fidelity"]*ry["fidelity"],
                           density_overlap=rx["density_overlap"]*ry["density_overlap"],
                           left_tail_x=rx["left_tail_2_initial_sigma"],
                           right_tail_x=rx["right_tail_2_initial_sigma"],
                           left_tail_y=ry["left_tail_2_initial_sigma"],
                           right_tail_y=ry["right_tail_2_initial_sigma"],
                           tail_asymmetry_x=rx["tail_asymmetry"],
                           tail_asymmetry_y=ry["tail_asymmetry"])
                rows.append(row)
            all_rows[key] = rows
            csv_rows(key+".csv", rows)

    checks_2d = []
    for name, eta, t in [("A", 1., 180.), ("B", .3, 180.),
                         ("C", 1., 180.), ("C", .3, 360.)]:
        size = 512 if t == 180 else 1024
        qx, qy = CENTERS[name]
        px, py = Packet(sigma, qx, 1., size), Packet(sigma, qy, eta, size)
        initial = common.gaussian(size, sigma, (qx, qy))
        actual = common.propagate(initial, t, eta)
        product = np.outer(py.state(t), px.state(t))
        checks_2d.append(dict(case=name, eta=eta, time=t, N=size,
                              amplitude_L2_error=float(np.linalg.norm(actual-product)),
                              amplitude_Linf_error=float(np.max(abs(actual-product)))))
    box_checks = []
    for q, j in packets:
        small = packets[(q, j)].state(4320)
        large = Packet(sigma, q, j, 2*n).state(4320)
        large = large[n//2:3*n//2]
        box_checks.append(dict(q0=q, coupling=j, t=4320, N=n, large_N=2*n,
                               amplitude_L2_error=float(np.linalg.norm(small-large))))

    crossing = packets[(np.pi/2, 1.)]
    analytic = gaussian_velocity_moments(sigma, np.pi/2)
    zero_time = np.sqrt(-analytic["mean"]/(4*analytic["kappa3"]))
    root_numerical = brentq(lambda t: crossing.row(t)["m3"], 700, 1050)
    third_moment_checks = []
    for t in [180, 360, 864, 900, 1728, 4320]:
        row = crossing.row(t)
        predicted_m3 = t*crossing.mean_v/4 + t**3*crossing.kappa3_v
        predicted_k4 = t*t*crossing.var_v + t**4*crossing.kappa4_v
        third_moment_checks.append(dict(
            time=t, numerical_m3=row["m3"], predicted_m3=predicted_m3,
            m3_abs_error=abs(row["m3"]-predicted_m3),
            numerical_kappa4=row["kappa4"], predicted_kappa4=predicted_k4,
            kappa4_abs_error=abs(row["kappa4"]-predicted_k4)))

    lifetimes, fits, spectral_checks, quadrature_checks = lifetime_study()
    csv_rows("lifetimes.csv", lifetimes)
    checkpoints = {
        key: [min(rows, key=lambda r: abs(r["t"]-t))
              for t in [0, 180, 360, 864, 1728, 4320]]
        for key, rows in all_rows.items()}
    results = dict(
        method="Exact separable discrete Fourier evolution; no time stepping",
        model="e(qx,qy)=(1-cos qx)+eta*(1-cos qy), a=hbar=Jx=1",
        original_conditions=dict(sigma_a=sigma, N=n, eta=[1., .3],
                                 t_range=[0, 4320], n_times=len(times)),
        metrics={
            "fidelity": "|<psi_initial translated at spectral mean velocity | psi(t)>|^2",
            "density_overlap": "(sum_sites sqrt[P_reference P(t)])^2; 1 iff densities coincide",
            "tail": "Per-axis marginal probability strictly beyond mean plus/minus 2 initial RMS widths; sites within 1e-9 lattice units of either boundary are symmetrically excluded. Hard-cutoff lattice jumps are not interpreted as dynamics.",
            "shape_moments": "Marginal central skewness and excess kurtosis",
            "lifetime": "First downward crossing of F=0.9 or 0.5; no claim of monotonicity at all times",
            "comparison": "Fixed initial width and equal time; distances also recorded for lifetime table"},
        diagnostics_1d=diagnostics, checks_2d=checks_2d,
        box_convergence=box_checks,
        crossing_skewness=dict(
            numerical_zero_time=root_numerical,
            continuous_Gaussian_zero_time=zero_time,
            large_sigma_zero_time=4*sigma**3,
            third_moment_formula="mu3_x=t*mean_velocity/4+t^3*kappa3_velocity (Jx=a=hbar=1)",
            fourth_cumulant_formula="kappa4_x=t^2*variance_velocity+t^4*kappa4_velocity",
            analytic_domain="Continuous Gaussian spectral approximation; negligible alias tails for this broad real Gaussian. Exact discrete FFT is the primary result.",
            checks=third_moment_checks),
        lifetimes=lifetimes, lifetime_log_slopes=fits,
        lifetime_spectral_convergence=spectral_checks,
        lifetime_Gaussian_quadrature_convergence=quadrature_checks,
        checkpoints=checkpoints)
    assert max(r["max_edge_mass"] for r in diagnostics) < 1e-18
    assert max(r["amplitude_L2_error"] for r in checks_2d) < 1e-12
    assert max(r["amplitude_L2_error"] for r in box_checks) < 1e-10
    assert max(r["spectral_N4096_vs8192_error"] for r in spectral_checks) < 1e-10
    assert max(r["difference_from_exact_discrete_spectrum"] for r in quadrature_checks) < 1e-9
    dump("results.json", results)
    plot_results(all_rows, crossing, lifetimes, fits, root_numerical)
    print(json.dumps(dict(lifetime_log_slopes=fits,
                          crossing_skewness_zero=root_numerical,
                          final_C=all_rows["C_eta1"][-1]), indent=2))


def plot_results(traces, crossing, lifetimes, fits, zero_time):
    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Microsoft YaHei", "DejaVu Sans"],
                         "font.size": 12, "axes.unicode_minus": False,
                         "svg.fonttype": "none"})
    fig, axs = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    for name in CENTERS:
        rows = traces[name+"_eta1"]
        t = np.array([r["t"] for r in rows])
        early = t <= 180
        axs[0, 0].plot(t[early], np.array([r["width_x"] for r in rows])[early],
                       color=COLORS[name], label=name+"：x")
        axs[0, 0].plot(t[early], np.array([r["width_y"] for r in rows])[early],
                       "--", color=COLORS[name], label=name+"：y")
        axs[0, 1].plot(t, [r["fidelity"] for r in rows], color=COLORS[name], label=name)
        axs[1, 0].plot(t, [r["skewness_x"] for r in rows], color=COLORS[name],
                       label=name+"：x")
    rows = traces["C_eta1"]
    t = np.array([r["t"] for r in rows])
    axs[1, 1].plot(t, [r["fidelity"] for r in rows], color=COLORS["C"],
                   label="C：复态重叠 F")
    axs[1, 1].plot(t, [r["density_overlap"] for r in rows], "--", color="#7e5496",
                   label="C：概率形状重叠")
    axs[0, 0].set(title="原动画时段：交点同时减弱两个方向的展宽",
                   ylabel=r"RMS 宽度 / $a$")
    axs[0, 1].set(title="延长演化：交点仍然会失去保形", ylabel="复态平移保真度")
    axs[1, 0].axhline(0, color="gray", lw=.7)
    axs[1, 0].axvline(zero_time, color="gray", ls=":", lw=1)
    axs[1, 0].set(title="交点的偏度先正后负", ylabel="x 方向偏度")
    axs[1, 1].set(title="相位重叠与概率形状不是同一指标", ylabel="重叠")
    for ax in axs.flat:
        ax.set_xlabel(r"$t/(\hbar/J_x)$")
        ax.grid(alpha=.15)
        ax.legend(fontsize=9)
    fig.suptitle(r"$\sigma=6a,\ J_y=J_x$；A=(0.7,0.7)，B=(π/2,0.7)，C=(π/2,π/2)，坐标为 $ka$")
    fig.savefig(OUT/"audit_overview.png", dpi=160)
    fig.savefig(OUT/"audit_overview.svg")
    plt.close(fig)

    fig, axs = plt.subplots(2, 3, figsize=(12, 7), layout="constrained")
    for ax, t in zip(axs.flat, [0, 180, 864, 1728, 2880, 4320]):
        row, psi = crossing.row(t, True)
        z = (crossing.x-row["centroid"])/crossing.sigma
        p = np.abs(psi)**2 / crossing.p0
        use = abs(z) < 9
        ax.plot(z[use], p[use], color=COLORS["C"], lw=1.5, label="C：实际边际概率")
        ax.plot(z[use], np.exp(-z[use]**2/2), "--", color="gray", lw=1,
                label="初始 Gaussian 平移参考")
        ax.set(xlim=(-9, 9), ylim=(0, 1.04), xlabel=r"$(x-\langle x\rangle)/\sigma$",
               ylabel="边际概率 / 初始边际峰值",
               title=rf"$t={t}\hbar/J_x$；偏度={row['skewness']:.3f}")
        ax.grid(alpha=.15)
    axs[0, 0].legend(fontsize=8)
    fig.suptitle("交点波包的真实形变：早期正偏，随后负偏与后侧旁瓣；固定纵轴")
    fig.savefig(OUT/"crossing_profiles.png", dpi=160)
    fig.savefig(OUT/"crossing_profiles.svg")
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), layout="constrained")
    for name in CENTERS:
        rows = [r for r in lifetimes if r["case"] == name]
        s = np.array([r["sigma_a"] for r in rows])
        t = np.array([r["time_F_0.9"] for r in rows])
        slope = fits[name]["time_F_0.9"]
        axs[0].loglog(s, t, "o-", color=COLORS[name],
                     label=f"{name}：拟合指数 {slope:.3f}")
    for sigma, color in zip([4., 6., 8., 12.], ["#246B9A", "#CF7048", "#27816E", "#8556A6"]):
        packet = Packet(sigma, np.pi/2, n=4096)
        z = np.linspace(0, 22, 160)
        axs[1].plot(z, [packet.fidelity(t*sigma**3)**2 for t in z], color=color,
                     label=rf"$\sigma={sigma:g}a$")
    axs[0].set(xlabel=r"初始宽度 $\sigma/a$", ylabel=r"首次达到 $F=0.9$ 的时间 / $(\hbar/J_x)$",
               title="交点寿命约随初宽三次方增长")
    axs[1].set(xlabel=r"$[t/(\hbar/J_x)]/(\sigma/a)^3$", ylabel="C：复态平移保真度",
               title="交点曲线在三次方时间标度下近乎重合", ylim=(0, 1.01))
    for ax in axs:
        ax.grid(alpha=.15)
        ax.legend(fontsize=10)
    fig.savefig(OUT/"lifetime_scaling.png", dpi=160)
    fig.savefig(OUT/"lifetime_scaling.svg")
    plt.close(fig)


if __name__ == "__main__":
    main()
