"""Band-surface Gaussian curvature and controlled one-magnon packet design.

Surface embedding: R(qx,qy)=(qx,qy,e), e=epsilon/Jx, q=k*a, eta=Jy/Jx>0.
Physical packet widths are given in a; lattice spacing is never changed.
"""
from pathlib import Path
import sys,json
import numpy as np
import sympy as sy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,TwoSlopeNorm
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle
from PIL import Image

OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parent))
from common import gaussian,energy,grid,moments,spectral_stats
plt.rcParams.update({'font.sans-serif':['Microsoft YaHei','DejaVu Sans'],'font.size':16,
 'axes.titlesize':20,'axes.labelsize':18,'xtick.labelsize':13,'ytick.labelsize':13,
 'axes.unicode_minus':False,'svg.fonttype':'path','pdf.fonttype':42,'figure.facecolor':'white'})
COL=['#246B9A','#D16143','#27816E']
ZERO='#158453';INK='#203648'
Q0={'A':(.7,.7),'B':(np.pi/2,.7),'C':(np.pi/2,np.pi/2)}
LABEL={'A':'A：普通点','B':'B：单条零曲率线','C':'C：零曲率交点'}
items=[];raw={};results={};case_checks=[]

def write(name,obj):
    def conv(x):
        if isinstance(x,np.ndarray):return x.tolist()
        if isinstance(x,np.generic):return x.item()
        raise TypeError(type(x).__name__)
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=conv),encoding='utf-8')

def kap(x,y,eta=1.):
    return eta*np.cos(x)*np.cos(y)/(1+np.sin(x)**2+eta**2*np.sin(y)**2)**2

def save(fig,key,title,caption):
    files={}
    for ext in ['png','svg','pdf']:
        p=OUT/f'{key}.{ext}';fig.savefig(p,dpi=170,bbox_inches='tight',facecolor='white');files[ext]=p.name
    plt.close(fig);items.append(dict(id=key,title=title,caption=caption,files=files))
    print('Saved',key,flush=True)

def symbolic_check():
    x,y=sy.symbols('q_x q_y',real=True);eta=sy.symbols('eta',positive=True)
    e=1-sy.cos(x)+eta*(1-sy.cos(y));R=sy.Matrix([x,y,e])
    a,b=R.diff(x),R.diff(y);normal=a.cross(b)
    I=sy.Matrix([[a.dot(a),a.dot(b)],[a.dot(b),b.dot(b)]])
    II=sy.Matrix([[normal.dot(R.diff(x,2)),normal.dot(R.diff(x,y))],
                  [normal.dot(R.diff(x,y)),normal.dot(R.diff(y,2))]])/sy.sqrt(normal.dot(normal))
    expected=eta*sy.cos(x)*sy.cos(y)/(1+sy.sin(x)**2+eta**2*sy.sin(y)**2)**2
    residual=sy.simplify(II.det()/I.det()-expected)
    assert residual==0
    H=sy.hessian(e,(x,y))
    assert sy.simplify(H.det()-eta*sy.cos(x)*sy.cos(y))==0
    assert sy.simplify(expected.subs(x,sy.pi/2))==0
    assert H.subs({x:sy.pi/2,y:sy.pi/2})==sy.zeros(2)
    check=dict(status='passed',assumptions='qx,qy real; eta>0; dimensionless Euclidean graph R=(qx,qy,e)',
        reference='https://mathworld.wolfram.com/GaussianCurvature.html, Monge patch equation (15)',
        fundamental_form_residual=str(residual),curvature=str(expected),hessian=str(H),
        zero_locus='qx=pi/2+n*pi OR qy=pi/2+m*pi, n,m integers',
        crossing_gradient=str(sy.Matrix([e.diff(x),e.diff(y)]).subs({x:sy.pi/2,y:sy.pi/2})),
        crossing_cubic_coefficients=[str(e.diff(x,3).subs(x,sy.pi/2)/6),str(e.diff(y,3).subs(y,sy.pi/2)/6)],
        distinction='The Hessian controls quadratic spectral phase; its eigenvalues are not the graph surface principal curvatures in general.')
    write('checks_symbolic.json',check)
    return check

