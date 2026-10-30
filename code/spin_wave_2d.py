#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linear spin waves of a nearest-neighbor Heisenberg ferromagnet on a square lattice.

Conventions: hbar = a = 1; dimensionless spin operators; each bond counted once.
H = -sum_{i,mu} J_mu S_i.S_{i+e_mu} - h sum_i S_i^x, h = g mu_B B.
The supported polarized ground state has S > 0, Jx,Jy >= 0, and h >= 0.
Jx != Jy is spatial exchange anisotropy, not spin-component anisotropy.

With S_i^x = S + O(s_perp^2/S), the linear equations are
    dot(sy) = A sz, dot(sz) = -A sy,
    A = h + S sum_mu J_mu (2 - T_mu - T_mu^-1).
Thus psi = sy + i sz obeys i dot(psi) = A psi, with
    epsilon(k) = h + 2S [Jx (1-cos kx) + Jy (1-cos ky)].
For positive ferromagnetic couplings, the only zero mode at h=0 is k=0
(modulo reciprocal lattice vectors); a decoupled direction adds degeneracy.
There is no zero-frequency ring for the default parameters.

Quadratic Holstein-Primakoff theory gives H2 = E_F + sum_k epsilon(k) a_k^dag a_k.
Here psi = sqrt(2S) <a> describes a coherent transverse amplitude, not a
many-body wavefunction. Require |s_perp|/S << 1 (or magnon density << 2S).
A one-magnon wavefunction obeys the same linear operator, but its amplitude
is not <S_y> + i<S_z> in a fixed-magnon-number state.

Numerics: periodic boundaries via np.roll, classical RK4 time integration.
The exact linear flow conserves Q = sum_i |psi_i|^2; finite-step RK4 does not
conserve it exactly. Regression tests compare with exact Fourier evolution.
A narrow-band packet moves at grad_k epsilon and generally disperses.

Usage:
    python code/spin_wave_2d.py --npz
    python code/spin_wave_2d.py --S 1 --Jy 0.2 --h 0 --no-gif
    python -m unittest discover -s code -v
Outputs: s_y.gif, s_z.gif, s_y_s_z.gif, snapshots.png, snapshot_t*.png,
and optional evolution.npz in spin_wave_out/ beside this script.
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
    S: float = 0.5              # 单个电子的自旋；有效自旋可用 --S 改变
    Jx: float = 1.0             # x 方向交换
    Jy: float = 0.5             # y 方向交换
    h: float = 0.5              # Zeeman 能量 g mu_B B，hbar=1
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
        """Upper bound on |epsilon_k|, including the longitudinal exchange field."""
        return abs(self.h + 2 * self.S * (self.Jx + self.Jy)) + 2 * self.S * (abs(self.Jx) + abs(self.Jy))

    def auto_dt(self) -> float:
        # Imaginary-axis RK4 stability limit is sqrt(8); use 0.1 for accuracy.
        return 0.1 / self.amax() if self.amax() > 0 else self.tmax

    def dispersion(self, kx, ky):
        """Return (epsilon_k, omega_k); hbar=a=1, so both are equal."""
        ak = self.h + 2.0 * self.S * (self.Jx * (1 - np.cos(kx)) + self.Jy * (1 - np.cos(ky)))
        return ak, ak

    def group_velocity(self, kx, ky):
        """Group velocity of psi=sy+i*sz at its actual Fourier momentum."""
        return 2.0 * self.S * np.array([self.Jx * np.sin(kx),
                                              self.Jy * np.sin(ky)])

    def validate(self):
        if self.N < 4:
            raise ValueError("N must be >= 4")
        if not np.all(np.isfinite([self.S, self.Jx, self.Jy, self.h, self.tmax])):
            raise ValueError("Model parameters and tmax must be finite")
        if self.S <= 0 or min(self.Jx, self.Jy, self.h) < 0:
            raise ValueError("Polarized ferromagnet requires S > 0 and Jx, Jy, h >= 0")
        if self.tmax <= 0 or self.frames < 2 or min(self.fps, self.dpi, self.nsnap) < 1:
            raise ValueError("Require tmax > 0, frames >= 2 and fps, dpi, nsnap >= 1")
        if self.dt is not None and (not np.isfinite(self.dt) or self.dt <= 0):
            raise ValueError("dt must be finite and positive")


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
                amp=0.025, handedness=+1):
    """高斯包络 × 行波，一次返回 (s^y, s^z)。

        s^y = A g cosθ ,  s^z = handedness · A g sinθ ,  θ = k·(r - r0)

    psi = sy+i*sz is centered at handedness*k. Positive handedness selects
    +k, with velocity grad(epsilon)(k); negative handedness selects -k.
    These are opposite momenta in one magnon band, not two magnon species.
    A narrow spectrum is needed for predominantly one-directional motion.
    """
    N = nx.shape[0]
    x0 = N / 2.0 if x0 is None else float(x0)
    y0 = N / 2.0 if y0 is None else float(y0)
    dx = pbc_delta(nx, x0, N)
    dy = pbc_delta(ny, y0, N)
    g = np.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))
    th = kx * dx + ky * dy
    return amp * g * np.cos(th), handedness * amp * g * np.sin(th)


