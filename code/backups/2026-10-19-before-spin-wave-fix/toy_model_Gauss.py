import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ============ 参数 ============
a  = 1.0
Jx = 1.0
Jy = 0.5          # 想观察各向异性可改成 0.5

# ============ 布里渊区网格 ============
N = 300
kx = np.linspace(-np.pi/a, np.pi/a, N)
ky = np.linspace(-np.pi/a, np.pi/a, N)
KX, KY = np.meshgrid(kx, ky)

# ============ 色散 E(kx, ky) ============
E = Jx*(1 - np.cos(KX*a)) + Jy*(1 - np.cos(KY*a))

# ============ 高斯曲率 K(kx, ky) ============
num = (a**2 * Jx * np.cos(KX*a)) * (a**2 * Jy * np.cos(KY*a))
den = (1 + (a*Jx*np.sin(KX*a))**2 + (a*Jy*np.sin(KY*a))**2)**2
GaussK = num / den

# 便于观察：以 π 为单位的刻度
ticks  = [-np.pi, -np.pi/2, 0, np.pi/2, np.pi]
labels = [r'$-\pi$', r'$-\pi/2$', r'$0$', r'$\pi/2$', r'$\pi$']

def style_axes(ax):
    ax.set_xticks(ticks); ax.set_xticklabels(labels)
    ax.set_yticks(ticks); ax.set_yticklabels(labels)
    ax.set_xlabel(r'$k_x a$', fontsize=12, labelpad=6)
    ax.set_ylabel(r'$k_y a$', fontsize=12, labelpad=6)

# ================= 图1：E-k 色散图 =================
fig1 = plt.figure(figsize=(9, 7))
ax1  = fig1.add_subplot(111, projection='3d')
surf1 = ax1.plot_surface(KX, KY, E, cmap='viridis',
                         edgecolor='none', rstride=3, cstride=3,
                         alpha=0.95, antialiased=True)
ax1.set_zlabel(r'$E$', fontsize=12, labelpad=6)
ax1.set_title(r'色散关系 $E=J_x(1-\cos k_xa)+J_y(1-\cos k_ya)$',
              fontsize=13)
style_axes(ax1)
fig1.colorbar(surf1, ax=ax1, shrink=0.6, aspect=12, pad=0.1, label='E')
ax1.view_init(elev=28, azim=-55)
plt.tight_layout()
plt.savefig('E_k.png', dpi=200, bbox_inches='tight')
plt.show()

# ================= 图2：K-k 高斯曲率图 =================
fig2 = plt.figure(figsize=(9, 7))
ax2  = fig2.add_subplot(111, projection='3d')

# 用发散色标使正负曲率对比明显；vmin/vmax 对称
vmax = np.abs(GaussK).max()
surf2 = ax2.plot_surface(KX, KY, GaussK, cmap='RdBu_r',
                         vmin=-vmax, vmax=vmax,
                         edgecolor='none', rstride=3, cstride=3,
                         alpha=0.95, antialiased=True)
ax2.set_zlabel(r'$K$', fontsize=12, labelpad=6)
ax2.set_title(r'高斯曲率 $K=\dfrac{J_xJ_ya^4\cos(k_xa)\cos(k_ya)}'
              r'{\left[1+(aJ_x\sin k_xa)^2+(aJ_y\sin k_ya)^2\right]^2}$',
              fontsize=12)
style_axes(ax2)
fig2.colorbar(surf2, ax=ax2, shrink=0.6, aspect=12, pad=0.1, label='K')
ax2.view_init(elev=28, azim=-55)
plt.tight_layout()
plt.savefig('K_k.png', dpi=200, bbox_inches='tight')
plt.show()

# ============ 可选：俯视等能面 / 曲率等高线 ============
fig3, axes = plt.subplots(1, 2, figsize=(12, 5))

c1 = axes[0].contourf(KX/np.pi, KY/np.pi, E, levels=30, cmap='viridis')
axes[0].set_title(r'$E$ 等能面（俯视）')
axes[0].set_xlabel(r'$k_x a/\pi$'); axes[0].set_ylabel(r'$k_y a/\pi$')
axes[0].set_aspect('equal')
fig3.colorbar(c1, ax=axes[0], shrink=0.8)

c2 = axes[1].contourf(KX/np.pi, KY/np.pi, GaussK, levels=30,
                      cmap='RdBu_r', vmin=-vmax, vmax=vmax)
axes[1].set_title(r'$K$ 等高线（俯视）')
axes[1].set_xlabel(r'$k_x a/\pi$'); axes[1].set_ylabel(r'$k_y a/\pi$')
axes[1].set_aspect('equal')
fig3.colorbar(c2, ax=axes[1], shrink=0.8)

plt.tight_layout()
plt.savefig('EK_overview.png', dpi=200, bbox_inches='tight')
plt.show()