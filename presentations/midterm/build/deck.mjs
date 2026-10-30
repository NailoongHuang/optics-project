import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {applyPresentationChartFont,finalizePresentation} from 'file:///C:/Users/xuanm/.codex/plugins/cache/openai-primary-runtime/presentations/26.1017.11052/skills/presentations/container_tools/artifact_tool_utils.mjs';

const PROJECT='C:/Users/xuanm/Desktop/optics';
const WORK=PROJECT+'/presentations/midterm';
const BUILD=WORK+'/build';
const OUTPUT=WORK+'/output';
const SKILL='C:/Users/xuanm/.codex/plugins/cache/openai-primary-runtime/presentations/26.1017.11052/skills/presentations';
const PYTHON='C:/Users/xuanm/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES='C:/Users/xuanm/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const F=JSON.parse(await fs.readFile(BUILD+'/data_facts.json','utf8'));
const AS=JSON.parse(await fs.readFile(WORK+'/assets.json','utf8'));
const P=Presentation.create({slideSize:{width:1280,height:720}});
const font='Microsoft YaHei',mathFont='Cambria';
const C={ink:'#203648',blue:'#246B9A',rust:'#C95F42',green:'#27816E',purple:'#8356A5',muted:'#586C7B',line:'#D8E1E7',pale:'#EDF4F7'};
const colors=[C.blue,C.rust,C.green,C.purple,'#B68F2A'];
const specifications=[];const nativeCharts=[];const nativeTables=[];
let slide=null,record=null;

function txt(s,x,y,w,h,size=24,{bold=false,color=C.ink,face=font,align='left'}={}){
  const sh=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  sh.text=s;sh.text.style={typeface:face,fontSize:size,bold,color,alignment:align,verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};
  record.text.push(s);return sh;
}
function rule(x,y,w,color=C.line){slide.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:1.4},fill:color,line:{fill:'none',width:0}});}
function start(title,source,notes=''){
  slide=P.slides.add();slide.background.fill='#FFFFFF';
  record={number:P.slides.items.length,title,source,notes,text:[],assets:[],charts:[]};specifications.push(record);
  txt(title,54,29,1170,65,40,{bold:true});rule(54,108,1170);
  txt(source,55,680,1115,24,14,{color:C.muted});txt(String(record.number).padStart(2,'0'),1186,678,42,24,15,{color:C.muted,align:'right'});
  slide.speakerNotes.text=notes+'\n\n来源：'+source+'\n原理PDF：'+PROJECT+'/Note/single_magnon_derivation/main.pdf\n模拟源：'+PROJECT+'/figures/midterm-report/';
  return slide;
}
function conclude(text){rule(54,614,1170);txt(text,57,629,1166,44,23,{bold:true,color:C.blue});}
function block(title,body,x,y,w=360,size=23){txt(title,x,y,w,34,25,{bold:true,color:C.blue});txt(body,x,y+43,w,140,size);}
async function picture(file,x,y,w,h,alt,contentType='image/png'){
  const bytes=await fs.readFile(file);slide.images.add({blob:bytes,contentType,fit:'contain',position:{left:x,top:y,width:w,height:h},alt});
  record.assets.push({path:file,alt});
}
async function formula(key,x,y,w,h){const a=AS.formula[key];if(!a)throw new Error('Missing formula '+key);await picture(a.path,x,y,w,h,'原理公式 '+a.equation);}
async function fig(id,x,y,w,h){const a=AS.figures?.[id];let file=a?.path;
  if(!file){const g=id.startsWith('a')?'a-dispersion':id.startsWith('b')?'b-local-flip':'c-gaussian';file=PROJECT+'/figures/midterm-report/'+g+'/'+id+'.png';}
  await picture(file,x,y,w,h,id);
}
async function gif(id,x,y,w,h){const g=id.startsWith('b')?'b-local-flip':'c-gaussian';await picture(PROJECT+'/figures/midterm-report/'+g+'/'+id+'.gif',x,y,w,h,id,'image/gif');}
function math(s,x,y,w,h,size=29){return txt(s,x,y,w,h,size,{face:mathFont});}
function nativeChart(key,x,y,w,h,title,opts={}){
  const data=F.native_chart_series[key];if(!data)throw new Error('Chart key '+key);
  let selected=data.series.filter(a=>!opts.names||opts.names.includes(a.name));
  const readable={'qx axis, qy=0':'沿 x，qᵧ = 0','qy axis, qx=0':'沿 y，qₓ = 0',
    'q0=(0,0): sigma_x':'q₀ = (0,0)，σₓ','q0=(.7,0): sigma_x':'q₀ = (0.7,0)，σₓ','q0=(.7,0): sigma_y':'q₀ = (0.7,0)，σᵧ',
    'eta=1':'η = 1','eta=.3':'η = 0.3','eta=0':'η = 0','sigma=3':'σ = 3','sigma=6':'σ = 6','sigma=10':'σ = 10',
    extension_ordinary:'q₀ = (0.7,0.7)',extension_inflection:'q₀ = (π/2,π/2)'};
  const series=selected.map((a,i)=>({name:opts.labels?.[a.name]??readable[a.name]??a.name,xValues:a.x??a.xValues??data.x,values:a.values,
    line:{fill:colors[i%colors.length],width:2.7,style:'solid'},marker:{symbol:'none',size:4}}));
  return chart(series,x,y,w,h,title,{...opts,xLabel:opts.xLabel??data.x_label,yLabel:opts.yLabel??data.y_label},key);
}
function chart(series,x,y,w,h,title,opts={},key='analytic'){
  const minX=opts.xMin??Math.min(...series.flatMap(s=>s.xValues));
  const minY=opts.yMin??Math.min(...series.flatMap(s=>s.values));
  const c=slide.charts.add('scatter',{position:{left:x,top:y,width:w,height:h},title,titleTextStyle:{fontSize:23,fill:C.ink,bold:false},
    series,scatterOptions:{style:'line'},hasLegend:opts.legend!==false,
    legend:{position:'bottom',overlay:false,textStyle:{fontSize:18,fill:C.muted}},
    xAxis:{visible:!opts.hideX,title:{text:opts.xLabel??'',textStyle:{fontSize:20,fill:C.ink}},textStyle:{fontSize:17,fill:C.muted},position:'bottom',crossesAt:minX,
      min:opts.xMin,max:opts.xMax,majorUnit:opts.xStep,majorGridlines:null,line:{fill:C.line,width:1},numberFormatCode:opts.xFormat??'0'},
    yAxis:{title:{text:opts.yLabel??'',textStyle:{fontSize:20,fill:C.ink}},textStyle:{fontSize:17,fill:C.muted},position:'left',crossesAt:minY,
      min:opts.yMin,max:opts.yMax,majorUnit:opts.yStep,majorGridlines:{fill:'#E3E9ED',width:.7},line:{fill:C.line,width:1},numberFormatCode:opts.yFormat??'0.0'},
    chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF'});
  applyPresentationChartFont(c,{fontFamily:font});
  if(c.xAxis?.title?.textStyle)c.xAxis.title.textStyle.typeface=font;
  if(c.yAxis?.title?.textStyle)c.yAxis.title.textStyle.typeface=font;
  nativeCharts.push(record.number);record.charts.push({key,title,series});return c;
}
function table(values,x,y,w,h,widths=null,size=22){
  const t=slide.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,...(widths?{columnWidths:widths}:{})});
  t.borders.assign({fill:C.line,width:.8,style:'solid'});
  for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
    const cell=t.getCell(r,c);cell.fill=r===0?C.pale:'#FFFFFF';cell.text.style={typeface:font,fontSize:size,bold:r===0,color:C.ink,insets:10,verticalAlignment:'middle'};
  }
  nativeTables.push(record.number);record.text.push(values.map(r=>r.join(' / ')).join('\n'));return t;
}
async function wideFigure(title,id,source,leftHead,leftText,rightHead,rightText,notes=''){
  start(title,source,notes);await fig(id,44,125,1192,365);
  block(leftHead,leftText,59,500,551,22);block(rightHead,rightText,665,500,550,22);
}