def plane_wave(nx, ny, *, mx=1, my=0, amp=0.025, phase=0.0):
    """平面波 cos(k·r + phase)，k = 2π(mx, my)/N。返回单个数组。

    它是 A 的本征模：把它同时用作 s^y、并令 s^z = 0，空间形状永不改变。
    """
    N = nx.shape[0]
    return amp * np.cos(2.0 * np.pi * (mx * nx + my * ny) / N + phase)


# ============================================================================
#  ①  初 始 构 型  ← ← ←  你要手动改的就是这两块
#
#      - nx, ny 是 shape=(N,N) 的二维数组（格点号），可以直接做数组运算
#      - P 是可选的 Params 实例，由 main 传入
#      - 返回值为 shape=(N,N) 实数组；物理线性化要求 hypot(sy,sz) << S
#      - 想标定位置就用格点号：例如中心在 (P.N/2, P.N/2)
#
#     下面默认是"高斯包络 × 单向行波"的例子，整段替换成你自己的公式即可。
# ============================================================================
def initial_sy(nx, ny, P=None):
    P = Params() if P is None else P
    sy, _sz = wave_packet(nx, ny, kx=0.6, ky=0.0, sigma=4.0, amp=0.05 * P.S)
    return sy
    # —— 备选写法（把上面两行注释掉，换下面任意一种）——
    # 1) 纯高斯，没有载波：只会原地缓慢色散，不会跑
    #    return 0.05 * P.S * np.exp(-pbc_delta(nx, P.N / 2, P.N) ** 2 / (2 * 5.0 ** 2)
    #                        - pbc_delta(ny, P.N / 2, P.N) ** 2 / (2 * 5.0 ** 2))
    # 2) 平面波本征模（严格不形变，用来做基准）：k = 2π(1,0)/N
    #    return plane_wave(nx, ny, mx=1, my=0, amp=0.05 * P.S)
    # 3) 斜向传播的高斯包络行波
    #    return wave_packet(nx, ny, kx=0.8, ky=0.5, sigma=3.5)[0]


def initial_sz(nx, ny, P=None):
    P = Params() if P is None else P
    _sy, sz = wave_packet(nx, ny, kx=0.6, ky=0.0, sigma=4.0, amp=0.05 * P.S)
    return sz
    # —— 与 initial_sy 保持一致的备选 ——
    # 1) 纯高斯：s^z = 0（对称的 ±k 成分，包络会色散）
    #    return np.zeros_like(nx)
    # 2) 平面波本征模：s^z = 0（配合上面的 2) 使用）
    #    return np.zeros_like(nx)


