# Physics outline for the midterm presentation

Scope: 30 slides, comprising 26 main slides and 4 appendices. This is an authoring outline for a Chinese presentation; it does not modify the source notes or simulation package.

Authoritative sources inspected: `Note/single_magnon_derivation/main.tex`, the actual five-page `main.pdf` extracted with `pdftotext -layout`, its equation/page labels, `figures/midterm-report/THEORY.md`, `README.md`, all three manifests, and `checks_independent.json`. All slide text below is grounded in these sources or explicitly identified as a direct consequence of the dispersion. Figure IDs refer to the existing simulation package.

## Narrative and visual contract

- The scientific chain is Coulomb direct/exchange integrals → four-dimensional matrix → triplet/singlet splitting → operator matching (J=2K) → lattice Hamiltonian → exact one-flip sector → amplitude EOM → dispersion → group velocity → local-flip and Gaussian dynamics.
- Use slides 3–11 for the complete derivation with mathematical illustrations; do not replace them by a single Hamiltonian slide. Slides 12–24 explain the physical meaning through plots. Slide 25 is a bounded exploratory result. Slide 26 reports established outcomes and future work.
- The first ten slides need editable state diagrams, colored matrix blocks, bond diagrams and energy-level diagrams; existing numerical plots cannot illustrate these steps faithfully on their own. The figures in this part are explanatory schematics, with no invented orbital shapes, material constants or measured energy values.
- Typical content per slide: one concrete claim, one equation chain, two or three explanatory sentences, and one dominant figure with one supporting graphic. Multi-panel figures already contain rich information; do not shrink six complete source figures onto a slide.
- Keep symbols stable: ↑/↓ mean along (+x/-x), spin operators are dimensionless, (J_x,J_y) are energies, (\mathcal N=N_xN_y) is the number of sites. Simulation manifests use `N=256` for **each** axis, so write (256\times256), never “256个格点”.
- The source PDF takes ℏ=1. Restore ℏ consistently in the slide EOM and then introduce (q_\mu=k_\mu a, \tau=J_xt/\hbar, \eta=J_y/J_x, e=\varepsilon/J_x). The chart variables are not physical seconds or nanometers.
- Each slide has a small source footer, with exact PDF page/equation numbers for derivation slides and figure IDs/parameter references for numerical slides. New results derived from equation (39) are labeled “由色散式导出”, not falsely attributed to a nonexistent PDF equation.

## Main slides

### 01 — 从库仑交换到自旋激发传播

**Slide text.** 中期报告围绕三个问题展开：局域翻转为什么能够传递、传播速度由什么决定、波包为什么逐渐展宽。用两电子交换矩阵建立模型，再用同一个精确色散解释两类初态的传播。

**Equation.** 
\[
\varepsilon(\mathbf k)=E_{\mathbf k}-E_F=J_x(1-\cos k_xa)+J_y(1-\cos k_ya).
\]

**Visual plan.** Main montage: `a01-lattice`, one late-time panel from `b04-isotropic-late-snapshots`, one moving panel from `c04-moving-gaussian`. Include a compact four-stage progression: 两电子交换 → 晶格模式 → 局域激发 → 波包传播. Title page can be information-rich without a fabricated presenter name or institute.

**Sources.** PDF p.5, Eq. (39); A01, B04, C04. **Avoid.** Claiming experimental data, a specific material, or completed strict nondispersive propagation.

### 02 — 先明确研究对象与我们观测的量

**Slide text.** 每个格点保留一个自旋 (1/2)，背景沿 (+x) 完全极化。我们制备一个翻转，并研究“在哪个格点测到这个翻转”的概率分布；改变初始相位和包络，可产生不同的传播行为。

**Equations.**
\[
|i\rangle=|\uparrow_1\cdots\downarrow_i\cdots\uparrow_{\mathcal N}\rangle,
\qquad |\Psi\rangle=\sum_i c_i|i\rangle,
\qquad P_i=|c_i|^2.
\]

**Visual plan.** A01 dominates, with small badges for fixed occupancy, nearest neighbors, (J_x,J_y>0), zero field, and three native schematic thumbnails “单格点 / 零载波Gaussian / 有载波Gaussian”. This is a map of the question, not a premature derivation.

**Sources.** PDF pp.1,3–4, Eqs. (22), (26), (30); A01, B01, C01. **Avoid.** Calling (|i\rangle) a one-electron orbital; interpreting a fixed-one-magnon amplitude as a classical rotating transverse moment.

### 03 — 直接积分与交换积分：同一个库仑作用的两类矩阵元

**Slide text.** 固定两个正交归一轨道 (a,b)，并限制每个轨道恰有一个电子。直接积分比较两个轨道的密度分布，交换积分来自不可区分电子的交换矩阵元；当前模型仅保留这种固定占据下的直接库仑交换。

