"""Finite-resolution detection of backflow in a free cosine lattice.

All outputs stay beside this script. Units are a=J=hbar=1. A small two-carrier
preparation family is optimized for a fixed finite-time measurement, not for an
instantaneous bond current. This is a lattice operational subtest of the
smooth-window question, not a solution of the full continuum optimization.
"""
from pathlib import Path
import csv
import json

import numpy as np
from scipy.linalg import eigh
from scipy.optimize import minimize, brentq
from scipy.special import erfc, ndtr
from scipy.integrate import quad
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

OUT = Path(__file__).resolve().parent
SIGMA = 6.
CENTER = .5
DURATION = 1.
DESIGN_RESOLUTION = .5
NEGATIVE_CACHE = {}


def lattice(n):
    x = np.arange(n) - n//2
    q = 2*np.pi*np.fft.fftfreq(n)
    return x, q, 1-np.cos(q)


def weight(x, cut, width):
    if width == 0:
        return (x <= cut).astype(float)
    return .5*erfc((x-cut-.5)/(np.sqrt(2)*width))


def evolve(psi, t):
    _, _, energy = lattice(psi.size)
    return np.fft.ifft(np.fft.fft(psi)*np.exp(-1j*energy*t))


def gaussian(n, q0, center=CENTER, sigma=SIGMA):
    x, _, _ = lattice(n)
    psi = np.exp(-(x-center)**2/(4*sigma**2)+1j*q0*(x-center))
    return psi / np.linalg.norm(psi)


def projection(psi):
    _, q, _ = lattice(psi.size)
    spectrum = np.fft.fft(psi)
    spectrum[np.sin(q) <= 0] = 0.
    return np.fft.ifft(spectrum)/np.sqrt(np.sum(abs(spectrum)**2)/psi.size)


def negative_weight(psi, order=256):
    """Infinite-chain Bloch probability integrated over -pi<q<0.

    For localized preparations, the finite array is an exponentially accurate
    representation of the infinite-lattice initial state. This avoids the
    O(1/N) endpoint ambiguity of summing discrete modes with sin(q)<0.
    """
    key=(psi.tobytes(),order)
    if key in NEGATIVE_CACHE:
        return NEGATIVE_CACHE[key]
    x, _, _=lattice(psi.size)
    keep=abs(psi)>1e-16
    nodes,weights=np.polynomial.legendre.leggauss(order)
    q=.5*np.pi*(nodes-1)
    amplitude=np.exp(-1j*q[:,None]*x[None,keep])@psi[keep]
    result=float(.25*np.sum(weights*abs(amplitude)**2))
    NEGATIVE_CACHE[key]=result
    return result


def discrete_negative_weight(psi):
    _,q,_=lattice(psi.size)
    spectrum=np.fft.fft(psi)/np.sqrt(psi.size)
    # q=0 and q=-pi are exactly zero-velocity modes, not negative modes.
    return float(np.sum(abs(spectrum[np.sin(q)<-1e-14])**2))


