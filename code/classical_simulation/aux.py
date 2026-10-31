#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aux.py — 在倒空间构造高斯自旋波包，再变换回实空间
================================================================================

约定（与 toy_model_EOM.tex / main.py 一致，a = 1）
--------------------------------------------------
    s̃ = s^y + i s^z ,     ds̃/dt = -i A s̃ ,     A_k = h - 2S(J_x cos k_x + J_y cos k_y)

于是每个 k 模式按 e^{-iA_k t} 旋转（带符号频率 ω_k = A_k）：
    s̃_k(t) = s̃_k(0) e^{-iA_k t}
    v_g = ∇_k A_k = 2S(J_x sin k_x, J_y sin k_y)
    曲率 Hessian = diag(2S J_x cos k_x, 2S J_y cos k_y)   （A_k 可分，混合项恒为 0）

**两个方向曲率同时为零**有且仅有 k = (±π/2, ±π/2)，与 J_x, J_y, h, S 都无关：
该点二次项严格为零，残余色散从三次项 ∓(S/3)(J_x q_x³ + J_y q_y³) 开始。
要求 π/2 落在离散网格上，N 必须是 4 的倍数。

构造
----
    s̃_k = Σ_{n1,n2} f(k − k₀ − n1·Δ1 − n2·Δ2) · e^{ i φ(k − k₀ − n1·Δ1 − n2·Δ2) }

f 是二维高斯（带相关系数 ρ，峰值 1），φ 定义在**相对坐标** q = k − 中心 上，
各镜像副本共用同一个 φ（相位保持一致）。之后：
    1) 丢掉 |s̃_k| < thresh·max 的模式（让 k 空间支撑干净、有限）；
    2) 乘 e^{−i k·r₀} 把波包平移到 r₀（默认盒子中心）；
    3) ifft2 回实空间，按 amp 归一化。

关于"多个布里渊区的点"（copies / pitch）—— 这一步要小心
----------------------------------------------------------
在连续 r 下，把同样的包放在 k₀, k₀+Δ, k₀+2Δ, … 上，实空间确实多出一个因子

    1 + e^{iΔ·r} + e^{2iΔ·r} + …

· Δ = 2π（倒格矢）时，在**整数格点** r 上 e^{i2πr} = 1，这个因子恒等于副本数，
  于是与单峰结果只差一个常数（归一化后逐位相同）。它对应的其实是"把 k 空间包络
  周期化"，而周期化与实空间采样本来就是同一件事，所以不会产生新结构。
· Δ = 2π/L（L > 1）时，因子 = 1 + 2cos(2πr/L) + …，在 r ≡ 0 (mod L) 处为 L、
  在别处接近 0 —— 波包被压进间隔 L 的一条条窄瓣里，这才是"在某些区域更局域"的
  机制；代价是它成了多个不同 Bloch 模式的叠加，会以 Δω 拍动，不再是单一模式。

所以 pitch 默认取倒格矢 (2π, 2π)（等价于不做），需要局域化就改成 2π/L。
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

TWO_PI = 2.0 * np.pi


# ============================================================================
#  k 网格与工具
# ============================================================================
def kgrid(N: int):
    """返回 (KX, KY)：弧度，np.fft 顺序（覆盖 (−π, π] 的一个周期），行←ky，列←kx。"""
    k = np.fft.fftfreq(N) * TWO_PI
    KX, KY = np.meshgrid(k, k, indexing="xy")
    return KX, KY


def wrap_k(q):
    """把 k 空间差值折回 (−π, π]：k 空间是以 2π 为周期的环面。"""
    return q - TWO_PI * np.round(q / TWO_PI)


def _gauss_k(qx, qy, s1, s2, rho):
    """二维高斯（相关系数 rho），峰值 1，就是你在图里给的那个形式。"""
    u = qx / s1
    v = qy / s2
    return np.exp(-(u * u - 2.0 * rho * u * v + v * v) / (2.0 * (1.0 - rho * rho)))


def split(st):
    """s̃ = s^y + i s^z → (s^y, s^z)，两个实数组。"""
    st = np.asarray(st)
    return st.real.copy(), st.imag.copy()


