#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 二维各向异性正方晶格 · 自旋波包（spin-wave packet）时间演化
================================================================================

体系
----
N×N 正方晶格，周期性边界条件（PBC）。每个格点 i 携带两个横向自旋分量
s_i^y, s_i^z（认为 s^x ≈ 1 为常量，即线性化近似）。运动方程与你给的式子逐字一致：

    d s_i^y / dt =  s_i^z h - S [ J_x (s^z_{i+e_x} + s^z_{i-e_x})
                                 + J_y (s^z_{i+e_y} + s^z_{i-e_y}) ]

    d s_i^z / dt = -s_i^y h + S [ J_x (s^y_{i+e_x} + s^y_{i-e_x})
                                 + J_y (s^y_{i+e_y} + s^y_{i-e_y}) ]

注意：四个邻居是"直接相加"，没有 1/2 因子（按你的约定）。

写成算符形式
------------
    d s^y/dt = A s^z ,      d s^z/dt = -A s^y
    A = h - S [ J_x (T_x + T_x^{-1}) + J_y (T_y + T_y^{-1}) ] ,   T = 平移算符

A 是对称算符，于是下面的量严格守恒（脚本最后会打印它的相对漂移，用来检查积分精度）：

    Q = Σ_i [ (s_i^y)^2 + (s_i^z)^2 ] = const

把 dt 减半再跑一次，Q 的漂移应当大幅下降，说明步长够小。

解析色散
--------
把 s ∝ cos(k·r - ωt) 代入，得到

    A_k = h - 2 S (J_x cos k_x + J_y cos k_y)
    ω_k = |A_k| ,  两支 ±ω_k
    v_g = ± sign(A_k) · 2S ( J_x sin k_x , J_y sin k_y )

默认参数 (h, S, J_x, J_y) = (0.5, 1.0, 1.0, 0.5) 时 A_k ∈ [-2.5, +3.5]，
并且在闭合曲线 2cos k_x + cos k_y = 0.5 上 A_k = 0，即这些模式 ω = 0、完全静止
（nodal ring）。所以在这类线性体系里，任何波包都会有一部分成分被"冻结"在原地。

关于"传播稳定且不变形"的波包  ← 你正在找的东西
----------------------------------------------
因为方程是线性的 + 平移不变，**严格不形变的解只有 A 的本征态，即平面波**：
取 s^y ∝ cos(k·r)、s^z 与之同形状，此时空间形状永远不变，只是 s^y/s^z 绕原点
匀速旋转（脚本里的 plane_wave() 就是干这个的，GIF 里应当看到形状完全不动）。
任何局域波包都会被展开成 ω_k 各不相同的平面波而色散、变形。可走的三条路：

 1) 平面波本征模：严格的基准，用来确认"代码没问题、色散没算错"；
 2) 窄带波包（σ 大、k 宽度小）：在中心 k 附近包络扩散最慢，
    这是线性体系里最接近"稳定不变形"的东西；
 3) 真正的自局域"自陷/孤子"结构：需要非线性。例如把模长约束
    s^x = sqrt(1 - (s^y)^2 - (s^z)^2) 代回方程，方程就不再线性。
    本脚本严格按你给的线性方程实现，因此不会出现孤子——这是方程本身决定的，
    不是数值问题。若需要第 3 条，告诉我，我加一个非线性开关。

输出（默认写到脚本同目录的 spin_wave_out/ 下）
---------------------------------------------
    s_y.gif / s_z.gif    s^y、s^z 各自的动图
    s_y_s_z.gif          左右并排的动图（由上面两张直接拼接，不额外渲染）
    snapshots.png        若干时刻的 2×k 快照拼图
    snapshot_t*.png      每个时刻单独的双面板快照
    evolution.npz        完整数据（加 --npz 才有）

用法
----
    python spin_wave_2d.py
    python spin_wave_2d.py --tmax 80 --frames 300 --fps 24
    python spin_wave_2d.py --N 128 --S 1 --Jx 1 --Jy 0.2 --h 0
    python spin_wave_2d.py --no-gif            # 只出 PNG，快速看结果
    python spin_wave_2d.py --help