**Equations.**
\[
D=\iint |\phi_a(1)|^2v(1-2)|\phi_b(2)|^2\,d1\,d2,
\]
\[
K=\iint\phi_a^*(1)\phi_b^*(2)v(1-2)\phi_b(1)\phi_a(2)\,d1\,d2,
\quad v(1-2)=\frac{e^2}{4\pi\varepsilon_0|\mathbf r_1-\mathbf r_2|}.
\]

**Visual plan.** Native diagram with two labeled orbitals, two electron-coordinate nodes, and straight versus exchanged connections. An inset “保留：固定占据；本模型未加入：电子跃迁产生的超交换” is short and physically necessary. Existing A01 may supply only a small two-site context.

**Sources.** PDF p.1, Eqs. (1)–(3). **Avoid.** Interpreting exchange connections as electrons following classical physical paths; equating (K) with a separately postulated magnetic interaction; inventing numerical (D,K).

### 04 — 四个自旋基矢，把库仑作用写成 (4\times4) 矩阵

**Slide text.** 采用固定产生算符顺序 (|\sigma_a\tau_b\rangle=f^\dagger_{a\sigma}f^\dagger_{b\tau}|0\rangle)。费米反对易关系使反平行态之间的交换矩阵元为 (-K)，而平行态的能量为 (D-K)。

**Equations.**
\[
V_{ab}=D\hat n_a\hat n_b+K\sum_{\sigma\tau}f^\dagger_{a\sigma}f^\dagger_{b\tau}f_{a\tau}f_{b\sigma},
\qquad
V_{ab}=\begin{pmatrix}D-K&0&0&0\\0&D&-K&0\\0&-K&D&0\\0&0&0&D-K\end{pmatrix}.
\]

**Visual plan.** Large readable colored matrix with labeled row/column bases (↑↑,↑↓,↓↑,↓↓). A two-state swap arrow illuminates the middle block; parallel states get their own diagonal highlights. No numerical heatmap is needed.

**Sources.** PDF p.2, Eqs. (8)–(11). **Avoid.** Losing the negative sign, double-counting the pair, or writing a factor (1/2) in front of (D) and (K) after the two equivalent orbital permutations have been counted.

### 05 — 对角化后：三重态与单重态的能量分裂

**Slide text.** 中间二阶块的对称组合对应 (D-K)，反对称组合对应 (D+K)。连同两个平行态，得到一个三重态能级和一个单重态能级；在这里的铁磁交换情形中，三重态能量更低。

**Equations.**
\[
|t_+\rangle=|\uparrow\uparrow\rangle,\quad
|t_0\rangle=\frac{|\uparrow\downarrow\rangle+|\downarrow\uparrow\rangle}{\sqrt2},\quad
|t_-\rangle=|\downarrow\downarrow\rangle,
\]
\[
|s\rangle=\frac{|\uparrow\downarrow\rangle-|\downarrow\uparrow\rangle}{\sqrt2},
\quad E_t=D-K,\quad E_s=D+K,\quad E_s-E_t=2K.
\]

**Visual plan.** Native two-level diagram with three state cards on the lower line and one state card on the upper line; vertical separation marked (2K). Beside it show the two eigenvectors of the (2\times2) block. (\pm,0) labels are the total (S^x) eigenvalues.

**Sources.** PDF p.2, Eqs. (12)–(14); classification follows the total-spin decomposition. **Avoid.** Saying “the triplet has only parallel spins”: (|t_0\rangle) is an entangled superposition of the two antiparallel basis states.

### 06 — 由矩阵匹配得到 Heisenberg 形式与 (J=2K)

**Slide text.** 自旋点积的矩阵具有完全相同的耦合结构。比较非对角元和对角元，便能确定交换系数与共同能量常数；这一步是同一算符的精确改写。

**Equations.**
\[
\mathbf S_a\cdot\mathbf S_b=\frac14\begin{pmatrix}1&0&0&0\\0&-1&2&0\\0&2&-1&0\\0&0&0&1\end{pmatrix},
\]
\[
V_{ab}=C\mathbb I-J\mathbf S_a\cdot\mathbf S_b,
\quad -J/2=-K,\quad C+J/4=D,
\]
\[
\boxed{J=2K,\qquad C=D-K/2.}
\]

**Visual plan.** Two matrices with matching colored entries, connected to two scalar matching equations; a small energy-level check gives (C-J/4=D-K) and (C+3J/4=D+K).

**Sources.** PDF p.3, Eqs. (17)–(20); p.2 Eq. (15) for the (x)-quantized convention. **Avoid.** Reversing the Hamiltonian sign or presenting (J=K); introducing physical (ℏ) into dimensionless spin matrices while leaving the coefficient unchanged.

