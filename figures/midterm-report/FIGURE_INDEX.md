# 逐图索引

完整浏览请打开 [离线图库](index.html) 或 [PDF 图册](midterm-figure-atlas.pdf)。

## A · 模型、色散与群速度

### a01-lattice · 交换晶格与单翻转基底

**用途：** 25个格点的局部示意中，蓝色实线是横向交换键，橙色虚线是纵向交换键。背景自旋沿+x极化，中心沿-x的箭头代表单翻转基底|0,0>；时间演化后态为这些基底的量子叠加，P_mn=|c_mn|²是测得翻转位于该点的概率。图中箭头示意量子化轴上的取向，不把固定单磁子态的系数解释为经典横向磁矩。eta描述空间方向的交换各向异性。

[PNG](a-dispersion/a01-lattice.png) · [SVG](a-dispersion/a01-lattice.svg) · [PDF](a-dispersion/a01-lattice.pdf)

### a02-isotropic-surface · 各向同性交换的色散曲面

**用途：** 在第一布里渊区内绘出eta=1的精确余弦色散。原点能量为零，最大能量为2(1+eta)=4。高度与统一的0至4色标都表示epsilon/Jx。曲面在原点附近近似抛物面；eta<1时沿qy方向起伏较小。三维透视用于概览，方向比较应结合A04的共同坐标截面。

[PNG](a-dispersion/a02-isotropic-surface.png) · [SVG](a-dispersion/a02-isotropic-surface.svg) · [PDF](a-dispersion/a02-isotropic-surface.pdf)

### a03-anisotropic-surface · 各向异性交换改变曲面起伏

**用途：** 在第一布里渊区内绘出eta=0.35的精确余弦色散。原点能量为零，最大能量为2(1+eta)=2.7。高度与统一的0至4色标都表示epsilon/Jx。曲面在原点附近近似抛物面；eta<1时沿qy方向起伏较小。三维透视用于概览，方向比较应结合A04的共同坐标截面。

[PNG](a-dispersion/a03-anisotropic-surface.png) · [SVG](a-dispersion/a03-anisotropic-surface.svg) · [PDF](a-dispersion/a03-anisotropic-surface.pdf)

### a04-axial-cuts · 方向色散截面

**用途：** 左图eta=1时沿x和y的截面完全重合（虚线覆盖实线），右图eta=0.35时y方向带宽降为0.7，而x方向带宽仍为2。每条曲线都固定另一分量为零，不能把两条轴向截面当成一般斜向传播的完整色散。

[PNG](a-dispersion/a04-axial-cuts.png) · [SVG](a-dispersion/a04-axial-cuts.svg) · [PDF](a-dispersion/a04-axial-cuts.pdf)

### a05-equal-frequency · 等频曲线

**用途：** 曲线数字是e=epsilon/Jx，依次为0.2、0.6、1.2、2、2.5。小波矢附近，eta=1的等频线近圆，eta=0.35时沿qy方向拉长；高波矢处方格晶格的结构清楚可见。等频线仅约束频率，群速度还取决于曲面的梯度，不能据此宣称局域波包保形。

[PNG](a-dispersion/a05-equal-frequency.png) · [SVG](a-dispersion/a05-equal-frequency.svg) · [PDF](a-dispersion/a05-equal-frequency.pdf)

### a06-group-velocity-field · 群速度场与等频线法向

**用途：** 灰线为等能曲线，蓝箭头为u=(sin qx,eta sin qy)，长度按统一比例绘制而未逐点归一化。梯度垂直于等能曲线，并指向能量上升方向。eta=0.35时箭头的y分量减小。该群速度描述窄频谱波包的主导运动；局域翻转包含整个能带，不能用单一箭头概括。

[PNG](a-dispersion/a06-group-velocity-field.png) · [SVG](a-dispersion/a06-group-velocity-field.svg) · [PDF](a-dispersion/a06-group-velocity-field.pdf)

### a07-slope-and-speed · 色散斜率与群速度

**用途：** 左侧三个彩色点及切线位于qx=-pi/2、0、pi/2；右侧对应点分别给出ux=-1、0、1。原点和布里渊区边界处斜率为零，能量最高并不意味着群速度最大。波包具有有限频谱宽度时，质心速度是其频谱加权平均，中心波矢处的速度是窄带近似。

