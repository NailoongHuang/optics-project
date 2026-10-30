# 从文献展望到波包研究的四个最小验证

研究与检索日期：2026 年 10 月 21 日。可直接打开 [离线 Demo 页](index.html)，切换四项测试的结果图和动画。各目录均包含可复现脚本、参数、数值结果和测试说明。

本轮优先级判断是：

| 方向 | 最小测试后的判断 | 继续的理由或降级原因 |
|---|---|---|
| 有限源高阶 caustic | **优先继续，但以实际接收信号为目标** | 有有限、可量化的几何优势；损耗和失准也能消除优势，适合进一步做受约束的完整响应优化。 |
| 有限分辨率反流认证 | **有条件继续** | 构造出可认证的局域态；原自然拖尾过弱，测量界、制备预算和探测成本比单纯最大负流更关键。 |
| 含损耗的脉冲逆设计 | **相位敏感任务下可继续** | 复场匹配改善，但绝对信号下降，强度形状几乎未改善；未建立 ensemble 的额外优势。 |
| 频率无序与耦合无序 | **保留为校准基准，降低新机制优先级** | 匹配实际后向散射强度后，大部分接收差异消失。 |

这些判断依据有限范围内的实际测试，不是新颖性证明，也不等于已实现完整磁学器件。作者的开放问题与本轮实际能检验的子问题在下面逐项对应。

## 作者究竟留下了什么

