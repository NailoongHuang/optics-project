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
初始构型由同目录的 aux.py 在倒空间构造（高斯包络 × 相位 φ × 可选布里渊区副本），
把中心波矢放在色散曲率为零的点 (±π/2, ±π/2) 上以抑制色散；参数见下面 ① 区域。

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

运行模式（启动后会用 input() 问你，也可以 --mode 直接指定）
------------------------------------------------------------
  [1] 常规模式          GIF 动画 + 若干时刻快照
  [2] 长时间观察模式    只出两张图：二阶矩 M2(t) 的长时演化、初始波包构型；
                        当 M2 涨到 STOP_FACTOR × M2(0) 时自动停止（见 ① 区域常量）
  [3] 补偿模式          在模式 2 的基础上启用论文 (8)(9) 的补偿相位
                            ω_nonlin = -(S/3)[Jx(kx-π/2)³ + Jy(ky-π/2)³]
                            φ(qx,qy) = ω_nonlin · T
                        先算 T=0（无补偿）得到 M2 翻 STOP_FACTOR 倍所需时间 t_ref，
                        再在**同样的 t_ref 时长**下比较几个代表性 T 的 M2(t)，只出一张图

输出（每次运行都新建一个以「日期_时间」命名的子目录，不会覆盖旧结果）
--------------------------------------------------------------------
  spin_wave_out/<YYYYmmdd_HHMMSS>/     模式 1
      s_y.gif / s_z.gif      s^y、s^z 各自的动图
      s_y_s_z.gif            左右并排的动图（由上面两张直接拼接）
      snapshots.png          若干时刻的 2×k 快照拼图
      snapshot_t*.png        每个时刻单独的双面板快照
      packet.png             初态对照图（加 --plot-packet 才有）
      evolution.npz          完整数据（加 --npz 才有）
  evolution/<YYYYmmdd_HHMMSS>/         模式 2
      second_moment.png      二阶矩 M2 = ⟨dx²+dy²⟩（含 x/y 分量）随时间
      initial_packet.png     初始构型 s^y、s^z
  compensation/<YYYYmmdd_HHMMSS>/      模式 3
      compensation_M2.png    不同补偿时间 T 下 M2(t) 的对比（同一时长 t_ref）

用法
----
    python main.py                    # 启动后选择模式
    python main.py --mode 2           # 直接进长时间观察模式
    python main.py --mode 3           # 直接进补偿模式
    python main.py --tmax 80 --frames 300 --fps 24
    python main.py --N 128 --S 1 --Jx 1 --Jy 0.2 --h 0
    python main.py --no-gif           # 只出 PNG，快速看结果
    python main.py --help
