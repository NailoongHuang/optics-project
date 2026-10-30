"""Generate the dispersion/principle figures for the midterm report.

Run from any directory with Python; outputs remain beside this script.
The plotted energy is the exact S=1/2 one-magnon band with h=0.
q=k*a, e=epsilon/Jx, eta=Jy/Jx, u=hbar*v/(Jx*a).
"""
from __future__ import annotations

import platform
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
import pymupdf
from matplotlib.patches import FancyArrowPatch, Circle
from common import ROOT, COLORS, INK, energy, heading, save_figure, write_json

GROUP = 'a-dispersion'
BASE = dict(S=0.5, h=0.0, q='k*a', energy='epsilon/Jx', eta='Jy/Jx',
            velocity='hbar*v/(Jx*a)', boundary='first Brillouin zone')
ENTRIES = []
DATA = {}


def axes_pi(ax, both=False):
    values = np.linspace(-np.pi, np.pi, 5)
    labels = [r'$-\pi$', r'$-\pi/2$', '$0$', r'$\pi/2$', r'$\pi$']
    ax.set_xticks(values, labels)
    ax.set_xlim(-np.pi, np.pi)
    if both:
        ax.set_yticks(values, labels)
        ax.set_ylim(-np.pi, np.pi)
        ax.set_xlabel(r'$q_x=k_xa$')
        ax.set_ylabel(r'$q_y=k_ya$')
        ax.set_aspect('equal')
    ax.grid(alpha=.16)


def finish(fig, stem, title, caption, params=None, role='core'):
    entry = save_figure(fig, GROUP, stem, title, caption,
                        {**BASE, **(params or {})}, role=role)
    entry['figure_inches'] = list(fig.get_size_inches())
    entry['raster_dpi'] = 170
    ENTRIES.append(entry)


def lattice():
    fig, ax = plt.subplots(figsize=(12.8, 8))
    heading(fig, 'A01  交换作用连接相邻格点',
            r'二维正方晶格；$J_x,J_y>0$；单翻转基底 $|m,n\rangle$ 的一幅示意',
            '背景自旋沿 +x 极化，中心自旋沿 −x；蓝色实线与橙色虚线分别标出 x、y 方向的交换键。')
    ax.set_position([.06,.16,.56,.64])
    for y in range(-2,3):
        for x in range(-2,2):
            ax.plot([x,x+1],[y,y],color=COLORS[0],lw=2.8,alpha=.62)
    for x in range(-2,3):
        for y in range(-2,2):
            ax.plot([x,x],[y,y+1],color=COLORS[1],lw=2.8,ls='--',alpha=.7)
    for y in range(-2,3):
        for x in range(-2,3):
            flipped = x == 0 and y == 0
            color = '#9C315D' if flipped else INK
            ax.add_patch(Circle((x,y),.075,color=color,zorder=4))
            start,end=(.28,-.28) if flipped else (-.24,.24)
            ax.add_patch(FancyArrowPatch((x+start,y),(x+end,y),arrowstyle='-|>',
                                         mutation_scale=19,color=color,lw=2,zorder=5))
    ax.annotate(r'$|0,0\rangle$',xy=(0,0),xytext=(.6,.6),fontsize=18,color='#9C315D',
                arrowprops=dict(arrowstyle='->',color='#9C315D'))
    ax.annotate('',xy=(2.4,-2.65),xytext=(1.1,-2.65),arrowprops=dict(arrowstyle='->',lw=1.8))
    ax.text(2.45,-2.65,'x',va='center',fontsize=16)
    ax.annotate('',xy=(-2.6,2.3),xytext=(-2.6,1),arrowprops=dict(arrowstyle='->',lw=1.8))
    ax.text(-2.6,2.45,'y',ha='center',fontsize=16)
    ax.set(xlim=(-2.9,2.9),ylim=(-2.95,2.8),aspect='equal')
    ax.axis('off')
    fig.text(.65,.71,r'$\eta=J_y/J_x$',fontsize=24,color=INK)
    fig.text(.65,.60,'横向交换：'+r'$J_x$',fontsize=18,color=COLORS[0])
    fig.text(.65,.52,'纵向交换：'+r'$J_y$',fontsize=18,color=COLORS[1])
    fig.text(.65,.39,r'$|\psi(\tau)\rangle=\sum_{m,n}c_{mn}(\tau)|m,n\rangle$',fontsize=17)
    fig.text(.65,.29,r'$P_{mn}(\tau)=|c_{mn}(\tau)|^2$',fontsize=18)
    finish(fig,'a01-lattice','交换晶格与单翻转基底',
           '25个格点的局部示意中，蓝色实线是横向交换键，橙色虚线是纵向交换键。背景自旋沿+x极化，中心沿-x的箭头代表单翻转基底|0,0>；时间演化后态为这些基底的量子叠加，P_mn=|c_mn|²是测得翻转位于该点的概率。图中箭头示意量子化轴上的取向，不把固定单磁子态的系数解释为经典横向磁矩。eta描述空间方向的交换各向异性。',
           dict(display_lattice=[5,5],schematic=True))