### 07 — 从一条键到二维晶格：两种空间方向的交换强度

**Slide text.** 对最近邻键求和，并去掉固定占据产生的共同常数，就得到二维铁磁交换模型。(J_x\ne J_y) 描述水平与竖直键强度不同；每条键的自旋耦合仍是旋转对称的点积。

**Equation.**
\[
H=-J_x\sum_{\langle ij\rangle_x}\mathbf S_i\cdot\mathbf S_j
-J_y\sum_{\langle ij\rangle_y}\mathbf S_i\cdot\mathbf S_j,
\qquad J_x,J_y>0.
\]

**Visual plan.** A01 large, with horizontal and vertical bonds labeled and a unit cell/cell spacing (a) callout. A small before/after energy-zero diagram shows the constant (\sum_{\langle ij\rangle}(D_{ij}-K_{ij}/2)) being removed from every state alike.

**Sources.** PDF p.3, Eqs. (21)–(22), and p.4 first paragraph. **Avoid.** Calling the parameter asymmetry an XXZ easy-axis anisotropy or counting each bond twice.

### 08 — 全极化基态与单翻转子空间

**Slide text.** 每条铁磁键的最低能量是 (-J_{ij}/4)，全极化态同时达到所有键的下界。选定一个翻转后，任意叠加态只需记录翻转位置；其状态空间维数从整个自旋空间的 (2^{\mathcal N}) 缩减为 (\mathcal N)。

**Equations.**
\[
|F\rangle=|\uparrow_1\cdots\uparrow_{\mathcal N}\rangle,
\qquad E_F=-\frac14\sum_{\langle ij\rangle}J_{ij}
=-\frac{\mathcal N}{4}(J_x+J_y),
\]
\[
|\Psi\rangle=\sum_i c_i|i\rangle,\qquad\sum_i|c_i|^2=1.
\]

**Visual plan.** Native all-up lattice beside three different one-flip basis configurations, plus a small “固定一个翻转” sector diagram. B01 supplies the probability view.

**Sources.** PDF pp.3–4, Eqs. (23)–(26), (30). **Avoid.** Claiming a unique ground state or claiming the whole many-body Hilbert space is equivalent to one magnon.

### 09 — 一条交换键如何把翻转传给邻居

**Slide text.** 连接翻转位置 (i) 与邻居 (j) 的键产生两项：一项保留翻转位置，一项把翻转转移到邻居。与全极化背景相比，每条相连键还带来 (J_{ij}/2) 的对角能量增量。

**Equations.**
\[
-J_{ij}\mathbf S_i\cdot\mathbf S_j|i\rangle=\frac{J_{ij}}4|i\rangle-\frac{J_{ij}}2|j\rangle,
\]
\[
(H-E_F)|i\rangle=\frac12\sum_{j\sim i}J_{ij}(|i\rangle-|j\rangle).
\]

**Visual plan.** Native bond action arrow (|\downarrow_i\uparrow_j\rangle\to(J/4)|\downarrow_i\uparrow_j\rangle-(J/2)|\uparrow_i\downarrow_j\rangle); below, a center site and four neighbors with couplings (-J_x/2,-J_y/2). State explicitly that the subspace is invariant.

**Sources.** PDF p.4, Eqs. (27)–(29). **Avoid.** Referring to this derivation as an uncontrolled small-angle or Holstein–Primakoff approximation: for the selected initial sector it is exact.

### 10 — 概率振幅的运动方程：离散的相干传播

**Slide text.** 把单翻转展开代入薛定谔方程，再比较每个 (|i\rangle) 的系数，就得到格点振幅的运动方程。振幅在近邻之间相干耦合，观测概率要在求得复振幅后取模平方。

**Equations.**
\[
i\hbar\dot c_i=E_Fc_i+\frac12\sum_{j\sim i}J_{ij}(c_i-c_j),
\]
\[
i\hbar\dot c_{m,n}=(E_F+J_x+J_y)c_{m,n}
-\frac{J_x}{2}(c_{m+1,n}+c_{m-1,n})
-\frac{J_y}{2}(c_{m,n+1}+c_{m,n-1}).
\]

**Visual plan.** Four-neighbor stencil with on-site and hopping coefficients, and a small pipeline (c\to|c|^2\to P). Use B03 as a narrow preview strip if readable. A short footnote states “原PDF取ℏ=1；此处恢复ℏ”.

**Sources.** PDF pp.4–5, Eqs. (31)–(35). **Avoid.** Writing a classical rate equation for (P_i), or equating interference-driven redistribution with dissipation.

### 11 — 平面波代入后，得到精确的余弦色散

**Slide text.** 均匀晶格的平移不变性允许使用平面波模式。向相邻格点移动只产生相位因子，把四个邻居的相位相加就得到余弦项，因此色散不需要另加近似。