"""

from __future__ import annotations

import argparse
import io
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")                       # 无窗口后端，直接出图/出 GIF
import matplotlib.pyplot as plt
from PIL import Image

import aux                      # 倒空间构造波包（同目录）

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
    plot_packet: bool = False  # 出初态对照图 packet.png
    mode: int | None = None     # 1 = 常规，2 = 长时间观察；None → 启动时询问

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
#  ①  初 始 构 型  ← ← ←  波包参数在这里改（由 aux.py 在倒空间构造）
#
#      k0       : 中心波矢（弧度）。零曲率点是 (±π/2, ±π/2)，与 Jx,Jy,h,S 无关；
#                 π/2 要落在离散网格上，需要 N 是 4 的倍数（64 ✓）。
#      sigma    : k 空间高斯沿 kx, ky 的标准差（弧度）；实空间宽度 ≈ 1/σ。
#      rho      : 相关系数（−1 < rho < 1），0 就是正椭圆。
#      PHASE    : φ(qx, qy)，定义在相对坐标 q = k − 中心 上；None = 全零。
#                 返回实数 → 乘 e^{iφ}；返回复数 → 直接当复因子。
#                 例：涡旋相位  lambda qx, qy: np.arctan2(qy, qx)
#      COPIES   : 布里渊区等价点的层数 (m1, m2)，共 (2m1+1)(2m2+1) 个副本。
#      PITCH    : 副本平移矢量 Δ。Δ = 2π 是倒格矢 → 整数格点上因子恒为常数，
#                 与单峰等价；要"压到间隔 L 的窄瓣里"就设 Δ = 2π/L，
#                 例如 PITCH = (2*np.pi/3, 0) 配 COPIES = (1, 0)。
#      THRESH   : |s̃_k|/max 低于此值的模式直接丢弃（让 k 空间支撑干净、有限）。
#      AMP / NORMALIZE : 目标幅度与归一化方式（"peak" | "norm" | "none"）。
#
#      注意：这个包在 k0 处的群速度是 v_g = 2S(Jx sin kx0, Jy sin ky0)
#            = (2, 1)（默认参数），走 0.6N 约需 t ≈ 17，所以 tmax 取 ~15-20 比较好看。
# ============================================================================
K0        = (np.pi / 2, np.pi / 2)
SIGMA     = (0.25, 0.25)
RHO       = 0.0
PHASE     = None
COPIES    = (0, 0)
PITCH     = (2 * np.pi, 2 * np.pi)
THRESH    = 1e-6
AMP       = 0.5
NORMALIZE = "peak"

# ---- 长时间观察模式（模式 2）的参数 ----
STOP_FACTOR = 2.0       # M2 涨到初始值的这个倍数就停止演化
TMAX_CAP    = 2000.0    # 保险上限：最多演化这么久（防止永远达不到目标）

# ---- 补偿模式（模式 3）的参数 ----
T_LIST = None           # 要比较的补偿时间 T；None → 自动取 t_ref 的 [0, 1/4, 1/2, 3/4, 1] 倍

_PACKET_CACHE = {}


def make_packet(nx, ny, phase=None, verbose=True):
    """按 ① 区域的参数构造一次波包，返回 (s^y, s^z, k 空间 s̃)。

    phase 给定时用它替换 PHASE（模式 3 用它注入补偿相位）。
    """
    N = nx.shape[0]
    st_r, st_k = aux.gaussian_k_packet(
        N, k0=K0, sigma=SIGMA, rho=RHO, phase=phase,
        copies=COPIES, pitch=PITCH, thresh=THRESH,
        amp=AMP, normalize=NORMALIZE,
        r0=(N / 2.0, N / 2.0), return_k=True, verbose=verbose)
    return (*aux.split(st_r), st_k)


def _packet(nx, ny):
    """initial_sy / initial_sz 用的缓存版本（相位取 ① 区域的 PHASE）。"""
    N = nx.shape[0]
    if N not in _PACKET_CACHE:
        _PACKET_CACHE[N] = make_packet(nx, ny, PHASE)
    return _PACKET_CACHE[N]


def compensation_phase(T, S=1.0, Jx=1.0, Jy=0.5):
    """论文 (8)(9) 的补偿相位：φ(q) = ω_nonlin(q)·T。

    ω_nonlin = -(S/3)[Jx qx³ + Jy qy³]，q = k - (π/2, π/2)。
    乘上 e^{iφ} 后，演化到 t = T 时三次色散被精确抵消。
    """
    return lambda qx, qy: -(S / 3.0) * T * (Jx * qx ** 3 + Jy * qy ** 3)


def initial_sy(nx, ny):
    return _packet(nx, ny)[0]


def initial_sz(nx, ny):
    return _packet(nx, ny)[1]


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


def _stamp():
    """以「日期_时间」命名的子目录名，例如 20261028_215812。"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ask_mode() -> int:
    """启动时用 input() 询问运行模式。"""
    print("=" * 74)
    print(" 请选择运行模式：")
    print("   [1] 常规模式        GIF 动画 + 若干时刻快照        → spin_wave_out/<时间>/")
    print("   [2] 长时间观察模式  二阶矩长时演化 + 初始构型"
          "       → evolution/<时间>/")
    print("   [3] 补偿模式        用论文的补偿相位比较不同 T 的 M2"
          "  → compensation/<时间>/")
    print("=" * 74)
    while True:
        try:
            s = input(" 输入 1 / 2 / 3 [默认 1]：").strip()
        except EOFError:                      # stdin 被重定向/关闭时的兜底
            print("\n （读不到输入，默认使用模式 1）")
            return 1
        if s in ("", "1"):
            return 1
        if s == "2":
            return 2
        if s == "3":
            return 3
        print(" 只能输入 1 / 2 / 3，请重试。")