def surface(eta, stem, title):
    fig = plt.figure(figsize=(12.8,8))
    heading(fig,title,rf'$e(\mathbf{{q}})=1-\cos q_x+\eta(1-\cos q_y)$，$\eta={eta:g}$；$e=\varepsilon/J_x$',
            '高度与颜色都表示同一激发能；两幅曲面采用相同的 0–4 能量范围，可直接比较纵向带宽。')
    ax=fig.add_axes([.07,.14,.69,.65],projection='3d')
    q=np.linspace(-np.pi,np.pi,81); qx,qy=np.meshgrid(q,q)
    z=energy(qx,qy,eta)
    surf=ax.plot_surface(qx,qy,z,cmap='viridis',vmin=0,vmax=4,
                         rstride=2,cstride=2,linewidth=.12,edgecolor=(1,1,1,.12),antialiased=True)
    ax.view_init(elev=28,azim=-54)
    ax.set(xlim=(-np.pi,np.pi),ylim=(-np.pi,np.pi),zlim=(0,4),
           xlabel=r'$q_x$',ylabel=r'$q_y$',zlabel=r'$e$')
    for axis in (ax.xaxis,ax.yaxis): axis.set_ticks([-np.pi,0,np.pi],labels=[r'$-\pi$','0',r'$\pi$'])
    ax.zaxis.set_ticks([0,1,2,3,4]); ax.set_box_aspect((1,1,.65))
    ax.scatter([0],[0],[0],color='#CC3311',s=35,depthshade=False)
    cax=fig.add_axes([.84,.29,.025,.38]); cb=fig.colorbar(surf,cax=cax)
    cb.set_label(r'$e=\varepsilon/J_x$',labelpad=11)
    fig.text(.78,.74,rf'$0\leq e\leq {2*(1+eta):g}$',fontsize=17,color=INK)
    DATA[f'{stem}_q']=q; DATA[f'{stem}_energy']=z
    finish(fig,stem,title[5:],
           f'在第一布里渊区内绘出eta={eta:g}的精确余弦色散。原点能量为零，最大能量为2(1+eta)={2*(1+eta):g}。高度与统一的0至4色标都表示epsilon/Jx。曲面在原点附近近似抛物面；eta<1时沿qy方向起伏较小。三维透视用于概览，方向比较应结合A04的共同坐标截面。',dict(eta_value=eta,mesh=81,color_limits=[0,4]))


def cuts():
    q=np.linspace(-np.pi,np.pi,1001)
    fig,axes=plt.subplots(1,2,figsize=(12.8,8),sharey=True)
    heading(fig,'A04  沿不同方向切开色散曲面',
            '固定另一个波矢分量为零；两条曲线使用相同的横轴与纵轴。',
            '交换越强，相应方向的能量变化越大；原点处斜率为零，并不意味着附近波包不能逐渐展开。')
    for ax,eta in zip(axes,[1,.35]):
        ax.plot(q,energy(q,0,eta),lw=3,label=r'$e(q_x,0)$：沿 x')
        ax.plot(q,energy(0,q,eta),lw=3,ls='--',label=r'$e(0,q_y)$：沿 y')
        axes_pi(ax); ax.set(ylim=(0,2.18),xlabel=r'沿所选方向的 $q$',title=rf'$\eta={eta:g}$')
        ax.legend(loc='upper center'); ax.set_ylabel(r'$e=\varepsilon/J_x$')
    finish(fig,'a04-axial-cuts','方向色散截面',
           '左图eta=1时沿x和y的截面完全重合（虚线覆盖实线），右图eta=0.35时y方向带宽降为0.7，而x方向带宽仍为2。每条曲线都固定另一分量为零，不能把两条轴向截面当成一般斜向传播的完整色散。',dict(eta_values=[1,.35],sample_points=1001))


