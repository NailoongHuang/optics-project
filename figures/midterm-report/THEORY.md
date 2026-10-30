# 中期报告：怎样从色散关系理解自旋激发的传播

这套图组对应均匀二维正方晶格上的自旋 $1/2$ 最近邻铁磁模型，取 $J_x>0$、$J_y\geq0$，不加外场。理论依据是项目现有的[单磁子推导](../../Note/single_magnon_derivation/main.tex)。$J_y=0$ 只作为彼此解耦的一维链的对照极限。

## 1. 传播的是什么

把全部自旋沿 $+x$ 极化的基态记作 $|F\rangle$，只有第 $i$ 个格点翻转的基矢记作 $|i\rangle$。单翻转子空间内的一般态是

$$|\Psi(t)\rangle=\sum_i c_i(t)|i\rangle,\qquad \sum_i|c_i(t)|^2=1.$$

交换作用把一个位置上的翻转与相邻位置上的翻转耦合起来，所以局域激发会随时间变成许多位置的叠加。图中的 $P_i=|c_i|^2$ 是测量到翻转位于第 $i$ 个格点的概率。对这个量子态，沿极化轴的局域平均自旋满足

$$\langle S_i^x\rangle=\frac12-P_i.$$

固定单磁子数态的横向自旋期望为零。这些概率动画因此应按单磁子概率来讲解。经典小振幅横向磁化可以服从相同的线性传播算符，但那对应另一类初态与观测量。

## 2. 色散关系提供哪些信息

在均匀晶格上，平面波是传播算符的本征模式，其激发能为

$$\varepsilon(\mathbf k)=E_{\mathbf k}-E_F=J_x(1-\cos k_xa)+J_y(1-\cos k_ya).$$

图组统一使用无量纲变量

$$q_\mu=k_\mu a,\qquad \tau=J_xt/\hbar,\qquad \eta=J_y/J_x,$$

并以 $a$ 为位置单位、$J_x$ 为激发能单位。于是

$$\varepsilon/J_x=1-\cos q_x+\eta(1-\cos q_y).$$

它的斜率给出窄带波包的群速度。用每单位 $\tau$ 移动的格点数表示，

$$\mathbf u(\mathbf q)=\left(\sin q_x,\eta\sin q_y\right),\qquad \mathbf v_g=(J_xa/\hbar)\mathbf u.$$

所以波矢方向与传播方向一般需要分别判断。即使在长波极限，$\eta\ne1$ 时也有 $\mathbf u\simeq(q_x,\eta q_y)$，对一般斜向波矢并不平行。只有 $\eta=1$ 且足够接近原点时，色散近似为旋转对称的抛物面。等方正方晶格在较大波矢处仍然只保留晶格的离散旋转对称性。

## 3. 怎样由色散得到动画

令 $\psi_i(t)=e^{iE_Ft/\hbar}c_i(t)$，显式去除所有格点共有的基态相位。这一步保持 $|\psi_i|^2=|c_i|^2$。对初态作离散 Fourier 变换后，每个模式独立演化：

$$A(\mathbf q,\tau)=A(\mathbf q,0)\exp\{-i[1-\cos q_x+\eta(1-\cos q_y)]\tau\}.$$

对它作逆变换得到实空间振幅。这里没有时间积分步长误差；空间仍是有限周期晶格，因此需要检查边界与扩大晶格后的变化。输出动画只抽取若干时刻展示，不改变计算的时间演化规律。

## 4. 单点激发为什么会向外展开

初始仅一个格点有翻转时，波矢空间的概率权重均匀。它包含向各个方向传播、群速度不同的模式，因而自然向周围展开。无限晶格上的精确传播概率为

$$P_{m,n}(\tau)=\mathrm J_m(\tau)^2\mathrm J_n(\eta\tau)^2,$$

其中 $\mathrm J_n$ 是第一类 Bessel 函数，$m,n$ 是相对于初始翻转位置的格点坐标。这个解析式是检验 FFT 模拟的一条独立途径。以格点数为宽度单位，它给出

$$\sigma_x=\tau/\sqrt2,\qquad \sigma_y=\eta\tau/\sqrt2.$$

因此均方根宽度与时间成正比，是弹道展宽。传播图中的振荡和旁瓣来自相干叠加。主要波前之外仍有小尾部，不能把最大群速度画出的线理解为概率严格为零的边界。

## 5. Gaussian 波包把“运动”和“展宽”分开

使用归一化初态

$$\psi(n_x,n_y,0)\propto\exp\left[-\frac{n_x^2}{4\sigma_x^2}-\frac{n_y^2}{4\sigma_y^2}\right]e^{i(q_{0x}n_x+q_{0y}n_y)}.$$

这里 $n_x=x/a,n_y=y/a$ 是格点数坐标，$\sigma_x,\sigma_y$ 是同样以格点数为单位的初始概率均方根宽度；相应物理长度为 $a\sigma_x,a\sigma_y$。对于本图组中宽于数个格点的 Gaussian，离散求和与连续 Gaussian 的差异极小。改变载波只改变初态相位与波矢分布，不改变初始概率包络。零中心波矢的对称包络质心保持不动；选择非零中心波矢后，波包通常会定向移动。

有限频宽时，精确的质心速度要对整个初始频谱加权：

$$\overline{\mathbf u}=\sum_{\mathbf q}|A(\mathbf q,0)|^2\mathbf u(\mathbf q),\qquad\sum_{\mathbf q}|A|^2=1.$$

只有足够窄带时，它才近似等于 $\mathbf u(\mathbf q_0)$。对于无额外啁啾的初始 Gaussian，在边界影响可忽略时，可用速度方差理解展宽：

$$\mathrm{Var}[n_x(\tau)]=\mathrm{Var}[n_x(0)]+\tau^2\mathrm{Var}[u_x],$$

另一方向同理。更一般的初态还需保留初始位置与速度的协方差项。窄波包对应更宽的频谱，通常含有更大的速度差异；实际展宽还取决于所选中心波矢附近的色散曲率。

## 6. 结尾可以引出的下一步

在 $\mathbf q_0=(\pi/2,\pi/2)$，两个方向的二阶导数都为零，因此窄带波包的二阶展宽受到抑制。令 $e=\varepsilon/J_x$，$\mathbf u_0=\nabla_{\mathbf q}e(\mathbf q_0)$；扣除常数项和产生平移的线性项后，残余色散为

$$e(\mathbf q_0+\delta\mathbf q)-e(\mathbf q_0)-\mathbf u_0\cdot\delta\mathbf q=-\frac{\delta q_x^3+\eta\delta q_y^3}{6}+O(|\delta\mathbf q|^5),$$

故长时间仍会发生相位与轮廓变化。延伸图用于展示这一机制及其有限时间效果；更完整的关联频谱设计、自准直和误差鲁棒性可以放到后续研究计划中。

图中的复态保真度若采用 $|\langle\psi_{\rm 平移参考}|\psi(\tau)\rangle|^2$，会同时检测幅度和相位变化；它与只比较概率轮廓的重合指标不同。判断保形应联合观察质心、宽度、完整轮廓与尾部。
