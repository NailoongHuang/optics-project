import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile,FileBlob} from '@oai/artifact-tool';
import {applyPresentationChartFont,finalizePresentation} from 'file:///C:/Users/xuanm/.codex/plugins/cache/openai-primary-runtime/presentations/26.1017.11052/skills/presentations/container_tools/artifact_tool_utils.mjs';

const PROJECT='C:/Users/xuanm/Desktop/optics';
const WORK=PROJECT+'/presentations/midterm';
const BUILD=WORK+'/build/compact';
const OUTPUT=WORK+'/output';
const SKILL='C:/Users/xuanm/.codex/plugins/cache/openai-primary-runtime/presentations/26.1017.11052/skills/presentations';
const PYTHON='C:/Users/xuanm/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES='C:/Users/xuanm/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const F=JSON.parse(await fs.readFile(WORK+'/build/data_facts.json','utf8'));
const AS=JSON.parse(await fs.readFile(WORK+'/assets.json','utf8'));
const P=await PresentationFile.importPptx(await FileBlob.load(BUILD+'/source-35slides.pptx'));
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

const DROOT=PROJECT+'/figures/midterm-report/dense-wave';
const DM=JSON.parse(await fs.readFile(DROOT+'/manifest.json','utf8'));
const DD=JSON.parse(await fs.readFile(BUILD+'/dense_chart_data.json','utf8'));
async function wave(id,x,y,w,h){
  const item=DM.items.find(a=>a.id===id);if(!item)throw new Error('Missing wave '+id);
  const ext=item.files.png?'png':'gif';await picture(DROOT+'/'+item.files[ext],x,y,w,h,item.caption,ext==='gif'?'image/gif':'image/png');
  slide.speakerNotes.append('\n波场说明：'+item.caption);
}
function note(s,x,y,w=1185,size=22){txt(s,x,y,w,80,size);}
function traj(names,field,x,y,w,h,title,labels){
  const ss=names.map((name,i)=>({name:labels[i],xValues:DD.cases[name].t,values:DD.cases[name][field],
    line:{fill:colors[i],width:3},marker:{symbol:'none'}}));
  return chart(ss,x,y,w,h,title,{xLabel:'时间 τ',yLabel:field==='cy'?'〈y〉/a':'〈x〉/a',xMin:0,xMax:60,xStep:20,yMin:0,yMax:40,yStep:10},'dense_'+field);
}

// 01. The first visual now shows resolved carrier crests, not an isolated pixel.
start('二维铁磁体中的单磁子传播','中期报告　原理 PDF 与实际格点传播模拟',
 '固定初始相位并去除E_F公共相位。主波场采用512×512周期盒、初始概率RMS宽度10a。左侧局部图和右侧真实格点样本表现振幅波峰波谷，N改变盒长而不是晶格常数。');
txt('交换作用、色散与波包的移动和展宽',47,113,1180,43,28,{color:C.blue,bold:true});
await wave('w06_lattice_sampling',42,178,1192,353);
await formula('dispersion',132,556,1022,87);

// 02. Compress the microscopic route while retaining its basis and energy meaning.
start('库仑交换、能级分裂与自旋耦合','原理 PDF 第 1–3 页，式 (2)、(3)、(11)、(14)、(20)',
 '固定正交轨道a,b，各占据一个电子；只保留直接库仑交换。矩阵基底依次为↑↑、↑↓、↓↑、↓↓。反平行积态的对称与反对称组合给出D−K和D+K。矩阵匹配得到J=2K。');
note('固定轨道，各有一个电子。矩阵基底：↑↑、↑↓、↓↑、↓↓。',47,113,1180,21);
await formula('direct_exchange',43,164,650,141);
await formula('coulomb_matrix',65,328,585,235);
chart([{name:'三重态',xValues:[.05,.45],values:[-1,-1],line:{fill:C.blue,width:5},marker:{symbol:'none'}},
       {name:'单重态',xValues:[.55,.95],values:[1,1],line:{fill:C.rust,width:5},marker:{symbol:'none'}}],735,150,500,260,'交换引起的能级分裂',
       {hideX:true,xMin:0,xMax:1,yMin:-1.5,yMax:1.5,yStep:.5,yLabel:'(E − D)/K'});
