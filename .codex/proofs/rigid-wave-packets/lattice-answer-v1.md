**对于最常见的二维最近邻晶格，答案是不可以。更一般地，非恒定、由有限个 \(\sin\)、\(\cos\) 项组成的周期色散，也不允许真正局域的波包持续严格保形。** 下面的结论针对无限、均匀、没有驱动和阻尼的标量线性晶格。

先把模型和条件固定下来。令晶格间距为 1，格点位置为 \(\mathbf n=(n_x,n_y)\in\mathbb Z^2\)，每个格点上的小振动用一个复振幅 \(\psi_{\mathbf n}(t)\) 描述。最简单的最近邻模型是

\[
i\dot\psi_{\mathbf n}
=h\psi_{\mathbf n}
+J_x(2\psi_{\mathbf n}-\psi_{\mathbf n+\mathbf e_x}-\psi_{\mathbf n-\mathbf e_x})
+J_y(2\psi_{\mathbf n}-\psi_{\mathbf n+\mathbf e_y}-\psi_{\mathbf n-\mathbf e_y}),
\quad h\in\mathbb R,\quad J_x,J_y>0.
\tag{1}
\]

\(\mathbf e_x,\mathbf e_y\) 分别表示沿两个方向移动一个格点，\(J_x,J_y\) 已吸收自旋长度等常数。把平面波 \(e^{i\mathbf k\cdot\mathbf n-i\omega t}\) 代进去，得到你说的周期色散：

\[
\boxed{
\omega(k_x,k_y)=h+2J_x(1-\cos k_x)+2J_y(1-\cos k_y).
}
\tag{2}
\]

波数只需取一个布里渊区 \(B=[-\pi,\pi)^2\)，相对的边界表示同一个波数。

沿用之前对局域的要求：总强度非零且有限，均方宽度有限。把总强度归一化后，条件是

\[
\sum_{\mathbf n}|\psi_{\mathbf n}(0)|^2=1,
\qquad
\sum_{\mathbf n}|\mathbf n|^2|\psi_{\mathbf n}(0)|^2<\infty.
\tag{3}
\]

**晶格上的一个细节：位置是离散的。** 为避免对“半个格点的平移”作额外定义，我们甚至只要求：每隔一个时间 \(T>0\)，强度分布原样平移一个整数格矢 \(\boldsymbol\ell\)，而且能一直这样重复：

\[
|\psi_{\mathbf n}(mT)|^2
=|\psi_{\mathbf n-m\boldsymbol\ell}(0)|^2,
\qquad m=0,1,2,\ldots.
\tag{4}
\]

中间时刻暂时不要求保形，内部相位也不要求保持。下面会证明：**连这个条件都无法满足。持续保持均方宽度的波包也不存在。**

**证明的核心：宽度随时间必然含有一个正的二次项。**

晶格上的傅里叶演化为

\[
\psi_{\mathbf n}(t)=
\int_B A(\mathbf k)e^{i\mathbf k\cdot\mathbf n-i\omega(\mathbf k)t}
\frac{d^2k}{(2\pi)^2},
\qquad
\int_B|A|^2\frac{d^2k}{(2\pi)^2}=1.
\tag{5}
\]

定义群速度 \(\mathbf V(\mathbf k)=\nabla_{\mathbf k}\omega\)。对于式 (2)，

\[
\boxed{\mathbf V(\mathbf k)=(2J_x\sin k_x,\;2J_y\sin k_y).}
\tag{6}
\]

令 \(\bar{\mathbf n}(t)=\sum_{\mathbf n}\mathbf n|\psi_{\mathbf n}(t)|^2\) 为波包中心，\(\bar{\mathbf V}=\int_B\mathbf V|A|^2d^2k/(2\pi)^2\) 为平均群速度。位置乘法在傅里叶空间对应 \(i\nabla_{\mathbf k}\)，因此

\[
i\nabla_{\mathbf k}(Ae^{-i\omega t})
=e^{-i\omega t}(i\nabla_{\mathbf k}A+t\mathbf V A).
\tag{7}
\]

有限初始均方宽度保证 \(\nabla A\) 平方可积；周期光滑色散的 \(\mathbf V\) 有界，所以这里的速度矩也有限。由式 (7)，中心为 \(\bar{\mathbf n}(t)=\bar{\mathbf n}(0)+t\bar{\mathbf V}\)。再用 Parseval 恒等式计算绕中心的均方宽度：

