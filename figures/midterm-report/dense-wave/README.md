# Dense lattice-wave figures

This supplement makes the carrier oscillations visible in the revised midterm presentation. It uses the existing exact one-magnon propagator from `../common.py` and does not change the original figure package.

## Reproduce

From the project root:

```powershell
python figures/midterm-report/dense-wave/generate_dense_wave.py
```

Dependencies: NumPy, SciPy, Matplotlib, and Pillow. The script produces six PNG/SVG/PDF figures, two GIFs, `dense_wave_data.npz`, `manifest.json`, and `checks.json`. Figure captions and file paths are in `manifest.json`. Chinese fonts use Microsoft YaHei with DejaVu Sans as the fallback.

## Physical model and display contract

- Coordinates are lattice indices, `x/a` and `y/a`; `q=ka`, `tau=Jx*t/hbar`, and `eta=Jy/Jx`.
- The dispersion is `epsilon/Jx = 1-cos(qx) + eta*(1-cos(qy))`, with `S=1/2`, zero applied field, and the common ground-state phase removed.
- The complex initial state is `psi(x,y) proportional to exp[-(x^2+y^2)/(4 sigma^2)] exp[i(q0x*x+q0y*y)]`, normalized to unit total probability. Thus `sigma=10a` is the initial probability RMS width in each direction.
- Every field is computed on a `512 x 512` periodic lattice. Increasing `N` enlarges the periodic box; it does not change the lattice spacing or the number of samples per physical wavelength.
- Gaussian cases use `q0=(0.7,0)` or `(0.7,0.7)` and `eta=1` or `0.3`. The carrier period along a direction with `q0=0.7` is about `8.98a`. A local spatial view shows several well-resolved periods without displaying the largely empty box.
- Heatmaps use the exact site values and `interpolation='nearest'`. Line plots connect actual site samples only as a reading aid. There is no spatial smoothing, interpolation onto a finer lattice, or framewise normalization.
- `A0=max|psi(0)|` and `P0=A0^2` are fixed for all Gaussian panels and frames. The corresponding color ranges are `Re(psi)/A0 in [-1,1]` and `P/P0 in [0,1]`.
- `w04` shows the raw delta-state amplitude and probability at `tau=24`, with fixed color limits `[-0.06,0.06]` and `[0,0.0036]`. The data stay inside these limits.
- `Re(psi)` is phase dependent and is displayed in one fixed convention. It is a probability-amplitude component, not the transverse-spin expectation of a fixed one-magnon state. The probability `|psi|^2` answers where a spin flip can be found. The real amplitude reveals the coherent carrier structure that the probability envelope hides.

## Files

| ID | Content |
|---|---|
| w01 | The same complex Gaussian state: real amplitude, probability, and an actual lattice line cut |
| w02 | Real-amplitude maps at `tau=0,30,60` with fixed window and color range |
| w03 | Actual line cuts plotted relative to the probability centroid; no rephasing |
| w04 | Delta-state interference: real amplitude and probability at `tau=24` |
| w05 | Equal initial diagonal carrier propagated with `eta=1` and `0.3` |
| w06 | Local lattice resolution and the approximately nine-site carrier period |
| w07 | Real-amplitude/probability animation over `tau=0..60`, 61 frames |
| w08 | Anisotropy animation over `tau=0..60`, 61 frames |

## Data layout

`dense_wave_data.npz` retains complex amplitudes, not just rendered intensities.

- `x`: lattice coordinates, length 512.
- `snapshot_times`: `[0,30,60]`.
- `{case}_psi`: complex128, shape `(3,512,512)`, indexed `(time,y,x)`.
- Cases: `x_eta1`, `x_eta03`, `diagonal_eta1`, and `diagonal_eta03`.
- `delta_tau24`: complex128, shape `(512,512)`.
- `trajectory_times`: 61 equally spaced times, `0..60`.
- `{case}_trajectory_{quantity}`: complete moment trajectories for `norm`, `cx`, `cy`, `wx`, `wy`, `edge_mass`, `t`, and `fidelity`.
- `fidelity` compares the evolved complex state with its translated initial state using the exact spectral mean velocity. It is not a framewise phase-adjusted field display.

## Numerical evidence

The generator asserts all checks before writing the figures. `checks.json` contains the measured errors and parameters:

1. Unit total probability over all recorded Gaussian times.
2. Probability centroids and variances against exact spectral moments: mean position grows as `tau*<v>`, and variance as `sigma^2 + tau^2 Var(v)` for these initially unchirped Gaussian states.
3. The `tau=60` complex amplitudes on `N=512` against the central `512 x 512` crop of an `N=1024` run with identical physical spacing and initial condition.
4. The delta-state propagator against `exp[-i(1+eta)tau] i^(m+n) J_m(tau) J_n(eta*tau)`, with its exact probability variance `tau^2/2` at `eta=1`.

In the delivered run, the maximum norm error was `1.33e-15`, the largest `N=512` versus `1024` amplitude error was `5.82e-17`, and the Bessel amplitude error was `2.10e-16`. Edge probability stayed below `1.06e-30` for the Gaussian cases. These establish numerical consistency for the stated finite-time linear model; they do not establish a strict shape-preserving solution.

All six static PNGs and three extracted times from each GIF were visually inspected. The GIF decoder also reads all 61 frames. The audit contact sheet is `qa_animation_frames.png`; it is for review, not a scientific plot to substitute for the originals.