await formula('heisenberg_pair',723,429,506,83);
math('J = 2K',751,535,400,52,38);
conclude('K > 0 时三重态更低；去掉共同能量常数后，得到铁磁 Heisenberg 交换。');

// 03. Keep the small lattice only as an explicitly labeled model inset.
start('晶格模型与单翻转子空间','原理 PDF 第 3–4 页，式 (22)、(25)、(26)、(29)　A01 局部示意',
 '图中5×5只是局部交换晶格示意，中心额外标出单翻转。全极化基态所有自旋沿+x。单翻转空间在H作用下精确闭合。每条键计一次。');
await formula('lattice_H',65,121,1140,76);
await fig('a01-lattice',38,211,564,350);
await formula('oneflip_action',630,217,602,117);
await formula('state_expansion',631,365,600,81);
await formula('ground_energy',711,481,422,72);
note('左图为局部模型示意；数值波场保留全部格点。',47,573,1175,21);
conclude('单翻转态的叠加始终留在同一子空间，能够精确计算其概率振幅。');

// 04. Equation-to-dispersion chain, without an extra slide for each substitution.
start('运动方程与单磁子色散','原理 PDF 第 4–5 页，式 (28)、(35)–(39)　本页沿用 ℏ = 1',
 '每条含翻转的键产生−Jij/2的相邻位置振幅。平面波移动一个格点只改变相位。正反方向指数相加为2cos，得到余弦色散。');
await formula('lattice_eom',72,125,1125,151);
await formula('plane_wave',65,300,625,79);
note('最近邻位移只产生相位因子。\n两个相反方向合并成为余弦项。',762,307,460,23);
await formula('neighbors',66,408,1142,65);
await formula('dispersion_derivation',73,495,1120,110);
conclude('相对基态的激发能决定传播；共同的基态能量仅改变整体相位。');

// 05. Geometry and derivative interpretation on one page.
start('色散的斜率决定群速度','色散 ε/Jₓ = 1−cos qₓ+η(1−cos qᵧ)，q = ka，η = Jᵧ/Jₓ',
 '图为沿x轴的能量与群速度。空间各向异性使uy=eta sin qy，群速度一般不平行于q。单点激发包含整个能带，不能用单一箭头描述。');
math('e = ε/Jₓ',48,111,220,43,25);math('q = ka',285,111,175,43,25);
math('τ = Jₓt/ℏ',465,111,260,43,25);math('u = ℏv/(Jₓa)',810,111,410,43,25);
await fig('a07-slope-and-speed',42,171,827,388);
math('u = (sin qₓ, η sin qᵧ)',901,185,330,73,26);
block('速度与方向','群速度是色散的梯度。\nη 改变 y 向传播速度。',901,275,330,22);
block('带宽与长波极限','η = 1 时带宽为 4Jₓ。\n小波矢附近近似抛物面。',901,437,330,22);
conclude('有限频宽波包的精确质心速度由整个频谱加权平均。');

// 06. Observable and phase convention, accompanied by a visibly oscillating field.
start('同一个波包：振幅波纹与概率包络','新波场 W01　512×512，初始 RMS 宽度 10a，q₀=(0.7,0)，τ=30',
 '采用psi=e^{iE_Ft/hbar}c去掉共同基态相位，固定初始相位且不逐帧重定相位。Repsi是此约定下的概率振幅实部，不是固定单磁子数态的横向自旋期望。|psi|²是翻转概率。A0=max|psi(0)|,P0=A0²固定。');
await wave('w01_real_probability',42,118,1194,457);
math('ψ = exp(i',48,582,165,36,24);math('E',185,582,27,36,24);
math('F',202,593,20,24,15);math('t/ℏ)c',219,582,158,36,24);
math('A₀ = max|ψ(0)|，P₀ = A₀²',520,582,700,36,24);
txt('Reψ 用于显示波纹，P 用于概率观测；固定单磁子态的横向自旋均值为零。',48,633,1180,40,21);

// 07. Replace the coarse early-time spot by a resolved nonzero-time interference field.
start('单点激发形成多波矢干涉','新波场 W04　单点翻转，η = 1，τ = 24',
 '单点在波矢空间中权重均匀，含整个能带。热图显示实际格点，无连续插值。实部可正可负而概率非负。Bessel传播核可独立验证单点演化。');
