"""Show propagation in fixed laboratory coordinates, preserving local wave detail."""
from pathlib import Path
import importlib.util,json
import numpy as np
from PIL import Image
from matplotlib.patches import Circle

OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('notation_assets',OUT/'generate_notation.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
ns=module.ns;plt=ns['plt']
data=json.loads((OUT.parent/'curvature-design/chart_data.json').read_text())['cases']
arrays=np.load(OUT.parent/'curvature-design/design_data.npz')

def animation(real):
    key='g15_lab_real_animation' if real else 'g14_lab_probability_animation'
    fig,axs=plt.subplots(1,3,figsize=(15,5.6),dpi=120)
    fig.subplots_adjust(left=.055,right=.905,top=.84,bottom=.17,wspace=.25)
    cases=[]
    for i,name in enumerate(['A','B','C']):
        r=data[name+'_eta1'];psi0=arrays[name+'_eta1_psi_t0'];N=r['N']
        pos=np.arange(-N//2,N//2);_,_,_,kx,ky=ns['grid'](N)
        mask=(pos>=-36)&(pos<=226);sel=np.flatnonzero(mask)
        c=dict(r=r,pos=pos,A=np.fft.fft2(psi0),eps=ns['energy'](kx,ky,1),A0=float(abs(psi0).max()),sel=sel)
        ax=axs[i]
        value=psi0.real/c['A0'] if real else abs(psi0)**2/c['A0']**2
        c['im']=ax.imshow(value[np.ix_(sel,sel)],extent=(pos[sel[0]]-.5,pos[sel[-1]]+.5,pos[sel[0]]-.5,pos[sel[-1]]+.5),
            origin='lower',interpolation='nearest',cmap='RdBu_r' if real else 'magma',vmin=-1 if real else 0,vmax=1)
        ax.set(xlim=(-35,225),ylim=(-35,225),xlabel=r'$x/a$',ylabel=r'$y/a$',title=ns['LABEL'][name]);ax.set_aspect('equal')
        ax.set_xticks([0,100,200]);ax.set_yticks([0,100,200]);ax.tick_params(labelsize=12)
        color='#596A76' if real else '#C1D9DF'
        c['trail'],=ax.plot([],[],ls='--',lw=1.25,color=color,alpha=.85)
        c['center'],=ax.plot([],[],marker='o',ms=5,mfc='none',mec='#176E60' if real else '#95E8B4',mew=1.3,ls='none')
        ax.add_patch(Circle((0,0),12,fill=False,ec=color,lw=1.1,ls=':'))
        if real:
            inset=ax.inset_axes([.035,.57,.40,.40]);local=np.zeros((49,49))
            c['zoom']=inset.imshow(local,extent=(-24.5,24.5,-24.5,24.5),origin='lower',interpolation='nearest',cmap='RdBu_r',vmin=-1,vmax=1)
            inset.set(xlim=(-24,24),ylim=(-24,24),title='随质心放大');inset.title.set_fontsize(10)
            inset.set_xticks([-20,0,20]);inset.set_yticks([-20,0,20]);inset.tick_params(labelsize=7,pad=1)
            inset.set_xlabel(r'$(x-\langle x\rangle)/a$',fontsize=8,labelpad=1)
            inset.set_ylabel(r'$(y-\langle y\rangle)/a$',fontsize=8,labelpad=1)
        cases.append(c)
    cb=fig.colorbar(cases[-1]['im'],cax=fig.add_axes([.927,.22,.012,.52]));cb.set_label(r'$\mathrm{Re}\,\psi/A_0$' if real else r'$P/P_0$',fontsize=15)
    cb.ax.tick_params(labelsize=11)
    timestamp=fig.text(.055,.94,'',fontsize=20,color=ns['INK'])
    fig.text(.055,.035,'固定实验室坐标，范围 −35a 至 225a；虚线为质心轨迹，原点虚圆为初始轮廓。',fontsize=12,color='#526476')
    frames=[];checks=[]
    for index,t in enumerate(np.linspace(0,180,61)):
        for c in cases:
            psi=np.fft.ifft2(c['A']*np.exp(-1j*c['eps']*t));sel=c['sel'];r=c['r']
            shown=psi[np.ix_(sel,sel)];c['im'].set_data(shown.real/c['A0'] if real else abs(shown)**2/c['A0']**2)
            cx=r['track']['cx'][index];cy=r['track']['cy'][index]
            c['trail'].set_data(r['track']['cx'][:index+1],r['track']['cy'][:index+1]);c['center'].set_data([cx],[cy])
            if real:
                pos=c['pos'];mx=abs(pos-cx)<=24.5;my=abs(pos-cy)<=24.5
                c['zoom'].set_data(psi[np.ix_(my,mx)].real/c['A0'])
                c['zoom'].set_extent((pos[mx][0]-.5-cx,pos[mx][-1]+.5-cx,pos[my][0]-.5-cy,pos[my][-1]+.5-cy))
            mass=float(np.sum(abs(shown)**2));checks.append(mass)
        timestamp.set_text(rf'$t={t:.0f}\hbar/J_x$'+('：载波随波包传播，附局部波纹放大' if real else '：波包的平移与展宽'))
        fig.canvas.draw();pixels=np.asarray(fig.canvas.buffer_rgba())[...,:3]
        if index in [0,30,60]:Image.fromarray(pixels.copy()).save(OUT/f'{key}-frame{index:02d}.png')
        frames.append(Image.fromarray(pixels.copy()).convert('P',palette=Image.Palette.ADAPTIVE,colors=192))
    durations=[100]*61;durations[0]=700;durations[-1]=1600
    path=OUT/(key+'.gif');frames[0].save(path,save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False,disposal=2)
    plt.close(fig)
    assert min(checks)>.999, min(checks)
    with Image.open(path) as image:
        assert image.n_frames==61
        for frame in range(61):image.seek(frame);image.load()
    return dict(id=key,title='固定坐标中的波包传播',caption='固定x,y实验室坐标，x/a,y/a范围均为-35至225；三组初宽6a，Jy=Jx，t=0至180hbar/Jx。虚线为实际概率质心轨迹。'+('左上附随质心移动的载波局部放大，主图仍为固定坐标。' if real else 'P0固定为共同初始峰值，不逐帧重标度。'),files={'gif':path.name},frames=61,min_mass_in_view=min(checks),laboratory_limits_a=[-35,225],local_inset=real)

if __name__=='__main__':
    items=[animation(False),animation(True)]
    manifest=json.loads((OUT/'manifest.json').read_text());manifest['items']=[i for i in manifest['items'] if i['id'] not in {j['id'] for j in items}]+items
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'checks_lab_animation.json').write_text(json.dumps(dict(passed=True,items=items),ensure_ascii=False,indent=2),encoding='utf-8')
    print('Saved 2 fixed-laboratory-coordinate GIFs, 61 frames each. Min view mass:',min(i['min_mass_in_view'] for i in items))
