"""Plot the diagnosed phase modulation beside the unchanged probability data.

This script reads the existing simulation and diagnostic records. It only writes
summary figures inside this diagnostic directory.
"""
from pathlib import Path
import json
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
sys.path.insert(0, str(ROOT))
import common


def main():
    arrays = np.load(ROOT / "curvature-design" / "design_data.npz")
    psi0 = arrays["C_eta1_psi_t0"]
    a0 = float(np.abs(psi0).max())
    pos = np.arange(psi0.shape[0]) - psi0.shape[0] // 2
    dense = np.genfromtxt(OUT / "dynamics" / "dense_trace.csv",
                         delimiter=",", names=True)
    movie = np.genfromtxt(OUT / "dynamics" / "movie_trace.csv",
                         delimiter=",", names=True)
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Microsoft YaHei", "DejaVu Sans"],
        "font.size": 12,
        "axes.unicode_minus": False,
        "svg.fonttype": "none",
    })
    fig = plt.figure(figsize=(12.2, 10.0), layout="constrained")
    grid = fig.add_gridspec(3, 3, height_ratios=[1, 1, .85])
    real_axes = [fig.add_subplot(grid[0, i]) for i in range(3)]
    prob_axes = [fig.add_subplot(grid[1, i]) for i in range(3)]
    records = []
    for col, t in enumerate([0., 9., 15.]):
        psi = common.propagate(psi0, t, 1.)
        stats = common.moments(psi)
        ix = np.abs(pos - stats["cx"]) <= 16.5
        iy = np.abs(pos - stats["cy"]) <= 16.5
        field = psi[np.ix_(iy, ix)]
        extent = (pos[ix][0] - .5 - stats["cx"],
                  pos[ix][-1] + .5 - stats["cx"],
                  pos[iy][0] - .5 - stats["cy"],
                  pos[iy][-1] + .5 - stats["cy"])
        real_image = real_axes[col].imshow(
            field.real / a0, origin="lower", extent=extent,
            cmap="RdBu_r", vmin=-1, vmax=1, interpolation="nearest")
        prob_image = prob_axes[col].imshow(
            np.abs(field)**2 / a0**2, origin="lower", extent=extent,
            cmap="magma", vmin=0, vmax=1, interpolation="nearest")
        real_peak = float(np.abs(psi.real).max() / a0)
        prob_peak = float((np.abs(psi)**2).max() / a0**2)
        real_axes[col].set_title(
            rf"$t={t:g}\hbar/J_x$" + f"\n实部绝对峰值：{real_peak:.4f}")
        prob_axes[col].set_title(f"概率峰值：{prob_peak:.5f}")
        for ax in (real_axes[col], prob_axes[col]):
            ax.set(xlim=(-16, 16), ylim=(-16, 16),
                   xticks=[-10, 0, 10], yticks=[-10, 0, 10],
                   xlabel=r"$(x-\langle x\rangle)/a$")
            ax.set_aspect("equal")
        records.append(dict(t=t, real_peak_over_initial=real_peak,
                            probability_peak_over_initial=prob_peak))
    real_axes[0].set_ylabel("振幅实部\n" + r"$(y-\langle y\rangle)/a$")
    prob_axes[0].set_ylabel("翻转概率\n" + r"$(y-\langle y\rangle)/a$")
    fig.colorbar(real_image, ax=real_axes, shrink=.84,
                 label=r"$\mathrm{Re}\,\psi/A_0$")
    fig.colorbar(prob_image, ax=prob_axes, shrink=.84,
                 label=r"$|\psi|^2/P_0$")

    trace = fig.add_subplot(grid[2, :])
    keep = dense["t"] <= 33
    keep_movie = movie["t"] <= 33
    trace.plot(dense["t"][keep],
               dense["real_absolute_peak_over_initial"][keep],
               color="#b3bac5", lw=1.0,
               label=r"实部峰值，加密采样 $\Delta t=0.05\hbar/J_x$")
    trace.plot(movie["t"][keep_movie],
               movie["real_absolute_peak_over_initial"][keep_movie],
               "o-", color="#b8493b", ms=5, lw=1.5,
               label=r"实部峰值，原动画 $\Delta t=3\hbar/J_x$")
    trace.plot(dense["t"][keep],
               dense["absolute_amplitude_peak_over_initial"][keep],
               color="#126c89", lw=2.0, label=r"模长峰值 $\max|\psi|/A_0$")
    trace.set(xlim=(0, 33), ylim=(.65, 1.025),
              xlabel=r"$t/(\hbar/J_x)$", ylabel="相对初始振幅峰值",
              title="实部对比度随相位变化；稀疏取帧改变了显示节奏")
    trace.legend(loc="lower left", fontsize=10, ncol=1)
    trace.grid(alpha=.18)
    fig.suptitle(
        r"交点波包：$k_{x0}a=k_{y0}a=\pi/2$，$J_y=J_x$，$\sigma=6a$"
        "\n各图固定色标；只平移观察窗口，不改变相位或逐帧归一化",
        fontsize=15)
    fig.savefig(OUT / "phase_probability_comparison.png", dpi=160)
    fig.savefig(OUT / "phase_probability_comparison.svg")
    plt.close(fig)
    (OUT / "summary_values.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