await wave('w04_local_interference',42,118,1194,430);
block('单点初态','ψₘₙ(0)=δₘ₀δₙ₀。\n各个波矢共同参与传播。',49,566,555,22);
block('相干展开','不同路径的振幅相加，\n在空间中形成条纹与旁瓣。',665,566,555,22);

// 08. Keep the two distinct expansion scales in one compact quantitative slide.
start('传播前沿与弹道展宽','单点初态 B07、B09　左图 η=1，右图 η=1、0.3、0',
 'Px为对y求和的边际概率。最大群速度给出主要前沿|x|/a约tau；尾部不严格为零。RMS_x/a=tau/sqrt2，RMS_y/a=eta*tau/sqrt2。原有256与512格点盒比较已验证。');
await fig('b07-spacetime-isotropic',34,124,660,430);
nativeChart('local_flip_rms_y',706,128,530,413,'y 方向 RMS 宽度',
 {xLabel:'时间 τ',yLabel:'σᵧ/a',xMin:0,xMax:40,xStep:10,yMin:0,yMax:30,yStep:10});
math('主要前沿：|x|/a ≈ τ',56,573,570,47,26);
math('σₓ/a = τ/√2；σᵧ/a = ητ/√2',710,573,520,47,25);
conclude('概率宽度与时间成正比；主要前沿和 RMS 宽度是不同的传播尺度。');

// 09. Match source bandwidth examples to the wider carrier-resolved demonstration.
start('Gaussian 包络、频宽与载波周期','C02 图例中的宽度数值为 σ/a；新波场主要采用 σ=10a',
 '这里sigma为物理位置概率的RMS宽度，初态振幅exp[-(x²+y²)/(4sigma²)] exp(ik0.r)。q0=k0a，主波场q0=(.7,0)，沿x周期2pi/.7约8.98a。N只改变盒长，不改变a。');
math('ψ(r,0) ∝ exp[−(x²+y²)/(4σ²)] exp(i k₀·r)',48,112,1182,53,31);
await fig('c02-space-bandwidth',42,187,1194,350);
note('本组主波场：σ=10a，q₀=(0.7,0)，沿 x 每个周期约含 9 个格点。',48,555,1180,24);
conclude('较宽包络容纳更多载波周期；局部视窗与完整格点展示让波峰波谷可辨。');

// 10. Actual carrier profiles are retained, not replaced by a featureless density blob.
start('波纹与包络在共动坐标中的变化','新波场 W03　σ=10a，q₀=(0.7,0)，τ=0、30、60',
 '仅在横坐标减去实际概率质心，没有逐帧旋转复相位。载波相位与包络运动是不同概念，质心位移从P计算。截线显示实际格点样本与包络。');
await wave('w03_comoving_sections',42,116,1194,455);
note('蓝线为 Reψ，橙色实线为当前包络，灰色虚线为初始包络。',48,584,1180,23);
conclude('载波波峰与概率质心不必同速；传播位置与展宽应由概率分布度量。');

// 11. Animation starts with a resolved wave, while a native curve provides a static reference.
start('载波传播与概率质心运动','新波场 W07　σ=10a，q₀=(0.7,0)，η=1',
 'GIF含61个真实演化时刻，固定色标与坐标。右侧质心轨迹来自新512格点模型保存的概率矩。平均速度.643412918，与sin(.7)=.644217687的差来自有限频宽。');
await wave('w07_wave_probability_animation',37,140,795,390);
traj(['x_eta1'],'cx',846,143,392,345,'概率质心', ['σ = 10a']);
note('谱平均速度 ūₓ = 0.643413\nτ=60 时 〈x〉=38.6048a',856,520,371,22);
conclude('动画同时展示 Reψ 和 P，定量位移使用 P 的质心。');

// 12. Width and its controlled dependence, avoiding separate near-duplicate pages.
start('初始宽度如何影响展宽','q₀=(0.7,0)，η=1　左：σ=4a；右：σ=3a、6a、10a',
 '左图是原有sigma4a的共动边际，右图比较3a/6a/10a的相对RMS宽度。初始空间资源不同，应把结果解释为频宽规律，不是同资源性能排名。');