def background(ax,limit=3):
    ax.set(xlim=(-limit,limit),ylim=(-limit,limit),xlabel=r'$k_xa/\pi$',ylabel=r'$k_ya/\pi$')
    ax.set_aspect('equal');ax.set_xticks(np.arange(-limit,limit+1));ax.set_yticks(np.arange(-limit,limit+1))
    for k in [-1,1]:
        ax.axvline(k,color='#172C3B',lw=1.4,ls='--');ax.axhline(k,color='#172C3B',lw=1.4,ls='--')
    for k in np.arange(-2.5,3,.5):
        if abs(k%1-.5)<1e-12:
            ax.axvline(k,color=ZERO,lw=1.05);ax.axhline(k,color=ZERO,lw=1.05)

def point_marks(ax):
    for i,(name,q) in enumerate(Q0.items()):
        ax.scatter(q[0]/np.pi,q[1]/np.pi,s=65,c=COL[i],edgecolor='white',lw=1,zorder=10)
        ax.annotate(name,(q[0]/np.pi,q[1]/np.pi),xytext=(7,7),textcoords='offset points',color=COL[i],weight='bold',fontsize=15)

def pair_map(eta,key,zero_only=False):
    q=np.linspace(-3*np.pi,3*np.pi,1201);xx,yy=np.meshgrid(q,q)
    fig,axs=plt.subplots(1,2,figsize=(14.5,6.4),layout='constrained')
    if zero_only:
        norm=Normalize(0,4);cmap=plt.get_cmap('Greys');segs=[];values=[]
        l=np.linspace(-3*np.pi,3*np.pi,1201)
        for z in np.arange(-2.5,3,1)*np.pi:
            for axis in [0,1]:
                x=l if axis else np.full_like(l,z);y=np.full_like(l,z) if axis else l
                pts=np.column_stack([x/np.pi,y/np.pi]);segs.extend(np.stack([pts[:-1],pts[1:]],axis=1))
                values.extend((energy(x,y,eta)[:-1]+energy(x,y,eta)[1:])/2)
        im=LineCollection(segs,cmap=cmap,norm=norm,linewidths=5);im.set_array(np.asarray(values));axs[0].add_collection(im)
        axs[0].set_facecolor('#F2F4F5')
        for k in [-1,1]:axs[0].axvline(k,color='#203648',lw=1.4,ls='--');axs[0].axhline(k,color='#203648',lw=1.4,ls='--')
        axs[0].set(xlim=(-3,3),ylim=(-3,3),xlabel=r'$k_xa/\pi$',ylabel=r'$k_ya/\pi$');axs[0].set_aspect('equal')
        axs[0].set_title('仅零曲率轨迹上的能量')
    else:
        im=axs[0].imshow(energy(xx,yy,eta),extent=(-3,3,-3,3),origin='lower',cmap='Greys',vmin=0,vmax=4,interpolation='nearest')
        background(axs[0]);axs[0].set_title(rf'能带 $e=\varepsilon/J_x$，$\eta={eta:g}$')
    fig.colorbar(im,ax=axs[0],shrink=.82,pad=.025,label=r'$e=\varepsilon/J_x$')
    vmax=eta
    im2=axs[1].imshow(kap(xx,yy,eta),extent=(-3,3,-3,3),origin='lower',cmap='RdBu_r',norm=TwoSlopeNorm(0,-vmax,vmax),interpolation='nearest')
    background(axs[1]);axs[1].set_title(r'对应 Gaussian curvature $\kappa_{\mathrm{G}}$')
    fig.colorbar(im2,ax=axs[1],shrink=.82,pad=.025,label=r'$\kappa_{\mathrm{G}}$')
    save(fig,key,'扩展布里渊区：能带与高斯曲率',
      f'eta={eta:g}；范围kx a,ky a属于[-3pi,3pi]，共3×3个布里渊区。左侧为'+('严格零曲率线上的能量，线外留空。' if zero_only else '完整能带，灰度越深能量越大。')+
      f'右侧红正蓝负，颜色深浅表示曲率绝对值，色标范围±{vmax:g}。绿色为解析零曲率轨迹；黑虚线框住中心第一布里渊区。曲率针对无量纲图面(qx,qy,e)，不是Berry曲率。')

