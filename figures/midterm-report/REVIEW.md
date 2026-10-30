# Independent scientific and numerical review

Review date: 2026-10-19. Reviewer: a separate agent from the three figure authors.

This review covers the model, propagation, observables, parameter comparisons and
captions in `common.py`, `verify_numerics.py`, `generate_dispersion.py`,
`generate_local_flip.py`, `generate_gaussian.py`, `manifest_a.json`,
`manifest_b.json`, `manifest_c.json`, and their numerical-check records. The
one-magnon part of `../../Note/single_magnon_derivation/main.tex` and the shared
`code/spin_wave_2d.py` dispersion were inspected as source context. `THEORY.md`
and `README.md` were also read when they became available.

## Findings and repair closure

The following findings were communicated to the main author during generation.
Repairs to the figure groups have been checked in the actual revised source,
manifest, and, where specified, regenerated PNG.

| Location | Finding | Disposition |
|---|---|---|
| A10 caption | A generic long-wave limit does not make group velocity parallel to wavevector when eta differs from one: u tends to (qx, eta qy). | Repaired. The caption now restricts the general long-wave parallelism to eta=1 and separately treats special directions. |
| C12 propagation formula | With tau=Jx t/hbar and epsilon an energy, exp(-i epsilon tau) mixed dimensional and dimensionless conventions. | Repaired in source, manifest and PNG. The exponent now uses e=epsilon/Jx. |
| A01 spin schematic | Vertical spin arrows could be confused with the spatial y direction, while the source quantizes spin along +x. | Repaired in source and PNG: background arrows point along +x and the flipped arrow along -x. |
| B01 spin expectation plot | The original origin had both a +1/2 reference marker and the actual -1/2 marker under a local-spin title. | Repaired in source and PNG: the actual origin has only the -1/2 marker; the other sites have +1/2. |
| A09 vertical label | The intended delta symbol was written as the literal math word `delta`. | Repaired to the delta symbol. |
| C06 velocity annotation | The same annotation was drawn four times because it was inside the carrier loop. | Repaired by moving the annotation outside the loop. |
| THEORY.md, first paragraph of section 1 | A localized single-flip basis vector was called a ground state. | Repaired to “基矢”; the revised paragraph was checked. |
| THEORY.md, sections 4–5 | Widths and Gaussian coordinates used x and sigma in lattice units, while the figures also use physical-width labels sigma/a. | Repaired: the Gaussian uses n_x=x/a and n_y=y/a, sigma is in lattice sites, and physical widths are a sigma. The Bessel widths explicitly use lattice-site units. |
| THEORY.md, section 6 | The proportional expression for delta omega did not define whether the constant and linear terms had been removed. | Repaired to the explicit residual e(q0+dq)-e(q0)-u0.dq and the cubic term with a fifth-order remainder. |
| C12 lower margin | The axis label and footer were too close. | Repaired by enlarging the footer area; the regenerated PNG was inspected. |
| README.md, animation summary | The animation list included a decoupled-chain animation and a zero-curvature animation, which exist only as static examples. | Repaired. The eight animation subjects now match the manifests, and the two static-only examples are explicitly distinguished. |

No unresolved material model or numerical defect was found in the three figure
generators, their captions or the revised theory note after these repairs. The
README inventory finding is also closed. Completion of full export, PDF and
browser verification remains a separate production check described below.

## Model and observables

The source counts every exchange bond once and uses dimensionless spin-1/2
operators. In the exactly invariant one-flip subspace, the relative Hamiltonian
has diagonal Jx+Jy and hopping amplitudes -Jx/2 and -Jy/2. Its Fourier eigenvalue
is therefore

\[
\varepsilon=J_x(1-\cos q_x)+J_y(1-\cos q_y).
\]

The shared `Params` implementation uses `S=0.5`, zero field and precisely this
eigenvalue. Using a class originally written for linear spin waves does not add
a spin-wave approximation to the present one-magnon calculation: the restricted
operator agrees with the source's exact single-flip operator.

The numerical state removes the common ground-state phase. With physical
coefficients c, psi=exp(i EF t/hbar)c, so both give the same probability. The
negative phase in `propagate` is consistent with the positive spatial carrier
exp(i q.r) and velocity u=(sin qx, eta sin qy). FFT normalization is paired
correctly between forward and inverse transforms. The orthonormal FFT used for
spectral probabilities preserves the state norm.

In this fixed one-magnon sector, P=|psi|^2, <Sx>=1/2-P and <Sy>=<Sz>=0. B01 and
B12 use these observables correctly; none of the probability animations is
interpreted as a nonzero transverse mean magnetization. A spatially isotropic
exchange parameter does not impose continuous rotational symmetry on the whole
square-lattice band. A10 and B04 preserve that distinction.

## Propagation and moment evidence

The numerical records were assessed against the methods that produced them,
not accepted solely from their pass flags.

* The sparse-matrix control constructs the real-space Hamiltonian bond by bond,
  without calling the dispersion. Its matrix-exponential comparison therefore
  tests the signs, factors of two, coordinate ordering and phase of the FFT
  evolution through a different representation. The recorded amplitude L2
  error is 3.40e-15 for N=12, eta=0.37, tau=4.3.