// 01. Cover: one scientific visual, one source-derived equation, no invented identity.
start('二维铁磁体中的单磁子传播','中期报告　理论来源：单磁子推导 PDF　模拟：均匀最近邻交换模型',
  '报告研究零外场、自旋1/2正方晶格铁磁体。先解释直接库仑交换与单翻转精确子空间，再讨论线性传播与波包展宽。图中是有效模型计算。');
txt('库仑交换与线性波包动力学',58,154,620,124,47,{bold:true});
txt('基本物理图像与数值模拟',61,294,590,48,29,{color:C.blue});
await fig('a03-anisotropic-surface',695,146,550,385);
await formula('dispersion',58,411,612,88);
txt('由微观交换确定传播算符，再用局域激发与波包解释它的动力学。',60,552,1140,63,27);

// 02. Scope and a motivating animation.
start('研究对象与报告问题','原理 PDF 第 3–5 页　动画 B14',
  '以全极化铁磁态为背景，在其中翻转一个自旋。首先关注激发怎样在格点间传递，再区分波包整体运动和形状变化。动画在放映模式中展示。');
await gif('b14-early-spreading',45,132,700,437);
block('物理对象','二维正方晶格，每格点自旋 1/2。\n最近邻交换 Jₓ、Jᵧ，零外场。',790,145,430);
block('需要回答的问题','局域翻转怎样向外传播？\n载波怎样决定传播方向？\n有限宽度波包为什么会展宽？',790,323,430);
conclude('本报告把原理推导与可观测的概率分布逐一对应。');

// 03. Microscopic exchange.
start('两电子的直接积分与交换积分','原理 PDF 第 1–2 页，式 (1)–(9)',
  '固定两个正交归一的相邻轨道a,b，各占据一个电子。只保留固定占据下的直接库仑交换，不纳入电子跃迁产生的超交换。D和K都具有能量量纲。');