def evolve_until(P: Params, sy0, sz0, *, factor=2.0, tmax_cap=2000.0,
                 t_end=None, quiet=False):
    """演化并逐步记录二阶矩。

    - 不给 t_end：跑到 M2 ≥ factor×M2(0) 为止（最长 tmax_cap 的保护上限）；
    - 给 t_end：固定演化到 t_end（factor 不起作用），用于横向比较。
    只存标量（t、M2、M2x、M2y），不存场，所以能跑很久。
    """
    rhs = make_rhs(P)
    dt = P.dt if P.dt else P.auto_dt()
    sy = np.array(sy0, dtype=float, copy=True)
    sz = np.array(sz0, dtype=float, copy=True)

    m2_0, m2x_0, m2y_0, _cx, _cy = aux.second_moment(sy, sz)
    if m2_0 <= 0.0:
        raise ValueError("初始二阶矩为 0，检查初态")

    if t_end is not None:
        target = float("inf")
        nsteps_max = max(1, int(round(t_end / dt)))
        horizon = float(t_end)
    else:
        target = factor * m2_0
        nsteps_max = max(1, int(round(tmax_cap / dt)))
        horizon = float(tmax_cap)
        m2_sat = P.N * P.N / 6.0              # 均匀分布（铺满盒子）时的饱和值
        if target > m2_sat:
            print(f"   ⚠ 目标 {factor:g}×M2(0) = {target:.1f} 已超过均匀分布的饱和值 "
                  f"{m2_sat:.1f}，可能永远达不到")

    ts, m2s = [0.0], [m2_0]
    m2xs, m2ys = [m2x_0], [m2y_0]
    half = 0.5 * dt
    step = 0
    stopped = False
    next_report = 0.1
    for step in range(1, nsteps_max + 1):
        k1y, k1z = rhs(sy, sz)
        k2y, k2z = rhs(sy + half * k1y, sz + half * k1z)
        k3y, k3z = rhs(sy + half * k2y, sz + half * k2z)
        k4y, k4z = rhs(sy + dt * k3y, sz + dt * k3z)
        c = dt / 6.0
        sy = sy + c * (k1y + 2.0 * k2y + 2.0 * k3y + k4y)
        sz = sz + c * (k1z + 2.0 * k2z + 2.0 * k3z + k4z)

        t = step * dt
        cur = aux.second_moment(sy, sz)
        ts.append(t)
        m2s.append(cur[0])
        m2xs.append(cur[1])
        m2ys.append(cur[2])
        if (not quiet) and t >= next_report * horizon:
            print(f"   t = {t:8.1f}   M2 = {cur[0]:10.3f}  "
                  f"({cur[0] / m2_0:6.3f} × M2(0))   RMS = {np.sqrt(cur[0]):6.2f} 格点")
            next_report += 0.1
        if cur[0] >= target:
            stopped = True
            break

    return {"t": np.array(ts), "M2": np.array(m2s), "M2x": np.array(m2xs),
            "M2y": np.array(m2ys), "dt": dt, "steps": step,
            "M2_0": m2_0, "target": target, "factor": factor, "stopped": stopped}


def plot_second_moment(res, P, path):
    """二阶矩随时间的长时间演化图。"""
    t = res["t"]
    fig, ax = plt.subplots(figsize=(8.8, 5.4), dpi=140)
    ax.plot(t, res["M2"], lw=2.0, color="C0",
            label=r"$M_2=\langle dx^2+dy^2\rangle$")
    ax.plot(t, res["M2x"], lw=1.0, ls="--", color="C3", label=r"$\langle dx^2\rangle$")
    ax.plot(t, res["M2y"], lw=1.0, ls="--", color="C2", label=r"$\langle dy^2\rangle$")
    ax.axhline(res["M2_0"], color="gray", ls="-.", lw=1.0, label=r"$M_2(0)$")
    ax.axhline(res["target"], color="k", ls=":", lw=1.2,
               label=rf"目标 ${res['factor']:g}\times M_2(0)$")
    t_end = float(t[-1])
    ax.axvline(t_end, color="k", ls=":", lw=0.9)
    ax.plot(t_end, res["M2"][-1], "o", color="k", ms=5, zorder=5)
    ax.text(0.985, 0.05,
            f"停止 t = {t_end:.2f}\n"
            f"$M_2$ = {res['M2'][-1]:.3f}\n"
            f"RMS = {np.sqrt(res['M2'][-1]):.2f} 格点",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="0.7", alpha=0.92))
    ax.set_xlabel("时间 $t$")
    ax.set_ylabel(r"二阶矩（格点$^2$）")
    ax.set_title(f"二阶矩的长时间演化    N={P.N}, S={P.S:g}, "
                 f"$J_x$={P.Jx:g}, $J_y$={P.Jy:g}, h={P.h:g}", fontsize=11)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"   ✓ {Path(path).name}")