def geometry_figures():
    q=np.linspace(-3*np.pi,3*np.pi,1201);xx,yy=np.meshgrid(q,q)
    fig,ax=plt.subplots(figsize=(9,6.3),layout='constrained')
    im=ax.imshow(energy(xx,yy,1),extent=(-3,3,-3,3),origin='lower',cmap='Greys',vmin=0,vmax=4)
    background(ax);fig.colorbar(im,ax=ax,pad=.02,label=r'$\varepsilon/J_x$')
    save(fig,'g00_cover','能带与零曲率轨迹','无量纲扩展能带。绿色线为kappa_G=0的解析轨迹，黑虚线是中心第一布里渊区边界。')
    pair_map(1,'g01_multibz_eta1');pair_map(.3,'g02_multibz_eta03');pair_map(1,'g03_zero_locus_band',True)
    q=np.linspace(-np.pi,np.pi,801);xx,yy=np.meshgrid(q,q)
    fig,ax=plt.subplots(figsize=(7.6,6.5),layout='constrained')
    im=ax.imshow(energy(xx,yy,1),extent=(-1,1,-1,1),origin='lower',cmap='Greys',vmin=0,vmax=4)
    for z in [-.5,.5]:ax.axvline(z,c=ZERO,lw=1.5);ax.axhline(z,c=ZERO,lw=1.5)
    point_marks(ax);ax.set(xlabel=r'$k_xa/\pi$',ylabel=r'$k_ya/\pi$',xlim=(0,.85),ylim=(0,.85));ax.set_aspect('equal')
    fig.colorbar(im,ax=ax,pad=.02,label=r'$e$')
    save(fig,'g04_candidates','三类候选中心','A=(0.7,0.7)，B=(pi/2,0.7)，C=(pi/2,pi/2)。绿色为零曲率线，颜色对应e。三组初态只改变载波中心，统一初始概率RMS宽度6a。')
    fig,axs=plt.subplots(1,3,figsize=(14.5,4.8),layout='constrained')
    for i,(name,q0) in enumerate(Q0.items()):
        p0=gaussian(512,6,q0);power=np.fft.fftshift(abs(np.fft.fft2(p0,norm='ortho'))**2)
        q=np.fft.fftshift(2*np.pi*np.fft.fftfreq(512));mx=abs(q-q0[0])<.35;my=abs(q-q0[1])<.35
        dx=q[mx]-q0[0];dy=q[my]-q0[1];X,Y=np.meshgrid(dx,dy)
        k=kap(X+q0[0],Y+q0[1],1)
        axs[i].imshow(k,extent=(dx[0],dx[-1],dy[0],dy[-1]),origin='lower',cmap='RdBu_r',norm=TwoSlopeNorm(0,-.3,.3),aspect='equal')
        b=power[np.ix_(my,mx)];axs[i].contour(X,Y,b/b.max(),levels=[.1,.5,.9],colors=['#233B4D'],linewidths=1.3)
        if name in ['B','C']:axs[i].axvline(0,c=ZERO,lw=2)
        if name=='C':axs[i].axhline(0,c=ZERO,lw=2)
        axs[i].set(title=LABEL[name],xlabel=r'$\delta q_x$',ylabel=r'$\delta q_y$')
        axs[i].set_xlim(-.35,.35);axs[i].set_ylim(-.35,.35)
    save(fig,'g05_spectral_support','有限频谱与零曲率轨迹','背景是各候选点附近的实际曲率，同一色标±0.3。等高线为实际FFT初始谱功率的0.1、0.5、0.9相对峰值；sigma=6a，谱RMS宽度约1/12。有限带宽会覆盖曲率不为零的邻域。')
    formulae=[('formula_curvature_general',r'$\kappa_{\rm G}=\frac{e_{xx}e_{yy}-e_{xy}^2}{(1+e_x^2+e_y^2)^2}$'),
              ('formula_curvature_model',r'$\kappa_{\rm G}(q_x,q_y)=\frac{\eta\cos q_x\cos q_y}{[1+\sin^2q_x+\eta^2\sin^2q_y]^2}$'),
              ('formula_zero',r'$\kappa_{\rm G}=0\quad\Longleftrightarrow\quad q_x=\frac{\pi}{2}+n\pi\ \ \mathrm{or}\ \ q_y=\frac{\pi}{2}+m\pi$')]
    for key,eq in formulae:
        fig=plt.figure(figsize=(14,1.7));fig.text(.02,.48,eq,fontsize=29,va='center',color=INK)
        save(fig,key,'曲率解析公式','qx=kxa，qy=kya，e=epsilon/Jx，eta>0；下标x,y指对无量纲q求偏导。')

