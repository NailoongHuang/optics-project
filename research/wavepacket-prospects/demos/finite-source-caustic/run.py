"""Finite-source scalar caustic test using Wartelle et al. Eq. (4).

The model propagates a matched, finite angular spectrum on the actual
isofrequency contour. It is not a magnetic-susceptibility/antenna calculation.
All lengths are in film thickness d and frequencies in omega_M.
"""
from pathlib import Path
import json
import hashlib

import numpy as np
import mpmath as mp
from scipy.interpolate import PchipInterpolator
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

OUT = Path(__file__).resolve().parent
ETA = 0.10253664614147
H = 1.15e-21
NU_HIGH = 0.315279504
NU_REGULAR = .95 * NU_HIGH
N = 131072
PMAX = 8.
CUT = .27
BW = .10
ZMAX = 100000.


def curve(r, nu):
    r = np.asarray(r)
    xi = 1 + np.expm1(-r) / r
    aa = H + ETA**2 * r*r
    cc = (aa*(1+aa) + xi*(1-xi) - nu*nu) / (xi*(1-xi+aa))
    with np.errstate(invalid="ignore"):
        return r*np.sqrt(cc), r*np.sqrt(1-cc), cc


def velocity(r, nu):
    x, y, _ = curve(r, nu)
    c, s = x/r, y/r
    xi = 1 + np.expm1(-r)/r
    xp = (1 - np.exp(-r)*(1+r)) / r**2
    aa = H + ETA**2*r*r
    ap = 2*ETA**2*r
    fr = ap*(2*aa+1) - (xp*(1-2*xi+aa)+xi*ap)*c*c + xp*(1-2*xi)
    fp = 2*xi*(1-xi+aa)*c*s
    return np.array([(fr*c-fp*s/r)/(2*nu),
                     (fr*s+fp*c/r)/(2*nu)])


def critical_radius(nu, bracket):
    mp.mp.dps = 60
    eta, hh, vv = mp.mpf(str(ETA)), mp.mpf(str(H)), mp.mpf(str(nu))
    def xy(rr):
        xi = 1 + mp.expm1(-rr)/rr
        aa = hh + eta**2*rr**2
        cc = (aa*(1+aa)+xi*(1-xi)-vv**2)/(xi*(1-xi+aa))
        return rr*mp.sqrt(cc), rr*mp.sqrt(1-cc)
    def numerator(rr):
        xp = mp.diff(lambda z: xy(z)[0], rr)
        yp = mp.diff(lambda z: xy(z)[1], rr)
        return (xp*mp.diff(lambda z: xy(z)[1], rr, 2)
                - yp*mp.diff(lambda z: xy(z)[0], rr, 2))
    rr = mp.findroot(numerator, tuple(mp.mpf(str(b)) for b in bracket),
                     solver="anderson")
    xp = mp.diff(lambda z: xy(z)[0], rr)
    yp = mp.diff(lambda z: xy(z)[1], rr)
    tangent = np.array([float(xp), float(yp)])
    tangent /= np.linalg.norm(tangent)
    return float(rr), tangent, float(numerator(rr))


def frame(nu, rc, tangent=None):
    if tangent is None:
        dr = 1e-5
        tangent = np.array(curve(rc+dr, nu)[:2])-np.array(curve(rc-dr, nu)[:2])
        tangent /= np.linalg.norm(tangent)
    normal = np.array([-tangent[1], tangent[0]])
    center = np.array(curve(rc, nu)[:2])
    return dict(nu=nu, radius=rc, tangent=tangent, normal=normal, center=center)


