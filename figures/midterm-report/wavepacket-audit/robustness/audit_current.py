"""Audit probability currents and carrier detuning in the existing cosine model.

Units: a=Jx=hbar=1. This script only writes files beside itself. Product-state
factorization reduces the diagnostic to one-dimensional marginal evolution.
"""
from pathlib import Path
import csv
import json
import sys

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq, minimize_scalar
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT))
import common


class Chain:
    def __init__(self, n=4096, sigma=6., q0=np.pi/2, positive_only=False):
        self.n = n
        self.x = np.arange(n) - n//2
        self.q = 2*np.pi*np.fft.fftfreq(n)
        self.eps = 1-np.cos(self.q)
        psi = np.exp(-self.x**2/(4*sigma**2)+1j*q0*self.x)
        psi /= np.linalg.norm(psi)
        self.initial = psi
        self.A = np.fft.fft(psi)
        self.removed_weight = float(np.sum(abs(self.A[np.sin(self.q) <= 0])**2)/n)
        if positive_only:
            self.A[np.sin(self.q) <= 0] = 0
            self.A /= np.sqrt(np.sum(abs(self.A)**2)/n)
        self.projected_distance = float(np.linalg.norm(np.fft.ifft(self.A)-psi))
        self.power = abs(self.A)**2/n
        self.mean_v = float(np.sum(self.power*np.sin(self.q)))
        self.var_v = float(np.sum(self.power*(np.sin(self.q)-self.mean_v)**2))

    def state(self, t):
        return np.fft.ifft(self.A*np.exp(-1j*self.eps*t))

    def at_cut(self, cut, t):
        psi = self.state(t)
        idx = cut+self.n//2
        return float(np.imag(psi[idx].conjugate()*psi[idx+1]))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)


def event(n, cut, search_lo, search_hi, near):
    chain = Chain(n=n, positive_only=True)
    times = np.linspace(search_lo, search_hi, 601)
    vals = np.array([chain.at_cut(cut, t) for t in times])
    roots = []
    for i in range(len(times)-1):
        if vals[i]*vals[i+1] < 0:
            roots.append(brentq(lambda t: chain.at_cut(cut, t),
                                times[i], times[i+1], xtol=1e-12))
    intervals = [(a,b) for a,b in zip(roots[:-1], roots[1:])
                 if chain.at_cut(cut, (a+b)/2) < 0]
    start,end = min(intervals, key=lambda pair: abs((pair[0]+pair[1])/2-near))
    integral, qerror = quad(lambda t: chain.at_cut(cut, t), start,end,
                            epsabs=1e-13, epsrel=1e-10)
    minimum = minimize_scalar(lambda t: chain.at_cut(cut,t),
                              bounds=(start,end), method="bounded",
                              options={"xatol":1e-11})
    pstart = chain.state(start)
    pend = chain.state(end)
    right = chain.x > cut
    right_change = float(np.sum(abs(pend[right])**2)-np.sum(abs(pstart[right])**2))
    left_change = float(np.sum(abs(pend[~right])**2)-np.sum(abs(pstart[~right])**2))
    other_flux, _ = quad(
        lambda t: float(np.imag(chain.state(t)[-1].conjugate()*chain.state(t)[0])),
        start,end, epsabs=1e-17)
    record = dict(
        N=n, sigma_a=6., q0=np.pi/2, cut_bond=[cut,cut+1],
        positive_velocity_projection=True,
        excluded_spectral_weight=chain.removed_weight,
        initial_state_L2_change=chain.projected_distance,
        start=start, end=end, integrated_cut_flux=integral,
        quadrature_error_estimate=qerror, min_current=float(minimum.fun),
        min_current_time=float(minimum.x),
        right_probability_change=right_change,
        left_probability_change=left_change,
        other_periodic_cut_integrated_flux=other_flux,
        continuity_integral_error=abs(right_change-(integral-other_flux)),
        spectral_mean_velocity=chain.mean_v)
    profile = []
    for t in np.linspace(start-1,end+1,151):
        psi = chain.state(t)
        profile.append(dict(
            t=float(t), current=chain.at_cut(cut,t),
            right_probability=float(np.sum(abs(psi[right])**2)),
            left_probability=float(np.sum(abs(psi[~right])**2))))
    return record,profile