def second_moment(sy, sz, N=None):
    """周期边界下的二阶矩（相对质心，最小镜像距离），返回 (M2, M2x, M2y, cx, cy)。

    权重 w = (s^y)^2 + (s^z)^2，质心用圆周平均求（不会被 PBC 撕开）：
        M2 = Σ_r w(r) [dx² + dy²] / Σ_r w(r)
    对宽 σ 的二维高斯包，各向同性时 M2 = 2σ²；均匀分布时 M2 → N²/6。
    """
    sy = np.asarray(sy, dtype=float)
    sz = np.asarray(sz, dtype=float)
    N = int(sy.shape[0] if N is None else N)
    w = sy * sy + sz * sz
    tot = float(w.sum())
    if tot <= 1e-300:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    ph = np.exp(2j * np.pi * np.arange(N) / N)
    cx = float(np.angle((w.sum(axis=0) * ph).sum()) * N / TWO_PI) % N
    cy = float(np.angle((w.sum(axis=1) * ph).sum()) * N / TWO_PI) % N
    xs = np.arange(N, dtype=float)[None, :]
    ys = np.arange(N, dtype=float)[:, None]
    dx = xs - cx
    dx -= N * np.round(dx / N)
    dy = ys - cy
    dy -= N * np.round(dy / N)
    m2x = float((w * dx * dx).sum() / tot)
    m2y = float((w * dy * dy).sum() / tot)
    return m2x + m2y, m2x, m2y, cx, cy


# ============================================================================
#  主函数：k 空间高斯波包 → 实空间
# ============================================================================
def gaussian_k_packet(N, *, k0=(np.pi / 2, np.pi / 2), sigma=(0.25, 0.25), rho=0.0,
                      phase=None, copies=(0, 0), pitch=(TWO_PI, TWO_PI),
                      thresh=1e-6, amp=1.0, normalize="peak", r0=None,
                      return_k=False, verbose=False):
    """在 k 空间放一个（或几个）高斯包，ifft 回实空间，返回复数场 s̃ = s^y + i s^z。

    参数
    ----
    N        : 晶格尺寸，k 网格正好 N×N 个点（PBC 下与实空间格点数相同）。
    k0       : 中心波矢（弧度）。零曲率点用 (±π/2, ±π/2)。
    sigma    : (σ1, σ2)，k 空间高斯沿 kx、ky 的标准差（弧度）；实空间宽度 ≈ 1/σ。
    rho      : kx、ky 的相关系数，−1 < rho < 1。
    phase    : φ(qx, qy)，q 为相对坐标（可为 −π..π 的网格数组）。
               返回实数 → 当作相位，乘 e^{iφ}；返回复数 → 直接当复因子用。
               None → 全零相位。
    copies   : (m1, m2)，在各方向加 m 层镜像，共 (2m1+1)(2m2+1) 个副本。
    pitch    : (Δ1, Δ2) 副本平移矢量（弧度）。2π = 倒格矢（整数格点上因子为常数，
               与单峰等价）；2π/L 才能得到实空间光栅式的局域化。
    thresh   : |s̃_k|/max 小于此值的模式直接置零。
    amp      : 目标幅度；normalize = "peak"（max|s̃|=amp）| "norm"（Σ|s̃|²=amp²）| "none"。
    r0       : 波包在实空间的中心（格点坐标）。None → 盒子中心；给 (0,0) 回到原点。
    return_k : 同时返回 k 空间数组（调试用）。
    verbose  : 打印一句构造摘要。

    返回
    ----
    s̃(r)（复数，(N,N)）；return_k=True 时返回 (s̃(r), s̃(k))。
    """
    N = int(N)
    if N < 4:
        raise ValueError("N 太小")
    s1, s2 = float(sigma[0]), float(sigma[1])
    if s1 <= 0 or s2 <= 0:
        raise ValueError("sigma 必须为正")
    rho = float(rho)
    if not -1.0 < rho < 1.0:
        raise ValueError("rho 必须落在 (−1, 1)")
    if isinstance(copies, (int, np.integer)):
        copies = (copies, copies)
    m1, m2 = int(copies[0]), int(copies[1])
    if m1 < 0 or m2 < 0:
        raise ValueError("copies 不能为负")
    p1, p2 = float(pitch[0]), float(pitch[1])
    if normalize not in ("peak", "norm", "none"):
        raise ValueError("normalize 只能是 'peak' / 'norm' / 'none'")

    KX, KY = kgrid(N)
    st = np.zeros((N, N), dtype=complex)
    n_copies = 0
    for n1 in range(-m1, m1 + 1):
        for n2 in range(-m2, m2 + 1):
            n_copies += 1
            qx = wrap_k(KX - (k0[0] + n1 * p1))
            qy = wrap_k(KY - (k0[1] + n2 * p2))
            env = _gauss_k(qx, qy, s1, s2, rho)
            if phase is None:
                st += env
            else:
                ph = np.asarray(phase(qx, qy))
                st += env * ph if np.iscomplexobj(ph) else env * np.exp(1j * ph)

    peak = float(np.abs(st).max())
    if peak <= 0.0:
        raise ValueError("包络全为零：检查 sigma / k0")
    if thresh and thresh > 0:
        keep = np.abs(st) >= thresh * peak
        st = np.where(keep, st, 0.0)
        n_kept = int(keep.sum())
    else:
        keep = np.ones_like(st, dtype=bool)
        n_kept = N * N

    # 平移到 r0（k 空间乘一个线性相位，不改变形状）
    r0 = (N / 2.0, N / 2.0) if r0 is None else (float(r0[0]), float(r0[1]))
    st = st * np.exp(-1j * (KX * r0[0] + KY * r0[1]))

    st_r = np.fft.ifft2(st)

    if normalize == "peak":
        st_r = st_r * (amp / np.abs(st_r).max())
    elif normalize == "norm":
        st_r = st_r * (amp / np.sqrt(np.sum(np.abs(st_r) ** 2)))
    else:
        st_r = st_r * amp

    if verbose:
        kx_kept = np.unique(np.round(KX[keep], 6))
        ky_kept = np.unique(np.round(KY[keep], 6))
        ax = np.unravel_index(np.argmax(np.abs(st_r)), st_r.shape)
        print(f"[波包] N={N}, k0=({k0[0]:+.4f}, {k0[1]:+.4f}), "
              f"sigma=({s1:g}, {s2:g}), rho={rho:g}, 副本 {n_copies} 个")
        print(f"       保留模式 {n_kept}/{N * N} (thresh={thresh:g})，"
              f"k 支撑: kx∈[{kx_kept.min():+.2f},{kx_kept.max():+.2f}], "
              f"ky∈[{ky_kept.min():+.2f},{ky_kept.max():+.2f}]")
        print(f"       实空间: max|s̃|={np.abs(st_r).max():.4f}, "
              f"Σ|s̃|²={np.sum(np.abs(st_r) ** 2):.4f}, "
              f"峰值位置≈({ax[1]}, {ax[0]})")

    return (st_r, st) if return_k else st_r