def spectrum_grid(n=N, pmax=PMAX):
    dp = 2*pmax/n
    p = (np.arange(n)-n//2)*dp
    dx = np.pi/pmax
    x = (np.arange(n)-n//2)*dx
    return p, x, dp, dx


def input_spectrum(p, dp, bw):
    inside = np.abs(p) < CUT
    a = np.zeros(p.shape)
    u = p[inside]/CUT
    # Compact C-infinity taper gives finite RMS and identical finite support.
    a[inside] = np.exp(-p[inside]**2/(4*bw*bw) + 1 - 1/(1-u*u))
    return a/np.sqrt(np.sum(a*a)*dp)


def branch_arrays(fr, p, nu=None, contour_points=80001):
    nu = fr["nu"] if nu is None else nu
    rr = np.linspace(.01, 6., contour_points)
    xx, yy, cc = curve(rr, nu)
    valid = (cc > 0) & (cc < 1)
    rr, xx, yy = rr[valid], xx[valid], yy[valid]
    kk = np.stack([xx, yy])
    delta = kk - fr["center"][:, None]
    transverse = fr["tangent"] @ delta
    longitudinal = fr["normal"] @ delta
    vn = fr["normal"] @ velocity(rr, nu)
    # Select the monotone outgoing branch around the source's transverse center.
    keep = (transverse > -.29) & (transverse < .35) & (vn > 0)
    rr, transverse = rr[keep], transverse[keep]
    longitudinal, vn = longitudinal[keep], vn[keep]
    if np.any(np.diff(transverse) <= 0):
        raise ValueError("Selected angular-spectrum branch is not monotone")
    active = np.abs(p) < CUT
    if transverse[0] >= -CUT or transverse[-1] <= CUT:
        raise ValueError(f"Finite spectrum not supported: {transverse[[0,-1]]}")
    phase = np.zeros(p.shape)
    speed = np.ones(p.shape)
    phase[active] = PchipInterpolator(transverse, longitudinal)(p[active])
    speed[active] = PchipInterpolator(transverse, vn)(p[active])
    return phase, speed, dict(p_branch_min=float(transverse[0]),
                             p_branch_max=float(transverse[-1]),
                             minimum_normal_speed=float(speed[active].min()))


def propagate(a, phase, speed, z, gamma, dp):
    evolved = a*np.exp(1j*phase*z-gamma*z/speed)
    field = (np.fft.fftshift(np.fft.ifft(np.fft.ifftshift(evolved)))
             *len(a)*dp/np.sqrt(2*np.pi))
    return field


def metrics(field, x, dx, half_window):
    prob = np.abs(field)**2
    total = np.sum(prob)*dx
    peak_index = int(np.argmax(prob))
    half = prob[peak_index]/2
    left = peak_index
    right = peak_index
    while left > 0 and prob[left] >= half:
        left -= 1
    while right < len(prob)-1 and prob[right] >= half:
        right += 1
    xl = np.interp(half, prob[left:left+2], x[left:left+2])
    xr = np.interp(half, prob[right-1:right+1][::-1], x[right-1:right+1][::-1])
    mean = np.sum(x*prob)*dx/total if total else np.nan
    rms = np.sqrt(np.sum((x-mean)**2*prob)*dx/total) if total else np.nan
    in_window = np.abs(x) < half_window
    window_x = np.r_[-half_window, x[in_window], half_window]
    window_prob = np.r_[np.interp(-half_window,x,prob), prob[in_window],
                        np.interp(half_window,x,prob)]
    return dict(norm=float(total), peak=float(prob[peak_index]),
                peak_position=float(x[peak_index]), fwhm=float(xr-xl),
                rms=float(rms), receiving_power=float(np.trapezoid(window_prob,window_x)),
                edge_power=float((prob[:512].sum()+prob[-512:].sum())*dx))


def main():
    OUT.mkdir(exist_ok=True, parents=True)
    rh, th, residual_h = critical_radius(NU_HIGH, [.71, .74])
    ro, to, residual_o = critical_radius(NU_REGULAR, [.43, .44])
    frames = dict(higher=frame(NU_HIGH, rh, th),
                  ordinary=frame(NU_REGULAR, ro, to),
                  away=frame(NU_HIGH, 1.3))
    p, x, dp, dx = spectrum_grid()
    a = input_spectrum(p, dp, BW)
    initial = propagate(a, p*0, p*0+1, 0, 0, dp)
    initial_rms = np.sqrt(np.sum(x*x*np.abs(initial)**2)*dx)
    half_window = 2*initial_rms
    initial_m = metrics(initial, x, dx, half_window)
    branches = {key: branch_arrays(fr, p) for key, fr in frames.items()}
    zvalues = np.unique(np.r_[0., np.geomspace(10., ZMAX, 71)])
    tracks = {}
    for key, fr in frames.items():
        phase, speed, info = branches[key]
        tracks[key] = []
        for z in zvalues:
            field = propagate(a, phase, speed, z, 0., dp)
            tracks[key].append(dict(z=float(z), **metrics(field, x, dx, half_window)))
    checkpoints = {}
    for key in frames:
        phase, speed, _ = branches[key]
        checkpoints[key] = [
            dict(z=z, **metrics(propagate(a, phase, speed, z, 0., dp),
                               x, dx, half_window))
            for z in [0., 1000., 10000., 30000., 100000.]]

    bandwidth_scan = []
    for bw in [.025, .05, .075, .10, .125]:
        ab = input_spectrum(p, dp, bw)
        init = propagate(ab, p*0, p*0+1, 0, 0, dp)
        sr = np.sqrt(np.sum(x*x*np.abs(init)**2)*dx)
        values = {}
        for key in ["higher", "ordinary"]:
            phase, speed, _ = branches[key]
            values[key] = metrics(propagate(ab, phase, speed, 10000, 0, dp),
                                  x, dx, 2*sr)
        bandwidth_scan.append(dict(spectral_parameter=bw, input_rms=sr,
                                   higher=values["higher"], ordinary=values["ordinary"],
                                   peak_ratio=values["higher"]["peak"]/values["ordinary"]["peak"]))

    damping_scan = []
    for gamma in [0., 1e-6, 3e-6, 1e-5, 3e-5, 1e-4]:
        values = {}
        for key in ["higher", "ordinary"]:
            phase, speed, _ = branches[key]
            values[key] = metrics(propagate(a, phase, speed, 10000, gamma, dp),
                                  x, dx, half_window)
        damping_scan.append(dict(gamma_over_omegaM=gamma,
                                   higher=values["higher"], ordinary=values["ordinary"],
                                   peak_ratio=values["higher"]["peak"]/values["ordinary"]["peak"]))
    detuning_scan = []
    for detuning in [-.01, -.005, -.002, 0., .002, .005, .01]:
        phase, speed, info = branch_arrays(frames["higher"], p, NU_HIGH*(1+detuning))
        mm = metrics(propagate(a, phase, speed, 10000, 0., dp),
                     x, dx, half_window)
        detuning_scan.append(dict(relative_frequency_detuning=detuning, **mm))

    flux = {}
    for key in frames:
        phase, speed, _ = branches[key]
        input_flux = float(np.sum(speed*a*a)*dp)
        mm = checkpoints[key][2]
        flux[key] = dict(input_scalar_norm=1., input_normal_flux=input_flux,
                         peak_at_z10000_equal_input_flux=mm["peak"]/input_flux,
                         receiving_power_at_z10000_equal_input_flux=mm["receiving_power"]/input_flux)

    convergence = []
    for key in ["higher", "ordinary"]:
        phase, speed, _ = branches[key]
        base = metrics(propagate(a, phase, speed, ZMAX, 0, dp), x, dx, half_window)
        phase2, speed2, _ = branch_arrays(frames[key], p, contour_points=160001)
        refined_c = metrics(propagate(a, phase2, speed2, ZMAX, 0, dp),
                            x, dx, half_window)
        p2, x2, dp2, dx2 = spectrum_grid(2*N)
        a2 = input_spectrum(p2, dp2, BW)
        ph2, sp2, _ = branch_arrays(frames[key], p2, contour_points=160001)
        refined = metrics(propagate(a2, ph2, sp2, ZMAX, 0, dp2),
                          x2, dx2, half_window)
        p3,x3,dp3,dx3=spectrum_grid(2*N,pmax=2*PMAX)
        a3=input_spectrum(p3,dp3,BW)
        ph3,sp3,_=branch_arrays(frames[key],p3,contour_points=160001)
        finer_x=metrics(propagate(a3,ph3,sp3,ZMAX,0,dp3),x3,dx3,half_window)
        convergence.append(dict(case=key,
            contour_refinement_peak_relative_error=abs(base["peak"]/refined_c["peak"]-1),
            spectral_refinement_peak_relative_error=abs(refined_c["peak"]/refined["peak"]-1),
            transverse_grid_peak_relative_error=abs(refined_c["peak"]/finer_x["peak"]-1),
            transverse_grid_receiver_absolute_error=abs(refined_c["receiving_power"]-finer_x["receiving_power"]),
            receiver_power_absolute_error=abs(base["receiving_power"]-refined["receiving_power"]),
            max_norm_error=max(abs(base["norm"]-1),abs(refined["norm"]-1)),
            edge_power=base["edge_power"]))
    # Initial spectrum is exactly identical in all geometry comparisons.
    all_norm_error = max(abs(row["norm"]-1) for rows in tracks.values() for row in rows)
    assert all_norm_error < 1e-11
    assert max(r["edge_power"] for rows in tracks.values() for r in rows) < 1e-7
    assert max(row["contour_refinement_peak_relative_error"] for row in convergence) < 1e-4
    assert max(row["spectral_refinement_peak_relative_error"] for row in convergence) < 1e-4

    result = dict(
        source=dict(arxiv="2301.01220v1", equation=4, figure=13,
                    outlook="Section III.D, PDF p.13: finite-source higher-order amplitude enhancement left unquantified",
                    eta=ETA, h=H, near_higher_frequency=NU_HIGH, ordinary_frequency=NU_REGULAR),
        model="Scalar outgoing angular-spectrum propagation on the actual dipole-exchange isofrequency contour; not a susceptibility or antenna-response calculation.",
        units=dict(position="d", frequency="omega_M", spectral_coordinate="k_t*d",
                   propagation="central group-velocity normal"),
        normalization="Identical finite Gaussian transverse spectrum with compact taper and integral |A|^2 dp=1; equal-normal-flux rescaling additionally reported.",
        spectrum=dict(N=N, transverse_p_max=PMAX, compact_support=CUT,
                      gaussian_parameter=BW, input_rms=float(initial_rms),
                      receiving_half_width=float(half_window)),
        geometry={key: dict(nu=fr["nu"], radius=fr["radius"],
                            angle_k_deg=float(np.degrees(np.arctan2(fr["center"][1],fr["center"][0]))),
                            angle_velocity_deg=float(np.degrees(np.arctan2(fr["normal"][1],fr["normal"][0]))),
                            central_group_speed=float(np.linalg.norm(velocity(fr["radius"],fr["nu"]))),
                            branch=branches[key][2]) for key,fr in frames.items()},
        curvature_root_residuals=dict(higher=residual_h, ordinary=residual_o),
        initial=initial_m, checkpoints=checkpoints, tracks=tracks,
        bandwidth_scan=bandwidth_scan, damping_scan=damping_scan,
        detuning_scan=detuning_scan, equal_normal_flux_sensitivity=flux,
        convergence=convergence, maximum_lossless_norm_error=all_norm_error,
        discarded_small_box_checks=[
            dict(N=32768,z=100000,ordinary_edge_power=0.00013066122741699053,
                 decision="Rejected for transverse FFT wraparound"),
            dict(N=65536,z=100000,ordinary_edge_power=4.4490291365264873e-7,
                 decision="Rejected; N enlarged again to 131072")
        ],
        caveats=[
            "The published high-order parameter set is approximate; called near-higher-order throughout.",
            "Same scalar modal norm is not automatically equal actual microwave power; full susceptibility, ellipticity and antenna matching are absent.",
            "Damping is phenomenological frequency-independent temporal amplitude decay gamma, producing exp(-gamma*z/v_normal).",
            "This is a monochromatic beam calculation, not a two-dimensional localized pulse.",
            "Each best-point comparison is steered to its own caustic direction; the detuning test holds the nominal high-order source spectrum and detector axis fixed.",
            "No novelty or experimental gain claim is made."
        ])
    (OUT/"results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2),encoding="utf-8")
    plot_summary(result, x, p, a, dp, dx, half_window, branches,frames)
    print(json.dumps(dict(initial_rms=initial_rms, checkpoints=checkpoints,
                          damping=damping_scan, detuning=detuning_scan,
                          convergence=convergence),ensure_ascii=False,indent=2))


def plot_summary(result, x, p, a, dp, dx, half_window, branches,frames):
    styles=dict(higher=("#207e6a","近高阶 caustic"),ordinary=("#c26432","普通 caustic"),
                away=("#637d9d","离开 caustic"))
    with plt.rc_context({"font.family":"sans-serif",
                         "font.sans-serif":["Microsoft YaHei","DejaVu Sans"],
                         "axes.unicode_minus":False,"font.size":12,"svg.fonttype":"none"}):
        fig,axs=plt.subplots(2,2,figsize=(12.8,9.0),layout="constrained")
        for key,rows in result["tracks"].items():
            col,label=styles[key]
            axs[0,0].semilogx([r["z"] for r in rows[1:]],
                              [r["peak"]/result["initial"]["peak"] for r in rows[1:]],
                              color=col,label=label)
            phase,speed,_=branches[key]
            f=propagate(a,phase,speed,10000,0,dp)
            keep=np.abs(x)<160
            axs[0,1].plot(x[keep],np.abs(f[keep])**2/result["initial"]["peak"],
                          color=col,label=label)
        axs[0,0].set(xlabel=r"$z/d$",ylabel="峰值 / 共同初始峰值",title="同一有限角谱：几何保形优势")
        axs[0,0].legend()
        axs[0,1].axvspan(-half_window,half_window,color="grey",alpha=.10)
        axs[0,1].set(xlabel=r"$x_\perp/d$",ylabel="强度 / 共同初始峰值",title=r"固定色标截面，$z=10^4d$")
        bw=result["bandwidth_scan"]
        axs[1,0].plot([r["input_rms"] for r in bw],[r["peak_ratio"] for r in bw],"o-",color="#207e6a")
        axs[1,0].axhline(1,color="grey",lw=.8)
        axs[1,0].set(xlabel=r"共同输入 RMS 宽度 / $d$",ylabel="近高阶 / 普通：峰值比",
                      title="有限孔径改变可见优势")
        damp=result["damping_scan"]
        axs[1,1].semilogx([r["gamma_over_omegaM"] for r in damp[1:]],
                          [r["peak_ratio"] for r in damp[1:]],"o-",color="#8a518e")
        axs[1,1].axhline(1,color="grey",lw=.8)
        axs[1,1].set(xlabel=r"现象学振幅衰减率 $\Gamma/\omega_M$",ylabel="近高阶 / 普通：峰值比",
                      title="较慢群速付出更大的损耗代价")
        for ax in axs.flat:ax.grid(alpha=.15)
        fig.suptitle("有限激发源的 caustic 子测试：实际等频线，归一化标量角谱\n不含真实天线耦合与磁化率；近高阶参数来自 Wartelle 2023 Fig.13",fontsize=15)
        fig.savefig(OUT/"summary.png",dpi=150)
        fig.savefig(OUT/"summary.svg")
        plt.close(fig)

        fig,axs=plt.subplots(1,2,figsize=(11.5,4.4),layout="constrained")
        keep=np.abs(x)<90
        for det,col in [(-.005,"#c26432"),(0.,"#207e6a"),(.005,"#637d9d")]:
            phase,speed,_=branch_arrays(frames["higher"],p,NU_HIGH*(1+det))
            f=propagate(a,phase,speed,10000,0,dp)
            axs[0].plot(x[keep],abs(f[keep])**2/result["initial"]["peak"],
                         color=col,label=f"频率偏移 {100*det:+.1f}%")
        axs[0].axvspan(-half_window,half_window,color="grey",alpha=.15,label="固定接收窗")
        axs[0].set(xlabel=r"$x_\perp/d$",ylabel="强度 / 初始峰值",
                    title=r"波束仍很窄，但可能偏离探测器：$z=10^4d$")
        axs[0].legend(fontsize=10)
        det=result["detuning_scan"]
        axs[1].plot([r["relative_frequency_detuning"]*100 for r in det],
                    [r["receiving_power"] for r in det],"o-",color="#207e6a")
        axs[1].set(xlabel="相对频率偏移 (%)",ylabel="固定接收窗中的标量功率",
                    title="源和接收轴保持在标称近高阶设置")
        for ax in axs:ax.grid(alpha=.15)
        fig.suptitle("失谐检验区分“峰值增强”与“接收信号增强”",fontsize=15)
        fig.savefig(OUT/"detuning.png",dpi=150)
        fig.savefig(OUT/"detuning.svg")
        plt.close(fig)

        fig,axs=plt.subplots(1,2,figsize=(11.5,4.5),layout="constrained")
        lines={}
        keep=np.abs(x)<160
        for key in ["higher","ordinary","away"]:
            c,l=styles[key];lines[key],=axs[0].plot(x[keep],np.abs(initial_like(a,dp))[keep]**2/result["initial"]["peak"],color=c,label=l)
        axs[0].set(xlim=(-160,160),ylim=(0,1.05),xlabel=r"$x_\perp/d$",ylabel="强度 / 初始峰值")
        axs[0].legend(loc="upper right",fontsize=10)
        for key,rows in result["tracks"].items():
            c,l=styles[key];axs[1].plot([r["z"] for r in rows],[r["receiving_power"] for r in rows],color=c,label=l)
        axs[1].set(xlim=(0,ZMAX),ylim=(0,1),xlabel=r"$z/d$",ylabel="固定接收窗中的标量功率")
        marker=axs[1].axvline(0,color="grey",ls="--")
        label=fig.suptitle("",fontsize=14)
        images=[]
        for z in np.linspace(0,ZMAX,51):
            for key in lines:
                phase,speed,_=branches[key]
                f=propagate(a,phase,speed,float(z),0,dp)
                lines[key].set_ydata(abs(f[keep])**2/result["initial"]["peak"])
            marker.set_xdata([z,z])
            label.set_text(f"相同有限输入，逐距离比较：z/d = {z:.0f}\n标量等频线模型；无逐帧归一化")
            fig.canvas.draw()
            images.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[...,:3].copy()))
        palette=images[0].quantize(colors=192)
        quantized=[im.quantize(palette=palette) for im in images]
        quantized[0].save(OUT/"demo.gif",save_all=True,append_images=quantized[1:],
                          duration=[400]+[100]*49+[1200],loop=0,disposal=2)
        plt.close(fig)
        with Image.open(OUT/"demo.gif") as im:
            for n in range(im.n_frames):im.seek(n);im.load()
            assert im.n_frames==51


def initial_like(a,dp):
    return np.fft.fftshift(np.fft.ifft(np.fft.ifftshift(a)))*len(a)*dp/np.sqrt(2*np.pi)


if __name__=="__main__":
    main()
