# Physical notation and fixed-coordinate propagation displays

These assets reuse the verified wavefields and numerical trajectories from
`../curvature-design/`. Their values and simulation parameters are unchanged.
The original derivation PDF and previous figures are preserved.

## Display contract

- Physical position is x,y. Wavevector is kx,ky. The lattice spacing a appears
  explicitly in neighbor positions, phases and band derivatives.
- Excitation energy is epsilon=E_k-E_F. Time is t, with hbar retained in evolution.
  Numerical chart ticks use hbar/Jx for time, a for position/width, and 1/a for
  spectral width. No extra q,n,e,tau,s or eta aliases appear on the slides.
- H denotes the Hamiltonian only. Band derivatives are written explicitly.
- Initial packet width sigma is each position-probability RMS width. Its spectral
  probability RMS width is approximately 1/(2 sigma).
- Gaussian curvature uses the scaled graph axes (kx*a,ky*a,epsilon/Jx). This
  preserves the previous numerical curvature and avoids adding unlike units.
  The zeros and signs survive positive axis scaling; curvature is not Berry
  curvature and is not sufficient to predict two-dimensional preservation.
- Position means use angle brackets consistently in maps and explanatory text.

## Propagation GIFs

`g14_lab_probability_animation.gif` and `g15_lab_real_animation.gif` use fixed
laboratory x,y axes spanning -35a to 225a in each direction, over t=0..180 hbar/Jx.
They do not subtract the moving centroid. Dashed paths show actual probability
centroids and a dotted circle marks the initial envelope. The real-amplitude
animation adds a separately labeled centroid-following inset to resolve crests.
All maps use actual sites, a fixed initial phase and fixed initial peak scales.

Both have 61 frames. The minimum probability inside the fixed viewport is
0.9999999988732283. GIF decoding is verified; native PowerPoint playback has not
been tested. The PPTX embeds both complete frame sequences. The PDF is static.

## Reproduce

From the project root run, in this order:

1. `python figures/midterm-report/notation/generate_notation.py`
2. `python figures/midterm-report/notation/generate_lab_animations.py`

The first runner reuses the existing scientific plotting functions with physical
labels and regenerates equations and diagrams. It reads the original NPZ and
JSON data. The second runner adds the fixed-laboratory animations to its manifest.
`checks.json` checks physical derivative/unit conversion and the original data
checksum. `checks_lab_animation.json` records viewport mass, limits and frames.
