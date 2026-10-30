# Delivery evidence

The released PPTX is `output/中期报告_单磁子传播.pptx` relative to the parent
midterm directory. The first-party finalizer passed structure, geometry, declared
font policy, editable-chart references and arithmetic policies with zero findings
and zero geometry warnings. Its exact-file hash is recorded in the validation
receipt and independently checked in delivery_check.json.

All 35 exported slides were reimported and rendered. Round-trip images differ
from the authored renders by at most 0.000504 mean absolute RGB intensity units.
The exported file contains eight native charts and three complete GIFs, with
65, 73 and 61 frames. All embedded animation frames decoded successfully.

Independent agents inspected every first-round slide at full size, and then
inspected final exported renders 01-17 and 18-35 respectively. Their science
review traced simulation callouts to the actual NPZ arrays, energy-level data
to the analytic source, and native chart caches to the authored series. The author
inspected the complete contact-sheet sequence and selected
full pages. After the final minor changes, pages 04, 06, 11, 19, 20, 21, 27 and
30 received a further full-resolution check. The false-positive concern about
duplicate x/a labels on slide 26 was checked against source and final images:
each of its two panels correctly has its own single axis label.

Resolved issues included oversized source whitespace, small multi-panel images,
unhelpful initial-state posters on static explanation pages, axis crossings,
raw variable names in legends, one unsupported empty-axis default font, line
wrapping, the visible common-phase convention, width units, and the distinction
between complex-state overlap and probability-shape similarity.

The bundled direct PDF exporter could not resolve its Helvetica font module.
The preview PDF therefore uses the verified high-resolution slide renders.
This does not rasterize the delivered PPTX's editable charts or text.

PowerPoint desktop itself was not opened or tested. The preview/round-trip checks
verify exported content through Artifact Tool, not application-specific playback.
