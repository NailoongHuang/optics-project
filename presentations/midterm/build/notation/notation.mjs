import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile,FileBlob} from '@oai/artifact-tool';
import {applyPresentationChartFont,finalizePresentation} from 'file:///C:/Users/xuanm/.codex/plugins/cache/openai-primary-runtime/presentations/26.1017.11052/skills/presentations/container_tools/artifact_tool_utils.mjs';

const PROJECT='C:/Users/xuanm/Desktop/optics';
const WORK=PROJECT+'/presentations/midterm';
const BUILD=WORK+'/build/notation';
const OUTPUT=WORK+'/output';
const SKILL='C:/Users/xuanm/.codex/plugins/cache/openai-primary-runtime/presentations/26.1017.11052/skills/presentations';
const PYTHON='C:/Users/xuanm/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES='C:/Users/xuanm/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const F=JSON.parse(await fs.readFile(WORK+'/build/data_facts.json','utf8'));
const AS=JSON.parse(await fs.readFile(WORK+'/assets.json','utf8'));
const P=await PresentationFile.importPptx(await FileBlob.load(BUILD+'/source-before-notation.pptx'));
const sourceInspect=await P.inspect({kind:'slide,layout,notes',maxChars:200000});
await fs.writeFile(BUILD+'/source-inspect.ndjson',sourceInspect.ndjson??JSON.stringify(sourceInspect));
P.slides.keep([]);
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
  txt(title,44,22,1192,62,38,{bold:true});rule(44,96,1192);
  txt(source,45,687,1130,21,13,{color:C.muted});txt(String(record.number).padStart(2,'0'),1190,684,42,24,14,{color:C.muted,align:'right'});
  slide.speakerNotes.text=notes+'\n\n来源：'+source+'\n原理PDF：'+PROJECT+'/Note/single_magnon_derivation/main.pdf\n模拟源：'+PROJECT+'/figures/midterm-report/';
  return slide;
}
function conclude(text){rule(44,623,1192);txt(text,46,635,1188,38,22,{bold:true,color:C.blue});}
function block(title,body,x,y,w=360,size=23){txt(title,x,y,w,34,25,{bold:true,color:C.blue});txt(body,x,y+43,w,Math.min(140,674-y-43),size);}
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

const GROOT=PROJECT+'/figures/midterm-report/notation';
const GM=JSON.parse(await fs.readFile(GROOT+'/manifest.json','utf8'));
const GD=JSON.parse(await fs.readFile(PROJECT+'/figures/midterm-report/curvature-design/chart_data.json','utf8'));
const cases=GD.cases;
async function g(id,x,y,w,h){
 const a=GM.items.find(s=>s.id===id);if(!a)throw new Error(id);
 const ext=a.files.png?'png':'gif';await picture(GROOT+'/'+a.files[ext],x,y,w,h,a.caption,ext==='gif'?'image/gif':'image/png');
 slide.speakerNotes.append('\n图：'+a.caption);
}
function note(s,x,y,w=1182,size=22,h=85){return txt(s,x,y,w,h,size);}
const keys=['A_eta1','B_eta1','C_eta1'];
const labels=['A 普通点','B 零曲率线','C 零曲率交点'];
function series(ks,field,ls){return ks.map((k,i)=>({name:ls[i],xValues:cases[k].track.t,values:cases[k].track[field],line:{fill:colors[i],width:3},marker:{symbol:'none'}}));}
function metric(k,field,n=3){return cases[k].track[field].at(-1).toFixed(n);}
const timeAxis='时间 t（单位 ℏ/Jₓ）';
const main='σ=6a，Jᵧ=Jₓ，512×512 格点，完整余弦色散';
const commonNotes='使用物理变量x,y,kx,ky,epsilon,t。a为晶格间距，x,y取晶格位置。epsilon=E_k-E_F。psi已去掉E_F公共相位，固定初始相位。时轴数字以hbar/Jx为单位，位置与宽度以a为单位。传播为完整余弦色散的精确谱演化，内部存储数组保持原数值，物理谱相位epsilon*t/hbar不变。主比较初始概率RMS宽度6a、t=180hbar/Jx，行进距离不同。总概率为1。均匀、自旋1/2、铁磁、单磁子、零外场、无耗散。';

