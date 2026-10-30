"""Finite-distance disorder benchmark for a Gaussian in an XY/cavity chain.

Outputs are confined to this directory. No clock entropy or first-arrival
statistics are inferred from the fixed-time bulk receiver probability.
"""
from pathlib import Path
import argparse
import csv
import json
import time

import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.sparse import diags
from scipy.sparse.linalg import expm_multiply
from scipy.stats import t as student_t
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

OUT = Path(__file__).resolve().parent
N = 1024
SIGMA = 6.0
DISTANCE = 160.0
X0 = -160.0
SEED_BASE = 2026102100
DEMO_SEED = SEED_BASE  # Prespecified; not selected by outcome.
KINDS = ("onsite", "bond", "heisenberg")
LABELS = {
    "onsite": "独立 onsite 频率无序",
    "bond": "独立 bond 跃迁无序",
    "heisenberg": "Heisenberg 交换无序",
}
COLORS = {"onsite": "#c25141", "bond": "#256c9c", "heisenberg": "#27836c"}
STRENGTHS = (0.02, 0.05, 0.10, 0.20)


def gaussian(n, q0):
    x = np.arange(n) - n // 2
    psi = np.exp(-(x-X0)**2/(4*SIGMA**2) + 1j*q0*(x-X0))
    return x, psi / np.linalg.norm(psi)


def clean_reference(n, q0):
    x, initial = gaussian(n, q0)
    q = 2*np.pi*np.fft.fftfreq(n)
    spectrum = np.fft.fft(initial)
    power = np.abs(spectrum)**2/n
    velocity = float(np.sum(power*np.sin(q)))
    arrival = DISTANCE/velocity
    exact = np.fft.ifft(spectrum*np.exp(-1j*(1-np.cos(q))*arrival))
    translated = np.fft.ifft(spectrum*np.exp(-1j*q*DISTANCE))
    return x, initial, exact, translated, arrival, velocity


def disorder_arrays(seed, n):
    """Use the same physical realization when extending the box."""
    rng = np.random.default_rng(seed)
    all_values = rng.normal(size=8192)
    offset = 4096 - n//2
    onsite = all_values[offset:offset+n]
    bonds = all_values[offset:offset+n-1]
    return onsite, bonds


def hamiltonian(kind, w, seed, n=N, budget_n=N):
    z_site, z_bond = disorder_arrays(seed, n)
    diagonal = np.ones(n)
    off = np.full(n-1, -.5)
    if kind == "onsite":
        delta_d = w*z_site
        delta_o = np.zeros(n-1)
    elif kind == "bond":
        # 2(N-1) Var(delta hopping) / N = w^2.
        delta_o = w*np.sqrt(budget_n/(2*(budget_n-1)))*z_bond
        delta_d = np.zeros(n)
    elif kind == "heisenberg":
        # The physical graph Laplacian has half the bulk diagonal at its ends.
        diagonal[[0, -1]] = .5
        delta_j = w*np.sqrt(budget_n/(budget_n-1))*z_bond
        delta_o = -.5*delta_j
        delta_d = np.zeros(n)
        delta_d[:-1] += .5*delta_j
        delta_d[1:] += .5*delta_j
    else:
        raise ValueError(kind)
    d, o = diagonal+delta_d, off+delta_o
    h = diags([o, d, o], [-1, 0, 1], format="csr")
    realized_budget = float((np.sum(delta_d**2)+2*np.sum(delta_o**2))/n)
    return h, d, o, realized_budget


def evolve(h, initial, t):
    return expm_multiply(-1j*t*h, initial, traceA=-1j*t*h.diagonal().sum())


def metrics(psi, x, exact, translated):
    p = np.abs(psi)**2
    return {
        "norm": float(p.sum()),
        "receiver_probability": float(p[np.abs(x) <= 2*SIGMA].sum()),
        "fidelity_to_clean_evolution": float(abs(np.vdot(exact, psi))**2),
        "fidelity_to_rigid_translation": float(abs(np.vdot(translated, psi))**2),
        "centroid": float(np.sum(x*p)),
        "participation_sites": float(1/np.sum(p*p)),
        "left_edge_probability": float(p[:32].sum()),
        "right_edge_probability": float(p[-32:].sum()),
    }


def mean_ci(values):
    a = np.asarray(values)
    avg = float(a.mean())
    se = float(a.std(ddof=1)/np.sqrt(len(a))) if len(a) > 1 else 0.
    half = float(student_t.ppf(.975, len(a)-1)*se) if len(a) > 1 else 0.
    return {"mean": avg, "standard_error": se,
            "ci95": [avg-half, avg+half], "n": len(a)}