\[
\begin{aligned}
W^2(t)
&=\sum_{\mathbf n}|\mathbf n-\bar{\mathbf n}(t)|^2|\psi_{\mathbf n}(t)|^2\\
&=\int_B\left|i\nabla A-\bar{\mathbf n}(0)A
+t(\mathbf V-\bar{\mathbf V})A\right|^2\frac{d^2k}{(2\pi)^2}\\
&=W^2(0)+2Ct+t^2\underbrace{
\int_B|\mathbf V-\bar{\mathbf V}|^2|A|^2\frac{d^2k}{(2\pi)^2}
}_{\displaystyle\operatorname{Var}_A(\mathbf V)}.
\end{aligned}
\tag{8}
\]

\(2C\) 是展开平方后交叉项的系数，可以受初始相位影响。最后的系数是各频谱成分的群速度方差，始终非负。这是精确恒等式，没有做窄带近似。

如果波包持续保形，宽度必须恒定，因此这个二次项必须为零。即使只要求式 (4)，\(W^2(mT)\) 也必须始终相同；一个二次多项式在这些时刻取同一个值，同样要求

\[
\operatorname{Var}_A(\mathbf V)=0.
\tag{9}
\]

方差为零意味着：**波包实际使用的所有波数，必须具有同一个群速度。** 将式 (6) 代入，就是

\[
\sin k_x=\frac{\bar V_x}{2J_x},
\qquad
\sin k_y=\frac{\bar V_y}{2J_y},
\quad\text{在 }A(\mathbf k)\ne0\text{ 的地方几乎处处成立。}
\tag{10}
\]

但在一个周期内，\(\sin k=c\) 最多只有两个解。因此同时满足这两个条件的 \((k_x,k_y)\)，在布里渊区里最多只有四个点。

这就产生矛盾：\(A\) 是一个平方可积函数，如果它只能在有限几个点上非零，其二维积分必然为零，不可能满足式 (5) 的归一化条件。用 Dirac \(\delta\) 强行集中在点上，得到的是无限延伸的平面波叠加，违反式 (3) 的局域条件。

所以，任何满足式 (3) 的非零波包都有

\[
\boxed{\operatorname{Var}_A(\mathbf V)>0,}
\]

其宽度不可能保持不变。初始相位可以让它先收缩、再展开，却不能取消这个正的二次项。**最近邻二维 \(\cos\) 晶格的严格保形局域波包因此不存在。**

**如果加入更多 \(\sin\)、\(\cos\) 项，结论也可以推广。**

设 \(\omega(k_x,k_y)\) 是任意实值、非恒定的有限三角多项式，例如还包含 \(\cos(k_x+k_y)\)、\(\cos 2k_x\)、\(\sin k_y\) 等。它是周期的实解析函数。

仍然从式 (8) 出发。保形要求 \(\nabla\omega=\bar{\mathbf V}\) 在 \(A\ne0\) 的集合上成立，而非零平方可积频谱的非零集合必有正面积。此处使用一个标准实解析函数定理：**在连通开域中，不恒为零的实解析函数，其零点集的面积为零。**

将定理分别用于 \(\partial_{k_x}\omega-\bar V_x\) 和 \(\partial_{k_y}\omega-\bar V_y\)，得到两者必须处处为零。因此

\[
\omega(\mathbf k)=\Omega+\bar{\mathbf V}\cdot\mathbf k.
\tag{11}
\]

然而 \(\omega\) 在两个波数方向都是 \(2\pi\) 周期的，式 (11) 只能在 \(\bar V_x=\bar V_y=0\) 时具有这种周期性，于是 \(\omega\) 必须是常数，与假设矛盾。

因此，**在这些条件下，任何非恒定的有限 \(\sin/\cos\) 组合色散都不行；更一般的非恒定实解析周期色散也不行。** 若色散完全为常数，确实可以保持任意初始形状，但它只作统一相位振动，不会向前传播。

两个边界需要保留：这里证明的是**无限晶格**；有限周期网格可能在特殊时刻出现复现，不能直接用本证明否定。并且，证明排除的是持续保形或反复按固定步长保形，**没有排除强度轮廓只在两个时刻偶然相同**。