| 原始文献与位置 | 作者明确留下的问题 | 本轮取出的子问题 |
|---|---|---|
| [Wartelle et al., PRB 107, 144431 (2023)](https://arxiv.org/html/2301.01220v1)，PDF p.13 §III.D、p.15 结论 | 高阶 caustic 相比普通点能增强多少幅度，以及如何得到有限实验幅度，未在文中定量完成。 | 相同有限输入角谱下，峰值、宽度及固定接收窗信号的收益能否经得住损耗与频偏。 |
| [Paterek & Goussev, PRL 136, 090202 (2026)](https://arxiv.org/html/2511.10155v2)，Discussion，PDF p.4；[Chen & Tang, PRA 113, 063304 (2026)](https://arxiv.org/html/2602.12767v2)，Conclusion，PDF p.9 | 平滑空间测量窗怎样影响 general backflow；强反流的细条纹怎样从多时密度测量中提取。 | 固定 PSF、制备宽度和时间窗，比较可认证概率增量及所需重复测量数。 |
| [Casulleras et al., PRApplied 19, 064085 (2023)](https://arxiv.org/html/2209.06608v1)，Conclusion，PDF p.6；[Vilsmeier et al. 2026 展望预印本](https://arxiv.org/html/2607.07324v1)，§4.1–4.2 | 在逆传播中纳入波长相关损耗；系统研究参数容差和激发端优化。 | 固定输入预算下比较相位逆传播、正则损耗补偿、matched filter 和同等训练条件下的 ensemble 设计。 |
| [Meier et al., Nature Physics 21, 1147–1152 (2025)，正式发表版](https://pmc.ncbi.nlm.nih.gov/articles/PMC12263443/)，Methods → Stability under perturbations，PDF p.9 | 作者预期裸 qubit 频率无序与耦合误差影响相近，但没有给出频率无序的直接数值比较。 | 在同一 bulk 波包任务下，用两种明确的误差预算检查该预期。 |

版本核查改变了筛选：Meier 的 2024 预印本曾将通道损耗和稳定性列作展望，但正式版已补做耦合误差和振幅阻尼。因此本轮没有把“给模型加一点噪声”当作新空白。Longhi 2009、Chen 2007 的结尾主要总结已完成工作，也没有被改写成作者未提出的研究计划。

## Demo 1　有限源高阶 caustic

**可检验问题。** 高阶点在理想几何中的较低发散，是否在有限输入尺度下转化为接收收益？

采用 Wartelle Eq.(4) 的实际偶极—交换色散及 Fig.13 的近高阶参数，直接构造等频线。普通 caustic 使用该图的 \(0.95\nu\) 对照，再加入离开 caustic 的控制。对每组沿局部切向取相同 Gaussian 角谱：

\[
u(x_\perp,z)=\frac{1}{\sqrt{2\pi}}
\int A(q_\perp)e^{i[q_\perp x_\perp+k_\parallel(q_\perp)z]}dq_\perp,
\qquad \int|A(q_\perp)|^2dq_\perp=1.
\]

初始横向 RMS 均为 \(7.12675d\)，\(d\) 为膜厚，固定接收窗为 \(|x_\perp|\le2\sigma_{\rm initial}\simeq14.2535d\)。这里固定的是标量角谱范数，不能自动称为相同实际微波输入功率。该模型检验单色波束的几何相干聚焦，不包含完整动态磁化率和真实天线。

在 \(z=10^4d\)、无损时：

| 指标 | 近高阶点 | 普通点 |
|---|---:|---:|
| 标量强度峰值 | 0.0539648 | 0.0339690 |
| 主瓣 FWHM | \(17.8013d\) | \(23.6571d\) |
| 固定接收窗积分 | 0.958566 | 0.590380 |

峰值比约 **1.589**，接收收益也存在，所以不是仅靠重新归一化得到的亮图。但两个负向控制限定了结论：

- 加入现象学时间振幅衰减 \(\Gamma/\omega_M=10^{-4}\)，近高阶与普通点的峰值比降到 **0.562**；近高阶较慢的群速度付出更多传播损耗。
- 保持源和接收轴不动，仅偏移频率 \(\pm0.5\%\)，固定接收窗积分从 **0.9586** 降到 **0.0261／0.0287**。全局峰值仍接近原值，主要问题是波束转向。

输入更宽、更窄带时，无损优势也趋小：RMS \(20.36d\) 时峰值比约 **1.014**。

**闭合结果。** 有限源增强成立，但“高阶点更亮”不是一个足够的器件目标。最值得继续的是加入磁化率、有限天线、阻尼和接收器容差后的接收信号优化。[Wagle 2026](https://arxiv.org/html/2404.15011v4) 已处理普通 caustic 的有限源、阻尼与磁化率响应，因此剩余问题是等资源下普通／高阶点的比较，而不是泛称有限幅度尚无人计算。论文数值参数应称“近高阶”，不宣称严格的高阶临界点。

核验包括等频线残差、群速度有限差分、单调出射分支、Parseval 范数及谱／空间盒收敛。横向网格减半时峰值变化约 \(0.0201\%\)，窗积分变化小于 \(5\times10^{-5}\)。较小盒出现的长距离边缘污染被识别并保留为失败记录。补充的等 normal-flux 归一化只用于敏感性分析，其中的标量窗积分可以大于 1，不能解释为透射率。

[结果图](demos/finite-source-caustic/summary.png) · [动画](demos/finite-source-caustic/demo.gif) · [详细说明](demos/finite-source-caustic/report.txt) · [数据与核验](demos/finite-source-caustic/results.json)

## Demo 2　有限空间分辨率下认证反流

**可检验问题。** 在指定探测分辨率和有限制备预算下，观察到的左侧概率增加是否仍超过经典弹道粒子的允许值？

沿用自由余弦带，取 \(a=J=\hbar=1\)，速度为 \(v(q)=\sin q\)。用 Gaussian PSF 对应的平滑左侧测量窗

\[
W_\ell(n)=\frac12\operatorname{erfc}
\left(\frac{n-m_{\rm cut}-1/2}{\sqrt2\,\ell}\right),
\]

定义
\[
B_\ell=\langle W_\ell\rangle_{t_2}
-\langle W_\ell\rangle_{t_1}-P(v<0).
\]

对无力、速度守恒、具有非负位置—波矢联合分布的经典弹道系综，\(B_\ell\le0\)。正值违反这个具体零假设；这不是声称所有经典相干波动模型都被排除，也不使用连续自由粒子的最大 backflow 常数。

首先单独诊断原来的自然 Gaussian 拖尾事件：

| PSF 标准差 | 反流见证 |
|---|---:|
| 0 | \(+3.3520\times10^{-5}\) |
| \(0.25a\) | \(+2.4366\times10^{-5}\) |
| \(0.5a\) | \(-3.1951\times10^{-5}\) |

固定原截面和时间窗时，约在 \(\ell=0.3614a\) 失去认证。这个阈值属于所选事件，不是任意态的普适极限。

另做一项同资源制备比较：固定中心 \(0.5a\)、RMS \(6a\)、归一化 1、截面 \(0\to1\)、时间 \(0\to1\)，比较单 Gaussian 与有限参数的两载波相干叠加。两载波的实际中心和 RMS 也受到约束；这个几何不同于长时自然拖尾，不能把二者差值称为等资源增益。

在 PSF \(0.5a\) 下：

| 初态 | \(B_\ell\) |
|---|---:|
| 单 Gaussian | −0.0656654 |
| 按锐利窗优化的两载波 | +0.00557010 |
| 按该分辨率优化的两载波 | +0.00562080 |
| 相同载波、权重的非相干混合 | −0.01772964 |

这给出了有限分辨率下的可认证实例，但重新按分辨率优化只提高约 **0.91%**，不支持巨大优化优势。冻结设计后，载波 \(\pm0.02\) rad、相位 \(\pm0.10\) rad 和相对幅度 \(\pm5\%\) 的单参数误差仍保留正见证。

给定已知 PSF、独立模糊后二元位置读出和独立速度符号测量，正态近似的 \(5\sigma\) 要求约 **396,417 次／组，共三组**。这不包含技术噪声或 PSF 标定误差；单位格距也还没有映射到实际成像装置。

**一个补充的测量界。** 对固定负速度，先最大化初始位置所能产生的平滑窗增量，可得到更紧的经典上界

\[
C_\ell=\int_{v<0}\rho(q)
\operatorname{erf}\!\left[
\frac{|v(q)|(t_2-t_1)}{2\sqrt2\,\ell}
\right]dq,\qquad
B_{\rm tight}=\Delta\langle W_\ell\rangle-C_\ell.
\]

这里 \(\rho(q)\) 是归一化波矢谱概率密度，\(\int_{-\pi}^{\pi}\rho(q)dq=1\)。该界允许任意位置—波矢相关性，是本轮直接推导并核验的细化，没有归于原论文，也不作新颖性主张。没有重新优化，只重评冻结态：半格点 PSF 下，原锐利窗优化态的 \(B_{\rm tight}=0.00707086\)，约需 **249,938 次／组**；原分辨率优化态为 0.00672910，约需 275,966 次／组。第三组此时需要速度分辨测量以估计相应加权函数。

**更紧判据反转了两种冻结态的排序。** 因此值得继续的不是简单增加载波搜索，而是同时明确制备资源、PSF、认证界及统计测量成本。原自然拖尾不宜作为粗分辨率检测首选；对 PSF \(1a,2a\)，这两种冻结态在本时间窗中也未获得认证。

核验包括概率增量／加权流积分一致性、另一周期截面、非相干与普通左行对照、连续 Bloch 积分和盒尺寸收敛。硬正速度投影产生长尾，不计入等 RMS 制备排名。

[结果图](demos/backflow-resolution/summary.png) · [动画](demos/backflow-resolution/demo.gif) · [数据](demos/backflow-resolution/results.json) · [更紧测量界](demos/backflow-resolution/supplemental_bound_report.txt)

## Demo 3　含损耗的受限脉冲设计

**可检验问题。** 在同一输入预算下，把波长相关损耗纳入逆设计，是否提高指定接收任务的表现？

使用明确的线性谱传递 surrogate：
\[
G(q)=A(q)e^{-\Gamma(q)T-i\varepsilon(q)T}.
\]
\(A\) 表示有限带宽的有效激发传递，\(\Gamma\) 为波矢相关振幅衰减。输入平方范数为 1，并扫描共同峰值预算；名义比较使用 0.15。这里的代价是无量纲谱范数，不是已标定的微波能量，也没有实现完整因果天线驱动。

对输出 \(y=Gu\) 和单位范数目标 \(\phi\)，分别报告
\[
F=\frac{|\langle\phi,y\rangle|^2}{\|y\|^2},
\qquad Q=|\langle\phi,y\rangle|^2.
\]
\(F\) 是归一化复场匹配，\(Q\) 保留绝对输出代价。matched filter \(u\propto G^\dagger\phi\) 是绝对目标重叠的基准；不能用归一化后的高 \(F\) 代替效率。

| 方法 | 名义 \(F\) | 名义 \(Q\) | 留出样本 \(F\ge0.95\) 比例 |
|---|---:|---:|---:|
| 忽略传播损耗 | 0.79874 | 0.07711 | 0% |
| 名义损耗补偿 | 0.95346 | 0.04592 | 55% |
| 名义模型＋同样训练选择正则参数 | 0.96749 | 0.04030 | 86.25% |
| Ensemble 设计 | 0.96878 | 0.03953 | 85% |
| Matched filter | 0.44088 | 0.12242 | 0% |

强度形状重叠仅从 **0.98336** 变为 **0.98360**。本例的主要改善在复场而非强度包络。把损耗增至四倍时，补偿仍可有 \(F\simeq0.9506\)，但 \(Q\) 只有 \(5.14\times10^{-7}\)。

公平对照也关闭了一项看似有利的结论：若仅拿固定参数的名义模型与训练过的 ensemble 比，后者显得更好；当名义模型也使用同样训练规则选择正则参数，额外优势没有建立。86.25% 与 85% 只差 2/160 个样本，不能证明显著差异或统计等价；两者都没有达到预设的 95% 留出成功率目标。

**闭合结果。** 相干接收任务可以在保真度与绝对信号之间作权衡，但本例没有给出全面性能提升。若只关心强度包络，不值得仅凭这个测试推动损耗补偿；若接收任务需要相位匹配，下一步应使用测得的传递函数、真实驱动预算和实验参数分布。

无损极限、matched-filter 上界、单调衰减、FFT 范数和网格加倍已检查。峰值预算 0.10 下测试输入族的失败保留，没有将无约束精确逆演化视为研究成果。

[结果图](demos/loss-aware-pulse/overview.png) · [动画](demos/loss-aware-pulse/demo.gif) · [说明](demos/loss-aware-pulse/report.txt) · [数据](demos/loss-aware-pulse/results.json)

## Demo 4　频率误差与耦合误差

**可检验问题。** 两种误差“同样大”时，是否造成可比较的输运损失？

采用明确的 XY／cavity bulk tight-binding 模型，固定初宽 \(6a\)、传播距离 \(160a\)、接收窗、干净平均到达时刻和 64 个配对无序实现。先按
\[
\mathbb E[\operatorname{Tr}((\delta H)^2)/N]=w^2
\]
匹配矩阵扰动预算，再匹配最低阶后向散射矩阵元方差。另检查离开带中心的载波，以及随机 Heisenberg 交换同时改变对角和跃迁项的物理对照。

在 \(k_0a=\pi/2,w=0.05J\)：

| 比较 | 平均接收概率 |
|---|---:|
| onsite 无序 | 0.671020 |
| 同 Frobenius 预算的 bond 无序 | 0.475718 |
| 同后向散射预算的 bond 无序 | 0.671105 |

初始配对差为 0.19530，95% 区间 \([0.18620,0.20441]\)。匹配后向散射后，差为 −0.000085，95% 区间 \([-0.002134,0.001964]\)。

**闭合结果。** 主要差别来自误差预算到散射强度的映射，没有支持额外的新带中心保护。这个结果不推翻作者较宽泛的“影响可比较”预期，也不证明所有指标严格相同。它适合作为后续研究的校准基准，不优先作为新的物理方向。

计算检查了 Hermiticity、干净 FFT、独立本征分解、概率守恒、盒尺寸和 Heisenberg 图 Laplacian 行和。未逐个无序样本调接收时间或重新归一化接收概率。此为 bulk 子测试，不是完整量子时钟的精度／熵验证。

[匹配散射后的对照图](demos/transport-disorder/born_matched_control.png) · [动画](demos/transport-disorder/demo.gif) · [说明](demos/transport-disorder/report.txt) · [数据](demos/transport-disorder/results.json)

## 本轮未列入优先测试的方向

- **SSH 链反流**是 Torres Arvizu 2026 明确列出的展望，但需要先统一带投影、速度符号、胞元及截面，再区分边界与拓扑效应。本轮选择先解决现有模型的测量可见性，没有把“交换强弱键”直接当作新颖方案。
- **三阶色散补偿和五阶寿命**可由较早的色散合成提案导出，例如添加第三邻居项，但一般长程色散工程已有后续工作。它可作工程基准，不因重新得到 \(\sigma^5\) 而自动成为新方向。
- **Gaussian 散射门、多激发相互作用**需要更换单磁子模型。本轮没有把单粒子 demo 当作这些问题的验证。
- **泛泛加噪声或损耗**已有大量工作；此次只保留正式论文未直接检验的具体预期，并用公平对照关闭了其主要差异。

## 复现与证据

在项目根目录分别运行：

```powershell
python research/wavepacket-prospects/demos/finite-source-caustic/run.py
python research/wavepacket-prospects/demos/backflow-resolution/run.py
python research/wavepacket-prospects/demos/backflow-resolution/supplemental_bound.py
python research/wavepacket-prospects/demos/loss-aware-pulse/run.py
python research/wavepacket-prospects/demos/transport-disorder/run.py
python research/wavepacket-prospects/build_gallery.py
```

四项测试经过独立科学审阅，检查了模型、数值、对照公平性和来源边界；已修复反流负速度积分端点、计数噪声解释及 caustic 接收窗积分的问题。动画逐帧解码，并检查代表帧。所有原研究材料和动画保持不变。

离线 HTML 已生成并校验本地资源。后台预览服务被执行策略拒绝，浏览器工具也禁止 `file:` 协议，因此本轮未完成浏览器交互实测；这不影响已经查看和逐帧校验的独立 PNG／GIF。用户可直接打开本地 HTML，或使用各项独立动画。

作者展望、正式版／预印本差异和后续文献核查保存在 [outlooks 目录](../../literature/wavepacket-prospects-2026-10/outlooks/)：

- [反流](../../literature/wavepacket-prospects-2026-10/outlooks/backflow/outlook_records.json)
- [磁学逆设计与 caustic](../../literature/wavepacket-prospects-2026-10/outlooks/magnon-design/outlook-evidence.json)
- [量子输运与时钟](../../literature/wavepacket-prospects-2026-10/outlooks/transport-clock/outlook_evidence.json)
- [离散光学及未入选提案](../../literature/wavepacket-prospects-2026-10/outlooks/discrete-optics/outlook_evidence.json)

检索包括原始论文全文、作者明确展望及后续工作；未把“本轮未找到同例”写成“此前无人研究”。四个 demo 是可复核的最小子测试，后续是否形成新贡献仍取决于真实制备、探测或器件约束下能否超出现有基线。
