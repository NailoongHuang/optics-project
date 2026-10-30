"""Render the existing verified simulations in physical, familiar notation.

Internal stored arrays retain their original dimensionless representation.
Only labels and analytical equations change. Source files are not overwritten.
"""
from pathlib import Path
import json,hashlib,re
import numpy as np
import sympy as sp

OUT=Path(__file__).resolve().parent
OLD=OUT.parent/'curvature-design'
source=(OLD/'generate_design.py').read_text(encoding='utf-8')
source=source[:source.index('    formulae=[')]+source[source.index('\ndef solve'):]
source=source.replace("['png','svg','pdf']","['png','svg']")
source=source.replace("rf'能带 $e=\\varepsilon/J_x$，$\\eta={eta:g}$'", "rf'能带 $\\varepsilon/J_x$，$J_y/J_x={eta:g}$'")
source=source.replace("label=r'$e=\\varepsilon/J_x$'", "label=r'$\\varepsilon/J_x$'")
source=source.replace("label=r'$e$'", "label=r'$\\varepsilon/J_x$'")
source=source.replace("xlabel=r'$\\delta q_x$'", "xlabel=r'$(k_x-k_{x0})a$'")
source=source.replace("ylabel=r'$\\delta q_y$'", "ylabel=r'$(k_y-k_{y0})a$'")
source=source.replace("rf'$\\eta={eta:g},\\ \\tau=180$'", "rf'$J_y/J_x={eta:g},\\ t=180\\hbar/J_x$'")
source=source.replace("label=rf'$\\tau={t}$'", "label=rf'$t={t}\\hbar/J_x$'")
source=source.replace("label=r'$-\\delta q^3/6$'", "label=r'$-a^3(k_x-\\pi/(2a))^3/6$'")
source=source.replace("xlabel=r'$\\delta q$'", "xlabel=r'$(k_x-\\pi/(2a))a$'")
source=source.replace("ylabel='减去常数与一阶项后的 e'", "ylabel=r'减去常数与一阶项后的 $\\varepsilon/J_x$'")
source=source.replace("label=r'$\\tau\\,\\delta e\\quad(\\mathrm{rad})$'", "label='剩余谱相位（rad）'")
source=source.replace("rf'$\\tau={t:.0f}$'", "rf'$t={t:.0f}\\hbar/J_x$'")
source=source.replace(r'\bar x',r'\langle x\rangle').replace(r'\bar y',r'\langle y\rangle')
source=source.replace("axs[i].imshow(k,", "im=axs[i].imshow(k,")
source=source.replace("    save(fig,'g05_spectral_support'", "    fig.colorbar(im,ax=axs,shrink=.8,label=r'$\\kappa_{\\mathrm{G}}$')\n    save(fig,'g05_spectral_support'")
ns={'__file__':str(Path(__file__).resolve()),'__name__':'notation_plotting'}
exec(compile(source,str(OLD/'generate_design.py'),'exec'),ns)
plt=ns['plt'];save=ns['save'];INK=ns['INK']

def equation(key,expression,size=30):
    expression=re.sub(r'\\(mathbf|mathcal|mathrm|mathbb)\s+([A-Za-z])',lambda m:'\\'+m[1]+'{'+m[2]+'}',expression)
    fig=plt.figure(figsize=(16,2))
    fig.text(.01,.5,expression,fontsize=size,va='center',color=INK)
    save(fig,key,'Physical-variable equation','位置x,y与波矢kx,ky均为物理变量，a为晶格间距，hbar显式保留。')