def summary(psi, cut=0, start=0., end=DURATION, width=0.,
            negative_rule="continuous_bloch"):
    x, q, _ = lattice(psi.size)
    first, last = evolve(psi, start), evolve(psi, end)
    w = weight(x, cut, width)
    p1, p2 = abs(first)**2, abs(last)**2
    negative = (negative_weight(psi) if negative_rule=="continuous_bloch"
                else discrete_negative_weight(psi))
    mean = float(np.sum(x*abs(psi)**2))
    rms = float(np.sqrt(np.sum((x-mean)**2*abs(psi)**2)))
    mean1, mean2 = float(w@p1), float(w@p2)
    var1 = float(w*w@p1-mean1*mean1)
    var2 = float(w*w@p2-mean2*mean2)
    increase = mean2-mean1
    witness = increase-negative
    noise_variance = max(var1+var2, 0.)
    # Three independent ensembles: positions at t1,t2 and velocity-sign weight.
    estimated_variance = noise_variance+negative*(1-negative)
    binary_variance=mean1*(1-mean1)+mean2*(1-mean2)+negative*(1-negative)
    edge = (abs(x) >= psi.size//2-32)
    return dict(
        N=psi.size, cut=cut, start=start, end=end, psf_sigma_a=width,
        left_before=mean1, left_after=mean2, left_probability_increase=increase,
        negative_velocity_weight=negative, certified_margin=witness,
        negative_weight_rule=negative_rule,
        norm_error=float(max(abs(p1.sum()-1), abs(p2.sum()-1))),
        initial_centroid_a=mean, initial_rms_a=rms,
        initial_peak_probability=float(np.max(abs(psi)**2)),
        endpoint_edge_mass=float(max(p1[edge].sum(), p2[edge].sum())),
        shots_per_ensemble_5sigma_known_negative_weight=(
            float(25*noise_variance/witness**2) if witness>0 else None),
        shots_per_ensemble_5sigma_estimated_negative_weight=(
            float(25*estimated_variance/witness**2) if witness>0 else None),
        shots_per_ensemble_5sigma_blurred_binary_detector=(
            float(25*binary_variance/witness**2) if witness>0 else None),
    )


def basis(n, q1, q2):
    return np.stack([gaussian(n,q1), gaussian(n,q2)], axis=1)


def best_for_pair(n, q1, q2, width):
    if not (.10 <= q1 < q2 <= np.pi-.10 and q2-q1 >= .60):
        return -1., None, None
    x, q, energy = lattice(n)
    b = basis(n, q1, q2)
    spectrum = np.fft.fft(b,axis=0)
    final = np.fft.ifft(spectrum*np.exp(-1j*energy[:,None]*DURATION),axis=0)
    w = weight(x,0,width)
    gram = b.conj().T@b
    # The normalized Gaussian spectral density has variance 1/(4 sigma^2).
    # Wrapped cross-alias terms are exponentially negligible for sigma=6 and
    # the stated positive carrier range; direct Bloch quadrature checks this.
    def tail(center):
        return .5*(erfc(np.sqrt(2)*SIGMA*center)
                   +erfc(np.sqrt(2)*SIGMA*(np.pi-center)))
    overlap=np.exp(-.5*SIGMA**2*(q1-q2)**2)
    negative=np.array([[tail(q1),overlap*tail((q1+q2)/2)],
                       [overlap*tail((q1+q2)/2),tail(q2)]])
    operator = (final.conj().T@(w[:,None]*final)
                -b.conj().T@(w[:,None]*b)
                -negative)
    operator = (operator+operator.conj().T)/2
    vals, vecs = eigh(operator,gram)
    coefficients = vecs[:,-1]
    psi = b@coefficients
    psi /= np.linalg.norm(psi)
    center = float(np.sum(x*abs(psi)**2))
    rms = float(np.sqrt(np.sum((x-center)**2*abs(psi)**2)))
    # A common external envelope is fixed; actual moments are also constrained.
    if abs(center-CENTER)>.10 or not (5.90 <= rms <= 6.10):
        return -1., None, None
    return float(vals[-1]), coefficients, psi


def optimize_family(n, width):
    grid = np.linspace(.10,np.pi-.10,43)
    candidates = []
    for i,q1 in enumerate(grid):
        for q2 in grid[i+1:]:
            if q2-q1 < .60:
                continue
            value, coeff, _ = best_for_pair(n,q1,q2,width)
            candidates.append((value,float(q1),float(q2)))
    candidates.sort(reverse=True)
    solutions = []
    for _,q1,q2 in candidates[:6]:
        sol = minimize(lambda q: -best_for_pair(n,*q,width)[0],
                       np.array([q1,q2]), method="Nelder-Mead",
                       options={"maxiter":300,"xatol":2e-9,"fatol":2e-12})
        value, coeff, psi = best_for_pair(n,*sol.x,width)
        solutions.append((value,sol.x,coeff,psi))
    value, pair, coeff, psi = max(solutions,key=lambda a:a[0])
    return (dict(
        designed_psf_sigma_a=width,
        q1=float(pair[0]), q2=float(pair[1]),
        coefficients_real=coeff.real.tolist(),
        coefficients_imag=coeff.imag.tolist(),
        objective=value, coarse_pairs=len(candidates),
        resource_constraints=dict(nominal_gaussian_rms_a=SIGMA,
                                  gaussian_center_a=CENTER,
                                  actual_rms_bounds_a=[5.90,6.10],
                                  actual_centroid_tolerance_a=.10,
                                  minimum_carrier_separation=.60,
                                  norm=1.,time_window=[0.,DURATION],
                                  cut_bond=[0,1])),
        psi)


def recreate(record,n, dq1=0., dq2=0., phase_error=0., amplitude_factor=1.):
    coeff=(np.array(record["coefficients_real"])
           +1j*np.array(record["coefficients_imag"]))
    coeff[1]*=amplitude_factor*np.exp(1j*phase_error)
    psi=basis(n,record["q1"]+dq1,record["q2"]+dq2)@coeff
    return psi/np.linalg.norm(psi)


def current_consistency(psi, cut, width, start, end):
    x, _, _ = lattice(psi.size)
    w=weight(x,cut,width)
    dw=np.roll(w,-1)-w
    def flux(t):
        field=evolve(psi,t)
        j=np.imag(field.conj()*np.roll(field,-1))
        return float(dw@j)
    integral,error=quad(flux,start,end,epsabs=2e-13,epsrel=1e-10)
    def edge_flux(t):
        f=evolve(psi,t)
        return float(dw[-1]*np.imag(f[-1].conjugate()*f[0]))
    edge,edge_error=quad(edge_flux,start,end,epsabs=1e-16)
    measured=float(w@(abs(evolve(psi,end))**2-abs(evolve(psi,start))**2))
    return dict(cut=cut,psf_sigma_a=width,start=start,end=end,
                weighted_current_integral=integral,
                direct_probability_increase=measured,
                integral_consistency_error=abs(integral-measured),
                integration_error_estimate=error,
                periodic_second_cut_contribution=edge)


def save_csv(name,rows):
    with (OUT/name).open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)


