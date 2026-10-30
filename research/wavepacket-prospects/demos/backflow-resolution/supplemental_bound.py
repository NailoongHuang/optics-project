"""Evaluate a tighter finite-PSF classical bound for frozen prepared states.

This adds no optimization and does not modify the original figures or result
records. Units are a=J=hbar=1; the source is the existing run.py preparation.
"""
from pathlib import Path
import importlib.util
import json

import numpy as np
from scipy.special import erf

OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("base_demo",OUT/"run.py")
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def velocity_moments(psi,psf,time_interval,order=256):
    x,_,_=base.lattice(psi.size)
    keep=abs(psi)>1e-16
    nodes,weights=np.polynomial.legendre.leggauss(order)
    q=.5*np.pi*(nodes-1)
    amplitude=np.exp(-1j*q[:,None]*x[None,keep])@psi[keep]
    probability_weights=.25*weights*abs(amplitude)**2
    g=(np.ones_like(q) if psf==0 else
       erf(abs(np.sin(q))*time_interval/(2*np.sqrt(2)*psf)))
    mean=float(probability_weights@g)
    second=float(probability_weights@(g*g))
    return dict(bound=mean,weighted_velocity_second_moment=second,
                weighted_velocity_variance=max(0.,second-mean*mean),
                negative_velocity_probability=float(probability_weights.sum()))


def evaluate(psi,psf):
    measured=base.summary(psi,width=psf)
    v256=velocity_moments(psi,psf,1.,256)
    v512=velocity_moments(psi,psf,1.,512)
    tight=measured["left_probability_increase"]-v512["bound"]
    p1,p2=measured["left_before"],measured["left_after"]
    binary_position_variance=p1*(1-p1)+p2*(1-p2)
    variance=binary_position_variance+v512["weighted_velocity_variance"]
    return dict(
        psf_sigma_a=psf,time_interval=1.,
        left_probability_increase=measured["left_probability_increase"],
        original_sign_bound=measured["negative_velocity_weight"],
        original_witness=measured["certified_margin"],
        tighter_classical_bound=v512["bound"],
        tighter_witness=tight,
        weighted_velocity_variance=v512["weighted_velocity_variance"],
        weighted_velocity_second_moment=v512["weighted_velocity_second_moment"],
        quadrature_256_vs_512_bound_error=abs(v256["bound"]-v512["bound"]),
        shots_per_each_of_three_ensembles_5sigma=(
            25*variance/tight**2 if tight>0 else None),
        original_sign_test_shots_per_ensemble=measured[
            "shots_per_ensemble_5sigma_blurred_binary_detector"],
    )


def main():
    initial=json.loads((OUT/"results.json").read_text())
    records={}
    for name in ["sharp_optimized","resolution_aware"]:
        psi=base.recreate(initial["designs"][name],1024)
        records[name]=[evaluate(psi,w) for w in [0.,.5,1.,2.]]
    result=dict(
        source="Our analytic refinement of the same classical null; not attributed as an authors' theorem or novelty claim.",
        hypothesis=("Classical joint f(x,q)>=0, conserved q, straight trajectories "
                    "x(t2)=x(t1)+v(q)*Delta_t, v(q)=sin(q), known Gaussian left-window PSF."),
        derivation=("For v<0, maximizing W_l(x+v*Delta_t)-W_l(x) over initial x "
                    "puts the detector boundary at the midpoint of the displacement, "
                    "and gives erf(|v|*Delta_t/(2*sqrt(2)*l)). For v>=0 the gain "
                    "is nonpositive. Integrating the negative-velocity maxima yields C_l."),
        formula="C_l=integral_(sin(q)<0) rho(q)*erf(|sin(q)|*Delta_t/(2*sqrt(2)*l)) dq; B_tight=Delta<W>-C_l.",
        limits=("As l->0, C_l->P(v<0). For |v|*Delta_t << l, "
                "C_l is approximately Delta_t*<|v| 1_(v<0)>/(sqrt(2*pi)*l). "
                "This is a measurement bound, not a continuum Bracken-Melloy bound."),
        scope=("Frozen coefficients, same source envelope, cut and time window as base test. "
               "Only PSF points already present in the original test are evaluated. "
               "No reoptimization, new state family, or altered main demo."),
        noise_model=("Independent blurred binary left/right position readouts at t1 and t2 "
                     "have variances p1(1-p1) and p2(1-p2). A third independent "
                     "velocity-resolved ensemble estimates g(v)=1_(v<0)*erf(...), "
                     "with variance <g^2>-<g>^2. The shot count assumes velocity "
                     "resolution sufficient to compute g, known PSF, no calibration "
                     "or technical noise, and a normal-approximation 5-sigma threshold."),
        records=records,
    )
    (OUT/"supplemental_bound_results.json").write_text(
        json.dumps(result,indent=2),encoding="utf-8")
    chosen=records["resolution_aware"][1]
    sharp=records["sharp_optimized"][1]
    report=f"""平滑窗口的更紧经典上界补充

这是一条在本轮经典零假设下直接推导的测量界，不归于原作者定理，也不作新颖性主张。

对于v<0且位移v Delta_t，Gaussian左窗的最大经典增量为
erf(|v| Delta_t/(2 sqrt(2) ell))。
故 C_ell=∫_(v<0) rho(q) erf(|v(q)| Delta_t/(2 sqrt(2) ell)) dq，
更紧见证为 Delta<W>-C_ell。ell→0时恢复P(v<0)界。

沿用冻结的resolution-aware态、cut0、t0..1、PSF=0.5a：
Delta<W>={chosen['left_probability_increase']:.12g}
原负速度权重界={chosen['original_sign_bound']:.12g}
更紧上界 C_ell={chosen['tighter_classical_bound']:.12g}
原见证={chosen['original_witness']:.12g}
更紧见证={chosen['tighter_witness']:.12g}

若第三组实验可解析速度并估计g(v)，而非仅判断符号，
g的方差={chosen['weighted_velocity_variance']:.12g}。
加上两个时刻的模糊二元位置读出，5sigma估计每组需要
{chosen['shots_per_each_of_three_ensembles_5sigma']:.7g}次，共三组；
原符号判据为每组{chosen['original_sign_test_shots_per_ensemble']:.7g}次。
这不是免费改进：要求速度分辨读出及已知PSF，技术噪声和标定误差未包含。

冻结态之间的排序也改变了：原锐利窗优化态在更紧判据下给
B_tight={sharp['tighter_witness']:.12g}，每组约
{sharp['shots_per_each_of_three_ensembles_5sigma']:.7g}次，比原先按宽松符号判据命名的
resolution-aware态更好。没有按新判据再优化；这说明选择测量见证本身会影响设计目标，
不能将旧判据下0.91%的改进推广为新判据下的优势。

没有重新优化态或扩大参数扫描。ell=0,0.5,1,2a的完整结果及256/512积分核对见supplemental_bound_results.json。
"""
    (OUT/"supplemental_bound_report.txt").write_text(report,encoding="utf-8")
    print(json.dumps(records,indent=2))


if __name__=="__main__":
    main()