await fig('c07-comoving-marginals',37,137,741,353);
nativeChart('width_relative',800,136,437,359,'相对初始宽度',
 {labels:{'sigma=3':'σ=3a','sigma=6':'σ=6a','sigma=10':'σ=10a'},xLabel:'时间 τ',yLabel:'σₓ(τ)/σₓ(0)',xMin:0,xMax:60,xStep:20,yMin:1,yMax:3,yStep:.5});
table([['初始 RMS 宽度/a','3','6','10'],['σₓ(60)/σₓ(0)','2.718','1.185','1.026']],47,530,1185,78,[330,285,285,285],22);
conclude('更窄频谱通常带来更小的相对展宽，同时需要更大的初始空间范围。');

// 13. Resolved diagonal carrier fronts in two exchange environments.
start('各向异性改变波包的传播方向','新波场 W05　σ=10a，q₀=(0.7,0.7)，τ=60',
 '波矢的方向都是45度，但平均群速度方向分别45度和arctan(.3)=16.699度。深色箭头表示实际概率质心位移。Repsi只作波纹显示，不能把条纹法线直接当作各向异性下的群速度方向。');
await wave('w05_anisotropic_waves',42,117,1194,449);
note('相同载波方向 45°；包络传播方向随 η 从 45° 改变到 16.70°。',49,580,1180,24);
conclude('中心附近，条纹法线近似平行 q₀；包络轨迹由谱平均群速度决定。');

// 14. Animation and a trajectory distinguish phase-front and packet motion.
start('方向变化的动态与定量对照','新波场 W08　η=1 与 0.3，σ=10a，q₀=(0.7,0.7)',
 '两组初态相同，只有Jy改变。动画使用固定实部色标，未逐帧峰值归一化。y质心来自保存的概率分布，tau60分别38.6048a和11.5814a。');
await wave('w08_anisotropy_animation',38,139,795,411);
traj(['diagonal_eta1','diagonal_eta03'],'cy',848,145,390,340,'y 方向的概率质心',['η = 1','η = 0.3']);
note('τ=60：\nη=1：〈y〉=38.6048a\nη=0.3：〈y〉=11.5814a',855,511,378,21);
conclude('降低 y 向交换会减小 y 向位移；它不改变初始载波的波矢方向。');

// 15. The physical mechanism is paired directly with the relevant spectrum evidence.
start('展宽来自速度差与相对相位积累','C12：σ=4a 的相位示例　e=ε/Jₓ，τ=Jₓt/ℏ',
 '左图谱概率保持不变，右图扣去常数与线性平移相位后仍有高阶残差。无啁啾Gaussian的初始位置-速度协方差为零，方差律成立；一般初态还要加协方差项。');
await fig('c12-spectrum-phase',43,116,1193,362);
math('Var[n(τ)] = Var[n(0)] + τ² Var(u)',54,499,1175,55,31);
note('n=x/a，逐方向使用。该式适用于初始位置—速度协方差为零的 Gaussian。\n各模式权重不变，相对相位仍改变实空间轮廓；动力学本身保持线性。',51,566,1180,21);

// 16. One controlled extension, explicitly bounded in time and initial size.
start('零二阶曲率点的有限时间保形探索','C13　两组初始 RMS 宽度均为 3a，η=1',
 '普通中心(.7,.7)与(pi/2,pi/2)同初宽比较。F是与按各自平均速度平移的初态的复态重合模平方，含相对相位差。二阶曲率cos q=0仍留三阶色散，不能宣称永久保形。');
math('∂²e/∂qₓ² = cos qₓ，∂²e/∂qᵧ² = η cos qᵧ',49,107,1180,38,24);
nativeChart('inflection_width',40,147,577,323,'RMS 宽度',
 {xLabel:'时间 τ',yLabel:'σₓ/a',xMin:0,xMax:60,xStep:20,yMin:3,yMax:9,yStep:2});
nativeChart('inflection_fidelity',655,147,580,323,'相对平移参考态的重合度',
 {xLabel:'时间 τ',yLabel:'F',xMin:0,xMax:60,xStep:20,yMin:0,yMax:1,yStep:.25,yFormat:'0.00'});
