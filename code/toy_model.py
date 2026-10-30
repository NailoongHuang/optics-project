import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from spin_wave_2d import Params

# ============ 参数设置 ============
a  = 1.0      # 晶格常数
P = Params()  # Same S, exchange couplings and Zeeman energy as the evolution.
Jx, Jy, S, h = P.Jx, P.Jy, P.S, P.h

# ============ 布里渊区网格 ============
N = 200
kx = np.linspace(-np.pi/a, np.pi/a, N)
ky = np.linspace(-np.pi/a, np.pi/a, N)
KX, KY = np.meshgrid(kx, ky)

# ============ 色散关系 ============
E, _ = P.dispersion(KX*a, KY*a)

# ============ 三维绘图 ============
fig = plt.figure(figsize=(10, 7))
ax  = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(KX, KY, E,
                       cmap='viridis',
                       edgecolor='none',
                       rstride=2, cstride=2,   # 稀疏采样，让网格更清晰
                       alpha=0.95,
                       antialiased=True)

# ============ 坐标轴和标签 ============
ax.set_xlabel(r'$k_x a$', fontsize=13, labelpad=8)
ax.set_ylabel(r'$k_y a$', fontsize=13, labelpad=8)
ax.set_zlabel(r'$\epsilon_{\mathbf{k}}$',  fontsize=13, labelpad=8)
ax.set_title(r'自旋波色散: $\epsilon_{\mathbf{k}} = h+2S[J_x(1-\cos k_xa)+J_y(1-\cos k_ya)]$',
             fontsize=14)

# 让坐标刻度以 π 为单位
ticks = [-np.pi, -np.pi/2, 0, np.pi/2, np.pi]
labels = [r'$-\pi$', r'$-\pi/2$', r'$0$', r'$\pi/2$', r'$\pi$']
ax.set_xticks(ticks); ax.set_xticklabels(labels)
ax.set_yticks(ticks); ax.set_yticklabels(labels)

# 色彩条
fig.colorbar(surf, ax=ax, shrink=0.6, aspect=12, pad=0.1, label='E')

# 视角
ax.view_init(elev=28, azim=-55)

plt.tight_layout()
plt.savefig('dispersion_3d.png', dpi=200, bbox_inches='tight')
plt.show()