def solve(name,q0,sigma,eta,T,N,store_full=True):
    x,X,Y,qx,qy=grid(N);psi0=gaussian(N,sigma,q0);A=np.fft.fft2(psi0);eps=energy(qx,qy,eta)
    spec=spectral_stats(psi0,eta);power=spec['power'];vel=spec['velocity'];vvar=spec['velocity_variance']
    residual=eps-vel[0]*qx-vel[1]*qy;mean=float(np.sum(power*residual));residual-=mean
    de_std=float(np.sqrt(np.sum(power*residual**2)))
    times=np.linspace(0,T,61);track={k:[] for k in ['t','cx','cy','wx','wy','norm','edge_mass','fidelity']};snaps={}
    max_center=0.;max_var=0.
    for i,t in enumerate(times):
        psi=np.fft.ifft2(A*np.exp(-1j*eps*t));m=moments(psi)
        F=float(abs(np.sum(power*np.exp(-1j*residual*t)))**2)
        for k in track:track[k].append(float(t) if k=='t' else F if k=='fidelity' else m[k])
        max_center=max(max_center,abs(m['cx']-vel[0]*t),abs(m['cy']-vel[1]*t))
        max_var=max(max_var,abs(m['wx']**2-sigma**2-t*t*vvar[0]),abs(m['wy']**2-sigma**2-t*t*vvar[1]))
        if i in [0,30,60]:
            if store_full:snaps[i]=psi.copy()
            else:
                maskx=abs(x-m['cx'])<=80;masky=abs(x-m['cy'])<=80
                raw[name+f'_roi_t{int(t)}']=psi[np.ix_(masky,maskx)]
                raw[name+f'_roi_x_t{int(t)}']=x[maskx];raw[name+f'_roi_y_t{int(t)}']=x[masky]
    norm_error=max(abs(np.array(track['norm'])-1));edge=max(track['edge_mass'])
    assert norm_error<2e-12 and edge<1e-9 and max_center<1e-7 and max_var<1e-6,(name,norm_error,edge,max_center,max_var)
    largeN=2*N if N==512 else 1536
    large=gaussian(largeN,sigma,q0);_,_,_,kx,ky=grid(largeN)
    large=np.fft.ifft2(np.fft.fft2(large)*np.exp(-1j*energy(kx,ky,eta)*T))
    off=(largeN-N)//2;large=large[off:off+N,off:off+N]
    end=np.fft.ifft2(A*np.exp(-1j*eps*T));l2=float(np.linalg.norm(large-end))
    assert l2<3e-11,(name,l2)
    check=dict(case=name,N=N,larger_N=largeN,max_norm_error=norm_error,max_edge_mass=edge,
        max_center_error=max_center,max_variance_error=max_var,enlarged_box_amplitude_L2=l2,passed=True)
    case_checks.append(check)
    result=dict(name=name,q0=q0,sigma_a=sigma,eta=eta,N=N,tmax=T,velocity=vel,velocity_variance=vvar,
        spectral_phase_residual_std=de_std,curvature_at_center=float(kap(*q0,eta)),
        hessian_diagonal=[float(np.cos(q0[0])),float(eta*np.cos(q0[1]))],track=track)
    results[name]=result
    for k,v in track.items():raw[name+'_'+k]=np.array(v)
    for i,p in snaps.items():raw[name+f'_psi_t{int(times[i])}']=p
    print('Simulated',name,'F_final',track['fidelity'][-1],flush=True)
    return dict(result=result,snaps=snaps,x=x,psi0=psi0,A=A,eps=eps,A0=float(abs(psi0).max()))

