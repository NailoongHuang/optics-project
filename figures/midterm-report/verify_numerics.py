"""Independent controls for the midterm one-magnon simulations."""
import platform
import numpy as np
import scipy
from scipy.special import jv
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import expm_multiply
from common import ROOT, energy, grid, delta, gaussian, propagate, moments, spectral_stats, write_json

def main():
    records=[]
    # Build an independent sparse real-space Hamiltonian bond by bond.
    n=12; eta=.37; rng=np.random.default_rng(20261019)
    h=lil_matrix((n*n,n*n),dtype=float)
    for y in range(n):
        for x in range(n):
            i=y*n+x
            for dx,dy,j in [(1,0,1.),(0,1,eta)]:
                k=((y+dy)%n)*n+(x+dx)%n
                h[i,i]+=j/2; h[k,k]+=j/2
                h[i,k]-=j/2; h[k,i]-=j/2
    psi=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)); psi/=np.linalg.norm(psi)
    t=4.3
    independent=expm_multiply(-1j*h.tocsr()*t,psi.ravel()).reshape(n,n)
    err=float(np.linalg.norm(propagate(psi,t,eta)-independent))
    assert err<1e-11
    records.append(dict(test='independent_sparse_real_space_exponential',N=n,eta=eta,tau=t,l2_error=err,threshold=1e-11,seed=20261019))
    # Full complex Bessel-function propagator on an effectively infinite lattice.
    for eta in [0.,.3,1.,1.7]:
        for t in [0.,.2,7.,45.]:
            x,*_=grid(256)
            bx=(1j)**x*jv(x,t); by=(1j)**x*jv(x,eta*t)
            exact=np.exp(-1j*(1+eta)*t)*np.outer(by,bx)
            actual=propagate(delta(256),t,eta)
            err=float(np.linalg.norm(actual-exact)); m=moments(actual)
            widtherr=max(abs(m['wx']-t/np.sqrt(2)),abs(m['wy']-eta*t/np.sqrt(2)))
            assert err<2e-12 and widtherr<1e-10 and m['edge_mass']<1e-12
            records.append(dict(test='bessel_complex_amplitude_and_ballistic_width',N=256,eta=eta,tau=t,
                l2_error=err,width_error=widtherr,norm_error=abs(m['norm']-1),edge_mass=m['edge_mass']))
    # Gaussian mean velocity and variance derived from its spectral Gaussian.
    for sigma in [3.,6.,10.]:
        for eta,q0 in [(1.,(.7,0.)),(.3,(.7,.7)),(1.,(np.pi/2,np.pi/2))]:
            psi=gaussian(384,sigma,q0); sp=spectral_stats(psi,eta)
            j=np.array([1.,eta]); q=np.array(q0)
            vel=j*np.sin(q)*np.exp(-1/(8*sigma*sigma))
            vvar=j*j*.5*(1-np.cos(2*q)*np.exp(-1/(2*sigma*sigma)))-vel*vel
            t=60.; actual=propagate(psi,t,eta); m=moments(actual)
            ce=float(np.max(np.abs(np.array([m['cx'],m['cy']])-t*vel)))
            we=float(np.max(np.abs(np.array([m['wx'],m['wy']])-np.sqrt(sigma*sigma+t*t*vvar))))
            ve=float(np.max(np.abs(sp['velocity']-vel)))
            assert ce<1e-8 and we<1e-8 and ve<1e-12 and m['edge_mass']<1e-8, (sigma,eta,q0,ce,we,ve,m['edge_mass'])
            large=propagate(gaussian(768,sigma,q0),t,eta)[192:576,192:576]
            boxerr=float(np.linalg.norm(large-actual))
            assert boxerr<1e-8
            records.append(dict(test='gaussian_analytic_moments_and_doubled_box',N=384,N_large=768,sigma=sigma,
                eta=eta,q0=q0,tau=t,velocity_error=ve,center_error=ce,width_error=we,
                norm_error=abs(m['norm']-1),edge_mass=m['edge_mass'],doubled_box_l2_error=boxerr))
    # Zero momentum is stationary; any nonzero eigenmode acquires only a phase.
    n=64; _,x,y,_,_=grid(n)
    qx,qy=2*np.pi*7/n,2*np.pi*(-3)/n
    psi=np.exp(1j*(qx*x+qy*y))/n; t=31.
    err=float(np.linalg.norm(propagate(psi,t,.3)-psi*np.exp(-1j*energy(qx,qy,.3)*t)))
    zeroerr=float(np.linalg.norm(propagate(np.ones((n,n))/n,t,.3)-np.ones((n,n))/n))
    assert err<1e-12 and zeroerr<1e-14
    records.append(dict(test='plane_wave_and_zero_mode',plane_wave_l2_error=err,zero_mode_l2_error=zeroerr))
    result=dict(status='passed',checks_count=len(records),conventions=dict(a=1,hbar=1,Jx=1,S=.5,h=0,
        psi='normalized one-magnon amplitude after removing common E_F phase'),
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        pilot_limitations=[dict(N=256,sigma=10,q0=[float(np.pi/2)]*2,tau=60,edge_mass=4.0580166278068936e-8,
            width_error=2.1417374540533274e-8,resolution='Expanded Gaussian validation to N=384 and compared N=768.')],results=records)
    write_json(ROOT/'checks_independent.json',result)
    print('Independent numerical controls passed:',len(records))
    print('Sparse exponential L2 error:',records[0]['l2_error'])
    print('Largest doubled-box L2 error:',max(r.get('doubled_box_l2_error',0) for r in records))

if __name__=='__main__': main()