* The infinite-lattice local-flip amplitude is
  exp[-i(1+eta)tau] i^(m+n) J_m(tau) J_n(eta tau). Both the global relative
  phase and the spatial Bessel factors agree with the implemented propagator.
  The B-group controls compare complex amplitudes, probabilities and widths,
  rather than only intensity pictures. Their largest complex-amplitude error
  is 1.46e-14 and their largest probability error is 5.55e-16.
* For a localized flip, sigma_x/a=tau/sqrt(2) and
  sigma_y/a=eta tau/sqrt(2) follow from the Bessel moments. The recorded width
  errors are at most 7.11e-15. The x marginal used in B08 can legitimately be
  shared across eta values because both the initial state and the dispersion
  separate into x and y factors.
* For Gaussian input exp[-n^2/(4 sigma^2)], the probability envelope is
  exp[-n^2/(2 sigma^2)]. Thus sigma is its probability RMS width in the
  well-resolved regime, rather than the amplitude width with a different
  factor of sqrt(2). C02 explicitly limits Delta q=1/(2 sigma) to the
  wide-envelope, non-wrapping spectral regime.
* In the infinite-lattice position representation, n(tau)=n(0)+tau u(q).
  Consequently the exact variance includes an initial symmetric covariance
  term. That term is zero for the centered real Gaussian envelope with a
  linear carrier used here. C09 computes Var(u) from the full discrete
  spectrum, so it does not substitute a quadratic Taylor approximation for
  the exact cosine band. Its caption explicitly retains the covariance term
  for more general initial states.

The elementary Gaussian averages in `verify_numerics.py` are wide-envelope
expressions. On a discrete infinite lattice, the nearest-neighbor average has
the correction factor

\[
R(\sigma)=
\frac{\sum_n\exp[-(n+1/2)^2/(2\sigma^2)]}
     {\sum_n\exp[-n^2/(2\sigma^2)]}.
\]

For the tested sigma=3,6,10, this differs from one by less than the displayed
double-precision rounding. The reviewer explicitly evaluated the two sums;
at sigma=1 the difference is already about -1.07e-8, and at sigma=0.4 it is
about -0.157. Thus the Gaussian checks are reliable for their actual parameters,
but the same closed forms should not be advertised as exact for arbitrarily
narrow lattice states. The exact spectral-moment reference used in C09 avoids
this limitation.

An additional reviewer calculation tested an unequal-width Gaussian not in the
author's 27 shared controls: N=384, (sigma_x,sigma_y)=(3,8), q0=(0.7,1.3),
eta=0.35, tau=60. The velocity was computed directly in real space from the
imaginary part of nearest-neighbor overlaps, rather than from the FFT spectrum.
It was (0.6353320678861173, 0.33658732536861613). The largest difference from
the spectral velocity was 3.34e-16; the largest centroid and RMS-width errors
against the Gaussian moment formulas were 7.11e-15. The edge probability was
1.29e-30. This checks the x/y ordering and the independent `sigma_y` convention.
The reviewer-added result, exact parameter values, overlap formula, environment
and discrete-Gaussian correction sums are saved in `review_checks.json`.

## Boundaries, scales and preservation claims

B-group comparisons use N=256 and N=512; the largest cropped amplitude
difference is 1.00e-14 and the largest monitored edge probability is 1.92e-29.
C-group comparisons use N=256 and N=384 for every actual named case. Their
largest amplitude difference is 2.30e-9 for sigma=10; the largest probability
L1 difference over all cases is 3.75e-15. The largest sampled edge probability
is 5.70e-14 and the largest variance-law error is 1.42e-13. These are small
relative to the displayed probabilities and widths. The finite box is not
mathematically identical to the infinite lattice; the conclusions are limited
to the recorded parameters and time windows.

The code uses fixed norms and fixed color limits within comparative snapshots
and animations. Local-flip maps disclose logarithmic color scales and hidden
small tails. C08 explicitly declares its dimensionless rescaling; it does not
rank unequal initial widths as equal-size resources. Marginal probabilities
sum over the other coordinate, whereas B12 is explicitly a central slice.
The maximum group-velocity lines are described as principal ballistic-front
scales, with nonzero tails outside, rather than a hard support boundary.

C13 compares equal initial widths and uses a complex-state overlap with an
initial state rigidly shifted at the actual mean velocity. The absolute square
removes a global phase, but relative phase distortions remain detectable. Its
caption identifies this distinction from a probability-shape metric. C14 uses
a separate sigma=2 example and explicitly discloses the change from C13.
The vanishing quadratic curvature is accompanied by a nonzero cubic residual;
the figures make a finite-time suppression claim and do not establish exact
or indefinitely sustained shape preservation.

## Inspection limits

This was an independent scientific and numerical audit, not a second full
production run or a complete two-role, sentence-chunk teaching review. The
original Coulomb-to-spin derivation before the one-magnon section was not
rederived. No experimental material parameters, dissipative model, multi-magnon
effects or physical preparation protocol were validated.

All three generator scripts and their captions were read. Selected rendered
PNGs A01, B01, C06, C12 and C13 were inspected, including the repaired A01,
B01 and C12 images. The full-page visual audit, all animation frame decoding,
merged PDF layout and browser interactions are separate production checks
owned by the main author; this report does not claim to have independently
inspected every animation frame or every rendered panel. C12's flagged lower
margin has been corrected and its final regenerated PNG inspected.