def contours():
    q=np.linspace(-np.pi,np.pi,501); x,y=np.meshgrid(q,q)
    fig,axes=plt.subplots(1,2,figsize=(12.8,8))
    heading(fig,'A05  等频线：能量相同的波矢在哪里？',
            '同一条曲线上的模式具有相同频率；两个面板采用完全相同的等能值。',
            '长波区近圆或椭圆；接近布里渊区边界后必须使用完整余弦色散。等频不代表所有群速度相同。')
    levels=[.2,.6,1.2,2.0,2.5]
    for ax,eta in zip(axes,[1,.35]):
        cs=ax.contour(x,y,energy(x,y,eta),levels=levels,cmap='viridis',vmin=0,vmax=3.6,linewidths=2)
        ax.clabel(cs,fmt='%g',fontsize=11)
        axes_pi(ax,True); ax.set_title(rf'$\eta={eta:g}$，曲线数字为 $e$')
    finish(fig,'a05-equal-frequency','等频曲线',
           '曲线数字是e=epsilon/Jx，依次为0.2、0.6、1.2、2、2.5。小波矢附近，eta=1的等频线近圆，eta=0.35时沿qy方向拉长；高波矢处方格晶格的结构清楚可见。等频线仅约束频率，群速度还取决于曲面的梯度，不能据此宣称局域波包保形。',dict(eta_values=[1,.35],levels=levels,mesh=501))


def velocity_field():
    q=np.linspace(-np.pi,np.pi,17); x,y=np.meshgrid(q,q)
    fine=np.linspace(-np.pi,np.pi,401); fx,fy=np.meshgrid(fine,fine)
    fig,axes=plt.subplots(1,2,figsize=(12.8,8))
    heading(fig,'A06  群速度沿等频线的法向',
            r'$\mathbf{u}=\hbar\mathbf{v}_g/(J_xa)=\nabla_{\mathbf{q}}e=(\sin q_x,\eta\sin q_y)$',
            '箭头保留相对长度，两个面板使用同一比例尺；在能带极值等驻点处，群速度为零。')
    for ax,eta in zip(axes,[1,.35]):
        ax.contour(fx,fy,energy(fx,fy,eta),levels=[.3,.8,1.4,2,2.6,3.4],colors='#AEBBC4',linewidths=.9)
        qu=ax.quiver(x,y,np.sin(x),eta*np.sin(y),color=COLORS[0],angles='xy',scale_units='xy',scale=3.7,width=.0045)
        ax.quiverkey(qu,.75,1.07,1,r'$|\mathbf{u}|=1$',labelpos='E',coordinates='axes')
        axes_pi(ax,True); ax.set_title(rf'$\eta={eta:g}$',loc='left',pad=10)
    finish(fig,'a06-group-velocity-field','群速度场与等频线法向',
           '灰线为等能曲线，蓝箭头为u=(sin qx,eta sin qy)，长度按统一比例绘制而未逐点归一化。梯度垂直于等能曲线，并指向能量上升方向。eta=0.35时箭头的y分量减小。该群速度描述窄频谱波包的主导运动；局域翻转包含整个能带，不能用单一箭头概括。',dict(eta_values=[1,.35],vector_mesh=17,arrow_scale=3.7))