[PNG](a-dispersion/a07-slope-and-speed.png) · [SVG](a-dispersion/a07-slope-and-speed.svg) · [PDF](a-dispersion/a07-slope-and-speed.pdf)

### a08-long-wave-approximation · 长波二次近似

**用途：** 两图绘出同一函数的不同范围；左图q<=0.7，右图覆盖0至pi。由cos q=1-q²/2+O(q⁴)得到二次色散。近似只适合小波矢，不能把其无界抛物线及线性增长的群速度延伸到整个晶格能带。

[PNG](a-dispersion/a08-long-wave-approximation.png) · [SVG](a-dispersion/a08-long-wave-approximation.svg) · [PDF](a-dispersion/a08-long-wave-approximation.pdf)

### a09-long-wave-error · 长波近似的定量误差

**用途：** 纵轴是轴向能量的相对高估量；曲线在q=0取连续极限0，插图放大小误差区。1%与5%的示例门槛分别对应q约0.345和0.763。门槛仅刻画该轴向能量近似，不等同于波包传播保真度；相位误差还会随时间累积。

[PNG](a-dispersion/a09-long-wave-error.png) · [SVG](a-dispersion/a09-long-wave-error.svg) · [PDF](a-dispersion/a09-long-wave-error.pdf)

### a10-wavevector-velocity-direction · 波矢与群速度的方向差

**用途：** 橙色虚线箭头指波矢方向，蓝色实线箭头指群速度方向；两者都单位化，箭长不表示速度大小。选择q0=(0.35pi,0.15pi)，eta=1时仍有有限角差，反映方格晶格而非连续各向同性介质的色散；eta=0.35时y向速度降低，传播更偏向x。eta=1的长波极限下二者趋于平行；eta不等于1时，即使长波区u约为(qx,eta*qy)，一般仍不平行。坐标轴等特殊方向需单独判断。

[PNG](a-dispersion/a10-wavevector-velocity-direction.png) · [SVG](a-dispersion/a10-wavevector-velocity-direction.svg) · [PDF](a-dispersion/a10-wavevector-velocity-direction.pdf)

### a11-curvature-and-cubic · 色散曲率与三阶残差

**用途：** 左图分别画cos q与0.35 cos q，标出q=±pi/2处零曲率。右图在qx=pi/2、qy=0附近减去一阶切线，所得残差接近-delta qx³/6。二维点(pi/2,pi/2)的两个二阶系数都为零，但三阶仍在；本图只建立机制线索，不证明有限宽度波包严格无色散。

[PNG](a-dispersion/a11-curvature-and-cubic.png) · [SVG](a-dispersion/a11-curvature-and-cubic.svg) · [PDF](a-dispersion/a11-curvature-and-cubic.pdf)

### a12-exchange-and-scales · 交换比与能量和速度尺度

**用途：** 左图的带宽为2(1+eta)，右图分别是x、y分量和速度模的全布里渊区最大值。eta=1是空间交换各向同性，eta=0对应互不耦合的x向链并带来qy简并。所有上限是精确群速度界，不把它们误读为概率分布的严格有限支撑边界。

[PNG](a-dispersion/a12-exchange-and-scales.png) · [SVG](a-dispersion/a12-exchange-and-scales.svg) · [PDF](a-dispersion/a12-exchange-and-scales.pdf)

## B · 单格点翻转怎样传播

### b01-initial-local-flip · 局域单翻转初态

**用途：** 左图颜色为原点单翻转的概率P，线性色标0至1。右图显示y=0行的纵向自旋期望，原点为-1/2，其余为+1/2。量子化轴为+x；S为无量纲自旋算符。该归一化态有一个确定磁子，不能解释成具有非零横向自旋均值的经典旋转箭头。

[PNG](b-local-flip/b01-initial-local-flip.png) · [SVG](b-local-flip/b01-initial-local-flip.svg) · [PDF](b-local-flip/b01-initial-local-flip.pdf)

### b02-flat-spectrum · 局域初态的均匀波矢权重