**Equations.**
\[
c_i=\mathcal N^{-1/2}e^{i\mathbf k\cdot\mathbf r_i-iE_{\mathbf k}t/\hbar},\qquad
c_{i\pm\mathbf e_\mu}=e^{\pm ik_\mu a}c_i,
\]
\[
E_{\mathbf k}=E_F+J_x+J_y-J_x\cos k_xa-J_y\cos k_ya,
\quad\varepsilon=E_{\mathbf k}-E_F.
\]

**Visual plan.** Native chain of equal-amplitude sites with advancing phase arrows, paired with A02 as the destination of the derivation. Bottom convention strip introduces (q_\mu=k_\mu a, \eta=J_y/J_x,  e=\varepsilon/J_x), so subsequent plots have defined axes.

**Sources.** PDF p.5, Eqs. (36)–(39). **Avoid.** Calling (\varepsilon) the total lattice energy; the (q=0) mode has zero excitation energy, not zero total exchange energy.

### 12 — 先读曲面，再比较方向截面

**Slide text.** 色散曲面的高度给出每个波矢的激发能。减小 (J_y/J_x) 会压低沿 (q_y) 方向的起伏；共同坐标下的截面使这种差异可以直接比较。

**Equation and values.**
\[
e=1-\cos q_x+\eta(1-\cos q_y),\qquad0\le e\le2(1+\eta).
\]

**Visual plan.** A02 and A03 surfaces as two comparably sized panels, plus one clean crop of A04 axial cuts. Annotate (\eta=1) band top 4 and (\eta=0.35) band top 2.7. Both surfaces already share the same color scale.

**Sources.** PDF p.5 Eq. (39); A02–A04 manifests. **Avoid.** Letting separate color scales make anisotropic differences invisible; calling the two axis cuts a complete description of every oblique direction.

### 13 — 长波近似从哪里来，它在哪个范围适用

**Slide text.** 当整个相关频谱都靠近原点时，余弦可展开成二次函数。此时等频线近似椭圆；只有等方交换且小波矢时才近似为圆，整个布里渊区仍保留方格晶格特征。

**Equations.**
\[
e\simeq\frac12(q_x^2+\eta q_y^2),\qquad
1-\cos q=\frac{q^2}{2}+O(q^4).
\]

**Visual plan.** Dominant A08 exact/parabolic comparison, with A05 small-(q) equal-frequency view. A09 error curve can be an inset; source thresholds (q\approx0.345) for 1% and (q\approx0.763) for 5% are for **axis energy relative error only**.

**Sources.** Derived from PDF Eq. (39); A05, A08, A09. **Avoid.** Applying the long-wave model to a single-site initial state spanning the full Brillouin zone; interpreting energy-error thresholds as dynamical fidelity bounds.

### 14 — 色散的斜率决定群速度，能量越高未必越快

**Slide text.** 群速度来自色散梯度，方向垂直于等频线。能带底部和边界处斜率为零，最大分量速度出现在 (q_\mu=\pm\pi/2)；传播方向需要从梯度判断。

**Equations.**
\[
\mathbf v_g=\frac1\hbar\nabla_{\mathbf k}\varepsilon
=\frac{J_xa}{\hbar}(\sin q_x,\eta\sin q_y),
\qquad\mathbf u=(\sin q_x,\eta\sin q_y).
\]

**Visual plan.** A07 slope-and-speed curve and A06 gradient arrows. A10's paired arrows may replace a low-value duplicate panel. Important visual labels distinguish wavevector arrow from velocity arrow.

**Sources.** Direct derivative of PDF Eq. (39); A06, A07, A10. **Avoid.** Universally setting (\mathbf v_g\parallel\mathbf k); using one group-velocity arrow to represent a broadband point excitation.

### 15 — 把理论变成模拟：逐模式相位演化

**Slide text.** 先去除所有格点共有的 (E_F) 相位，再对初态做 Fourier 变换。每个模式的谱概率保持不变，但频率不同会积累不同相位；逆变换给出随时间变化的空间图像。

**Equations.**
\[
\psi_i=e^{iE_Ft/\hbar}c_i,\qquad\tau=J_xt/\hbar,
\qquad A(\mathbf q,\tau)=A(\mathbf q,0)e^{-ie(\mathbf q)\tau},
\]
\[
\psi(\tau)=\mathcal F^{-1}\!\left[\mathcal F[\psi(0)]e^{-ie\tau}\right],
\qquad |\psi_i|^2=|c_i|^2.
\]

**Visual plan.** Editable four-stage diagram with real-space image → FFT spectrum → phase wheel → evolved real-space image. A small C12 spectrum plot supports probability conservation. Parameter strip: (256\times256), periodic numerical lattice, complete cosine dispersion, finite-window boundary checks.

