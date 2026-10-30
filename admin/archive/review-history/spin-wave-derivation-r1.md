**原 toy-model 的线性化计算确实不对。**下面给出当前项目要模拟的二维铁磁自旋波模型，并从量子哈密顿量算到波包演化；铁磁交换是这里明确采用的有效模型假设，不沿用原笔记中未成立的微观推导。

取二维正方晶格、周期边界、晶格常数 \(a\)，总格点数为 \(\mathcal N\)。自旋算符无量纲，取 \(\hbar=1\)，每条最近邻键只计一次：
\[
\boxed{\hat H=-\sum_{i,\mu=x,y}J_\mu\,
\hat{\mathbf S}_i\cdot\hat{\mathbf S}_{i+a\mathbf e_\mu}
-h\sum_i\hat S_i^x,\qquad J_x,J_y>0,\quad h=g\mu_BB\geq0.}
\]
\(J_x\neq J_y\) 表示不同空间方向的交换强度不同，自旋交换仍各向同性；每格点一个自旋电子时 \(S=\tfrac12\)。沿 \(+x\) 完全极化的态是严格基态之一，其能量为
\[
E_F=-\mathcal N S^2(J_x+J_y)-\mathcal N hS.
\]
这里每条铁磁键都达到 \(\hat{\mathbf S}_i\cdot\hat{\mathbf S}_j\) 的最大本征值 \(S^2\)，Zeeman 项也达到最低能量，所以这一基态选择不依赖自旋波近似。

沿 \(x\) 轴做 Holstein–Primakoff 变换，定义 \(\hat S_i^{\pm(x)}=\hat S_i^y\pm i\hat S_i^z\)：
\[
\hat S_i^x=S-\hat n_i,\qquad
\hat S_i^{+(x)}=\sqrt{2S-\hat n_i}\,\hat b_i,\qquad
\hat S_i^{-(x)}=\hat b_i^\dagger\sqrt{2S-\hat n_i},\qquad
\hat n_i=\hat b_i^\dagger\hat b_i.
\]
在物理子空间 \(0\leq n_i\leq2S\) 上这是精确映射；随后采用低密度条件 \(\langle\hat n_i\rangle\ll2S\)，保留谐波阶：
\[
\hat S_i^{+(x)}\simeq\sqrt{2S}\hat b_i,\qquad
\hat S_i^{-(x)}\simeq\sqrt{2S}\hat b_i^\dagger,
\qquad \hat S_i^x=S-\hat n_i.
\]

把这些表达式代入一条键的交换项，保留玻色算符二次项：
\[
\begin{aligned}
\hat{\mathbf S}_i\cdot\hat{\mathbf S}_j
&=\hat S_i^x\hat S_j^x+
\frac12(\hat S_i^{+(x)}\hat S_j^{-(x)}+\hat S_i^{-(x)}\hat S_j^{+(x)})\\
&\simeq S^2-S(\hat n_i+\hat n_j)
+S(\hat b_i^\dagger\hat b_j+\hat b_j^\dagger\hat b_i).
\end{aligned}
\]
对所有键求和，得到二次哈密顿量
\[
\boxed{\begin{aligned}
\hat H_2={}&E_F+h\sum_i\hat n_i
+S\sum_{i,\mu}J_\mu
(\hat b_{i+a\mathbf e_\mu}^\dagger-\hat b_i^\dagger)
(\hat b_{i+a\mathbf e_\mu}-\hat b_i)\\
={}&E_F+[h+2S(J_x+J_y)]\sum_i\hat n_i\\
&-S\sum_{i,\mu}J_\mu
(\hat b_i^\dagger\hat b_{i+a\mathbf e_\mu}
+\hat b_{i+a\mathbf e_\mu}^\dagger\hat b_i).
\end{aligned}}
\]
每个格点在每个空间方向上连接两条键，所以 onsite 系数含 \(2S(J_x+J_y)\)。**原程序漏掉的就是这一项，它来自纵向交换 \(\hat S_i^x\hat S_j^x\) 的二次贡献。**