# ============================================================================
#  选点自检：曲率 / 群速度 / 残余色散
# ============================================================================
def curvature_report(N, k0=(np.pi / 2, np.pi / 2), *, S=1.0, Jx=1.0, Jy=0.5, h=0.5,
                     sigma=None, verbose=True):
    """打印并返回 k₀ 处的 A_k、ω、v_g、Hessian、三次项、最近网格点与残余色散估计。"""
    kx0, ky0 = float(k0[0]), float(k0[1])

    def A(kx, ky):
        return h - 2.0 * S * (Jx * np.cos(kx) + Jy * np.cos(ky))

    a0 = A(kx0, ky0)
    gx, gy = 2.0 * S * Jx * np.sin(kx0), 2.0 * S * Jy * np.sin(ky0)
    dxx, dyy = 2.0 * S * Jx * np.cos(kx0), 2.0 * S * Jy * np.cos(ky0)
    cxxx, cyyy = -2.0 * S * Jx * np.sin(kx0), -2.0 * S * Jy * np.sin(ky0)

    # 数值核对 Hessian（中心差分）
    e = 1e-4
    n_dxx = (A(kx0 + e, ky0) - 2.0 * a0 + A(kx0 - e, ky0)) / e ** 2
    n_dyy = (A(kx0, ky0 + e) - 2.0 * a0 + A(kx0, ky0 - e)) / e ** 2

    # 最近网格点
    kk = np.fft.fftfreq(N) * TWO_PI
    i1 = int(np.argmin(np.abs(wrap_k(kk - kx0))))
    i2 = int(np.argmin(np.abs(wrap_k(kk - ky0))))
    dk1 = float(wrap_k(kk[i1] - kx0))
    dk2 = float(wrap_k(kk[i2] - ky0))
    a_grid = A(kk[i1], kk[i2])
    curv_grid = (2.0 * S * Jx * np.cos(kk[i1]), 2.0 * S * Jy * np.cos(kk[i2]))

    vg = float(np.hypot(gx, gy))
    curv = (dxx, dyy)
    on_grid = (abs(dk1) < 1e-12 and abs(dk2) < 1e-12)

    out = {"A_k0": a0, "omega": a0, "v_g": (gx, gy), "curv": curv,
           "cubic": (cxxx, cyyy), "nearest_grid": (i1, i2, dk1, dk2),
           "curv_on_grid": curv_grid, "on_grid": on_grid}

    if sigma is not None:
        s1, s2 = float(sigma[0]), float(sigma[1])
        # 速度散布：二阶 ~ |∂²A|σ，三阶 ~ |∂³A|σ²/2
        dv2 = (abs(dxx) * s1, abs(dyy) * s2)
        dv3 = (abs(cxxx) * s1 * s1 / 2.0, abs(cyyy) * s2 * s2 / 2.0)
        out["dv_2nd"] = dv2
        out["dv_3rd"] = dv3

    if verbose:
        ok = "✓ 零曲率" if max(abs(dxx), abs(dyy)) < 1e-12 else "（有曲率）"
        print(f"[曲率诊断] N={N}, k0=({kx0:+.4f}, {ky0:+.4f})"
              f"   N%4={N % 4}" + ("，鞍点正好落在网格上" if on_grid else "，k0 不在网格点上"))
        print(f"   A_k0 = {a0:+.4f} = ω_k0，周期 2π/ω = "
              f"{(TWO_PI / abs(a0) if a0 else float('inf')):.2f}")
        print(f"   群速度 v_g = ∇A = ({gx:+.4f}, {gy:+.4f}), |v_g| = {vg:.4f}")
        print(f"   曲率 (2SJx cos kx0, 2SJy cos ky0) = ({dxx:+.4f}, {dyy:+.4f})  {ok}")
        print(f"   数值核对: ({n_dxx:+.4f}, {n_dyy:+.4f})")
        print(f"   三次项 ∂³A/∂kx³,∂³A/∂ky³ = ({cxxx:+.4f}, {cyyy:+.4f})  ← 残余色散起点")
        if sigma is not None:
            print(f"   σ_k=({s1:g},{s2:g}) 的速度散布: 二阶 "
                  f"({out['dv_2nd'][0]:.4f},{out['dv_2nd'][1]:.4f}), 三阶 "
                  f"({out['dv_3rd'][0]:.4f},{out['dv_3rd'][1]:.4f})")
        print(f"   最近网格点 (m1,m2)=({i1},{i2})，相对偏移 ({dk1:+.4f},{dk2:+.4f})，"
              f"该点曲率 ({curv_grid[0]:+.4f},{curv_grid[1]:+.4f})")
        if vg > 0:
            out["t_transit"] = 0.6 * N / vg
            print(f"   走 0.6N={0.6 * N:.1f} 格点需 t ≈ {out['t_transit']:.2f}")
    return out