def blurred_pixel_probabilities(rho,width):
    radius=max(1,int(np.ceil(8*width)))
    offsets=np.arange(-radius,radius+1)
    kernel=ndtr((offsets+.5)/width)-ndtr((offsets-.5)/width)
    return sum(w*np.roll(rho,int(shift)) for shift,w in zip(offsets,kernel))


def shot_validation(record,rng,shots=1000000,trials=1000):
    p1,p2,pneg=(record["left_before"],record["left_after"],
                record["negative_velocity_weight"])
    estimates=(rng.binomial(shots,p2,trials)
               -rng.binomial(shots,p1,trials)
               -rng.binomial(shots,pneg,trials))/shots
    variance=(p1*(1-p1)+p2*(1-p2)+pneg*(1-pneg))/shots
    sd=float(np.sqrt(variance))
    return dict(
        shots_per_each_of_three_ensembles=shots,trials=trials,
        expected_witness=record["certified_margin"],
        predicted_standard_deviation=sd,
        empirical_mean=float(estimates.mean()),
        empirical_standard_deviation=float(estimates.std(ddof=1)),
        fraction_positive=float(np.mean(estimates>0)),
        fraction_above_three_sigma=float(np.mean(estimates>3*sd)),
        model="Independent binary PSF-threshold counts at t1,t2 plus velocity-sign counts")


