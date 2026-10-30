"""Generate C-group midterm figures from exact one-magnon Fourier evolution.

Run with: python figures/midterm-report/generate_gaussian.py
All lengths are in a, time is tau=Jx*t/hbar, and q=ka.  Sigma denotes the
probability RMS width, not the width parameter of the amplitude squared again.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from common import (ROOT, COLORS, INK, gaussian, grid, energy, propagate,
    spectral_stats, moments, trajectory, heading as shared_heading, save_figure, save_animation,
    write_json)

GROUP = 'c-gaussian'
OUT = ROOT / GROUP
OUT.mkdir(parents=True, exist_ok=True)
N = 256
TIMES = np.linspace(0, 60, 31)
SNAPS = (0., 30., 60.)
X, XX, YY, QX, QY = grid(N)
QS = np.fft.fftshift(2*np.pi*np.fft.fftfreq(N))
manifest = []
cases = {}
data = {'x': X, 'q': QS, 'times': TIMES}

def heading(fig, title, subtitle='', footer=''):
    shared_heading(fig, title, subtitle, footer)
    # Reserve a separate band for explanatory footers below the axis labels.
    fig.subplots_adjust(bottom=.215)

def case(name, sigma=4., q0=(.7, 0.), eta=1.):
    if name not in cases:
        psi0 = gaussian(N, sigma, q0)
        stats = spectral_stats(psi0, eta)
        track = trajectory(psi0, TIMES, eta)
        c = dict(name=name, sigma=sigma, q0=q0, eta=eta,
                 psi0=psi0, stats=stats, track=track)
        cases[name] = c
        data[name+'_initial_spectral_power'] = np.fft.fftshift(stats['power']).astype('float32')
        for k, v in track.items(): data[name+'_'+k] = v
        for t in SNAPS:
            data[name+f'_P_tau{int(t):02}'] = np.abs(propagate(psi0, t, eta)).astype('float64')**2
    return cases[name]

def probability(c, t):
    return np.abs(propagate(c['psi0'], t, c['eta']))**2

def params(*cs, **extra):
    return dict(N=N, boundary='periodic; verified against N=384',
        tau_max=60, S=.5, h=0.,
        units=dict(position='a', time='hbar/Jx', momentum='1/a'),
        gaussian_convention='psi0 ~ exp[-x^2/(4 sigma^2)-y^2/(4 sigma^2)] exp(i q0.r); sum |psi|^2=1',
        cases=[{k:c[k] for k in ('name','sigma','q0','eta')} for c in cs], **extra)

def finish(fig, ident, title, caption, cs=(), role='core', **extra):
    manifest.append(save_figure(fig, GROUP, ident, title, caption, params(*cs, **extra), role))
    print(ident, flush=True)

def annotate(ax, text):
    ax.text(.04,.96,text,transform=ax.transAxes,va='top',fontsize=11,
            bbox=dict(facecolor='white', alpha=.88, edgecolor='none',pad=3))

def density(ax, c, t, limits=(-25,75,-25,75), vmax=None, title=''):
    if vmax is None: vmax=float(np.max(np.abs(c['psi0'])**2))
    im=ax.imshow(probability(c,t), origin='lower', extent=(X[0]-.5,X[-1]+.5,X[0]-.5,X[-1]+.5),
                 cmap='magma', vmin=0, vmax=vmax, interpolation='nearest')
    ax.set(xlim=limits[:2], ylim=limits[2:], xlabel=r'$x/a$', ylabel=r'$y/a$', title=title)
    return im

def maps_figure(cs, ts, title, subtitle, limits, footer):
    fig, axs=plt.subplots(1,len(cs),figsize=(14,5.6),squeeze=False)
    heading(fig,title,subtitle,footer)
    fig.subplots_adjust(left=.06,right=.88,bottom=.2,top=.75,wspace=.28)
    vmax=max(float(np.max(np.abs(c['psi0'])**2)) for c in cs)
    for ax,c,t in zip(axs[0],cs,ts):
        im=density(ax,c,t,limits,vmax,rf'$\tau={t:g}$')
    cb=fig.colorbar(im,cax=fig.add_axes([.91,.23,.015,.49]))
    cb.set_label(r'$P_{n_x,n_y}=|\psi_{n_x,n_y}|^2$')
    return fig,axs[0]

zero=case('qzero',q0=(0.,0.))
right=case('qright')
left=case('qleft',q0=(-.7,0.))
diagonal=case('qdiagonal',q0=(.7,.7))
anisotropic=case('qdiagonal_eta03',q0=(.7,.7),eta=.3)
widecases=[case(f'sigma{s}',sigma=float(s)) for s in (3,6,10)]

# 01: A carrier changes phase and spectrum while leaving initial probability intact.
fig,axs=plt.subplots(1,3,figsize=(14,5.6))
heading(fig,'C01  同一个包络，可以有不同的传播方向',
        r'初态 $\psi\propto e^{-(x^2+y^2)/(4\sigma^2)}e^{iq_{0x}x}$；$\sigma=4$，$\eta=1$',
        '概率只含振幅的模；载波信息保留在相位和频谱中。两种初态均归一化为 1。')
for j,c in enumerate((zero,right)):
    lab=rf'$q_{{0x}}={c["q0"][0]:g}$'
    axs[0].plot(X,(np.abs(c['psi0'])**2).sum(axis=0),
                lw=3 if j==0 else 2,ls='-' if j==0 else '--',label=lab)
    sel=abs(X)<=10
    axs[1].plot(X[sel],c['q0'][0]*X[sel],lw=2,label=lab)
    axs[2].plot(QS,np.fft.fftshift(c['stats']['power'].sum(axis=0)),lw=2,label=lab)
axs[0].set(xlim=(-15,15),xlabel=r'$x/a$',ylabel=r'$P_x=\sum_y|\psi|^2$',title='初始概率完全重合')
axs[1].set(xlabel=r'$x/a$',ylabel='展开后的相位 / rad',title='相位随位置的斜率不同')
axs[2].set(xlim=(-.6,1.3),xlabel=r'$q_x=k_xa$',ylabel='每个离散波矢的边际概率',title='频谱中心随载波平移')
for ax in axs: ax.legend(); ax.grid(alpha=.2)
finish(fig,'c01-carrier-envelope-spectrum','载波、包络与频谱',
    '两种归一化Gaussian初态只有载波不同：q0=(0,0)和(0.7,0)，sigma=4。左图的x边际概率严格相同；中图画中心区域连续展开的载波相位q0x*x，省略低振幅尾部；右图为单位正交FFT所得离散频谱的x边际概率，所有波矢的总概率为1。载波改变频谱中心及后续传播，但不改变初始概率包络。', (zero,right))

# 02: Width-bandwidth relation and the explicitly defined RMS convention.
fig,axs=plt.subplots(1,2,figsize=(12.5,5.5))
heading(fig,'C02  空间越宽，参与叠加的波矢越集中',
        r'统一载波 $\mathbf{q}_0=(0.7,0)$；各初态的总概率均为 1',
        r'宽度定义：$\Delta x=\sigma$；宽包络近似下 $\Delta q_x\simeq1/(2\sigma)$，所以 $\Delta x\Delta q_x\simeq1/2$。')
for c in widecases:
    label=rf'$\sigma={c["sigma"]:g},\ \Delta q_x\approx{1/(2*c["sigma"]):.3f}$'
    axs[0].plot(X,(np.abs(c['psi0'])**2).sum(axis=0),lw=2,label=label)
    axs[1].plot(QS,np.fft.fftshift(c['stats']['power'].sum(axis=0)),lw=2,label=label)
axs[0].set(xlim=(-35,35),xlabel=r'$x/a$',ylabel=r'$P_x(0)$',title='初始空间分布')
axs[1].set(xlim=(0,1.4),xlabel=r'$q_x$',ylabel='每个离散波矢的边际概率',title='初始波矢分布')
for ax in axs: ax.legend();ax.grid(alpha=.2)
finish(fig,'c02-space-bandwidth','空间宽度与频谱宽度',
    '比较sigma=3、6、10的无啁啾Gaussian初态，q0=(0.7,0)。sigma是概率分布的RMS宽度；不是振幅指数中再平方后的宽度。所有初态总概率为1，所以窄初态的空间峰值更高，而宽初态的频谱更窄。本图横轴和纵轴在各参数曲线之间统一。Delta q=1/(2 sigma)是宽包络、频谱远离Brillouin区接缝时的连续Gaussian表达式。',( *widecases,))

# 03/04: Fixed-scale density snapshots, zero and nonzero carriers.
for ident,c,title,limits in (
 ('c03-zero-carrier-spreading',zero,'C03  零中心波矢：质心停留，概率向外展开',(-25,25,-25,25)),
 ('c04-moving-gaussian',right,'C04  非零中心波矢：向右移动，同时逐渐展宽',(-20,65,-30,30))):
    fig,axs=maps_figure([c]*3,SNAPS,title,
        rf'$\mathbf{{q}}_0=({c["q0"][0]:g},0)$，$\sigma=4$；三个时刻使用同一线性色标',
        limits,'虚线交点为实际概率质心；不对各时刻峰值重新归一化。')
    for ax,t in zip(axs,SNAPS):
        m=moments(propagate(c['psi0'],t,c['eta']))
        ax.axvline(m['cx'],color='cyan',ls='--',lw=1);ax.axhline(m['cy'],color='cyan',ls='--',lw=1)
        annotate(ax,rf'$\sigma_x={m["wx"]:.2f}$'+'\n'+rf'$\sigma_y={m["wy"]:.2f}$')
    finish(fig,ident,title[5:],
        f'精确余弦色散下，sigma=4、q0={c["q0"]}的归一化Gaussian在tau=0、30、60的二维格点概率。三个面板采用相同位置坐标范围和固定线性色标。青色虚线标记由概率分布直接计算的质心，标注给出概率RMS宽度。'+
        ('谱分布关于零波矢对称，因此两个方向的平均群速度都为0，质心停留在原点；不同非零波矢成分仍会向外传播并引起展宽。' if c is zero else '频谱中心向正qx偏移，带来正x方向平均群速度；有限频宽仍使各成分群速度不同，所以包络一边移动一边展宽。y方向中心波矢为0，平均位移为0，但仍会展宽。'),(c,))

# 05: Changing the carrier reverses or redirects motion.
fig,axs=maps_figure([left,right,diagonal],[60]*3,'C05  改变载波：反向传播与斜向传播',
    r'$\sigma=4$，$\eta=1$，$\tau=60$；三个初态的概率包络相同',
    (-65,65,-25,65),'白色箭头：从初始原点指向最终概率质心；所有面板采用同一固定色标。')
for ax,c in zip(axs,(left,right,diagonal)):
    v=c['stats']['velocity'];ax.annotate('',xy=60*v,xytext=(0,0),arrowprops=dict(arrowstyle='->',color='white',lw=2))
    ax.set_title(rf'$\mathbf{{q}}_0=({c["q0"][0]:g},{c["q0"][1]:g})$')
finish(fig,'c05-carrier-directions','由载波控制传播方向',
    '保持sigma=4和初始概率包络相同，只将载波改成(-0.7,0)、(0.7,0)、(0.7,0.7)。在tau=60时分别得到左行、右行和斜向传播。白箭头由原点指向谱平均速度乘以时间得到的质心预测。对当前等宽、各向同性交换且两个非零波矢分量相同的例子，斜向群速度方向与载波方向一致；这一一致性并非任意色散或各向异性情形下的普遍规律。',(left,right,diagonal))

# 06: Exact mean velocity, with narrowband approximation clearly distinguished.
fig,axs=plt.subplots(1,2,figsize=(13,5.7))
heading(fig,'C06  质心沿直线移动：速度由整个频谱平均得到',
    r'$\langle n_\mu(\tau)\rangle=\langle n_\mu(0)\rangle+\tau\langle v_\mu\rangle$；$\mathbf{v}=(\sin q_x,\eta\sin q_y)$',
    '圆点：数值演化；实线：谱平均速度（精确矩关系）；虚线：中心波矢处群速度（窄谱近似）。')
for j,c in enumerate((zero,right,left,diagonal)):
    lab=rf'$\mathbf{{q}}_0=({c["q0"][0]:g},{c["q0"][1]:g})$'
    for ax,axis,key in zip(axs,(0,1),('cx','cy')):
        t=c['track']['t']; vv=c['stats']['velocity'][axis]
        center=np.sin(c['q0'][axis])*(1 if axis==0 else c['eta'])
        ax.plot(t,t*vv,color=COLORS[j],lw=2,label=lab)
        ax.plot(t[::3],c['track'][key][::3],color=COLORS[j],marker='o',mfc='white',ls='none',ms=4)
        ax.plot(t,t*center,color=COLORS[j],lw=1.3,ls='--',alpha=.8)
axs[0].text(.03,.04,rf'$\sigma=4:\quad\langle v_x\rangle={right["stats"]["velocity"][0]:.6f},\quad \sin(0.7)={np.sin(.7):.6f}$',
    transform=axs[0].transAxes,fontsize=11)
for ax,label in zip(axs,(r'$\langle x/a\rangle$',r'$\langle y/a\rangle$')):
    ax.set(xlabel=r'$\tau$',ylabel=label);ax.grid(alpha=.2);ax.legend(loc='upper left',fontsize=10)
finish(fig,'c06-centroid-velocity','质心运动与谱平均速度',
    '四种载波的概率质心由精确FFT演化计算。圆点为数值结果，实线用初态全频谱的<sin qx>和eta<sin qy>预测，虚线用中心波矢处的(sin q0x,eta sin q0y)近似。对于sigma=4，有限频宽使两者存在虽小但真实的差异，不能把中心值近似称为精确质心速度。当前无边界污染的平移不变模型中，位置期望按谱平均速度作直线运动。',(zero,right,left,diagonal))

# 07: Comoving marginals expose spreading separately from translation.
fig,axs=plt.subplots(1,2,figsize=(12.5,5.6))
heading(fig,'C07  跟着质心观察，展宽就能单独看清',
    r'$\mathbf{q}_0=(0.7,0)$，$\sigma=4$；横轴减去各时刻的实际质心',
    '每条边际分布的总概率均为 1；曲线峰值降低伴随宽度增加。')
for j,t in enumerate((0,20,40,60)):
    p=probability(right,t);m=moments(propagate(right['psi0'],t))
    for ax,key,marg in zip(axs,('cx','cy'),(p.sum(axis=0),p.sum(axis=1))):
        ax.plot(X-m[key],marg,lw=2,color=COLORS[j],label=rf'$\tau={t}$')
for ax,axis in zip(axs,('x','y')):
    ax.set(xlim=(-25,25),ylim=(0,.105),xlabel=rf'$({axis}-\langle {axis}\rangle)/a$',ylabel=rf'$P_{axis}$',
           title='沿移动方向的边际概率' if axis=='x' else '横向边际概率')
    ax.legend();ax.grid(alpha=.2)
finish(fig,'c07-comoving-marginals','共动坐标下的包络展宽',
    '对q0=(0.7,0)、sigma=4的同一个波包，画tau=0、20、40、60的x和y边际概率。仅在横轴减去数值质心，没有重新归一化峰值或宽度。曲线使用实际格点概率并连线。x、y方向的色散曲率不同，因而展宽程度不同；质心的直线移动与包络的形状变化是可以分别测量的两件事。',(right,))

# 08: Equal normalization does not mean equal physical initial size.
fig,axs=plt.subplots(1,2,figsize=(12.5,5.6))
heading(fig,'C08  同一传播时间下，初始宽度怎样影响展宽',
    r'$\mathbf{q}_0=(0.7,0)$，$\eta=1$，$\tau=60$；$\sigma=3,6,10$',
    '左图比较实际概率；右图用初始宽度作单位。不同初始宽度是物理输入，不能当作同尺寸方案比较。')
for j,c in enumerate(widecases):
    p=probability(c,60);m=moments(propagate(c['psi0'],60));s=c['sigma']
    lab=rf'$\sigma={s:g},\ \sigma_x(60)/\sigma={m["wx"]/s:.2f}$'
    axs[0].plot(X-m['cx'],p.sum(axis=0),lw=2,label=lab)
    axs[1].plot((X-m['cx'])/s,s*p.sum(axis=0),lw=2,label=lab)
axs[0].set(xlim=(-35,35),xlabel=r'$(x-\langle x\rangle)/a$',ylabel=r'$P_x(60)$',title='同一位置单位、同一总概率')
axs[1].set(xlim=(-8,8),xlabel=r'$(x-\langle x\rangle)/(a\sigma)$',ylabel=r'$\sigma P_x(60)$',title='比较相对初始宽度的形变')
for ax in axs: ax.grid(alpha=.2);ax.legend(fontsize=10)
finish(fig,'c08-width-comparison','不同初始宽度的传播对照',
    'sigma=3、6、10的Gaussian都以q0=(0.7,0)传播至tau=60，各自归一化总概率为1。左图画共动坐标下真实x边际概率；右图明确采用u=(x-<x>)/sigma、纵轴sigma*Px，以比较相对初始宽度的变化，保持分布面积一致。宽初态频谱更窄，因此相对展宽较小，但需要更大的初始空间范围。本图不把不同初始尺寸的波包解释成相同制备资源下的性能排名。',widecases)

# 09: Independent exact moment law for unchirped Gaussian packets.
fig,axs=plt.subplots(1,2,figsize=(12.5,5.6))
heading(fig,'C09  展宽的定量检验：速度方差决定宽度增长',
    r'无初始啁啾：$\sigma_\mu^2(\tau)=\sigma_\mu^2(0)+\tau^2\operatorname{Var}(v_\mu)$',
    '实线：由初始频谱计算的矩关系；圆点：实际演化概率的 RMS 宽度。这里不作二阶色散截断。')
for j,c in enumerate((zero,right,diagonal)):
    for ax,axis,key in zip(axs,(0,1),('wx','wy')):
        initial=c['track'][key][0];theory=np.sqrt(initial**2+TIMES**2*c['stats']['velocity_variance'][axis])
        lab=rf'$\mathbf{{q}}_0=({c["q0"][0]:g},{c["q0"][1]:g})$'
        ax.plot(TIMES,theory,color=COLORS[j],lw=2,label=lab)
        ax.plot(TIMES[::3],c['track'][key][::3],color=COLORS[j],marker='o',mfc='white',ls='none',ms=4)
for ax,axis in zip(axs,('x','y')):
    ax.set(xlabel=r'$\tau$',ylabel=rf'$\sigma_{axis}(\tau)/a$',ylim=(3.7,9));ax.legend(fontsize=10);ax.grid(alpha=.2)
finish(fig,'c09-rms-exact-moments','概率宽度与精确速度方差',
    '对于初始实Gaussian包络乘线性载波，初始位置与速度的对称协方差为零，因此无限晶格上Var(n_mu(tau))=Var(n_mu(0))+tau^2 Var(v_mu)精确成立。一般有啁啾的初态还会有2*tau*Cov_sym(n_mu,v_mu)项，不能直接套用本图公式。图中实线完全由初态离散频谱平均计算，圆点来自精确余弦色散演化；有限周期盒在tau<=60内已检查边缘概率与扩大网格误差。',(zero,right,diagonal))

# 10: Anisotropy bends the velocity away from the wavevector.
fig,axs=maps_figure([diagonal,anisotropic],[60,60],'C10  各向异性使传播方向偏离波矢方向',
    r'相同初态：$\mathbf{q}_0=(0.7,0.7)$，$\sigma=4$；相同时间 $\tau=60$',
    (-12,60,-12,60),'青色虚箭头仅表示波矢方向；白色实箭头从原点指向最终概率质心。')
for ax,c in zip(axs,(diagonal,anisotropic)):
    ax.set_title(rf'$\eta=J_y/J_x={c["eta"]:g}$')
    ax.annotate('',xy=(30,30),xytext=(0,0),arrowprops=dict(arrowstyle='->',color='cyan',lw=2,linestyle='--'))
    v=c['stats']['velocity'];ax.annotate('',xy=60*v,xytext=(0,0),arrowprops=dict(arrowstyle='->',color='white',lw=2))
    annotate(ax,rf'$\theta_q=45^\circ$'+'\n'+rf'$\theta_v={np.degrees(np.arctan2(v[1],v[0])):.1f}^\circ$')
finish(fig,'c10-anisotropy-direction','各向异性下波矢与传播方向',
    '固定q0=(0.7,0.7)、sigma=4和tau=60，仅改变eta=Jy/Jx为1或0.3。青色虚箭头示意波矢方向，长度不代表物理速度；白色箭头表示实际质心位移。两个初态的波矢方向同为45度，谱平均群速度方向分别约为45度和16.7度。由于vy=eta sin qy，较弱的y方向交换降低了y方向传播速率。所有概率图用同一固定线性色标。',(diagonal,anisotropic))

# 11: Anisotropy changes two widths separately.
fig,axs=plt.subplots(1,2,figsize=(12.5,5.6))
heading(fig,'C11  各向异性也改变波包形状',
    r'$\mathbf{q}_0=(0.7,0.7)$，$\sigma_x(0)=\sigma_y(0)=4$；比较 $\eta=1$ 与 $0.3$',
    r'$v_y=\eta\sin q_y$，所以同一初态下 $\operatorname{Var}(v_y)\propto\eta^2$。')
for j,c in enumerate((diagonal,anisotropic)):
    axs[0].plot(TIMES,c['track']['wx'],lw=2,color=COLORS[j],ls='-',label=rf'$\eta={c["eta"]:g}:\sigma_x$')
    axs[0].plot(TIMES,c['track']['wy'],lw=2,color=COLORS[j],ls='--',label=rf'$\eta={c["eta"]:g}:\sigma_y$')
    axs[1].plot(TIMES,c['track']['wx']/c['track']['wy'],lw=2,color=COLORS[j],label=rf'$\eta={c["eta"]:g}$')
axs[0].set(xlabel=r'$\tau$',ylabel='概率 RMS 宽度 / a',title='分别测量两个方向的宽度')
axs[1].set(xlabel=r'$\tau$',ylabel=r'$\sigma_x/\sigma_y$',title='从圆形包络到椭圆形包络')
for ax in axs:ax.legend();ax.grid(alpha=.2)
finish(fig,'c11-anisotropy-width','各向异性与二维宽度',
    '相同圆对称Gaussian包络在eta=1和eta=0.3下的x、y概率RMS宽度。由于qx=qy=0.7且初始频宽相同，eta=1时两个方向的宽度曲线重合；eta=0.3保留相同x方向演化，但减小y方向的速度方差，导致宽度比sigma_x/sigma_y增大。这里的圆形和椭圆形描述包络尺度，不意味着离散晶格具有连续旋转对称性。',(diagonal,anisotropic))

# 12: Spectral power is conserved, while phase shears the packet.
fig,axs=plt.subplots(1,2,figsize=(12.5,5.6))
heading(fig,'C12  波包变形来自相位积累，频谱概率保持不变',
    r'$A(\mathbf{q},\tau)=A(\mathbf{q},0)e^{-ie(\mathbf{q})\tau}$，$e=\varepsilon/J_x$；均匀、无耗散、线性模型',
    '右图去除了整体相位与中心群速度产生的线性相位，剩余相位反映色散引起的形变。')
for j,t in enumerate((0,30,60)):
    psi=propagate(right['psi0'],t)
    power=np.abs(np.fft.fft2(psi,norm='ortho'))**2
    axs[0].plot(QS,np.fft.fftshift(power.sum(axis=0)),lw=3-j*.5,ls=('-', '--', ':')[j],label=rf'$\tau={t}$')
    qq=np.linspace(.25,1.15,400)
    residual=-t*(energy(qq,0)-energy(.7,0)-np.sin(.7)*(qq-.7))
    axs[1].plot(qq,residual,lw=2,label=rf'$\tau={t}$')
axs[0].set(xlim=(.2,1.2),xlabel=r'$q_x$',ylabel='每个离散波矢的边际概率',title='频谱概率：三个时刻完全重合')
axs[1].set(xlabel=r'$q_x$（截面 $q_y=0$）',ylabel='去除常数项和线性项后的相位 / rad',title='非线性相位随时间积累')
for ax in axs:ax.legend();ax.grid(alpha=.2)
finish(fig,'c12-spectrum-phase','频谱功率守恒与相位积累',
    '左图从tau=0、30、60的实际演化波函数重新做单位正交FFT，显示频谱概率逐点不变。这里e=epsilon/Jx为无量纲能量，tau=Jx*t/hbar。右图在qy=0截面画精确传播因子的残余相位-tau[e(qx,0)-e(0.7,0)-sin(0.7)(qx-0.7)]，相位连续展开而不是模2pi显示；去掉的是整体相位和中心群速度平移对应的线性相位。频谱概率不变并不保证实空间形状不变，因为不同模式的相对相位仍会变化。',(right,))

# 13/14: Limited extension, explicitly separated from the basic midterm story.
ordinary=case('extension_ordinary',sigma=3.,q0=(.7,.7))
inflection=case('extension_inflection',sigma=3.,q0=(np.pi/2,np.pi/2))
sharp=case('extension_inflection_sigma2',sigma=2.,q0=(np.pi/2,np.pi/2))
fig,axs=plt.subplots(1,2,figsize=(12.5,5.6))
heading(fig,'C13  拓展：二阶曲率消失，可以减慢有限时间内的展宽',
    r'相同初始宽度 $\sigma=3$；比较 $\mathbf{q}_0=(0.7,0.7)$ 与 $(\pi/2,\pi/2)$',
    r'在 $q_0=\pi/2$ 处 $\varepsilon^{\prime\prime}=0$，但 $\varepsilon^{\prime\prime\prime}\neq0$；更高阶色散仍然存在。')
for j,c in enumerate((ordinary,inflection)):
    lab=r'$\mathbf{q}_0=(0.7,0.7)$' if j==0 else r'$\mathbf{q}_0=(\pi/2,\pi/2)$'
    axs[0].plot(TIMES,c['track']['wx'],lw=2,label=lab)
    axs[1].plot(TIMES,c['track']['fidelity'],lw=2,label=lab)
axs[0].set(xlabel=r'$\tau$',ylabel=r'$\sigma_x(\tau)/a=\sigma_y(\tau)/a$',title='宽度增长变慢')
axs[1].set(xlabel=r'$\tau$',ylabel=r'$|\langle\psi_{\rm rigid}(\tau)|\psi(\tau)\rangle|^2$',ylim=(0,1.03),title='与刚性平移初态的波函数重合度')
for ax in axs:ax.legend();ax.grid(alpha=.2)
finish(fig,'c13-extension-inflection','拓展：零二阶曲率点',
    '这是后续保形研究的初步入口。两种初态的sigma都为3、总概率都为1。q0=(pi/2,pi/2)处两个方向的二阶色散项消失，有限频宽内速度差减小，因此tau<=60内的展宽与形变明显较弱。右图比较实际波函数与按各自谱平均速度刚性平移的初态的模平方重合度，对整体相位不敏感，但会检测相对相位形变；它不是仅比较概率轮廓的指标。三阶及更高阶项仍存在，不能据此宣称无限时间严格保形。',(ordinary,inflection),role='extension')

fig,axs=plt.subplots(1,2,figsize=(12.8,5.6))
heading(fig,'C14  拓展：二阶项为零以后，三阶色散仍会积累',
    r'$\mathbf{q}_0=(\pi/2,\pi/2)$，$\sigma=2$；以更宽频谱显露高阶形变',
    '左图的初始峰值和后续峰值采用同一纵轴；右图为模型色散本身的截面展开。')
for j,t in enumerate((0,20,40,60)):
    p=probability(sharp,t);m=moments(propagate(sharp['psi0'],t))
    axs[0].plot(X-m['cx'],p.sum(axis=0),lw=2,label=rf'$\tau={t}$')
dq=np.linspace(-.9,.9,400)
axs[1].plot(dq,np.sin(dq)-dq,lw=2,label=r'精确：$\sin(\delta q)-\delta q$')
axs[1].plot(dq,-dq**3/6,lw=2,ls='--',label=r'三阶：$-(\delta q)^3/6$')
axs[0].set(xlim=(-14,14),ylim=(0,.205),xlabel=r'$(x-\langle x\rangle)/a$',ylabel=r'$P_x$',title='共动坐标中仍出现不对称形变')
axs[1].set(xlabel=r'$\delta q=q_x-\pi/2$',ylabel='去掉常数项与线性项后的能量 / Jx',title='二阶为零，首个修正是三阶项')
for ax in axs:ax.legend(fontsize=10);ax.grid(alpha=.2)
finish(fig,'c14-extension-cubic-distortion','拓展：高阶色散的有限带宽形变',
    '为使高阶形变在中期报告图中可见，本图用sigma=2、q0=(pi/2,pi/2)的独立示例；它与C13的sigma=3不同，不能据此直接比较保形性能。左图画tau=0、20、40、60的实际x边际概率，仅减去实际质心，保持统一纵轴。右图固定qy=pi/2，精确能量去除常数与线性项后为sin(delta q)-delta q，其首项是-(delta q)^3/6。有限频谱因此仍有相位差累积，产生不对称形变与尾部。此图说明零二阶曲率不等于零色散。',(sharp,),role='extension')

# Four animations, with time-independent spatial axes and probability scales.
anim_times=np.linspace(0,60,61)
for ident,cs,title,limits,caption in (
 ('c15-animation-carrier',(zero,right),'C15  有无载波：静止展宽与移动展宽',(-30,70,-35,35),
  'sigma=4的两个相同概率包络，载波分别为(0,0)与(0.7,0)，在精确色散下演化到tau=60。二维格点概率使用固定线性色标，图框和概率归一化固定，不逐帧放大。'),
 ('c16-animation-directions',(left,right,diagonal),'C16  载波选择左行、右行与斜向传播',(-65,65,-25,65),
  '三个sigma=4的初态仅载波不同，分别为(-0.7,0)、(0.7,0)、(0.7,0.7)。在相同尺度下播放到tau=60，帮助将载波相位梯度与传播方向联系起来。色标、位置范围、总概率固定。'),
 ('c18-animation-anisotropy',(diagonal,anisotropic),'C18  交换各向异性改变传播方向与形状',(-15,70,-15,70),
  '固定q0=(0.7,0.7)、sigma=4，比较eta=1与0.3。降低y方向交换后，y方向质心位移和宽度增长均减小。概率图采用相同固定线性色标及位置范围。')):
    fig,axs=maps_figure(cs,[0]*len(cs),title,
      '精确 Fourier 演化；固定位置范围、固定线性色标；无耗散',limits,
      r'$\tau=J_xt/\hbar$；$P=|\psi|^2$；每个波包的总概率为 1。')
    ims=[ax.images[0] for ax in axs]
    for ax,c in zip(axs,cs):
        ax.set_title(rf'$\mathbf{{q}}_0=({c["q0"][0]:g},{c["q0"][1]:g}),\ \eta={c["eta"]:g}$',fontsize=12)
    stamp=fig.text(.94,.855,r'$\tau=0$',ha='right',fontsize=14,color=INK)
    def update(t, cs=cs, ims=ims, stamp=stamp):
        for im,c in zip(ims,cs):im.set_data(probability(c,t))
        stamp.set_text(rf'$\tau={t:.0f}$')
    manifest.append(save_animation(fig,update,anim_times,GROUP,ident,title,caption,params(*cs)))
    print(ident,flush=True)

fig,axs=plt.subplots(1,2,figsize=(12.5,5.6))
heading(fig,'C17  初始宽度控制后续相对展宽',
    r'$\mathbf{q}_0=(0.7,0)$；不同 $\sigma$，相同总概率；随实际质心移动观察',
    '位置范围和概率纵轴全程固定；右图显示相对于各自初始宽度的增长。')
lines=[];dots=[]
for j,c in enumerate(widecases):
    line,=axs[0].plot([],[],lw=2,color=COLORS[j],label=rf'$\sigma={c["sigma"]:g}$');lines.append(line)
    axs[1].plot(TIMES,c['track']['wx']/c['track']['wx'][0],lw=1.6,color=COLORS[j],alpha=.35)
    dot,=axs[1].plot([0],[1],'o',color=COLORS[j],label=rf'$\sigma={c["sigma"]:g}$');dots.append(dot)
axs[0].set(xlim=(-35,35),ylim=(0,.14),xlabel=r'$(x-\langle x\rangle)/a$',ylabel=r'$P_x$')
axs[1].set(xlim=(0,60),ylim=(.95,3),xlabel=r'$\tau$',ylabel=r'$\sigma_x(\tau)/\sigma_x(0)$')
for ax in axs:ax.legend();ax.grid(alpha=.2)
stamp=fig.text(.94,.855,r'$\tau=0$',ha='right',fontsize=14,color=INK)
def update_width(t):
    for c,line,dot in zip(widecases,lines,dots):
        p=probability(c,t);m=moments(propagate(c['psi0'],t))
        line.set_data(X-m['cx'],p.sum(axis=0));dot.set_data([t],[m['wx']/c['track']['wx'][0]])
    stamp.set_text(rf'$\tau={t:.0f}$')
manifest.append(save_animation(fig,update_width,anim_times,GROUP,'c17-animation-width',
    '不同初始宽度的展宽动画','sigma=3、6、10的无啁啾Gaussian以q0=(0.7,0)传播。左图在各自共动坐标中显示真实边际概率，使用固定位置和纵轴范围；右图的移动点显示各自相对初始宽度的增长。所有初态总概率为1，初始尺寸不同是明确的物理输入。',params(*widecases)))
print('c17-animation-width',flush=True)

# Numerical checks address actual assumptions used in these figures.
checks=[]
for name,c in cases.items():
    tr=c['track'];spec=c['stats'];p0=moments(c['psi0'])
    errors={}
    for axis,ck,wk in ((0,'cx','wx'),(1,'cy','wy')):
        errors[ck+'_mean_error']=float(np.max(np.abs(tr[ck]-(p0[ck]+TIMES*spec['velocity'][axis]))))
        theory=p0[wk]**2+TIMES**2*spec['velocity_variance'][axis]
        errors[wk+'_variance_error']=float(np.max(np.abs(tr[wk]**2-theory)))
    psi60=propagate(c['psi0'],60,c['eta'])
    large=propagate(gaussian(384,c['sigma'],c['q0']),60,c['eta'])
    crop=large[64:320,64:320]
    spectral_change=float(np.max(np.abs(np.abs(np.fft.fft2(psi60,norm='ortho'))**2-spec['power'])))
    entry=dict(name=name,max_norm_error=float(np.max(abs(tr['norm']-1))),
        max_edge_mass=float(np.max(tr['edge_mass'])),
        enlarged_grid=384,enlarged_grid_amplitude_L2=float(np.linalg.norm(psi60-crop)),
        enlarged_grid_probability_L1=float(np.sum(np.abs(abs(psi60)**2-abs(crop)**2))),
        max_spectral_power_change=spectral_change,**errors)
    checks.append(entry)
    assert entry['max_norm_error']<1e-12,entry
    assert entry['max_edge_mass']<1e-9,entry
    assert entry['enlarged_grid_amplitude_L2']<1e-7,entry
    assert entry['max_spectral_power_change']<1e-12,entry
    assert max(errors.values())<1e-7,entry

data['parameters_json']=np.array(json.dumps(params(*cases.values()),ensure_ascii=False))
np.savez_compressed(OUT/'gaussian_simulation_data.npz',**data)
manifest.sort(key=lambda entry:entry['id'])
write_json(ROOT/'manifest_c.json',dict(group_title='C Gaussian 波包、移动与展宽',items=manifest))
write_json(ROOT/'checks_c.json',dict(passed=True,model='spin_wave_2d.Params(S=.5,Jx=1,Jy=eta,h=0)',
    norm_tolerance=1e-12,edge_mass_tolerance=1e-9,moment_tolerance=1e-7,
    wavefunction_enlarged_box_tolerance=1e-7,spectral_power_tolerance=1e-12,
    tested_times=TIMES,cases=checks,static_count=14,animation_count=4,
    data_file='c-gaussian/gaussian_simulation_data.npz',
    limitations=['Finite periodic FFT box, checked against a larger box before boundary return.',
      'Exact variance law shown assumes the unchirped real Gaussian envelope used here.',
      'Extension figures do not establish infinite-duration or finite-resource exact shape preservation.']))
print('C group complete: 14 static figures, 4 animations, data and numerical checks.',flush=True)