start('二维单磁子的能带几何与波包设计','中期报告　原理 PDF、曲率解析与波包数值模拟',commonNotes);
txt('从交换模型到零曲率选点与有限时间传播',48,112,1182,44,28,{bold:true,color:C.blue});
await g('g00_cover',665,170,560,430);
await g('eq_dispersion',44,188,595,104);
block('物理问题','怎样选择中心波矢，使二维波包\n在传播中较少展宽？',49,327,577,26);
block('基本物理量','位置 x、y，波矢 kₓ、kᵧ，时间 t。\n激发能 ε 已在上式定义，晶格间距 a。',49,472,577,25);
conclude('用能带几何提出设计，再用完整色散检验有效传播时间与限制。');

start('交换模型与单磁子子空间','原理 PDF 第 3–4 页，式 (20)、(22)、(25)、(29)　改用位置 x、y',
 commonNotes+'H仅表示哈密顿量。原理PDF中格点编号i改写为物理位置x,y，近邻位置明确相差a。每条键计一次，J=2K>0，极化方向+x。单翻转子空间精确闭合。');
await g('eq_lattice_H',54,113,1168,97);
await g('g_lattice',37,219,478,339);
await g('eq_action',540,236,688,142);
await g('eq_state',543,401,678,111);
note('a 是相邻格点间距。|x,y〉表示该位置的一次自旋翻转。\n全极化基态沿 +x，ψ 是去掉基态公共相位后的振幅。',542,531,682,21);
conclude('相邻位置的交换耦合使单翻转振幅传播，单磁子空间内可精确求解。');

start('运动方程与完整能带的谱演化','原理 PDF 第 5 页，式 (35)–(39)　所有公式显式保留 ℏ',commonNotes);
await g('eq_eom',53,118,1170,154);
await g('eq_evolution',63,317,1150,109);
math('P(x,y,t) = |ψ(x,y,t)|²，Σₓ,ᵧ P(x,y,t) = 1',49,468,1180,57,29);
note('ψ(x,y,t) 随时间演化，P(x,y,t) 是各格点的翻转概率。\n图中位置与宽度以 a 计，时间以 ℏ/Jₓ 计，所有格点的总概率守恒。',49,542,1180,23);
conclude('色散的一阶项控制平移，二阶及更高阶项改变包络与相位结构。');

start('能带导数与高斯曲率','高斯曲率按统一尺度的能量图面计算。H 仅用于哈密顿量。',
 commonNotes+'曲率图面采用坐标(kx*a,ky*a,epsilon/Jx)，以统一轴尺度，数值与上版完全相同。对物理kx,ky的导数保留a和J。二阶混合导数为0。曲率不是Berry曲率，轴缩放改变曲率数值但正轴缩放保留零集合与符号。定义见 https://mathworld.wolfram.com/GaussianCurvature.html 公式(15)。物理导数换算经SymPy验证残差0。');
await g('eq_derivatives1',80,124,1120,93);
await g('eq_derivatives2',57,241,1165,105);
await g('eq_curvature',87,383,1107,145);
note('曲率图统一使用三轴坐标 (kₓa, kᵧa, ε/Jₓ)。分母始终为正。',51,563,1178,23);
conclude('曲率符号由 cos(kₓa)cos(kᵧa) 决定，零曲率位置可解析求出。');

start('各向同性：多个布里渊区中的能带与曲率','Jᵧ=Jₓ　kₓ、kᵧ 范围均为 −3π/a 至 3π/a，共 3×3 个布里渊区',
 commonNotes+'左图色标epsilon/Jx范围0至4。右图高斯曲率范围正负1，绿线为零曲率，虚线围成中心第一BZ。多BZ为同一带的周期延拓，坐标轴kx a/pi、ky a/pi只是标注刻度单位。');