**用途：** 对归一化单格点态作正交归一化二维离散Fourier变换。每个离散波矢的概率均为1/N²，图中绘制N²|A|²以提高可读性。左图为整个第一布里渊区，右图为qy=0截面。局域初态包含整个能带，不能用单个中心波矢及低阶Taylor展开描述其全部传播。

[PNG](b-local-flip/b02-flat-spectrum.png) · [SVG](b-local-flip/b02-flat-spectrum.svg) · [PDF](b-local-flip/b02-flat-spectrum.pdf)

### b03-early-neighbor-spreading · 早期近邻传播

**用途：** 四幅图依次为τ=0.25、0.6、1.2、2，固定线性色标0至1，显示中心7×7格点。颜色直接表示单翻转概率，不能逐图归一化解释为同一峰高。哈密顿量的近邻耦合产生概率向外转移；图中为完整FFT计算的局部裁切。

[PNG](b-local-flip/b03-early-neighbor-spreading.png) · [SVG](b-local-flip/b03-early-neighbor-spreading.svg) · [PDF](b-local-flip/b03-early-neighbor-spreading.pdf)

### b04-isotropic-late-snapshots · 等方晶格的后期传播

**用途：** τ=6、12、24、36的二维翻转概率采用相同空间范围及10^-7至0.1的对数色标。概率低于色标下限不可见，显示边缘不是严格截止。分布向外展开，同时保留相干干涉条纹和方格晶格的四重对称性；因此等方交换的点激发传播并不必然形成圆形波前。

[PNG](b-local-flip/b04-isotropic-late-snapshots.png) · [SVG](b-local-flip/b04-isotropic-late-snapshots.svg) · [PDF](b-local-flip/b04-isotropic-late-snapshots.pdf)

### b05-anisotropy-comparison · 交换各向异性与一维极限

**用途：** 固定τ=24与Jx，比较η=0、0.3、1。所有图使用同一空间尺度及10^-7至0.1的对数色标。η=0时y方向无耦合，概率严格停留在y=0行；η=0.3时二维分布沿y较窄；η=1时两个方向对称。这里的各向异性是空间交换参数差异，并未引入自旋空间的易轴或易面项。

[PNG](b-local-flip/b05-anisotropy-comparison.png) · [SVG](b-local-flip/b05-anisotropy-comparison.svg) · [PDF](b-local-flip/b05-anisotropy-comparison.pdf)

### b06-marginal-probabilities · 两个方向的边际概率

**用途：** η=0.3时τ=4、12、24的边际概率：左图对y求和，右图对x求和。各曲线对全部格点求和均为1；固定相同横坐标范围和纵轴范围以比较扩展速度。边际概率P_x、P_y与中心截线P_{m,0}、P_{0,n}不同。

[PNG](b-local-flip/b06-marginal-probabilities.png) · [SVG](b-local-flip/b06-marginal-probabilities.svg) · [PDF](b-local-flip/b06-marginal-probabilities.pdf)

### b07-spacetime-isotropic · 时空传播与最大群速度

**用途：** 对每个时间计算归一化二维态，再对y求和得到P_x。纵轴为τ，横轴为x/a；固定对数色标10^-7至1。青色虚线为x/a=±τ，对应|v_x|≤Jx a/ℏ，指出主要弹道前沿的位置。有限时间的晶格传播核在线外仍有小而非零的尾部，图示不是严格光锥。

[PNG](b-local-flip/b07-spacetime-isotropic.png) · [SVG](b-local-flip/b07-spacetime-isotropic.svg) · [PDF](b-local-flip/b07-spacetime-isotropic.pdf)

### b08-anisotropic-spacetime · 各向异性时空传播

**用途：** η=0.3的x、y边际概率时空图。由于初态和色散都可分离，P_x不依赖η；其数据与η=1完全相同。虚线分别为|x|/a=τ和|y|/a=0.3τ，颜色使用固定10^-7至1对数范围。线外仍存在非零尾部，最大群速度给出主要弹道前沿尺度。

[PNG](b-local-flip/b08-anisotropic-spacetime.png) · [SVG](b-local-flip/b08-anisotropic-spacetime.svg) · [PDF](b-local-flip/b08-anisotropic-spacetime.pdf)

### b09-ballistic-rms · 均方根宽度的弹道增长