def plot_initial_packet(sy, sz, P, path):
    """初始波包构型：s^y 与 s^z 两个面板。"""
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.9), dpi=140)
    for ax, arr, lab in ((axes[0], sy, "$s^y$"), (axes[1], sz, "$s^z$")):
        vl = float(np.abs(arr).max()) or 1.0
        im = ax.imshow(arr, origin="lower",
                       extent=(-0.5, P.N - 0.5, -0.5, P.N - 0.5),
                       cmap="RdBu_r", vmin=-vl, vmax=vl, interpolation="nearest")
        ax.set_xlabel("$n_x$")
        ax.set_ylabel("$n_y$")
        ax.set_aspect("equal")
        ax.set_title(f"初始 {lab}   (max {vl:.3f})", fontsize=11)
        fig.colorbar(im, ax=ax, shrink=0.85, pad=0.03)
    fig.suptitle(f"初始波包构型   k0=({K0[0]:+.3f}, {K0[1]:+.3f}), "
                 f"σ=({SIGMA[0]:g}, {SIGMA[1]:g}), ρ={RHO:g}, amp={AMP:g}",
                 fontsize=11.5)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"   ✓ {Path(path).name}")


def plot_compensation(curves, t_ref, P, path):
    """模式 3：一张图比较不同补偿时间 T 下的 M2(t)（只画总 M2）。"""
    cmap = matplotlib.colormaps["viridis"]
    n = max(1, len(curves) - 1)
    fig, ax = plt.subplots(figsize=(9.4, 5.8), dpi=140)
    for i, (T, res) in enumerate(curves):
        col = cmap(i / n) if n else cmap(0.2)
        tag = f"T = {T:.2f}" + ("（无补偿）" if T == 0 else f" = {T / t_ref:.2f} t_ref")
        ax.plot(res["t"], res["M2"], lw=1.9, color=col, label=tag)
        if T > 0:                              # 标出补偿生效的位置 t = T
            j = int(np.argmin(np.abs(res["t"] - T)))
            ax.plot(res["t"][j], res["M2"][j], "o", color=col, ms=6, zorder=5)
    m2_0 = next((r["M2_0"] for T, r in curves if T == 0), curves[0][1]["M2_0"])
    ax.axhline(STOP_FACTOR * m2_0, color="gray", ls="-.", lw=1.0,
               label=f"$2\\times M_2(0)$（T=0 的判据）")
    ax.axvline(t_ref, color="k", ls=":", lw=1.1, label=f"$t_\\mathrm{{ref}}$ = {t_ref:.2f}")
    ax.set_xlabel("时间 $t$")
    ax.set_ylabel(r"二阶矩 $M_2$（格点$^2$）")
    ax.set_title(f"补偿相位对比：不同 $T$ 下 $M_2(t)$    "
                 f"N={P.N}, S={P.S:g}, $J_x$={P.Jx:g}, $J_y$={P.Jy:g}, h={P.h:g}",
                 fontsize=11)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8.5, loc="upper center", ncol=2, framealpha=0.95)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"   ✓ {Path(path).name}")


