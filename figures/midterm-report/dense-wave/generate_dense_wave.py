"""Reproduce the dense lattice-wave figures used by the revised midterm deck.

Run: python figures/midterm-report/dense-wave/generate_dense_wave.py
Uses the project's exact one-magnon Fourier propagator from ../common.py.
No smoothing, interpolation, or framewise normalization is used in field maps.
"""
from pathlib import Path
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from PIL import Image
from scipy.special import jv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import common as cm

N = 512
SIGMA = 10.
TIMES = np.array([0., 30., 60.])
ANIMATION_TIMES = np.linspace(0., 60., 61)
X = np.arange(N) - N//2
INK = '#183447'
BLUE = '#226B9A'
ORANGE = '#CB6742'
ITEMS = []
PARAMETERS = {'N':N, 'sigma_a':SIGMA, 'a':1., 'hbar':1., 'Jx':1.,
              'S':0.5, 'h':0., 'boundary':'periodic',
              'dimensionless_time':'tau=Jx*t/hbar',
              'wavevectors':[[.7,0.],[.7,.7]], 'etas':[1.,.3],
              'snapshot_times':TIMES.tolist(), 'animation_times':ANIMATION_TIMES.tolist(),
              'phase_convention':'Remove exp(-i E_F t/hbar) only; no per-frame rephasing.',
              'field_maps':'Exact site values; imshow interpolation=nearest.',
              'sampling':'N enlarges the periodic box. a and the carrier sampling are unchanged.',
              'interpretation':'Re(psi) is the probability-amplitude real part in a fixed phase convention, not a transverse-spin expectation in a fixed one-magnon state.',
              'gaussian_normalization':'A0=max|psi(t=0)|; P0=A0^2, held fixed in every panel/frame.'}


def write_json(path, obj):
    def encode(x):
        if isinstance(x,np.ndarray): return x.tolist()
        if isinstance(x,np.generic): return x.item()
        raise TypeError(type(x).__name__)
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=encode),encoding='utf-8')


def save(fig, stem, title, caption):
    paths={}
    for ext in ('png','svg','pdf'):
        path=ROOT/f'{stem}.{ext}'
        fig.savefig(path, dpi=185, bbox_inches='tight', pad_inches=.08)
        paths[ext]=path.name
    plt.close(fig)
    ITEMS.append({'id':stem,'title':title,'caption':caption,'files':paths})


def region(array,xlim,ylim):
    ix=(X>=xlim[0])&(X<=xlim[1]); iy=(X>=ylim[0])&(X<=ylim[1])
    return array[np.ix_(iy,ix)]


def field(ax, array, xlim, ylim, title, probability=False, vmin=None, vmax=None):
    if vmin is None: vmin=0 if probability else -1
    if vmax is None: vmax=1
    im=ax.imshow(region(array,xlim,ylim), origin='lower',
                 extent=[xlim[0]-.5,xlim[1]+.5,ylim[0]-.5,ylim[1]+.5],
                 interpolation='nearest',aspect='equal',
                 cmap='magma' if probability else 'RdBu_r',vmin=vmin,vmax=vmax,
                 rasterized=True)
    ax.set(xlabel=r'$x/a$',ylabel=r'$y/a$',title=title)
    return im


def colorbar(fig,im,ax,label):
    bar=fig.colorbar(im,ax=ax,pad=.025,fraction=.047,shrink=.95)
    bar.set_label(label,fontsize=15)
    bar.ax.tick_params(labelsize=12)


def setup():
    ROOT.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'sans-serif',
        'font.sans-serif':['Microsoft YaHei','DejaVu Sans'],
        'font.size':15,'axes.titlesize':17,'axes.labelsize':15,
        'xtick.labelsize':13,'ytick.labelsize':13,'legend.fontsize':12,
        'axes.unicode_minus':False,'svg.fonttype':'path','pdf.fonttype':42,
        'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False,
        'savefig.facecolor':'white','text.color':INK,'axes.labelcolor':INK})