def slope_speed():
    q=np.linspace(-np.pi,np.pi,1001)
    fig,axes=plt.subplots(1,2,figsize=(12.8,8))
    heading(fig,'A07  色散的斜率决定运动方向与速度',
            r'沿 x 方向：$q_y=0$，$e=1-\cos q_x$，$u_x=de/dq_x=\sin q_x$',
            '正斜率对应向 +x 运动，负斜率对应向 −x 运动；最快的位置在 qx=±π/2，而能带顶点的速度为零。')
    axes[0].plot(q,energy(q,0),lw=3)
    for j,q0 in enumerate([-np.pi/2,0,np.pi/2]):
        e0=energy(q0,0); half=.56
        axes[0].plot([q0-half,q0+half],[e0-half*np.sin(q0),e0+half*np.sin(q0)],lw=2.6,color=COLORS[j+1])
        axes[0].scatter([q0],[e0],s=55,color=COLORS[j+1],zorder=4)
        axes[1].scatter([q0],[np.sin(q0)],s=55,color=COLORS[j+1],zorder=4)
    axes[0].set(ylabel=r'$e$',title='能量曲线与局部切线',ylim=(-.15,2.25))
    axes[1].plot(q,np.sin(q),lw=3); axes[1].axhline(0,color='#90A0A9',lw=1)
    axes[1].set(ylabel=r'$u_x$',title='同一波矢对应的群速度',ylim=(-1.17,1.17))
    for ax in axes: axes_pi(ax); ax.set_xlabel(r'$q_x$')
    finish(fig,'a07-slope-and-speed','色散斜率与群速度',
           '左侧三个彩色点及切线位于qx=-pi/2、0、pi/2；右侧对应点分别给出ux=-1、0、1。原点和布里渊区边界处斜率为零，能量最高并不意味着群速度最大。波包具有有限频谱宽度时，质心速度是其频谱加权平均，中心波矢处的速度是窄带近似。',dict(qy=0,marked_qx=[-np.pi/2,0,np.pi/2]))


def approximation():
    q=np.linspace(0,np.pi,1001)
    fig,axes=plt.subplots(1,2,figsize=(12.8,8))
    heading(fig,'A08  长波极限把余弦色散化为抛物线',
            r'$e\simeq(q_x^2+\eta q_y^2)/2$，前提是 $|q_x|,|q_y|\ll1$',
            '放大图展示小波矢区的一致；全区图显示二次近似高估能量。后续传播计算采用精确余弦色散。')
    for ax in axes:
        ax.plot(q,energy(q,0),lw=3,label=r'精确：$1-\cos q$')
        ax.plot(q,q*q/2,lw=3,ls='--',label=r'近似：$q^2/2$')
        ax.grid(alpha=.18); ax.set(xlabel=r'$q$（沿 x，$q_y=0$）',ylabel=r'$e$')
    axes[0].set(xlim=(0,.7),ylim=(0,.26),title='小波矢区放大'); axes[0].legend(loc='upper left')
    axes[1].set(xlim=(0,np.pi),ylim=(0,5.1),title='延伸至区边界后失效')
    axes[1].set_xticks([0,np.pi/2,np.pi],['0',r'$\pi/2$',r'$\pi$']); axes[1].legend(loc='upper left')
    finish(fig,'a08-long-wave-approximation','长波二次近似',
           '两图绘出同一函数的不同范围；左图q<=0.7，右图覆盖0至pi。由cos q=1-q²/2+O(q⁴)得到二次色散。近似只适合小波矢，不能把其无界抛物线及线性增长的群速度延伸到整个晶格能带。',dict(path='qy=0',zoom_qmax=.7,exact_range=[0,np.pi]))