def show_field(ax,c,psi,t,real=False,lim=36):
    x=c['x'];v=np.array(c['result']['velocity']);cx,cy=v*t
    mx=abs(x-cx)<=lim+1;my=abs(x-cy)<=lim+1
    a=psi[np.ix_(my,mx)];value=a.real/c['A0'] if real else abs(a)**2/c['A0']**2
    extent=(x[mx][0]-.5-cx,x[mx][-1]+.5-cx,x[my][0]-.5-cy,x[my][-1]+.5-cy)
    im=ax.imshow(value,extent=extent,origin='lower',interpolation='nearest',cmap='RdBu_r' if real else 'magma',
        vmin=-1 if real else 0,vmax=1)
    ax.set(xlim=(-lim,lim),ylim=(-lim,lim),xlabel=r'$(x-\bar x)/a$',ylabel=r'$(y-\bar y)/a$');ax.set_aspect('equal')
    return im

def packet_figures(main,controls):
    fig,axs=plt.subplots(1,3,figsize=(14.5,4.8),layout='constrained')
    for name,ax in zip(Q0,axs):
        c=main[name+'_eta1'];im=show_field(ax,c,c['snaps'][0],0,True,24);ax.set_title(LABEL[name])
    fig.colorbar(im,ax=axs,shrink=.84,label=r'$\mathrm{Re}\,\psi/A_0$')
    save(fig,'g06_initial_carriers','相同概率包络，不同载波','三组sigma=6a，总概率1，初始相位在包络中心固定为实正。色标以共同初始振幅峰值A0固定。初始概率完全相同，载波中心不同。')
    for real,key in [(False,'g07_final_probability'),(True,'g08_final_real')]:
        fig,axs=plt.subplots(1,3,figsize=(14.5,4.8),layout='constrained')
        for name,ax in zip(Q0,axs):
            c=main[name+'_eta1'];im=show_field(ax,c,c['snaps'][60],180,real);ax.set_title(LABEL[name])
            if not real:ax.add_patch(Circle((0,0),12,fill=False,ls='--',color='#B9D3D8',lw=1.2))
        fig.colorbar(im,ax=axs,shrink=.84,label=r'$\mathrm{Re}\,\psi/A_0$' if real else r'$P/P_0$')
        save(fig,key,'同初宽波包的末态对照',
            'sigma=6a，eta=1，tau=180，三组均在各自概率质心坐标中显示；不缩放宽度，不逐图重标峰值。'+
            ('实部按固定整体相位约定展示，不表示横向磁化。' if real else '虚线是初始半径2sigma的轮廓。普通点两个方向展宽，零曲率线点保留一个方向的展宽，交点两个方向的展宽都较弱。'))
    fig,axs=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    for eta,ax in zip([1.,.3],axs):
        c=main['B_eta'+('1' if eta==1 else '03')];im=show_field(ax,c,c['snaps'][60],180,False);ax.set_title(rf'$\eta={eta:g},\ \tau=180$')
    fig.colorbar(im,ax=axs,shrink=.86,label=r'$P/P_0$')
    save(fig,'g10_anisotropic_design','同一零曲率线点的交换比对照','B=(pi/2,0.7)，相同sigma=6a和tau=180，只改变eta。零曲率线位置不变，但剩余y方向二阶色散系数为eta cos0.7，因而y向展宽与群速度都改变。比较固定时间，非固定传播距离。')
    fig,axs=plt.subplots(1,2,figsize=(13.5,5),layout='constrained')
    c=controls['C_sigma4'];r=c['result'];N=r['N'];x=c['x']
    for i,t in enumerate([0,180,360]):
        p=np.fft.ifft2(c['A']*np.exp(-1j*c['eps']*t));m=moments(p)
        axs[0].plot(x-m['cx'],(abs(p)**2).sum(axis=0),lw=2.2,label=rf'$\tau={t}$')
    axs[0].set(xlim=(-25,25),xlabel=r'$(x-\bar x)/a$',ylabel=r'$P_x$',title=r'交点初态 $\sigma=4a$ 的高阶形变');axs[0].legend()
    z=np.linspace(-.6,.6,500);axs[1].plot(z,np.sin(z)-z,lw=2.5,label='精确残差');axs[1].plot(z,-z**3/6,'--',lw=2,label=r'$-\delta q^3/6$')
    axs[1].set(xlabel=r'$\delta q$',ylabel='减去常数与一阶项后的 e',title='二阶为零，三阶仍保留');axs[1].legend()
    save(fig,'g09_higher_order_limit','有限带宽下的高阶形变','交点中心(pi/2,pi/2)，独立控制sigma=4a，N=1024，tau至360。左图不按峰值归一化，右图固定另一个分量于pi/2，精确残差sin(delta q)-delta q。与主比较sigma=6a不同，不直接作同初宽性能比较。')
    # Exact spectral-phase residual on the initial spectrum, not a curvature-only proxy.
    fig,axs=plt.subplots(1,3,figsize=(14,4.7),layout='constrained')
    q=np.fft.fftshift(2*np.pi*np.fft.fftfreq(512))
    for name,ax in zip(Q0,axs):
        c=main[name+'_eta1'];q0=np.array(c['result']['q0']);v=np.array(c['result']['velocity'])
        mx=abs(q-q0[0])<.25;my=abs(q-q0[1])<.25;X,Y=np.meshgrid(q[mx],q[my]);res=energy(X,Y,1)-v[0]*X-v[1]*Y
        pp=np.fft.fftshift(abs(np.fft.fft2(c['psi0'],norm='ortho'))**2)
        _,_,_,qx,qy=grid(512);pall=abs(np.fft.fft2(c['psi0'],norm='ortho'))**2
        mean=np.sum(pall*(energy(qx,qy,1)-v[0]*qx-v[1]*qy));res=(res-mean)*180
        im=ax.imshow(res,extent=(q[mx][0]-q0[0],q[mx][-1]-q0[0],q[my][0]-q0[1],q[my][-1]-q0[1]),origin='lower',cmap='RdBu_r',vmin=-3,vmax=3)
        b=pp[np.ix_(my,mx)];ax.contour(X-q0[0],Y-q0[1],b/b.max(),levels=[.1,.5,.9],colors='#263E4D',linewidths=1)
        ax.set(title=LABEL[name],xlabel=r'$\delta q_x$',ylabel=r'$\delta q_y$')
    fig.colorbar(im,ax=axs,shrink=.8,label=r'$\tau\,\delta e\quad(\mathrm{rad})$')
    save(fig,'g12_phase_budget','频谱内相对平移态的残余相位','tau=180；delta e=e(q)-u_mean dot q-C，C是谱平均。等高线是同一初态频谱。所有面板固定色标±3rad，超出值饱和。完整复态F由实际频谱的相位叠加计算，不由色标或曲率近似推断。')

