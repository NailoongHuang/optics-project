**结论是：一维并非一概不可能，但有一个很强的充要条件；二维最简单的二次色散下则不可能。**

这里把“局域波包”明确为平方可积、均方宽度有限。在这个意义下：

- **一维：存在非零的严格保形波包，当且仅当色散关系在某个非零宽度的波数区间内严格为直线。** 要求波包移动时，这条直线的斜率还必须非零。
- **二维：对于 \(\omega(\mathbf k)=\omega_0+D|\mathbf k|^2\)、\(D>0\)，不存在这样的波包。**

下面给出证明，也检查“只要求强度轮廓不变”的较弱定义。

**一、先固定问题的定义**

考虑无限连续空间中的一个标量自旋波分支，无驱动、无阻尼、无非线性。它按照给定的实色散关系演化：

\[
\psi(\mathbf r,t)=\frac{1}{(2\pi)^{d/2}}
\int_{\mathbb R^d} A(\mathbf k)
e^{i\mathbf k\cdot\mathbf r-i\omega(\mathbf k)t}\,d^dk,
\qquad d=1,2.
\tag{1}
\]

\(A\) 是初始波形的傅里叶变换；一般平方可积初态的积分按 \(L^2\) 意义理解。假设 \(\omega\) 为实值 \(C^1\) 函数，即连续可微；后面的二维例子是更简单的多项式。

局域条件取为

\[
0<\int |\psi(\mathbf r,0)|^2\,d^dr<\infty,
\qquad
\int |\mathbf r|^2|\psi(\mathbf r,0)|^2\,d^dr<\infty.
\tag{2}
\]

第一个条件是有限总强度，第二个条件是有限均方宽度。Gaussian 波包以及光滑有限带宽频谱构造出的波包都符合。这里不把无限平面波或只有中心峰局域、尾部总强度发散的理想解称为局域波包。

先采用完整复波形的严格保形定义：存在常数速度 \(\mathbf v\) 和实常数 \(\Omega\)，使

\[
\boxed{\psi(\mathbf r,t)=e^{-i\Omega t}\psi(\mathbf r-\mathbf vt,0)}
\quad\text{对所有 }t\text{ 成立。}
\tag{3}
\]

它允许整体平移和统一相位转动。若 \(\mathbf v=0\)，这是静止保形；如果课题要求传播，就另要求 \(\mathbf v\ne0\)。

**二、严格保形的频谱判据**

对式 (3) 的两边做空间傅里叶变换。由式 (1)，左边是 \(A(\mathbf k)e^{-i\omega(\mathbf k)t}\)；右边的平移产生因子 \(e^{-i\mathbf k\cdot\mathbf vt}\)，所以

\[
A(\mathbf k)e^{-i\omega(\mathbf k)t}
=A(\mathbf k)e^{-i(\Omega+\mathbf v\cdot\mathbf k)t}.
\tag{4}
\]

因此，在 \(A(\mathbf k)\ne0\) 的地方，必须有

\[
\boxed{\omega(\mathbf k)=\Omega+\mathbf v\cdot\mathbf k}
\quad\text{几乎处处成立。}
\tag{5}
\]

原因是式 (4) 对所有时间成立，两个指数中的频率只能相等，而不是仅在某个时刻相差整数个 \(2\pi\)。严格处理“几乎处处”时，先对可数列 \(t_n=1/n\) 取公共满测集。在这个集合内，若某个波数的频差 \(\Delta=\omega-\Omega-\mathbf v\cdot\mathbf k\ne0\)，则充分大的 \(n\) 使 \(0<|\Delta|/n<2\pi\)，不可能满足 \(e^{-i\Delta/n}=1\)，故必须 \(\Delta=0\)。反过来，把式 (5) 代回式 (1)，立即得到式 (3)，所以这是充要判据。“几乎处处”表示可以忽略零测集，它们不改变普通 \(L^2\) 傅里叶积分。

对给定的 \(\mathbf v,\Omega\)，记

\[
E_{\mathbf v,\Omega}
=\{\mathbf k:\omega(\mathbf k)-\mathbf v\cdot\mathbf k=\Omega\}.
\tag{6}
\]

**如果暂时只要求平方可积，存在非零保形解，当且仅当这个集合具有正的 \(d\) 维测度。** 必要性来自：普通 \(L^2\) 函数若只在零测集上非零，其范数就是零。充分性也直接：取一个正测度、有限测度的可测子集 \(F\subset E_{\mathbf v,\Omega}\)，令 \(A\) 在 \(F\) 内等于 1、外部等于 0，即得到非零平方可积频谱。这里的集合可测性由 \(\omega\) 的连续性保证。这一步保证有限总强度，尚未保证有限均方宽度。

**三、一维一般情形：严格直线频带是充要条件**

先证明必要性。有限总强度和有限均方宽度给出

\[
\int_{\mathbb R}|\psi(x,0)|\,dx
\le
\left[\int(1+x^2)|\psi(x,0)|^2dx\right]^{1/2}
\left[\int\frac{dx}{1+x^2}\right]^{1/2}
<\infty.
\tag{7}
\]