await g('g01_multibz_eta1',39,115,1200,493);
conclude('左深色表示高能量，右红正蓝负。绿色为零曲率线，黑虚线围成中心第一布里渊区。');

start('各向异性：曲率幅度改变，零点位置相同','Jᵧ=0.3Jₓ　波矢范围与能量色标不变，右侧曲率色标改为 ±0.3',
 commonNotes+'Jy减小时y向色散较弱。曲率数值范围与上一页不同，应读取色标。Jy/Jx>0时零集合不变。');
await g('g02_multibz_eta03',39,115,1200,493);
conclude('Jᵧ 减小后 y 向色散较弱。两页曲率色标不同，幅值比较应读取色标数值。');

start('零曲率位置上的能量分布','Jᵧ=Jₓ　左图只画零曲率线上的能量，浅灰背景表示未绘制',
 commonNotes+'使用解析精确轨迹，线外留空。m,n只为零曲率线的整数编号，不代表实空间位置。零曲率不等于零能量或零速度。');
await g('g03_zero_locus_band',39,112,1200,454);
await g('eq_zeros',59,569,1160,48);
conclude('两族零曲率线周期重复，交点同时使两个方向的二阶导数为零。');

start('中心波矢的三种选择','以下固定 Jᵧ=Jₓ。中列依次为能带对 kₓ、kᵧ 的二阶导数。',
 commonNotes+'二阶导数对物理波矢求导，单位Jx*a²。旧版Hessian记号H删除，避免与哈密顿量混用。二阶导数控制二次谱相位，一般不等于图面主曲率。k中心单位1/a。');
await g('g04_candidates',34,129,513,446);
table([['中心波矢 (kₓ₀,kᵧ₀)','二阶导数\n单位 Jₓa²','设计含义'],['A (0.7/a, 0.7/a)','(0.765, 0.765)','两个方向有二阶色散'],['B (π/(2a), 0.7/a)','(0, 0.765)','仅 x 向二阶项消失'],['C (π/(2a), π/(2a))','(0, 0)','两个二阶项同时消失']],556,161,678,288,[245,194,239],19);
note('图轴 kₓa/π=0.5 对应 kₓ=π/(2a)。\n单条零曲率线只消去一个方向的二阶项，交点才同时消去两个。',565,486,656,23);
conclude('优先选 C 的中心波矢，用同初始宽度的 A、B 波包作对照。');

start('初始波包：中心附近的一片波矢参与叠加','σ=6a，Jᵧ=Jₓ。kₓ₀、kᵧ₀ 为中心波矢，σ 为初始 RMS 宽度，式中系数保证总概率为1。',
 commonNotes+'Gaussian振幅用物理x,y,sigma表示，无格点编号及替换宽度。归一化常数N只保证总概率1。谱宽Delta kx=Delta ky约1/(2sigma)=1/(12a)。背景高斯曲率范围正负.3，等高线为FFT谱功率相对峰值.1,.5,.9。');
await g('eq_initial',49,112,1180,108);
await g('g05_spectral_support',39,237,1200,310);
note('每幅图的原点是各自中心波矢。黑圈显示主要谱分布，绿线表示零曲率。\n谱宽 Δkₓ=Δkᵧ≈1/(2σ)=1/(12a)，从内到外黑圈为谱峰值的 90%、50%、10%。',48,554,1182,21);
conclude('波包包含中心附近的一片波矢，中心曲率为零并不代表整片频谱曲率都为零。');

start('相同初始包络，不同载波波纹','σ=6a，Jᵧ=Jₓ，t=0　A₀=max|ψ(x,y,0)|，色标 Reψ/A₀ 固定',
 commonNotes+'初始概率分布完全相同，只改变中心波矢。A0为共同初始振幅峰值。每个像素为实际格点，未插值。P0=A0²。Repsi不表示固定单磁子数态的横向自旋均值。');
