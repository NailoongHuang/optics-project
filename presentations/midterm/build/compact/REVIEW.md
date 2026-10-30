# Compact deck independent review

## Status

Completed: the current 18-slide source, authoring renders, and all 18 final exported-PPTX re-import renders have been independently reviewed. All identified corrections are closed. The old 35-slide deck was used only for diagnosis, not as completion evidence.

## Evidence inspected

- `Note/single_magnon_derivation/main.tex`, complete source of the current five-page theory PDF.
- `figures/midterm-report/THEORY.md`, current probability, phase, units, and propagation conventions.
- `presentations/midterm/build/deck.mjs` and `slide_spec.json`, previous 35-slide authoring source.
- Previous full-size renders 02, 06, 15, and 20, only to diagnose the requested change.

## Scientific conditions for the revision

1. The source quantization axis is +x. For a fixed one-magnon state, the local expectations are <Sx_i> = 1/2 - P_i and <Sy_i> = <Sz_i> = 0. Re(psi) is a component of a complex probability amplitude under a specified phase convention, not the transverse local magnetization of this state.
2. Define psi = exp(i E_F t / hbar) c and retain the full excitation dispersion in its time evolution. Re(psi) depends on a global phase; set the initial phase explicitly and do not silently remove another time-dependent phase for display. P = |psi|^2 is phase independent.
3. Increasing N at fixed lattice spacing enlarges the periodic domain and refines the discrete Fourier grid. It does not increase the number of lattice samples per carrier wavelength. With q0x = 0.7, the x carrier wavelength is 2 pi / 0.7 = 8.976 lattice spacings. Full-site plotting, a wider envelope, and an appropriate local viewport make the oscillations legible.
4. A probability heatmap suppresses carrier phase by construction. Pair Re(psi) and P on matching views to show oscillation and localization together. State the plotted quantity and keep color scales fixed across time when comparing amplitudes.
5. Sigma is the probability RMS width in lattice-site units. The initial amplitude exponent is -n^2/(4 sigma^2). A new sigma = 10 display example and older sigma = 3 or 4 broadening examples have different resources and must be labeled as separate cases.
6. Finite-bandwidth centroid velocity is the spectral mean of sin(qx), eta sin(qy). The group velocity evaluated at q0 is a narrowband approximation. At sigma = 10 and q0x = 0.7, the broad-envelope expression gives mean ux = sin(0.7) exp[-1/(8 sigma^2)] approximately 0.6434.
7. Verify new propagation arrays with norm conservation and a larger-domain comparison before claiming that periodic boundaries are negligible. Exact spectral time evolution removes time-step integration error, but not finite-domain effects.
8. Vanishing quadratic curvature does not eliminate cubic distortion. A compact exploratory ending must retain the finite-bandwidth and finite-time qualification.

## Observed cause of weak wave appearance in the previous deck

- Previous slide 02 uses an initial single-cell probability block as the main visual; this cannot show a carrier wave.
- Previous slide 06 uses a 5 by 5 lattice as a local model schematic, not a simulation grid. It needs that distinction, not a claim that its physical discretization was refined.
- Previous slide 20 shows probability, unwrapped phase, and spectral weight, but no signed amplitude. Its content explains a carrier without directly showing wave peaks and troughs.
- Repeated full plot titles, plot footnotes, lower explanatory blocks, and separate conclusion bands reduce the actual image area in several slides. Compacting should enlarge evidence rather than just reduce the font size.

## Suggested content merge

Retain the source derivation through exchange integrals, matrix/eigenstates, operator matching, the one-flip sector, EOM, and plane waves. Merge related simulation evidence into coherent comparisons: local-flip snapshots with anisotropy; front with Bessel/RMS validation; carrier with Re(psi), P, and spectrum; translation with centroid velocity; spreading with width dependence. Keep one bounded curvature extension and one closing page. A total of 18 slides is feasible without dropping the derivation-to-observation connection.

## New simulation evidence reviewed

The new `figures/midterm-report/dense-wave/generate_dense_wave.py` has been read in full. The actual `checks.json` records passing norm, exact moment, and domain-size checks for four Gaussian cases, plus a Bessel complex-amplitude check for the point excitation. The largest reported N=512 versus N=1024 complex-amplitude difference at tau=60 is 5.82e-17; the maximum edge probability among the recorded Gaussian trajectories is 1.06e-30. The point-excitation Bessel amplitude difference at tau=24 is 2.10e-16. These results check the stated uniform model only.

Full rendered assets inspected so far: w01, w02, w04, and w06. The Gaussian signed-amplitude maps now clearly display multiple carrier peaks and troughs, while matching probability maps correctly show the localized envelope. The w06 sampling figure explicitly preserves one marker per physical lattice site and labels the x-projected wavelength. No scientific correction is needed in those assets. Final slide-level review remains pending.

Additional new assets w03 and w05 were inspected individually. The co-moving cross-sections correctly retain carrier phase evolution after subtracting the probability-centroid position. The anisotropy maps use identical initial carriers and amplitude scales, with centroid arrows matching the reported (38.605, 38.605) and (38.605, 11.581) positions at tau=60. The directional labels and color scale are consistent with the arrays and source conventions.

## First current-deck review: 18 slides

The actual current `compact.mjs`, `slide_spec.json`, and all 18 individual `renders/slide-01.png` through `slide-18.png` were reviewed. Every slide was opened at full slide size. No old-deck review was used as a substitute.

