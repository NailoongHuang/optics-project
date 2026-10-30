# Midterm figure and simulation package

## Scope

Explain the physical picture of the spin-1/2 one-magnon sector of the uniform
nearest-neighbor ferromagnet. The source is `Note/single_magnon_derivation/main.tex`.
Use h=0 and the exact dispersion epsilon=Jx(1-cos kx a)+Jy(1-cos ky a).
All new output lives here; existing source notes and figures remain authoritative.

## Conventions

- Dimensionless position n=r/a, momentum q=ka, time tau=Jx*t/hbar, eta=Jy/Jx.
- Normalize the one-magnon wavefunction to one; plotted probability is |psi|^2.
- psi removes the global E_F phase; physical probabilities are unchanged.
- Exact Fourier evolution on a periodic lattice; independently bound boundary effects.
- Gaussian amplitude exp[-x^2/(4 sigma_x^2)-y^2/(4 sigma_y^2)] exp(i q0.r),
  so sigma is the initial probability RMS width for well-resolved wide packets.
- Deterministic calculations; any random numerical checks record their seeds.

## Deliverables

1. Dispersion, equal-energy curves, slopes, velocities, and low-q limits.
2. Local-flip propagation, anisotropy, marginals, ballistic spreading, analytic controls.
3. Gaussian wavepackets, carriers, spectra, motion, broadening, bandwidth, and anisotropy.
4. A limited optional extension on zero quadratic dispersion, clearly labeled.
5. PNG/SVG/PDF figures, GIF animations, data/configurations, a reading guide,
   an offline HTML gallery, and a merged figure PDF.

## Verification

Reuse the existing model and run its regression suite. Compare new propagation with
independent Bessel-function, sparse-matrix, and analytic moment results. Compare
enlarged lattices at fixed spacing and monitor edge probability. Validate exported
animations through the final frame and visually inspect every static figure via
contact sheets, with full-resolution inspection of dense or questionable pages.
An independent agent reviews scientific interpretation and numerical evidence.

## Status

- Complete: 12 dispersion figures, 13 local-flip figures, 14 Gaussian figures,
  and 8 animations. Every static figure has PNG/SVG/PDF exports.
- Complete: exact Fourier simulations, saved arrays, parameter manifests, and
  model-source hashes. The original 10 regression checks and 27 independent
  numerical controls passed, as did each figure group's additional checks.
- Complete: independent scientific review; all identified issues resolved.
- Complete: full production runner executed, 40-page PDF with captions/bookmarks,
  offline searchable gallery, figure index, physical explanation and reproduction guide.
- Complete: all 39 static figures inspected; all 528 animation frames decoded and
  every animation's first/middle/last frames viewed. All 40 PDF pages rendered
  with Poppler and inspected via contact sheets, with selected full-page review.
- Complete: browser filtering, search and animation modal verified in the actual
  gallery. See QA.md and checks_exports.json for delivery evidence.