def make_static(states, data):
    initial=states['x_eta1'][0]; a0=float(np.abs(initial).max()); p0=a0*a0
    # A fixed scale and a local view expose carrier oscillations without resampling.
    psi=states['x_eta1'][1]
    fig=plt.figure(figsize=(15.5,7.3),layout='constrained')
    grid=fig.add_gridspec(2,2,height_ratios=[2.25,1.])
    ax1=fig.add_subplot(grid[0,0]); ax2=fig.add_subplot(grid[0,1])
    ax3=fig.add_subplot(grid[1,:])
    im1=field(ax1,psi.real/a0,(-25,65),(-30,30),r'振幅实部  $\tau=30$')
    im2=field(ax2,np.abs(psi)**2/p0,(-25,65),(-30,30),r'翻转概率  $\tau=30$',True)
    colorbar(fig,im1,ax1,r'$\mathrm{Re}\,\psi/A_0$')
    colorbar(fig,im2,ax2,r'$|\psi|^2/P_0$')
    mask=(X>=-25)&(X<=65); line=psi[N//2,mask]
    ax3.plot(X[mask],line.real/a0,'o-',color=BLUE,markersize=2.8,lw=1.8,label=r'$\mathrm{Re}\,\psi(x,0)/A_0$')
    ax3.plot(X[mask],np.abs(line)/a0,'--',color=ORANGE,lw=2,label=r'$\pm|\psi(x,0)|/A_0$')
    ax3.plot(X[mask],-np.abs(line)/a0,'--',color=ORANGE,lw=2)
    ax3.axhline(0,color='#758590',lw=.7); ax3.set(xlabel=r'$x/a$',ylabel='归一化振幅',xlim=(-25,65),ylim=(-1.05,1.05))
    ax3.legend(ncol=2,loc='upper right'); ax3.grid(alpha=.15)
    save(fig,'w01_real_probability','同一波包：载波振幅与翻转概率',
         'N=512，σ=10a，q₀=(0.7,0)，η=1，τ=30。上方为同一复振幅的实部与模方；下方取 y=0 的实际格点截线。实部显出波峰和波谷，概率显示包络。A₀=max|ψ(0)|、P₀=A₀²；色标固定，未逐帧归一化。Reψ 依赖固定相位约定，不表示固定单磁子态的横向自旋期望。')

    fig,axs=plt.subplots(1,3,figsize=(16,3.6),layout='constrained',sharey=True)
    for ax,t,psi in zip(axs,TIMES,states['x_eta1']):
        im=field(ax,psi.real/a0,(-30,80),(-33,33),rf'$\tau={t:g}$')
        center=cm.moments(psi)['cx']
        ax.axvline(center,color='#4F5A64',lw=1,ls='--',alpha=.75)
    colorbar(fig,im,list(axs),r'$\mathrm{Re}\,\psi/A_0$')
    save(fig,'w02_carrier_sequence','载波随波包传播的三个时刻',
         'q₀=(0.7,0)，σ=10a，η=1。τ=0、30、60 使用相同空间窗口与同一固定色标；虚线为概率质心。热图显示实际格点，没有连续插值。载波波峰与包络质心不必以同一速度运动。')

    fig,axs=plt.subplots(1,3,figsize=(16,4.5),layout='constrained',sharey=True)
    for ax,t,psi in zip(axs,TIMES,states['x_eta1']):
        center=cm.moments(psi)['cx']; xi=X-center; mask=np.abs(xi)<=34
        line=psi[N//2,mask]
        ax.plot(xi[mask],line.real/a0,'o-',color=BLUE,markersize=3,lw=1.6)
        ax.plot(xi[mask],np.abs(line)/a0,color=ORANGE,lw=2,label='振幅包络')
        ax.plot(xi[mask],-np.abs(line)/a0,color=ORANGE,lw=2)
        ax.plot(xi[mask],np.exp(-xi[mask]**2/(4*SIGMA**2)),'--',color='#88959B',lw=1.4,label='初始包络')
        ax.axhline(0,color='#758590',lw=.7)
        ax.set(xlabel=r'$(x-\langle x\rangle)/a$',title=rf'$\tau={t:g}$',xlim=(-34,34),ylim=(-1.08,1.08))
        ax.grid(alpha=.14)
    axs[0].set_ylabel(r'振幅 / $A_0$'); axs[0].legend(loc='upper right',fontsize=11)
    save(fig,'w03_comoving_sections','跟随质心观察波形与包络',
         'q₀=(0.7,0)，σ=10a，η=1；取 y=0 的真实格点数据，以 x−〈x〉作横坐标，并未空间插值或逐帧重定相位。蓝线为 Reψ/A₀，橙线为 ±|ψ|/A₀，灰虚线为初始正包络。共动坐标消去质心平移，但仍能看见载波相位变化及有限展宽。')

    psi=data['delta_tau24']
    fig,axs=plt.subplots(1,2,figsize=(14.8,6.0),layout='constrained')
    im=field(axs[0],psi.real,(-35,35),(-35,35),r'局域激发：$\mathrm{Re}\,\psi$  ($\tau=24$)',vmin=-.06,vmax=.06)
    colorbar(fig,im,axs[0],r'$\mathrm{Re}\,\psi$')
    im=field(axs[1],np.abs(psi)**2,(-35,35),(-35,35),r'局域激发：$|\psi|^2$  ($\tau=24$)',True,vmin=0,vmax=.0036)
    colorbar(fig,im,axs[1],r'$|\psi|^2$')
    save(fig,'w04_local_interference','单格点翻转形成密集干涉结构',
         '初态 ψₘₙ(0)=δₘ₀δₙ₀，η=1，N=512，τ=24。图示实际格点的振幅实部与翻转概率。两者直接使用原数值；指定色标范围为 Reψ∈[−0.06,0.06]、P∈[0,0.0036]，无归一化缩放。干涉结构是全布里渊区模式相干叠加的结果，不能用一个中心波矢的群速度解释全部细节。')

    fig,axs=plt.subplots(1,2,figsize=(15,6.2),layout='constrained',sharey=True)
    for ax,eta,key in zip(axs,[1.,.3],['diagonal_eta1','diagonal_eta03']):
        psi=states[key][-1]; m=cm.moments(psi)
        im=field(ax,psi.real/a0,(-15,82),(-22,75),rf'$\eta=J_y/J_x={eta:g}$,  $\tau=60$')
        ax.plot(0,0,'o',color='#1E2935',ms=4)
        ax.annotate('',xy=(m['cx'],m['cy']),xytext=(0,0),arrowprops={'arrowstyle':'->','lw':2.2,'color':'#222D38'})
        ax.plot(m['cx'],m['cy'],'o',mfc='white',mec='#222D38',ms=5)
    colorbar(fig,im,list(axs),r'$\mathrm{Re}\,\psi/A_0$')
    save(fig,'w05_anisotropic_waves','相同载波在不同交换各向异性下传播',
         '两图均为 q₀=(0.7,0.7)、σ=10a、τ=60。仅改变 η=Jᵧ/Jₓ：左1，右0.3；箭头从初始中心指向此刻概率质心。同一固定振幅色标。各向异性改变 y 方向群速度，载波相位法线方向与群速度方向因此一般不重合。')

    psi=states['diagonal_eta1'][0]
    fig,axs=plt.subplots(1,2,figsize=(14.8,5.7),layout='constrained',gridspec_kw={'width_ratios':[1.,1.35]})
    im=field(axs[0],psi.real/a0,(-18,18),(-18,18),r'局部格点：$\mathbf{q}_0=(0.7,0.7)$')
    colorbar(fig,im,axs[0],r'$\mathrm{Re}\,\psi/A_0$')
    mask=np.abs(X)<=22; line=psi[N//2,mask]
    axs[1].plot(X[mask],line.real/a0,'o-',ms=4.5,lw=1.5,color=BLUE,label='实际格点样本')
    axs[1].plot(X[mask],np.abs(line)/a0,'--',color=ORANGE,lw=1.8,label='振幅包络')
    axs[1].plot(X[mask],-np.abs(line)/a0,'--',color=ORANGE,lw=1.8)
    axs[1].axhline(0,color='#758590',lw=.7); axs[1].grid(alpha=.15)
    axs[1].set(xlabel=r'$x/a$  ($y=0$)',ylim=(-1.1,1.1),xlim=(-22,22),title=r'$\lambda_x/a=2\pi/0.7\approx8.98$')
    axs[1].legend(loc='upper right')
    save(fig,'w06_lattice_sampling','波长与真实格点采样',
         'τ=0，q₀=(0.7,0.7)，σ=10a。左图逐格显示振幅实部；右图每个圆点是一个实际格点，连线只帮助读图。沿 x 每个载波周期约9个格点，二维波峰沿对角方向排列。增大 N 扩大周期盒，并不改变格距或每个波长的采样数；波的可见度来自选取合适局部视窗并画出相位敏感振幅。')


def save_gif(fig, update, stem,title,caption):
    frames=[]
    for t in ANIMATION_TIMES:
        update(float(t)); fig.canvas.draw()
        image=Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[...,:3])
        frames.append(image.convert('P',palette=Image.Palette.ADAPTIVE,colors=128))
    path=ROOT/f'{stem}.gif'; durations=[95]*len(frames); durations[-1]=1100
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=durations,
                   loop=0,optimize=False,disposal=2)
    plt.close(fig)
    with Image.open(path) as im:
        for k in range(im.n_frames): im.seek(k); im.load()
        nframes=im.n_frames
    ITEMS.append({'id':stem,'title':title,'caption':caption,'files':{'gif':path.name},
                  'frame_count':nframes,'frames_decoded':True})


def make_animations(initials):
    a0=float(np.abs(initials['x_eta1']).max()); p0=a0*a0
    fig,axs=plt.subplots(1,2,figsize=(12.8,4.6),dpi=105,layout='constrained',sharey=True)
    psi=initials['x_eta1']; limits=((-35,83),(-34,34))
    re=field(axs[0],psi.real/a0,*limits,r'振幅实部  $\tau=0$')
    pr=field(axs[1],np.abs(psi)**2/p0,*limits,r'翻转概率  $\tau=0$',True)
    colorbar(fig,re,axs[0],r'$\mathrm{Re}\,\psi/A_0$'); colorbar(fig,pr,axs[1],r'$|\psi|^2/P_0$')
    def update(t):
        psi=cm.propagate(initials['x_eta1'],t,1.)
        re.set_data(region(psi.real/a0,*limits)); pr.set_data(region(np.abs(psi)**2/p0,*limits))
        axs[0].set_title(rf'振幅实部  $\tau={t:g}$'); axs[1].set_title(rf'翻转概率  $\tau={t:g}$')
    save_gif(fig,update,'w07_wave_probability_animation','振幅实部与概率：完整传播过程',
             'N=512，q₀=(0.7,0)，σ=10a，η=1，τ=0…60。两图是同一复态，色标分别为固定 Reψ/A₀∈[−1,1]、P/P₀∈[0,1]。无逐帧归一化、无相位重置、无热图插值。')

    fig,axs=plt.subplots(1,2,figsize=(12.0,5.7),dpi=105,layout='constrained',sharey=True)
    limits=((-35,83),(-35,79)); psi=initials['diagonal_eta1']
    ims=[field(ax,psi.real/a0,*limits,rf'$\eta={eta:g}$,  $\tau=0$') for ax,eta in zip(axs,[1.,.3])]
    colorbar(fig,ims[-1],list(axs),r'$\mathrm{Re}\,\psi/A_0$')
    def update2(t):
        for ax,im,eta in zip(axs,ims,[1.,.3]):
            psi=cm.propagate(initials['diagonal_eta1'],t,eta)
            im.set_data(region(psi.real/a0,*limits)); ax.set_title(rf'$\eta={eta:g}$,  $\tau={t:g}$')
    save_gif(fig,update2,'w08_anisotropy_animation','交换各向异性改变波包传播方向',
             '两侧均 q₀=(0.7,0.7)、σ=10a，分别 η=1 与0.3；τ=0…60。固定初始峰值 A₀，统一色标 Reψ/A₀∈[−1,1]。热图严格取实际格点值；未改变格距。')


def build_data():
    configs={'x_eta1':((.7,0.),1.),'x_eta03':((.7,0.),.3),
             'diagonal_eta1':((.7,.7),1.),'diagonal_eta03':((.7,.7),.3)}
    states={}; initials={}; archive={'x':X,'snapshot_times':TIMES,'trajectory_times':ANIMATION_TIMES}
    checks={'parameters':PARAMETERS,'gaussians':{},'delta':{},'all_passed':False}
    for key,(q0,eta) in configs.items():
        psi0=cm.gaussian(N,SIGMA,q0); initials[key]=psi0
        snaps=np.stack([cm.propagate(psi0,t,eta) for t in TIMES]); states[key]=snaps
        archive[key+'_psi']=snaps
        tr=cm.trajectory(psi0,ANIMATION_TIMES,eta)
        for name,values in tr.items(): archive[key+'_trajectory_'+name]=values
        spec=cm.spectral_stats(psi0,eta)
        expected_center=ANIMATION_TIMES[:,None]*spec['velocity'][None,:]
        expected_var=SIGMA**2+ANIMATION_TIMES[:,None]**2*spec['velocity_variance'][None,:]
        center=np.stack([tr['cx'],tr['cy']],axis=-1)
        variance=np.stack([tr['wx']**2,tr['wy']**2],axis=-1)
        psi1024=cm.propagate(cm.gaussian(1024,SIGMA,q0),60.,eta)
        central=psi1024[256:768,256:768]
        check={'max_norm_error':float(np.max(np.abs(tr['norm']-1))),
               'max_probability_center_error_a':float(np.max(np.abs(center-expected_center))),
               'max_probability_variance_error_a2':float(np.max(np.abs(variance-expected_var))),
               'N512_vs_N1024_amplitude_Linf_tau60':float(np.max(np.abs(snaps[-1]-central))),
               'max_edge_probability':float(tr['edge_mass'].max()),
               'initial_amplitude_peak':float(np.abs(psi0).max()),
               'initial_probability_peak':float(np.max(np.abs(psi0)**2)),
               'exact_spectral_mean_velocity':spec['velocity'],
               'carrier_group_velocity':[np.sin(q0[0]),eta*np.sin(q0[1])],
               'final_center_a':center[-1], 'final_rms_width_a':np.sqrt(variance[-1])}
        check['passed']=bool(check['max_norm_error']<1e-12 and check['max_probability_center_error_a']<1e-10
                             and check['max_probability_variance_error_a2']<1e-9
                             and check['N512_vs_N1024_amplitude_Linf_tau60']<1e-12)
        checks['gaussians'][key]=check
    psi=cm.propagate(cm.delta(N),24.,1.); archive['delta_tau24']=psi
    xx,yy=np.meshgrid(X,X,indexing='xy')
    analytical=np.exp(-2j*24.)*(1j)**(xx+yy)*jv(xx,24.)*jv(yy,24.)
    m=cm.moments(psi)
    checks['delta']={'tau':24.,'bessel_amplitude_Linf':float(np.max(np.abs(psi-analytical))),
                     'norm_error':abs(m['norm']-1),'center_error_a':max(abs(m['cx']),abs(m['cy'])),
                     'variance_error_a2':max(abs(m['wx']**2-24**2/2),abs(m['wy']**2-24**2/2)),
                     'max_real_amplitude':float(np.abs(psi.real).max()),
                     'max_probability':float(np.abs(psi).max()**2)}
    checks['delta']['passed']=bool(checks['delta']['bessel_amplitude_Linf']<1e-12 and checks['delta']['variance_error_a2']<1e-9)
    checks['all_passed']=all(c['passed'] for c in checks['gaussians'].values()) and checks['delta']['passed']
    assert checks['all_passed'],checks
    np.savez_compressed(ROOT/'dense_wave_data.npz',**archive)
    write_json(ROOT/'checks.json',checks)
    return states,initials,archive


def main():
    setup()
    states,initials,data=build_data()
    make_static(states,data)
    make_animations(initials)
    write_json(ROOT/'manifest.json',{'parameters':PARAMETERS,'items':ITEMS,
               'data':'dense_wave_data.npz','checks':'checks.json',
               'generator':'generate_dense_wave.py'})
    print(f'Created {len(ITEMS)} assets; checks passed.')


if __name__=='__main__': main()