def animation(main,real,key):
    fig,axs=plt.subplots(1,3,figsize=(13.5,4.9),dpi=100)
    fig.subplots_adjust(left=.055,right=.90,top=.84,bottom=.17,wspace=.28)
    ims=[]
    for name,ax in zip(Q0,axs):
        c=main[name+'_eta1'];ims.append(show_field(ax,c,c['snaps'][0],0,real));ax.set_title(LABEL[name],fontsize=15)
        ax.tick_params(labelsize=11);ax.xaxis.label.set_size(13);ax.yaxis.label.set_size(13)
    cb=fig.colorbar(ims[-1],cax=fig.add_axes([.92,.22,.014,.52]));cb.set_label(r'$\mathrm{Re}\,\psi/A_0$' if real else r'$P/P_0$',fontsize=13)
    label=fig.text(.055,.94,'',fontsize=17,color=INK)
    fig.text(.055,.035,'共动坐标；初宽均为 6a；固定色标，未逐帧重标度。',fontsize=12,color='#526476')
    frames=[]
    for t in np.linspace(0,180,61):
        for i,name in enumerate(Q0):
            c=main[name+'_eta1'];p=np.fft.ifft2(c['A']*np.exp(-1j*c['eps']*t));x=c['x'];v=np.array(c['result']['velocity']);cx,cy=v*t
            mx=abs(x-cx)<=37;my=abs(x-cy)<=37;a=p[np.ix_(my,mx)]
            ims[i].set_data(a.real/c['A0'] if real else abs(a)**2/c['A0']**2)
            ims[i].set_extent((x[mx][0]-.5-cx,x[mx][-1]+.5-cx,x[my][0]-.5-cy,x[my][-1]+.5-cy))
        label.set_text(rf'$\tau={t:.0f}$'+('：载波实部' if real else '：概率包络比较'))
        fig.canvas.draw();a=np.asarray(fig.canvas.buffer_rgba())[...,:3]
        frames.append(Image.fromarray(a.copy()).convert('P',palette=Image.Palette.ADAPTIVE,colors=128))
    durations=[100]*len(frames);durations[-1]=1400
    path=OUT/f'{key}.gif';frames[0].save(path,save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False,disposal=2)
    plt.close(fig)
    with Image.open(path) as im:
        for i in range(im.n_frames):im.seek(i);im.load()
        count=im.n_frames
    items.append(dict(id=key,title='三组初步设计的传播动画',caption='A/B/C同初宽6a、同时间0至180；共动坐标只减去各自概率质心。固定初始相位约定与色标。Repsi不是横向自旋均值；概率均为实际单磁子翻转概率。',files={'gif':path.name},frames=count))
    print('Saved animation',key,flush=True)