def run_compensation(P, outdir):
    """模式 3：先由 T=0 定出 t_ref，再在同样时长下比较不同补偿时间 T 的 M2(t)。"""
    nx, ny = make_grid(P.N)

    # ---- 第 1 步：T = 0（无补偿），求 M2 翻 STOP_FACTOR 倍所需时间 ----------
    sy0, sz0, _st_k = make_packet(nx, ny, None)          # phase=None
    m2_0 = aux.second_moment(sy0, sz0)[0]
    print(f"   [1/2] T = 0（无补偿）：求 M2 → {STOP_FACTOR:g}×M2(0) 的时间, "
          f"M2(0) = {m2_0:.4f}")
    base = evolve_until(P, sy0, sz0, factor=STOP_FACTOR, tmax_cap=TMAX_CAP)
    t_ref = float(base["t"][-1])
    print(f"         → t_ref = {t_ref:.3f}（{base['steps']} 步, "
          f"M2 = {base['M2'][-1]:.4f}）")
    if not base["stopped"]:
        print(f"         ⚠ 到 TMAX_CAP={TMAX_CAP:g} 仍未翻 {STOP_FACTOR:g} 倍")

    # ---- 第 2 步：各 T 都跑同样的 t_ref ------------------------------------
    if T_LIST is not None:
        T_list = [float(x) for x in T_LIST]
    else:
        T_list = [0.0, 0.25 * t_ref, 0.5 * t_ref, 0.75 * t_ref, t_ref]

    print(f"   [2/2] 固定时长 t = {t_ref:.3f}（各 T 相同），比较 {len(T_list)} 个 T：")
    print(f"         {'T':>9} {'T/t_ref':>8} {'M2(0)':>9} {'M2(t_ref)':>11} {'M2 峰值':>9}")
    curves = []
    for k, T in enumerate(T_list):
        if T == 0.0:
            res = base
        else:
            ph = compensation_phase(T, P.S, P.Jx, P.Jy)
            sy, sz, _ = make_packet(nx, ny, ph, verbose=(k == 1))
            res = evolve_until(P, sy, sz, t_end=t_ref, quiet=True)
        curves.append((T, res))
        print(f"         {T:9.2f} {T / t_ref:8.2f} {res['M2'][0]:9.3f} "
              f"{res['M2'][-1]:11.3f} {res['M2'].max():9.3f}")

    print("-" * 74)
    plot_compensation(curves, t_ref, P, outdir / "compensation_M2.png")
    return 0


def run_standard(P, sy0, sz0, outdir):
    """模式 1：RK4 演化 + GIF / 快照 / 诊断。"""
    res = evolve(P, sy0, sz0)
    fsy, fsz, times = res["sy"], res["sz"], res["t"]

    norm0 = float(np.sum(sy0 ** 2 + sz0 ** 2))
    drift = float(np.abs(res["norm"] - norm0).max() / norm0)
    print(f"   守恒量 Q 相对漂移 : {drift:.3e}   (dt 减半应显著变小)")
    vlimy = float(np.abs(fsy).max()) or 1.0
    vlimz = float(np.abs(fsz).max()) or 1.0
    print(f"   峰值     : max|s^y| = {vlimy:.4f}, max|s^z| = {vlimz:.4f}")

    try:
        c = centroid_track(fsy, fsz, P.N)
        d = np.diff(c, axis=0)
        d -= P.N * np.round(d / P.N)
        vel = np.median(d / np.diff(times)[:, None], axis=0)
        kx, ky = estimate_k(sy0, sz0, P.N)
        ak, om = P.dispersion(kx, ky)
        vg = P.group_velocity(kx, ky)
        print(f"   谱峰波矢 k_ψ ≈ ({kx:+.3f}, {ky:+.3f})   (ψ = s^y + i·s^z；"
              f"实波包的单支波矢为 ±k_ψ)")
        print(f"   → A_k = {ak:+.3f}, ω = {om:.3f}")
        print(f"   解析群速度候选 ±v_g = ±({vg[0]:+.3f}, {vg[1]:+.3f})")
        print(f"   实测质心速度  v ≈ ({vel[0]:+.3f}, {vel[1]:+.3f})")
    except Exception as exc:                  # 诊断出错不影响主流程
        print(f"   (质心/群速度诊断跳过: {exc})")
    print("-" * 74)

    if P.plot_packet:
        nx, ny = make_grid(P.N)
        _sy, _sz, _st_k = _packet(nx, ny)
        aux.plot_packet(_sy + 1j * _sz, _st_k, outdir / "packet.png",
                        k0=K0, sigma=SIGMA, rho=RHO, copies=COPIES,
                        pitch=PITCH, thresh=THRESH)

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
    return 0


