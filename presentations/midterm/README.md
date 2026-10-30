# Midterm presentation

The current release is `output/中期报告_统一符号与传播优化版.pptx`, with
`output/中期报告_统一符号与传播优化版_预览.pdf` as a static preview.
It contains 19 slides including the cover, within the requested limit of 20.
The main entry `output/中期报告_能带曲率与波包设计.pptx` and the original
`output/中期报告_单磁子传播.pptx` point to the same verified release.
The files explicitly named `18页优化版` remain historical 18-slide outputs.

## Latest revision

Positions use x,y and wavevectors use kx,ky throughout equations, diagrams,
charts, tables and animation frames. Energy is epsilon=E_k-E_F and time is t.
The lattice spacing a and hbar are explicit. Native time axes state their unit
hbar/Jx. No extra dimensionless notation is required to read the report.
H denotes the Hamiltonian only; band second derivatives are written explicitly.

Slides 12 and 13 embed two 61-frame GIFs in fixed laboratory coordinates.
Their x,y ranges are -35a to 225a. Dashed centroid trajectories show propagation
from the original position. The real-amplitude GIF adds a separately labeled
moving local inset to retain visible carrier crests. The full trajectories are
not subtracted from the main axes. Slide 11 retains a static centroid-centered
comparison for inspecting broadening. The PDF uses static animation frames.
Native PowerPoint application playback has not been tested.

The sequence is exchange model, single-magnon evolution, band geometry,
extended-zone maps, candidate centers, packet spectrum, spatial propagation,
quantitative broadening and overlap, finite-width controls and future work.
Scientific claims, the nine controlled cases and all native-chart data retain
the previous finite-time scope. The source PDF and raw data are unchanged.

## Editable content

Text, five native charts and native tables are editable. Equations and scientific
maps are high-resolution images, with their source SVGs retained. Both complete
GIF sequences are embedded, not linked externally.

## Reproduce and verify

- Source derivation: `../../Note/single_magnon_derivation/main.pdf`
- Scientific data: `../../figures/midterm-report/curvature-design/`
- Physical labels and animations: `../../figures/midterm-report/notation/README.md`
- Authoring sequence: `build/notation/content.mjs`
- Builder preparation: `build/notation/prepare_builder.py`
- Complete artifact-tool builder: `build/notation/notation.mjs`
- Exact output render: `build/notation/render_release.mjs`
- Static PDF and package checks: `build/notation/package_preview.py`
- Notation, data and GIF audit: `build/notation/audit_notation.py`
- Verified publication: `build/notation/publish.py`

Generate notation assets, then laboratory animations, then prepare the builder.
Use a fresh `--revision=N` and unused output/receipt paths for each revision.
The finalizer does not overwrite releases. Reimport the exact final PPTX,
inspect each slide at full size, audit native data and GIF hashes, and verify
all checks before copying its exact bytes to the stable entry points.
Preserve intervening human edits. The build runtime uses the existing bundled
artifact-tool and `build/node_modules`; no installed app internals are modified.

The replaced PPTX/PDF are preserved in `build/notation/source-before-notation.*`.
Earlier compact and curvature backups remain under their build directories.
Build QA and notation-conversion details stay outside the report's main content.