def incoherent_control(record,width=.5):
    coeff=(np.array(record["coefficients_real"])
           +1j*np.array(record["coefficients_imag"]))
    weights=abs(coeff)**2
    weights/=weights.sum()
    components=[summary(gaussian(1024,q),width=width)
                for q in [record["q1"],record["q2"]]]
    values={key:float(sum(w*r[key] for w,r in zip(weights,components)))
            for key in ["left_before","left_after",
                        "left_probability_increase","negative_velocity_weight",
                        "certified_margin"]}
    return dict(psf_sigma_a=width,component_weights=weights.tolist(),
                initial_centroid_a=CENTER,initial_rms_a=SIGMA,
                preparation="incoherent mixture of the same two normalized carrier states",
                **values)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    sharp_record,sharp=optimize_family(1024,0.)
    aware_record,aware=optimize_family(1024,DESIGN_RESOLUTION)
    designs={"sharp_optimized":sharp_record,"resolution_aware":aware_record}
    print("Designs",json.dumps(designs),flush=True)
    resolutions=[0.,.125,.25,.375,.5,.625,.75,1.,1.5,2.,4.]
    natural=gaussian(4096,np.pi/2,center=0.)
    natural_start=863.666661775626
    natural_end=864.6700074368066
    natural_records=[summary(natural,843,natural_start,natural_end,w)
                     for w in resolutions]

    preparations={
        "single_gaussian":gaussian(1024,np.pi/2),
        "sharp_optimized":sharp,
        "resolution_aware":aware,
        "resolution_aware_positive_projection":projection(aware),
        "negative_velocity_control":gaussian(1024,-np.pi/2),
    }
    prepared=[]
    for name,psi in preparations.items():
        for w in resolutions:
            rule=("finite_periodic_dft" if "projection" in name
                  else "continuous_bloch")
            prepared.append(dict(preparation=name,
                                 **summary(psi,width=w,negative_rule=rule)))
    heldout=[]
    for record_name,record in designs.items():
        for dq1,dq2,phase_error,amplitude_factor in [
                (-.02,0.,0.,1.),(.02,0.,0.,1.),(0.,-.02,0.,1.),
                (0.,.02,0.,1.),(0.,0.,-.10,1.),(0.,0.,.10,1.),
                (0.,0.,0.,.95),(0.,0.,0.,1.05)]:
            psi=recreate(record,1024,dq1,dq2,phase_error,amplitude_factor)
            heldout.append(dict(
                preparation=record_name,dq1=dq1,dq2=dq2,
                phase_error=phase_error,relative_amplitude_factor=amplitude_factor,
                **summary(psi,width=DESIGN_RESOLUTION)))
    checks=[]
    for name,record in designs.items():
        p1=recreate(record,1024)
        p2=recreate(record,2048)
        for w in [0.,.5,1.]:
            r1=summary(p1,width=w)
            r2=summary(p2,width=w)
            checks.append(dict(
                preparation=name,
                doubled_N_witness_error=abs(r1["certified_margin"]
                                            -r2["certified_margin"]),
                doubled_N_rms_error=abs(r1["initial_rms_a"]
                                        -r2["initial_rms_a"]),
                **current_consistency(p1,0,w,0.,1.)))
        fine_modes=[]
        for n in [1024,2048,8192,16384]:
            p=recreate(record,n)
            fine_modes.append(dict(N=n,
                finite_DFT_negative_weight=discrete_negative_weight(p),
                continuous_Bloch_negative_weight=negative_weight(p),
                certified_margin_at_half_site=summary(p,width=.5)["certified_margin"]))
        record["finite_grid_negative_weight_checks"]=fine_modes
        record["Bloch_256_vs_512_error"]=abs(negative_weight(p1,256)
                                            -negative_weight(p1,512))
    natural_large=gaussian(8192,np.pi/2,center=0.)
    natural_checks=[]
    for w in [0.,.25,.5,1.]:
        small=summary(natural,843,natural_start,natural_end,w)
        large=summary(natural_large,843,natural_start,natural_end,w)
        natural_checks.append(dict(
            doubled_N_witness_error=abs(small["certified_margin"]
                                        -large["certified_margin"]),
            **current_consistency(natural,843,w,natural_start,natural_end)))
    projection_checks=[]
    for n in [1024,2048,4096]:
        projected=projection(recreate(aware_record,n))
        projection_checks.append(dict(
            **summary(projected,width=.5,negative_rule="finite_periodic_dft"),
            current_check=current_consistency(projected,0,.5,0.,1.)))
    critical_resolutions=dict(
        natural_fixed_event=float(brentq(
            lambda w:summary(natural,843,natural_start,natural_end,w)["certified_margin"],
            .25,.375,xtol=1e-12)),
        prepared_fixed_event=float(brentq(
            lambda w:summary(aware,width=w)["certified_margin"],
            .5,.625,xtol=1e-12)),
        meaning="Zero of the frozen-state, fixed-cut, fixed-time-window witness; not a universal resolution bound")

    # A finer time series is used for both checking and the viewer data.
    times=np.linspace(0,1,201)
    time_rows=[]
    for t in times:
        row={"time":float(t)}
        for w in [0.,.5,1.]:
            row[f"delta_left_psf_{w:g}"]=summary(
                aware,start=0.,end=float(t),width=w)["left_probability_increase"]
        time_rows.append(row)
    save_csv("natural_psf_scan.csv",natural_records)
    save_csv("prepared_psf_scan.csv",prepared)
    save_csv("heldout_parameter_errors.csv",heldout)
    save_csv("detector_time_trace.csv",time_rows)
    rng=np.random.default_rng(20261021)
    shot_controls={}
    for name,record in [
            ("natural_sharp",natural_records[0]),
            ("natural_half_site",[r for r in natural_records
                                   if r["psf_sigma_a"]==.5][0]),
            ("prepared_half_site",[r for r in prepared
                                   if r["preparation"]=="resolution_aware"
                                   and r["psf_sigma_a"]==.5][0])]:
        shot_controls[name]=shot_validation(record,rng)
    results=dict(
        model="epsilon(q)=1-cos(q), velocity=sin(q); a=J=hbar=1",
        literature_question="Effect of smooth spatial measurement windows on general backflow",
        sources=[
            {"url":"https://arxiv.org/html/2511.10155v2",
             "locator":"Discussion, PDF p.4",
             "scope":"Author-stated general-backflow smooth-window question"},
            {"url":"https://arxiv.org/html/2602.12767v2",
             "locator":"Conclusion",
             "scope":"Fine density fringes challenge fluorescence imaging"}],
        witness="B_l=<W_l>(t2)-<W_l>(t1)-P(sin(q)<0)",
        classical_null=("For nonnegative classical joint position-quasimomentum distributions, "
                        "constant q and v=sin(q), a bounded monotone left weight has "
                        "Delta<W> <= P(v<0). Positive B_l is sufficient to violate that null."),
        scope_limit=("This is an operational lattice extension of a measurement question, "
                     "not a continuum bound, experimental implementation, or proof of novelty."),
        psf="W_l(n)=0.5*erfc((n-cut-0.5)/(sqrt(2)*l)); l=0 is n<=cut",
        natural_event=dict(records=natural_records,checks=natural_checks,
                           comparison="Separate original Gaussian-tail diagnostic; not a resource-matched preparation baseline"),
        designs=designs,prepared_records=prepared,heldout_errors=heldout,
        incoherent_mixture_controls={name:incoherent_control(r)
                                     for name,r in designs.items()},
        verification=checks,
        projection_control_checks=projection_checks,
        critical_psf_sigma_a=critical_resolutions,
        shot_noise_validation=shot_controls,
        shot_noise_seed=20261021,
        projection_control_note=("Hard positive-velocity projection changes the spatial "
                                 "budget and creates long tails. Its finite-periodic "
                                 "DFT result is a diagnostic only and is not ranked as "
                                 "an equal-resource preparation. Principal results use "
                                 "unprojected localized states and continuous Bloch integrals."),
        sampling_noise_model=("Five-sigma normal-approximation estimate for independent "
                              "measurements at t1 and t2; separately report ideal exact-position "
                              "W-weighted variance and actual blurred binary-threshold "
                              "variance p(1-p). A third independent velocity-sign ensemble "
                              "estimates P(v<0). "
                              "M is shots per ensemble, not total shots or camera photons; "
                              "technical noise and PSF calibration uncertainty are omitted."),
        not_tested=["Complete optimization over all states",
                    "Antenna drive or coherent preparation energy",
                    "Detector imperfections beyond a known Gaussian PSF",
                    "Loss, dephasing, interactions, and material-specific spin readout"],
    )
    (OUT/"results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    np.savez_compressed(OUT/"demo_data.npz",x=lattice(1024)[0],
                        initial_aware=aware,initial_sharp=sharp,
                        gaussian=preparations["single_gaussian"])
    plot_results(results,preparations,time_rows)
    write_report(results)
    print(json.dumps({
        "natural":natural_records,
        "design_at_half_site":[r for r in prepared if r["psf_sigma_a"]==.5],
        "max_consistency_error":max(r["integral_consistency_error"] for r in checks+natural_checks),
        "max_doubled_N_error":max(r["doubled_N_witness_error"] for r in checks+natural_checks),
    },indent=2))


