# Final scientific and visual review: slides 18–35

## Actual review scope

Individually viewed all 18 full-size images in build/final-renders/slide-18.png through slide-35.png. These are renders made after exporting the 35-slide PPTX and importing that PPTX again. This review therefore checks the exported presentation result rather than only the authoring state.

Also read the current source footers and speaker notes for slides18–35 from slide_spec.json. Numerical facts are unchanged from the earlier independent source review, which checked data_facts.json and the B/C/independent verification JSON files. No new physical simulation was run.

Full-slide visual review of pages01–17 is outside this final pass; the initial pass checked the earlier deck's full scientific text and equation/source identities, and another reviewer owns the early-page final visual pass. Native PowerPoint animation playback was not tested by this reviewer.

## Result

No remaining blocking scientific or layout defect was found in the inspected exported/imported slides18–35. The previously reported substantive presentation issues in this range are resolved:

- Slides18–19: return probability and longitudinal spin observations are separate, readable full-size figures.
- Slide20: the Gaussian initial-condition formula is visible, with the correct 4σ² in the amplitude exponent and an explicit probability-RMS definition.
- Slide21: late-time propagation directions now appear in the static preview, rather than three identical initial states.
- Slide22: native chart x-axis labeling is readable at the bottom.
- Slide25: the table clearly labels initial RMS width divided by a and a ratio to the initial width.
- Slide28: concrete q₀ values replace internal case names; the complex-state F definition and sensitivity to relative phase are visible. The finite-time interpretation and higher-order limitation remain explicit.
- Slide32: the error table differentiates amplitude L², maximum absolute probability error and probability L¹. Reported values remain consistent with source checks.
- Slide33: the distinct σ=2 example is visibly distinguished from the earlier σ=3 comparison.
- Slide34: the animation appendix has explicit captions, while main scientific comparisons now have useful static counterparts. Its static first-frame appearance is expected and is not evidence of animation playback failure.

No unexpected cropping, overlap, missing chart series or formula truncation was observed. The scope is model calculation, not material/experimental validation; this boundary remains intact.

## Minor final polish, without changing results

| Slide | Remaining item |
|---:|---|
|20|Add “n=r/a，σ以格点数计” near the Gaussian formula or in its source line, so its dimensionless width convention is fully visible. The formula itself is correct.|
|21|Add τ=60 to the source line. The displayed late-time C05 snapshot no longer has the animation timer, so the snapshot time is currently only recoverable from the source package.|
|26|The left source panel still contains a doubled horizontal-axis caption “x/a x/a”. This is a cosmetic source-figure defect; a presentation-only crop/replot can remove it.|
|30|“决定” still breaks between two text lines. It remains readable; a shorter sentence would improve appearance.|
|35|B/C file locators use paths relative to figures/midterm-report while A uses a project-relative path. A shared base-path label would make the table more consistent.|

The parent author has separately identified old animation wording in notes16/21 and is correcting it, and plans a visible statement on slide27 that the model remains linear. Those pending text edits were not claimed as already rendered in this review.
