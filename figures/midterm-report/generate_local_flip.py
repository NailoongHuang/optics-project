"""Generate the local one-magnon propagation section of the midterm gallery.

Run from any directory with ``python generate_local_flip.py``. Deterministic;
no stochastic sampling is involved. The independent infinite-lattice Bessel
solution checks the FFT propagator, while N=512 checks periodic-image effects.
"""
from pathlib import Path
from functools import lru_cache
import hashlib
import platform
import numpy as np
import scipy
from scipy.special import jv
import matplotlib
from matplotlib.colors import LogNorm
from common import (ROOT, plt, COLORS, delta, grid, propagate, moments,
                    heading, save_figure, save_animation, write_json)

GROUP = 'b-local-flip'
OUT = ROOT / GROUP
N = 256
X = np.arange(N)-N//2
INITIAL = delta(N)
MANIFEST = []
DATA = {'lattice_indices': X, 'initial_amplitude': INITIAL}
PROB_CMAP = plt.get_cmap('magma').copy()
PROB_CMAP.set_bad(PROB_CMAP(0))
PROB_CMAP.set_under(PROB_CMAP(0))
BASE = dict(N=N, S=.5, h=0, a=1, Jx=1, hbar=1,
            time_definition='tau=Jx*t/hbar', eta_definition='eta=Jy/Jx',
            initial_state='one normalized spin flip at (0,0)',
            boundary='periodic; edge mass and N=512 comparison checked',
            method='FFT exp[-i ((1-cos qx)+eta(1-cos qy))*tau]')


@lru_cache(maxsize=24)
def prob(tau, eta=1.):
    return abs(propagate(INITIAL, float(tau), float(eta)))**2


def analytic(tau, eta=1.):
    return np.outer(jv(X, eta*tau)**2, jv(X, tau)**2)


def add(fig, stem, title, caption, params=None, role='core'):
    MANIFEST.append(save_figure(fig, GROUP, stem, title, caption,
                               BASE | (params or {}), role=role))


def heat(ax, p, extent=40, *, log=True, vmax=1., vmin=1e-7):
    c=N//2
    crop=p[c-extent:c+extent+1, c-extent:c+extent+1]
    kw={'norm': LogNorm(vmin=vmin,vmax=vmax)} if log else {'vmin':0,'vmax':vmax}
    im=ax.imshow(crop,origin='lower',cmap=PROB_CMAP,interpolation='nearest',
                 extent=(-extent-.5,extent+.5,-extent-.5,extent+.5),**kw)
    ax.set(xlabel=r'$x/a$',ylabel=r'$y/a$')
    return im


def colorbar(fig, im, axes, label=r'$P_{m,n}$（对数色标）'):
    cb=fig.colorbar(im,ax=axes,fraction=.035,pad=.025)
    cb.set_label(label)
    return cb


def begin(title, subtitle, ncols=1, size=None, footer=''):
    fig, axes=plt.subplots(1,ncols,figsize=size or (11.5,6.8),squeeze=False)
    heading(fig,title,subtitle,footer)
    return fig,axes[0]


