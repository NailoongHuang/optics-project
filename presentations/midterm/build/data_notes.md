# Midterm presentation: data audit and figure pairing notes

This audit reads the three saved NPZ files and the associated manifests and verification records. It does not regenerate simulations or infer unrecorded results. Full arrays for native PowerPoint charts and per-value source keys are in `data_facts.json`.

## Conventions that must appear in the deck

- Use q = ka, tau = Jx t / hbar, eta = Jy / Jx; plot energy as epsilon / Jx, lengths in a, and velocity in Jx a / hbar.
- The dynamic figures use a normalized S = 1/2 one-magnon state, h = 0. The common ground-state phase has been removed.
- Gaussian sigma is the RMS width of probability: psi0 is proportional to exp[-(nx^2+ny^2)/(4 sigma^2)] exp(i q0 dot n). It is not FWHM.
- A03 anisotropic dispersion has eta = 0.35. B/C propagation comparisons use eta = 0.3. Retain actual values in each caption.
- Quantization is along +x in the project figures: <Sx_mn> = 1/2 - P_mn, and <Sy> = <Sz> = 0 for a one-magnon number state.

## Best quantitative callouts

### Gaussian packet at tau = 60

| Saved case | sigma | q0 | eta | <x>/a | <y>/a | sigma_x/a | sigma_y/a | F |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| qzero | 4 | [0.0, 0.0] | 1 | -0.000000 | -0.000000 | 8.448679 | 8.448679 | 0.534307 |
| qright | 4 | [0.7, 0.0] | 1 | 38.352261 | -0.000000 | 6.969652 | 8.448679 | 0.595100 |
| qdiagonal | 4 | [0.7, 0.7] | 1 | 38.352261 | 38.352261 | 6.969652 | 6.969652 | 0.662811 |
| qdiagonal_eta03 | 4 | [0.7, 0.7] | 0.3 | 38.352261 | 11.505678 | 6.969652 | 4.351074 | 0.796139 |
| sigma3 | 3 | [0.7, 0.0] | 1 | 38.119924 | 0.000000 | 8.152530 | 10.308878 | 0.318978 |
| sigma6 | 6 | [0.7, 0.0] | 1 | 38.519082 | 0.000000 | 7.110505 | 7.799179 | 0.880103 |
| sigma10 | 10 | [0.7, 0.0] | 1 | 38.604775 | -0.000000 | 10.259453 | 10.439231 | 0.982530 |
| extension_ordinary | 3 | [0.7, 0.7] | 1 | 38.119924 | 38.119924 | 8.152530 | 8.152530 | 0.382296 |
| extension_inflection | 3 | [1.5707963267948966, 1.5707963267948966] | 1 | 59.172427 | 59.172427 | 3.217286 | 3.217286 | 0.977104 |
| extension_inflection_sigma2 | 2 | [1.5707963267948966, 1.5707963267948966] | 1 | 58.153994 | 58.153994 | 3.256900 | 3.256900 | 0.832886 |

Source: `figures/midterm-report/c-gaussian/gaussian_simulation_data.npz`; values come from keys `<case>_cx`, `<case>_cy`, `<case>_wx`, `<case>_wy`, `<case>_fidelity` at index 30; `<case>_t[30] = 60`. Parameters are stored in `parameters_json`.

The sigma = 4 right-moving packet provides a useful numerical check on the group-velocity explanation:

- Center-wavevector approximation: sin(0.7) = 0.6442176872.
- Measured centroid speed: 38.3522607253 / 60 = 0.6392043454.
- Difference in predicted displacement at tau = 60: 0.30080050896 a.
- Explain the difference as finite spectral width. The exact centroid speed is the spectrum-weighted average <sin qx>. Do not label the center value exact.

The initial-width comparison has a particularly clear result: sigma_x(60)/sigma = 2.71751, 1.18508, and 1.02595 for sigma = 3, 6, and 10. All states have total probability 1, but their initial spatial resources differ. This supports a bandwidth explanation, not a same-resource optimization claim.

For q0 = (0.7,0.7), sigma = 4, eta = 1 and 0.3 give directions 45 degrees and 16.699244 degrees. The carrier direction remains 45 degrees. In the eta = 0.3 example, the centroid is (38.3523, 11.5057) a, so the direction change has direct data support.