# ============================================================================
#  初态对照图：k 空间包络 + 实空间波包
# ============================================================================
def plot_packet(st_r, st_k=None, path=None, *, k0=(np.pi / 2, np.pi / 2),
                sigma=(0.25, 0.25), rho=0.0, copies=(0, 0),
                pitch=(TWO_PI, TWO_PI), thresh=1e-6, dpi=140, verbose=True):
    """画一张初态对照图，返回保存路径。

    上排：|s̃(k)|（含 1σ 椭圆、零曲率点、阈值轮廓）、arg s̃(k)、过 k0 的一维切面；
    下排：|s̃(r)|、s^y、s^z。
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
    except Exception:
        pass
    import matplotlib.pyplot as plt

    N = st_r.shape[0]
    if st_k is None:
        st_k = np.fft.fft2(st_r)
    KX, KY = kgrid(N)
    kk = np.fft.fftfreq(N) * TWO_PI
    kk_s = np.fft.fftshift(kk)
    amp_k = np.abs(st_k)
    kmax = float(amp_k.max())
    keep = amp_k >= thresh * kmax
    n_kept = int(keep.sum())

    sy, sz = split(st_r)
    absr = np.abs(st_r)
    w = sy * sy + sz * sz
    Wt = float(w.sum())
    ph = np.exp(2j * np.pi * np.arange(N) / N)
    rx = abs((w.sum(axis=0) * ph).sum()) / Wt
    ry = abs((w.sum(axis=1) * ph).sum()) / Wt
    sx = np.sqrt(-2.0 * np.log(rx)) * N / TWO_PI
    sy_r = np.sqrt(-2.0 * np.log(ry)) * N / TWO_PI
    ny_pk, nx_pk = np.unravel_index(int(np.argmax(absr)), absr.shape)

    m1, m2 = (copies, copies) if isinstance(copies, (int, np.integer)) else copies
    ext_k = (-np.pi, np.pi, -np.pi, np.pi)
    ext_r = (-0.5, N - 0.5, -0.5, N - 0.5)

    fig = plt.figure(figsize=(15.6, 9.6), dpi=dpi)
    gs = fig.add_gridspec(2, 3, hspace=0.34, wspace=0.28)

    # ---- (0,0) |s̃(k)| ------------------------------------------------------
    ax = fig.add_subplot(gs[0, 0])
    im = ax.imshow(np.fft.fftshift(amp_k), origin="lower", extent=ext_k,
                   cmap="magma", interpolation="nearest")
    ax.contour(kk_s, kk_s, np.fft.fftshift(amp_k), levels=[thresh * kmax],
               colors="w", linewidths=0.8)
    # 1σ 椭圆
    cov = np.array([[sigma[0] ** 2, rho * sigma[0] * sigma[1]],
                    [rho * sigma[0] * sigma[1], sigma[1] ** 2]])
    ell = np.linalg.cholesky(cov) @ np.stack([np.cos(np.linspace(0, TWO_PI, 200)),
                                              np.sin(np.linspace(0, TWO_PI, 200))])
    ax.plot(k0[0] + ell[0], k0[1] + ell[1], color="cyan", lw=1.0, label="1σ 包络")
    for a in (-1, 1):
        for b in (-1, 1):
            ax.plot(a * np.pi / 2, b * np.pi / 2, "o", mfc="none", mec="lime",
                    ms=6, mew=1.0, label="零曲率点" if (a, b) == (-1, -1) else None)
    for n1 in range(-m1, m1 + 1):
        for n2 in range(-m2, m2 + 1):
            if (n1, n2) != (0, 0):
                ax.plot(k0[0] + n1 * pitch[0], k0[1] + n2 * pitch[1], "+",
                        color="cyan", ms=8, mew=1.2)
    ax.plot(k0[0], k0[1], "x", color="w", ms=9, mew=1.6, label="k0")
    ax.set_xlim(-np.pi, np.pi)
    ax.set_ylim(-np.pi, np.pi)
    ax.set_aspect("equal")
    ax.set_xlabel("$k_x$")
    ax.set_ylabel("$k_y$")
    ax.set_title(f"$|\\tilde{{s}}(k)|$   （保留 {n_kept}/{N * N} 个模式）", fontsize=11)
    ax.legend(loc="lower left", fontsize=7.5, framealpha=0.85)
    fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)

    # ---- (0,1) arg s̃(k) ----------------------------------------------------
    ax = fig.add_subplot(gs[0, 1])
    # 先扣掉平移带来的线性相位 e^{-i k·r_pk}，剩下才是包络自身的相位（即 φ(k)）
    st_k_ph = st_k * np.exp(1j * (KX * nx_pk + KY * ny_pk))
    ang = np.ma.masked_where(~np.fft.fftshift(keep),
                             np.angle(np.fft.fftshift(st_k_ph)))
    im = ax.imshow(ang, origin="lower", extent=ext_k, cmap="twilight",
                   vmin=-np.pi, vmax=np.pi, interpolation="nearest")
    ax.set_xlim(-np.pi, np.pi)
    ax.set_ylim(-np.pi, np.pi)
    ax.set_aspect("equal")
    ax.set_xlabel("$k_x$")
    ax.set_ylabel("$k_y$")
    ax.set_title(r"$\arg\tilde{s}(k)$（已扣平移相位；阈值外留白）", fontsize=11)
    cb = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
    cb.set_ticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
    cb.set_ticklabels([r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"])

    # ---- (0,2) 过 k0 的一维切面 --------------------------------------------
    ax = fig.add_subplot(gs[0, 2])
    iy0 = int(np.argmin(np.abs(wrap_k(kk - k0[1]))))
    qx = wrap_k(KX[iy0, :] - k0[0])
    qy_row = np.full(N, wrap_k(KY[iy0, 0] - k0[1]))
    o = np.argsort(qx)
    ax.plot(qx[o], amp_k[iy0, o] / kmax, "o-", ms=3.2, lw=1.0,
            label=r"$|s_k|/\max$")
    ax.plot(qx[o], _gauss_k(qx[o], qy_row[o], sigma[0], sigma[1], rho), "--",
            lw=1.3, label="解析高斯")
    ax.axvline(0.0, color="k", lw=0.6)
    for s in (-sigma[0], sigma[0]):
        ax.axvline(s, color="gray", ls=":", lw=0.8)
    ax.axhline(thresh, color="r", ls=":", lw=0.8, label=f"thresh={thresh:g}")
    ax.set_xlim(max(-np.pi, qx.min() - 0.2), min(np.pi, qx.max() + 0.2))
    ax.set_ylim(-0.02, 1.08)
    ax.set_xlabel(r"$q_x = k_x - k_{0x}$")
    ax.set_ylabel("归一化振幅")
    ax.set_title(f"沿 $k_y={kk[iy0]:+.3f}$ 的切面", fontsize=11)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, loc="upper right")

    # ---- (1,0) |s̃(r)| ------------------------------------------------------
    ax = fig.add_subplot(gs[1, 0])
    im = ax.imshow(absr, origin="lower", extent=ext_r, cmap="magma",
                   interpolation="nearest")
    ax.plot(nx_pk, ny_pk, "+", color="cyan", ms=13, mew=1.4,
            label=f"峰值 ({nx_pk},{ny_pk})")
    ax.set_xlabel("$n_x$")
    ax.set_ylabel("$n_y$")
    ax.set_aspect("equal")
    ax.set_title(r"$|\tilde{s}(r)| = \sqrt{(s^y)^2+(s^z)^2}$", fontsize=11)
    ax.legend(loc="upper right", fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)

    # ---- (1,1)(1,2) s^y, s^z ----------------------------------------------
    for col, (arr, lab) in enumerate(((sy, "$s^y$"), (sz, "$s^z$"))):
        ax = fig.add_subplot(gs[1, 1 + col])
        vl = float(np.abs(arr).max()) or 1.0
        im = ax.imshow(arr, origin="lower", extent=ext_r, cmap="RdBu_r",
                       vmin=-vl, vmax=vl, interpolation="nearest")
        ax.set_xlabel("$n_x$")
        ax.set_ylabel("$n_y$")
        ax.set_aspect("equal")
        ax.set_title(f"{lab}   (max {vl:.3f})", fontsize=11)
        fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)

    fig.suptitle(
        f"初态：k0=({k0[0]:+.3f}, {k0[1]:+.3f})  σ=({sigma[0]:g}, {sigma[1]:g})  "
        f"ρ={rho:g}  副本 {(2 * m1 + 1) * (2 * m2 + 1)} 个  N={N}\n"
        f"保留 {n_kept}/{N * N} 个 k 模式    实空间 σx={sx:.2f}, σy={sy_r:.2f} 格点"
        f"    max$|\\tilde{{s}}|$={np.abs(st_r).max():.4f},  "
        f"Σ$|\\tilde{{s}}|^2$={Wt:.3f}",
        fontsize=11.5)

    path = Path(path) if path is not None else Path("packet.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    if verbose:
        print(f"   ✓ {path.name}")
    return path


# ============================================================================
#  自检 demo：python aux.py
# ============================================================================
def _demo():
    N = 64
    print("=" * 74)
    curvature_report(N, (np.pi / 2, np.pi / 2), sigma=(0.25, 0.25))

    base = dict(k0=(np.pi / 2, np.pi / 2), sigma=(0.25, 0.25), rho=0.0,
                amp=0.5, normalize="peak", thresh=1e-6, r0=(N / 2, N / 2))

    print("-" * 74)
    print("① 单峰 (无副本)")
    a = gaussian_k_packet(N, copies=(0, 0), **base)

    print("② 倒格矢副本 pitch=(2π,2π), copies=(1,1)")
    b = gaussian_k_packet(N, copies=(1, 1), pitch=(TWO_PI, TWO_PI), **base)
    print(f"   与单峰的最大差异: {np.abs(a - b).max():.3e}  ← 应约等于机器精度"
          f"（整数格点上 e^{{iGr}} = 1，因子恒为常数 9）")

    print("③ 分数平移 pitch=(2π/3,0), copies=(1,0)")
    c = gaussian_k_packet(N, copies=(1, 0), pitch=(TWO_PI / 3, 0), **base)
    print(f"   与单峰的最大差异: {np.abs(a - c).max():.3e}  ← 这里出现真实光栅")

    def lobes(f, frac=0.2):
        m = np.abs(f) > frac * np.abs(f).max()
        return m.sum()

    print(f"   半高以上的格点数: 单峰 {lobes(a)}, 光栅 {lobes(c)}"
          f"  （光栅每 3 列一瓣，被压窄约 3 倍）")
    print("=" * 74)


if __name__ == "__main__":
    _demo()
