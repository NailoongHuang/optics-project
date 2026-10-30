# Visual review of slides 01-17

Reviewed every rendered slide individually at 1920 x 1080. This review did not use only a contact sheet. No edits to the deck were made.

## Issues requiring correction

1. **Slide 04 - native energy chart.** The horizontal axis crosses the middle of the diagram, and the label for state grouping occupies the same narrow band as the tick labels. The arbitrary horizontal ticks 0, 0.2, ..., 1 have no physical meaning. The energy ticks 1.4, 0.4, -0.6, -1.6 also obscure the intended levels at +1 and -1. Remove the numeric horizontal axis and use explicit state-group labels; use energy ticks at -1, 0, +1 or label the two levels directly.
2. **Slide 05 - literal formula syntax.** Both equations in the right column display `J_H` with a literal underscore. Use proper subscript typography, consistently with the PDF formula images.
3. **Slide 07 - figure legibility.** B01 is squeezed into the right column; each panel is only about 280 px wide. Its tick labels and legend text are approximately 10 px at the full slide render, while the equations are very large. Reduce equation scale and give the two-panel figure substantially more width/height, or move the observable comparison to a larger dedicated panel.
4. **Slide 08 - literal formula syntax.** The coefficient table displays `E_F` with an underscore. Use a real subscript.
5. **Slide 10 - native chart axis placement.** The vertical axis crosses at q=0 and its rotated energy label sits inside the data region. Move the vertical axis and its title to the left edge. The axis runs to +/-4 although the displayed band is restricted to +/-pi; use a Brillouin-zone limit and appropriate ticks. The legend uses English fragments while the rest of this report is Chinese.
6. **Slide 11 - orphan punctuation.** The left explanatory paragraph ends with a standalone Chinese full stop on the next line. Shorten or manually reflow the sentence. This is a visible typesetting defect.
7. **Slide 12 - literal formula syntax and wrap.** The paragraph begins `v_g` rather than a typeset subscript. The right paragraph breaks `q_x = +/-pi/2` across the line at the equality, creating an unnecessarily fragmented mathematical statement. Keep this short condition on a single line.

## Important improvements for the requested visual density

8. **Slide 02 - animation framing.** The original GIF includes its own large title, subtitle and footnote; substantial internal white space reduces the actual heatmap to roughly 400 px square. Crop the animation frames to their axes/colorbar area and provide the short context as editable slide text. This would make the first visual explanation much clearer.
9. **Slide 13 - formula/table-only page with unused space.** The upper right half is almost entirely empty. The page has no actual propagation or Fourier visual despite being the bridge from theory to simulation. A compact initial real-space / spectrum / propagated real-space visual sequence would use this space and better satisfy the user's request for rich graphical content. Keep the evolution equation and units, but compact their vertical spacing.
10. **Slide 15 - eight snapshots are too small.** Each heatmap is only about 200 px square; tick labels and the colorbar labels are small. Use two slides for early and late evolution, or increase the usable figure area with a layout that preserves the quantitative labels. The current page communicates qualitative shape but not comfortably readable axes.
11. **Slide 16 - static poster differs from discussed time.** The displayed GIF poster shows tau=0, with both panels nearly black, while the surrounding analysis gives tau=24 widths. For the static render/PDF, show a meaningful tau=24 poster or a tau=24 snapshot alongside the animation. Also crop the source animation's repeated title/footnote to enlarge the actual plots.

## General observation

The formula crops are complete and the large matrix brackets are intact. Slides 01, 03, 06, 09, 14 and 17 show no material clipping or overlap. Slides 11-12 have clear plots but their small raster tick labels would benefit from any available enlargement; this is secondary to the concrete defects above.