**用途：** 从归一化FFT概率计算质心及标准差σ。无限晶格Bessel恒等式给出σx/a=τ/√2和σy/a=ητ/√2；实线为解析值，空心点为FFT矩。η=1、0.3、0的x曲线重合，y曲线随η变化。这里表征的是局域初态分布的展开，不是窄带Gaussian包络的二阶色散近似。

[PNG](b-local-flip/b09-ballistic-rms.png) · [SVG](b-local-flip/b09-ballistic-rms.svg) · [PDF](b-local-flip/b09-ballistic-rms.pdf)

### b10-return-probability · 中心返回概率的相干振荡

**用途：** 比较η=1和0.3的原点翻转概率，纵轴为对数。曲线为P00=J0(τ)^2 J0(ητ)^2，空心点为FFT直接读出的原点值。这里J0表示第一类Bessel函数，与交换常数Jx、Jy不同。原点概率的降低和再升高源于相干演化，不代表耗散或非线性相互作用。

[PNG](b-local-flip/b10-return-probability.png) · [SVG](b-local-flip/b10-return-probability.svg) · [PDF](b-local-flip/b10-return-probability.pdf)

### b11-anisotropy-scan · 交换比与RMS长宽比

**用途：** 固定Jx、初态、格点数和τ=24，只扫描η。左图显示σx不变、σy随η线性增长；右图为σy/σx=η。解析线和FFT点对照。在η>1时分布沿y比沿x宽；η=0退化为一维传播。该比较固定的是无量纲τ，即固定Jx条件下相同的物理时间。

[PNG](b-local-flip/b11-anisotropy-scan.png) · [SVG](b-local-flip/b11-anisotropy-scan.svg) · [PDF](b-local-flip/b11-anisotropy-scan.pdf)

### b12-probability-to-spin · 翻转概率与纵向自旋观测量

**用途：** η=1、τ=8时的y=0截线。左图为P_m0，右图逐格点应用<Sx>=1/2-P得到纵向自旋期望；虚线为背景1/2。两图纵轴不同，峰值概率对应自旋亏损。归一化单磁子态的总亏损为1，而<Sy>=<Sz>=0；概率波的复相位不能直接画成非零的局域横向平均自旋。

[PNG](b-local-flip/b12-probability-to-spin.png) · [SVG](b-local-flip/b12-probability-to-spin.svg) · [PDF](b-local-flip/b12-probability-to-spin.pdf)

### b13-independent-bessel-check · Bessel解析核独立验证

**用途：** 去除基态整体相位exp[-i EF t/ℏ]后，无限晶格解析振幅为exp[-i(1+η)τ] i^(m+n) J_m(τ)J_n(ητ)，故概率为两个Bessel平方的乘积。左图比较x边际，右图为FFT概率与解析概率逐格点之差的绝对值乘以10^17，采用线性色标；色标1代表实际误差10^-17。有限周期晶格只有在边界回绕可忽略时才与无限晶格核一致；另有N=512和边界概率质量检查。

[PNG](b-local-flip/b13-independent-bessel-check.png) · [SVG](b-local-flip/b13-independent-bessel-check.svg) · [PDF](b-local-flip/b13-independent-bessel-check.pdf)

### b14-early-spreading · 最初几步的单格点传播

**用途：** 从τ=0到4的实际FFT时间演化，η=[1.0]。所有帧采用相同空间窗以及1e-05至1的对数概率色标，无逐帧峰值归一化。坐标单位为a，时间单位为ℏ/Jx；截断显示的尾部不是严格零。

[GIF](b-local-flip/b14-early-spreading.gif)

### b15-isotropic-propagation · 等方晶格中的局域传播

**用途：** 从τ=0到36的实际FFT时间演化，η=[1.0]。所有帧采用相同空间窗以及1e-07至1的对数概率色标，无逐帧峰值归一化。坐标单位为a，时间单位为ℏ/Jx；截断显示的尾部不是严格零。

[GIF](b-local-flip/b15-isotropic-propagation.gif)

### b16-anisotropic-propagation · 等方与各向异性交换的传播对照

**用途：** 从τ=0到36的实际FFT时间演化，η=[1.0, 0.3]。所有帧采用相同空间窗以及1e-07至1的对数概率色标，无逐帧峰值归一化。坐标单位为a，时间单位为ℏ/Jx；截断显示的尾部不是严格零。