await formula('direct_exchange',61,155,790,205);
block('固定占据的出发点','轨道 a、b 正交归一，各有一个电子。\n库仑核作用在两电子坐标上。',900,145,320,22);
block('两种矩阵元','D 对应保持轨道配对的直接项。\nK 对应交换轨道配对的交换项。',900,345,320,22);
table([['积分','依赖的空间结构','在自旋模型中的作用'],['D','两轨道的密度分布','贡献共同能量常数'],['K','两轨道的交叉乘积','决定自旋交换耦合']],61,393,785,188,[100,330,355],21);
conclude('在固定轨道模型中，交换积分把电子的空间结构带入自旋动力学。');

// 04. Matrix and energy levels.
start('库仑矩阵与单重态、三重态','原理 PDF 第 2 页，式 (10)–(14)',
  '有序基底为↑↑、↑↓、↓↑、↓↓。反平行积态之间有−K的非对角矩阵元。两个反平行积态的对称和反对称组合分别属于triplet和singlet。D±K是本征态能量。');
txt('有序基底：↑↑、↑↓、↓↑、↓↓',60,124,590,31,22,{color:C.muted});
await formula('coulomb_matrix',52,155,585,220);await formula('eigenstates',115,403,456,172);
chart([{name:'三重态，3 个态',xValues:[.05,.45],values:[-1,-1],line:{fill:C.blue,width:5},marker:{symbol:'none'}},
       {name:'单重态，1 个态',xValues:[.55,.95],values:[1,1],line:{fill:C.rust,width:5},marker:{symbol:'none'}}],665,148,550,340,'交换引起的能级分裂',{xMin:0,xMax:1,hideX:true,yMin:-1.5,yMax:1.5,yStep:.5,yLabel:'(E − D) / K'});
txt('K > 0 时，三重态能量更低。\n能级间隔为 2K。',710,520,460,76,25,{bold:true,color:C.blue});

// 05. Operator matching.
start('矩阵匹配给出 Heisenberg 交换','原理 PDF 第 3 页，式 (17)–(21)',
  '比较S_a·S_b与库仑作用矩阵。中间块的非对角元为1/2，所以−J_H/2=−K，得到J_H=2K。常数项D−K/2只平移所有能量。');
await formula('spin_matrix',60,151,610,233);
await formula('heisenberg_pair',63,438,630,108);
math('−J / 2 = −K',760,162,450,70,35);
math('J = 2K',760,248,450,65,43);
block('共同的能量常数','D − K/2 不改变自旋态之间的能量差。\n对所有最近邻键求和得到晶格模型。',760,359,440,24);
conclude('自旋点积形式与两电子矩阵等价，交换系数由矩阵元确定。');

// 06. Lattice and ground state.
start('二维交换模型与全极化基态','原理 PDF 第 3 页，式 (22)–(25)　图 A01',
  '每条无向键计一次，背景沿+x极化。Jx和Jy的差异属于空间方向的交换各向异性，每条键上的自旋作用仍是点积。每条铁磁键均达到其能量下界。');
await fig('a01-lattice',38,142,725,420);
await formula('lattice_H',780,159,440,108);await formula('ground_energy',827,315,355,84);
txt('每条键只计一次\nJₓ、Jᵧ > 0，零外场\n背景自旋沿 +x 极化',804,442,409,131,25);
txt('左图为 5 × 5 个格点的局部示意。',66,574,675,31,21,{color:C.muted});
conclude('Jₓ ≠ Jᵧ 改变空间方向的耦合强度，单磁子仍在同一条能带上运动。');

// 07. Exact one-magnon sector.
start('单翻转子空间中的精确动力学','原理 PDF 第 4 页，式 (26)–(31)　图 B01',
  '局域翻转是基矢，不是一般的能量本征态。H作用后仍是单翻转基矢的线性组合，因此这个子空间精确闭合。概率P_i给出翻转位置的测量分布。');
await formula('oneflip_state',58,143,1100,71);await formula('oneflip_action',54,274,610,128);
txt('H 作用后仍是单翻转基矢的叠加。',60,414,610,40,24,{color:C.blue});
await formula('state_expansion',54,463,610,82);
await picture(BUILD+'/assets/figures/b01-initial-local-flip-left.png',735,238,480,345,'单点翻转概率初态');
conclude('Pᵢ = |cᵢ|²，ΣPᵢ = 1。沿极化轴的局域自旋满足 〈Sᵢˣ〉 = 1/2 − Pᵢ。');

// 08. Equation of motion.
start('交换耦合把翻转振幅传给相邻格点','原理 PDF 第 4–5 页，式 (28)、(34)、(35)',
  '一条含翻转的键相对基态增加Jij/2的对角能量，并产生−Jij/2的跃迁振幅。四个邻居的贡献相加，得到离散Schrödinger形式。E_F完整保留在原理推导中。');
await formula('bond_action',70,140,715,90);await formula('lattice_eom',60,282,1160,177);
table([['项','系数','物理含义'],['原格点振幅','基态能量 + Jₓ + Jᵧ','共同相位与交换对角能量'],['相邻格点振幅','−Jₓ/2、−Jᵧ/2','连接相邻翻转位置']],65,487,1145,150,[225,330,590],22);
txt('单条交换键',890,153,290,34,26,{bold:true,color:C.blue});txt('保留原位置，也产生相邻位置的振幅。',890,201,299,72,23);