await g('g06_initial_carriers',39,130,1200,382);
block('包络相同','三组初始概率均为同一个高斯分布。\n每个方向的初始 RMS 宽度为 6a。',49,533,573,22);
block('载波不同','中心波矢改变格点间的相位。\nReψ 显示波峰波谷，P 显示概率。',663,533,567,22);

start('末态概率比较：在各自质心附近观察展宽',main+'，t=180ℏ/Jₓ',
 commonNotes+'均在各自质心坐标显示，不缩放宽度，不逐图重标峰值。共同P0=maxP(x,y,0)。虚线半径2sigma。数值宽度及F均沿用验证数据，物理单位显式补齐。');
await g('g07_final_probability',39,117,1200,376);
table([['t=180ℏ/Jₓ','A 普通点','B 零曲率线','C 零曲率交点'],['(σₓ/a, σᵧ/a)',...keys.map(k=>`(${metric(k,'wx')}, ${metric(k,'wy')})`)]],48,512,1180,89,[278,300,300,302],23);
conclude('B 仍沿 y 明显展宽，C 在两个方向的有限时间展宽都较弱。');

start('固定坐标中的传播：同时观察平移与展宽',main+'，t=0 至 180ℏ/Jₓ，共 61 帧',
 commonNotes+'主图固定实验室坐标x/a,y/a，范围均为-35至225。每帧不减去质心，不移动坐标轴。虚线为实际概率质心轨迹，原点虚圆为初始半径2sigma。固定共同P0。绘图区每帧包含的概率大于.999，精确阈值见checks_lab_animation.json。PDF只显示GIF首帧。');
await g('g14_lab_probability_animation',43,112,1194,439);
note('坐标范围扩大为 −35a 至 225a，坐标轴保持不动，虚线记录概率质心轨迹。\n终点质心 A≈(115.6a,115.6a)，B≈(179.4a,115.6a)，C≈(179.4a,179.4a)。',48,553,1182,22);
conclude('固定实验室坐标保留整体位移，能够直接比较传播方向、距离与包络展宽。');

start('载波随波包传播：全程视图与局部放大',main+'，t=0 至 180ℏ/Jₓ，共 61 帧',
 commonNotes+'主图使用固定实验室坐标，范围-35a至225a，不减去质心。每个主图左上角另附随质心移动的局部放大，显示局部相位波纹。主图与小图固定共同A0和初始相位，均由实际格点数据绘制。Repsi是复振幅分量而不是固定单磁子态的横向自旋均值。');
await g('g15_lab_real_animation',43,112,1194,439);
note('主图的 x、y 坐标固定，用于观察传播。左上小图随质心移动，用于看清局部波纹。\nReψ 保留同一相位约定和色标，固定单磁子数态的横向自旋均值为零。',48,553,1182,22);
conclude('大范围主图展示整体传播，局部放大保留格点波峰波谷与形变。');

start('用概率宽度衡量两个方向的展宽','σₓ、σᵧ 分别为相对概率质心的 RMS 宽度，初始值均为 6a。',
 commonNotes+'使用完整概率矩，sigma_x²=sum(x-meanx)²P。无初始chirp时独立检查位置方差随物理时间的关系sigma_i²(t)=sigma_i²(0)+Var(v_i)t²。图横轴数值单位hbar/Jx。');
chart(series(keys,'wx',labels),37,135,592,367,'x 方向 RMS 宽度',{xLabel:timeAxis,yLabel:'σₓ/a',xMin:0,xMax:180,xStep:60,yMin:6,yMax:14,yStep:2},'rms_x');
chart(series(keys,'wy',labels),650,135,592,367,'y 方向 RMS 宽度',{xLabel:timeAxis,yLabel:'σᵧ/a',xMin:0,xMax:180,xStep:60,yMin:6,yMax:14,yStep:2},'rms_y');
note('x 图中 B 与 C 重合，y 图中 A 与 B 重合。\nC 在 t=180ℏ/Jₓ 时两个方向宽度均为 6.064a，比初始宽度增加约 1.07%。',50,540,1181,24);
conclude('相同初始宽度、相同传播时间的比较支持交点附近的有限时间低展宽设计。');

