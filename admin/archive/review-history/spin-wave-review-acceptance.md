# Chat derivation acceptance, 2026-10-19

Deliverable: `spin-wave-derivation-r2.md`; original frozen review snapshot:
`spin-wave-derivation-r1.md`. The task requests an inline derivation, not a
new lecture artifact or further source-code modification.

Four contiguous chunks cover the entire draft: C1 opening/model/ground state/HP;
C2 bond expansion/quadratic Hamiltonian/Fourier dispersion; C3 operator and
transverse-mean EoM; C4 propagation/velocity/default parameters/exactness limits.
Each received fresh independent grounding and learner-reading reviews using
gpt-6-luna at low reasoning, with the full draft and source locations shared.

Returned reports: c1_grounding, c2_grounding, c3_grounding, c3_reading,
c4_grounding and c4_reading had no findings in their assigned spans.
c1_reading and c2_reading findings were adjudicated as follows:

- C1 reader, optional units clarification: accepted; r2 labels h as Zeeman
  energy, with no mathematical change.
- C1 reader, alleged material error in the maximum eigenvalue of S_i.S_j:
  refuted by S_i.S_j=[T(T+1)-2S(S+1)]/2 for T=0,...,2S. The maximum is S^2,
  as in the draft, not S(S+1). The aligned product state simultaneously
  saturates every bond and field lower bound. This evidence was returned to
  the reviewer; the draft remains unchanged on this point.
- C1 reader, optional zero-field uniqueness clarification: declined because
  the draft already says 'one of the exact ground states' and makes no
  zero-field uniqueness claim.
- C2 reader, optional dimension of Taylor remainder: accepted; r2 includes
  the exchange-energy scale S(Jx+Jy). The unchanged quadratic coefficient and
  the added bound follow by expanding each cosine. Main checked this local
  dimensional clarification; no substantive argument changed.

Main read the entire final draft for cross-chunk continuity and checked both
local clarifications. No unresolved material findings. No new numerical claim
or code change requires another execution of the existing regression suite.