// 09. Plane wave substitution.
start('平面波代入运动方程得到色散','原理 PDF 第 5 页，式 (36)–(39)',
  '均匀晶格具有平移不变性。相邻格点只相差e^{±ik_mu a}。将这些相位代入四邻居方程，两个指数相加成为2cos，从而得到单磁子激发能。此页沿用源PDF的hbar=1。');
await formula('plane_wave',72,142,637,91);await formula('neighbors',72,276,1130,84);
await formula('dispersion_derivation',74,401,1110,133);
txt('平移本征模式',811,149,368,40,27,{bold:true,color:C.blue});txt('相邻格点的振幅大小相同，\n空间移动只改变相位。',811,198,368,85,24);
conclude('余弦项来自正、反两个最近邻方向的相位之和。');

// 10. Dispersion surface plus native cuts.
start('色散曲面与方向带宽','原理 PDF 式 (39)　模拟 A02、A03 轴向截面数据',
  '能量用Jx归一化。左图eta=1色散曲面，右图使用实际保存的eta=.35轴向截面。原点是零激发能，最高能量2(1+eta)。二维点激发包含整个布里渊区。');
await fig('a02-isotropic-surface',40,144,600,380);
nativeChart('a03-anisotropic-surface_axial_cuts',655,145,566,383,'η = 0.35 的两个方向',{xLabel:'q = ka',xFormat:'0.0',yLabel:'ε / Jₓ',yMin:0,yMax:2.1});
txt('η = 1：能带宽度 4Jₓ',103,547,495,42,25,{bold:true,color:C.blue});
txt('固定 Jₓ，减小 η 会降低 y 方向带宽。',680,547,535,65,24);
conclude('正方晶格在大波矢处保留晶格对称性，长波区域才近似抛物面。');

// 11. Constant frequency and gradient.
await wideFigure('等频线与能量传播方向','a06-group-velocity-field','模拟 A05、A06，η = 1 与 0.35',
 '同一条等频线','线上各模式的频率相同。\n群速度指向色散曲面的梯度方向。',
 '空间各向异性','减小 Jᵧ 会降低群速度的 y 分量。\n波矢方向与传播方向需分别判断。',
 '箭头长度按共同尺度编码速度大小。等频不等于等群速度，也不自动保证完整局域波包保形。');

// 12. Slope and speed.
await wideFigure('群速度由色散斜率决定','a07-slope-and-speed','模拟 A07　ω = ε / ℏ',
 '群速度','v = (1/ℏ)∇ₖε。沿 x 方向，vₓ = (Jₓa/ℏ) sin qₓ。',
 '方向与速度上限','近原点，qₓ 的符号决定方向。\n最大 |vₓ| 对应 qₓ = ±π/2。',
 '有限频宽波包的精确质心速度是谱平均，中心波矢处群速度是窄带近似。');

// 13. Numerical bridge without changing the source convention silently.
start('原理公式与传播模拟的对应关系','原理 PDF 第 5 页　模拟 common.py 与 THEORY.md',
  '原理PDF保留E_F且取hbar=1。模拟恢复hbar后显式去除公共基态相位psi=e^{iE_Ft/hbar}c；概率保持不变。使用q=ka、tau=Jx*t/hbar、eta=Jy/Jx。每个FFT模式直接乘完整余弦色散的时间相位。');
math('ψ = exp(i',60,136,185,55,31);math('E',218,136,30,55,31);
math('F',240,151,24,31,20);math('t/ℏ)c',264,136,160,55,31);
math('|ψ|² = |c|²',525,136,625,55,31);
math('n = r/a',60,211,175,55,29);math('q = ka',255,211,165,55,29);
math('τ = Jₓt/ℏ',430,211,200,55,29);math('η = Jᵧ/Jₓ',655,211,230,55,29);
math('u = ℏv/(Jₓa)',900,211,320,55,29);
math('e(q) = ε/Jₓ = 1 − cos qₓ + η(1 − cos qᵧ)',60,286,1150,56,33);
math('A(q,τ) = A(q,0) exp[−i e(q)τ]',62,365,1145,56,33);
table([['实空间','波矢空间','可观测量'],['初态 ψ(n,0)','FFT 得到 A(q,0)','P(n,0) = |ψ(n,0)|²'],['逆 FFT 得到 ψ(n,τ)','各模式独立积累时间相位','P(n,τ)、质心、RMS 宽度']],63,444,1155,153,[355,415,385],22);
conclude('完整余弦色散直接决定时间演化，有限周期盒的影响另用扩大晶格对照检查。');

// 14. Local excitation and broad spectrum.
await wideFigure('一个格点的局域翻转包含整个能带','b02-flat-spectrum','模拟 B02　N = 256 表示 256 × 256 格点，Σ|A|² = 1',
 '位置越局域，频谱越宽','单点初态 ψₘₙ = δₘ₀δₙ₀。每个离散波矢的概率都为 1/N²。',
 '传播的直接后果','许多方向和速度的分量同时参与演化，局域激发自然向周围展开。',
 '图中为N²|A|²，仅为可读性缩放。不能用单一中心波矢或只在原点展开的二阶色散描述全部传播。');

