**可以。现在明确选择：初始只有一个格点的自旋翻转，随后研究这个激发的传播。**单个格点只是初态的空间分布；它并不意味着后来的态仍局限在一个格点。至于是否称为波包，可以由它包含哪些平面波直接判断。

沿用已认可的无外场模型，考虑自旋 \(1/2\) 的二维正方晶格，取 \(\hbar=1\)：
\[
H=-J_x\sum_{\langle ij\rangle_x}\mathbf S_i\cdot\mathbf S_j
-J_y\sum_{\langle ij\rangle_y}\mathbf S_i\cdot\mathbf S_j,
\qquad J_x,J_y>0.
\]
每条键只计一次，采用周期边界，格点总数为 \(\mathcal N\)，晶格常数为 \(a\)。把全极化方向记为 \(+x\)，从而继续用 \(\langle S_i^x(t)\rangle\) 表示要展示的物理量。全向上态的精确能量是
\[
E_F=-\frac{\mathcal N}{4}(J_x+J_y).
\]
\(|i\rangle\) 表示仅格点 \(i\) 的自旋沿 \(-x\)，其余都沿 \(+x\)。将初始翻转所在的格点记为 \(i_0\)，初态为
\[
|\Psi(0)\rangle=|i_0\rangle.
\]
你已经认可 \(H\) 作用在 \(|i\rangle\) 上只会得到这类态的线性组合，所以演化始终留在单翻转子空间。于是可以写
\[
|\Psi(t)\rangle=\sum_i c_i(t)|i\rangle,
\qquad c_i(0)=\delta_{i,i_0},\qquad \sum_i|c_i(t)|^2=1.
\]
这里 \(c_i(t)\) 是翻转位于格点 \(i\) 的概率振幅，\(\delta_{i,i_0}\) 在 \(i=i_0\) 时为 \(1\)，其余为 \(0\)。

保留原来的能量零点，不另作相位变换。你认可的式子加回 \(E_F|i\rangle\) 后是
\[
H|i\rangle=E_F|i\rangle
+\frac12\sum_{j\text{ 邻接 }i}J_{ij}\bigl(|i\rangle-|j\rangle\bigr).
\]
将 \(|\Psi(t)\rangle\) 代入 \(i\partial_t|\Psi\rangle=H|\Psi\rangle\)，并把右边求和指标重新排列，使各项都乘在 \(|i\rangle\) 上，得到
\[
\sum_i i\dot c_i|i\rangle
=\sum_i\left[E_Fc_i
+\frac12\sum_{j\text{ 邻接 }i}J_{ij}(c_i-c_j)\right]|i\rangle.
\]
比较相同基矢的系数，并写出正方晶格的四个邻居：
\[
\boxed{\begin{aligned}
i\dot c_i={}&(E_F+J_x+J_y)c_i\\
&-\frac{J_x}{2}(c_{i+\mathbf e_x}+c_{i-\mathbf e_x})
-\frac{J_y}{2}(c_{i+\mathbf e_y}+c_{i-\mathbf e_y}).
\end{aligned}}
\]
\(i\pm\mathbf e_x\) 表示沿水平方向移动一个格点，\(i\pm\mathbf e_y\) 表示沿竖直方向移动一个格点。这就是所选单翻转问题的运动方程；在这个子空间中它是精确的。

由于交换强度不依赖格点位置，运动方程在均匀晶格上具有平移不变性。为了找出传播模式，我们使用平移算符的本征模式，即平面波，代入检验：
\[
c_i(t)=\frac1{\sqrt{\mathcal N}}
e^{i\mathbf k\cdot\mathbf r_i-iE_{\mathbf k}t}.
\]
\(\mathbf r_i\) 是格点位置，\(\mathbf k=(k_x,k_y)\) 是波矢，\(E_{\mathbf k}\) 是这个模式的总能量，包括 \(E_F\)。空间平移一个格点给出
\[
c_{i\pm\mathbf e_x}=e^{\pm ik_xa}c_i,
\qquad c_{i\pm\mathbf e_y}=e^{\pm ik_ya}c_i,
\qquad i\dot c_i=E_{\mathbf k}c_i.
\]
代入运动方程，得到
\[
\begin{aligned}
E_{\mathbf k}
&=E_F+J_x+J_y
-\frac{J_x}{2}(e^{ik_xa}+e^{-ik_xa})
-\frac{J_y}{2}(e^{ik_ya}+e^{-ik_ya})\\
&=E_F+J_x(1-\cos k_xa)+J_y(1-\cos k_ya).
\end{aligned}
\]
因此，相对全极化基态的激发能为
\[
\boxed{E_{\mathbf k}-E_F
=J_x(1-\cos k_xa)+J_y(1-\cos k_ya).}
\]
这就是当前自旋 \(1/2\)、无外场模型的单磁子色散。每个这样的平面波模式都遍布晶格；它本身不局域在某一个点。

现在回到你指定的单格点初态。周期晶格的离散傅里叶恒等式给出
\[
\delta_{i,i_0}
=\frac1{\mathcal N}\sum_{\mathbf k}
e^{i\mathbf k\cdot(\mathbf r_i-\mathbf r_{i_0})},
\]
其中求和遍历周期晶格允许的全部 \(\mathcal N\) 个波矢。这说明：**单格点局域态是全部波矢模式的等模长叠加。**在 \(t=0\)，它们在初始格点以外相消；随后每个模式分别积累自己的时间相位 \(e^{-iE_{\mathbf k}t}\)，于是
\[
\boxed{c_i(t)=\frac1{\mathcal N}\sum_{\mathbf k}
e^{i\mathbf k\cdot(\mathbf r_i-\mathbf r_{i_0})-iE_{\mathbf k}t}.}
\]
由于这条色散并非常数，各模式之间的相对相位随时间改变，原来使其他格点振幅为零的相消关系不再保持，翻转的振幅就分布到其他格点。

最终展示的物理量仍然是纵向自旋期望值。只有 \(|i\rangle\) 这一项在格点 \(i\) 向下，其余 \(|j\rangle\)、\(j\ne i\)，在该格点都向上，所以
\[
\begin{aligned}
\langle S_i^x(t)\rangle
&=-\frac12|c_i(t)|^2+\frac12\sum_{j\ne i}|c_j(t)|^2\\
&=\boxed{\frac12-|c_i(t)|^2.}
\end{aligned}
\]
初始图像是 \(1/2\) 的均匀背景上，有一个格点降到 \(-1/2\)；随后这个局域磁化缺口展开成时空分布。总自旋减少量始终满足
\[
\sum_i\left[\frac12-\langle S_i^x(t)\rangle\right]=1.
\]

**这个初态可以称为单格点局域的单磁子波包，但它是宽带波包：包含整个布里渊区，没有集中的中心波矢。**它不同于具有宽广实空间包络、波矢集中在某个 \(\mathbf k_0\) 附近的窄带波包。这里也就不应该拿某一个 \(\mathbf k_0\) 的群速度代表整个激发；空间图样来自上面所有模式的叠加。在对称的晶格中，点激发会向多个方向展开，而不是自动形成单向移动、形状不变的一团。

文献中确实把这一过程作为自旋激发的波包传播来研究；Wrzosek 等人的 §III 定义局域单翻转制备和磁化测量，§IV 解释整个布里渊区的模式如何塑造传播前沿。[Phys. Rev. B 102, 024440（2020）](https://arxiv.org/pdf/2002.00812)
