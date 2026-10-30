# Science and slide review, initial render

## Review scope

- Visually inspected every full-size PNG from renders/slide-18.png through renders/slide-33.png individually, in four groups of four. These were the initial rendered files available when review began, not contact-sheet-only checks.
- Read the text, notes, formula-asset identities, native chart series and source footers for all 33 slides in slide_spec.json, plus deck.mjs.
- Checked the scientific chain against the actual five-page Note/single_magnon_derivation/main.pdf and its TeX/aux equation-page map, already read in the outline task. Checked figure interpretation against A/B/C manifests and THEORY.md.
- Checked reported numerical values against data_facts.json, checks_b.json, checks_c.json and checks_independent.json. This was provenance and mathematical-consistency review, not a fresh simulation run.
- Did not visually inspect full-slide renders 01–17 in this pass. Their text, formula choices and source mappings were inspected. PowerPoint animation playback was not tested.
- The working deck.mjs acquired readable native-chart mappings during review. Findings below refer to the first PNG renders unless noted as source text.

## Specific changes to make

| Priority | Slide | Observed issue and exact correction |
|---|---:|---|
| P2 | 03 | Source says “原理 PDF 第 1 页，式 (1)–(9)”, but (8) and (9) are on PDF p.2. Use “第1页，式(1)–(3)” for the visible integrals, or “第1–2页，式(1)–(9)” for the broader context. |
| P2 | 04 | The visible matrix has no ordered basis label; it is only in notes. Add “基底：↑↑、↑↓、↓↑、↓↓” near the matrix. The note correctly identifies the middle symmetric state as part of the triplet. |
| P2 | 08–09 / 13 | Visible derivation uses source-PDF units ℏ=1, but later formulas restore ℏ. The bridge is only in notes. On13 visibly state “推导中取ℏ=1；模拟恢复量纲” and ψ=exp(iE_Ft/ℏ)c, |ψ|²=|c|². This connects total-energy and excitation-energy evolution. |
| P2 | 14 | “N=256” and “每个波矢概率1/N²” assume N is the linear grid size; earlier theory uses total-site \(\mathcal N\). Change to “256×256格点，\(\mathcal N=256^2\)” and spectral probability \(1/\mathcal N\), or explicitly define \(N_x=N_y=N=256\). |
| P2 | 17 | Footer globally says η=1, but native RMS-y chart has η=1,0.3,0. Use “左图η=1；右图η=1,0.3,0”. The adjacent “等方情形” formula is correctly qualified. |
| P2 | 18 | Right-hand B12 pair is too small: axis labels and numerical ticks are roughly half the readable size of the left plots. Enlarge the right area, or replot probability and spin profiles as one labeled panel. This is the main plot-legibility defect found in18–33. |
| P2 | 19 / 24 | Gaussian is introduced without a visible initial-condition formula or definition of σ; these are only in notes. Add the Gaussian formula and define initial probability RMS width. A clean dimensional convention is ψ(r,0)∝exp[−(x²+y²)/(4σ₀²)]exp(ik₀·r), σ₀/a=4. Slide24 then uses σ₀/a=3,6,10 and σₓ(τ)/σ₀. This avoids mixing code dimensionless sigma with a physical length. |
| P2 | 20 | PDF/static preview shows GIF at τ=0, so all three panels are identical and propagation directions are invisible. Preserve animation but provide a meaningful late-time poster frame or add trajectories/late-time thumbnails for the PDF. |
| P3 | 20 | Lower-left text has four lines with “量。” alone on its final line. Shorten to “对称频谱使平均速度为零，包络仍向外展宽。” or widen. No footer overlap, but avoidable orphan. |
| P3 | 21 | Native x-axis crosses the chart at y=0, placing “时间τ” above the zero trajectory and producing two adjacent zero labels. Move x-axis title/ticks to bottom. Scientific values are correct. |
| P3 | 23–24 / 27 | Initial renders use internal labels q0=(.7,0):sigma_x, sigma=3, extension_ordinary. Current source has readable mappings; regenerate and verify PNGs. Source editing alone does not establish visual completion. |
| P3 | 25 | Left horizontal-axis caption visibly repeats “x/a x/a”. Remove the repeated label in a presentation-only asset or replot, preserving source figure. Data and direction claim are correct. |
| P2 | 27 | First render omits concrete q₀ values from visible prose; readable legends in revised source resolve part of this. Also show why curvature vanishes: \(e_{xx}=\cos q_x,\ e_{yy}=\eta\cos q_y\), both zero at (π/2,π/2). Currently this basic-principle step is verbal only. |
| P2 | 27 | F definition and translation reference are only in notes. Add \(F=|\langle\psi_{\rm shift}|\psi(\tau)\rangle|^2\), and “参考初态按各自谱平均速度平移；同时检测相对相位变化”. Values are correct, but F must be distinguishable from probability-profile overlap. |
| P3 | 29 | Right explanation breaks “决定” across lines. Use “交换负号来自费米反对易关系。自旋矩阵采用沿x量子化的基底。” with a deliberate line break. Layout cleanup only. |
| P2 | 31 | “概率≈5.6×10⁻¹⁶” leaves norm unspecified. Write “max|ΔP|≈5.6×10⁻¹⁶”. Preserve “概率L1” for Gaussian grid comparison; do not relabel it amplitude-L2. Small note “记录案例最大值；256²→384²” makes scope explicit. |
| P3 | 33 | B/C data paths omit figures/midterm-report/ while A is project-relative. State a common base directory or make paths consistently project-relative. The files exist. |