// 15. Short and long dynamics.
await wideFigure('局域激发的后期传播与干涉图样','b04-isotropic-late-snapshots','模拟 B04　η = 1，四个时刻使用共同对数色标',
 '由近邻传递到空间展开','τ = 6、12、24、36 时，概率逐步向外展开，图中保留完整余弦能带的贡献。',
 '晶格与相干干涉','方格晶格留下四重对称图样。不同传播路径叠加形成条纹和旁瓣。',
 '早期过程见第2页动画。此页固定色标1e-7到0.1。显示边缘是色标阈值，前沿外仍有小概率尾部。');

// 16. Anisotropic probability animation and measured widths.
start('交换各向异性控制概率展开的方向尺度','模拟 B05、B11、B16　Jₓ 固定',
  '快照比较eta=0、.3、1，均为同一单点初态tau24。RMS_x=tau/sqrt2，RMS_y=eta*tau/sqrt2。eta=0为解耦链极限。动画对照在附录。');
await fig('b05-anisotropy-comparison',42,141,802,420);
block('相同初态，相同时间','τ = 24 时，x 方向 RMS 宽度均为 16.971a。',887,151,335,24);
block('改变 η = Jᵧ/Jₓ','η = 1：σᵧ = 16.971a\nη = 0.3：σᵧ = 5.091a\nη = 0：严格停留在原链。',887,340,335,24);
conclude('单点初态的 RMS 长宽比 σᵧ/σₓ = η，给出可直接检查的各向异性规律。');

// 17. Main front and RMS.
start('传播前沿与均方根宽度描述不同尺度','模拟 B07、B09　左图 η = 1，右图 η = 1、0.3、0',
  '热图是Px，即对y求和的边际概率。主要前沿由最大x群速度|u_x|≤1描述，RMS_x=tau/sqrt2。前沿之外仍有非零尾部，不是严格有限支持。');
await fig('b07-spacetime-isotropic',38,140,655,418);
nativeChart('local_flip_rms_y',712,146,516,389,'RMS 宽度的弹道增长',{xLabel:'时间 τ',yLabel:'σᵧ / a',xMin:0,xMax:40,yMin:0,yMax:30,xStep:10,yStep:10});
txt('主要前沿：|x|/a ≈ τ',90,564,550,44,26,{bold:true,color:C.blue});
txt('等方情形：σₓ/a = σᵧ/a = τ/√2',735,564,485,44,25,{face:mathFont});
conclude('宽度与时间成正比，对应相干弹道展开。图示前沿之外仍存在小尾部。');

// 18. Return and observable.
start('局域返回概率的相干振荡','模拟 B10　固定单磁子数态，η = 1 与 0.3',
  '原点返回概率的振荡是无耗散相干传播的结果。沿+x量子化时<Sx>=1/2-P，而<Sy>=<Sz>=0。所有格点的纵向亏损之和为1。图的两部分纵轴不同。');
await fig('b10-return-probability',45,136,1188,377);
txt('P₀₀ 随时间降低并出现振荡，ΣP 始终为 1。',57,540,1140,55,26);
conclude('局部概率减少表示激发向外传播，当前模型没有引入阻尼或磁子损失。');

await wideFigure('翻转概率对应纵向自旋亏损','b12-probability-to-spin','模拟 B12　η = 1，τ = 8，背景沿 +x 极化',
 '局域观测量','〈Sᵢˣ〉 = 1/2 − Pᵢ。\n概率峰对应自旋亏损。\n全部格点的亏损之和为 1。',
 '量子态的解释','固定单磁子数态满足\n〈Sᵢʸ〉 = 〈Sᵢᶻ〉 = 0。\n概率振幅描述翻转位置的量子叠加。',
 '左图是y=0中心截线，不是对y求和的边际。两个面板纵轴不同，右图显示相对1/2背景的亏损。');

// 19. Gaussian preparation.
start('载波、包络与初始频谱','模拟 C01　n = r/a，σ 以格点数计，σ = 4，η = 1',
 'Gaussian振幅的指数分母为4sigma²，sigma是概率分布的RMS宽度。载波改变频谱中心，但不改变初始概率。');
math('ψ₀(n) ∝ exp[−(nₓ²+nᵧ²)/(4σ²)] exp(i q₀·n)',63,128,1148,57,30);
await fig('c01-carrier-envelope-spectrum',43,200,1192,290);
block('σ 是初始概率 RMS 宽度','载波只改变相位与频谱。\n初始位置概率包络保持相同。',60,510,550,22);
block('相位决定频谱位置','频谱中心移到 q₀。\n平均速度与传播方向随之改变。',665,510,550,22);

// 20. Motion examples and animation.
start('载波选择静止、左行、右行与斜向传播','模拟 C05　静态快照 τ = 60，σ = 4，η = 1',
  '三个tau60快照对应相同初始概率包络，q0分别为(-.7,0),(.7,0),(.7,.7)。零载波情况下质心不动但包络仍展宽，见C03。三幅图使用共同空间窗与色标。');