这里使用 Cauchy–Schwarz 不等式。因此初态不仅平方可积，也绝对可积，它的傅里叶变换 \(A(k)\) 是连续函数。这个连续性可以直接由傅里叶积分中的控制收敛得到。

由于波包不为零，存在 \(k_*\) 使 \(A(k_*)\ne0\)。连续性保证在 \(k_*\) 附近的某个开区间 \(I\) 上，\(A(k)\) 始终不为零。于是式 (5) 要求

\[
\boxed{\omega(k)=\Omega+vk,\qquad k\in I.}
\tag{8}
\]

式 (5) 原本是几乎处处相等，但 \(\omega(k)-\Omega-vk\) 连续，因此在这个区间上处处相等。这就证明：**真正有限宽度的波包必须占据一段频谱，而不是只有几个波数；在这段频谱上，色散必须完全是一条直线。**

再证明充分性。若某个开区间 \(I\) 内确实满足式 (8)，选任意非零、光滑、紧支撑且支撑位于 \(I\) 内的 \(A(k)\)。紧支撑表示频谱在某个有限区间之外为零。则

\[
\begin{aligned}
\psi(x,t)
&=\frac{1}{\sqrt{2\pi}}\int_I A(k)e^{ikx-i(\Omega+vk)t}\,dk\\
&=e^{-i\Omega t}\frac{1}{\sqrt{2\pi}}
\int_I A(k)e^{ik(x-vt)}\,dk\\
&=e^{-i\Omega t}\psi(x-vt,0).
\end{aligned}
\tag{9}
\]

而且，\(A\) 非零且平方可积，Plancherel 定理保证初态的总强度有限且非零。对这个傅里叶积分反复分部积分可知，\(\psi(x,0)\) 比任意幂次 \(|x|^{-n}\) 都衰减得快，所以均方宽度也有限，满足式 (2)。必要性和充分性都成立。

这个结论不需要假设 \(\omega\) 是抛物线，也不需要排查奇怪函数：只要采用上述有限宽度的局域条件，就已经得到一维的一般判定。

如果进一步采用物理模型中常见的**实解析色散**——在每一点附近都等于其收敛 Taylor 展开——则结论更强：若 \(\omega\) 的解析定义域是一个连通开区间，只要它在其中某个开区间等于 \(\Omega+vk\)，实解析函数的唯一性定理就要求它在整个定义域都等于这条直线。因此，一条实解析但非仿射的色散分支，不允许这样的严格保形局域波包。

例如，\(\omega(k)=\omega_0+Dk^2\)、\(D>0\)，不含任何直线区间，所以不可能。仅凭某一点满足 \(\omega''(k_*)=0\)，或某个窄频带内近似直线，不能推出严格保形；需要检查实际使用的频带是否完全是直线。若模型确实含有这样的频带，式 (9) 就给出一整族保形波包，而不是只有平面波。

**四、二维代表：普通二次色散下不存在局域保形波包**

取长波交换型自旋波最简单的模型

\[
\boxed{\omega(k_x,k_y)=\omega_0+D(k_x^2+k_y^2),\qquad D>0.}
\tag{10}
\]

把它代入严格保形条件 (5)：

\[
\omega_0+D(k_x^2+k_y^2)=\Omega+v_xk_x+v_yk_y.
\]

配方得到

\[
\boxed{
\left(k_x-\frac{v_x}{2D}\right)^2+
\left(k_y-\frac{v_y}{2D}\right)^2
=\frac{\Omega-\omega_0}{D}+\frac{v_x^2+v_y^2}{4D^2}.
}
\tag{11}
\]

右边为正、零、负时，允许的频谱分别是一条圆周、一个点或空集。三者在二维波数平面里的面积都为零。

因此，普通平方可积的 \(A(k_x,k_y)\) 如果只能放在这些集合上，就只能是零函数。得到

\[
\boxed{\text{二维二次色散不允许非零、平方可积的严格刚性平移波包。}}
\tag{12}
\]

这里甚至不需要有限均方宽度，有限总强度已经足够。各向异性的正二次色散 \(\omega=\omega_0+D_xk_x^2+D_yk_y^2\)、\(D_x,D_y>0\) 也一样：配方后圆周变成椭圆周，仍是零面积集合。

**五、如果只要求强度不变，允许内部相位改变呢？**

现在放宽要求，只要求

\[
|\psi(\mathbf r,t)|^2=|\psi(\mathbf r-\mathbf vt,0)|^2.
\tag{13}
\]

对有限均方宽度的波包，前面的一维存在性结论与二维不存在性结论仍成立。下面证明这一点，而不是把完整复波形的结论直接套给强度。

把总强度归一化为 1，并记群速度 \(\mathbf V(\mathbf k)=\nabla_{\mathbf k}\omega(\mathbf k)\)。位置乘法在傅里叶空间对应 \(i\nabla_{\mathbf k}\)，对演化后的频谱求导得到