"""

from __future__ import annotations

import argparse
import io
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")                       # 无窗口后端，直接出图/出 GIF
import matplotlib.pyplot as plt
from PIL import Image

# 中文字体（Windows 自带）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============================================================================
#  参数：改这里的默认值，或者用命令行覆盖（命令行优先）
# ============================================================================
@dataclass
class Params:
    N: int = 64                 # 晶格 N×N
    S: float = 1.0              # 自旋长度 / 交换标度
    Jx: float = 1.0             # x 方向交换
    Jy: float = 0.5             # y 方向交换
    h: float = 0.5              # 沿 x 的外场
    tmax: float = 40.0          # 总演化时间
    dt: float | None = None     # None → 自动（取 A_max·dt = 0.1）
    frames: int = 180           # 记录/动画帧数
    fps: int = 20
    dpi: int = 85
    nsnap: int = 4              # 快照个数
    save_npz: bool = False
    no_gif: bool = False
    outdir: Path | None = None

    def amax(self) -> float:
        """max_k |A_k| 的解析上界（在 k=(π,π) 处取到）。"""
        return abs(self.h) + 2.0 * self.S * (abs(self.Jx) + abs(self.Jy))

    def auto_dt(self) -> float:
        # RK4 稳定域上限约 A_max·dt < 2.78；取 0.1 时每步相位误差 ≈ θ^5/120 ≈ 1e-7，
        # 守恒量 Q 在 t ~ 40 的漂移约 1e-6，足够"看起来守恒"
        return 0.1 / self.amax()

    def dispersion(self, kx, ky):
        """解析：A_k 与 ω_k（ω_k = |A_k|）。"""
        ak = self.h - 2.0 * self.S * (self.Jx * np.cos(kx) + self.Jy * np.cos(ky))
        return ak, np.abs(ak)

    def group_velocity(self, kx, ky):
        """解析群速度的候选值 ±v_g（取哪一支取决于 s^y/s^z 的相位关系）。"""
        ak, _ = self.dispersion(kx, ky)
        sgn = 1.0 if ak >= 0 else -1.0
        return sgn * 2.0 * self.S * np.array([self.Jx * np.sin(kx),
                                              self.Jy * np.sin(ky)])


# ============================================================================
#  小工具：网格与几种现成的初态构件（手写你的初态时可以直接调用）
# ============================================================================
def make_grid(N: int):
    """返回 (nx, ny)，都是 shape=(N,N) 的二维坐标数组：行←ny，列←nx。"""
    n = np.arange(N, dtype=float)
    nx, ny = np.meshgrid(n, n, indexing="xy")
    return nx, ny


def pbc_delta(coord, center, N):
    """带周期的最小镜像距离，保证包络跨过边界时不被撕裂。"""
    d = coord - center
    return d - N * np.round(d / N)


def wave_packet(nx, ny, *, kx=0.6, ky=0.0, sigma=4.0, x0=None, y0=None,
                amp=1.0, handedness=+1):
    """高斯包络 × 行波，一次返回 (s^y, s^z)。

        s^y = A g cosθ ,  s^z = -handedness · A g sinθ ,  θ = k·(r - r0)

    handedness = +1 对应 ω = +|A_k| 那一支，-1 对应另一支（群速度反向）。
    关键点：s^z 与 s^y 差 90° 相位（cos / sin）才会得到**单向**传播；
    若 s^z = 0，则 ±k 两个分量会朝相反方向分开，看到一个包分裂成两个。
    """
    N = nx.shape[0]
    x0 = N / 2.0 if x0 is None else float(x0)
    y0 = N / 2.0 if y0 is None else float(y0)
    dx = pbc_delta(nx, x0, N)
    dy = pbc_delta(ny, y0, N)
    g = np.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))
    th = kx * dx + ky * dy
    return amp * g * np.cos(th), -handedness * amp * g * np.sin(th)


def plane_wave(nx, ny, *, mx=1, my=0, amp=1.0, phase=0.0):
    """平面波 cos(k·r + phase)，k = 2π(mx, my)/N。返回单个数组。

    它是 A 的本征模：把它同时用作 s^y、并令 s^z = 0，空间形状永不改变。
    """
    N = nx.shape[0]
    return amp * np.cos(2.0 * np.pi * (mx * nx + my * ny) / N + phase)


# ============================================================================
#  ①  初 始 构 型  ← ← ←  你要手动改的就是这两块
#
#      - nx, ny 是 shape=(N,N) 的二维数组（格点号），可以直接做数组运算
#      - P 是 Params 实例，可用 P.N / P.S / P.Jx / P.Jy / P.h
#      - 返回值必须是 shape=(N,N) 的实数数组；幅值随便取（方程线性，
#        整体幅值只是缩放，不改变动力学与"是否变形"）
#      - 想标定位置就用格点号：例如中心在 (P.N/2, P.N/2)
#
#     下面默认是"高斯包络 × 单向行波"的例子，整段替换成你自己的公式即可。
# ============================================================================
def initial_sy(nx, ny):
    sy, _sz = wave_packet(nx, ny, kx=0.6, ky=0.0, sigma=4.0)
    return sy
    # —— 备选写法（把上面两行注释掉，换下面任意一种）——
    # 1) 纯高斯，没有载波：只会原地缓慢色散，不会跑
    #    return 0.8 * np.exp(-pbc_delta(nx, P.N / 2, P.N) ** 2 / (2 * 5.0 ** 2)
    #                        - pbc_delta(ny, P.N / 2, P.N) ** 2 / (2 * 5.0 ** 2))
    # 2) 平面波本征模（严格不形变，用来做基准）：k = 2π(1,0)/N
    #    return plane_wave(nx, ny, mx=1, my=0, amp=0.8)
    # 3) 斜向传播的高斯包络行波
    #    return wave_packet(nx, ny, kx=0.8, ky=0.5, sigma=3.5)[0]


def initial_sz(nx, ny):
    _sy, sz = wave_packet(nx, ny, kx=0.6, ky=0.0, sigma=4.0)
    return sz
    # —— 与 initial_sy 保持一致的备选 ——
    # 1) 纯高斯：s^z = 0（会同时激发两支，看到拍频）
    #    return np.zeros_like(nx)
    # 2) 平面波本征模：s^z = 0（配合上面的 2) 使用）
    #    return np.zeros_like(nx)


# ============================================================================
#  ②  计 算 核 心
# ============================================================================
def make_rhs(P: Params):
    """返回 (s^y, s^z) -> (ds^y/dt, ds^z/dt)。axis=0 是 ny，axis=1 是 nx。"""
    S, Jx, Jy, h = P.S, P.Jx, P.Jy, P.h

    def rhs(sy, sz):
        # s^z 的四个邻居（e_x 在 axis=1，e_y 在 axis=0），PBC 由 np.roll 给出
        sz_e = (Jx * (np.roll(sz, 1, axis=1) + np.roll(sz, -1, axis=1))
                + Jy * (np.roll(sz, 1, axis=0) + np.roll(sz, -1, axis=0)))
        dsy = sz * h - S * sz_e

        sy_e = (Jx * (np.roll(sy, 1, axis=1) + np.roll(sy, -1, axis=1))
                + Jy * (np.roll(sy, 1, axis=0) + np.roll(sy, -1, axis=0)))
        dsz = -sy * h + S * sy_e
        return dsy, dsz

    return rhs


def evolve(P: Params, sy0, sz0, verbose=True):
    """经典四阶 Runge–Kutta 推进，按 frames 均匀记录。"""
    rhs = make_rhs(P)
    dt = P.dt if P.dt else P.auto_dt()
    nsteps = max(1, int(round(P.tmax / dt)))
    dt = P.tmax / nsteps                      # 让最后一帧正好落在 tmax
    idx = np.unique(np.round(np.linspace(0, nsteps, P.frames)).astype(int))
    nf, N = idx.size, P.N

    fsy = np.empty((nf, N, N), dtype=np.float32)
    fsz = np.empty((nf, N, N), dtype=np.float32)
    times = np.empty(nf)
    norms = np.empty(nf)
    slot = {int(k): i for i, k in enumerate(idx)}

    sy = np.array(sy0, dtype=float, copy=True)
    sz = np.array(sz0, dtype=float, copy=True)

    def record(i, step):
        fsy[i], fsz[i] = sy, sz
        times[i] = step * dt
        norms[i] = np.sum(sy * sy + sz * sz)

    if 0 in slot:
        record(slot[0], 0)

    half = 0.5 * dt
    for step in range(1, nsteps + 1):
        k1y, k1z = rhs(sy, sz)                                   # 第 1 段
        k2y, k2z = rhs(sy + half * k1y, sz + half * k1z)          # 第 2 段
        k3y, k3z = rhs(sy + half * k2y, sz + half * k2z)          # 第 3 段
        k4y, k4z = rhs(sy + dt * k3y, sz + dt * k3z)              # 第 4 段
        c = dt / 6.0
        sy = sy + c * (k1y + 2.0 * k2y + 2.0 * k3y + k4y)
        sz = sz + c * (k1z + 2.0 * k2z + 2.0 * k3z + k4z)
        if step in slot:
            record(slot[step], step)

    if verbose:
        print(f"   积分: dt = {dt:.6g}  (A_max·dt = {P.amax() * dt:.3f}), "
              f"{nsteps} 步, 记录 {nf} 帧, t ∈ [0, {P.tmax:g}]")
    return {"sy": fsy, "sz": fsz, "t": times, "norm": norms, "dt": dt,
            "nsteps": nsteps}


# ============================================================================
#  ③  诊 断
# ============================================================================
def centroid_track(fsy, fsz, N):
    """用周期边界下的"圆周平均"求波包质心（单位：格点），返回 (nf, 2) 的 (x, y)。"""
    ph = np.exp(2j * np.pi * np.arange(N) / N)
    out = np.empty((fsy.shape[0], 2))
    for i in range(fsy.shape[0]):
        w = fsy[i].astype(float) ** 2 + fsz[i].astype(float) ** 2
        tot = w.sum()
        if tot <= 1e-300:
            out[i] = np.nan
            continue
        zx = (w.sum(axis=0) * ph).sum() / tot      # 每个 x 列的总权重 → 圆周平均
        zy = (w.sum(axis=1) * ph).sum() / tot      # 每个 y 行的总权重
        out[i, 0] = np.angle(zx) * N / (2 * np.pi) % N
        out[i, 1] = np.angle(zy) * N / (2 * np.pi) % N
    return out


def estimate_k(sy0, sz0, N, exclude=2):
    """由 ψ = s^y + i·s^z 的二维 FFT 峰值估计主导波矢 k（1/格点）。

    注意谱峰给出的是 ψ 的波矢；s^y/s^z 构成的实波包的单支波矢与它差一个符号，
    所以下面输出的是 ±k_ψ。
    """
    psi = np.asarray(sy0, float) + 1j * np.asarray(sz0, float)
    mag = np.abs(np.fft.fft2(psi))
    k1 = np.fft.fftfreq(N) * (2 * np.pi)                     # 每个索引对应的 k
    keep = np.abs(k1) > exclude * 2 * np.pi / N              # 屏蔽包络本身的低频
    mag = np.where(keep[:, None] | keep[None, :], mag, 0.0)
    iy, ix = np.unravel_index(np.argmax(mag), mag.shape)
    kx = 2 * np.pi * ix / N if ix <= N // 2 else 2 * np.pi * (ix - N) / N
    ky = 2 * np.pi * iy / N if iy <= N // 2 else 2 * np.pi * (iy - N) / N
    return kx, ky


# ============================================================================
#  ④  出 图
# ============================================================================
CMAP = "RdBu_r"


def _panel(ax, data, t, title, vlim, P, cbar=False):
    im = ax.imshow(data, origin="lower", cmap=CMAP, vmin=-vlim, vmax=vlim,
                   interpolation="nearest",
                   extent=(-0.5, P.N - 0.5, -0.5, P.N - 0.5))
    ax.set_xlabel("$n_x$")
    ax.set_ylabel("$n_y$")
    ax.set_aspect("equal")
    ax.set_title(f"{title}   t = {t:.2f}", fontsize=11)
    if cbar:
        cb = ax.figure.colorbar(im, ax=ax, shrink=0.88, pad=0.03)
        cb.set_label(title, fontsize=10)
    return im


def save_snapshots(P, res, vlimy, vlimz, outdir):
    fsy, fsz, times = res["sy"], res["sz"], res["t"]
    pick = np.unique(np.round(np.linspace(0, len(times) - 1, P.nsnap)).astype(int))

    # (a) 拼图：上排 s^y，下排 s^z
    fig, axes = plt.subplots(2, pick.size, figsize=(3.2 * pick.size, 6.6), dpi=140)
    axes = np.atleast_2d(axes)
    for j, i in enumerate(pick):
        _panel(axes[0, j], fsy[i], times[i], "$s^y$", vlimy, P, cbar=False)
        _panel(axes[1, j], fsz[i], times[i], "$s^z$", vlimz, P, cbar=False)
    for row, v in enumerate((vlimy, vlimz)):
        im = axes[row, 0].images[0]
        cb = fig.colorbar(im, ax=axes[row, :].tolist(), shrink=0.85, pad=0.01)
        cb.set_label("$s^y$" if row == 0 else "$s^z$", fontsize=10)
    fig.suptitle(f"N = {P.N}, S = {P.S}, $J_x$ = {P.Jx}, $J_y$ = {P.Jy}, h = {P.h}",
                 fontsize=12)
    fig.savefig(outdir / "snapshots.png", bbox_inches="tight")
    plt.close(fig)
    print("   ✓ snapshots.png")

    # (b) 每个时刻单独的双面板图
    for i in pick:
        fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.9), dpi=140)
        _panel(axes[0], fsy[i], times[i], "$s^y$", vlimy, P, cbar=True)
        _panel(axes[1], fsz[i], times[i], "$s^z$", vlimz, P, cbar=True)
        fig.tight_layout()
        fig.savefig(outdir / f"snapshot_t{times[i]:06.2f}.png", bbox_inches="tight")
        plt.close(fig)
    print(f"   ✓ snapshot_t*.png  ({pick.size} 张)")


def _gif_canvas(P, title, vlim):
    """建一块固定尺寸的画布，逐帧只改数据（比每帧重建 figure 快得多）。"""
    fig, ax = plt.subplots(figsize=(5.9, 5.1), dpi=P.dpi)
    _panel(ax, np.zeros((P.N, P.N)), 0.0, title, vlim, P, cbar=True)
    fig.tight_layout()
    return fig, ax


def render_gifs(P, fsy, fsz, times, vlimy, vlimz, outdir):
    """一次遍历渲染出 s_y.gif / s_z.gif / s_y_s_z.gif（并排图由两张直接拼接）。"""
    figy, axy = _gif_canvas(P, "$s^y$", vlimy)
    figz, axz = _gif_canvas(P, "$s^z$", vlimz)
    imy, imz = axy.images[0], axz.images[0]

    imgs_y, imgs_z, imgs_c = [], [], []
    dur = max(20, int(round(1000.0 / P.fps)))
    for i, t in enumerate(times):
        imy.set_data(fsy[i])
        axy.set_title(f"$s^y$   t = {t:.2f}", fontsize=11)
        axz.images[0].set_data(fsz[i])
        axz.set_title(f"$s^z$   t = {t:.2f}", fontsize=11)

        bufs = []
        for fig in (figy, figz):
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=P.dpi)
            buf.seek(0)
            bufs.append(Image.open(buf).convert("RGB"))
        a, b = bufs
        imgs_y.append(a)
        imgs_z.append(b)
        c = Image.new("RGB", (a.width + b.width, max(a.height, b.height)), "white")
        c.paste(a, (0, 0))
        c.paste(b, (a.width, 0))
        imgs_c.append(c)

    plt.close(figy)
    plt.close(figz)

    for imgs, name in ((imgs_y, "s_y.gif"), (imgs_z, "s_z.gif"),
                       (imgs_c, "s_y_s_z.gif")):
        imgs[0].save(outdir / name, save_all=True, append_images=imgs[1:],
                     duration=dur, loop=0, optimize=False)
        print(f"   ✓ {name}")


# ============================================================================
#  ⑤  主 程 序
# ============================================================================
def build_parser() -> argparse.ArgumentParser:
    d = Params()
    p = argparse.ArgumentParser(
        description="N×N 各向异性正方晶格（PBC）上的自旋波包时间演化",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--N", type=int, default=d.N, help="晶格尺寸 N×N")
    p.add_argument("--S", type=float, default=d.S, help="自旋长度 / 交换标度")
    p.add_argument("--Jx", type=float, default=d.Jx, help="x 方向交换")
    p.add_argument("--Jy", type=float, default=d.Jy, help="y 方向交换")
    p.add_argument("--h", type=float, default=d.h, help="沿 x 的外场")
    p.add_argument("--tmax", type=float, default=d.tmax, help="总演化时间")
    p.add_argument("--dt", type=float, default=None,
                   help="时间步长；不给则自动取 A_max·dt = 0.1")
    p.add_argument("--frames", type=int, default=d.frames, help="记录/动画帧数")
    p.add_argument("--fps", type=int, default=d.fps, help="GIF 帧率")
    p.add_argument("--dpi", type=int, default=d.dpi, help="出图 dpi")
    p.add_argument("--nsnap", type=int, default=d.nsnap, help="快照张数")
    p.add_argument("--outdir", type=Path, default=None,
                   help="输出目录（默认 <脚本目录>/spin_wave_out）")
    p.add_argument("--npz", dest="save_npz", action="store_true",
                   help="额外保存 evolution.npz")
    p.add_argument("--no-gif", dest="no_gif", action="store_true",
                   help="不出 GIF，只出 PNG")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    P = Params(**{k: v for k, v in vars(args).items()})
    if P.N < 4:
        print("N 至少取 4", file=sys.stderr)
        return 2

    outdir = Path(P.outdir) if P.outdir else Path(__file__).resolve().parent / "spin_wave_out"
    outdir.mkdir(parents=True, exist_ok=True)

    nx, ny = make_grid(P.N)
    sy0 = np.asarray(initial_sy(nx, ny), dtype=float)
    sz0 = np.asarray(initial_sz(nx, ny), dtype=float)
    for name, arr in (("initial_sy", sy0), ("initial_sz", sz0)):
        if arr.shape != (P.N, P.N):
            print(f"{name} 返回形状 {arr.shape}，应为 {(P.N, P.N)}", file=sys.stderr)
            return 2
        if not np.all(np.isfinite(arr)):
            print(f"{name} 含 nan/inf", file=sys.stderr)
            return 2

    norm0 = float(np.sum(sy0 ** 2 + sz0 ** 2))
    print("=" * 74)
    print(f" 体系 : {P.N}×{P.N}  PBC   S={P.S:g}  Jx={P.Jx:g}  Jy={P.Jy:g}  h={P.h:g}")
    print(f" A_k  : h - 2S(Jx cos kx + Jy cos ky),  max|A| = {P.amax():.4f}")
    print(f" 初态 : max|s^y| = {np.abs(sy0).max():.4f}, "
          f"max|s^z| = {np.abs(sz0).max():.4f},  Q(0) = {norm0:.6e}")
    if norm0 <= 0:
        print(" 初态恒为 0，没有东西可演化", file=sys.stderr)
        return 2
    print("-" * 74)

    t0 = time.perf_counter()
    res = evolve(P, sy0, sz0)
    fsy, fsz, times = res["sy"], res["sz"], res["t"]

    # ---- 诊断 ----
    drift = float(np.abs(res["norm"] - norm0).max() / norm0)
    print(f"   守恒量 Q 相对漂移 : {drift:.3e}   (dt 减半应显著变小)")
    vlimy = float(np.abs(fsy).max()) or 1.0
    vlimz = float(np.abs(fsz).max()) or 1.0
    print(f"   峰值     : max|s^y| = {vlimy:.4f}, max|s^z| = {vlimz:.4f}")

    try:
        c = centroid_track(fsy, fsz, P.N)
        d = np.diff(c, axis=0)
        d -= P.N * np.round(d / P.N)                  # 每帧位移取最小镜像
        vel = np.median(d / np.diff(times)[:, None], axis=0)
        kx, ky = estimate_k(sy0, sz0, P.N)
        ak, om = P.dispersion(kx, ky)
        vg = P.group_velocity(kx, ky)
        print(f"   谱峰波矢 k_ψ ≈ ({kx:+.3f}, {ky:+.3f})   (ψ = s^y + i·s^z；"
              f"实波包的单支波矢为 ±k_ψ)")
        print(f"   → A_k = {ak:+.3f}, ω = {om:.3f}")
        print(f"   解析群速度候选 ±v_g = ±({vg[0]:+.3f}, {vg[1]:+.3f})")
        print(f"   实测质心速度  v ≈ ({vel[0]:+.3f}, {vel[1]:+.3f})")
    except Exception as exc:                          # 诊断出错不影响主流程
        print(f"   (质心/群速度诊断跳过: {exc})")
    print("-" * 74)

    # ---- 出图 ----
    print(f" 输出目录: {outdir}")
    save_snapshots(P, res, vlimy, vlimz, outdir)
    if not P.no_gif:
        render_gifs(P, fsy, fsz, times, vlimy, vlimz, outdir)
    if P.save_npz:
        np.savez_compressed(
            outdir / "evolution.npz",
            sy=fsy, sz=fsz, t=times, norm=res["norm"],
            N=P.N, S=P.S, Jx=P.Jx, Jy=P.Jy, h=P.h, dt=res["dt"],
            nsteps=res["nsteps"])
        print("   ✓ evolution.npz")

    print("-" * 74)
    print(f" 完成，用时 {time.perf_counter() - t0:.1f} s")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