def run_long(P, sy0, sz0, outdir):
    """模式 2：长时间观察，只出「二阶矩-时间」与「初始构型」两张 PNG。"""
    res = evolve_until(P, sy0, sz0, factor=STOP_FACTOR, tmax_cap=TMAX_CAP)
    m2_0 = res["M2_0"]
    print(f"   积分: dt = {res['dt']:.6g}, {res['steps']} 步, "
          f"t_end = {res['t'][-1]:.2f}")
    print(f"   M2(0) = {m2_0:.4f}  →  目标 {STOP_FACTOR:g}× = {res['target']:.4f}   "
          f"实际 M2 = {res['M2'][-1]:.4f}")
    print(f"   RMS 宽度: {np.sqrt(m2_0):.2f} → {np.sqrt(res['M2'][-1]):.2f} 格点")
    if not res["stopped"]:
        print(f"   ⚠ 到 TMAX_CAP={TMAX_CAP:g} 仍未达到目标倍数，已强制停止")
    print("-" * 74)
    plot_second_moment(res, P, outdir / "second_moment.png")
    plot_initial_packet(sy0, sz0, P, outdir / "initial_packet.png")
    return 0


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
    p.add_argument("--plot-packet", dest="plot_packet", action="store_true",
                   help="额外输出初态对照图 packet.png（k 空间包络 + 实空间波包）")
    p.add_argument("--mode", type=int, choices=(1, 2, 3), default=None,
                   help="直接指定运行模式（1 常规 / 2 长时间观察 / 3 补偿）；不给就启动时询问")
    return p


MODENAME = {1: "1 · 常规（GIF + 快照）", 2: "2 · 长时间观察（二阶矩）",
            3: "3 · 补偿（论文补偿相位，比较不同 T）"}


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    P = Params(**{k: v for k, v in vars(args).items()})
    if P.N < 4:
        print("N 至少取 4", file=sys.stderr)
        return 2

    # ---- 选模式：命令行优先，否则用 input() 问 -------------------------------
    mode = P.mode if P.mode in (1, 2, 3) else ask_mode()

    # ---- 输出目录：每次运行一个以日期时间命名的新文件夹 ----------------------
    base = Path(__file__).resolve().parent
    if P.outdir is not None:
        outdir = Path(P.outdir)
    else:
        sub = {1: "spin_wave_out", 2: "evolution", 3: "compensation"}[mode]
        outdir = base / sub / _stamp()
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
    print(f" 模式 : {MODENAME[mode]}")
    print(f" 体系 : {P.N}×{P.N}  PBC   S={P.S:g}  Jx={P.Jx:g}  Jy={P.Jy:g}  h={P.h:g}")
    print(f" A_k  : h - 2S(Jx cos kx + Jy cos ky),  max|A| = {P.amax():.4f}")
    print(f" 初态 : max|s^y| = {np.abs(sy0).max():.4f}, "
          f"max|s^z| = {np.abs(sz0).max():.4f},  Q(0) = {norm0:.6e}")
    if norm0 <= 0:
        print(" 初态恒为 0，没有东西可演化", file=sys.stderr)
        return 2
    print("-" * 74)

    aux.curvature_report(P.N, K0, S=P.S, Jx=P.Jx, Jy=P.Jy, h=P.h, sigma=SIGMA)
    print("-" * 74)
    print(f" 输出目录: {outdir}")

    t0 = time.perf_counter()
    if mode == 3:
        rc = run_compensation(P, outdir)
    elif mode == 2:
        rc = run_long(P, sy0, sz0, outdir)
    else:
        rc = run_standard(P, sy0, sz0, outdir)

    print("-" * 74)
    print(f" 完成，用时 {time.perf_counter() - t0:.1f} s")
    print("=" * 74)
    return rc


if __name__ == "__main__":
    sys.exit(main())
