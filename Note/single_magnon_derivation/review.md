# Verification and acceptance

Date: 2026-10-20. Deliverable: main.pdf, 2 pages, 94,814 bytes.
Source SHA-256: 5FAB8D052EDD8101249E640776484C6D0DD0F2D3E454A13898FAD0C757FD62D7.

## Requested revision

Reordered the opening as Coulomb potential, second quantization, ordered
singly occupied basis and interaction matrix, followed by D and K integrals.
Removed superexchange discussion, pair counting explanations, fermionic
reordering calculations, pair eigenvalues/eigenvectors, the undetermined
coefficient ansatz and inverse coefficient matching. Stated the spin identity
directly. Pruned repeated symbol definitions, tensor-product preliminaries,
explicit matrix-vector multiplication, repeated energy-offset discussions and
summation-index bookkeeping. Retained the physical-state E_F, the exact
single-flip equation and the final excitation dispersion.

The previous source, PDF and review record are preserved under
../../admin/archive/review-history/pdfs/single-magnon-derivation-review/20261020/ as before.tex,
before.pdf and before-review.md. The former source footnote identified Zhang
Pengfei, Quantum Many-Body Theory lecture notes, section 1.5, and Wrzosek et al.,
Phys. Rev. B 102, 024440 (2020), DOI 10.1103/PhysRevB.102.024440.
These references were inherited provenance and were not reconsulted for this
pruning revision; the source-specific footnote was removed from the body.

## Independent review

The complete draft was frozen as revision.tex and supplied to every reviewer.
Five contiguous chunks covered all body content. Each received fresh grounding
and learner-reading reviewers, gpt-6-luna with low reasoning, with full actual
Chinese draft context and exact user corrections:

- C1 lines 27-74: potential/quantization; orbitals/field expansion; basis/matrix;
  direct and exchange integrals.
- C2 lines 76-108: spin convention/matrix; direct spin identity; lattice H;
  square lattice couplings and boundary conditions.
- C3 lines 110-140: polarized state/energy; single-flip basis; bond action;
  summed Hamiltonian action.
- C4 lines 141-167: invariant subspace/state; coefficient equation;
  four-neighbor equation and index convention.
- C5 lines 169-197: plane waves; substitutions; total energy; excitation energy.

All ten reports returned. C1 grounding and both roles for C3-C5 returned no
findings. C2 learner-reading also returned no findings.

C1 learner-reading identified the late x-axis convention. Accepted: moved
hbar=1 and the arrow/axis definition before the first basis use. The full
updated draft is revision2.tex. Both C1 reviewers inspected that repair and
returned no remaining findings. The C2 removal of its former convention
sentence is a relocation only and changes no mathematical assertion.

C2 grounding raised four points. Main adjudicated them against the actual
source and the user's requested depth:

1. Claimed a missing single-spin phase convention invalidates the dot matrix.
   Declined: the same spin basis is used for both sites. A common spinor
   rephasing multiplies |up,down> and |down,up> by the same phase, so the
   off-diagonal dot-product matrix elements are unchanged. No single-spin
   component matrix is needed for the given rotational scalar.
2. Suggested removing hbar=1 as a duplicate. Declined: it appeared exactly
   once in revision.tex and exactly once in revision2.tex. The report's
   claimed earlier occurrence was absent from the actual draft.
3. Requested more explicit J=2K sign/coefficient matching. Declined: the
   displayed identity gives -2K S_i.S_j; the immediately following sentence
   explicitly sums nearest-neighbor bonds, drops constants and sets J=2K.
   This is the input-operation-result chain requested by the user, who
   explicitly rejected coefficient-solving and routine algebra commentary.
   The fixed-occupation premise was already stated before the pair matrix.
4. Warned that Jx,Jy>0 could be confused with an established sign theorem for
   K. Declined: the sentence explicitly says to take ferromagnetic exchanges
   Jx,Jy>0, so this is a model selection; no positivity proof is claimed.

No material finding remains open. Optional suggestions and warnings are
recorded above with their dispositions. Main also read the complete final
source continuously after the repair.

## Artifact checks and limits

Used the existing runner in the source directory:
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error -synctex=1 main.tex
Final exit code 0. Final main.log has no LaTeX warnings, unresolved references
or overfull/underfull boxes. The shell's Perl locale fallback warning did not
affect compilation. Both final pages were rendered with Poppler and visually
inspected (final-1.png, final-2.png in the review directory). PDF text bounds
are inside the pages; metadata title matches the document title. These checks
establish artifact integrity; the separate independent review assessed the
mathematics and exposition. No new physical formula was introduced.

The lecture-mode preset gate tools were not exposed in this session. The
maintained personal WORKFLOWS.md selects lecture for substantial teaching-note
revisions; that available workflow, including independent review, was used.
No lecture-mode gate approval is claimed.