def plot_results(results,preparations,time_rows):
    plt.rcParams.update({"font.sans-serif":["Microsoft YaHei","DejaVu Sans"],
                         "axes.unicode_minus":False,"font.size":11,
                         "svg.fonttype":"none"})
    colors={"single_gaussian":"#667384","sharp_optimized":"#d17b35",
            "resolution_aware":"#126c89"}
    labels={"single_gaussian":"单 Gaussian",
            "sharp_optimized":"按锐利窗优化",
            "resolution_aware":"按 0.5a 分辨率优化"}
    fig,axs=plt.subplots(2,2,figsize=(12.5,8.7),layout="constrained")
    natural=results["natural_event"]["records"]
    shown_natural=[r for r in natural if r["psf_sigma_a"]<=1.]
    axs[0,0].plot([r["psf_sigma_a"] for r in shown_natural],
                   [r["certified_margin"] for r in shown_natural],"o-",color="#85539b")
    axs[0,0].axhline(0,color=".5",lw=.8)
    axs[0,0].set(xlim=(0,1.),xlabel="空间 PSF 标准差 / a",
                 ylabel=r"$\Delta\langle W\rangle-P(v<0)$",
                 title="原 Gaussian 拖尾：单独检查测量分辨率")
    for key in colors:
        rows=[r for r in results["prepared_records"] if r["preparation"]==key]
        axs[0,1].plot([r["psf_sigma_a"] for r in rows],
                       [r["certified_margin"] for r in rows],"o-",
                       color=colors[key],label=labels[key])
    mixture=results["incoherent_mixture_controls"]["resolution_aware"]
    axs[0,1].plot([.5],[mixture["certified_margin"]],"s",ms=6,
                   color="#222222",label="同载波非相干混合（0.5a）")
    axs[0,1].axhline(0,color=".5",lw=.8)
    axs[0,1].axvline(.5,color="#126c89",ls=":",alpha=.7)
    axs[0,1].set(xlim=(0,2),xlabel="空间 PSF 标准差 / a",
                 ylabel="一般反流见证",title="同一制备族：针对分辨率优化只带来小幅改进")
    axs[0,1].legend(fontsize=9)
    x=lattice(1024)[0]
    mask=abs(x-CENTER)<=20
    for key in colors:
        axs[1,0].plot(x[mask],abs(preparations[key][mask])**2,
                      color=colors[key],label=labels[key],lw=1.2)
    axs[1,0].axvline(.5,color=".4",ls=":")
    axs[1,0].set(xlabel="位置 / a",ylabel="初始格点概率",
                 title="共同 Gaussian 外包络；实际 RMS 也受约束")
    axs[1,0].legend(fontsize=9)
    for w,col in [(0.,"#d17b35"),(.5,"#126c89"),(1.,"#6f7781")]:
        axs[1,1].plot([r["time"] for r in time_rows],
                       [r[f"delta_left_psf_{w:g}"] for r in time_rows],
                       color=col,label=rf"PSF = {w:g}a")
    neg=summary(preparations["resolution_aware"],width=.5)["negative_velocity_weight"]
    axs[1,1].axhline(neg,color="#b43b3b",ls="--",label=r"$P(v<0)$")
    axs[1,1].set(xlabel=r"$t/(\hbar/J)$",ylabel=r"$\langle W(t)\rangle-\langle W(0)\rangle$",
                 title="有限时间概率增量；超过红线才认证反流")
    axs[1,1].legend(fontsize=9)
    fig.suptitle("有限空间分辨率下的晶格反流：最小闭合测试",fontsize=16)
    for ax in axs.flat:
        ax.grid(alpha=.15)
    fig.savefig(OUT/"summary.png",dpi=150)
    fig.savefig(OUT/"summary.svg")
    plt.close(fig)

    aware=preparations["resolution_aware"]
    fig,axs=plt.subplots(1,2,figsize=(11.5,4.3),layout="constrained")
    true_line,=axs[0].plot([],[],"o-",ms=3,color="#596679",label="逐格点概率")
    blur_line,=axs[0].plot([],[],color="#126c89",lw=2,label="PSF 0.5a 后的显示")
    axs[0].axvline(.5,color="#b43b3b",ls=":",label="固定截面")
    maxp=max(abs(evolve(aware,t)).max()**2 for t in [0.,.5,1.])
    axs[0].set(xlim=(-16,17),ylim=(0,maxp*1.1),xlabel="位置 / a",
               ylabel="格点概率 / 模糊后概率",title="同一波包的有限分辨率读出")
    axs[0].legend(fontsize=9)
    traces={}
    for w,col in [(0.,"#d17b35"),(.5,"#126c89"),(1.,"#6f7781")]:
        line,=axs[1].plot([],[],color=col,label=f"PSF {w:g}a")
        traces[w]=line
    axs[1].axhline(neg,color="#b43b3b",ls="--",label=r"$P(v<0)$")
    vals=[r[f"delta_left_psf_{w:g}"] for r in time_rows for w in [0.,.5,1.]]
    lo,hi=min(vals),max(vals)
    axs[1].set(xlim=(0,1),ylim=(lo-.1*(hi-lo),hi+.12*(hi-lo)),
               xlabel=r"$t/(\hbar/J)$",ylabel="左侧加权概率增量",
               title="图中每条曲线使用自己的固定 PSF")
    axs[1].legend(fontsize=9)
    title=fig.suptitle("",fontsize=14)
    frames=[]
    viewer=[]
    for index,t in enumerate(np.linspace(0,1,51)):
        rho=abs(evolve(aware,t))**2
        blurred=blurred_pixel_probabilities(rho,.5)
        true_line.set_data(x,rho)
        blur_line.set_data(x,blurred)
        subset=[r for r in time_rows if r["time"]<=t+1e-12]
        for w,line in traces.items():
            line.set_data([r["time"] for r in subset],
                           [r[f"delta_left_psf_{w:g}"] for r in subset])
        title.set_text(rf"两载波制备：$t={t:.2f}\hbar/J$；固定归一化和纵轴")
        fig.canvas.draw()
        image=Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[...,:3].copy())
        if index in [0,25,50]:
            image.save(OUT/f"demo_frame_{index:02d}.png")
        frames.append(image.convert("P",palette=Image.Palette.ADAPTIVE,colors=192))
        viewer.append(dict(time=float(t),
                           probability=rho[mask].tolist(),
                           blurred_probability=blurred[mask].tolist()))
    frames[0].save(OUT/"demo.gif",save_all=True,append_images=frames[1:],
                   duration=[80]*50+[1500],loop=0,optimize=False,disposal=2)
    plt.close(fig)
    with Image.open(OUT/"demo.gif") as im:
        assert im.n_frames==51
        for frame in range(im.n_frames):
            im.seek(frame)
            im.load()
    (OUT/"viewer_data.json").write_text(json.dumps(
        dict(x=x[mask].tolist(),frames=viewer,time_trace=time_rows)),
        encoding="utf-8")