采用
\[
\hat b_i=\frac1{\sqrt{\mathcal N}}\sum_{\mathbf k}
e^{i\mathbf k\cdot\mathbf r_i}\hat b_{\mathbf k},
\]
其中 \(\mathbf k\) 取周期晶格允许的第一布里渊区波矢；平移一格给出
\[
\sum_i\hat b_i^\dagger\hat b_{i+a\mathbf e_\mu}
=\sum_{\mathbf k}e^{ik_\mu a}\hat b_{\mathbf k}^\dagger\hat b_{\mathbf k}.
\]
将它代入 \(\hat H_2\)，正反向跃迁相加得到
\[
\boxed{\hat H_2=E_F+\sum_{\mathbf k}\epsilon_{\mathbf k}
\hat b_{\mathbf k}^\dagger\hat b_{\mathbf k},\qquad
\epsilon_{\mathbf k}=h+2S\big[J_x(1-\cos k_xa)+J_y(1-\cos k_ya)\big].}
\]
这已经对角化，不需要 Bogoliubov 混合；本模型在谐波阶没有 \(bb+b^\dagger b^\dagger\) 项。长波极限与均匀模分别为
\[
\epsilon_{\mathbf k}=h+Sa^2(J_xk_x^2+J_yk_y^2)+O(k^4a^4),\qquad
\epsilon_{\mathbf0}=h.
\]

由 \(i\dot{\hat b}_i=[\hat b_i,\hat H_2]\)，对应的算符 EoM 为
\[
\boxed{i\dot{\hat b}_i=[h+2S(J_x+J_y)]\hat b_i
-S\sum_{\mu=x,y}J_\mu
(\hat b_{i+a\mathbf e_\mu}+\hat b_{i-a\mathbf e_\mu}).}
\]
令程序中的横向平均振幅为
\[
\psi_i=s_i^y+i s_i^z\simeq\sqrt{2S}\langle\hat b_i\rangle,
\qquad s_i^{y,z}=\langle\hat S_i^{y,z}\rangle.
\]
对算符 EoM 取期望值并分离实虚部，得到
\[
\boxed{\begin{aligned}
\dot s_i^y={}&[h+2S(J_x+J_y)]s_i^z
-S\sum_{\mu=x,y}J_\mu(s_{i+a\mathbf e_\mu}^z+s_{i-a\mathbf e_\mu}^z),\\
\dot s_i^z={}&-[h+2S(J_x+J_y)]s_i^y
+S\sum_{\mu=x,y}J_\mu(s_{i+a\mathbf e_\mu}^y+s_{i-a\mathbf e_\mu}^y).
\end{aligned}}
\]
这组 c-number 方程由二次量子理论直接闭合，不需要再对 \(\langle\hat b_i\rangle\) 的方程做平均场解耦；相互作用修正已经在舍去高阶 HP 项时被排除。

给定初始波包 \(\psi_i(0)\)，其在线性理论中的精确演化为
\[
\boxed{\psi_i(t)=\frac1{\mathcal N}\sum_{j,\mathbf k}
e^{i\mathbf k\cdot(\mathbf r_i-\mathbf r_j)-i\epsilon_{\mathbf k}t}
\psi_j(0).}
\]
实际计算就是对初态做 FFT，将每个模式乘以 \(e^{-i\epsilon_{\mathbf k}t}\)，再做逆 FFT，并取 \(s_i^y=\operatorname{Re}\psi_i\)、\(s_i^z=\operatorname{Im}\psi_i\)。当前程序的 RK4 求解的是同一方程，以上表达式提供不含时间步进误差的基准。

对于窄带波包，其中心波矢 \(\mathbf k_0\) 处的群速度是
\[
\mathbf v_g=\nabla_{\mathbf k}\epsilon_{\mathbf k}\big|_{\mathbf k_0}
=2Sa\big(J_x\sin k_{0x}a,\ J_y\sin k_{0y}a\big),
\]
包络一般会因色散曲率而展宽。以当前默认参数 \(S=\tfrac12,J_x=1,J_y=\tfrac12,h=\tfrac12,a=1\) 为例，
\[
\epsilon_{\mathbf k}=\frac12+(1-\cos k_x)+\frac12(1-\cos k_y),
\qquad \frac12\leq\epsilon_{\mathbf k}\leq\frac72.
\]
因此这组参数没有零频环，\(k=0\) 的进动频率就是 \(h=\tfrac12\)。

最后区分精确性：完全极化基态及该模型的单 magnon 色散是精确的，\(S=\tfrac12\) 也成立；有限密度波包按上述自由 magnon 方程传播，则采用了低密度近似。若把同一传播方程用于固定粒子数的单 magnon 波函数，其振幅不能再解释为 \(\langle S^y\rangle+i\langle S^z\rangle\)，因为该态的横向一阶期望值为零。