def main():
    symbolic=symbolic_check();geometry_figures()
    maincases={};controls={}
    for eta in [1.,.3]:
        for name,q0 in Q0.items():
            key=name+'_eta'+('1' if eta==1 else '03');maincases[key]=solve(key,q0,6,eta,180,512)
    for sigma in [4,6,8]:
        key=f'C_sigma{sigma}';controls[key]=solve(key,Q0['C'],sigma,1,360,1024,False)
    packet_figures(maincases,controls)
    animation(maincases,False,'g11_probability_animation');animation(maincases,True,'g13_real_animation')
    # Finite-difference derivative control and reciprocal periodicity.
    rng=np.random.default_rng(20261020);pts=rng.uniform(-3*np.pi,3*np.pi,(40,2));h=.002;errs=[]
    for eta in [1.,.3]:
        for x,y in pts:
            f=lambda u,v:float(energy(u,v,eta))
            fx=(f(x-2*h,y)-8*f(x-h,y)+8*f(x+h,y)-f(x+2*h,y))/(12*h)
            fy=(f(x,y-2*h)-8*f(x,y-h)+8*f(x,y+h)-f(x,y+2*h))/(12*h)
            fxx=(-f(x+2*h,y)+16*f(x+h,y)-30*f(x,y)+16*f(x-h,y)-f(x-2*h,y))/(12*h*h)
            fyy=(-f(x,y+2*h)+16*f(x,y+h)-30*f(x,y)+16*f(x,y-h)-f(x,y-2*h))/(12*h*h)
            fxy=(f(x+h,y+h)-f(x+h,y-h)-f(x-h,y+h)+f(x-h,y-h))/(4*h*h)
            errs.append(abs((fxx*fyy-fxy*fxy)/(1+fx*fx+fy*fy)**2-kap(x,y,eta)))
    assert max(errs)<1e-7,max(errs)
    periodic=max(abs(kap(pts[:,0]+2*np.pi,pts[:,1],.3)-kap(pts[:,0],pts[:,1],.3)))
    assert periodic<1e-13
    write('checks.json',dict(status='passed',symbolic=symbolic,cases=case_checks,
        gaussian_curvature_finite_difference_max_error=max(errs),curvature_periodicity_error=periodic,
        random_seed=20261020,coordinate_convention='R=(qx,qy,e), q=ka, e=epsilon/Jx',
        interpretation='Hessian eigenvalues control quadratic spectral phase. Curvature zero alone does not imply H=0 or packet preservation.'))
    write('chart_data.json',dict(cases=results,main_keys=list(maincases),control_keys=list(controls)))
    np.savez_compressed(OUT/'design_data.npz',**raw)
    write('manifest.json',dict(items=items,parameters=dict(main_N=512,main_sigma_a=6,main_tmax=180,control_N=1024,control_sigma_a=[4,6,8],control_tmax=360,
        phase='Only E_F common phase removed; no per-frame rephasing',normalization='sum |psi|^2=1; A0 and P0 fixed at initial values',
        dynamics='Complete cosine band, exact Fourier phases on a periodic lattice; no time-step integration'),
        source_model='../common.py and code/spin_wave_2d.py',curvature_source='https://mathworld.wolfram.com/GaussianCurvature.html'))
    print('Complete:',len(items),'figures/animations;',len(results),'controlled simulations.',flush=True)

if __name__=='__main__':main()