The equal-width inflection comparison uses sigma = 3 in both cases:

- Ordinary q0 = (0.7,0.7): sigma_x(60)/a = 8.15253, F(60) = 0.382296.
- Inflection q0 = (pi/2,pi/2): sigma_x(60)/a = 3.21729, F(60) = 0.977104.
- F is the squared complex-wavefunction overlap with the initial packet translated at its own spectral mean velocity. It includes phase deformation and is not only an intensity-shape metric.
- C14 changes sigma to 2 to make cubic deformation visible. Label it a separate example; do not compare its F = 0.832886 to C13 as an equal-width test.

### Local flip at tau = 24

| eta | FFT sigma_x/a | FFT sigma_y/a | FFT P00 |
|---:|---:|---:|---:|
| 0.0 | 16.97056275 | 0.00000000 | not saved as return curve |
| 0.3 | 16.97056275 | 5.09116882 | 0.0002752913406 |
| 1.0 | 16.97056275 | 16.97056275 | 9.997255791e-06 |

Source: `local_flip_data.npz`; widths use `stats_eta_0p0/0p3/1p0_wx/wy[48]`, `moment_times[48]=24`. Return probabilities use `return_eta_0p3/1p0[240]`, `return_times[240]=24`.

Separate analytic prediction from those computed values: sigma_x/a = tau/sqrt(2), sigma_y/a = eta tau/sqrt(2), and P00 = J0(tau)^2 J0(eta tau)^2. Here J0 denotes the Bessel function, not exchange energy. At eta = 1, the width is 16.97056 a while the main group-velocity front scale is 24 a. These are distinct notions of spread. The front has nonzero outside tails.

The eta scan at fixed tau = 24 gives:

| eta | FFT sigma_x/a | FFT sigma_y/a | sigma_y/sigma_x |
|---:|---:|---:|---:|
| 0 | 16.970563 | 0.000000 | 0.000000 |
| 0.3 | 16.970563 | 5.091169 | 0.300000 |
| 1 | 16.970563 | 16.970563 | 1.000000 |
| 1.5 | 16.970563 | 25.455844 | 1.500000 |

Source: `eta_scan` and `eta_scan_widths[:,0:2]`. The columns are x then y. The scan includes 31 values from 0 to 1.5.

### Dispersion and approximation

The saved A surfaces have an 81 x 81 grid, including the Brillouin-zone endpoints. Exact energy ranges are [0,4] for eta = 1 and [0,2.7] for eta = 0.35. The equal color scale [0,4] supports comparison.

A09 gives axial quadratic-energy relative errors of 1% at q = 0.34537558 and 5% at q = 0.76329961. These are energy-error thresholds, not wavepacket-fidelity guarantees; propagation phase error accumulates with time.

## Recommended editable charts

The JSON contains complete saved numerical series in `native_chart_series`:

| Chart key | Recommended rendering | Use |
|---|---|---|
| gaussian_centroid_x | XY lines, sparse numerical markers | Motion and finite-bandwidth group velocity |
| gaussian_rms | XY lines | Translation versus spreading |
| width_relative | XY lines | sigma = 3,6,10 normalized broadening |
| diagonal_trajectory | XY scatter lines, equal physical axis scale | eta = 1 / 0.3 direction comparison |
| gaussian_anisotropy_width | XY lines | Same initial state, directional broadening |
| local_flip_rms_x, local_flip_rms_y | XY lines + sparse markers | Ballistic law |
| eta_scan | XY lines + numerical markers | Controlled exchange anisotropy |
| return_probability | XY lines, logarithmic y | Coherent return oscillation |
| inflection_width, inflection_fidelity | XY lines, F axis [0,1] | Future preservation direction |
| a02-isotropic-surface_axial_cuts, a03-anisotropic-surface_axial_cuts | XY lines | Energy vs q without perspective ambiguity |
| long_wave_relative_error | XY curve; add 1% and 5% horizontal guides | Validity of quadratic approximation |

Use the full two-dimensional probability maps, spacetime heatmaps, contour/arrow fields, and 3D surfaces as original scientific images. They encode scales and visual structures that native line charts cannot retain. Cropping panels is reasonable if axis labels and colorbar meaning remain available. Use the pre-made full figure when panel association is needed.

## Suggested figure pairings


