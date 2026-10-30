# Verification and acceptance

Date: 2026-10-19. Deliverable: `main.pdf` (5 pages), generated from `main.tex`.
Final source SHA-256: `0F37A677F72943EEA827E32BA0DE5E780CF3147B844CF50929CA63EDA7E8C60A`.

The document follows the conversation's accepted matrix route from the
fixed-occupation Coulomb interaction to the spin-1/2 ferromagnetic model,
the exact single-flip equation of motion, and the requested excitation
dispersion. The last body content is the boxed dispersion formula. It uses
Chinese connected prose with no lists/tables or ladder operators, retains
E_F in the physical Schrödinger equation, and introduces no rotating-frame
state. No writing-style retrieval tools were exposed; explicit user
preferences and the supplied conversation governed the prose.

The complete actual draft was reviewed in six contiguous chunks, each by a
fresh grounding reviewer and learner-reading reviewer (gpt-6-luna, low).
Initial source targets were: C1 lines27-80 (Coulomb projection/matrix), C2
81-147 (eigenvectors/spin rewrite), C3 148-183 (lattice/ground energy), C4
184-222 (single-flip action), C5 223-276 (Schrödinger EoM), and C6 277-306
(plane waves/final dispersion). Full-draft context and rendered pages were
provided. Frozen sources and renders are in
`../../tmp/pdfs/single-magnon-derivation-review/`.

All six grounding and six reading reports returned. C1 grounding identified
the missing explicit orbital-to-operator projection; C1 reading requested
the surviving orbital arrangements and fermion reorderings. Revisions r2/r3
added the full Coulomb expansion, all four surviving arrangements, direct
number-operator identity and reverse-exchange reordering. Both original C1
reviewers accepted the repaired span. The final optional suggestion to remove
the early statement about reversed integrals was declined: it identifies the
integral symmetry before its use in the operator counting.

C3 reading requested an explicit relation between E_F and omitted Coulomb
constants. This was added without another temporary energy symbol; both C3
reviewers accepted the clarification. C2 reading's optional eigenvector
verification and C6 reading's optional plane-wave normalization explanation
were added and checked by the relevant original reviewers. C2 grounding
accepted the new matrix products. C4 and C5 had no findings; their reasoning
remained unchanged. No material findings remain open.

Independent mechanical check: a 16-dimensional four-mode fermionic Fock
construction reproduced the projected Coulomb matrices for the independent
D and K coefficient choices and matched `(D-K/2) I - 2K S_a.S_b` exactly for
their binary-rational matrix entries. This checks signs/coefficient matching,
not the microscopic suitability of the chosen effective model for a material.

Final local build: `latexmk -xelatex -interaction=nonstopmode -halt-on-error
-file-line-error -synctex=1 main.tex`. The log contains no overfull/underfull
boxes, undefined references, or LaTeX warnings. The built-in desktop compiler
also returned success for the final saved source. An initial stale-project
result occurred while terminal artifacts were changing and was resolved by
compiling after the terminal build completed.

All five final pages were rendered with Poppler and visually inspected.
Automated checks confirmed page bounds, PDF title, absence of list/table
environments, and the exact requested source ending. Final PDF: 199,195 bytes.
Sources, PDFs and unrelated code outside this new project were preserved.
