"""Shared model, exact propagation, and export conventions for the midterm figures.

Coordinates x,y are lattice indices; q=ka; tau=Jx*t/hbar; eta=Jy/Jx.
All dynamic figures describe a normalized spin-1/2 one-magnon amplitude.
The common ground-state phase exp(-i E_F t/hbar) is removed explicitly.
"""
from pathlib import Path
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
sys.path.insert(0, str(PROJECT / 'code'))
from spin_wave_2d import Params

COLORS = ['#246B9A', '#D16143', '#26846B', '#8556A6', '#C09527', '#566A7C']
INK = '#203648'

def style():
    plt.rcParams.update({'font.family':'sans-serif',
        'font.sans-serif':['Microsoft YaHei','DejaVu Sans'],
        'font.size':13,'axes.titlesize':15,'axes.labelsize':13,
        'xtick.labelsize':11,'ytick.labelsize':11,'legend.fontsize':11,
        'axes.unicode_minus':False,'svg.fonttype':'path','pdf.fonttype':42,
        'figure.facecolor':'white','axes.spines.top':False,
        'axes.spines.right':False,'axes.prop_cycle':matplotlib.cycler(color=COLORS),
        'savefig.facecolor':'white'})

def energy(qx, qy, eta=1.):
    return Params(S=.5, Jx=1., Jy=float(eta), h=0.).dispersion(qx, qy)[0]

def grid(n=256):
    x=np.arange(n)-n//2
    xx,yy=np.meshgrid(x,x,indexing='xy')
    q=2*np.pi*np.fft.fftfreq(n)
    qx,qy=np.meshgrid(q,q,indexing='xy')
    return x,xx,yy,qx,qy

def gaussian(n=256, sigma=6., q0=(.7,0.), sigma_y=None):
    _,x,y,_,_=grid(n)
    sy=sigma if sigma_y is None else sigma_y
    psi=np.exp(-x*x/(4*sigma*sigma)-y*y/(4*sy*sy)+1j*(q0[0]*x+q0[1]*y))
    return psi/np.linalg.norm(psi)

def delta(n=256):
    psi=np.zeros((n,n),complex); psi[n//2,n//2]=1.
    return psi

def propagate(psi0,t,eta=1.):
    _,_,_,qx,qy=grid(psi0.shape[0])
    return np.fft.ifft2(np.fft.fft2(psi0)*np.exp(-1j*energy(qx,qy,eta)*t))

def spectral_stats(psi0,eta=1.):
    _,_,_,qx,qy=grid(psi0.shape[0])
    power=np.abs(np.fft.fft2(psi0,norm='ortho'))**2
    vx,vy=np.sin(qx),eta*np.sin(qy)
    mean=np.array([np.sum(power*vx),np.sum(power*vy)])
    var=np.array([np.sum(power*(vx-mean[0])**2),np.sum(power*(vy-mean[1])**2)])
    return {'velocity':mean,'velocity_variance':var,'power':power}

def moments(psi):
    _,x,y,_,_=grid(psi.shape[0]); p=np.abs(psi)**2; norm=p.sum()
    cx=np.sum(p*x)/norm; cy=np.sum(p*y)/norm
    wx=np.sqrt(np.sum(p*(x-cx)**2)/norm); wy=np.sqrt(np.sum(p*(y-cy)**2)/norm)
    edge=np.zeros_like(p,dtype=bool); edge[:12,:]=True; edge[-12:,:]=True
    edge[:,:12]=True; edge[:,-12:]=True
    return {'norm':float(norm),'cx':float(cx),'cy':float(cy),
            'wx':float(wx),'wy':float(wy),'edge_mass':float(p[edge].sum())}

def translated_reference(psi0,velocity,t):
    _,_,_,qx,qy=grid(psi0.shape[0])
    return np.fft.ifft2(np.fft.fft2(psi0)*np.exp(-1j*(velocity[0]*qx+velocity[1]*qy)*t))

def trajectory(psi0,times,eta=1.):
    spec=spectral_stats(psi0,eta); rows=[]
    for t in times:
        psi=propagate(psi0,float(t),eta); row=moments(psi)
        ref=translated_reference(psi0,spec['velocity'],float(t))
        row.update(t=float(t),fidelity=float(abs(np.vdot(ref,psi))**2))
        rows.append(row)
    return {key:np.array([r[key] for r in rows]) for key in rows[0]}

def heading(fig,title,subtitle='',footer=''):
    fig.subplots_adjust(left=.085,right=.94,bottom=.17,top=.78,wspace=.32,hspace=.45)
    fig.text(.045,.945,title,fontsize=21,weight='bold',color=INK,va='top')
    if subtitle: fig.text(.045,.865,subtitle,fontsize=12.5,color='#526476',va='top')
    if footer: fig.text(.045,.055,footer,fontsize=11,color='#526476',va='bottom')

def save_figure(fig,group,stem,title,caption,params=None,role='core'):
    out=ROOT/group; out.mkdir(parents=True,exist_ok=True)
    files={}
    for ext in ('png','svg','pdf'):
        p=out/f'{stem}.{ext}'; fig.savefig(p,dpi=170)
        files[ext]=p.relative_to(ROOT).as_posix()
    plt.close(fig)
    return dict(id=stem,title=title,caption=caption,group=group,role=role,
                parameters=params or {},files=files)

def save_animation(fig,update,times,group,stem,title,caption,params=None):
    out=ROOT/group; out.mkdir(parents=True,exist_ok=True)
    images=[]
    for t in times:
        update(float(t)); fig.canvas.draw()
        images.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[...,:3]).convert('P',palette=Image.Palette.ADAPTIVE,colors=128))
    path=out/f'{stem}.gif'
    durations=[80]*len(images); durations[-1]=1200
    images[0].save(path,save_all=True,append_images=images[1:],duration=durations,loop=0,optimize=False,disposal=2)
    plt.close(fig)
    with Image.open(path) as im:
        for j in range(im.n_frames): im.seek(j); im.load()
        frames=im.n_frames
    return dict(id=stem,title=title,caption=caption,group=group,role='animation',
                parameters=params or {},files={'gif':path.relative_to(ROOT).as_posix()},
                frame_count=frames,frames_decoded=True)

def write_json(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    def convert(x):
        if isinstance(x,np.ndarray): return x.tolist()
        if isinstance(x,np.generic): return x.item()
        raise TypeError(type(x).__name__)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=convert),encoding='utf-8')

style()
