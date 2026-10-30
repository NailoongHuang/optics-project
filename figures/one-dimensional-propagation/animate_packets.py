"""Fourier propagation of one common finite-bandwidth packet.

No time-stepping approximation: A(k,t)=A(k,0) exp(-i omega(k)t).
FFT implements a large periodic box; doubled-box and doubled-grid checks
bound its influence on the displayed central region. All units dimensionless.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

OUT=Path(__file__).resolve().parent
BAND=2.2
TMAX=18.
TIMES=np.linspace(0,TMAX,121)
CASES=[
    dict(id='01_linear', title='直线色散：波包只平移', formula=r'$\omega(k)=4+k$',
         omega=lambda k:4+k, velocity=lambda k:np.ones_like(k), color='#16856C'),
    dict(id='02_quadratic', title='抛物线色散：波包展宽、变矮', formula=r'$\omega(k)=4+k+0.5k^2$',
         omega=lambda k:4+k+.5*k*k, velocity=lambda k:1+k, color='#C75B40'),
    dict(id='03_inflection', title='拐点附近：仍然会变形', formula=r'$\omega(k)=4+\sin k$',
         omega=lambda k:4+np.sin(k), velocity=lambda k:np.cos(k), color='#7256B2'),
    dict(id='04_local_linear', title='局部直线：频谱完全落在直线段内',
         formula=r'$\omega(k)=4+k+0.25\,[\max(|k|-2.4,0)]^4$',
         omega=lambda k:4+k+.25*np.maximum(np.abs(k)-2.4,0)**4,
         velocity=lambda k:1+np.sign(k)*np.maximum(np.abs(k)-2.4,0)**3,
         color='#2779A8'),
]


def initial(N=8192,L=512.):
    dx=L/N
    x=(np.arange(N)-N//2)*dx
    k=2*np.pi*np.fft.fftfreq(N,d=dx)
    A=np.zeros(N,complex)
    z=k/BAND
    mask=np.abs(z)<1
    A[mask]=np.exp(-1/(1-z[mask]**2))
    psi=np.fft.fftshift(np.fft.ifft(A))
    A/=np.sqrt(np.sum(np.abs(psi)**2)*dx)
    psi=np.fft.fftshift(np.fft.ifft(A))
    return x,k,A,np.abs(psi)**2,dx


def density(k,A,omega,t):
    # Only occupied modes are evaluated, so remote high-k phases are irrelevant.
    phase=np.zeros_like(k)
    occupied=np.abs(A)>0
    phase[occupied]=omega(k[occupied])*t
    return np.abs(np.fft.fftshift(np.fft.ifft(A*np.exp(-1j*phase))))**2


def translated(k,A,v,t):
    return np.abs(np.fft.fftshift(np.fft.ifft(A*np.exp(-1j*k*v*t))))**2


def moments(x,rho,dx):
    norm=rho.sum()*dx
    center=np.sum(x*rho)*dx/norm
    width=np.sqrt(np.sum((x-center)**2*rho)*dx/norm)
    return float(norm),float(center),float(width)


def verify(x,k,A,rho0,dx):
    checks=[]
    _,_,w0=moments(x,rho0,dx)
    xf,kf,Af,rhof,dxf=initial(N=16384,L=512.)
    xb,kb,Ab,rhob,dxb=initial(N=16384,L=1024.)
    roi=np.abs(x)<100
    for c in CASES:
        v=float(np.sum(np.abs(A)**2*c['velocity'](k))/np.sum(np.abs(A)**2))
        rho=density(k,A,c['omega'],TMAX)
        rref=translated(k,A,v,TMAX)
        norm,center,width=moments(x,rho,dx)
        fine=density(kf,Af,c['omega'],TMAX)[::2]
        large=density(kb,Ab,c['omega'],TMAX)[4096:12288]
        initial_large=rhob[4096:12288]
        rec=dict(case=c['id'],group_velocity_mean=v,initial_rms_width=w0,
                 final_rms_width=width,width_ratio=width/w0,
                 relative_norm_error=abs(norm-1),center_error=abs(center-v*TMAX),
                 relative_density_shape_error=float(np.linalg.norm(rho-rref)/np.linalg.norm(rho0)),
                 doubled_grid_max_density_error=float(np.max(np.abs(fine[roi]-rho[roi]))),
                 doubled_box_max_density_error=float(np.max(np.abs(large[roi]-rho[roi]))),
                 doubled_box_initial_max_error=float(np.max(np.abs(initial_large[roi]-rho0[roi]))),
                 outer_box_mass=float(rho[np.abs(x)>200].sum()*dx))
        assert rec['relative_norm_error']<1e-12,rec
        assert rec['doubled_grid_max_density_error']<1e-10,rec
        assert rec['doubled_box_max_density_error']<1e-7,rec
        assert rec['outer_box_mass']<1e-9,rec
        if c['id'] in ('01_linear','04_local_linear'):
            assert rec['relative_density_shape_error']<1e-11,rec
        checks.append(rec)
    (OUT/'checks.json').write_text(json.dumps(dict(
        model='i dt psi=omega(-i dx) psi',N=len(x),L=512,band_limit=BAND,
        tmax=TMAX,frames=len(TIMES),initial_spectrum='exp[-1/(1-(k/B)^2)] inside |k|<B, zero outside',
        same_initial_spectrum_for_all_cases=True,per_frame_peak_renormalization=False,
        results=checks),ensure_ascii=False,indent=2),encoding='utf-8')
    return checks


def render_case(c,x,k,A,rho0,dx,check):
    vmax=check['group_velocity_mean']
    peak0=rho0.max()
    fig,axes=plt.subplots(1,2,figsize=(11,5.3),dpi=105,
                          gridspec_kw={'width_ratios':[1.5,1]})
    fig.subplots_adjust(left=.075,right=.975,bottom=.27,top=.72,wspace=.22)
    fig.text(.06,.93,c['title'],fontsize=18.5,weight='bold',color='#243444')
    fig.text(.06,.871,c['formula'],fontsize=15,color='#536372')
    label=fig.text(.73,.875,'',fontsize=14,color='#243444')
    axes[0].set_title('固定坐标：看它怎样向前走',fontsize=13.5,pad=12)
    axes[1].set_title('跟随波包中心：只看形状变化',fontsize=13.5,pad=12)
    lines=[]
    for i,ax in enumerate(axes):
        ax.set_xlim((-22,58) if i==0 else (-20,20))
        ax.set_ylim(-.015,1.09)
        ax.set_xlabel('位置 x' if i==0 else '相对中心的位置',fontsize=13)
        ax.spines[['top','right']].set_visible(False)
        ax.spines[['left','bottom']].set_color('#A0ABB5')
        ax.set_yticks([0,.5,1])
        ax.tick_params(labelsize=11,colors='#64717D')
        ax.grid(axis='y',color='#E4E8EC',lw=.7)
        line,=ax.plot([],[],color=c['color'],lw=2.6,zorder=3)
        ref,=ax.plot([],[],color='#7A8590',lw=1.65,ls=(0,(5,4)),zorder=4)
        lines.append((line,ref))
    axes[0].set_ylabel('强度（以初始峰值为 1）',fontsize=12.5)
    fig.text(.06,.10,'彩色：实际波包　　灰虚线：初始波形原样平移的参考',fontsize=12.5,color='#425462')
    fig.text(.06,.035,'四种情况使用同一初始波包；纵轴固定，不逐帧放大。时间与位置均为无量纲。',fontsize=11,color='#677581')
    frames=[]
    for j,t in enumerate(TIMES):
        rho=density(k,A,c['omega'],t)
        ref=translated(k,A,vmax,t)
        center=vmax*t
        _,_,width=moments(x,rho,dx)
        lines[0][0].set_data(x,rho/peak0)
        lines[0][1].set_data(x,ref/peak0)
        lines[1][0].set_data(x-center,rho/peak0)
        lines[1][1].set_data(x,rho0/peak0)
        label.set_text(f't = {t:4.1f}   宽度 ×{width/check["initial_rms_width"]:.2f}')
        fig.canvas.draw()
        frame=Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:,:,:3].copy())
        frames.append(frame)
        if j in (0,60,120):
            frame.save(OUT/f'{c["id"]}_t{t:04.1f}.png')
    durations=[75]*len(frames)
    durations[0]=650
    durations[-1]=1400
    path=OUT/f'{c["id"]}.gif'
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=durations,
                   loop=0,optimize=False,disposal=2)
    plt.close(fig)
    print(f'SAVED {path.name}: {path.stat().st_size/1024/1024:.2f} MiB',flush=True)


def main():
    x,k,A,rho0,dx=initial()
    checks=verify(x,k,A,rho0,dx)
    print(json.dumps(checks,ensure_ascii=False,indent=2),flush=True)
    with plt.rc_context({'font.family':'sans-serif','font.sans-serif':['Microsoft YaHei','DejaVu Sans'],
                         'axes.unicode_minus':False,'mathtext.fontset':'dejavusans'}):
        for c,check in zip(CASES,checks):
            render_case(c,x,k,A,rho0,dx,check)


if __name__=='__main__':
    main()