def equations():
    equation('eq_dispersion',r'$\varepsilon(k_x,k_y)\equiv E_{\mathbf k}-E_F=J_x[1-\cos(k_xa)]+J_y[1-\cos(k_ya)]$')
    equation('eq_lattice_H',r'$H=-J_x\sum_{x,y}\mathbf S_{x,y}\!\cdot\!\mathbf S_{x+a,y}-J_y\sum_{x,y}\mathbf S_{x,y}\!\cdot\!\mathbf S_{x,y+a}$')
    equation('eq_action',r'$(H-E_F)|x,y\rangle=(J_x+J_y)|x,y\rangle-\frac{J_x}{2}(|x+a,y\rangle+|x-a,y\rangle)$'+'\n'+r'$\qquad\qquad-\frac{J_y}{2}(|x,y+a\rangle+|x,y-a\rangle)$',25)
    equation('eq_state',r'$|\Psi(t)\rangle=e^{-iE_Ft/\hbar}\sum_{x,y}\psi(x,y,t)|x,y\rangle$')
    equation('eq_eom',r'$i\hbar\frac{\partial\psi(x,y,t)}{\partial t}=(J_x+J_y)\psi(x,y,t)-\frac{J_x}{2}[\psi(x+a,y,t)+\psi(x-a,y,t)]$'+'\n'+r'$\qquad\qquad-\frac{J_y}{2}[\psi(x,y+a,t)+\psi(x,y-a,t)]$',25)
    equation('eq_evolution',r'$\psi(x,y,t)=\mathcal F^{-1}\!\left\{\mathcal F[\psi(x,y,0)]\exp\!\left[-\frac{i\varepsilon(k_x,k_y)t}{\hbar}\right]\right\}$')
    equation('eq_initial',r'$\psi(x,y,0)=\mathcal N\exp\!\left[-\frac{x^2+y^2}{4\sigma^2}\right]\exp[i(k_{x0}x+k_{y0}y)]$')
    equation('eq_derivatives1',r'$\frac{\partial\varepsilon}{\partial k_x}=J_xa\sin(k_xa),\qquad\frac{\partial\varepsilon}{\partial k_y}=J_ya\sin(k_ya)$')
    equation('eq_derivatives2',r'$\frac{\partial^2\varepsilon}{\partial k_x^2}=J_xa^2\cos(k_xa),\quad\frac{\partial^2\varepsilon}{\partial k_y^2}=J_ya^2\cos(k_ya),\quad\frac{\partial^2\varepsilon}{\partial k_x\partial k_y}=0$',28)
    equation('eq_curvature',r'$\kappa_{\mathrm G}(k_x,k_y)=\frac{(J_y/J_x)\cos(k_xa)\cos(k_ya)}{[1+\sin^2(k_xa)+(J_y/J_x)^2\sin^2(k_ya)]^2}$',34)
    equation('eq_zeros',r'$\kappa_{\mathrm G}=0\quad\Longleftrightarrow\quad k_x=\frac{\pi}{2a}+\frac{m\pi}{a}\quad\mathrm{or}\quad k_y=\frac{\pi}{2a}+\frac{n\pi}{a},\quad m,n\in\mathbb Z$',28)
    equation('eq_reference',r'$\psi_{\rm ref}(x,y,t)=\psi(x-\langle v_x\rangle t,\ y-\langle v_y\rangle t,\ 0)$'+'\n'+r'$F(t)=\left|\sum_{x,y}\psi_{\rm ref}^{*}(x,y,t)\psi(x,y,t)\right|^2$',25)
    equation('eq_cubic',r'$\varepsilon(k_x,k_y)-(J_x+J_y)-J_xa\!\left(k_x-\frac{\pi}{2a}\right)-J_ya\!\left(k_y-\frac{\pi}{2a}\right)$'+'\n'+r'$\qquad=-\frac{a^3}{6}\!\left[J_x\!\left(k_x-\frac{\pi}{2a}\right)^3+J_y\!\left(k_y-\frac{\pi}{2a}\right)^3\right]+\cdots$',25)

def schematic():
    fig,ax=plt.subplots(figsize=(5.9,5.1),layout='constrained')
    for y in range(-2,3):ax.plot([-2,2],[y,y],color='#246B9A',lw=1.7)
    for x in range(-2,3):ax.plot([x,x],[-2,2],color='#C95F42',lw=1.7,ls='--')
    for y in range(-2,3):
        for x in range(-2,3):
            ax.annotate('',(x+.22,y),(x-.22,y),arrowprops=dict(arrowstyle='-|>',color=INK,lw=1.6))
    ax.scatter([0],[0],c='#9D2758',s=80,zorder=5)
    ax.annotate(r'$|x,y\rangle$',(0,0),xytext=(.35,.5),arrowprops=dict(arrowstyle='-',color='#9D2758'),color='#9D2758',fontsize=18)
    ax.annotate('',(-1,-2.45),(-2,-2.45),arrowprops=dict(arrowstyle='<->',color=INK));ax.text(-1.55,-2.78,r'$a$',fontsize=20)
    ax.text(.55,2.32,r'$J_x$',color='#246B9A',fontsize=22);ax.text(2.2,.8,r'$J_y$',color='#C95F42',fontsize=22)
    ax.set(xlim=(-2.6,2.8),ylim=(-3,2.8),xlabel=r'$x$',ylabel=r'$y$');ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
    save(fig,'g_lattice','局部交换晶格','位置用x,y表示，相邻格点相差晶格间距a，横向与纵向交换分别为Jx与Jy。')