- **模型到色散**: a01-lattice, a02-isotropic-surface, a04-axial-cuts. Lattice exchange schematic + band surface + axial cuts establish how Jx,Jy enter propagation.
- **局域初态为何四向展开**: b01-initial-local-flip, b02-flat-spectrum, b03-early-neighbor-spreading. Local position state has broad q support; show early neighbors before late-time interference.
- **前沿与RMS是两种尺度**: b04-isotropic-late-snapshots, b07-spacetime-isotropic, b09-ballistic-rms. Pair density map and spacetime with quantitative RMS, keeping front scale |x|~tau distinct from rms tau/sqrt2.
- **各向异性可定量控制**: b05-anisotropy-comparison, b11-anisotropy-scan. Keep tau=24 fixed; width ratio equals eta for this local-flip model.
- **局域概率减少仍守恒**: b10-return-probability, b12-probability-to-spin. Return oscillations and longitudinal spin deficit connect probability to observable.
- **相位控制传播方向**: c01-carrier-envelope-spectrum, c05-carrier-directions, c06-centroid-velocity. Use same initial probability envelope; carrier shifts spectrum and centroid motion. Verify c01 ID in manifest before placing.
- **移动与展宽分开测量**: c04-moving-gaussian, c07-comoving-marginals, c09-rms-exact-moments. Snapshots + comoving cuts + RMS curve distinguish translation and deformation.
- **宽初态与窄频谱**: c02-space-bandwidth, c08-width-comparison. Compare sigma=3,6,10 with declared initial resources and normalized probability.
- **传播方向不必平行波矢**: a10-wavevector-velocity-direction, c10-anisotropy-direction, c11-anisotropy-width. Use eta=.3 Gaussian comparison as quantitative example; A10 has its own parameters.
- **后续保形研究入口**: a11-curvature-and-cubic, c13-extension-inflection, c14-extension-cubic-distortion. C13 same sigma=3: fair carrier comparison; C14 sigma=2 is independent visibility example, not same-resource performance comparison.

## Verification evidence and limits

- Local-flip FFT vs Bessel probability maximum error: 5.5511151231e-16. Complex-amplitude L2 error: 1.4581102181e-14. Grid enlargement N = 256 to 512 L2 change: 1.0030936630e-14. Source: `checks_b.json.summary`.
- Gaussian cases: maximum norm error 6.6613381478e-16; maximum spectral-power change 1.7347234760e-17; maximum N = 256 versus 384 amplitude L2 change 2.3014879403e-9 (sigma = 10); maximum edge probability 5.6970429077e-14. Source: `checks_c.json.cases`.
- Independent sparse real-space exponential vs spectral propagator: L2 error 3.4042761482e-15, N = 12, eta = 0.37, tau = 4.3. Source: `checks_independent.json.results[0]`.
- These checks support the specified model and time windows, not experimental material validity or nonlinear spin dynamics.
- The infinite-lattice unchirped Gaussian variance law is exact in spectral moments; a general chirped state additionally has 2 tau Cov_sym(n,v).
- The continuous Gaussian formula <vx> approximately equals exp[-1/(8 sigma^2)] sin(q0x). A sampled lattice Gaussian is not literally a continuous Gaussian; use the actual saved trajectory as quantitative evidence.
- Zero quadratic curvature at q = pi/2 leaves cubic and higher phase terms. Report improved finite-duration preservation only.
- The square lattice with Jx = Jy has fourfold symmetry; do not assert exact radial isotropy.
- Return probability decreases and revives under unitary dynamics. It is not a decay law, damping rate or evidence of magnon loss.
- Avoid interpreting <Sy>=<Sz>=0 as no excitation: the one-magnon state has a longitudinal spin deficit encoded by P.

## Source artifacts

- `figures/midterm-report/a-dispersion/data/dispersion_arrays.npz`
- `figures/midterm-report/b-local-flip/local_flip_data.npz`
- `figures/midterm-report/c-gaussian/gaussian_simulation_data.npz`
- `manifest_a.json`, `manifest_b.json`, `manifest_c.json`
- `checks_a.json`, `checks_b.json`, `checks_c.json`, `checks_independent.json`
- `common.py`, `generate_local_flip.py`, `generate_gaussian.py` were read to verify key semantics and analytic versus numerical origin.