[GIF](b-local-flip/b16-anisotropic-propagation.gif)

### b17-marginal-animation · 各向异性边际概率演化

**用途：** η=0.3时的x、y边际概率动画。对另一空间方向求和，分别得到归一化分布Px和Py；两个面板全程使用相同的空间窗[-45a,45a]及对数纵轴[10^-7,1.2]。数值零仅在绘图时下限替代为10^-15，处于显示范围以外。

[GIF](b-local-flip/b17-marginal-animation.gif)

## C · Gaussian 波包怎样移动和展宽

### c01-carrier-envelope-spectrum · 载波、包络与频谱

**用途：** 两种归一化Gaussian初态只有载波不同：q0=(0,0)和(0.7,0)，sigma=4。左图的x边际概率严格相同；中图画中心区域连续展开的载波相位q0x*x，省略低振幅尾部；右图为单位正交FFT所得离散频谱的x边际概率，所有波矢的总概率为1。载波改变频谱中心及后续传播，但不改变初始概率包络。

[PNG](c-gaussian/c01-carrier-envelope-spectrum.png) · [SVG](c-gaussian/c01-carrier-envelope-spectrum.svg) · [PDF](c-gaussian/c01-carrier-envelope-spectrum.pdf)

### c02-space-bandwidth · 空间宽度与频谱宽度

**用途：** 比较sigma=3、6、10的无啁啾Gaussian初态，q0=(0.7,0)。sigma是概率分布的RMS宽度；不是振幅指数中再平方后的宽度。所有初态总概率为1，所以窄初态的空间峰值更高，而宽初态的频谱更窄。本图横轴和纵轴在各参数曲线之间统一。Delta q=1/(2 sigma)是宽包络、频谱远离Brillouin区接缝时的连续Gaussian表达式。

[PNG](c-gaussian/c02-space-bandwidth.png) · [SVG](c-gaussian/c02-space-bandwidth.svg) · [PDF](c-gaussian/c02-space-bandwidth.pdf)

### c03-zero-carrier-spreading · 零中心波矢：质心停留，概率向外展开

**用途：** 精确余弦色散下，sigma=4、q0=(0.0, 0.0)的归一化Gaussian在tau=0、30、60的二维格点概率。三个面板采用相同位置坐标范围和固定线性色标。青色虚线标记由概率分布直接计算的质心，标注给出概率RMS宽度。谱分布关于零波矢对称，因此两个方向的平均群速度都为0，质心停留在原点；不同非零波矢成分仍会向外传播并引起展宽。

[PNG](c-gaussian/c03-zero-carrier-spreading.png) · [SVG](c-gaussian/c03-zero-carrier-spreading.svg) · [PDF](c-gaussian/c03-zero-carrier-spreading.pdf)

### c04-moving-gaussian · 非零中心波矢：向右移动，同时逐渐展宽

**用途：** 精确余弦色散下，sigma=4、q0=(0.7, 0.0)的归一化Gaussian在tau=0、30、60的二维格点概率。三个面板采用相同位置坐标范围和固定线性色标。青色虚线标记由概率分布直接计算的质心，标注给出概率RMS宽度。频谱中心向正qx偏移，带来正x方向平均群速度；有限频宽仍使各成分群速度不同，所以包络一边移动一边展宽。y方向中心波矢为0，平均位移为0，但仍会展宽。

[PNG](c-gaussian/c04-moving-gaussian.png) · [SVG](c-gaussian/c04-moving-gaussian.svg) · [PDF](c-gaussian/c04-moving-gaussian.pdf)

### c05-carrier-directions · 由载波控制传播方向

**用途：** 保持sigma=4和初始概率包络相同，只将载波改成(-0.7,0)、(0.7,0)、(0.7,0.7)。在tau=60时分别得到左行、右行和斜向传播。白箭头由原点指向谱平均速度乘以时间得到的质心预测。对当前等宽、各向同性交换且两个非零波矢分量相同的例子，斜向群速度方向与载波方向一致；这一一致性并非任意色散或各向异性情形下的普遍规律。