**Sources.** PDF Eq. (39), THEORY §3, model manifests. **Avoid.** Saying “no numerical error”: there is no time-step integration error, but finite-domain and floating-point errors remain. The PDF retains (E_F); the simulation transformation must be stated explicitly.

### 16 — 单格点翻转包含整个能带，先从近邻展开

**Slide text.** 单点初态在实空间最局域，因此离散波矢上的权重均匀。短时间内最先可见的是近邻概率增长，随后不同传播路径相干叠加。

**Equations.**
\[
\psi_{m,n}(0)=\delta_{m0}\delta_{n0},\qquad
|A(\mathbf q,0)|^2=1/\mathcal N.
\]

**Visual plan.** B01 initial condition and B02 flat spectrum occupy the top strip; B03 early snapshots or B14 GIF dominates the lower half. Label B02's plotted scale (\mathcal N|A|^2) so a flat ordinate of 1 is not misread as total probability (\mathcal N).

**Sources.** PDF p.4 Eq. (30), p.5 Eqs. (36)–(39); B01–B03, B14. **Avoid.** Assigning one center wavevector or one velocity to this initial state.

### 17 — 从二维快照到时空图：传播前沿与干涉

**Slide text.** 后期分布呈现向外推进的主要前沿，以及持续存在的干涉条纹。沿另一坐标求和得到边际概率后，可以在一张时空图里读出前沿随时间的运动。

**Equations.**
\[
P_x(m,\tau)=\sum_nP_{m,n}(\tau),\qquad |u_x|\le1,
\qquad m\simeq\pm\tau\ \text{为主要前沿尺度}.
\]

**Visual plan.** B04 two selected late snapshots plus B07 spacetime plot. B15 GIF can replace snapshots in slideshow, with a useful poster frame for PDF. Preserve logarithmic colorbar labels.

**Sources.** B04, B07; derivative of PDF Eq. (39). **Avoid.** Calling the dashed front a strict probability cutoff or “relativistic light cone”; isotropic bonds on a square lattice do not require circular point-spread patterns.

### 18 — 交换各向异性控制展开方向与弹道宽度

**Slide text.** 固定 (J_x)，减小 (J_y) 只减慢竖直方向的传播。概率宽度正比于时间，说明这里的局域激发具有弹道展开；(\eta=0) 是彼此解耦的一维链极限。

**Equations.**
\[
\sigma_{n_x}=\tau/\sqrt2,\qquad\sigma_{n_y}=\eta\tau/\sqrt2,
\qquad\sigma_x=a\sigma_{n_x},\ \sigma_y=a\sigma_{n_y}.
\]

**Visual plan.** B05 comparison (\eta=0,0.3,1) plus B09 measured/analytic RMS curves. B08 spacetime may be supporting crop, or B16 GIF with static backup. Use symbols (sigma_{n_\mu}) or axis unit “格点数” consistently to avoid an extra (a).

**Sources.** THEORY §4; B05, B08, B09, B16. **Avoid.** Describing this as diffusive (\sqrt t) spreading; treating (\eta=0) as the strict (J_y>0) baseline rather than an explicitly added comparison limit.

### 19 — 概率图如何对应自旋观测：中心下降不是耗散

**Slide text.** 单翻转概率直接决定局域纵向磁化的缺失量。原点概率会下降并振荡，但总概率始终为1；这些变化来自相干传播与干涉。

**Equations.**
\[
\langle S_i^x\rangle=\frac12-P_i,\qquad
\sum_i\left(\frac12-\langle S_i^x\rangle\right)=1,
\]
\[
P_{00}(\tau)=\mathrm J_0(\tau)^2\mathrm J_0(\eta\tau)^2.
\]

**Visual plan.** B12 probability-to-spin map dominates one side; B10 return-probability plot fills the other side. A small conservation badge connects the two. The Bessel derivation is deferred to Appendix B.

**Sources.** One-flip basis PDF Eq. (26); THEORY §1,§4; B10, B12. **Avoid.** Equating a lower peak with loss of magnon number; confusing Bessel (mathrm J_0) with exchange (J_x,J_y). Fixed-number states have zero transverse spin expectation.

### 20 — Gaussian 初态：包络决定频宽，载波决定谱中心

**Slide text.** Gaussian包络把频谱集中在有限区域，便于区分整体运动与形状变化。乘上平面波载波会改变初始相位和谱中心，同时保持初始概率包络不变。

**Equations.**
\[
\psi(\mathbf n,0)\propto e^{-n_x^2/(4\sigma_x^2)-n_y^2/(4\sigma_y^2)}e^{i\mathbf q_0\cdot\mathbf n},
\qquad\Delta q_\mu\simeq\frac1{2\sigma_\mu}.
\]