def approximation_error():
    q=np.linspace(1e-3,np.pi,1600)
    rel=(q*q/2/(1-np.cos(q))-1)*100
    fig,ax=plt.subplots(figsize=(12.8,8))
    heading(fig,'A09  长波近似的适用范围可以定量检查',
            r'轴向相对误差 $\delta(q)=[(q^2/2)/(1-\cos q)-1]\times100\%$；$q=0$ 取连续极限 0',
            '1% 与 5% 仅为示例容差；误差是确定性截断误差，不是统计误差。二维波包还需要检查全部显著频谱分量。')
    ax.plot(q,rel,lw=3,color=COLORS[0]); ax.grid(alpha=.18)
    thresholds={}
    for limit,color in zip([1,5],[COLORS[2],COLORS[1]]):
        at=float(np.interp(limit,rel,q)); thresholds[str(limit)]=at
        ax.axhline(limit,color=color,ls='--',lw=1.8)
        ax.plot([at,at],[0,limit],color=color,ls=':',lw=2)
        ax.scatter([at],[limit],color=color,zorder=4)
        ax.annotate(rf'{limit}%：$q\approx{at:.3f}$',xy=(at,limit),xytext=(at+.3,limit+8),
                    arrowprops=dict(arrowstyle='->',color=color),color=color,fontsize=15)
    ax.set(xlim=(0,np.pi),ylim=(0,155),xlabel=r'$q$（沿 x，$q_y=0$）',ylabel=r'能量相对误差 $\delta$（%）')
    ax.set_xticks([0,np.pi/2,np.pi],['0',r'$\pi/2$',r'$\pi$'])
    inset=ax.inset_axes([.08,.49,.43,.43]); inset.plot(q,rel,lw=2.4)
    inset.set(xlim=(0,1),ylim=(0,9),xlabel=r'$q$',ylabel='误差（%）',title='小误差区放大')
    inset.grid(alpha=.18)
    for limit,color in zip([1,5],[COLORS[2],COLORS[1]]): inset.axhline(limit,color=color,ls='--',lw=1.3)
    DATA['approx_q']=q; DATA['approx_relative_error_percent']=rel
    finish(fig,'a09-long-wave-error','长波近似的定量误差',
           f'纵轴是轴向能量的相对高估量；曲线在q=0取连续极限0，插图放大小误差区。1%与5%的示例门槛分别对应q约{thresholds["1"]:.3f}和{thresholds["5"]:.3f}。门槛仅刻画该轴向能量近似，不等同于波包传播保真度；相位误差还会随时间累积。',dict(tolerance_q=thresholds,sample_points=1600))


def direction():
    q0=np.array([.35*np.pi,.15*np.pi])
    fig,axes=plt.subplots(1,2,figsize=(12.8,8))
    heading(fig,'A10  波矢方向与群速度方向一般不同',
            r'同一波矢 $\mathbf{q}_0=(0.35\pi,0.15\pi)$；箭头均已单位化，仅比较方向',
            '即使 Jx=Jy，有限波矢下晶格色散也不具连续旋转对称性；各向异性会进一步改变传播方向。')
    for ax,eta in zip(axes,[1,.35]):
        u=np.array([np.sin(q0[0]),eta*np.sin(q0[1])])
        qn=q0/np.linalg.norm(q0); un=u/np.linalg.norm(u)
        for vec,color,ls,label in [(qn,COLORS[1],'--',r'$\hat{\mathbf{q}}_0$'),(un,COLORS[0],'-',r'$\hat{\mathbf{v}}_g$')]:
            ax.annotate('',xy=vec,xytext=(0,0),arrowprops=dict(arrowstyle='-|>',lw=3,color=color,linestyle=ls,mutation_scale=22))
            ax.text(vec[0]+.025,vec[1]+(.065 if ls=='-' else -.085),label,color=color,fontsize=19)
        tq=np.degrees(np.arctan2(q0[1],q0[0])); tu=np.degrees(np.arctan2(u[1],u[0]))
        ax.text(.05,.86,rf'$\theta_q={tq:.1f}^\circ$'+'\n'+rf'$\theta_v={tu:.1f}^\circ$',transform=ax.transAxes,fontsize=17,va='top')
        ax.set(xlim=(-.06,1.24),ylim=(-.1,1),aspect='equal',xlabel='x 方向',ylabel='y 方向',title=rf'$\eta={eta:g}$')
        ax.set_xticks([0,.5,1]); ax.set_yticks([0,.5,1]); ax.grid(alpha=.16)
    finish(fig,'a10-wavevector-velocity-direction','波矢与群速度的方向差',
           '橙色虚线箭头指波矢方向，蓝色实线箭头指群速度方向；两者都单位化，箭长不表示速度大小。选择q0=(0.35pi,0.15pi)，eta=1时仍有有限角差，反映方格晶格而非连续各向同性介质的色散；eta=0.35时y向速度降低，传播更偏向x。eta=1的长波极限下二者趋于平行；eta不等于1时，即使长波区u约为(qx,eta*qy)，一般仍不平行。坐标轴等特殊方向需单独判断。',dict(q0=q0,eta_values=[1,.35],normalized_arrows=True))