def write_report(results):
    prepared=results["prepared_records"]
    chosen=[r for r in prepared if r["preparation"]=="resolution_aware"
            and r["psf_sigma_a"]==.5][0]
    sharp=[r for r in prepared if r["preparation"]=="sharp_optimized"
           and r["psf_sigma_a"]==.5][0]
    baseline=[r for r in prepared if r["preparation"]=="single_gaussian"
              and r["psf_sigma_a"]==.5][0]
    nat0=results["natural_event"]["records"][0]
    nat05=[r for r in results["natural_event"]["records"]
           if r["psf_sigma_a"]==.5][0]
    held=[r["certified_margin"] for r in results["heldout_errors"]
          if r["preparation"]=="resolution_aware"]
    text=f"""有限空间分辨率下的晶格反流最小测试

来源：Paterek and Goussev, PRL 136, 090202 (2026), Discussion p.4，提出平滑空间测量窗对 general backflow 的影响问题。Chen and Tang, PRA 113, 063304 (2026)，讨论密度细条纹对荧光成像的困难。这里将问题具体化到既有自由余弦晶格，未声称解决原文的完整连续体系优化。

模型与判据：
epsilon(q)=1-cos(q)，v(q)=sin(q)，单位 a=J=hbar=1。
W_l(n)=0.5 erfc[(n-cut-0.5)/(sqrt(2)l)]，l=0 是锐利左半空间。
检测见证 B_l=Delta<W_l>-P(v<0)。自由经典正分布、守恒 q、单调有界左窗满足 B_l<=0，故正值是该经典零假设的充分反例；非正值不能证明不存在微观反流。

分开的两项测试：
1. 原自然 Gaussian 后尾部事件，cut=843，t=863.6666618..864.6700074。
   锐利窗 B={nat0['certified_margin']:.9g}；
   PSF=0.5a 时 B={nat05['certified_margin']:.9g}。
   这是原事件的分辨率诊断，不与新制备几何作等资源性能比。
2. 固定 cut=0、t=0..1、sigma=6a 外包络、中心0.5a、归一化1的单 Gaussian / 两载波族。
   两载波实际 RMS 限制5.90..6.10a、质心偏移不超过0.10a、载波间距至少0.60。
   在 PSF=0.5a 下：
   单 Gaussian B={baseline['certified_margin']:.9g}；
   按锐利窗优化的两载波 B={sharp['certified_margin']:.9g}；
   按该分辨率优化的两载波 B={chosen['certified_margin']:.9g}。
   后者负速度谱权重={chosen['negative_velocity_weight']:.9g}，
   实际初始 RMS={chosen['initial_rms_a']:.9g}a，
   质心={chosen['initial_centroid_a']:.9g}a。
   未参与优化的单参数误差测试（载波±0.02rad、相对相位±0.10rad、相对幅度±5%）的 B 范围为 {min(held):.9g}..{max(held):.9g}。
   该半格点分辨率再优化相对锐利窗设计仅改善约 {(chosen['certified_margin']/sharp['certified_margin']-1)*100:.3f}%，不应称作大幅优势。
   相同两个载波、相同权重改为非相干混合，半格点见证变为 {results['incoherent_mixture_controls']['resolution_aware']['certified_margin']:.9g}；正见证需要相干干涉，不是两股普通向右概率流相加。
   固定态、固定截面和固定时间窗中，见证变号的PSF标准差：原拖尾约 {results['critical_psf_sigma_a']['natural_fixed_event']:.6g}a，新制备约 {results['critical_psf_sigma_a']['prepared_fixed_event']:.6g}a。这不是对任意态的普适分辨率上限。

采样可见性：
理想的精确位置测量后按W加权，正态近似5sigma要求每组约 {chosen['shots_per_ensemble_5sigma_estimated_negative_weight']:.6g} 次；真实PSF模糊后二元阈值读出的Bernoulli方差更大，要求每组约 {chosen['shots_per_ensemble_5sigma_blurred_binary_detector']:.6g} 次。共三组独立样本（t1、t2及负速度谱权重）；这是粒子/激发重复制备计数模型，不是CCD相机光子数，也没有包含技术噪声及PSF标定误差。固定seed20261021的1000次重复二项计数模拟另保存在JSON。

验证：
负速度权重主要使用局域初态的连续Bloch谱Gauss-Legendre积分，并核对256/512节点；有限N的DFT半区求和排除精确零速度端点，另记录至N=16384的趋近过程及残余端点误差（此时resolution-aware态仍约有0.77%的负谱权重误差，未用于主结论）。保存了严格正速度投影、负速度单Gaussian的否定对照，N加倍，固定窗加权流积分与概率增量一致性，以及第二周期截面的通量。硬投影产生长尾并增加RMS，所以只作诊断，不列为等空间预算下的优势。不同PSF扫描和参数误差测试不重新优化。全部实际数值见results.json。

未完成：任意态优化、真实天线/驱动功率限制、实际材料和探测器、损耗与退相干。共同Gaussian外包络和RMS约束只代表空间预算，不等于完整的相同实验制备资源。

demo.gif展示同一有限时间事件的格点概率、PSF模糊显示与加权左侧概率增量；曲线只有超过P(v<0)才认证一般反流。
"""
    (OUT/"report.txt").write_text(text,encoding="utf-8")


if __name__=="__main__":
    main()