The deck is exactly 18 slides, has a coherent source-equations-to-propagation sequence, and now displays carrier oscillations clearly. The principal numerical claims are consistent with the new saved trajectories and the older source arrays. No clipping, missing image, or text/figure overlap was observed in the first renders. The following corrections were requested from the author and still require verification in the next render:

| Slide | Finding | Requested correction |
|---|---|---|
| 05 | u is introduced without its dimensionless definition; tau is used on the next page but is not defined until page 15. | Add visible definitions q=ka, tau=Jx*t/hbar, e=epsilon/Jx, u=hbar*v/(Jx*a)=grad_q e. |
| 06 | A0 and P0 appear on axes but are defined only in notes. The c-to-psi phase relation is also only in notes. | Show A0=max|psi(0)|, P0=A0^2 and psi=exp(i E_F t/hbar)c in the visible slide. Retain the existing transverse-spin qualification. |
| 08 | Right chart is only sigma_y across eta, while its title says two directions. | Rename to y-direction RMS width. |
| 09 | Main formula uses physical sigma, while inherited C02 legends write the numerical site widths as sigma=3,6,10. | Add a visible statement that the figure legend numbers denote sigma/a, or relabel the legend with physical lengths. |
| 10 | Caption calls the current envelope a dashed line, while the current envelope is orange solid and the initial envelope is gray dashed. | Describe the actual colors and line styles. |
| 12 | Left marginal distribution is a sigma=4a case, only specified in notes; right chart is sigma=3a,6a,10a. | State the left/right widths visibly and add a to the native chart legend. |
| 13 | Carrier-normal direction is stated without a narrowband/local qualification. | Prefer 'near the center, the fringe normal approximately follows the carrier' to avoid asserting a constant local phase gradient throughout the evolved finite-bandwidth state. |
| 15 | n in the variance relation has not been defined visibly. | Define n=x/a, and state the relation componentwise. |
| 17 | Middle error-map x-axis tick labels 0,20,40 are visually crowded, with the latter two nearly joined. | Reduce x ticks or enlarge the error-map panel. |

Optional explanatory improvement: slide 16 can include d2e/dqx2=cos(qx) and the analogous y expression near the top so the special pi/2 carrier is directly connected to the title. Its finite-time claim, equal initial widths, fidelity definition, and cubic-residual qualification are already correct.

Scientific checks by page group:

- 01-04: The x-projected wavelength, exchange sign/factor, one-flip closure, energy offset, and plane-wave substitution match the original source. The local 5 by 5 diagram is explicitly identified as a model schematic.
- 05-09: Group velocity, phase-dependent real amplitude versus probability, full-band point excitation, main-front versus RMS distinction, and Gaussian amplitude exponent are correct. Definitions and width-label issues above affect self-contained readability.
- 10-14: Co-moving coordinates, spectral-mean velocity 0.643413, endpoint x=38.6048a, width ratios 2.718/1.185/1.026, directional angles 45 and 16.70 degrees, and endpoint y=11.5814a at eta=0.3 match the saved data. The two animations are present as images in the source; actual PowerPoint playback has not been tested by this review.
- 15-18: The variance statement preserves its zero-covariance condition. The equal-width inflection comparison and reported fidelities 0.3823/0.9771 agree with the saved data. Numerical error types and finite-model limitations are stated consistently.

## R2 correction review

The actual R2 source and full-size rendered slides 05, 06, 08, 09, 10, 12, 13, 15, 16, and 17 were re-opened after the 22:36 build. All nine requested correction items are now closed:

- Units, time scale, and dimensionless speed are visibly defined on slide 05.
- Phase and A0/P0 scaling are visible on slide 06; the fixed-magnon transverse-mean qualification remains.
- The page 08 right chart title now accurately identifies y RMS width.
- The page 09 footer explains inherited site-width legends; page 12 separately labels the 4a marginal case and the 3a/6a/10a width scan, whose editable legend includes a.
- Page 10 matches the actual current and initial envelope line styles.
- Page 13 qualifies the carrier-normal statement near the center.
- Page 15 defines n=x/a and states that the variance formula applies direction by direction under the zero-covariance condition.
- Page 17 replaces the crowded two-panel source image with a readable Bessel/FFT marginal comparison while preserving the independent numerical-error table.
- The optional curvature equations were also added to page 16 and remain legible.

No unresolved scientific or visual blocker is present in the R2 authoring renders. Verification of the final exported PPTX's re-imported renders is still pending; actual PowerPoint animation playback is outside this review.


## Final exported-deck review: completed

All 18 individual images in `final-renders/slide-01.png` through `slide-18.png` were opened and inspected after the 22:39 export/re-import build. The renderer `render_release.mjs` imports the release PPTX identified by `build_result.json`, verifies that it contains 18 slides, and renders each slide at scale 1.5. The finalization record `validation-r3.json` identifies SHA-256 `069209cf8f4a2c1ccbff1208faf999157744207d858a92af3466fd27ede3165a` and reports 18 slides.

The final re-imported slides preserve the source derivation, scientific qualifications, readable wave peaks and troughs, native chart labels, and all corrections listed above. In particular, pages 05/06/08/09/10/12/13/15/16/17 were checked again for the exact issues raised; all are closed. Page 07's explanatory text stays within the slide. No unresolved clipping, overlap, chart-label crowding, scientific mismatch, or slide-count violation was found.

The result satisfies the review scope: an 18-slide compact report with visibly resolved carrier waves and source-grounded probability interpretation. This review verifies static renders and the underlying current source/data consistency; it does not claim native PowerPoint animation playback or experimental validation.
