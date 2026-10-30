# 线性自旋波的保形传播：文献导读

检索与下载日期：2026-10-19。问题是“在不依靠非线性的条件下，怎样设计传播形状不变的自旋波波包”。本次从该问题出发检索，不把现有 toy model 当作既定研究方向。

已下载 **9 篇 arXiv 论文：6 篇直接研究自旋波，3 篇提供光学中的线性波包设计方法**。全部下载的是本次官方摘要页所列的最新 arXiv 版本，不等于期刊最终排版版本。作者、标题、版本、DOI、来源 URL、文件大小和 SHA-256 见 [manifest.json](manifest.json)，引用条目见 [references.bib](references.bib)。

## 先用人话说结论

这件事已经有人做过，而且不止一条路。最接近“短脉冲走出去以后不变长”的，是在 YIG 磁性波导里找到一段合适频率，让组成脉冲的各个频率成分传播得差不多快。另一类工作让波束不向左右散开；还有人把光学中的特殊波束搬到自旋波里，利用不同部分之间的干涉维持一个窄的主峰。

这些结果不能混为一谈：**一条持续发射的窄波束不变宽，并不证明一小团短波包前后左右都不变形。** 同样，形状保持不代表振幅不衰减，传播后恢复形状也不代表中间一直没有变形。

目前最直接的实验依据是 2108.08054。若研究重点是“设计初始波包本身”，则 Bessel–Gaussian 自旋波工作及 space-time wave packets 的频谱设计方法值得比较。但后三篇光学论文只提供可迁移方法，本次没有找到并核实一篇已经在磁性自旋波中实现同类完整时空保形波包的论文；这不构成“此前无人做过”的证明。

## 已有工作与对应 PDF

### 1. 找到不同频率成分传播速度接近的窗口：最直接的脉冲实验