## Confirmed points

- Slides03–09 preserve direct/exchange matrix elements → Coulomb matrix → singlet/triplet split → J_H=2K → lattice → exact one-flip closure → EOM → plane-wave dispersion. Selected formula assets map to correct PDF equations. Factor2, Hamiltonian sign, bond counting and x-quantized spin matrices match the source.
- Slide18 correctly uses \(\langle S_i^x\rangle=1/2-P_i\), total deficit1 and no magnon loss. Slide32 correctly distinguishes σ=2 from earlier σ=3 and states cubic residual. Slide30 restricts 1%/5% to axial energy approximation rather than fidelity.
- Slides22,26,28,30,32,33 have no material text overlap or clipping in inspected PNGs. Their conclusions match source. Slide28's text table is acceptable as a single synthesis page.
- Slide23's variance law is valid for the stated unchirped Gaussian. General chirped states need \(2\tau\mathrm{Cov}_{sym}(n,u)\), correctly acknowledged in notes. Finite-box validity is also qualified there.
- No actual-material parameter, experimental or infinite-time exact shape-preservation claim was found.

## Numerical checks

| Slide | Quantity | Verified source value |
|---:|---|---|
|16|τ24 RMS x, RMS y for η=.3|16.970562748477143a; 5.091168824543142a|
|21|Mean x velocity; x centroid at60|.639204345421764; 38.352260725305854a|
|22|qright widths at60|6.969652118716968a; 8.448679064953332a|
|24|Relative widths|2.7175098454867794; 1.1850840893433185; 1.0259452675541316|
|25|Anisotropic widths; angle|6.969652118716968a; 4.3510739546730575a; arctan(.3)=16.699244°|
|27|F at60|.38229551913806026; .9771040711622112|
|30|1%/5% q thresholds|.34537557866113044; .7632996084439329|
|31|Sparse vsFFT amplitudeL2|3.404276148170018e-15|
|31|Bessel vsFFT max probability error|5.551115123125783e-16|
|31|Gaussian enlarged-grid probabilityL1 max|3.747965492026441e-15|
|31|Gaussian edge-mass max|5.697042907726274e-14|

Outcome: no wrong numerical result or Hamiltonian/dispersion error found. Revisions concern visible definitions, source locations, parameter-label scope and concrete readability defects. Re-render specifically modified pages before marking the deck visually complete.