def curvature():
    q=np.linspace(-np.pi,np.pi,1001)
    fig,axes=plt.subplots(1,2,figsize=(12.8,8))
    heading(fig,'A11  曲率刻画邻近频谱分量的速度差',
            r'$\partial_{q_x}^2 e=\cos q_x$，$\partial_{q_y}^2 e=\eta\cos q_y$；混合二阶导数为零',
            '在 qx=qy=π/2 两个二阶项同时消失；三阶导数仍非零。这个特殊点为后续抑制展宽提供线索。')
    axes[0].plot(q,np.cos(q),lw=3,label=r'$\partial_{q_x}^2e$')
    axes[0].plot(q,.35*np.cos(q),lw=3,ls='--',label=r'$\partial_{q_y}^2e$，$\eta=0.35$')
    axes[0].axhline(0,color='#8B9AA4',lw=1)
    for s in [-1,1]: axes[0].axvline(s*np.pi/2,color='#9BA7AF',ls=':',lw=1.5)
    axes_pi(axes[0]); axes[0].set(xlabel=r'对应方向的 $q$',ylabel='二阶导数',ylim=(-1.15,1.15),title='曲率随波矢变号')
    axes[0].legend(loc='lower center')
    dq=np.linspace(-.65,.65,501); exact=energy(np.pi/2+dq,0); linear=1+dq
    axes[1].plot(dq,exact-linear,lw=3,label='精确色散 − 切线')
    axes[1].plot(dq,-dq**3/6,lw=2.4,ls='--',label=r'首项：$-\delta q^3/6$')
    axes[1].axhline(0,color='#8B9AA4',lw=1); axes[1].grid(alpha=.18)
    axes[1].set(xlabel=r'$\delta q_x=q_x-\pi/2$',ylabel=r'$e-(1+\delta q_x)$',title='二阶项消失后，三阶项保留')
    axes[1].legend(loc='upper right')
    finish(fig,'a11-curvature-and-cubic','色散曲率与三阶残差',
           '左图分别画cos q与0.35 cos q，标出q=±pi/2处零曲率。右图在qx=pi/2、qy=0附近减去一阶切线，所得残差接近-delta qx³/6。二维点(pi/2,pi/2)的两个二阶系数都为零，但三阶仍在；本图只建立机制线索，不证明有限宽度波包严格无色散。',dict(eta_values=[1,.35],residual_q0=[np.pi/2,0],residual_range=[-.65,.65]),role='bridge')


def scales():
    eta=np.linspace(0,1.5,301)
    fig,axes=plt.subplots(1,2,figsize=(12.8,8))
    heading(fig,'A12  交换比同时控制能带宽度与速度上限',
            r'固定 $J_x>0$，扫描 $\eta=J_y/J_x$；以下为精确能带性质',
            '分量速度上限不等于局域激发具有严格截断的传播边界；量子振幅在主要传播前沿之外仍可有小尾部。')
    axes[0].plot(eta,2*(1+eta),lw=3,label=r'$e_{\max}=2(1+\eta)$')
    axes[0].set(xlabel=r'$\eta$',ylabel=r'带宽 $\Delta\varepsilon/J_x$',title='能带宽度随交换比增大')
    axes[0].legend(loc='upper left')
    axes[1].plot(eta,np.ones_like(eta),lw=3,label=r'$\max|u_x|=1$')
    axes[1].plot(eta,eta,lw=3,ls='--',label=r'$\max|u_y|=\eta$')
    axes[1].plot(eta,np.sqrt(1+eta**2),lw=2.5,ls=':',label=r'$\max|\mathbf{u}|=\sqrt{1+\eta^2}$')
    axes[1].set(xlabel=r'$\eta$',ylabel='无量纲群速度上限',title='两个方向的速度尺度可分别调节')
    axes[1].legend(loc='lower right')
    for ax in axes: ax.set_xlim(0,1.5); ax.set_ylim(bottom=0); ax.grid(alpha=.18); ax.axvline(1,color='#9BA7AF',ls=':',lw=1)
    DATA['eta_scan']=eta; DATA['bandwidth_scan']=2*(1+eta)
    finish(fig,'a12-exchange-and-scales','交换比与能量和速度尺度',
           '左图的带宽为2(1+eta)，右图分别是x、y分量和速度模的全布里渊区最大值。eta=1是空间交换各向同性，eta=0对应互不耦合的x向链并带来qy简并。所有上限是精确群速度界，不把它们误读为概率分布的严格有限支撑边界。',dict(eta_range=[0,1.5],sample_points=301))


