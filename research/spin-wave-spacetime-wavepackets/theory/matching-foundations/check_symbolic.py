"""Exact algebra checks for the cosine-band spectral-matching research note.

The analytic proofs are in matching-foundations.md. These checks establish
only the listed algebraic identities, not novelty or an experimental result.
"""
from pathlib import Path
import json
import sympy as s

ROOT=Path(__file__).resolve().parent
x,y,p,r,ux,uy,b,t=s.symbols('x y p r ux uy b t',real=True)
eta=s.symbols('eta',positive=True)
energy=1-s.cos(x)+eta*(1-s.cos(y))
cross={x:s.pi/2,y:s.pi/2}
velocity=s.Matrix([s.diff(energy,x),s.diff(energy,y)]).subs(cross)
offset=(1+eta)*(1-s.pi/2)
delta=energy-x-eta*y-offset
cross_residual=s.trigsimp(delta.subs({x:s.pi/2+p,y:s.pi/2+r}))
branch_argument=(1+eta-s.cos(x)-ux*x-b)/eta
axis_branch_residual=s.simplify((energy-ux*x-b).subs(y,s.acos(branch_argument)))
c=eta**(-s.Rational(1,3))
anisotropic_leading=s.expand(s.series((s.sin(p)-p)+eta*(s.sin(-c*p)+c*p),p,0,4).removeO())
m1,m2,m3,m4=s.symbols('m1 m2 m3 m4',real=True)
overlap=1-s.I*m1*t-m2*t**2/2+s.I*m3*t**3/6+m4*t**4/24
fidelity=s.expand(overlap*s.conjugate(overlap))
checks={
    'crossing_velocity':list(velocity),
    'crossing_hessian':s.hessian(energy,(x,y)).subs(cross).tolist(),
    'third_derivative_x':s.diff(energy,x,3).subs(cross),
    'third_derivative_y':s.diff(energy,y,3).subs(cross),
    'crossing_residual_identity':s.simplify(cross_residual-((s.sin(p)-p)+eta*(s.sin(r)-r))),
    'isotropic_curve_energy':s.trigsimp(energy.subs({eta:1,y:s.pi-x})),
    'isotropic_curve_matching_residual':s.trigsimp((energy-x-y-(2-s.pi)).subs({eta:1,y:s.pi-x})),
    'isotropic_curve_spectral_phase':s.simplify((s.pi/2+p)*x+(s.pi/2-p)*y-(s.pi*(x+y)/2+p*(x-y))),
    'axis_arccos_branch_residual':axis_branch_residual,
    'fixed_y_level_function_second_derivative':s.diff(energy-ux*x-uy*y-b,x,2),
    'anisotropic_cubic_slope_residual':s.simplify(anisotropic_leading),
    'anisotropic_energy_linear_coefficient':s.simplify(1-eta*c),
    'fidelity_quadratic_coefficient_residual':s.simplify(fidelity.coeff(t,2)+(m2-m1**2)),
    'fidelity_cubic_coefficient':s.simplify(fidelity.coeff(t,3)),
}
zero_keys=['crossing_residual_identity','isotropic_curve_matching_residual','isotropic_curve_spectral_phase','axis_arccos_branch_residual','anisotropic_cubic_slope_residual','fidelity_quadratic_coefficient_residual','fidelity_cubic_coefficient']
expected={
    'crossing_velocity':[1,eta],
    'crossing_hessian':[[0,0],[0,0]],
    'third_derivative_x':-1,
    'third_derivative_y':-eta,
    'isotropic_curve_energy':2,
    'fixed_y_level_function_second_derivative':s.cos(x),
    'anisotropic_energy_linear_coefficient':1-eta**s.Rational(2,3),
}
failures=[key for key in zero_keys if checks[key]!=0]
failures.extend(key for key,value in expected.items() if checks[key]!=value)
out=dict(date='2026-10-21',engine='SymPy '+s.__version__,assumptions=['real wavevectors, target velocity and offset','eta>0','arccos branch is physical only where its argument is in [-1,1]'],results={k:str(v) for k,v in checks.items()},failures=failures,scope='Exact algebra only; Fubini, Fourier uniqueness, monotonicity and finite-norm conclusions require the written proofs.')
(ROOT/'symbolic-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
if failures: raise SystemExit(1)
