"""Complete-band propagation and equal-size, equal-velocity Gaussian controls."""
from pathlib import Path
import argparse,json,sys,time
import numpy as np
from scipy.optimize import brentq,differential_evolution,minimize
from scipy.sparse.linalg import LinearOperator,expm_multiply

OUT=Path(__file__).resolve().parent
PROJECT=OUT.parents[3]
sys.path.insert(0,str(PROJECT/'figures'/'midterm-report'))
from common import energy,grid

U=0.6
QSTAR=float(np.arcsin(U))
B=float(energy(QSTAR,0.8,1)-U*QSTAR)
CACHE={}

def write(name,data):
    def convert(x):
        if isinstance(x,np.ndarray):return x.tolist()
        if isinstance(x,np.generic):return x.item()
        raise TypeError(type(x).__name__)
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,default=convert),encoding='utf-8')

def fields(n):
    if n not in CACHE:
        _,x,y,qx,qy=grid(n)
        en=energy(qx,qy,1.)
        CACHE[n]=dict(x=x,y=y,qx=qx,qy=qy,e=en,delta=en-U*qx-B,
                      x2=x*x,xy=x*y,y2=y*y)
        radius=np.sqrt(x*x+y*y)
        CACHE[n]['radius']=radius
        CACHE[n]['radius_order']=np.argsort(radius.ravel())
    return CACHE[n]

def bump(q,lo,hi):
    z=(q-lo)/(hi-lo)
    out=np.zeros_like(q,dtype=float)
    use=(z>0)&(z<1)
    out[use]=np.exp(0.2-0.05/(z[use]*(1-z[use])))
    return out

def matched(n,s,delta,Q=None):
    g=fields(n)
    base=bump(g['qx'],.05,1.45)*bump(np.abs(g['qy']),.25,1.25)
    base*=np.exp(-g['delta']**2/(4*delta**2))
    def make(center):
        a=base*np.exp(-(g['qx']-center)**2/(4*s*s))
        a/=np.linalg.norm(a)
        return a
    if Q is None:
        Q=brentq(lambda q:np.sum(np.abs(make(q))**2*np.sin(g['qx']))-U,-2.,3.,xtol=1e-12)
    return make(Q),float(Q)

def psi_from(a):return np.fft.fftshift(np.fft.ifft2(a,norm='ortho'))