def main():
    begin = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    rows, summaries, comparisons, clean = [], [], [], {}
    # Primary test is band center; the smaller off-center set is a mechanism
    # control, not a new optimization problem.
    protocols = [
        ("band_center", np.pi/2, STRENGTHS, 64),
        ("off_center_control", .7, (.05, .10), 32),
    ]
    for tag, q0, strengths, count in protocols:
        x, initial, exact, translated, arrival, velocity = clean_reference(N, q0)
        clean[tag] = {
            "q0": q0, "arrival_time": arrival, "mean_velocity": velocity,
            **metrics(exact, x, exact, translated),
        }
        for w in strengths:
            grouped = {kind: [] for kind in KINDS}
            for seed_index in range(count):
                seed = SEED_BASE + seed_index
                for kind in KINDS:
                    h, _, _, budget = hamiltonian(kind, w, seed)
                    psi = evolve(h, initial, arrival)
                    row = {
                        "protocol": tag, "q0": q0, "strength_w": w,
                        "kind": kind, "seed": seed, "arrival_time": arrival,
                        "realized_perturbation_budget": budget,
                        **metrics(psi, x, exact, translated),
                    }
                    rows.append(row)
                    grouped[kind].append(row)
            for kind, group in grouped.items():
                summaries.append({
                    "protocol": tag, "q0": q0, "strength_w": w, "kind": kind,
                    "receiver_probability": mean_ci(
                        [r["receiver_probability"] for r in group]),
                    "fidelity_to_clean_evolution": mean_ci(
                        [r["fidelity_to_clean_evolution"] for r in group]),
                    "fidelity_to_rigid_translation": mean_ci(
                        [r["fidelity_to_rigid_translation"] for r in group]),
                    "realized_budget": mean_ci(
                        [r["realized_perturbation_budget"] for r in group]),
                })
            difference = [
                a["receiver_probability"]-b["receiver_probability"]
                for a, b in zip(grouped["onsite"], grouped["bond"])]
            stats = mean_ci(difference)
            # This equivalence margin is an operational benchmark, not a
            # quantitative claim made by the cited authors.
            equivalence = stats["ci95"][0] >= -.05 and stats["ci95"][1] <= .05
            comparisons.append({
                "protocol": tag, "strength_w": w,
                "onsite_minus_bond_receiver": stats,
                "within_five_percentage_point_equivalence_margin": equivalence,
            })
            print(tag, "w", w, "paired difference", stats["mean"],
                  stats["ci95"], flush=True)

    validation = validate(clean)
    result = {
        "scope": "Fixed-distance bulk transport; not full clock precision, entropy, or first-arrival statistics.",
        "units": "a=hbar=J=1; clean hopping is -J/2 and clean bulk diagonal is J",
        "source_anchor": {
            "paper": "Meier et al., Precision is not limited by the second law of thermodynamics",
            "doi": "10.1038/s41567-025-02929-2",
            "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12263443/",
            "location": "Published Methods: Stability under perturbations, second paragraph; published PDF page 9 including cover.",
            "explicit_unperformed_expectation": "Bare-qubit frequency disorder is expected to affect performance comparably to coupling imperfections; numerics there address coupling disorder and amplitude damping.",
            "our_subtest": "Compare fixed-distance Gaussian bulk reception under matched Hamiltonian-error budgets.",
        },
        "parameters": {
            "N": N, "sigma_a": SIGMA, "initial_center_a": X0,
            "distance_a": DISTANCE, "receiver_center_a": 0,
            "receiver_half_width_a": 2*SIGMA,
            "primary_confirmatory_draws": 64, "off_center_control_draws": 32,
            "strengths": list(STRENGTHS), "seed_base": SEED_BASE,
            "demo_seed": DEMO_SEED, "demo_strength": .05,
            "design_selection": "Parameters and demo seed fixed before ensemble; no fitting, per-realization timing selection, or test-set tuning.",
        },
        "budget": {
            "definition": "E[Tr((delta H)^2)]/N = w^2",
            "onsite_std": "w",
            "bond_hopping_std": "w sqrt[N/(2(N-1))]",
            "heisenberg_exchange_std": "w sqrt[N/(N-1)]",
            "pairing": "Models share an iid Gaussian coordinate-indexed sequence within each seed. Their marginal disorder laws are correct. Pairwise CIs use per-seed differences.",
            "interpretation": "Equal Frobenius variance does not imply equal backscattering strength. This defines a reproducible comparison, not universal disorder equivalence.",
        },
        "clean_baselines": clean,
        "summaries": summaries,
        "paired_comparisons": comparisons,
        "validation": validation,
        "max_ensemble_norm_error": max(abs(r["norm"]-1) for r in rows),
        "max_ensemble_edge_probability": max(
            r["left_edge_probability"]+r["right_edge_probability"] for r in rows),
        "runtime_seconds": time.perf_counter()-begin,
    }
    result["born_matched_control"] = born_control(rows)
    with (OUT/"ensemble.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    (OUT/"results.json").write_text(json.dumps(result, indent=2),
                                    encoding="utf-8")
    make_plots(result)
    plot_born_control(result)
    make_demo()
    print(json.dumps({"runtime_seconds": time.perf_counter()-begin,
                      "max_norm_error": result["max_ensemble_norm_error"],
                      "validation": validation}, indent=2))


