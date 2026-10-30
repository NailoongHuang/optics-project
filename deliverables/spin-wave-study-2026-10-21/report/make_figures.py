"""Create concise report figures from the project's verified numerical records.

This changes only report/assets. No simulation parameters or original files are
modified. The three short-time C snapshots reuse the existing exact propagator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE / "assets"
BLUE = "#286b88"
GREEN = "#23846b"
RUST = "#ba6048"
INK = "#233c4b"
GRAY = "#7c8992"


def configure():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
        "font.size": 15,
        "axes.titlesize": 17,
        "axes.labelsize": 14,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
        "axes.unicode_minus": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelcolor": INK,
        "text.color": INK,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "svg.fonttype": "path",
        "mathtext.fontset": "dejavusans",
    })


def save(fig, stem):
    for suffix in ("png", "svg"):
        fig.savefig(OUT / f"{stem}.{suffix}", dpi=240, facecolor="white")
    plt.close(fig)


def centered_region(psi, pos, cx, cy, radius):
    ix = np.abs(pos - cx) <= radius + .6
    iy = np.abs(pos - cy) <= radius + .6
    extent = (
        pos[ix][0] - .5 - cx, pos[ix][-1] + .5 - cx,
        pos[iy][0] - .5 - cy, pos[iy][-1] + .5 - cy,
    )
    return psi[np.ix_(iy, ix)], extent


def packet_tracking(arrays, common):
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.65), layout="constrained")
    titles = ["A  普通点", "B  主要减弱一个方向", "C  两个方向都减弱"]
    p0 = float(np.abs(arrays["C_eta1_psi_t0"]).max()**2)
    values = []
    for key, title, ax in zip(("A", "B", "C"), titles, axes):
        psi = arrays[f"{key}_eta1_psi_t180"]
        pos = np.arange(psi.shape[0]) - psi.shape[0] // 2
        moments = common.moments(psi)
        cropped, extent = centered_region(
            psi, pos, moments["cx"], moments["cy"], 36)
        im = ax.imshow(np.abs(cropped)**2 / p0, extent=extent, origin="lower",
                       cmap="magma", vmin=0, vmax=1, interpolation="nearest")
        ax.set(title=title, xlabel="横向位置（格距）",
               xlim=(-36, 36), ylim=(-36, 36),
               xticks=[-30, 0, 30], yticks=[-30, 0, 30])
        ax.set_aspect("equal")
        values.append({"case": key, "time_hbar_over_Jx": 180,
                       "rms_x_a": moments["wx"], "rms_y_a": moments["wy"],
                       "peak_probability_over_initial": float(
                           np.max(np.abs(psi)**2) / p0)})
    axes[0].set_ylabel("纵向位置（格距）")
    bar = fig.colorbar(im, ax=axes, fraction=.03, pad=.025, shrink=.83)
    bar.set_label("概率 / 初始峰值", fontsize=13)
    bar.set_ticks([0, .5, 1])
    save(fig, "packet_tracking")
    return values


def phase_probability(arrays, common):
    psi0 = arrays["C_eta1_psi_t0"]
    a0 = float(np.abs(psi0).max())
    pos = np.arange(psi0.shape[0]) - psi0.shape[0] // 2
    fig, axes = plt.subplots(2, 3, figsize=(11.2, 5.9), layout="constrained")
    values = []
    for col, t in enumerate((0, 9, 15)):
        psi = common.propagate(psi0, t, 1.)
        m = common.moments(psi)
        cropped, extent = centered_region(psi, pos, m["cx"], m["cy"], 16)
        re_peak = float(np.abs(psi.real).max() / a0)
        p_peak = float((np.abs(psi)**2).max() / a0**2)
        im_re = axes[0, col].imshow(
            cropped.real/a0, extent=extent, origin="lower",
            cmap="RdBu_r", vmin=-1, vmax=1, interpolation="nearest")
        im_p = axes[1, col].imshow(
            np.abs(cropped)**2/a0**2, extent=extent, origin="lower",
            cmap="magma", vmin=0, vmax=1, interpolation="nearest")
        axes[0, col].set_title(
            f"t = {t}\n实部绝对峰值 {100*re_peak:.0f}%", fontsize=15)
        axes[1, col].set_title(
            f"概率峰值 {100*p_peak:.2f}%", fontsize=15)
        for row in range(2):
            ax = axes[row, col]
            ax.set(xlim=(-16, 16), ylim=(-16, 16),
                   xticks=[-12, 0, 12], yticks=[-12, 0, 12])
            ax.set_aspect("equal")
        axes[1, col].set_xlabel("横向位置（格距）")
        values.append({"t_hbar_over_Jx": t,
                       "real_absolute_peak_over_initial": re_peak,
                       "probability_peak_over_initial": p_peak})
    axes[0, 0].set_ylabel("振幅实部\n纵向位置（格距）")
    axes[1, 0].set_ylabel("翻转概率\n纵向位置（格距）")
    cb = fig.colorbar(im_re, ax=list(axes[0]), shrink=.8, fraction=.03, pad=.025)
    cb.set_ticks([-1, 0, 1])
    cb.set_label("实部 / 初始峰值", fontsize=12)
    cb = fig.colorbar(im_p, ax=list(axes[1]), shrink=.8, fraction=.03, pad=.025)
    cb.set_ticks([0, .5, 1])
    cb.set_label("概率 / 初始峰值", fontsize=12)
    save(fig, "phase_probability")
    return values


def caustic_comparison(data):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.0), layout="constrained")
    damping = data["damping_scan"]
    xs = np.array([r["gamma_over_omegaM"] for r in damping]) * 1e4
    ys = [r["peak_ratio"] for r in damping]
    axes[0].plot(xs, ys, "o-", color=BLUE, lw=2.5, ms=6)
    axes[0].axhline(1, color=GRAY, lw=1, ls="--")
    axes[0].annotate("无损：1.59 倍", (xs[0], ys[0]), xytext=(.12, 1.63),
                     fontsize=14, color=BLUE)
    axes[0].annotate("损耗较大：0.56 倍", (xs[-1], ys[-1]),
                     xytext=(.45, .64), fontsize=14, color=BLUE)
    axes[0].set(title="损耗会反转峰值优势",
                xlabel=r"衰减率（$10^{-4}\omega_M$）",
                ylabel="近高阶 / 普通：峰值比",
                xlim=(-.035, 1.04), ylim=(.45, 1.75))
    axes[0].grid(alpha=.16)
    selected = [
        next(r for r in data["detuning_scan"]
             if abs(r["relative_frequency_detuning"] - delta) < 1e-12)
        for delta in (-.005, 0, .005)
    ]
    received = [r["receiving_power"] for r in selected]
    bars = axes[1].bar(["−0.5%", "0", "+0.5%"], received,
                      color=[RUST, GREEN, RUST], width=.56)
    for bar, value in zip(bars, received):
        axes[1].text(bar.get_x()+bar.get_width()/2, value+.035,
                     f"{value:.3f}", ha="center", fontsize=15)
    axes[1].set(title="频率稍偏，窄波束会错过接收器",
                xlabel="频率偏移", ylabel="固定接收窗内的信号",
                ylim=(0, 1.12))
    axes[1].grid(axis="y", alpha=.16)
    axes[1].set_axisbelow(True)
    save(fig, "caustic_comparison")
    return {"damping_scan": damping,
            "selected_detuning": selected,
            "normalization": "equal scalar input norm, not calibrated microwave power",
            "distance_z_over_d": 10000}


def backflow_detection(data):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.05), layout="constrained")
    single = next(r for r in data["prepared_records"]
                  if r["preparation"] == "single_gaussian"
                  and r["psf_sigma_a"] == .5)
    coherent = next(r for r in data["prepared_records"]
                    if r["preparation"] == "resolution_aware"
                    and r["psf_sigma_a"] == .5)
    mixture = data["incoherent_mixture_controls"]["resolution_aware"]
    records = [single, coherent, mixture]
    values = [r["certified_margin"] for r in records]
    bars = axes[0].bar(
        ["单 Gaussian", "两个载波\n可以干涉", "同样成分\n互不干涉"], values,
        color=[GRAY, GREEN, RUST], width=.55)
    axes[0].axhline(0, color=INK, lw=1)
    for bar, value in zip(bars, values):
        axes[0].text(bar.get_x()+bar.get_width()/2,
                     value+(.0025 if value >= 0 else -.003),
                     f"{value:+.4f}", ha="center",
                     va="bottom" if value >= 0 else "top", fontsize=14)
    axes[0].set(title="半个格距模糊下，干涉决定结果",
                ylabel="反流判断量：正值才能确认", ylim=(-.079, .018))
    axes[0].grid(axis="y", alpha=.16)
    axes[0].set_axisbelow(True)
    natural = [r for r in data["natural_event"]["records"]
               if r["psf_sigma_a"] <= .5]
    axes[1].plot(
        [r["psf_sigma_a"] for r in natural],
        [r["certified_margin"]*1e5 for r in natural],
        "o-", color=BLUE, lw=2.5, ms=6)
    axes[1].axhline(0, color=INK, lw=1)
    axes[1].set(title="原来的微弱拖尾更难被确认",
                xlabel="成像模糊宽度（格距）",
                ylabel=r"反流判断量（$10^{-5}$）",
                xlim=(-.015, .515), ylim=(-4.3, 4.3))
    axes[1].grid(alpha=.16)
    save(fig, "backflow_detection")
    return {"prepared_half_site_comparison": records, "natural_event_scan": natural,
            "comparison_note":
                "Left: common prepared geometry. Right: separate natural-tail event. "
                "Do not compare these panels as equal-resource enhancement."}


def main():
    parser = argparse.ArgumentParser()
    portable = HERE.parent
    original = HERE.parents[2]
    parser.add_argument("--project-root", type=Path,
                        default=portable if (portable/"figures").exists() else original)
    args = parser.parse_args()
    project = args.project_root.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(project/"figures"/"midterm-report"))
    import common
    configure()
    sources = [
        Path("figures/midterm-report/curvature-design/design_data.npz"),
        Path("figures/midterm-report/common.py"),
        Path("code/spin_wave_2d.py"),
        Path("research/wavepacket-prospects/demos/finite-source-caustic/results.json"),
        Path("research/wavepacket-prospects/demos/backflow-resolution/results.json"),
    ]
    arrays = np.load(project/sources[0])
    caustic = json.loads((project/sources[3]).read_text(encoding="utf-8"))
    backflow = json.loads((project/sources[4]).read_text(encoding="utf-8"))
    selections = {
        "packet_tracking": packet_tracking(arrays, common),
        "phase_probability": phase_probability(arrays, common),
        "caustic_comparison": caustic_comparison(caustic),
        "backflow_detection": backflow_detection(backflow),
    }
    provenance = {
        "created_date": "2026-10-21",
        "source_root_used": str(project),
        "sources": [{"relative_path": p.as_posix(),
                     "sha256": hashlib.sha256((project/p).read_bytes()).hexdigest()}
                    for p in sources],
        "selections": selections,
        "display": {
            "spatial_maps": "actual lattice values, nearest display, centroid-relative windows",
            "normalization": "fixed initial maxima for lattice maps; no per-frame rescaling",
            "output": "PNG at 240 dpi plus editable SVG geometry",
        },
    }
    (OUT/"data_provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Created four report figures in", OUT)


if __name__ == "__main__":
    main()