def spatial(psi,initial_sigma=None):
    n=psi.shape[0];g=fields(n)
    p=np.abs(psi)**2;norm=p.sum();p=p/norm
    cx=float(np.sum(p*g['x']));cy=float(np.sum(p*g['y']))
    dx=g['x']-cx;dy=g['y']-cy
    cov=np.array([[np.sum(p*dx*dx),np.sum(p*dx*dy)],[np.sum(p*dx*dy),np.sum(p*dy*dy)]])
    edge=(np.abs(g['x'])>.45*n)|(np.abs(g['y'])>.45*n)
    sx,sy=np.sqrt(np.diag(cov))
    r=g['radius'];order=g['radius_order']
    cumulative=np.cumsum(p.ravel()[order])
    radii={str(level):float(r.ravel()[order][np.searchsorted(cumulative,level)]) for level in [.9,.95]}
    if initial_sigma is None:initial_sigma=(sx,sy)
    ellipse=(g['x']/initial_sigma[0])**2+(g['y']/initial_sigma[1])**2
    central=(np.abs(g['x'])<=1)&(np.abs(g['y'])<=1)
    return dict(norm=float(norm),centroid=[cx,cy],covariance=cov,sigma=[sx,sy],edge_mass=float(p[edge].sum()),radii=radii,
                peak=float(p.max()),center_peak=float(p[n//2,n//2]),core_ellipse_1=float(p[ellipse<=1].sum()),core_ellipse_2=float(p[ellipse<=4].sum()),central_3x3=float(p[central].sum()),ipr=float(np.sum(p*p)))

def spectral(a):
    g=fields(a.shape[0]);w=np.abs(a)**2;w/=w.sum()
    ex=float(np.sum(w*g['e']));res=float(np.sum(w*g['delta']))
    qmean=np.array([np.sum(w*g['qx']),np.sum(w*g['qy'])])
    qc=np.array([[np.sum(w*(g['qx']-qmean[0])**2),np.sum(w*(g['qx']-qmean[0])*(g['qy']-qmean[1]))],
                 [np.sum(w*(g['qx']-qmean[0])*(g['qy']-qmean[1])),np.sum(w*(g['qy']-qmean[1])**2)]])
    vx=np.sin(g['qx']);vy=np.sin(g['qy']);mean=np.array([np.sum(w*vx),np.sum(w*vy)])
    vvar=[np.sum(w*(vx-mean[0])**2),np.sum(w*(vy-mean[1])**2)]
    return dict(norm=float(np.sum(np.abs(a)**2)),mean_energy=ex,frequency_sigma=float(np.sqrt(np.sum(w*(g['e']-ex)**2))),
                mismatch_mean=res,mismatch_sigma=float(np.sqrt(np.sum(w*(g['delta']-res)**2))),wavevector_mean=qmean,
                wavevector_covariance=qc,mean_velocity=mean,velocity_variance=vvar,upper_branch_weight=float(w[g['qy']>0].sum()))

def fidelity(a,t):
    w=np.abs(a)**2
    return float(abs(np.sum(w*np.exp(-1j*fields(a.shape[0])['delta']*t)))**2)

def crossing(a,level):
    sig=spectral(a)['mismatch_sigma']
    dt=.03/max(sig,1e-12)
    previous=0.
    for t in np.arange(dt,20/max(sig,1e-12)+dt,dt):
        if fidelity(a,t)<level:
            return float(brentq(lambda x:fidelity(a,x)-level,previous,t,xtol=1e-8))
        previous=t
    return None

def pilot():
    records=[]
    for s in [.25,.35,.45]:
        for delta in [.02,.04,.06]:
            a,Q=matched(512,s,delta)
            sp=spatial(psi_from(a));sk=spectral(a)
            row=dict(s=s,delta=delta,Q=Q,spatial=sp,spectral=sk,t09=crossing(a,.9),t05=crossing(a,.5))
            records.append(row)
            print('PILOT',s,delta,'sigma',sp['sigma'],'edge',sp['edge_mass'],'domega',sk['frequency_sigma'],'t09',row['t09'],flush=True)
    write('pilot.json',dict(model='full cosine, eta=1, normalized one magnon',u=U,b=B,records=records))

def gaussian_state(n,sigma,parameters,branch):
    rho,bxx,bxy,byy=np.asarray(parameters,dtype=float)
    sx,sy=sigma
    cov=np.array([[sx*sx,rho*sx*sy],[rho*sx*sy,sy*sy]])
    eig,vec=np.linalg.eigh(cov)
    if eig.min()<2.25:return None,None
    inv=(vec*(1/eig))@vec.T
    half=(vec*(1/np.sqrt(eig)))@vec.T
    chirp=half@np.array([[bxx,bxy],[bxy,byy]])@half
    g=fields(n)
    amplitude=-.25*(inv[0,0]*g['x2']+2*inv[0,1]*g['xy']+inv[1,1]*g['y2'])
    phase=.5*(chirp[0,0]*g['x2']+2*chirp[0,1]*g['xy']+chirp[1,1]*g['y2'])
    base=np.exp(amplitude+1j*phase);base/=np.linalg.norm(base)
    overlap=np.sum(base.conj()*np.roll(base,-1,axis=1))
    cx=float(overlap.real)
    if cx<U:return None,None
    qx=float(np.arcsin(U/cx))
    if branch[0]:qx=np.pi-qx
    qy=np.pi if branch[1] else 0.
    psi=base*np.exp(1j*(qx*g['x']+qy*g['y']))
    a=np.fft.fft2(np.fft.ifftshift(psi),norm='ortho')
    return a,dict(parameters=list(parameters),carrier=[qx,qy],spatial_covariance=cov,normalized_chirp=[[bxx,bxy],[bxy,byy]],quadratic_phase=chirp)

def optimize_gaussians():
    records=[]
    for case_index,delta in enumerate([.02,.04,.06]):
        start=time.time();a,Q=matched(1024,.35,delta)
        initial=spatial(psi_from(a));sigma=initial['sigma']
        horizon=crossing(a,.5)
        n=256 if max(sigma)<22 else 512
        g=fields(n)
        times=np.linspace(0,horizon,9)
        phase=np.exp(-1j*times[:,None]*g['delta'].ravel()[None,:])
        weights=np.array([1,4,2,4,2,4,2,4,1])/24
        candidates=[]
        for bx in [0,1]:
            for by in [0,1]:
                branch=(bx,by);calls=[0]
                def objective(parameters):
                    ag,_=gaussian_state(n,sigma,parameters,branch)
                    calls[0]+=1
                    if ag is None:return 2.
                    coeff=np.einsum('ij,j->i',phase,np.abs(ag.ravel())**2,optimize=False)
                    return float(1-np.dot(weights,np.abs(coeff)**2))
                zero=np.zeros(4);simple_score=objective(zero)
                de=differential_evolution(objective,[(-.85,.85),(-1.5,1.5),(-1.5,1.5),(-1.5,1.5)],
                    maxiter=18,popsize=6,tol=1e-7,polish=False,rng=np.random.default_rng(41021+10*case_index+2*bx+by),x0=zero)
                seed=zero if simple_score<=de.fun else de.x
                local=minimize(objective,seed,method='Powell',bounds=[(-.85,.85),(-1.5,1.5),(-1.5,1.5),(-1.5,1.5)],
                               options=dict(maxiter=100,xtol=2e-5,ftol=1e-11))
                options=[(simple_score,zero),(float(de.fun),de.x),(float(local.fun),local.x)]
                score,params=min(options,key=lambda x:x[0])
                ag,meta=gaussian_state(1024,sigma,params,branch)
                az,metaz=gaussian_state(1024,sigma,zero,branch)
                candidate=dict(branch=branch,objective=score,parameters=params,metadata=meta,
                    objective_evaluations=calls[0],de_success=bool(de.success),de_message=str(de.message),
                    local_success=bool(local.success),initial=spatial(psi_from(ag)),spectral=spectral(ag),
                    t09=crossing(ag,.9),t05=crossing(ag,.5),zero_phase_t09=crossing(az,.9),
                    zero_phase_objective=simple_score,zero_phase_metadata=metaz)
                candidates.append(candidate)
                print('OPT',delta,branch,'loss',score,'t09',candidate['t09'],'params',params,'calls',calls[0],flush=True)
        best=min(candidates,key=lambda x:x['objective'])
        case=dict(delta=delta,s=.35,Q=Q,n_initial=1024,n_optimization=n,horizon=horizon,
            objective_times=times,correlated_initial=initial,correlated_spectral=spectral(a),
            correlated_t09=crossing(a,.9),candidates=candidates,best_branch=best['branch'],
            best_parameters=best['parameters'],elapsed_seconds=time.time()-start)
        records.append(case);write('optimization.json',dict(u=U,b=B,cases=records))
        print('CASE DONE',delta,'elapsed',time.time()-start,flush=True)

def evolution(a,t):
    return psi_from(a*np.exp(-1j*fields(a.shape[0])['delta']*t))

def density_overlap(p0,psi):return float(np.sum(np.sqrt(p0)*np.abs(psi))**2)

def trajectory(a,times,sigma):
    initial=psi_from(a);p0=np.abs(initial)**2
    out=[];g=fields(a.shape[0]);spec=spectral(a)
    vxpsi=psi_from(a*np.sin(g['qx']));vypsi=psi_from(a*np.sin(g['qy']))
    c0=spatial(initial)['covariance']
    cross=np.array([np.sum(initial.conj()*g['x']*vxpsi).real,np.sum(initial.conj()*g['y']*vypsi).real])
    for t in times:
        psi=evolution(a,float(t));row=spatial(psi,sigma)
        row.update(t=float(t),F=float(abs(np.vdot(initial,psi))**2),D=density_overlap(p0,psi))
        row['variance_predicted']=np.diag(c0)+2*cross*t+np.asarray(spec['velocity_variance'])*t*t
        row['variance_residual']=np.diag(row['covariance'])-row['variance_predicted']
        shift=int(round(U*t))
        labp=np.roll(np.abs(psi)**2,shift,axis=1)
        edge=(np.abs(g['x'])>.45*a.shape[0])|(np.abs(g['y'])>.45*a.shape[0])
        row['lab_edge_mass']=float(labp[edge].sum())
        out.append(row)
    return out

def independence_check():
    n=64;a,_=matched(n,.35,.04);psi=psi_from(a)
    def act(v):
        z=np.asarray(v).reshape(n,n)
        return (-1j*(2*z-.5*(np.roll(z,1,0)+np.roll(z,-1,0)+np.roll(z,1,1)+np.roll(z,-1,1)))).ravel()
    op=LinearOperator((n*n,n*n),matvec=act,rmatvec=lambda v:-act(v),dtype=np.complex128)
    real=expm_multiply(3.*op,psi.ravel(),traceA=-1j*6*n*n).reshape(n,n)
    fourier=psi_from(a*np.exp(-1j*fields(n)['e']*3.))
    return dict(n=n,t=3.,real_space_exponential_vs_spectral_l2=float(np.linalg.norm(real-fourier)))

def analyze():
    optimization=json.loads((OUT/'optimization.json').read_text(encoding='utf-8'))
    summaries=[];states={};snaps={}
    all_checks={'independent_propagator':independence_check(),'convergence':[]}
    for case in optimization['cases']:
        delta=case['delta'];sigma=case['correlated_initial']['sigma'];Q=case['Q']
        a,_=matched(1024,.35,delta,Q)
        ag,meta=gaussian_state(1024,sigma,case['best_parameters'],case['best_branch'])
        lowgauss,lowmeta=gaussian_state(1024,sigma,[0,0,0,0],[0,0])
        t05g=crossing(ag,.5)
        end=1.15*max(t05g,case['horizon'])
        # These times give exact integer-site translations: u*t is an integer.
        times=np.arange(0,np.ceil(end*U)+1)/U
        dense=np.linspace(0,times[-1],301)
        rowsc=trajectory(a,times,sigma);rowsg=trajectory(ag,times,sigma)
        p0c=spatial(psi_from(a));p0g=spatial(psi_from(ag))
        record=dict(delta=delta,s=.35,Q=Q,n=1024,sigma_target=sigma,gaussian=meta,
            initial_correlated=p0c,initial_gaussian=p0g,spectral_correlated=spectral(a),spectral_gaussian=spectral(ag),
            lifetimes_correlated={str(f):crossing(a,f) for f in [.9,.8,.5]},
            lifetimes_gaussian={str(f):crossing(ag,f) for f in [.9,.8,.5]},
            low_energy_zero_phase_gaussian=dict(metadata=lowmeta,spectral=spectral(lowgauss),t09=crossing(lowgauss,.9)),
            times=dense,F_correlated=[fidelity(a,t) for t in dense],F_gaussian=[fidelity(ag,t) for t in dense],
            spatial_trajectory_correlated=rowsc,spatial_trajectory_gaussian=rowsg)
        summaries.append(record)
        suffix=str(delta).replace('.','_')
        states['matched_'+suffix]=a;states['gaussian_'+suffix]=ag
        coarse, _=matched(512,.35,delta,Q)
        check=dict(delta=delta,reference_sigma=sigma,coarse_sigma=spatial(psi_from(coarse))['sigma'],
            coarse_fidelity_max_error=max(abs(fidelity(coarse,t)-fidelity(a,t)) for t in np.linspace(0,end,9)),
            normalization_max_error=max(abs(r['norm']-1) for r in rowsc+rowsg),
            maximum_comoving_edge_mass=max(r['edge_mass'] for r in rowsc+rowsg),
            maximum_lab_edge_mass=max(r['lab_edge_mass'] for r in rowsc+rowsg),
            gaussian_size_relative_error=max(abs(np.asarray(p0g['sigma'])/sigma-1)),
            velocity_error_correlated=float(np.linalg.norm(np.asarray(spectral(a)['mean_velocity'])-[U,0])),
            velocity_error_gaussian=float(np.linalg.norm(np.asarray(spectral(ag)['mean_velocity'])-[U,0])),
            max_moment_variance_relative_residual=max(max(abs(np.asarray(r['variance_residual']))/np.maximum(np.asarray(r['variance_predicted']),1)) for r in rowsc+rowsg))
        if delta==.04:
            fine,_=matched(2048,.35,delta,Q)
            fineg,_=gaussian_state(2048,sigma,case['best_parameters'],case['best_branch'])
            check['fine_sigma']=spatial(psi_from(fine))['sigma']
            check['fine_correlated_fidelity_max_error']=max(abs(fidelity(fine,t)-fidelity(a,t)) for t in np.linspace(0,end,9))
            check['fine_gaussian_fidelity_max_error']=max(abs(fidelity(fineg,t)-fidelity(ag,t)) for t in np.linspace(0,end,9))
            for label,state in [('matched',a),('gaussian',ag)]:
                for t in [0.,10.,30.,60.]:snaps[f'{label}_{int(t)}']=np.abs(evolution(state,t))**2
            # Large grids are not retained between cases.
            del fine,fineg
            CACHE.pop(2048,None)
        all_checks['convergence'].append(check)
        write('results.json',dict(model='eta=1 full cosine band',u=U,b=B,cases=summaries))
        write('verification.json',all_checks)
        print('ANALYZED',delta,'t09 C/G',record['lifetimes_correlated']['0.9'],record['lifetimes_gaussian']['0.9'],'checks',check,flush=True)
    np.savez_compressed(OUT/'initial_states.npz',**states)
    np.savez_compressed(OUT/'main_snapshots.npz',**snaps)

def figures():
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    from PIL import Image
    data=json.loads((OUT/'results.json').read_text(encoding='utf-8'))
    main=next(c for c in data['cases'] if c['delta']==.04)
    arrays=np.load(OUT/'initial_states.npz');snaps=np.load(OUT/'main_snapshots.npz')
    a=arrays['matched_0_04'];ag=arrays['gaussian_0_04'];g=fields(a.shape[0])
    colors=['#0072B2','#D55E00']
    plt.rcParams.update({'font.size':11,'axes.titlesize':13,'axes.labelsize':12,'legend.fontsize':10})
    manifest=[]
    def save(fig,key,caption):
        paths={}
        for ext in ['png','svg','pdf']:
            path=OUT/f'{key}.{ext}';fig.savefig(path,dpi=170,bbox_inches='tight');paths[ext]=path.name
        plt.close(fig);manifest.append(dict(id=key,caption=caption,files=paths))
    fig,ax=plt.subplots(2,2,figsize=(12,9),layout='constrained')
    power=np.fft.fftshift(np.abs(a)**2);q=np.fft.fftshift(2*np.pi*np.fft.fftfreq(a.shape[0]))
    im=ax[0,0].imshow(power,origin='lower',extent=(q[0],q[-1],q[0],q[-1]),aspect='auto',norm=LogNorm(max(power.max()*1e-5,1e-12),power.max()),cmap='viridis')
    xx=np.linspace(.05,1.45,500);arg=2-np.cos(xx)-U*xx-B;ok=np.abs(arg)<=1
    for sign in [-1,1]:ax[0,0].plot(xx[ok],sign*np.arccos(arg[ok]),color='white',lw=1,ls='--')
    ax[0,0].set(xlim=(0,1.5),ylim=(-1.35,1.35),xlabel=r'$q_x=k_xa$',ylabel=r'$q_y=k_ya$',title='有限匹配谱与理想非等频分支')
    fig.colorbar(im,ax=ax[0,0],label=r'离散谱概率 $|A|^2$')
    pmax=max(snaps['matched_0'].max(),snaps['gaussian_0'].max())
    choose=(np.abs(g['x'])<=22)&(np.abs(g['y'])<=35)
    for panel,label,title in [(ax[0,1],'matched','关联包初态'),(ax[1,0],'gaussian','同尺寸、同速度优化高斯')]:
        p=snaps[label+'_0'];rows=np.where(np.abs(g['y'][:,0])<=35)[0];cols=np.where(np.abs(g['x'][0])<=22)[0]
        im=panel.imshow(p[np.ix_(rows,cols)],origin='lower',extent=(-22.5,22.5,-35.5,35.5),vmin=0,vmax=pmax,cmap='viridis',aspect='auto')
        panel.set(xlabel=r'$(x-ut)/a$',ylabel=r'$y/a$',title=title)
        fig.colorbar(im,ax=panel,label=r'格点概率 $P$')
    bins=np.linspace(-.16,.16,121)
    for label,state,col in [('关联包',a,colors[0]),('高斯',ag,colors[1])]:
        centered=g['delta']-spectral(state)['mismatch_mean']
        hist,_=np.histogram(centered,bins=bins,weights=np.abs(state)**2)
        ax[1,1].plot((bins[1:]+bins[:-1])/2,hist/(bins[1]-bins[0]),label=label,color=col)
    ax[1,1].set(xlabel=r'$\Delta-\langle\Delta\rangle$',ylabel='失配概率密度',title='去掉整体相位后的实际失配');ax[1,1].legend()
    save(fig,'construction','主组 delta=0.04。谱图使用对数色标，两个初态使用相同绝对概率色标；图中空间范围为裁剪窗口。')
    fig,ax=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    t=np.asarray(main['times'])
    for key,label,col in [('correlated','关联包',colors[0]),('gaussian','优化高斯',colors[1])]:
        rows=main['spatial_trajectory_'+key];ts=np.array([r['t'] for r in rows]);sig=np.array([r['sigma'] for r in rows])
        ax[0,0].plot(t,main['F_'+key],label=label,color=col)
        ax[0,1].plot(ts,[r['D'] for r in rows],label=label,color=col)
        ax[1,0].plot(ts,sig[:,0]/main['sigma_target'][0],label=label+'：纵向',color=col)
        ax[1,0].plot(ts,sig[:,1]/main['sigma_target'][1],label=label+'：横向',color=col,ls='--')
        ax[1,1].plot(ts,[r['core_ellipse_2'] for r in rows],label=label,color=col)
    for panel in ax.flat:panel.set_xlabel(r'$\tau=J_xt/\hbar$');panel.legend();panel.grid(alpha=.2)
    ax[0,0].axhline(.9,color='gray',ls=':',lw=1);ax[0,0].set(title='完整复态平移保真度',ylabel=r'$F$',ylim=(0,1.02))
    ax[0,1].set(title='完整密度形状重叠',ylabel=r'$D$',ylim=(0,1.02))
    ax[1,0].set(title='相对初始 RMS 尺寸',ylabel=r'$\sigma(\tau)/\sigma(0)$')
    ax[1,1].set(title='固定随动椭圆内的绝对概率',ylabel=r'$P[(x/\sigma_x)^2+(y/\sigma_y)^2\leq4]$',ylim=(0,1))
    save(fig,'comparison','主组：归一化、初始纵横 RMS 和平均速度匹配。密度与尺寸在 u*t 为整数的时刻评估；无逐帧峰值重归一化。')
    fig,axs=plt.subplots(4,2,figsize=(10,12),layout='constrained')
    rows=np.where(np.abs(g['y'][:,0])<=45)[0];cols=np.where(np.abs(g['x'][0])<=25)[0]
    for i,tau in enumerate([0,10,30,60]):
        for j,label in enumerate(['matched','gaussian']):
            p=snaps[f'{label}_{tau}'];crop=p[np.ix_(rows,cols)]
            im=axs[i,j].imshow(crop,origin='lower',extent=(-25.5,25.5,-45.5,45.5),aspect='auto',vmin=0,vmax=pmax,cmap='viridis')
            axs[i,j].set(title=f'{"关联包" if j==0 else "优化高斯"}，τ={tau}，框内概率={crop.sum():.3f}',xlabel=r'$(x-ut)/a$',ylabel=r'$y/a$')
    fig.colorbar(im,ax=axs.ravel().tolist(),shrink=.65,label='格点概率（全图统一色标）')
    save(fig,'snapshots','完整色散传播的固定速度随动图。所有面板使用同一概率色标；标题报告裁剪框内权重，完整分布另存 NPZ。')
    fig,ax=plt.subplots(1,3,figsize=(14,4),layout='constrained')
    cases=data['cases'];ds=[c['delta'] for c in cases]
    ax[0].plot(ds,[c['sigma_target'][0] for c in cases],'o-',label='纵向');ax[0].plot(ds,[c['sigma_target'][1] for c in cases],'s--',label='横向')
    for label,key,col in [('关联包','correlated',colors[0]),('优化高斯','gaussian',colors[1])]:
        ax[1].plot(ds,[c['lifetimes_'+key]['0.9'] for c in cases],'o-',label=label,color=col)
        ax[2].plot(ds,[c['spectral_'+key]['frequency_sigma'] for c in cases],'o-',label=label,color=col)
    for panel in ax:panel.set_xlabel(r'失配厚度 $\delta$');panel.legend();panel.grid(alpha=.2)
    ax[0].set(title='初态空间代价',ylabel=r'RMS / $a$');ax[1].set(title='同尺寸比较的保形时间',ylabel=r'$\tau_{F\geq0.9}$');ax[2].set(title='实际频率带宽代价',ylabel=r'$\sigma_e$')
    save(fig,'tradeoffs','固定沿线谱窗 s=0.35，改变谱厚度；每一点均用各自实测初宽重新构造和搜索高斯基线。')
    write('figure-manifest.json',manifest)
    # A compact animation is evaluated at integer-site translations.
    fig,ax=plt.subplots(1,2,figsize=(10,5),layout='constrained');images=[]
    ims=[]
    for panel,label in zip(ax,['关联包','优化高斯']):
        ims.append(panel.imshow(np.zeros((len(rows),len(cols))),origin='lower',extent=(-25.5,25.5,-45.5,45.5),aspect='auto',vmin=0,vmax=pmax,cmap='viridis'))
        panel.set(title=label,xlabel=r'$(x-ut)/a$',ylabel=r'$y/a$')
    for tau in np.arange(37)/U:
        for image,state in zip(ims,[a,ag]):image.set_data(np.abs(evolution(state,tau))[np.ix_(rows,cols)]**2)
        fig.suptitle(f'完整色散；同尺寸同平均速度；τ={tau:.2f}，u=0.6',fontsize=13)
        fig.canvas.draw();images.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[...,:3]).convert('P',palette=Image.Palette.ADAPTIVE,colors=128))
    images[0].save(OUT/'propagation.gif',save_all=True,append_images=images[1:],duration=[110]*36+[1200],loop=0,optimize=False)
    plt.close(fig)
    print('FIGURES DONE',flush=True)

def controls():
    states=np.load(OUT/'initial_states.npz')
    data=json.loads((OUT/'results.json').read_text(encoding='utf-8'))
    a=states['matched_0_04'];ag=states['gaussian_0_04']
    w=np.abs(a)**2
    sep=np.sqrt(w.sum(axis=0)[None,:]*w.sum(axis=1)[:,None])
    row=dict(description='Product of the original qx and qy marginal probabilities; no phase. A mechanism ablation, not an equal-size performance baseline.',
             marginal_error_x=float(np.max(abs((np.abs(sep)**2).sum(axis=0)-w.sum(axis=0)))),
             marginal_error_y=float(np.max(abs((np.abs(sep)**2).sum(axis=1)-w.sum(axis=1)))),
             spatial=spatial(psi_from(sep)),spectral=spectral(sep),t09=crossing(sep,.9),t05=crossing(sep,.5))
    qx=np.linspace(.05,1.45,2001);arg=2-np.cos(qx)-U*qx-B;qy=np.arccos(arg)
    grad=np.sqrt((np.sin(qx)-U)**2+np.sin(qy)**2)
    checks=json.loads((OUT/'verification.json').read_text(encoding='utf-8'))
    checks['branch']=dict(qx_interval=[.05,1.45],positive_qy_range=[float(qy.min()),float(qy.max())],
        ideal_energy_range=[float(B+U*qx.min()),float(B+U*qx.max())],minimum_sampled_gradient_norm=float(grad.min()),
        analytic_curve_residual=float(np.max(abs(energy(qx,qy,1)-U*qx-B))))
    checks['space_spectrum_overlap_max_error']=max(abs(abs(np.vdot(psi_from(state),evolution(state,t)))**2-fidelity(state,t)) for state in [a,ag] for t in [0,10,30,60])
    main=next(c for c in data['cases'] if c['delta']==.04)
    fine,_=matched(2048,.35,.04,main['Q'])
    fineg,_=gaussian_state(2048,main['sigma_target'],main['gaussian']['parameters'],[0,0])
    density_checks=[]
    for label,state,reference in [('correlated',fine,a),('gaussian',fineg,ag)]:
        p0=np.abs(psi_from(state))**2;pref=np.abs(psi_from(reference))**2
        for t in [10,30,60]:
            ps=evolution(state,t);pr=evolution(reference,t)
            sf=spatial(ps);sr=spatial(pr)
            density_checks.append(dict(label=label,t=t,D_error=abs(density_overlap(p0,ps)-density_overlap(pref,pr)),
                sigma_relative_error=max(abs(np.asarray(sf['sigma'])/sr['sigma']-1)),edge_mass=sf['edge_mass']))
    checks['fine_density_checks']=density_checks
    objective_checks=[]
    opt=json.loads((OUT/'optimization.json').read_text(encoding='utf-8'))
    for case in data['cases']:
        source=next(c for c in opt['cases'] if c['delta']==case['delta'])
        state=states['gaussian_'+str(case['delta']).replace('.','_')]
        objective=1-np.dot(np.array([1,4,2,4,2,4,2,4,1])/24,[fidelity(state,t) for t in source['objective_times']])
        best=min(source['candidates'],key=lambda v:v['objective'])
        objective_checks.append(dict(delta=case['delta'],objective_fine=float(objective),objective_optimization_grid=best['objective'],absolute_difference=abs(objective-best['objective'])))
    checks['optimization_resolution']=objective_checks
    checks['scope']='Deterministic numerical checks; parameterized search, not a global optimality proof or novelty claim.'
    write('controls.json',dict(marginal_product=row))
    write('verification.json',checks)
    print('CONTROLS',row,flush=True)
    print('VALIDATION',dict(branch=checks['branch'],density=density_checks,optimization=objective_checks),flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['pilot','optimize','analyze','controls','figures'],default='pilot')
    args=parser.parse_args()
    if args.stage=='pilot':pilot()
    elif args.stage=='optimize':optimize_gaussians()
    elif args.stage=='analyze':analyze()
    elif args.stage=='figures':figures()
    elif args.stage=='controls':controls()

if __name__=='__main__':main()
