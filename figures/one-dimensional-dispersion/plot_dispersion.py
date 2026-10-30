"""Plot four exact 1D dispersion examples for rigid packet propagation.

All coordinates are dimensionless. Shading denotes allowed spectral support,
not the amplitude of a rectangular spectrum. A smooth compactly supported
spectrum can be chosen inside each band. No propagation simulation is claimed.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
K = np.linspace(-2.5, 2.5, 2401)
GREEN = '#147D64'
RED = '#B84B49'
GREY = '#9CA4AC'
INK = '#202F3D'


def local_affine(k):
    return 3 + .7 * k + .25 * np.maximum(np.abs(k) - 1.1, 0)**4


cases = [
    dict(title='① 可以：直线色散', subtitle=r'$\omega=3+0.7k$',
         fn=lambda k: 3+.7*k, band=(-.8,.8), color=GREEN,
         ylim=(.7,5.8), note='使用的整段频谱，斜率完全相同。'),
    dict(title='② 可以：中间有一段严格直线', subtitle='示意模型：两侧弯，中间完全直',
         fn=local_affine, band=(-.8,.8), color=GREEN,
         ylim=(.7,5.8), note='频谱全放在直线段内；不使用弯曲部分。'),
    dict(title='③ 不可以：抛物线色散', subtitle=r'$\omega=1+0.45k^2$',
         fn=lambda k: 1+.45*k*k, band=(.55,1.85), color=RED,
         ylim=(.3,4.6), note='波包可以移动，但不同成分会跑散。'),
    dict(title='④ 不可以：一点曲率为零', subtitle=r'$\omega=3+\sin k$',
         fn=lambda k: 3+np.sin(k), band=(-.9,.9), color=RED,
         ylim=(1.5,4.5), note='一个点“变直”，不等于一整段是直线。'),
]


def main():
    style = {
        'font.family': 'sans-serif',
        'font.sans-serif': ['Microsoft YaHei', 'DejaVu Sans'],
        'font.size': 15,
        'axes.unicode_minus': False,
        'mathtext.fontset': 'dejavusans',
        'svg.fonttype': 'path',
    }
    with plt.rc_context(style):
        fig, axes = plt.subplots(2,2,figsize=(12.8,10.4))
        fig.patch.set_facecolor('white')
        fig.subplots_adjust(left=.09,right=.965,bottom=.18,top=.80,wspace=.24,hspace=.73)
        fig.text(.055,.963,'一维：哪些色散允许局域波包严格保形地移动？',
                 fontsize=23,weight='bold',color=INK)
        fig.text(.055,.919,'彩色线 = 波包使用的那一段　　灰线 = 其余色散　　阴影 = 所选波数区间',
                 fontsize=14.5,color='#4E5E6C')
        for idx,(ax,c) in enumerate(zip(axes.flat,cases)):
            lo,hi=c['band']
            selected=np.linspace(lo,hi,700)
            ax.axvspan(lo,hi,color=c['color'],alpha=.10,zorder=0)
            ax.plot(K,c['fn'](K),color=GREY,lw=2.3,zorder=2)
            ax.plot(selected,c['fn'](selected),color=c['color'],lw=4.3,zorder=3,
                    solid_capstyle='round')
            ax.scatter([lo,hi],c['fn'](np.array([lo,hi])),s=28,color=c['color'],zorder=4)
            ax.set_xlim(-2.5,2.5)
            ax.set_ylim(*c['ylim'])
            ax.set_xticks([-2,-1,0,1,2])
            ax.set_yticks([1,3,5] if idx<2 else ([1,2,3,4] if idx==2 else [2,3,4]))
            ax.tick_params(labelsize=12,length=3,color='#A5AFB8',labelcolor='#53616D')
            ax.spines[['top','right']].set_visible(False)
            ax.spines[['left','bottom']].set_color('#8895A0')
            ax.grid(axis='y',color='#DFE4E8',lw=.65,zorder=-1)
            ax.set_xlabel(r'波数 $k$',fontsize=14,labelpad=5,color=INK)
            ax.set_ylabel(r'频率 $\omega$',fontsize=14,labelpad=7,color=INK)
            ax.text(0,1.20,c['title'],transform=ax.transAxes,fontsize=17,
                    weight='bold',color=c['color'])
            ax.text(0,1.07,c['subtitle'],transform=ax.transAxes,fontsize=13.5,color='#53616D')
            ax.text(0,-.31,c['note'],transform=ax.transAxes,fontsize=13.4,color=INK)
            if idx==1:
                ax.annotate('外侧弯曲也没关系',xy=(2.23,float(local_affine(2.23))),
                            xytext=(-2.28,5.08),fontsize=12,color='#53616D',
                            arrowprops=dict(arrowstyle='->',color='#7B8995',lw=1.1),
                            bbox=dict(fc='white',ec='none',alpha=.92,pad=2))
            if idx==3:
                tangent_k=np.linspace(-1.23,1.23,300)
                ax.plot(tangent_k,3+tangent_k,color='#5D6772',lw=1.35,ls=(0,(5,4)),zorder=2)
                ax.scatter([0],[3],s=44,facecolor='white',edgecolor=RED,lw=1.8,zorder=5)
                ax.annotate(r'$k=0$：曲率为零',xy=(0,3),xytext=(-2.28,4.15),
                            fontsize=12,color=INK,
                            arrowprops=dict(arrowstyle='->',color='#7B8995',lw=1.1),
                            bbox=dict(fc='white',ec='none',alpha=.9,pad=1))
                ax.text(.7,.15,'虚线是切线，曲线没有与它整段重合',
                        transform=ax.transAxes,fontsize=11.5,color='#53616D',ha='center',
                        bbox=dict(fc='white',ec='none',alpha=.92,pad=2))
        fig.text(.055,.043,'判据：所选频谱占有一段宽度，并且这一整段的色散严格为斜直线。',
                 fontsize=17,weight='bold',color=INK)
        fig.text(.055,.012,'阴影只表示频谱范围；可在其中选光滑频谱包络。参数均为无量纲示意值。',
                 fontsize=12.5,color='#53616D')
        fig.savefig(OUT/'one-dimensional-dispersion.png',dpi=180,facecolor='white')
        fig.savefig(OUT/'one-dimensional-dispersion.svg',facecolor='white')
        plt.close(fig)

    # Exact structural assertions plus a sampled numerical sanity check.
    selected=np.linspace(-.8,.8,1001)
    residual=local_affine(selected)-(3+.7*selected)
    assert np.max(np.abs(residual))==0
    assert abs(float(local_affine(2)-(3+.7*2)))>0
    checks={
        'local_affine_residual_in_selected_band':float(np.max(np.abs(residual))),
        'parabolic_velocity_range_in_band':[.9*.55,.9*1.85],
        'sine_velocity_at_center':1.0,
        'sine_velocity_at_band_edge':float(np.cos(.9)),
        'scope':'Static plots of exact illustrative functions; not time-propagation simulations.',
        'spectral_band_semantics':'Support range, not a rectangular amplitude spectrum.'
    }
    (OUT/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(checks,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