**B. Divinskiy et al., Dispersionless propagation of ultra-short spin-wave pulses in ultrathin yttrium iron garnet waveguides.** Phys. Rev. Applied 16, 024028 (2021). [arXiv:2108.08054v1](https://arxiv.org/abs/2108.08054v1) · [本地 PDF](spin-wave/2108.08054v1_dispersionless-pulses.pdf)

- 做法：使用厚 50 nm、宽 1 μm 的 YIG 波导，激发约 2.5 ns 的短脉冲，改变载频，利用时空分辨的 Brillouin light scattering 测量传播。
- 结果：在约 10 μm 的传播距离上，4.8 GHz 的脉冲宽度约增至三倍；5.2 GHz 的脉冲宽度几乎不变。5.2 GHz 是这组样品和磁场下的结果，不是所有 YIG 器件的通用频率。
- 原因：偶极作用和交换作用对群速度的影响相互竞争，使群速度在一个频段内对频率变化不敏感。可以理解为“快慢不同的队员，在这一段频率内跑得差不多快”。
- 与线性的关系：解释来自线性色散关系，没有采用非线性自聚焦来抵消展宽；微磁模拟的激发场为 0.1 Oe。这里没有把全 LLG 数值求解本身误称为严格线性方程求解。
- 边界：这是有限频宽、有限距离、受波导横向约束的近似无展宽传播；不是无限大二维薄膜上任意形状、任意频宽波包的永久保形，也不代表无损耗。
- 正文定位：PDF 第 5–10 页；Fig. 2 在 PDF 第 19 页，Fig. 4 及相关解释讨论偶极与交换的竞争。优先读 Fig. 2(b,c)。

### 2. 改变波导形状，把自旋波送入更合适的传播区域

**S. R. Lake et al., Efficient geometrical control of spin waves in microscopic YIG waveguides.** (2021 preprint). DOI: 10.1063/5.0071757. [arXiv:2111.02236v1](https://arxiv.org/abs/2111.02236v1) · [本地 PDF](spin-wave/2111.02236v1_geometrical-control.pdf)

- 做法：将 100 nm 厚的 YIG 波导从宽 2 μm 逐渐缩窄到 0.5 μm，让波长下降，并改变群速度。
- 证据：实验与微磁模拟研究波长转换；用 20 ns 脉冲的传播延迟提取速度，发现窄端群速度对频率的依赖明显减弱，从而支持近似无色散传播的判断。
- 用人话说：通过改变“道路”，让原来难直接激发的短波长状态进入一个不容易前后拉开的工作区。
- 边界：过渡区会减速和空间压缩，横向宽度也随波导改变；不能称为整个过渡过程中的刚性平移。本文的相关证据重心是群速度特征，不应与上一篇直接测量短脉冲展宽的证据等同。
- 正文定位：PDF 第 7–8 页和 Fig. 4。

### 3. 把波束的不同部分安排好，用干涉维持窄的中心结构

**M. Vogel, B. Hillebrands, G. von Freymann, Spin-Wave Optical Elements: Towards Spin-Wave Fourier Optics.** (2019 preprint). DOI: 10.1063/5.0018519. [arXiv:1906.02301v1](https://arxiv.org/abs/1906.02301v1) · [本地 PDF](spin-wave/1906.02301v1_bessel-gaussian-fourier-optics.pdf)

- 做法：在 YIG 薄膜中用温度引起的饱和磁化变化，构造一个三角形的折射区域，充当二维 axicon；让入射 Gaussian 波束折射、相互干涉。
- 结果：微磁模拟得到近似 Bessel–Gaussian 自旋波束，并展示遇到障碍后的自愈。作者对横向轮廓作 Bessel–Gaussian 拟合，报告约 0.88 的决定系数；应理解为近似 Bessel-like 结构。
- 与课题的关系：它表明设计波束的空间结构和相位，是实际存在的自旋波研究路线；机制是折射和干涉，并非孤子式自聚焦。
- 边界：保形区域由有限入射波束、折射率和 axicon 角度决定。论文是波束模拟，不是前后方向也局域的短脉冲实验。它采用完整 LLG 求解，所读正文没有提供系统的激发幅度趋零检验；若复现时要求严格无非线性，应另做线性化或幅度缩放检查。
- 正文定位：PDF 第 1–3 页，Section I、Fig. 2–3、Eq. (3)；附录给出面内磁化模式。

### 4. 让不同方向的波都往同一方向输送能量：自准直

**J. W. Kłos et al., All-Angle Collimation for Spin Waves.** IEEE Magnetics Letters 6, 3500804 (2015); arXiv 上传于 2017 年。[arXiv:1703.05548v1](https://arxiv.org/abs/1703.05548v1) · [本地 PDF](spin-wave/1703.05548v1_all-angle-collimation.pdf)

- 做法：利用 Co/Py 界面两侧的磁性差异，或在 YIG 中制作周期孔阵列，改变等频曲线的形状，使相关区段接近平直。
- 结果：分析和模拟显示，入射方向不同的单频自旋波可以折射到相近方向；周期 YIG 结构给出全角度准直的色散设计。
- 与线性的关系：Co/Py 微磁模拟明确采用远小于饱和磁化的激发幅度，以保持在线性范围。
- 用人话说：不是把波“拴住”，而是把材料设计成让一批成分自然往同一个方向走。
- 边界：重点是单色波束方向与横向传播；相同方向不意味着不同频率的传播速度相同，不能自动推出短脉冲的纵向保形。金属磁体阻尼和界面耦合效率也会限制可用性。
- 正文定位：PDF 第 1–4 页，Fig. 1–3；第 2 页附近给出线性激发条件。

### 5. 利用材料各向异性，直接发射低发散的窄波束：caustic beams

**A. Wartelle et al., Caustic spin wave beams in soft, thin films: properties and classification.** Phys. Rev. B 107, 144431 (2023). [arXiv:2301.01220v1](https://arxiv.org/abs/2301.01220v1) · [本地 PDF](spin-wave/2301.01220v1_caustic-classification.pdf)

- 做法：系统分析薄膜的色散关系，寻找一组波矢变化时群速度方向变化很小的位置，并用时间分辨 Kerr 显微实验检验。
- 结果：得到低发散的定向波束，讨论高阶 caustic 点及可用参数范围。论文明确以线性小偏离为理论出发点。
- 用人话说：虽然波长或波矢有差别，这些波的能量却挤在同一方向传播，因此不容易向两侧散开。
- 边界：文中“宽带”有时指波矢范围宽，并不等于时间频率范围宽。群速度方向稳定，也不等于群速度大小稳定；仍不能直接宣称完整短脉冲保形。
- 正文定位：PDF 第 1–3 页的线性模型与 caustic 条件，及后文高阶 caustic 点、Fig. 13–14。

**D. Wagle et al., Shaping non-reciprocal caustic spin-wave beams.** 2024 初稿，2026 修订；Phys. Rev. B 113, L060405 (2026). [arXiv:2404.15011v4](https://arxiv.org/abs/2404.15011v4) · [本地 PDF](spin-wave/2404.15011v4_nonreciprocal-caustic-beams.pdf)

- 做法：通过具有纳米收窄部位的射频天线直接激发 caustic-like 波束，利用磁场和频率控制其方向、非互易性；用动态磁化率和激发场的傅里叶谱计算近场图样。
- 证据：近场模型、MuMax3 模拟和微聚焦 BLS 实验相互比较。
- 与课题的关系：提供了“想要这样的波束，激发源应该怎么做”的具体实现工具。
- 边界：正文模型计算的是固定频率的稳态磁化分布，验证波束成形与转向，不是短波包的完整保形传播。
- 正文定位：PDF 第 2 页 Eq. (1) 及近场构造，第 3–5 页实验图与频率/磁场调控。

## 可迁移的线性方法：必须与自旋波实证分开

### 6. 同时安排频率与传播方向：space-time wave packets

**H. He, C. Guo, M. Xiao, Non-Dispersive Space-Time Wave Packets Propagating in Dispersive Media.** (2021). [arXiv:2109.00782v1](https://arxiv.org/abs/2109.00782v1) · [本地 PDF](optical-method/2109.00782v1_space-time-dispersive-media.pdf)

这篇光学理论论文研究的正是：材料本来有色散，能否仍通过线性叠加得到不展宽波包？方法是把频率与空间波矢关联起来，而不是各自独立选取。PDF 第 1–2 页 Eqs. (3)–(4) 直接展示设计条件如何导出包络的刚性传播；后文讨论近轴、窄带及高阶项。

**M. Yessenov et al., Space-time wave packets.** (2022 review). [arXiv:2201.08297v1](https://arxiv.org/abs/2201.08297v1) · [本地 PDF](optical-method/2201.08297v1_space-time-review.pdf)

这篇长综述适合查设计路线和现实限制。优先看 Section 3 的传播不变性与频谱关联，Section 9.3 的频谱不确定度及传播距离。严格频谱约束的理想解与有限能量、有限孔径的实验实现必须区分：现实实现只能在有限范围内近似保形。

**N. K. Efremidis, Spatiotemporal diffraction-free pulsed beams in free-space of the Airy and Bessel type.** (2017). [arXiv:1711.04027v1](https://arxiv.org/abs/1711.04027v1) · [本地 PDF](optical-method/1711.04027v1_airy-bessel-pulsed-beams.pdf)

这篇给出用色散曲面与平面的交线构造 Airy、Bessel 等时空波包的具体例子，适合理解怎样把“选择频谱”落实成可计算的波形。研究对象是自由空间光，不是磁性材料；不能直接照搬其光锥色散。

**对自旋波的设计推论，而非上述论文已经完成的自旋波结果：** 在均匀、无耗散的线性单分支模型里，若所选成分满足

\[
\omega(\mathbf{k})=\omega_0+\mathbf{v}\cdot(\mathbf{k}-\mathbf{k}_0),
\]

代入平面波叠加的相位即可得到

\[
\psi(\mathbf{r},t)=e^{-i(\omega_0-\mathbf{v}\cdot\mathbf{k}_0)t}
\psi(\mathbf{r}-\mathbf{v}t,0).
\]

这表示图样以速度 \(\mathbf v\) 平移，另乘一个不影响强度的整体相位。设计上可考虑在真实自旋波色散曲面上挑选接近这一条件的频谱。接着还需检查其能否形成所需局域波包、实际天线能否激发、有限频谱厚度能保形多久，以及阻尼和不同模式是否破坏形状。不能从这个理想条件直接跳到“实验已实现”或“有限能量可无限距离严格保形”。

## 其他相关线索及排除项

- Schneider et al., **Nondiffractive Subwavelength Wave Beams in a Medium with Externally Controlled Anisotropy**, PRL 104, 197203 (2010), [期刊原始记录](https://doi.org/10.1103/PhysRevLett.104.197203)。官方摘要报告了 YIG 中近乎无衍射的亚波长横向波束实验，是 caustic 路线的重要早期工作。本次没有找到核实的 arXiv 版本，未下载，未做全文评估。
- Dai et al., **Magnetically tunable Airy-like beam of magnetostatic surface spin waves**, Chinese Optics Letters 19, 013501 (2021), [期刊原始记录](https://opg.optica.org/col/abstract.cfm?uri=col-19-1-013501)。官方摘要报告以 3/2 相位图样激发源在微磁模拟中生成 Airy-like 波束，并用磁场调节弯曲轨迹。本次未找到核实的 arXiv 版本，页面标记全文不可访问，未下载；只将其作为待补全文的线索，不以摘要断言严格线性保形。
- [1501.03493](https://arxiv.org/abs/1501.03493) 的“dispersionless spin waves”指近乎平坦能带与局域激发，不能因标题相似就当作“传播且不展宽”的直接证据；未收入下载集。
- 非线性包络孤子、spin-wave bullets、利用非线性产生高次谐波的 caustic 激发，不作为满足“无非线性”的主方案。相关文献可以用来比较，但不能替代本课题的线性解。
- Talbot 自成像关注特定距离上的图样重现，不能直接作为连续传播中一直不变形的证据。
- 光学自旋角动量、电子 spinor 波包、原子量子存储中的 spin wave，与磁性薄膜中的自旋波不同，本次不混入直接证据集合。

## 建议的阅读顺序和问题划分

先读 **2108.08054 的 Fig. 2–4**，弄清已经实现的脉冲效果。再读 **1906.02301 的 Fig. 2–3**，理解怎样设计空间波束。接着读 **2109.00782 的 Eqs. (3)–(4)**，判断能否把频谱关联用于你希望研究的自旋波体系。若选择二维薄膜方向，再深入 2301.01220 和 1703.05548。

选方案时，首先要区分：是否允许波导约束；要保持的是横向宽度、时间脉冲宽度，还是整个二维包络；是否接受整体衰减或弯曲轨迹；要求在哪个距离内达到多小的形变误差。这些定义决定哪些现有结果真正满足课题，而不是先由 toy model 限定路线。

## 检索与验证边界

这是一次以 arXiv 为主、追踪相关原始期刊记录的主题检索，不是穷尽式系统综述。检索词、纳入/排除规则与停止条件见 [search-log.md](search-log.md)。对下载论文核对了研究相关正文；未将 103 页综述声称为逐段精读。

9 个 PDF 均通过文件签名、打开解析、首页标题匹配、逐页文本提取和首页渲染检查；另实际查看了 2108.08054 的 Fig. 2。验证记录位于 [verification/checks.json](verification/checks.json)，首页预览位于 [verification/first-pages.jpg](verification/first-pages.jpg)。这些检查证明文件身份与可读性，不等于独立复现论文结果。