\[
i\nabla_{\mathbf k}\left[Ae^{-i\omega t}\right]
=e^{-i\omega t}\left(i\nabla_{\mathbf k}A+t\mathbf V A\right).
\tag{14}
\]

这些求导按弱导数理解。有限初始宽度意味着 \(\nabla A\in L^2\)；若式 (13) 成立，任意非零时刻的宽度也有限，意味着 \(\nabla(Ae^{-i\omega t})\in L^2\)。将这两点代入式 (14)，得到 \(\mathbf V A\in L^2\)，因而下面使用的速度均值和二阶矩有限。

定义中心 \(\bar{\mathbf r}(t)=\int\mathbf r|\psi(\mathbf r,t)|^2d^dr\)，初始中心为 \(\bar{\mathbf r}_0\)，谱平均速度为
\(\bar{\mathbf V}=\int\mathbf V|A|^2d^dk\)。由式 (14) 和 Plancherel 定理，中心满足 \(\bar{\mathbf r}(t)=\bar{\mathbf r}_0+t\bar{\mathbf V}\)，绕中心的均方宽度满足

\[
\begin{aligned}
W^2(t)
&=\int|\mathbf r-\bar{\mathbf r}(t)|^2|\psi(\mathbf r,t)|^2d^dr\\
&=\int\left|
i\nabla A-\bar{\mathbf r}_0A
+t(\mathbf V-\bar{\mathbf V})A
\right|^2d^dk\\
&=W^2(0)+2Ct
+t^2\underbrace{\int|\mathbf V-\bar{\mathbf V}|^2|A|^2d^dk}_{\displaystyle\operatorname{Var}_A(\mathbf V)}.
\end{aligned}
\tag{15}
\]

其中 \(C\) 来自展开平方后的交叉项：
\(C=\operatorname{Re}\int(i\nabla A-\bar{\mathbf r}_0A)^*\cdot(\mathbf V-\bar{\mathbf V})A\,d^dk\)。它依赖初始相位与位置—速度关联，但不随时间变化。这里的“速度方差”就是不同频谱成分的群速度偏离平均值的加权平方。

如果形状严格不变，\(W^2(t)\) 就必须恒定。式 (15) 是关于时间的二次多项式，因此其二次项必须为零：

\[
\boxed{\operatorname{Var}_A(\mathbf V)=0.}
\tag{16}
\]

一维时，这要求 \(\omega'(k)=\bar V\) 在 \(A(k)\ne0\) 的地方几乎处处成立。利用第三部分已经证明的 \(A\) 的连续性，必有一个开区间使 \(\omega'\) 恒定；积分后仍得到 \(\omega(k)=\Omega+vk\)。式 (13) 的中心移动速度就是 \(v=\bar V\)。反向构造仍由式 (9) 给出，所以**即使只要求强度保形，一维的存在性充要条件仍然是存在严格直线频带**。

二维二次色散时，\(\mathbf V=2D\mathbf k\)，故

\[
\operatorname{Var}_A(\mathbf V)
=4D^2\int|\mathbf k-\bar{\mathbf k}|^2|A(\mathbf k)|^2d^2k>0.
\tag{17}
\]

严格大于零的原因是：若它为零，\(A\) 只能集中在单个点 \(\mathbf k=\bar{\mathbf k}\)，这与非零、平方可积矛盾。因此有限宽度的二维波包连强度轮廓都不能严格保持。改变初始相位可以调整式 (15) 的一次项，让波包先收缩再展开，却不能消掉正的二次项；这个结论也排除了在任何非零时间区间内完全保形。

**六、为什么“在圆周上选谱”看起来又能构造保形解？**

式 (11) 确实允许一种形式构造：用 Dirac \(\delta\) 分布把频谱压在圆周上。取圆周上均匀的角向权重，逆变换会得到 Bessel 型轮廓。

但是，这种频谱不是普通 \(L^2\) 函数。设圆周半径为 \(q>0\)，对应轮廓的模正比于 \(|J_0(qr)|\)。利用 Bessel 函数的标准大参数渐近式，

\[
J_0(qr)=\sqrt{\frac{2}{\pi qr}}\cos\left(qr-\frac\pi4\right)
+O(r^{-3/2}),
\]

可得 \(r|J_0(qr)|^2\) 的主项是不随距离衰减的 \(2\cos^2(qr-\pi/4)/(\pi q)\)。因此二维总强度

\[
2\pi\int_0^\infty r|J_0(qr)|^2dr=\infty.
\]

它虽有一个明显中心峰，却带有总强度发散的无限尾部，不满足式 (2)。把圆周加厚，或在实空间截断尾部，才可得到有限总强度，但也会失去严格保形条件。

这正是我前面说明需要补全的一点：**色散曲面与平面相交，给出了形式上的选谱条件；它本身并不保证得到一个有限总强度的局域波包。**

对你规定的范围，现在可以明确判定：**一维一般色散，检查有没有严格直线频带；二维普通二次色散，严格局域保形不成立。**