def verify_units():
    kx,ky,a,Jx,Jy=sp.symbols('kx ky a Jx Jy',positive=True)
    eps=Jx*(1-sp.cos(kx*a))+Jy*(1-sp.cos(ky*a))
    numerator=eps.diff(kx,2)*eps.diff(ky,2)-eps.diff(kx,ky)**2
    denom=Jx**2*a**4*(1+(eps.diff(kx)/(Jx*a))**2+(eps.diff(ky)/(Jx*a))**2)**2
    expected=(Jy/Jx)*sp.cos(kx*a)*sp.cos(ky*a)/(1+sp.sin(kx*a)**2+(Jy/Jx)**2*sp.sin(ky*a)**2)**2
    assert sp.simplify(numerator/denom-expected)==0
    assert eps.diff(kx,2).subs(kx,sp.pi/(2*a))==0
    return dict(passed=True,scaled_graph_axes='(kx*a, ky*a, epsilon/Jx)',physical_derivative_curvature_residual=0,
        units=dict(position='x,y',wavevector='kx,ky',energy='epsilon',time='t',plot_time='t in hbar/Jx'),
        data_sha256=hashlib.sha256((OLD/'design_data.npz').read_bytes()).hexdigest(),
        old_to_physical=dict(q='a*k',e='epsilon/Jx',tau='Jx*t/hbar',n='x/a',s='sigma/a',eta='Jy/Jx'),
        evidence='Rendering reuses the saved complex wavefields; phase epsilon*t/hbar equals stored e*tau exactly.')

def main():
    ns['geometry_figures']();equations();schematic()
    dataset=json.loads((OLD/'chart_data.json').read_text())['cases'];arrays=np.load(OLD/'design_data.npz')
    cases={};controls={}
    for key,r in dataset.items():
        N=r['N'];x=np.arange(-N//2,N//2);psi0=ns['gaussian'](N,r['sigma_a'],r['q0']);A=np.fft.fft2(psi0)
        _,_,_,kx,ky=ns['grid'](N);eps=ns['energy'](kx,ky,r['eta'])
        snaps={i:arrays[key+f'_psi_t{int(t)}'] for i,t in [(0,0),(30,90),(60,180)]} if N==512 else {}
        c=dict(result=r,snaps=snaps,x=x,psi0=psi0,A=A,eps=eps,A0=float(abs(psi0).max()))
        (cases if N==512 else controls)[key]=c
        if N==512:assert np.max(abs(snaps[0]-psi0))<1e-13
    ns['packet_figures'](cases,controls);ns['animation'](cases,True,'g13_real_animation')
    captions={
      'g00_cover':'能带能量epsilon/Jx与解析零曲率轨迹。坐标kx a/pi、ky a/pi。',
      'g01_multibz_eta1':'Jy/Jx=1，扩展3x3布里渊区。左epsilon/Jx，右无量纲图面(kx a,ky a,epsilon/Jx)的高斯曲率，范围正负1。',
      'g02_multibz_eta03':'Jy/Jx=0.3，能量色标与上一图相同，曲率色标改为正负0.3。',
      'g03_zero_locus_band':'左侧只画精确零曲率轨迹上的epsilon/Jx，线外留空。右侧为对应完整曲率。',
      'g04_candidates':'中心波矢A=(0.7/a,0.7/a)，B=(pi/(2a),0.7/a)，C=(pi/(2a),pi/(2a))。',
      'g05_spectral_support':'局部波矢坐标为(kx-kx0)a和(ky-ky0)a。圆线表示初始谱功率相对峰值0.1、0.5、0.9。sigma=6a，Delta k=1/(12a)。背景曲率正负0.3。',
      'g06_initial_carriers':'t=0，sigma=6a，Jy/Jx=1。总概率1，相同初始包络，固定A0=max|psi(x,y,0)|。',
      'g07_final_probability':'t=180 hbar/Jx，sigma=6a，Jy/Jx=1。各自质心坐标，固定共同P0=maxP(x,y,0)，虚线半径2sigma。',
      'g08_final_real':'t=180 hbar/Jx，sigma=6a，Jy/Jx=1。固定相位与A0。',
      'g10_anisotropic_design':'B中心，固定sigma=6a和t=180 hbar/Jx，比较Jy/Jx=1和0.3。',
      'g09_higher_order_limit':'C中心，sigma=4a，t=0,180,360 hbar/Jx。右图减去常数与一次项后的epsilon/Jx，横轴(kx-pi/(2a))a，ky=pi/(2a)。',
      'g12_phase_budget':'t=180 hbar/Jx，减去按谱平均速度平移所需的相位及谱平均公共相位，所有面板正负3rad。',
      'g13_real_animation':'三中心，同sigma=6a，t=0至180 hbar/Jx，共61帧，各自质心坐标，固定初始相位和A0。'
    }
    for item in ns['items']:
        item['caption']=captions.get(item['id'],item['caption'])
    checks=verify_units();ns['write']('checks.json',checks)
    ns['write']('manifest.json',dict(items=ns['items'],source_data=str(OLD/'design_data.npz'),checks=checks))
    print('Completed physical-notation figures and unit verification',flush=True)

if __name__=='__main__':main()