def born_control(rows):
    """One discriminating check; do not mislabel this as equal-Frobenius."""
    w = .05
    x, initial, exact, translated, arrival, _ = clean_reference(N, np.pi/2)
    onsite = {
        int(r["seed"]): r for r in rows
        if r["protocol"] == "band_center" and r["kind"] == "onsite"
        and float(r["strength_w"]) == w
    }
    controls = []
    for seed in sorted(onsite):
        # The Frobenius-matched bond std was w sqrt[N/(2(N-1))].
        # Dividing by sqrt(2) matches its backscattering matrix-element
        # variance to the onsite value w^2/N.
        h, _, _, budget = hamiltonian("bond", w/np.sqrt(2), seed)
        psi = evolve(h, initial, arrival)
        m = metrics(psi, x, exact, translated)
        controls.append({"seed": seed, "realized_budget": budget, **m})
    paired_p = [
        float(onsite[r["seed"]]["receiver_probability"])-r["receiver_probability"]
        for r in controls
    ]
    paired_f = [
        float(onsite[r["seed"]]["fidelity_to_clean_evolution"])
        - r["fidelity_to_clean_evolution"] for r in controls
    ]
    with (OUT/"born_matched_control.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=controls[0])
        writer.writeheader()
        writer.writerows(controls)
    result = {
        "scope": "One added diagnostic control, q0=pi/2, onsite w=.05, same 64 seeds and geometry.",
        "onsite_std": w,
        "bond_std": float(w*np.sqrt(N/(4*(N-1)))),
        "bond_expected_frobenius_budget": w*w/2,
        "onsite_expected_frobenius_budget": w*w,
        "variance_of_backscatter_matrix_element": "onsite: w^2/N; bond: 4(N-1)*std_bond^2/N^2 = w^2/N",
        "important": "This control matches leading Born backscattering, not total Hamiltonian perturbation budget. It is not a disorder-free or exact scattering-equivalence theorem.",
        "bond_receiver_probability": mean_ci([r["receiver_probability"] for r in controls]),
        "bond_fidelity_to_clean_evolution": mean_ci(
            [r["fidelity_to_clean_evolution"] for r in controls]),
        "onsite_minus_bond_receiver": mean_ci(paired_p),
        "onsite_minus_bond_fidelity_to_clean_evolution": mean_ci(paired_f),
        "max_norm_error": max(abs(r["norm"]-1) for r in controls),
    }
    print("Born-matched control", json.dumps(result, indent=2), flush=True)
    return result


def plot_born_control(result):
    configure_plot()
    primary = {
        s["kind"]: s for s in result["summaries"]
        if s["protocol"] == "band_center" and s["strength_w"] == .05
    }
    control = result["born_matched_control"]
    entries = [
        primary["onsite"]["receiver_probability"],
        primary["bond"]["receiver_probability"],
        control["bond_receiver_probability"],
    ]
    labels = ["onsite\n参考误差预算",
              "bond\n相同 Hamiltonian 预算",
              "bond\n相同最低阶后向散射"]
    fig, ax = plt.subplots(figsize=(8.6, 4.9), layout="constrained")
    means = [r["mean"] for r in entries]
    error = [[r["mean"]-r["ci95"][0] for r in entries],
             [r["ci95"][1]-r["mean"] for r in entries]]
    ax.bar(np.arange(3), means, yerr=error, capsize=5,
           color=["#c25141", "#256c9c", "#69a5c2"], width=.65)
    for i, value in enumerate(means):
        ax.text(i, value+.025, f"{value:.4f}", ha="center")
    ax.set(xticks=np.arange(3), xticklabels=labels, ylim=(0, .85),
           ylabel="固定接收窗概率",
           title=r"$k_0a=\pi/2$：一次针对误差归因的对照")
    fig.suptitle(
        r"onsite 标准差 $0.05J$；同一初态、距离和 64 个配对实现",
        fontsize=12)
    fig.savefig(OUT/"born_matched_control.png", dpi=160)
    fig.savefig(OUT/"born_matched_control.svg")
    plt.close(fig)


def validate(clean):
    x, initial, exact, translated, arrival, _ = clean_reference(N, np.pi/2)
    checks = []
    for kind in KINDS:
        h, _, _, _ = hamiltonian(kind, 0, DEMO_SEED)
        actual = evolve(h, initial, arrival)
        checks.append({"kind": kind,
                       "clean_FFT_L2_error": float(np.linalg.norm(actual-exact)),
                       "hermiticity_max_error": float(
                           abs(h-h.getH()).max())})
    h, diagonal, off, _ = hamiltonian("onsite", .1, DEMO_SEED)
    eigenvalues, eigenvectors = eigh_tridiagonal(diagonal, off)
    independent = eigenvectors @ (
        np.exp(-1j*eigenvalues*arrival)*(eigenvectors.T @ initial))
    direct = evolve(h, initial, arrival)
    eig_error = float(np.linalg.norm(independent-direct))
    boxes = []
    for kind in KINDS:
        small, _, _, _ = hamiltonian(kind, .2, DEMO_SEED, N, N)
        large, _, _, _ = hamiltonian(kind, .2, DEMO_SEED, 2*N, N)
        _, bigger_initial = gaussian(2*N, np.pi/2)
        small_final = evolve(small, initial, arrival)
        large_final = evolve(large, bigger_initial, arrival)
        off = N//2
        cropped = large_final[off:off+N]
        boxes.append({
            "kind": kind, "N": N, "larger_N": 2*N,
            "same_physical_disorder_coefficients": True,
            "amplitude_L2_error": float(np.linalg.norm(small_final-cropped)),
        })
    hs, _, _, _ = hamiltonian("heisenberg", .1, DEMO_SEED)
    row_sum = float(np.max(abs(hs @ np.ones(N))))
    assert max(c["clean_FFT_L2_error"] for c in checks) < 1e-10
    assert eig_error < 1e-10
    assert max(c["amplitude_L2_error"] for c in boxes) < 1e-9
    assert row_sum < 1e-12
    return {"clean_limits": checks,
            "independent_eigendecomposition_L2_error": eig_error,
            "box_enlargement": boxes,
            "heisenberg_graph_laplacian_row_sum_error": row_sum,
            "evolution": "Direct scipy expm_multiply; no integration time-step discretization.",
            "boundary_note": "Physical open Heisenberg diagonal is 1/2 at the ends; XY diagonal is 1. Source and receiver are far from both ends."}


def configure_plot():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Microsoft YaHei", "DejaVu Sans"],
        "axes.unicode_minus": False, "font.size": 11,
        "svg.fonttype": "none",
    })