def checks():
    rng=np.random.default_rng(61751)
    x,y=rng.uniform(-np.pi,np.pi,(2,1000)); eta=.35
    h=1e-5; hh=1e-4
    exact=1-np.cos(x)+eta*(1-np.cos(y))
    vx=(energy(x+h,y,eta)-energy(x-h,y,eta))/(2*h)
    vy=(energy(x,y+h,eta)-energy(x,y-h,eta))/(2*h)
    dxx=(energy(x+hh,y,eta)-2*energy(x,y,eta)+energy(x-hh,y,eta))/hh**2
    dyy=(energy(x,y+hh,eta)-2*energy(x,y,eta)+energy(x,y-hh,eta))/hh**2
    mixed=(energy(x+hh,y+hh,eta)-energy(x+hh,y-hh,eta)-energy(x-hh,y+hh,eta)+energy(x-hh,y-hh,eta))/(4*hh**2)
    q=np.linspace(-np.pi,np.pi,401); gx,gy=np.meshgrid(q,q)
    band=energy(gx,gy,eta)
    result=dict(model_formula_max_abs_error=float(np.max(abs(energy(x,y,eta)-exact))),
                inversion_symmetry_max_abs_error=float(np.max(abs(energy(x,y,eta)-energy(-x,-y,eta)))),
                gradient_x_max_abs_error=float(np.max(abs(vx-np.sin(x)))),
                gradient_y_max_abs_error=float(np.max(abs(vy-eta*np.sin(y)))),
                curvature_x_max_abs_error=float(np.max(abs(dxx-np.cos(x)))),
                curvature_y_max_abs_error=float(np.max(abs(dyy-eta*np.cos(y)))),
                mixed_curvature_max_abs_error=float(np.max(abs(mixed))),
                band_min=float(band.min()),band_max=float(band.max()),
                band_max_expected=2*(1+eta),
                zero_curvature_point=[np.pi/2,np.pi/2],
                zero_curvature_values=[float(np.cos(np.pi/2)),float(eta*np.cos(np.pi/2))],
                cubic_values_at_zero_curvature=[-1.,-eta],
                finite_difference_step_gradient=h,finite_difference_step_curvature=hh,
                random_seed=61751,samples=1000,eta=eta,
                versions=dict(python=platform.python_version(),numpy=np.__version__,matplotlib=matplotlib.__version__))
    assert result['model_formula_max_abs_error'] < 1e-14
    assert max(result['gradient_x_max_abs_error'],result['gradient_y_max_abs_error']) < 1e-8
    assert max(result['curvature_x_max_abs_error'],result['curvature_y_max_abs_error'],result['mixed_curvature_max_abs_error']) < 2e-7
    assert abs(result['band_max']-2*(1+eta))<1e-13 and result['band_min']==0
    exports=[]
    for item in ENTRIES:
        with Image.open(ROOT/item['files']['png']) as im:
            im.load()
            size=list(im.size)
            assert size == [2176,1360]
        ET.parse(ROOT/item['files']['svg'])
        with pymupdf.open(ROOT/item['files']['pdf']) as pdf:
            assert len(pdf)==1
            page_size=[float(pdf[0].rect.width),float(pdf[0].rect.height)]
            assert abs(page_size[0]-921.6)<.01 and abs(page_size[1]-576)<.01
        exports.append(dict(id=item['id'],png_size=size,svg_parsed=True,pdf_pages=1,pdf_points=page_size))
    result['exports']=exports
    result['figure_count']=len(ENTRIES)
    result['passed']=True
    write_json(ROOT/'checks_a.json',result)


def main():
    lattice()
    surface(1.,'a02-isotropic-surface','A02  各向同性交换的色散曲面')
    surface(.35,'a03-anisotropic-surface','A03  各向异性交换改变曲面起伏')
    cuts(); contours(); velocity_field(); slope_speed(); approximation()
    approximation_error(); direction(); curvature(); scales(); checks()
    data_dir=ROOT/GROUP/'data'; data_dir.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(data_dir/'dispersion_arrays.npz',**DATA)
    write_json(ROOT/'manifest_a.json',dict(group_title='A 色散关系与基本传播原理',items=ENTRIES))
    print(f'Generated {len(ENTRIES)} figures in {ROOT/GROUP}; checks passed.')


if __name__ == '__main__':
    main()
