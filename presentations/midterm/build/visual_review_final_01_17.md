# Final-export visual review: slides 01-17

## Scope and evidence

The reviewed files are `build/final-renders/slide-01.png` through `slide-17.png`, each 1920 x 1080. These are the renders made by re-importing the finalized PowerPoint export, not the earlier working previews. Every one of the 17 images was opened and inspected individually at full size. Slides 18-35 are outside this review's scope.

## Verified corrections

- Slide 04: the arbitrary numeric horizontal axis is gone; both energy levels and the vertical energy scale are legible, with no overlap.
- Slides 05 and 08: literal underscore notation was removed from native text.
- Slide 07: one probability panel is enlarged, with complete axes and colorbar. The exact one-flip-subspace statement is explicit.
- Slide 10: the vertical energy axis/title now sits at the left edge of the plotted data; legend labels are Chinese and distinguish the two directions. The plot still includes small unused x-axis margins out to +/-4, but the curves correctly terminate at +/-pi; this is not a scientific or readability blocker.
- Slide 12: the group-velocity expression and the maximum-speed condition are no longer broken by literal underscore syntax or an awkward equality wrap.
- Slide 13: the phase convention is correct: psi = exp(+i E_F t / hbar) c, so the probabilities agree. Definitions n = r/a, q = ka, tau = J_x t/hbar, eta = J_y/J_x and u = hbar v/(J_x a) are dimensionally consistent. Evolution uses the relative energy e(q).
- Slide 15: four late-time probability snapshots are enlarged and share the displayed logarithmic color scale. Axis labels and the colorbar are complete.
- Slide 16: the static image now shows the tau=24 anisotropy comparison described in the text. sigma_x/a = 24/sqrt(2) = 16.971 and sigma_y/a = 0.3*24/sqrt(2) = 5.091 agree with the displayed values.
- Slide 17: the right native chart displays sigma_y/a for eta=1, 0.3, 0, with correct relative slopes. The separate equal-exchange statement sigma_x/a = sigma_y/a = tau/sqrt(2) is correct.

## Remaining minor defect

- Slide 11: the left explanatory paragraph still puts its final Chinese full stop on a separate line. Suggested fixed line break: `线上各模式的频率相同。` then `群速度指向色散曲面的梯度方向。` This is a small typesetting defect, not a scientific error.

## Outcome

Within the inspected final-export range, no blocking overlap, cropped equation, missing matrix bracket, clipped axis or incorrect scientific annotation was found. Slide 11's orphan punctuation is the remaining requested fix. The theoretical formulas on slides 08-09 inherit hbar=1 from the source PDF; this convention should be stated in the slide or speaker notes if not already present. This report verifies rendered appearance and the listed annotations only; it does not independently validate the simulations or PowerPoint animation playback.