start('保形还需比较完整复振幅','F(t) 是波包与“按自身平均速度平移的初态”的重叠平方。',
 commonNotes+'参考态psi_ref(x,y,t)=psi(x-meanvx*t,y-meanvy*t,0)，平移使用谱相位实现。F包括相位，不只是概率形状重叠。上图扣除平移相位与共同谱平均相位，范围正负3rad。参考态与演化态使用同一晶格归一化，F对整体相位不敏感。');
await g('g12_phase_budget',44,111,1189,195);
await g('eq_reference',169,309,970,78);
chart(series(keys,'fidelity',labels),45,399,734,214,'相对平移初态的重叠 F(t)',{xLabel:timeAxis,yLabel:'F(t)',xMin:0,xMax:180,xStep:60,yMin:.5,yMax:1,yStep:.25,yFormat:'0.00'},'fidelity_main');
table([['t=180ℏ/Jₓ','F(t)'],...keys.map((k,i)=>[labels[i],metric(k,'fidelity',4)])],816,406,411,200,[270,141],20);
conclude('C 的剩余谱相位较小，F≈0.9965。该结论对应当前初宽与传播时间。');

start('频宽设计：较宽初态可以延长保形时间','C 点 (kₓ₀,kᵧ₀)=(π/(2a),π/(2a))，Jᵧ=Jₓ，1024×1024 格点',
 commonNotes+'不同初始概率宽度4a、6a、8a，比较到t=360hbar/Jx。初始空间资源不同，不是同初宽对照。Delta k在每方向是1/(2sigma)，表中数值单位1/a。');
const ck=['C_sigma4','C_sigma6','C_sigma8'];
chart(series(ck,'fidelity',['σ=4a','σ=6a','σ=8a']),39,137,761,388,'同一中心波矢，不同初始宽度',{xLabel:timeAxis,yLabel:'F(t)',xMin:0,xMax:360,xStep:120,yMin:.88,yMax:1,yStep:.04,yFormat:'0.00'},'fidelity_width');
table([['初宽 σ/a','谱宽 Δk\n单位 1/a','F(360ℏ/Jₓ)'],...ck.map(k=>[String(cases[k].sigma_a),(1/(2*cases[k].sigma_a)).toFixed(4),metric(k,'fidelity',4)])],812,162,422,261,[120,144,158],19);
note('Δkₓ=Δkᵧ≈1/(2σ)。\n较宽初态占用更大的空间范围，\n对应更窄频谱与更小的高阶形变。',823,469,400,22);
conclude('初步设计需要同时选择中心波矢与初始宽度，比较时明确所用空间资源。');

start('零曲率交点仍保留三阶色散','中心 (π/(2a),π/(2a))，Jᵧ=Jₓ，σ=4a。展开式省略五阶及更高阶项。',
 commonNotes+'下面为交点处展开：减去常数Jx+Jy及线性项Jx*a(kx-pi/(2a))+Jy*a(ky-pi/(2a))，得到三次项-a³[Jx(kx-pi/(2a))³+Jy(ky-pi/(2a))³]/6。余项为五阶及以上。图用完整能带模拟，不是三阶截断。独立sigma4控制，区别于主比较sigma6。');
await g('eq_cubic',49,113,1180,125);
await g('g09_higher_order_limit',38,258,1202,331);
conclude('二阶项消失后仍保留三阶项，有限带宽波包在更长时间内仍会偏斜和展宽。');

start('减小纵向交换，调节剩余的 y 向色散','B 点 (kₓ₀,kᵧ₀)=(π/(2a),0.7/a)，σ=6a，t=180ℏ/Jₓ',
 commonNotes+'只改Jy/Jx从1到.3，B中心固定。对物理ky的二阶导数为Jy*a² cos.7。Jy降低同时降低y平均群速度和速度方差，固定时间比较不等于固定行进距离。均速数字的单位Jx*a/hbar。');