def main():
    chains = {"ordinary":Chain(q0=.7), "crossing":Chain()}
    times = np.unique(np.r_[np.linspace(0,180,721), np.arange(182,1201,2)])
    rows = []
    for label,chain in chains.items():
        for t in times:
            psi = chain.state(t)
            rho = abs(psi)**2
            current = np.imag(psi.conjugate()*np.roll(psi,-1))
            dotpsi = -1j*(psi-.5*(np.roll(psi,1)+np.roll(psi,-1)))
            continuity = (2*np.real(psi.conjugate()*dotpsi)
                          -(np.roll(current,1)-current))
            rephased = psi*np.exp(1j*.734)
            gauge_error = np.max(abs(
                np.imag(rephased.conjugate()*np.roll(rephased,-1))-current))
            negative = np.maximum(-current,0)
            center = float(np.sum(chain.x*rho))
            rows.append(dict(
                case=label, t=float(t), norm=float(rho.sum()),
                centroid=center,
                width=float(np.sqrt(np.sum((chain.x-center)**2*rho))),
                total_current=float(current.sum()),
                minimum_current=float(current.min()),
                minimum_current_bond=int(chain.x[np.argmin(current)]),
                sum_negative_current=float(negative.sum()),
                continuity_max_error=float(np.max(abs(continuity))),
                global_phase_current_max_error=float(gauge_error)))
    write_csv(OUT/"current_trace.csv",rows)

    detuning = []
    for sigma in [4.,6.,8.,12.]:
        s2=1/(4*sigma**2)
        crossover=float(np.arctan(np.sqrt(np.tanh(s2/2))))
        for d in sorted(set([0.,.025,.05,.075,.1,.15,.2,crossover])):
            chain=Chain(n=2048,sigma=sigma,q0=np.pi/2+d)
            exact_gauss=.5*np.cos(d)**2*(1-np.exp(-s2))**2 + .5*np.sin(d)**2*(1-np.exp(-2*s2))
            psi=chain.state(180.)
            rho=abs(psi)**2
            center=float(np.sum(chain.x*rho))
            width=float(np.sqrt(np.sum((chain.x-center)**2*rho)))
            detuning.append(dict(
                sigma_a=sigma, delta_q=d, crossover_delta_q=crossover,
                spectral_velocity_variance=chain.var_v,
                gaussian_velocity_variance=float(exact_gauss),
                variance_formula_error=float(abs(chain.var_v-exact_gauss)),
                width_t180_a=width,
                moment_width_t180_a=float(np.sqrt(sigma**2+180**2*chain.var_v)),
                width_doubling_time_prediction=float(np.sqrt(3)*sigma/np.sqrt(chain.var_v))))
    write_csv(OUT/"detuning.csv",detuning)

    events=[]
    for n in [4096,8192]:
        for cut,lo,hi,near in [(155,165.,195.,180.),(843,850.,880.,864.)]:
            result,profile=event(n,cut,lo,hi,near)
            events.append(result)
            if n==4096:
                write_csv(OUT/f"fixed_cut_{cut}.csv",profile)

    q0=(np.pi/2,np.pi/2)
    full=common.propagate(common.gaussian(512,6.,q0),180.,1.)
    one=Chain(n=512).state(180.)
    product=np.outer(one,one)
    jx=np.imag(full.conjugate()*np.roll(full,-1,axis=1))
    jy=np.imag(full.conjugate()*np.roll(full,-1,axis=0))
    jone=np.imag(one.conjugate()*np.roll(one,-1))
    factorization=dict(
        full_2d_product_Linf=float(np.max(abs(full-product))),
        x_marginal_current_Linf=float(np.max(abs(jx.sum(axis=0)-jone))),
        y_marginal_current_Linf=float(np.max(abs(jy.sum(axis=1)-jone))))
    summary=dict(
        units="a=Jx=hbar=1; sigma is initial probability RMS width in a",
        model="epsilon=1-cos(qx)+eta*(1-cos(qy)); unchanged source Hamiltonian",
        probability_current="jx=Im(conj(psi_mn)*psi_(m+1,n)); jy=eta Im(conj(psi_mn)*psi_(m,n+1))",
        continuity="d|psi|^2/dtau=jx_(m-1,n)-jx_mn+jy_(m,n-1)-jy_mn",
        factorization=factorization,
        current_trace_checks=dict(
            max_norm_error=max(abs(r["norm"]-1) for r in rows),
            max_continuity_error=max(r["continuity_max_error"] for r in rows),
            max_global_phase_error=max(r["global_phase_current_max_error"] for r in rows),
            max_total_current_drift=max(abs(r["total_current"]-chains[r["case"]].mean_v) for r in rows)),
        representative_currents=[r for r in rows if r["t"] in (0.,180.,432.,864.,1200.)],
        fixed_cut_backflow_events=events,
        detuning_crossover=[dict(sigma_a=s,crossover_delta_q=float(
            np.arctan(np.sqrt(np.tanh(1/(8*s*s)))))) for s in [4,6,8,12]],
        max_detuning_formula_error=max(r["variance_formula_error"] for r in detuning),
        max_moment_width_error=max(abs(r["width_t180_a"]-r["moment_width_t180_a"]) for r in detuning),
        interpretation=(
            "Coordinate factorization does not imply absence of entanglement between spin partitions. "
            "The small fixed-cut backflow is phase invariant and survives positive-velocity projection. "
            "It is distinct from global-phase-sensitive Re(psi) pulsing. No novelty claim is made."))
    (OUT/"results.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")

    plt.rcParams.update({"font.sans-serif":["Microsoft YaHei","DejaVu Sans"],
                         "axes.unicode_minus":False,"font.size":12})
    fig,axs=plt.subplots(2,2,figsize=(12,8.6),layout="constrained")
    crossing=[r for r in rows if r["case"]=="crossing"]
    axs[0,0].plot([r["t"] for r in crossing],[r["total_current"] for r in crossing])
    axs[0,0].set(xlabel=r"$t/(\hbar/J_x)$",ylabel="总概率流",
                 title="总流恒定且向右",ylim=(.99,1.003))
    axs[0,1].semilogy([r["t"] for r in crossing],
                     [max(r["sum_negative_current"],1e-32) for r in crossing])
    axs[0,1].set(xlabel=r"$t/(\hbar/J_x)$",ylabel="负键流绝对值之和",
                 title="后尾部出现小幅局部反流")
    profile=np.genfromtxt(OUT/"fixed_cut_843.csv",delimiter=",",names=True)
    axs[1,0].plot(profile["t"],profile["current"],color="#b8493b")
    axs[1,0].axhline(0,color=".5",lw=.8)
    late=events[1]
    axs[1,0].axvspan(late["start"],late["end"],color="#b8493b",alpha=.12)
    axs[1,0].set(xlabel=r"$t/(\hbar/J_x)$",ylabel="固定截面概率流",
                 title=r"$m=843\to844$：严格正速度谱仍有反流")
    six=[r for r in detuning if r["sigma_a"]==6]
    axs[1,1].plot([r["delta_q"] for r in six],
                 [r["width_t180_a"] for r in six],"o-")
    axs[1,1].axvline(six[0]["crossover_delta_q"],color=".5",ls="--")
    axs[1,1].set(xlabel=r"$k_0a-\pi/2$",ylabel=r"$\sigma(t=180)/a$",
                 title=r"初宽 $6a$：失谐使展宽增大")
    fig.suptitle("交点波包的概率流与失谐鲁棒性",fontsize=16)
    fig.savefig(OUT/"current_and_detuning.png",dpi=160)
    fig.savefig(OUT/"current_and_detuning.svg")
    plt.close(fig)
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