**Visual plan.** C01 envelope/phase/spectrum triad as main figure, C02 width/bandwidth comparison as supporting crop. The formula caption explicitly identifies (sigma_\mu) as initial **probability RMS width in site units**.

**Sources.** THEORY §5; C01, C02. **Avoid.** Omitting the factor 4 in the amplitude exponent; calling the continuous Gaussian bandwidth relation exact for arbitrary narrow discrete wave packets or a Brillouin-zone seam crossing.

### 21 — 相同包络，不同载波：静止展宽、右行、左行与斜向

**Slide text.** 零载波的谱分布关于原点对称，所以平均速度为零，但波包仍会展宽。选择非零载波后，谱平均速度可以非零，包络一边移动一边发生形变。

**Equation.**
\[
\mathbf q_0=(0,0),\ (-0.7,0),\ (0.7,0),\ (0.7,0.7),\qquad\sigma=4.
\]

**Visual plan.** C03/C04 use matched initial and final panels; C05 shows the three moving directions. A C15 or C16 GIF occupies the same planned image zone with a static summary underneath. Preserve common color scales and coordinate ranges.

**Sources.** C03–C05, C15–C16. **Avoid.** Saying zero mean group velocity means no dynamics; interpreting ((0.7,0)) as no spreading in (y).

### 22 — 质心速度要对频谱求平均，传播方向不总等于波矢方向

**Slide text.** 有限频宽下，质心沿全部频谱的平均速度运动；中心波矢处的群速度只是窄带近似。各向异性使相同斜向载波对应更偏向强交换轴的传播方向。

**Equations.**
\[
\overline{\mathbf u}=\sum_{\mathbf q}|A(\mathbf q,0)|^2\nabla_\mathbf q e,
\qquad\langle\mathbf n(\tau)\rangle=\langle\mathbf n(0)\rangle+\tau\overline{\mathbf u}.
\]

**Visual plan.** C06 centroid prediction/measurement comparison and C10 anisotropic direction side-by-side. Numeric example from C10: (\mathbf q_0=(0.7,0.7)), (\eta=1\to0.3), direction (45^\circ\to16.7^\circ), with equal initial widths.

**Sources.** THEORY §5; C06, C10; A10 for the general direction distinction. **Avoid.** Calling (\mathbf u(\mathbf q_0)) exact for a finite-width packet. Note that C10 uses (\eta=0.3), while A03/A06 use 0.35; do not merge the cases silently.

### 23 — 在共动坐标里观察展宽：初始宽度的影响

**Slide text.** 减去实际质心后，剩下的就是包络本身的变化。较宽初态对应较窄频谱，通常包含较小的速度差，因此相对展宽较缓；这是以更大的初始空间范围为代价的选择。

**Equations.**
\[
\xi_\mu=n_\mu-\langle n_\mu\rangle,
\qquad\sigma_\mu^2(\tau)=\sum_{\mathbf n}\xi_\mu^2P_{\mathbf n}(\tau).
\]

**Visual plan.** C07 unrescaled comoving marginals and C08 width comparison, with (\sigma=3,6,10) clearly labeled. C17 can be an animation inset or replacement. Avoid showing all source panels if labels would be smaller than comfortable slide text.

**Sources.** C07–C08, C17. **Avoid.** Rescaling every peak to height 1 without labeling it; claiming fair identical-resource performance for different initial widths. C08's scaled panel uses (u=\xi/\sigma) and vertical coordinate (\sigma P_x), which preserves area.

### 24 — 展宽的共同机制：速度差与相对相位积累

**Slide text.** 一阶色散让包络平移，二阶及更高阶残余色散改变不同频谱成分的相对相位。对于当前无啁啾Gaussian，初始位置—速度协方差为零，宽度增长可以用速度方差定量预测。

**Equations.**
\[
e(\mathbf q_0+\delta\mathbf q)=e_0+\mathbf u_0\cdot\delta\mathbf q
+\tfrac12\delta\mathbf q^TH_e\delta\mathbf q+\cdots,
\]
\[
H_e=\mathrm{diag}(\cos q_{0x},\eta\cos q_{0y}),
\qquad\mathrm{Var}[n_\mu(\tau)]=\mathrm{Var}[n_\mu(0)]+\tau^2\mathrm{Var}[u_\mu].
\]

**Visual plan.** C12 spectrum/phase figure and C09 RMS relation validation. A small native “常数：全局相位 / 一阶：平移 / 高阶：形变” diagram replaces prose-heavy explanation. C11 anisotropic width can be reserved for Appendix C if the page becomes crowded.

**Sources.** Derived from Eq. (39); THEORY §5; C09, C12. **Avoid.** Saying unchanged spectral probability implies preserved real-space shape; applying the no-covariance width formula to arbitrary chirped initial states.

### 25 — 从理解展宽走向抑制展宽：零二阶曲率的初步结果