txt('F = |〈ψ平移参考 | ψ(τ)〉|²，包含相对相位变化。',51,500,1181,42,25);
txt('τ=60：普通中心 F=0.3823；零曲率点 F=0.9771。',51,558,1181,42,25,{bold:true,color:C.blue});
conclude('二阶项消失可以减慢形变，高阶色散仍限制可用的保形时间。');

// 17. Summarize independent evidence without a long technical appendix.
start('数值结果的独立核验','左：B13 解析核对照　右：新增密集波场 checks.json',
 '左图是原有FFT与Bessel核比较。右表使用新增512波场的实际误差记录，N512到1024是相同a下的扩大盒检查。N增加不改变载波每波长格点数。');
await picture(BUILD+'/bessel-left.png',38,127,746,390,'FFT 与 Bessel 解析传播核的边际概率对照');
table([['新增波场检查','最大误差'],['归一化','1.33×10⁻¹⁵'],['512→1024 末态振幅','L∞ < 5.82×10⁻¹⁷'],['点激发 Bessel 振幅','L∞ ≈ 2.10×10⁻¹⁶']],813,156,422,292,[218,204],19);
note('真实格点直接显示，无连续插值。\n固定色标与相位约定，全程不按峰值重标度。',55,542,1172,23);
conclude('扩大盒、独立传播核与概率矩共同检查当前模型和时间范围内的计算。');

// 18. Close on the physical results, not production details.
start('物理认识与后续研究','理论：原理 PDF 第 1–5 页　模拟：A/B/C 与 dense-wave 数据',
 '本报告仅建立均匀、零外场、无耗散、单磁子模型中的传播图像。真实材料参数、阻尼以及多磁子相互作用需要后续扩展。当前零曲率结论是有限时间效果。');
table([['原理与证据','物理认识'],
 ['库仑矩阵与 J=2K','交换作用耦合相邻翻转位置'],
 ['余弦色散与群速度','色散斜率控制运动方向与速度'],
 ['Reψ、概率和共动剖面','载波波纹、质心移动和包络展宽可以分别观察'],
 ['等初宽的零曲率对照','有限时间形变减弱，高阶残差仍然存在']],46,133,1187,312,[430,757],24);
block('下一步','以给定初始宽度为约束，比较保形距离与高阶色散。',49,492,560,24);
block('适用范围','均匀晶格、单磁子、零外场、无耗散；材料实现仍需具体参数。',668,492,560,24);

if(P.slides.items.length!==18)throw new Error('Expected 18 slides including cover');
await fs.writeFile(BUILD+'/slide_spec.json',JSON.stringify(specifications,null,2),'utf8');
await fs.writeFile(BUILD+'/deck.proto.json',JSON.stringify(P.toProto()),'utf8');
for(let i=0;i<P.slides.items.length;i++){
  const b=await P.export({slide:P.slides.items[i],format:'png',scale:1.5});
  await fs.writeFile(BUILD+`/renders/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await b.arrayBuffer()));
  console.log('Rendered',i+1,'/18');
}
const revision=process.argv.find(x=>x.startsWith('--revision='))?.split('=')[1]??'1';
const candidate=BUILD+`/candidate-r${revision}.pptx`;
await(await PresentationFile.exportPptx(P)).save(candidate);
const release=revision==='1'?'中期报告_18页优化版.pptx':`中期报告_18页优化版-r${revision}.pptx`;
const result=await finalizePresentation({workspaceDir:WORK,candidatePath:candidate,finalPath:OUTPUT+'/'+release,
 pythonExecutable:PYTHON,integrityValidatorPath:SKILL+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:SKILL+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--expected-slide-count','18','--validate-heading-fit','--validate-bullet-geometry',
 ...[...new Set(nativeTables)].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeChartOwnerSlides:[...new Set(nativeCharts)],requiredNativeTableOwnerSlides:[...new Set(nativeTables)],
 materializeLiteralChartWorkbooks:true,nativeChartTargetApplication:'powerpoint',
 fontPolicy:{basis:'design',families:[font,mathFont]},verifyArtifactToolImport:true,
 receiptPath:BUILD+`/validation-r${revision}.json`});
await fs.writeFile(BUILD+'/build_result.json',JSON.stringify({revision,release,slides:18,charts:nativeCharts,tables:nativeTables,finalizer:result},null,2));
console.log('FINAL',OUTPUT+'/'+release);

