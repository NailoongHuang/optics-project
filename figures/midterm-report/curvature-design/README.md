# Gaussian curvature and preliminary wave-packet design

The model is the exact spin-1/2 one-magnon dispersion with positive exchange,
zero external field and no damping. Coordinates are q=ka, e=(E-E_F)/Jx,
eta=Jy/Jx>0 and tau=Jx t/hbar. Gaussian curvature refers to the Euclidean
dimensionless graph R=(qx,qy,e), not Berry curvature. Numerical curvature values
depend on axis scaling. Zero loci and signs survive positive axis rescaling.

The curvature is eta cos(qx)cos(qy)/(1+sin(qx)^2+eta^2 sin(qy)^2)^2.
Its zero locus is qx=pi/2+n*pi OR qy=pi/2+m*pi. A single zero line removes
only one quadratic spectral-phase coefficient. The crossing removes both,
but cubic and higher orders remain. Hessian eigenvalues are not generally
the graph principal curvatures.

## Controlled experiments

- A=(0.7,0.7), B=(pi/2,0.7), C=(pi/2,pi/2). Six main cases share initial
  probability RMS width sigma=6a, N=512, tau=0..180, and eta=1 or 0.3.
  This is an equal-width, equal-time comparison, not equal-distance.
- Three crossing controls use sigma=4a,6a,8a, N=1024 and tau=0..360.
  Different initial widths consume different spatial resources.
- Evolution uses the full cosine band in the exact spectral exponential.
  No finite time step or quadratic/cubic truncation generates the data.
- Total probability is one. Re(psi) follows a fixed initial phase convention
  after removing E_F's global phase. No frame is rephased or normalized by its
  current peak. Re(psi) is not the transverse spin expectation in a fixed
  one-magnon number state.
- Fidelity is the squared complex overlap with each packet's own initial state
  translated at its spectral mean velocity. It includes phase, not just density.

## Reproduce and verify

Run `python figures/midterm-report/curvature-design/generate_design.py` from the
project root. The script reuses `common.py`, records actual FFT spectra,
trajectories and complex snapshots in `design_data.npz`, saves native chart data
in `chart_data.json`, and records figure conventions in `manifest.json`.
Scientific figures also have editable SVG and vector PDF exports.

`checks_symbolic.json` independently checks the first/second fundamental forms
with SymPy. `checks.json` checks finite-difference curvature, periodicity,
normalization, velocity moments, packet variances and box enlargement.
The enlarged-box comparison holds a fixed lattice constant: N enlarges the box
and does not refine the lattice. The derivative check records its random seed.

Extended-zone maps cover [-3pi,3pi]^2, or 3 by 3 Brillouin zones. They show
periodic continuation of the same band. The eta=1 and eta=0.3 curvature maps
use different explicitly labeled ranges; read numerical colorbar values.
The zero-only energy plot uses exact analytic lines, not a threshold mask.

The main conclusion is finite-time reduction of broadening near the crossing.
It does not establish permanent dispersion-free propagation. Material parameters,
damping, preparation and equal-distance optimization remain future work.
