# Final production QA

Status: complete. Scientific interpretation is reviewed separately in REVIEW.md.

## Reproduction and numerical evidence

The full build_all.py production route ran successfully through original model
tests, independent controls, all three figure generators, and catalog assembly.
The final export-validation stage was subsequently run successfully as well and
is included in the maintained build_all.py route. Logs are in logs/.

The original model suite passed 10 tests. Independent controls passed 27 cases;
each group also passed its actual displayed parameter and output checks. The
reviewer added independent elliptical-Gaussian and discrete-Gaussian controls.
Numerical evidence and tolerances are saved in checks_*.json and review_checks.json.

## Static figures and PDF

All 39 static figures were inspected in qa/contact-01.jpg through contact-05.jpg;
group authors additionally inspected their individual figures. The assembled
40-page PDF was rendered with Poppler at 90 dpi. Every page was inspected in
qa/pdf-contact-01.jpg through pdf-contact-07.jpg, with full-page checks of the
cover and the dense C12 page. The final PDF has no extracted text outside its
page rectangle and every page contains text.

The initial cover render revealed that Microsoft YaHei lacks U+210F. PDF prose
now uses the unambiguous ASCII spelling hbar; the vector figures retain their
proper mathematical hbar glyphs. The PDF was regenerated, glyph coverage checked,
and all pages rerendered and reviewed after this correction. No clipping,
unresolved missing glyphs or caption overflow was observed in the final render.

## Animations

All 528 frames across the 8 GIFs decoded successfully. Every animation's first,
middle and last frames were visually inspected in qa/animations-01.jpg and
qa/animations-02.jpg. Comparative color limits and axes stay fixed; the final
frame holds briefly and the GIF loops. Looping is replay, not physical recurrence.

## Offline gallery

The actual index.html was opened in the Codex in-app browser through a loopback
HTTP server bound to 127.0.0.1. The narrow sidebar layout remained usable.
The extension filter returned only the two extension figures. Combining the
animation filter with a carrier search returned the intended animations. Opening
an animation loaded the actual GIF into the modal; closing and reloading worked.
The close button was adjusted to prevent wrapping at narrow widths.
The playback screenshot is qa/gallery-preview.png.

All gallery asset references are relative and use no external libraries or
network services; index.html can also be opened directly from this folder.
The temporary loopback server is only a preview convenience.