**Slide text.** 在 (\mathbf q_0=(\pi/2,\pi/2)) 附近，两个方向的二阶色散系数同时为零。相同初始宽度下，模拟显示有限时间内形变显著减缓；三阶相位仍会积累，限定了这一机制的适用范围。

**Equations.**
\[
H_e(\pi/2,\pi/2)=0,
\qquad e-e_0-\mathbf u_0\cdot\delta\mathbf q
=-\frac{\delta q_x^3+\eta\delta q_y^3}{6}+O(|\delta\mathbf q|^5).
\]

**Visual plan.** C13 same-(\sigma=3) comparison dominates; A11 curvature plot can be a compact supporting panel. C14 (\sigma=2) cubic-distortion panel only as a separately labeled counterpoint, or move to appendix so the unequal widths cannot be mistaken for one matched experiment.

**Sources.** THEORY §6; A11, C13, C14. **Avoid.** “严格无色散”“无限时间保形”; interpreting C13's complex-state overlap as a probability-profile-only metric; comparing C13 and C14 as same-width performance.

### 26 — 当前已经建立的物理链条，与下一步研究

**Slide text.** 已建立从库仑交换矩阵到单翻转精确色散的完整链条，并用两类初态验证了速度、方向和展宽机制。下一步围绕有限频宽下的近似保形展开：选择载波、设计相关频谱，再在相同初始尺度下比较传播距离与误差敏感性。

**Content blocks.** “已建立” includes (J=2K)、单翻转精确闭合、(\mathbf u=\nabla e)、单点弹道展开、Gaussian速度方差。“后续问题” includes 高阶色散、横向准直与整体保形的区别、有限尺寸和制备误差。

**Visual plan.** Three compact evidence panels: B09 width check, C06 speed check, C13 initial preservation result; a clear causal chain connects the results. Include one concise numerical-evidence line: sparse-Hamiltonian independent (L^2) difference (3.4\times10^{-15}); expanded Gaussian-domain difference at most (1.04\times10^{-14}) in recorded independent cases. This is computational verification, not experimental validation.

**Sources.** PDF Eqs. (20), (29), (39); B09, C06, C13; `checks_independent.json`. **Avoid.** Framing future correlated-spectrum/self-collimation studies as already simulated; treating 39 plots as 39 independent physical discoveries.

## Appendices

### 27 — 附录A：费米符号、计数与矩阵匹配的核对

**Slide text.** 固定产生算符顺序后，交换项的负号可以直接通过反对易关系核对。两种相同贡献的轨道排列抵消二次量子化式的 (1/2)，使 (J=2K) 与每条键计一次的约定一致。

**Equations.**
\[
f^\dagger_{a\downarrow}f^\dagger_{b\uparrow}f_{a\uparrow}f_{b\downarrow}
(f^\dagger_{a\uparrow}f^\dagger_{b\downarrow}|0\rangle)
=-|\downarrow_a\uparrow_b\rangle,
\]
\[
S^x=\sigma_z/2,\quad S^y=\sigma_x/2,\quad S^z=\sigma_y/2
\quad\text{（当前沿x量子化的基底与相位约定）}.
\]

**Visual plan.** Native operator-order ribbon, repeated (2\times2) block with arrows to the two eigenvectors, and compact (4\times4) identity check. **Sources.** PDF pp.1–3, Eqs. (4)–(20). **Avoid.** Replacing (S^x) by the usual (z)-quantized off-diagonal matrix without changing the basis convention.

### 28 — 附录B：单点传播的Bessel解析核与独立验证

**Slide text.** 色散对两个方向可分离，因此点激发传播核也分离为两个Bessel函数。解析解同时预测复振幅、返回概率和弹道宽度，是FFT实现之外的独立核对。

**Equations.**
\[
\psi_{m,n}(\tau)=e^{-i(1+\eta)\tau}i^{m+n}\mathrm J_m(\tau)\mathrm J_n(\eta\tau),
\]
\[
P_{m,n}=\mathrm J_m(\tau)^2\mathrm J_n(\eta\tau)^2,
\quad\sum_m m^2\mathrm J_m(z)^2=z^2/2.
\]

**Visual plan.** B13 FFT/Bessel comparison and B06 marginal-probability plot; a small B10 return curve if it remains legible. **Sources.** THEORY §4; B06, B10, B13; `checks_independent.json`. **Avoid.** Claiming the infinite-lattice formula exactly equals an arbitrary small periodic lattice at all times; restore (e^{-iE_Ft/\hbar}) if describing original (c) instead of reduced (\psi).

### 29 — 附录C：Gaussian矩关系、高阶形变与有限盒检查

**Slide text.** 一般初态的宽度公式含位置—速度协方差；无啁啾实包络乘载波时该项为零。计算还通过扩大晶格区分物理展宽和周期边界污染，复杂态重合度则补充了RMS宽度无法描述的相位变化。