await g('g10_anisotropic_design',35,124,777,337);
chart(series(['B_eta1','B_eta03'],'wy',['Jᵧ=Jₓ','Jᵧ=0.3Jₓ']),826,139,413,319,'y 方向宽度',{xLabel:timeAxis,yLabel:'σᵧ/a',xMin:0,xMax:180,xStep:60,yMin:6,yMax:14,yStep:2},'anisotropy_rms');
note('Jᵧ=0.3Jₓ 时，末态 σᵧ=6.913a，F=0.9597。\ny 向平均速度同时由 0.642Jₓa/ℏ 降为 0.193Jₓa/ℏ，传播方向也改变。',51,508,1177,24);
conclude('减小 Jᵧ 可以减弱剩余的 y 向色散，设计还需满足目标传播方向与距离。');

start('波包初步方案与下一步检验','当前范围：均匀、零外场、无耗散的自旋 1/2 铁磁单磁子模型',
 commonNotes+'本轮仅统一符号与物理单位，保留原18页主线和全部数值。完成曲率解析、3x3BZ、9组受控模拟。原数据与原理PDF保留。实际材料、阻尼、制备、等距离优化仍为后续。');
table([['设计环节','当前初步方案','依据与边界'],['中心波矢','优先 (kₓ₀,kᵧ₀)=(π/(2a),π/(2a))','两个方向的能带二阶导数同时为零'],['初始宽度','先取 σ=6a，可扩展至 8a','较窄频谱减小高阶形变，初态占用空间更大'],['本阶段传播','Jᵧ=Jₓ，主比较至 t=180ℏ/Jₓ','σ=6a 时 F≈0.9965，宽度增加约 1.07%'],['继续调节','交换比 Jᵧ/Jₓ、宽度与传播距离','检查高阶色散、边界与实际材料参数']],47,130,1185,320,[193,437,555],21);
block('已完成','解析曲率、扩展能带图和 9 组受控模拟。\n完整色散演化与扩大盒检查相互核验。',50,491,576,22);
block('下一阶段','给定目标距离和初态空间范围，\n优化保形程度并加入实际制备与耗散。',668,491,557,22);
conclude('当前方案支持有限时间的低展宽传播，尚不构成永久无色散波包。');

if(P.slides.items.length!==19)throw new Error('Expected 19 slides');
await fs.writeFile(BUILD+'/slide_spec.json',JSON.stringify(specifications,null,2),'utf8');
await fs.writeFile(BUILD+'/deck.proto.json',JSON.stringify(P.toProto()),'utf8');
for(let i=0;i<P.slides.items.length;i++){
 const b=await P.export({slide:P.slides.items[i],format:'png',scale:1.5});
 await fs.writeFile(BUILD+`/renders/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await b.arrayBuffer()));
 console.log('Rendered',i+1,'/19');
}
const revision=process.argv.find(x=>x.startsWith('--revision='))?.split('=')[1]??'1';
const candidate=BUILD+`/candidate-r${revision}.pptx`;
await(await PresentationFile.exportPptx(P)).save(candidate);
const release=`中期报告_统一符号与传播优化版-r${revision}.pptx`;
const result=await finalizePresentation({workspaceDir:WORK,candidatePath:candidate,finalPath:OUTPUT+'/'+release,
 pythonExecutable:PYTHON,integrityValidatorPath:SKILL+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:SKILL+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--expected-slide-count','19','--validate-heading-fit','--validate-bullet-geometry',
 ...[...new Set(nativeTables)].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeChartOwnerSlides:[...new Set(nativeCharts)],requiredNativeTableOwnerSlides:[...new Set(nativeTables)],
 materializeLiteralChartWorkbooks:true,nativeChartTargetApplication:'powerpoint',
 fontPolicy:{basis:'design',families:[font,mathFont]},verifyArtifactToolImport:true,
 receiptPath:BUILD+`/validation-r${revision}.json`});
await fs.writeFile(BUILD+'/build_result.json',JSON.stringify({revision,release,slides:19,charts:nativeCharts,tables:nativeTables,finalizer:result},null,2));
console.log('FINAL',OUTPUT+'/'+release);