def static_figures():
    fig,axs=begin('B01｜一次局域翻转：初态是什么？',
                  r'背景沿 $+x$ 极化；在原点放置一个归一化的单磁子。',2,
                  footer=r'$P_{m,n}=|c_{m,n}|^2$；空间坐标 $x,y$ 与自旋极化方向是不同的概念。')
    im=heat(axs[0],prob(0.),3,log=False)
    axs[0].set_title(r'翻转概率：$P_{0,0}=1$')
    colorbar(fig,im,axs[0],r'$P_{m,n}$')
    sites=np.arange(-3,4)
    axs[1].scatter(sites[sites!=0],np.full(6,.5),s=75,color=COLORS[0],label='其余格点')
    axs[1].scatter([0],[-.5],s=120,color=COLORS[1],label='原点翻转')
    axs[1].plot([0,0],[.5,-.5],color=COLORS[1],lw=2,ls=':')
    axs[1].set(xlabel=r'$x/a$（$y=0$）',ylabel=r'$\langle S^x_{m,0}\rangle$',
               ylim=(-.65,.7),xticks=sites,title=r'局部自旋：$\langle S^x\rangle=\frac{1}{2}-P$')
    axs[1].legend(loc='lower right'); axs[1].grid(alpha=.2)
    add(fig,'b01-initial-local-flip','局域单翻转初态',
        '左图颜色为原点单翻转的概率P，线性色标0至1。右图显示y=0行的纵向自旋期望，原点为-1/2，其余为+1/2。量子化轴为+x；S为无量纲自旋算符。该归一化态有一个确定磁子，不能解释成具有非零横向自旋均值的经典旋转箭头。',{'tau':0,'eta':1})

    q=2*np.pi*np.fft.fftshift(np.fft.fftfreq(N))
    fq=np.fft.fftshift(np.fft.fft2(INITIAL,norm='ortho'))
    weight=abs(fq)**2
    DATA['q_shifted']=q; DATA['initial_spectral_probability']=weight
    fig,axs=begin('B02｜空间越局域，包含的波矢越多',
                  r'$c_{m,n}(0)=\delta_{m,0}\delta_{n,0}\quad\Longrightarrow\quad |A(q_x,q_y)|^2=1/N^2$',2,
                  footer=r'纵轴乘以 $N^2$ 仅为显示方便；全布里渊区权重相等，并非一个窄带波包。')
    im=axs[0].imshow(N*N*weight,origin='lower',extent=(-np.pi,np.pi,-np.pi,np.pi),
                     vmin=0,vmax=1,cmap='Blues',interpolation='nearest')
    axs[0].set(xlabel=r'$q_x=k_xa$',ylabel=r'$q_y=k_ya$',title='二维波矢权重')
    cb=fig.colorbar(im,ax=axs[0],fraction=.045,pad=.04); cb.set_label(r'$N^2|A|^2$')
    axs[1].plot(q,N*N*weight[N//2],lw=2.5)
    axs[1].set(xlabel=r'$q_x$（$q_y=0$）',ylabel=r'$N^2|A|^2$',ylim=(0,1.2),
               xlim=(-np.pi,np.pi),title='一条截线：所有波矢都有贡献')
    axs[1].grid(alpha=.2)
    add(fig,'b02-flat-spectrum','局域初态的均匀波矢权重',
        '对归一化单格点态作正交归一化二维离散Fourier变换。每个离散波矢的概率均为1/N²，图中绘制N²|A|²以提高可读性。左图为整个第一布里渊区，右图为qy=0截面。局域初态包含整个能带，不能用单个中心波矢及低阶Taylor展开描述其全部传播。')

    early=[.25,.6,1.2,2.]
    fig,axs=begin('B03｜最初几步：概率怎样流向邻近格点？',
                  r'$\eta=1$；同一固定色标，逐个格点显示。',4,(15.6,6.2),
                  footer='交换跃迁先使近邻获得振幅；后续振幅相干叠加，形成空间干涉结构。')
    for ax,t in zip(axs,early):
        p=prob(t); DATA[f'early_tau_{str(t).replace(".","p")}']=p
        im=heat(ax,p,3,log=False,vmax=1)
        ax.set_title(rf'$\tau={t:g}$'); ax.set_xticks([-3,0,3]); ax.set_yticks([-3,0,3])
    colorbar(fig,im,list(axs),r'$P_{m,n}$（固定线性色标）')
    add(fig,'b03-early-neighbor-spreading','早期近邻传播',
        '四幅图依次为τ=0.25、0.6、1.2、2，固定线性色标0至1，显示中心7×7格点。颜色直接表示单翻转概率，不能逐图归一化解释为同一峰高。哈密顿量的近邻耦合产生概率向外转移；图中为完整FFT计算的局部裁切。',{'times':early,'eta':1,'display_crop':3})

    late=[6.,12.,24.,36.]
    fig,axs=begin('B04｜更长时间：传播与晶格干涉图样',
                  r'$\eta=1$；固定观察窗与固定对数色标。',4,(15.6,6.2),
                  footer=r'方格晶格具有四重对称性；等方交换 $J_x=J_y$ 不等于任意波矢下的连续旋转对称。')
    for ax,t in zip(axs,late):
        p=prob(t); DATA[f'isotropic_tau_{int(t)}']=p
        im=heat(ax,p,44,vmax=.1,vmin=1e-7); ax.set_title(rf'$\tau={t:g}$')
    colorbar(fig,im,list(axs))
    add(fig,'b04-isotropic-late-snapshots','等方晶格的后期传播',
        'τ=6、12、24、36的二维翻转概率采用相同空间范围及10^-7至0.1的对数色标。概率低于色标下限不可见，显示边缘不是严格截止。分布向外展开，同时保留相干干涉条纹和方格晶格的四重对称性；因此等方交换的点激发传播并不必然形成圆形波前。',{'times':late,'eta':1,'display_crop':44,'color_limits':[1e-7,.1]})

    etas=[0.,.3,1.]
    fig,axs=begin('B05｜改变交换强度：从一维链到二维展开',
                  r'固定 $J_x$ 与 $\tau=24$，只改变 $\eta=J_y/J_x$。',3,(14.5,6.4),
                  footer=r'$J_y=0$ 时各行彼此解耦；$0<J_y<J_x$ 时沿 $y$ 的展开较慢。')
    for ax,e in zip(axs,etas):
        p=prob(24.,e); DATA[f'anisotropy_eta_{str(e).replace(".","p")}']=p
        im=heat(ax,p,34,vmax=.1,vmin=1e-7); ax.set_title(rf'$\eta={e:g}$')
    colorbar(fig,im,list(axs))
    add(fig,'b05-anisotropy-comparison','交换各向异性与一维极限',
        '固定τ=24与Jx，比较η=0、0.3、1。所有图使用同一空间尺度及10^-7至0.1的对数色标。η=0时y方向无耦合，概率严格停留在y=0行；η=0.3时二维分布沿y较窄；η=1时两个方向对称。这里的各向异性是空间交换参数差异，并未引入自旋空间的易轴或易面项。',{'tau':24,'etas':etas,'display_crop':34})

    times=[4.,12.,24.]
    fig,axs=begin('B06｜把二维分布投影到两个方向',
                  r'$P_x(m)=\sum_n P_{m,n}$，$P_y(n)=\sum_m P_{m,n}$；$\eta=0.3$。',2,
                  footer='边际概率对另一坐标求和，区别于只取 y=0 或 x=0 的截线。')
    for t,col in zip(times,COLORS):
        p=prob(t,.3)
        axs[0].plot(X,p.sum(axis=0),color=col,lw=1.9,label=rf'$\tau={t:g}$')
        axs[1].plot(X,p.sum(axis=1),color=col,lw=1.9,label=rf'$\tau={t:g}$')
    for ax,coord in zip(axs,['x','y']):
        ax.set(xlim=(-32,32),ylim=(0,.5),xlabel=rf'${coord}/a$',ylabel='边际翻转概率',title=f'{coord} 方向')
        ax.legend(); ax.grid(alpha=.2)
    add(fig,'b06-marginal-probabilities','两个方向的边际概率',
        'η=0.3时τ=4、12、24的边际概率：左图对y求和，右图对x求和。各曲线对全部格点求和均为1；固定相同横坐标范围和纵轴范围以比较扩展速度。边际概率P_x、P_y与中心截线P_{m,0}、P_{0,n}不同。',{'eta':.3,'times':times})

    st=np.linspace(0,40,161)
    px=np.array([prob(float(t),1.).sum(axis=0) for t in st])
    py=np.array([prob(float(t),.3).sum(axis=1) for t in st])
    DATA.update(spacetime_times=st,spacetime_px=px,spacetime_py_eta03=py)
    fig,axs=begin('B07｜时空图：传播前沿与干涉条纹',
                  r'横轴为空间，纵轴为时间；颜色为 $P_x(m,\tau)$。',1,
                  footer=r'虚线 $|x|/a=\tau$ 来自最大群速度；线外仍有小概率尾部，不是严格零概率边界。')
    ax=axs[0]; sel=abs(X)<=50
    im=ax.imshow(px[:,sel],origin='lower',aspect='auto',extent=(-50.5,50.5,-.125,40.125),
                 norm=LogNorm(vmin=1e-7,vmax=1),cmap=PROB_CMAP,interpolation='nearest')
    for sign in [-1,1]: ax.plot(sign*st,st,'--',lw=1.4,color='#71DFD5')
    ax.set(xlabel=r'$x/a$',ylabel=r'$\tau=J_x t/\hbar$',ylim=(0,40))
    colorbar(fig,im,ax,r'$P_x$（对数色标）')
    add(fig,'b07-spacetime-isotropic','时空传播与最大群速度',
        '对每个时间计算归一化二维态，再对y求和得到P_x。纵轴为τ，横轴为x/a；固定对数色标10^-7至1。青色虚线为x/a=±τ，对应|v_x|≤Jx a/ℏ，指出主要弹道前沿的位置。有限时间的晶格传播核在线外仍有小而非零的尾部，图示不是严格光锥。',{'eta':1,'times':st.tolist(),'color_limits':[1e-7,1]})

    fig,axs=begin('B08｜两个传播前沿：交换强度决定斜率',
                  r'$\eta=0.3$；$|v_x|\leq J_xa/\hbar$，$|v_y|\leq J_ya/\hbar$。',2,
                  footer='两个面板采用相同坐标和色标，直接比较 x 与 y 的展开范围。')
    for ax,data,e,coord in zip(axs,[px,py],[1.,.3],['x','y']):
        im=ax.imshow(data[:,sel],origin='lower',aspect='auto',extent=(-50.5,50.5,-.125,40.125),
                     norm=LogNorm(vmin=1e-7,vmax=1),cmap=PROB_CMAP,interpolation='nearest')
        for sign in [-1,1]: ax.plot(sign*e*st,st,'--',lw=1.4,color='#71DFD5')
        ax.set(xlabel=rf'${coord}/a$',ylabel=r'$\tau$',title=f'{coord} 方向的边际概率',ylim=(0,40))
    colorbar(fig,im,list(axs),r'$P_x$ 或 $P_y$（对数色标）')
    add(fig,'b08-anisotropic-spacetime','各向异性时空传播',
        'η=0.3的x、y边际概率时空图。由于初态和色散都可分离，P_x不依赖η；其数据与η=1完全相同。虚线分别为|x|/a=τ和|y|/a=0.3τ，颜色使用固定10^-7至1对数范围。线外仍存在非零尾部，最大群速度给出主要弹道前沿尺度。',{'eta':.3,'times':st.tolist()})

    ts=np.linspace(0,40,81)
    stats={}
    for e in [1.,.3,0.]:
        rows=[moments(propagate(INITIAL,float(t),e)) for t in ts]
        stats[e]={k:np.array([r[k] for r in rows]) for k in rows[0]}
        for k,v in stats[e].items(): DATA[f'stats_eta_{str(e).replace(".","p")}_{k}']=v
    DATA['moment_times']=ts
    fig,axs=begin('B09｜展开有多快？均方根宽度随时间线性增长',
                  r'$\sigma_x/a=\tau/\sqrt{2}$，$\sigma_y/a=\eta\tau/\sqrt{2}$。',2,
                  footer='线：无限晶格解析结果；点：二维 FFT 概率的矩。线性宽度增长称为弹道展开。')
    for ax,key,coord in zip(axs,['wx','wy'],['x','y']):
        for e,col in zip([1.,.3,0.],COLORS):
            pred=ts*(1 if coord=='x' else e)/np.sqrt(2)
            ax.plot(ts,pred,color=col,alpha=.8,lw=2)
            ax.scatter(ts[::6],stats[e][key][::6],s=32,facecolors='none',edgecolors=col,label=rf'$\eta={e:g}$')
        ax.set(xlabel=r'$\tau$',ylabel=rf'$\sigma_{coord}/a$',title=f'{coord} 方向 RMS 宽度')
        ax.grid(alpha=.2); ax.legend()
    add(fig,'b09-ballistic-rms','均方根宽度的弹道增长',
        '从归一化FFT概率计算质心及标准差σ。无限晶格Bessel恒等式给出σx/a=τ/√2和σy/a=ητ/√2；实线为解析值，空心点为FFT矩。η=1、0.3、0的x曲线重合，y曲线随η变化。这里表征的是局域初态分布的展开，不是窄带Gaussian包络的二阶色散近似。',{'etas':[1,.3,0],'times':ts.tolist()})

    rt=np.linspace(0,40,401)
    fig,axs=begin('B10｜原点会被再次找到吗？返回概率的振荡',
                  r'$P_{0,0}(\tau)=\mathrm{J}_0(\tau)^2\,\mathrm{J}_0(\eta\tau)^2$；$\mathrm{J}_0$ 为 Bessel 函数。',2,
                  footer='振荡反映相干叠加；原点概率减少并不等于磁子消失，总概率始终为 1。')
    for ax,e in zip(axs,[1.,.3]):
        vals=np.array([prob(float(t),e)[N//2,N//2] for t in rt])
        exact=jv(0,rt)**2*jv(0,e*rt)**2
        DATA[f'return_eta_{str(e).replace(".","p")}']=vals
        ax.semilogy(rt,exact,lw=2,label='Bessel 解析解')
        ax.scatter(rt[::9],vals[::9],s=18,facecolors='none',edgecolors=COLORS[1],label='FFT')
        ax.set(xlabel=r'$\tau$',ylabel=r'$P_{0,0}$',ylim=(1e-12,1.5),title=rf'$\eta={e:g}$')
        ax.legend(); ax.grid(alpha=.2)
    DATA['return_times']=rt
    add(fig,'b10-return-probability','中心返回概率的相干振荡',
        '比较η=1和0.3的原点翻转概率，纵轴为对数。曲线为P00=J0(τ)^2 J0(ητ)^2，空心点为FFT直接读出的原点值。这里J0表示第一类Bessel函数，与交换常数Jx、Jy不同。原点概率的降低和再升高源于相干演化，不代表耗散或非线性相互作用。',{'etas':[1,.3],'times':rt.tolist()})

    es=np.linspace(0,1.5,31)
    widths=np.array([[moments(propagate(INITIAL,24.,float(e)))[k] for k in ['wx','wy']] for e in es])
    DATA.update(eta_scan=es,eta_scan_widths=widths)
    fig,axs=begin('B11｜连续改变各向异性：分布长宽比怎样变化？',
                  r'固定 $\tau=24$，扫描 $0\leq\eta\leq1.5$。',2,
                  footer=r'RMS 长宽比 $\sigma_y/\sigma_x=\eta$；这是指定模型与单格点初态的结果。')
    axs[0].plot(es,np.full_like(es,24/np.sqrt(2)),label=r'$\sigma_x$ 解析值')
    axs[0].plot(es,es*24/np.sqrt(2),label=r'$\sigma_y$ 解析值')
    axs[0].scatter(es[::2],widths[::2,0],s=22,facecolors='none',edgecolors=COLORS[0])
    axs[0].scatter(es[::2],widths[::2,1],s=22,facecolors='none',edgecolors=COLORS[1])
    axs[0].set(xlabel=r'$\eta=J_y/J_x$',ylabel=r'$\sigma/a$',title='两个方向的实际宽度'); axs[0].legend()
    axs[1].plot(es,es,label='解析关系')
    axs[1].scatter(es,widths[:,1]/widths[:,0],s=23,facecolors='none',edgecolors=COLORS[1],label='FFT')
    axs[1].set(xlabel=r'$\eta=J_y/J_x$',ylabel=r'$\sigma_y/\sigma_x$',title='归一化长宽比'); axs[1].legend()
    for ax in axs: ax.grid(alpha=.2)
    add(fig,'b11-anisotropy-scan','交换比与RMS长宽比',
        '固定Jx、初态、格点数和τ=24，只扫描η。左图显示σx不变、σy随η线性增长；右图为σy/σx=η。解析线和FFT点对照。在η>1时分布沿y比沿x宽；η=0退化为一维传播。该比较固定的是无量纲τ，即固定Jx条件下相同的物理时间。',{'tau':24,'etas':es.tolist()})

    tau=8.; p=prob(tau); sl=abs(X)<=15
    fig,axs=begin('B12｜从翻转概率读出可观测的自旋分布',
                  r'$\langle S^x_{m,n}\rangle=\frac{1}{2}-P_{m,n}$，$\langle S^y\rangle=\langle S^z\rangle=0$。',2,
                  footer=r'单磁子态的总纵向自旋亏损 $\sum_{m,n}(1/2-\langle S^x_{m,n}\rangle)=1$。')
    axs[0].plot(X[sl],p[N//2,sl],'o-',ms=4)
    axs[0].set(xlabel=r'$x/a$（$y=0$）',ylabel=r'$P_{m,0}$',title=rf'中心截线：$\tau={tau:g}$')
    axs[1].plot(X[sl],.5-p[N//2,sl],'o-',ms=4,color=COLORS[2])
    axs[1].axhline(.5,color='#8493A0',ls='--',label='完全极化背景')
    axs[1].set(xlabel=r'$x/a$（$y=0$）',ylabel=r'$\langle S^x_{m,0}\rangle$',title='同一截线的纵向自旋期望')
    axs[1].legend(loc='lower right')
    for ax in axs: ax.grid(alpha=.2)
    add(fig,'b12-probability-to-spin','翻转概率与纵向自旋观测量',
        'η=1、τ=8时的y=0截线。左图为P_m0，右图逐格点应用<Sx>=1/2-P得到纵向自旋期望；虚线为背景1/2。两图纵轴不同，峰值概率对应自旋亏损。归一化单磁子态的总亏损为1，而<Sy>=<Sz>=0；概率波的复相位不能直接画成非零的局域横向平均自旋。',{'tau':tau,'eta':1})

    p=prob(36.,.3); pa=analytic(36.,.3); err=np.abs(p-pa)
    DATA.update(validation_fft_probability=p,validation_bessel_probability=pa)
    fig,axs=begin('B13｜独立核对：FFT 与无限晶格解析传播核',
                  r'$P_{m,n}=\mathrm{J}_m(\tau)^2\,\mathrm{J}_n(\eta\tau)^2$；$\tau=36$，$\eta=0.3$。',2,
                  footer='左图对照完整 x 边际；右图显示逐格点的绝对误差。解析核与 FFT 使用不同计算路线。')
    axs[0].plot(X,pa.sum(axis=0),lw=2,label='Bessel 解析解')
    axs[0].scatter(X[::2],p.sum(axis=0)[::2],s=22,facecolors='none',edgecolors=COLORS[1],label='FFT')
    axs[0].set(xlim=(-48,48),xlabel=r'$x/a$',ylabel=r'$P_x$',title='解析结果与数值结果重合'); axs[0].legend(); axs[0].grid(alpha=.2)
    im=heat(axs[1],err*1e17,48,log=False,vmax=max(float(err.max())*1e17,1.))
    axs[1].set_title('绝对概率误差')
    colorbar(fig,im,axs[1],r'$10^{17}|P_{\rm FFT}-P_{\rm Bessel}|$')
    add(fig,'b13-independent-bessel-check','Bessel解析核独立验证',
        '去除基态整体相位exp[-i EF t/ℏ]后，无限晶格解析振幅为exp[-i(1+η)τ] i^(m+n) J_m(τ)J_n(ητ)，故概率为两个Bessel平方的乘积。左图比较x边际，右图为FFT概率与解析概率逐格点之差的绝对值乘以10^17，采用线性色标；色标1代表实际误差10^-17。有限周期晶格只有在边界回绕可忽略时才与无限晶格核一致；另有N=512和边界概率质量检查。',{'tau':36,'eta':.3},role='verification')


def animations():
    configs=[
        ('b14-early-spreading','最初几步的单格点传播',np.linspace(0,4,65),[1.],6,1e-5,1.),
        ('b15-isotropic-propagation','等方晶格中的局域传播',np.linspace(0,36,73),[1.],45,1e-7,1.),
        ('b16-anisotropic-propagation','等方与各向异性交换的传播对照',np.linspace(0,36,73),[1.,.3],45,1e-7,1.),
    ]
    for stem,title,times,etas,extent,vmin,vmax in configs:
        fig,axs=begin(title,'归一化单磁子；全程固定坐标与概率色标。',len(etas),
                      (10.2 if len(etas)==1 else 12.8,6.8),
                      footer='颜色为真实概率的对数；低于色标下限的尾部不可见。')
        images=[]
        for ax,e in zip(axs,etas):
            images.append(heat(ax,prob(0.,e),extent,vmin=vmin,vmax=vmax))
            ax.set_title(rf'$\eta={e:g}$')
        colorbar(fig,images[-1],list(axs))
        time_text=fig.text(.77,.86,'',fontsize=14,color='#203648')
        def update(t):
            c=N//2
            for im,e in zip(images,etas):
                pp=prob(t,e); im.set_data(pp[c-extent:c+extent+1,c-extent:c+extent+1])
            time_text.set_text(rf'$\tau={t:.2f}$')
        item=save_animation(fig,update,times,GROUP,stem,title,
            f'从τ=0到{times[-1]:g}的实际FFT时间演化，η={etas}。所有帧采用相同空间窗以及{vmin:g}至{vmax:g}的对数概率色标，无逐帧峰值归一化。坐标单位为a，时间单位为ℏ/Jx；截断显示的尾部不是严格零。',
            BASE|{'etas':etas,'times':times.tolist(),'display_crop':extent,'color_limits':[vmin,vmax]})
        MANIFEST.append(item)

    times=np.linspace(0,36,73)
    fig,axs=begin('两个方向的边际概率如何随时间改变？',
                  r'$\eta=0.3$；曲线与纵轴全程采用同一个概率尺度。',2,(12,6.8),
                  footer='各边际分布的总和为 1；图中使用对数纵轴来同时看清主峰与尾部。')
    lines=[]
    for ax,coord,col in zip(axs,['x','y'],COLORS):
        line,=ax.semilogy(X,np.maximum(prob(0.,.3).sum(axis=0 if coord=='x' else 1),1e-15),color=col,lw=2)
        lines.append(line)
        ax.set(xlim=(-45,45),ylim=(1e-7,1.2),xlabel=rf'${coord}/a$',ylabel='边际概率',title=f'{coord} 方向')
        ax.grid(alpha=.2)
    time_text=fig.text(.78,.86,'',fontsize=14,color='#203648')
    def update_marginal(t):
        pp=prob(t,.3)
        lines[0].set_ydata(np.maximum(pp.sum(axis=0),1e-15))
        lines[1].set_ydata(np.maximum(pp.sum(axis=1),1e-15))
        time_text.set_text(rf'$\tau={t:.2f}$')
    MANIFEST.append(save_animation(fig,update_marginal,times,GROUP,'b17-marginal-animation',
        '各向异性边际概率演化','η=0.3时的x、y边际概率动画。对另一空间方向求和，分别得到归一化分布Px和Py；两个面板全程使用相同的空间窗[-45a,45a]及对数纵轴[10^-7,1.2]。数值零仅在绘图时下限替代为10^-15，处于显示范围以外。',
        BASE|{'eta':.3,'times':times.tolist(),'axis_limits':[1e-7,1.2]}))


def verification():
    records=[]
    for e in [0.,.3,1.,1.5]:
        for t in [0.,.25,2.,12.,24.,36.,45.]:
            psi=propagate(INITIAL,t,e); p=abs(psi)**2; pa=analytic(t,e)
            mm=moments(psi)
            amp=(np.exp(-1j*(1+e)*t)*np.outer((1j)**X*jv(X,e*t),(1j)**X*jv(X,t)))
            big=propagate(delta(512),t,e)
            crop=big[128:384,128:384]
            records.append(dict(tau=t,eta=e,**mm,
                probability_max_abs_error=float(np.max(abs(p-pa))),
                amplitude_l2_error=float(np.linalg.norm(psi-amp)),
                N256_N512_amplitude_l2_error=float(np.linalg.norm(psi-crop)),
                width_x_error=abs(mm['wx']-t/np.sqrt(2)),
                width_y_error=abs(mm['wy']-e*t/np.sqrt(2))))
    maxs={k:max(r[k] for r in records) for k in ['probability_max_abs_error','amplitude_l2_error',
           'N256_N512_amplitude_l2_error','width_x_error','width_y_error','edge_mass']}
    maxs['norm_error']=max(abs(r['norm']-1) for r in records)
    maxs['centroid_abs']=max(max(abs(r['cx']),abs(r['cy'])) for r in records)
    # All diagnostics are many orders below the plotting scale; no fitted tolerance.
    thresholds={'probability_max_abs_error':1e-12,'amplitude_l2_error':1e-11,
                'N256_N512_amplitude_l2_error':1e-11,'width_x_error':1e-10,
                'width_y_error':1e-10,'edge_mass':1e-12,'norm_error':1e-12,'centroid_abs':1e-10}
    check={'status':'pass' if all(maxs[k]<v for k,v in thresholds.items()) else 'fail',
           'summary':maxs,'thresholds':thresholds,'records':records,
           'animations':[{'id':m['id'],'frame_count':m['frame_count'],'frames_decoded':m['frames_decoded']} for m in MANIFEST if 'frame_count' in m],
           'environment':{'python':platform.python_version(),'numpy':np.__version__,
                          'scipy':scipy.__version__,'matplotlib':matplotlib.__version__},
           'deterministic':True,'seed':None,'config':BASE,
           'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    write_json(ROOT/'checks_b.json',check)
    if check['status']!='pass': raise AssertionError(maxs)
    return check


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    static_figures()
    animations()
    checks=verification()
    np.savez_compressed(OUT/'local_flip_data.npz',**DATA)
    write_json(ROOT/'manifest_b.json',{'group_title':'B｜单格点翻转的传播','items':MANIFEST})
    write_json(OUT/'parameters.json',BASE|{'data_file':'local_flip_data.npz',
                                         'description':'All static figure data and sampled diagnostic trajectories; animation timestamps are stored in manifest_b.json.'})
    print(f'Generated {sum("png" in m["files"] for m in MANIFEST)} figures and {sum("gif" in m["files"] for m in MANIFEST)} animations.')
    print(checks['summary'])


if __name__=='__main__':
    main()