[PNG](c-gaussian/c05-carrier-directions.png) · [SVG](c-gaussian/c05-carrier-directions.svg) · [PDF](c-gaussian/c05-carrier-directions.pdf)

### c06-centroid-velocity · 质心运动与谱平均速度

**用途：** 四种载波的概率质心由精确FFT演化计算。圆点为数值结果，实线用初态全频谱的<sin qx>和eta<sin qy>预测，虚线用中心波矢处的(sin q0x,eta sin q0y)近似。对于sigma=4，有限频宽使两者存在虽小但真实的差异，不能把中心值近似称为精确质心速度。当前无边界污染的平移不变模型中，位置期望按谱平均速度作直线运动。

[PNG](c-gaussian/c06-centroid-velocity.png) · [SVG](c-gaussian/c06-centroid-velocity.svg) · [PDF](c-gaussian/c06-centroid-velocity.pdf)

### c07-comoving-marginals · 共动坐标下的包络展宽

**用途：** 对q0=(0.7,0)、sigma=4的同一个波包，画tau=0、20、40、60的x和y边际概率。仅在横轴减去数值质心，没有重新归一化峰值或宽度。曲线使用实际格点概率并连线。x、y方向的色散曲率不同，因而展宽程度不同；质心的直线移动与包络的形状变化是可以分别测量的两件事。

[PNG](c-gaussian/c07-comoving-marginals.png) · [SVG](c-gaussian/c07-comoving-marginals.svg) · [PDF](c-gaussian/c07-comoving-marginals.pdf)

### c08-width-comparison · 不同初始宽度的传播对照

**用途：** sigma=3、6、10的Gaussian都以q0=(0.7,0)传播至tau=60，各自归一化总概率为1。左图画共动坐标下真实x边际概率；右图明确采用u=(x-<x>)/sigma、纵轴sigma*Px，以比较相对初始宽度的变化，保持分布面积一致。宽初态频谱更窄，因此相对展宽较小，但需要更大的初始空间范围。本图不把不同初始尺寸的波包解释成相同制备资源下的性能排名。

[PNG](c-gaussian/c08-width-comparison.png) · [SVG](c-gaussian/c08-width-comparison.svg) · [PDF](c-gaussian/c08-width-comparison.pdf)

### c09-rms-exact-moments · 概率宽度与精确速度方差

**用途：** 对于初始实Gaussian包络乘线性载波，初始位置与速度的对称协方差为零，因此无限晶格上Var(n_mu(tau))=Var(n_mu(0))+tau^2 Var(v_mu)精确成立。一般有啁啾的初态还会有2*tau*Cov_sym(n_mu,v_mu)项，不能直接套用本图公式。图中实线完全由初态离散频谱平均计算，圆点来自精确余弦色散演化；有限周期盒在tau<=60内已检查边缘概率与扩大网格误差。

[PNG](c-gaussian/c09-rms-exact-moments.png) · [SVG](c-gaussian/c09-rms-exact-moments.svg) · [PDF](c-gaussian/c09-rms-exact-moments.pdf)

### c10-anisotropy-direction · 各向异性下波矢与传播方向

**用途：** 固定q0=(0.7,0.7)、sigma=4和tau=60，仅改变eta=Jy/Jx为1或0.3。青色虚箭头示意波矢方向，长度不代表物理速度；白色箭头表示实际质心位移。两个初态的波矢方向同为45度，谱平均群速度方向分别约为45度和16.7度。由于vy=eta sin qy，较弱的y方向交换降低了y方向传播速率。所有概率图用同一固定线性色标。

[PNG](c-gaussian/c10-anisotropy-direction.png) · [SVG](c-gaussian/c10-anisotropy-direction.svg) · [PDF](c-gaussian/c10-anisotropy-direction.pdf)

### c11-anisotropy-width · 各向异性与二维宽度

**用途：** 相同圆对称Gaussian包络在eta=1和eta=0.3下的x、y概率RMS宽度。由于qx=qy=0.7且初始频宽相同，eta=1时两个方向的宽度曲线重合；eta=0.3保留相同x方向演化，但减小y方向的速度方差，导致宽度比sigma_x/sigma_y增大。这里的圆形和椭圆形描述包络尺度，不意味着离散晶格具有连续旋转对称性。