def make_plots(result):
    configure_plot()
    fig, axes = plt.subplots(2, 2, figsize=(12.8, 8.8), layout="constrained")
    for col, (tag, title) in enumerate([
            ("band_center", r"中心波矢 $k_0a=\pi/2$"),
            ("off_center_control", r"离中心对照 $k_0a=0.7$")]):
        baseline = result["clean_baselines"][tag]
        for kind in KINDS:
            items = [s for s in result["summaries"]
                     if s["protocol"] == tag and s["kind"] == kind]
            for row, metric in enumerate(
                    ("receiver_probability", "fidelity_to_clean_evolution")):
                xs = [0.] + [r["strength_w"] for r in items]
                ys = [baseline[metric]] + [r[metric]["mean"] for r in items]
                lo = [0.] + [r[metric]["mean"]-r[metric]["ci95"][0] for r in items]
                hi = [0.] + [r[metric]["ci95"][1]-r[metric]["mean"] for r in items]
                axes[row, col].errorbar(xs, ys, yerr=[lo, hi], color=COLORS[kind],
                                       marker="o", lw=1.8, capsize=3,
                                       label=LABELS[kind])
        axes[0, col].set_title(title)
        axes[0, col].set_ylabel("固定接收窗概率")
        axes[1, col].set_ylabel("与干净演化态的重叠模方")
        for row in range(2):
            axes[row, col].set(xlabel=r"扰动预算 $w/J$", ylim=(-.02, 1.04))
            axes[row, col].grid(alpha=.2)
            axes[row, col].legend(fontsize=9)
    fig.suptitle(
        "相同 Hamiltonian 扰动预算不意味着相同传输损失\n"
        r"$\sigma=6a$，距离 $160a$；误差条为均值 95% CI；未逐次优化到达时刻",
        fontsize=14)
    fig.savefig(OUT/"summary.png", dpi=160)
    fig.savefig(OUT/"summary.svg")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.3, 4.9), layout="constrained")
    for tag, color, label in [
            ("band_center", "#6a4c93", r"$k_0a=\pi/2$，64 个实现"),
            ("off_center_control", "#656d4a", r"$k_0a=0.7$，32 个实现")]:
        items = [r for r in result["paired_comparisons"] if r["protocol"] == tag]
        means = [r["onsite_minus_bond_receiver"]["mean"] for r in items]
        errs = [[m-r["onsite_minus_bond_receiver"]["ci95"][0]
                 for m, r in zip(means, items)],
                [r["onsite_minus_bond_receiver"]["ci95"][1]-m
                 for m, r in zip(means, items)]]
        ax.errorbar([r["strength_w"] for r in items], means,
                    yerr=errs, marker="o", color=color, capsize=4, label=label)
    ax.axhspan(-.05, .05, color="#dceada", label="本测试的 ±5 个百分点等效区")
    ax.axhline(0, color="black", lw=.8)
    ax.set(xlabel=r"扰动预算 $w/J$", ylabel="onsite − bond 接收概率",
           title="配对实现差值；等效区是本测试判据，不是论文原话")
    ax.legend(fontsize=10)
    ax.grid(alpha=.2)
    fig.savefig(OUT/"paired_difference.png", dpi=160)
    fig.savefig(OUT/"paired_difference.svg")
    plt.close(fig)