await fig('c05-carrier-directions',42,139,1188,350);
block('零中心波矢','q₀ = (0,0) 时，平均速度为零。\n向两侧运动的分量仍使包络展宽。',60,507,546,23);
block('非零中心波矢','相位梯度改变频谱权重，让概率质心产生净位移。',665,507,550,23);

// 21. Native trajectory with numerical evidence.
start('质心速度是整个频谱的加权平均','模拟 C06　σ = 4，η = 1，τ ≤ 60',
  '图表数值直接来自保存的NPZ轨迹。对于q0=(.7,0)，真实质心速度是.6392043454，而sin(.7)=.6442176872。tau60时，中心波矢近似会多预测.3008005a位移。');
nativeChart('gaussian_centroid_x',45,143,802,420,'不同载波的质心轨迹',{
  names:['qzero','qright','qleft'],labels:{qzero:'q₀ = (0,0)',qright:'q₀ = (0.7,0)',qleft:'q₀ = (−0.7,0)'},
  xLabel:'时间 τ',yLabel:'〈x〉/a',xMin:0,xMax:60,xStep:20,yMin:-40,yMax:40,yStep:20});
block('精确谱平均','ūₓ = Σ |A(q)|² sin qₓ\n相同初态的谱权重保持不变。',895,150,325,23);
block('有限频宽的差别','ūₓ = 0.639204\nsin(0.7) = 0.644218\nτ = 60：〈x〉 = 38.3523a',895,355,325,24);
conclude('中心波矢处群速度适用于窄带近似，实际质心轨迹由谱平均给出。');

// 22. Translation and broadening.
await wideFigure('共动坐标把展宽从整体移动中分离出来','c07-comoving-marginals','模拟 C07　q₀ = (0.7,0)，σ = 4，η = 1',
 '只减去质心位移','每条曲线都在各自的共动坐标中显示，峰值与宽度没有重新归一化。',
 '两个方向分别展宽','τ = 60 时 σₓ = 6.970a，σᵧ = 8.449a。不同方向的曲率导致不同速度方差。',
 'Px和Py都是对另一方向求和的边际概率，分别归一化为1。x运动和形状变化可以分别度量。');

// 23. Exact velocity variance relation and curves.
start('速度方差决定无啁啾 Gaussian 的展宽','模拟 C09　完整色散下的数值宽度与谱矩关系',
  '无限晶格下初始位置与速度的对称协方差为零，Var(n(tau))=Var(n0)+tau²Var(u)。当前有限周期盒在展示范围内有边界检查。对于一般有啁啾初态还存在2tau Cov_sym项。');
nativeChart('gaussian_rms',44,147,793,417,'概率 RMS 宽度随时间变化',{xLabel:'时间 τ',yLabel:'RMS 宽度 / a',xMin:0,xMax:60,xStep:20,yMin:3,yMax:9,yStep:2});
math('Var[n(τ)] = Var[n(0)]\n                 + τ² Var(u)',875,165,350,112,28);
block('物理解释','不同波矢的群速度不同。\n速度差随传播时间积累，\n形成包络宽度的增长。',885,335,335,24);
conclude('这里使用完整余弦色散的谱矩，不把结果限制为二阶抛物线近似。');

// 24. Width bandwidth.
start('初始空间宽度与相对展宽','模拟 C02、C08　q₀ = (0.7,0)，η = 1',
  'sigma3/6/10都归一化为1，但初始空间范围不同。更宽包络对应更窄频谱，通常有较小相对展宽。本页不将其解释为相同初始资源的性能比较。');
await fig('c02-space-bandwidth',43,146,727,343);
nativeChart('width_relative',790,151,436,353,'相对初始宽度',{xLabel:'时间 τ',yLabel:'σₓ(τ) / σ',xMin:0,xMax:60,xStep:20,yMin:1,yMax:3,yStep:.5});
table([['初始 RMS 宽度 / a','3','6','10'],['σₓ(60) / σₓ(0)','2.718','1.185','1.026']],61,526,1155,82,[315,280,280,280],22);
conclude('更窄频谱减小速度分散，同时需要更大的初始空间范围。');

// 25. Anisotropy changes direction and shape.
start('各向异性同时改变方向与包络尺度','模拟 C10、C11　q₀ = (0.7,0.7)，σ = 4',
  '左右保持q0、sigma和tau60相同，只改变eta。波矢均为45度，谱平均群速度方向分别45度和16.699度。eta.3时中心为(38.3523,11.5057)a。');
await fig('c10-anisotropy-direction',45,142,791,391);
block('相同的波矢方向','q₀ 的方向均为 45°。\nη = 1：传播方向 45°。\nη = 0.3：传播方向 16.70°。',886,150,336,23);
block('τ = 60 的宽度','η = 0.3 时\nσₓ = 6.970a\nσᵧ = 4.351a',886,363,336,24);
conclude('减弱 y 方向交换会同时降低 y 向质心速度和速度方差。');

