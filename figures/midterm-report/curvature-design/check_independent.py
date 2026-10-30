"""Independent Gaussian spectral quadrature; no shared propagation code."""
from pathlib import Path
import json, math
import numpy as np
from numpy.polynomial.hermite import hermgauss
B=Path(__file__).resolve().parent
data=json.loads((B/'chart_data.json').read_text())['cases']
checks=[]
for name,c in data.items():
    s=c['sigma_a']; d=1/(2*s); t=c['tmax']; q0=c['q0']; eta=c['eta']
    widths=[]
    for q,j in zip(q0,[1,eta]):
        mean=j*math.sin(q)*math.exp(-d*d/2)
        variance=j*j*(.5*(1-math.cos(2*q)*math.exp(-2*d*d)))-(mean*mean)
        widths.append(math.sqrt(s*s+t*t*variance))
    fs=[]
    for order in [80,160]:
        nodes,weights=hermgauss(order); amp=1+0j
        for q,j in zip(q0,[1,eta]):
            z=q+math.sqrt(2)*d*nodes
            mean=j*math.sin(q)*math.exp(-d*d/2)
            residual=j*(1-np.cos(z))-mean*z
            amp*=np.sum(weights*np.exp(-1j*residual*t))/math.sqrt(math.pi)
        fs.append(float(abs(amp)**2))
    width_error=max(abs(widths[0]-c['track']['wx'][-1]),abs(widths[1]-c['track']['wy'][-1]))
    f_error=abs(fs[-1]-c['track']['fidelity'][-1])
    assert width_error<1e-9 and f_error<1e-9 and abs(fs[0]-fs[1])<1e-10
    checks.append(dict(case=name,width_error=width_error,fidelity_error=f_error,quadrature_convergence=abs(fs[0]-fs[1])))
result=dict(passed=True,method='Closed Gaussian velocity moments and independent 80/160-point Gauss-Hermite quadrature of separable complex overlaps',
 approximation='Continuous Gaussian spectrum; lattice alias tails negligible for sigma/a>=4 and centers far from BZ boundaries',cases=checks)
(B/'checks_independent.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('Independent checks passed for',len(checks),'cases. Max F error:',max(x['fidelity_error'] for x in checks))
