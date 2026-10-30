# Exact rigid wave packets: proof review record

Date: 2026-10-19. Accepted delivery snapshot: [answer-v2.md](answer-v2.md). Original frozen snapshot: [answer-v1.md](answer-v1.md).

## Scope and mathematical obligations

Infinite continuous space, scalar translation-invariant lossless Fourier evolution with real C1 dispersion. Locality is nonzero finite L2 norm plus finite position second moment. Prove the 1D existence iff affine-interval theorem, the 2D positive quadratic no-go, and distinguish complex-profile preservation from intensity-only preservation. Explain the non-L2 delta-circle loophole. No numerical agreement is used as proof.

Two independent mathematical investigations (`onedim_proof_check`, `twodim_proof_check`) confirmed the spectral criterion, 1D finite-width continuity argument, quadratic obstruction, and variance-domain justification. Their findings are available in this chat's collaboration messages. Additional stronger no-go results without finite width for intensity were not added, to retain the agreed scope.

## Frozen target coverage

Each first-pass target received fresh GPT-6 Luna / low reviewers in both roles; all reviewers received the complete snapshot path and user scope. Targets group coherent mathematical/prose units rather than individual aligned rows.

| Target | v1 span | Units | Reviewer tasks |
| --- | --- | --- | --- |
| C1 | 1-43 | Result; Fourier model; locality; rigid profile | review_c1_grounding, review_c1_reading |
| C2 | 45-73 | Fourier identity; all-time necessity; converse; level-set criterion | review_c2_grounding, review_c2_reading |
| C3 | 75-118 | L1/continuity; affine-interval necessity; compact-spectrum sufficiency; analytic corollary/examples | review_c3_grounding, review_c3_reading |
| C4 | 120-155 | Quadratic symbol; completed square; zero measure; anisotropic extension | review_c4_grounding, review_c4_reading |
| C5 | 157-215 | Intensity definition; Fourier derivative; moments/center; variance; 1D and 2D consequences | review_c5_grounding, review_c5_reading |
| C6 | 217-225 | Delta-circle construction; nonlocal Bessel tail; scope correction | review_c6_grounding, review_c6_reading |

## Dispositions

- C1 grounding's claim that finite-width assumptions are missing from the intensity case is refuted by v1 line 3 and the explicit first sentence of the intensity argument at line 166. Continuity is established at lines 77-97 and explicitly reused at line 205. No premise is absent.
- C1 reading's claim that a positive-length interval may not permit a compact smooth bump is refuted: any interval of positive length contains a nonempty open interval. The proof explicitly takes an open neighborhood of k*. Its claim that the L2-only/finite-width distinction is absent is refuted by v1 line 73's final sentence and line 77's assumptions.
- C1's optional requests to reiterate global C1 assumptions, continuous representatives and compact support were declined where already explicit; introducing additional equivalent notation would not improve the proof. Out-of-target phase and analytic-domain comments were handled in C2 and C3.
- C2: accepted the need to spell out why a countable sequence of phase equalities forces zero frequency difference. Added the 0<|Delta|/n<2pi contradiction. Also accepted the optional indicator-spectrum witness. The alleged absent measurability assumption is refuted by the global C1 premise; nevertheless its consequence is now explicit for clarity. No repeated reminder about intensity was added because the two definitions and separate proof are already clearly distinguished.
- C3 grounding: accepted the wording correction that local zero curvature/approximate linearity alone does not establish the strict condition; it does not forbid an affine interval elsewhere. Specified a connected open analytic domain. C3 reading's positivity-of-interval concern is refuted by the explicitly open neighborhood; added a short Plancherel sentence to close finite nonzero norm in the constructive direction.
- C3 optional redundancy suggestions were declined: the nonpathological generality sentence responds to the user's explicit constraint, and defining real analytic is useful for this learner rather than assuming they know the term. The final repeated approximate-effects list was removed instead.
- C4: both reviewers returned no findings; unchanged in v2.
- C5: grounding returned no findings. Accepted learner-reading's order/definition suggestion: define the position center by its integral and establish the finite velocity moment before using its mean or variance. No new assumption is imposed; it follows from claimed finite-width preservation at a nonzero time.
- C6: accepted both roles' request to expose the Bessel-tail reason. Added the standard J0 asymptotic and its connection to the divergent 2D radial integral. Accepted the optional removal of the repeated approximate-effects list.

## Repair closure and acceptance

Both original roles reread v2 for C2, C3, C5 and C6. C2, C5 and C6 both returned no findings. C3 grounding and reading returned optional prose cuts only, disposed of above. C1 material objections were refuted from explicit assumptions and elementary interval facts; C4 retained its unchanged coverage. The final C6 span is now lines 217-238; other target boundaries remain unchanged.

Main checked the complete argument for scope, normalization, Fourier signs, the plus sign in the width expansion, existence vs classification, and the locality distinction. All substantive obligations in the agreed scope are discharged. This is mathematical review of the stated scalar model, not independent verification of material-specific physics or a numerical experiment.