// 26. Spectral phase mechanism.
await wideFigure('频谱概率守恒，实空间形状仍会改变','c12-spectrum-phase','模拟 C12　e = ε/Jₓ，τ = Jₓt/ℏ',
 '时间演化保持谱权重','A(q,τ) = A(q,0) exp[−ie(q)τ]。\n每个模式的概率保持不变。',
 '相对相位产生形变','去掉整体与平移相位后，\n高阶残余相位继续累积。\n动力学本身仍为线性。',
 '右图为固定qy=0时的精确残余相位，连续展开显示，不取模2pi。这里的非线性相位指相位对波矢的非线性依赖，模型动力学仍是线性的。');

// 27. Limited next-step result.
start('零二阶曲率是后续保形研究的入口','模拟 C13　同初宽 σ = 3，η = 1',
  '对比普通中心q0=(.7,.7)和(pi/2,pi/2)。sigma均3，tau均60，使用各自真实谱平均速度作平移参考。F为复态重合模平方，含相对相位改变，不仅是概率轮廓重合。');
nativeChart('inflection_width',47,146,570,350,'相同初始宽度的传播',{xLabel:'时间 τ',yLabel:'σₓ / a',xMin:0,xMax:60,xStep:20,yMin:3,yMax:9,yStep:2});
nativeChart('inflection_fidelity',655,146,570,350,'相对平移初态的复态重合度',{xLabel:'时间 τ',yLabel:'F',xMin:0,xMax:60,xStep:20,yMin:0,yMax:1,yStep:.25,yFormat:'0.00'});
txt('F = |〈ψ平移参考 | ψ(τ)〉|²，包含相对相位变化',80,507,1120,43,26);
txt('τ = 60：普通波矢 F = 0.3823',77,559,520,40,25,{color:C.blue,bold:true});
txt('τ = 60：零曲率点 F = 0.9771',684,559,530,40,25,{color:C.rust,bold:true});
conclude('二阶项消失能减慢有限时间内的形变，三阶及更高阶色散仍然存在。');

// 28. Main conclusions, represented as evidence mapping rather than generic summary.
start('当前结果与下一阶段问题','理论 PDF 第 1–5 页　模拟 A、B、C 组',
  '本次完成的层次是模型推导、线性传播图像与有限时间的数值证据。未来研究可针对具体初态局域性与完整二维保形，不将当前toy model直接等同于实际材料。');
table([['理论或模拟结果','已建立的物理认识','下一步需要回答'],
 ['两电子矩阵与 J = 2K','交换作用连接不同翻转位置','具体材料的有效交换参数'],
 ['色散曲面与群速度','斜率控制运动，曲率影响展宽','给定波包尺寸下的参数选择'],
 ['单点与 Gaussian 传播','质心、宽度和干涉可分别度量','完整二维波包的保形指标'],
 ['零二阶曲率点对照','有限时间内形变受到抑制','高阶残差与可用传播距离']],55,144,1170,333,[330,415,425],23);
txt('模型范围',60,518,280,38,27,{bold:true,color:C.blue});
txt('均匀晶格、单磁子、零外场、无耗散。当前结论对应记录的参数与时间窗口。',293,520,925,90,25);

// 29. Supporting microscopic detail.
start('附录：费米交换符号与自旋矩阵','原理 PDF 第 2–4 页，式 (9)、(15)、(17)、(27)',
  '本页用于回答交换负号和单翻转矩阵元问题。源推导固定产生算符顺序f_a† f_b†。从反平行态读出非对角元−K，再与−J S_a·S_b匹配。所有箭头相对于x量子化轴。');
await formula('fermi_exchange',62,149,1150,87);
await formula('spin_components',60,277,1140,90);
await formula('bond_matrix_action',80,416,708,147);
txt('费米反对易关系\n决定交换项的负号。\n自旋矩阵沿 x 轴量子化。',850,432,366,121,24);
conclude('固定基底与算符顺序后，矩阵元符号和 J = 2K 的系数保持一致。');

// 30. Long wave approximation.
start('附录：长波二次近似的适用范围','模拟 A08、A09　轴向能量近似',
  'e≈(qx²+eta qy²)/2只适用于小波矢。误差阈值是轴向能量的相对误差，不是传播保真度阈值。相位差还随时间积累。所有主动力学计算使用完整余弦色散。');
await fig('a08-long-wave-approximation',44,148,780,375);
block('相对能量误差','1%：q ≈ 0.3454\n5%：q ≈ 0.7633',881,166,335,27);
block('传播时的限制','同样的能量误差会随时间积累为相位误差。主模拟保留完整余弦能带。',881,371,335,23);
conclude('长波近似便于理解局部机制，其使用范围由波矢与传播时间共同约束。');

// 31. Numerical controls as scientific appendix.
start('附录：独立计算路径与边界检验','checks_independent.json、checks_b.json、checks_c.json',
  '验证图为FFT与无限晶格Bessel解析传播核比较。独立稀疏矩阵Hamiltonian直接按键构造。边界与扩大晶格测试说明当前展示区间内数值可信，不能代替材料参数验证。');