**Equations.**
\[
\mathrm{Var}[n_\mu(\tau)]=\mathrm{Var}[n_\mu(0)]
+2\tau\,\mathrm{Cov}_{\mathrm{sym}}(n_\mu,u_\mu)
+\tau^2\mathrm{Var}[u_\mu],
\]
\[
F(\tau)=|\langle\psi_{\mathrm{translated}}(\tau)|\psi(\tau)\rangle|^2.
\]

**Visual plan.** C11 anisotropic RMS widths and C14 cubic-distortion panel. A compact table lists checked cases: (\sigma=3,6,10), (\eta=1,0.3), ordinary and inflection carriers, (384^2\to768^2), (\tau=60). Explain that C14 uses (\sigma=2), independent from C13.

**Sources.** THEORY §5–6; C11, C14; `checks_independent.json`. **Avoid.** Omitting covariance for all possible states; calling (F) a direct intensity overlap or interpreting a finite-box precheck failure as a physical effect.

### 30 — 附录D：来源、参数范围与复现入口

**Slide text.** 理论来自五页单磁子推导，全部模拟采用同一个均匀最近邻交换模型。图像、原始数组、参数manifest与独立检查记录共同构成可追溯结果；报告中的无量纲参数用于机制研究。

**Table.**

| Item | Scope / source |
|---|---|
| 原理PDF | `Note/single_magnon_derivation/main.pdf`, pp.1–5, Eqs.(1)–(39) |
| 色散图组 | A01–A12；常用 (\eta=1,0.35)，标注各图实际取值 |
| 单点图组 | B01–B13；(\eta=0,0.3,1) 主对照；完整余弦谱演化 |
| Gaussian图组 | C01–C14；(\sigma=3,4,6,10) 主例，C14独立 (\sigma=2) |
| 动画 | B14–B17、C15–C18；每段有静态替代图 |
| 原始数据 | `dispersion_arrays.npz`、`local_flip_data.npz`、`gaussian_simulation_data.npz` |
| 计算核验 | `checks_independent.json`；27组独立检查，另有原模型10项回归检查 |
| 复现 | `python figures/midterm-report/build_all.py` |

**Visual plan.** Compact provenance flow from source PDF to equations to NPZ to plots, with one small montage. Link local gallery in deck notes or hyperlink. **Sources.** Package README and manifests. **Avoid.** Claiming real-material units or parameter calibration that is absent from the project; importing unrelated external literature results as measured project evidence.

## Highest-priority scientific review checks for the finished slides

1. The Hamiltonian sign and factor remain (H=-\sum J_{ij}\mathbf S_i\cdot\mathbf S_j, J=2K, S=1/2). Each bond is counted once.
2. The (4\times4) Coulomb matrix, its two eigenvalues and state multiplicities, and the exact (S\cdot S) matching are shown legibly, not merely named.
3. All ↑/↓ are along ±x. Do not accidentally label probability maps as transverse spin precession.
4. The exact-sector claim is restricted to one-flip initial states; no assumption about arbitrary many-body states is implied.
5. The derivation uses total (E_{\mathbf k}); excitation plots use (\varepsilon=E_{\mathbf k}-E_F); simulations use (\psi=e^{iE_Ft/\hbar}c). These three objects are explicitly connected.
6. (J_x\ne J_y) is real-space bond anisotropy. It does not insert spin-space easy-axis/easy-plane terms.
7. A-group anisotropy commonly uses 0.35; B/C-group propagation commonly uses 0.3. Do not label a shared combined figure with just one of these values.
8. (N=256) in manifests means (256\times256) sites. (\mathcal N) in theory is the total number of sites.
9. Gaussian (\sigma) is the probability RMS width; amplitude exponent has denominator (4\sigma^2). The bandwidth expression has its continuum/wide-envelope qualification.
10. Group velocity at (\mathbf q_0) is a narrowband approximation to actual centroid speed; recorded precise predictions use spectral averages.
11. Equal couplings preserve square-lattice discrete symmetry, not exact continuous rotational symmetry throughout the band.
12. Front lines indicate the major ballistic scale, not compact support; probability tails beyond them remain nonzero.
13. Single-point (\sigma\propto\tau) and Gaussian curvature/velocity-variance spreading are related but distinct initial-state results.
14. Fixed log/linear color scales and consistent axes survive cropping/recomposition. Every scaled marginal has its scaling written explicitly.
15. Zero second derivative at ((\pi/2,\pi/2)) does not eliminate cubic dispersion. C13 and C14 have different widths and different immediate comparison purposes.
16. Independent numerical checks establish numerical consistency of the stated model, not experimental confirmation or full robustness to omitted physical effects.