[PNG](c-gaussian/c11-anisotropy-width.png) · [SVG](c-gaussian/c11-anisotropy-width.svg) · [PDF](c-gaussian/c11-anisotropy-width.pdf)

### c12-spectrum-phase · 频谱功率守恒与相位积累

**用途：** 左图从tau=0、30、60的实际演化波函数重新做单位正交FFT，显示频谱概率逐点不变。这里e=epsilon/Jx为无量纲能量，tau=Jx*t/hbar。右图在qy=0截面画精确传播因子的残余相位-tau[e(qx,0)-e(0.7,0)-sin(0.7)(qx-0.7)]，相位连续展开而不是模2pi显示；去掉的是整体相位和中心群速度平移对应的线性相位。频谱概率不变并不保证实空间形状不变，因为不同模式的相对相位仍会变化。

[PNG](c-gaussian/c12-spectrum-phase.png) · [SVG](c-gaussian/c12-spectrum-phase.svg) · [PDF](c-gaussian/c12-spectrum-phase.pdf)

### c13-extension-inflection · 拓展：零二阶曲率点

**用途：** 这是后续保形研究的初步入口。两种初态的sigma都为3、总概率都为1。q0=(pi/2,pi/2)处两个方向的二阶色散项消失，有限频宽内速度差减小，因此tau<=60内的展宽与形变明显较弱。右图比较实际波函数与按各自谱平均速度刚性平移的初态的模平方重合度，对整体相位不敏感，但会检测相对相位形变；它不是仅比较概率轮廓的指标。三阶及更高阶项仍存在，不能据此宣称无限时间严格保形。

[PNG](c-gaussian/c13-extension-inflection.png) · [SVG](c-gaussian/c13-extension-inflection.svg) · [PDF](c-gaussian/c13-extension-inflection.pdf)

### c14-extension-cubic-distortion · 拓展：高阶色散的有限带宽形变

**用途：** 为使高阶形变在中期报告图中可见，本图用sigma=2、q0=(pi/2,pi/2)的独立示例；它与C13的sigma=3不同，不能据此直接比较保形性能。左图画tau=0、20、40、60的实际x边际概率，仅减去实际质心，保持统一纵轴。右图固定qy=pi/2，精确能量去除常数与线性项后为sin(delta q)-delta q，其首项是-(delta q)^3/6。有限频谱因此仍有相位差累积，产生不对称形变与尾部。此图说明零二阶曲率不等于零色散。

[PNG](c-gaussian/c14-extension-cubic-distortion.png) · [SVG](c-gaussian/c14-extension-cubic-distortion.svg) · [PDF](c-gaussian/c14-extension-cubic-distortion.pdf)

### c15-animation-carrier · C15  有无载波：静止展宽与移动展宽

**用途：** sigma=4的两个相同概率包络，载波分别为(0,0)与(0.7,0)，在精确色散下演化到tau=60。二维格点概率使用固定线性色标，图框和概率归一化固定，不逐帧放大。

[GIF](c-gaussian/c15-animation-carrier.gif)

### c16-animation-directions · C16  载波选择左行、右行与斜向传播

**用途：** 三个sigma=4的初态仅载波不同，分别为(-0.7,0)、(0.7,0)、(0.7,0.7)。在相同尺度下播放到tau=60，帮助将载波相位梯度与传播方向联系起来。色标、位置范围、总概率固定。

[GIF](c-gaussian/c16-animation-directions.gif)

### c17-animation-width · 不同初始宽度的展宽动画

**用途：** sigma=3、6、10的无啁啾Gaussian以q0=(0.7,0)传播。左图在各自共动坐标中显示真实边际概率，使用固定位置和纵轴范围；右图的移动点显示各自相对初始宽度的增长。所有初态总概率为1，初始尺寸不同是明确的物理输入。

[GIF](c-gaussian/c17-animation-width.gif)

### c18-animation-anisotropy · C18  交换各向异性改变传播方向与形状

**用途：** 固定q0=(0.7,0.7)、sigma=4，比较eta=1与0.3。降低y方向交换后，y方向质心位移和宽度增长均减小。概率图采用相同固定线性色标及位置范围。

[GIF](c-gaussian/c18-animation-anisotropy.gif)