await fig('b13-independent-bessel-check',41,144,742,365);
table([['对照','误差量级'],['实空间矩阵 vs FFT','振幅 L² ≈ 3.4×10⁻¹⁵'],['Bessel 核 vs FFT','max|ΔP| ≈ 5.6×10⁻¹⁶'],['Gaussian 扩大晶格','概率 L¹ ≤ 3.8×10⁻¹⁵'],['Gaussian 边缘概率','≤ 5.7×10⁻¹⁴']],810,159,416,332,[220,196],18);
conclude('解析解、独立推进与扩大晶格对照，共同约束计算误差和边界影响。');

// 32. Higher-order residual and model limitations.
await wideFigure('附录：零二阶曲率后的高阶形变','c14-extension-cubic-distortion','模拟 C14　独立示例 σ = 2，q₀ = (π/2,π/2)',
 '残余色散','扣除常数和线性项后，sin δq − δq 的首项为 −δq³/6。',
 '有限频宽的后果','相位差仍会积累，产生偏斜与尾部。本页 σ = 2，与前面的 σ = 3 对照不同。',
 '本页是为了显示高阶形变的独立例子，不能把结果与sigma3例子解释为同一初态资源的性能比较。');

// Animation supplement follows the static explanations.
start('附录：传播动画对照','单点翻转 B16　Gaussian 载波方向 C16',
 '本页嵌入完整GIF，在支持GIF的PowerPoint放映模式下播放。静态关键帧已经出现在正文各向异性和载波方向页。动画使用固定色标，不逐帧峰值归一化。');
await gif('b16-anisotropic-propagation',40,147,600,390);
await gif('c16-animation-directions',655,147,580,390);
txt('单点激发：η = 1 与 0.3',70,553,550,46,25,{bold:true,color:C.blue});
txt('相同 Gaussian 包络，不同载波',675,553,540,46,25,{bold:true,color:C.blue});
conclude('放映时观察时间演化，静态关键帧与定量曲线用于比较传播规律。');

// Source map that is useful for questions and later reuse.
start('附录：原理、图组与数据来源','项目本地材料与可复现模拟文件',
  '本报告未新增外部实验或材料参数。理论依据是本地五页原理PDF，数值结果来自既有39图8动画资料包。每个图表的具体来源已写入其所在页的备注。');
table([['材料','承担的内容','定位'],
 ['原理 PDF，5 页','直接交换、矩阵匹配、EOM、色散','Note/single_magnon_derivation/main.pdf'],
 ['A 组，12 图','色散、群速度、近似范围','figures/midterm-report/a-dispersion/'],
 ['B 组，13 图与 4 动画','局域翻转与解析传播核','b-local-flip/local_flip_data.npz'],
 ['C 组，14 图与 4 动画','Gaussian 质心、宽度与相位','c-gaussian/gaussian_simulation_data.npz']],55,143,1170,350,[270,390,510],21);
txt('符号对照',62,531,210,38,27,{bold:true,color:C.blue});
math('q = ka     τ = Jₓt/ℏ     η = Jᵧ/Jₓ     e = ε/Jₓ',280,530,935,55,30);

await fs.mkdir(BUILD+'/renders',{recursive:true});await fs.mkdir(OUTPUT,{recursive:true});
await fs.writeFile(BUILD+'/slide_spec.json',JSON.stringify(specifications,null,2),'utf8');
await fs.writeFile(BUILD+'/deck.proto.json',JSON.stringify(P.toProto()),'utf8');
for(let i=0;i<P.slides.items.length;i++){
 const s=P.slides.items[i]; const png=await P.export({slide:s,format:'png',scale:1.5});
 await fs.writeFile(BUILD+`/renders/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await png.arrayBuffer()));
 const layout=await s.export({format:'layout'});await fs.writeFile(BUILD+`/renders/slide-${String(i+1).padStart(2,'0')}.layout.json`,await layout.text());
 console.log('Rendered',i+1,'/',P.slides.items.length);
}
const candidate=BUILD+'/candidate.pptx';await(await PresentationFile.exportPptx(P)).save(candidate);
// The bundled PDF exporter currently lacks its Helvetica standard-font module.
// A preview PDF is assembled from the verified slide renders by prepare_preview.py.
const version=process.argv.includes('--release')?'中期报告_单磁子传播.pptx':(process.argv.includes('--final')?'midterm-report-final.pptx':(process.argv.includes('--revision2')?'midterm-report-v2.pptx':'midterm-report.pptx'));
const result=await finalizePresentation({workspaceDir:WORK,candidatePath:candidate,finalPath:OUTPUT+'/'+version,
 pythonExecutable:PYTHON,integrityValidatorPath:SKILL+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:SKILL+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',
   ...[...new Set(nativeTables)].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeChartOwnerSlides:[...new Set(nativeCharts)],requiredNativeTableOwnerSlides:[...new Set(nativeTables)],
 fontPolicy:{basis:'design',families:[font,mathFont]},verifyArtifactToolImport:true,
 materializeLiteralChartWorkbooks:true,nativeChartTargetApplication:'powerpoint',
 receiptPath:BUILD+'/'+version+'.validation.json'});
await fs.writeFile(BUILD+'/build_result.json',JSON.stringify({slides:P.slides.items.length,charts:nativeCharts,tables:nativeTables,finalizer:result},null,2));
console.log('FINAL',OUTPUT+'/'+version);