def make_demo():
    configure_plot()
    x, initial, exact, translated, arrival, _ = clean_reference(N, np.pi/2)
    count = 65
    times = np.linspace(0, arrival, count)
    cases = [("clean", 0.), ("onsite", .05), ("bond", .05),
             ("heisenberg", .05)]
    tracks = {}
    for label, w in cases:
        kind = "onsite" if label == "clean" else label
        h, _, _, _ = hamiltonian(kind, w, DEMO_SEED)
        tracks[label] = expm_multiply(
            -1j*h, initial, start=0., stop=arrival, num=count,
            traceA=-1j*h.diagonal().sum())
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 6.4), layout="constrained")
    lines = {}
    pmax = float(np.abs(initial).max()**2)*1.06
    for ax, (label, w) in zip(axes.flat, cases):
        color = "#777777" if label == "clean" else COLORS[label]
        line, = ax.plot(x, np.abs(initial)**2, color=color, lw=1.7)
        ax.axvspan(-2*SIGMA, 2*SIGMA, color="#c9d8b6", alpha=.5)
        ax.set(xlim=(-200, 50), ylim=(0, pmax), xlabel=r"$x/a$",
               ylabel="格点概率",
               title="干净 XY 对照" if label == "clean" else LABELS[label])
        lines[label] = line
    title = fig.suptitle("", fontsize=13)
    frames = []
    for i, t in enumerate(times):
        for label, _ in cases:
            lines[label].set_ydata(abs(tracks[label][i])**2)
        title.set_text(
            rf"$t={t:.1f}\hbar/J$，$w=0.05J$，预先固定 seed={DEMO_SEED}"
            "\n固定坐标与色标；绿色为接收窗；单个实现仅用于演示")
        fig.canvas.draw()
        frame = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())
        if i in (0, count//2, count-1):
            frame.save(OUT/f"demo_frame_{i:02d}.png")
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=192))
    durations = [80]*count
    durations[0], durations[-1] = 600, 1600
    frames[0].save(OUT/"demo.gif", save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=False, disposal=2)
    plt.close(fig)
    with Image.open(OUT/"demo.gif") as im:
        assert im.n_frames == count
        for i in range(count):
            im.seek(i)
            im.load()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--control-only", action="store_true",
                        help="Add only the discriminating control to existing results.")
    args = parser.parse_args()
    if args.control_only:
        with (OUT/"ensemble.csv").open(encoding="utf-8", newline="") as f:
            stored_rows = list(csv.DictReader(f))
        stored_result = json.loads((OUT/"results.json").read_text(encoding="utf-8"))
        stored_result["born_matched_control"] = born_control(stored_rows)
        (OUT/"results.json").write_text(json.dumps(stored_result, indent=2),
                                        encoding="utf-8")
        plot_born_control(stored_result)
    else:
        main()