# ============================================================================
#  ②  计 算 核 心
# ============================================================================
def make_rhs(P: Params):
    """返回 (s^y, s^z) -> (ds^y/dt, ds^z/dt)。axis=0 是 ny，axis=1 是 nx。"""
    S, Jx, Jy, h = P.S, P.Jx, P.Jy, P.h
    onsite = h + 2.0 * S * (Jx + Jy)

    def rhs(sy, sz):
        # s^z 的四个邻居（e_x 在 axis=1，e_y 在 axis=0），PBC 由 np.roll 给出
        sz_e = (Jx * (np.roll(sz, 1, axis=1) + np.roll(sz, -1, axis=1))
                + Jy * (np.roll(sz, 1, axis=0) + np.roll(sz, -1, axis=0)))
        dsy = sz * onsite - S * sz_e

        sy_e = (Jx * (np.roll(sy, 1, axis=1) + np.roll(sy, -1, axis=1))
                + Jy * (np.roll(sy, 1, axis=0) + np.roll(sy, -1, axis=0)))
        dsz = -sy * onsite + S * sy_e
        return dsy, dsz

    return rhs


def evolve(P: Params, sy0, sz0, verbose=True):
    """经典四阶 Runge–Kutta 推进，按 frames 均匀记录。"""
    P.validate()
    rhs = make_rhs(P)
    dt = P.dt if P.dt is not None else P.auto_dt()
    nsteps = max(1, int(np.ceil(P.tmax / dt)))
    dt = P.tmax / nsteps                      # 让最后一帧正好落在 tmax
    if dt * P.amax() >= np.sqrt(8):
        raise ValueError("dt exceeds the RK4 stability bound; reduce --dt")
    idx = np.unique(np.round(np.linspace(0, nsteps, P.frames)).astype(int))
    nf, N = idx.size, P.N

    fsy = np.empty((nf, N, N), dtype=np.float64)
    fsz = np.empty((nf, N, N), dtype=np.float64)
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


def estimate_k(sy0, sz0, N):
    """Dominant Fourier momentum of psi=sy+i*sz, including k=0."""
    psi = np.asarray(sy0, float) + 1j * np.asarray(sz0, float)
    mag = np.abs(np.fft.fft2(psi))
    k1 = np.fft.fftfreq(N) * (2 * np.pi)                     # 每个索引对应的 k
    iy, ix = np.unravel_index(np.argmax(mag), mag.shape)
    return k1[ix], k1[iy]


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
    fig, axes = plt.subplots(2, pick.size, figsize=(3.2 * pick.size, 6.6), dpi=140, squeeze=False)
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
    p.add_argument("--h", type=float, default=d.h, help="Zeeman 能量 g mu_B B（hbar=1）")
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
    try:
        P.validate()
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    outdir = Path(P.outdir) if P.outdir else Path(__file__).resolve().parent / "spin_wave_out"
    outdir.mkdir(parents=True, exist_ok=True)

    nx, ny = make_grid(P.N)
    sy0 = np.asarray(initial_sy(nx, ny, P), dtype=float)
    sz0 = np.asarray(initial_sz(nx, ny, P), dtype=float)
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
    print(f" A_k  : h + 2S[Jx(1-cos kx) + Jy(1-cos ky)], max|A| <= {P.amax():.4f}")
    print(f" 线性化: max|s_perp|/S = {np.max(np.hypot(sy0, sz0)) / P.S:.4f}")
    if np.max(np.hypot(sy0, sz0)) / P.S > 0.1:
        print(" 提醒: 初态横向振幅超过 0.1S，请检查小振幅近似。")
    print(f" 初态 : max|s^y| = {np.abs(sy0).max():.4f}, "
          f"max|s^z| = {np.abs(sz0).max():.4f},  Q(0) = {norm0:.6e}")
    if norm0 <= 0:
        print(" 初态恒为 0，没有东西可演化", file=sys.stderr)
        return 2
    print("-" * 74)

    t0 = time.perf_counter()
    try:
        res = evolve(P, sy0, sz0)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
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
        print(f"   谱峰波矢 k_ψ ≈ ({kx:+.3f}, {ky:+.3f})   (ψ = s^y + i·s^z)")
        print(f"   → A_k = {ak:+.3f}, ω = {om:.3f}")
        print(f"   谱峰处群速度 v_g = ({vg[0]:+.3f}, {vg[1]:+.3f})（窄带估计）")
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
            nsteps=res["nsteps"], model="heisenberg_ferromagnet_linear_v2",
            h_definition="g*mu_B*B", hbar=1.0, lattice_spacing=1.0)
        print("   ✓ evolution.npz")

    print("-" * 74)
    print(f" 完成，用时 {time.perf_counter() - t0:.1f} s")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
