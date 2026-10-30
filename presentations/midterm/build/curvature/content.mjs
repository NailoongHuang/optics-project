const GROOT=PROJECT+'/figures/midterm-report/curvature-design';
const GM=JSON.parse(await fs.readFile(GROOT+'/manifest.json','utf8'));
const GD=JSON.parse(await fs.readFile(GROOT+'/chart_data.json','utf8'));
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
const main='新模拟：σ=6a，η=1，512×512 格点，完整余弦色散';
const units='q = ka，e = ε/Jₓ，η = Jᵧ/Jₓ > 0，τ = Jₓt/ℏ，n = r/a';
const commonNotes='精确FFT谱演化psi(t)=IFFT[FFT(psi0)exp(-i e tau)]。固定晶格常数a，增加N只扩大盒长。主比较同初始概率RMS宽度sigma=6a、同时间tau=180，行进距离不同。归一化总概率为1，固定初态相位，移除E_F公共相位。无外场、无耗散的自旋1/2铁磁单磁子模型。';

start('二维单磁子的能带几何与波包设计','中期报告　原理 PDF、曲率解析与波包数值模拟',commonNotes);
txt('从交换模型到零曲率选点与有限时间传播',48,112,1182,44,28,{bold:true,color:C.blue});
await g('g00_cover',665,170,560,430);
await formula('dispersion',42,180,598,115);
block('物理问题','怎样选择载波中心，使二维波包\n在传播中较少展宽？',49,326,577,26);
block('本阶段内容','求解能带高斯曲率，确定候选点，\n用相同初宽的波包检验传播。',49,472,577,25);
conclude('用能带几何提出设计，再用完整色散检验设计的有效时间与限制。');

start('交换模型与单磁子子空间','原理 PDF 第 3–4 页，式 (20)、(22)、(25)、(29)',
 '从原理PDF的直接库仑交换得到J=2K>0。采用自旋1/2，极化方向+x，每条键计一次。单翻转子空间在H作用下精确闭合。局部晶格图仅表示相邻交换，不是模拟分辨率。');
await formula('lattice_H',53,119,1169,78);
await fig('a01-lattice',38,218,514,338);
await formula('oneflip_action',574,226,650,134);
math('|Ψ(t)〉 = Σᵢ cᵢ(t)|i〉，Σᵢ |cᵢ(t)|² = 1',580,401,646,90,29);
note('铁磁交换 J=2K>0。\n全极化基态沿 +x，单次翻转的位置可以相干叠加。',580,520,635,23);
conclude('交换作用使翻转振幅在相邻格点间传播，单磁子空间内可精确求解。');

start('运动方程、色散与传播的计算','原理 PDF 第 5 页，式 (35)–(39)　下方恢复 ℏ 的单位',commonNotes);
await formula('lattice_eom',54,116,1170,133);
await formula('dispersion',63,270,1150,95);
note(units,48,382,1180,24);
note('ψ 去掉 c 中的基态公共相位。波纹比较沿用同一初始相位。',49,427,1170,22);
math('ψ(n,τ) = ℱ⁻¹[ ψ̃(q,0) exp(−i e(q)τ) ]',49,478,1170,58,31);
math('ū = 〈∇e〉谱，P(n,τ) = |ψ(n,τ)|²，ΣₙP = 1',49,548,1170,53,27);
conclude('色散的线性相位控制平移，偏离线性的剩余相位产生展宽与形变。');

start('求解能带图面的高斯曲率','无量纲图面 R=(qₓ,qᵧ,e)　曲率定义：Monge 图面公式',
 '曲率定义采用无量纲欧氏图面R=(qx,qy,e)，下标x,y指对q求导。不同轴尺度改变曲率数值，但在正轴缩放下零点和符号不变。不是Berry曲率。独立第一、第二基本形式推导经SymPy验证残差为零。定义来源 https://mathworld.wolfram.com/GaussianCurvature.html 公式(15)。');
await g('formula_curvature_general',48,125,440,155);
math('eₓ = sin qₓ，eᵧ = η sin qᵧ',548,145,670,53,29);
math('eₓₓ = cos qₓ，eᵧᵧ = η cos qᵧ，eₓᵧ = 0',548,219,670,57,28);
await g('formula_curvature_model',83,322,1107,142);
note('分母始终为正，曲率符号由 cos qₓ cos qᵧ 决定。\n正曲率区、负曲率区与零曲率线可以在整个扩展能带中直接标出。',51,503,1178,25);
conclude('高斯曲率描述能量图面的局部几何，零曲率轨迹来自解析方程。');

start('各向同性：多个布里渊区中的能带与曲率','η=1　qₓ,qᵧ ∈ [−3π,3π]，共 3×3 个布里渊区',commonNotes+
 '左灰度越深能量越大，固定e范围0至4。右红正蓝负，深浅表示曲率绝对值，范围正负1。绿线为解析零曲率，黑虚线框为中心第一BZ。多个BZ只是同一能带的周期延拓。');
await g('g01_multibz_eta1',39,115,1200,493);
conclude('左深色表示高能量，右红正蓝负。绿色为零曲率线，黑虚线围成中心第一布里渊区。');

start('各向异性：曲率幅度改变，零点仍然相同','η=0.3　同一 q 范围与能量色标，右侧曲率色标改为 ±0.3',commonNotes+
 '与eta1相比，eta.3时能带沿qy变平。此页曲率范围正负.3，上页正负1，不可以仅凭色深跨页比较曲率幅值。eta>0时零集合不变。');
await g('g02_multibz_eta03',39,115,1200,493);
conclude('Jᵧ 减小后 y 向色散较弱。两页曲率色标不同，幅值比较应读取色标数值。');

start('严格零曲率位置上的能带分布','η=1　左侧只保留 κ_G=0 线上的能量，右侧为完整曲率图',
 '左图线外空白，不是零能量。使用精确解析轨迹而非阈值筛选。各线上的能量仍然变化，曲率为零不等于能量或群速度为零。扩展3×3BZ展示同一带的周期结构。');
await g('g03_zero_locus_band',39,112,1200,454);
await g('formula_zero',104,570,1072,45);
conclude('零曲率组成两族周期直线，交点同时满足两个方向的二阶导数为零。');

start('波包中心：普通点、零曲率线与交点','H = ∂ᵢ∂ⱼe = diag(cos qₓ, η cos qᵧ)　以下先固定 η=1',
 'H控制局部二次谱相位，其特征值一般不是图面的主曲率。单条线B只有一个H本征值为0，交点C两个均为0。三类中心的区别用于设计比较。');
await g('g04_candidates',34,129,520,446);
table([['中心 q₀','H 的对角元','设计含义'],['A (0.7, 0.7)','(0.765, 0.765)','两个方向有二阶色散'],['B (π/2, 0.7)','(0, 0.765)','仅 x 向二阶项消失'],['C (π/2, π/2)','(0, 0)','两个二阶项同时消失']],565,164,669,277,[237,190,242],20);
note('κ_G=0 只要求 det H=0。\n二维波包的二阶形变还要分别检查 H 的两个方向。',572,484,647,24);
conclude('初步优先选择 C 作为中心，并用 A、B 作为相同初始宽度的受控对照。');

start('初始波包：有限宽度意味着有限频谱','主比较：σ=6a，η=1，三组只改变载波中心 q₀',commonNotes+
 '振幅初态exp[-(nx²+ny²)/(4s²)]exp(iq0.n)，s=sigma/a。sigma为概率在每个方向的RMS。频谱概率RMS约1/(2s)=1/12。背景曲率统一正负.3，红正蓝负，FFT谱等高线为相对峰值.1,.5,.9。');
math('ψ(n,0) = 𝒩 exp[−(nₓ²+nᵧ²)/(4s²)] exp(i q₀·n)，s=σ/a',47,111,1184,57,28);
await g('g05_spectral_support',39,191,1200,353);
note('谱宽 Δq ≈ 1/(2s) = 1/12。等高线为初始谱功率的 0.1、0.5、0.9 倍峰值。\n背景为 κ_G，红正蓝负，统一范围 ±0.3。有限频谱始终覆盖零线附近的区域。',48,550,1182,22);
conclude('选在零曲率中心只是第一步，波包实际占据的整片频谱决定最终形变。');

start('初始设计的实际格点波纹','σ=6a，η=1，τ=0　色标 Reψ/A₀ 固定，总概率为 1',commonNotes+
 'P初态完全相同，区别仅为载波中心。A0=max|psi0|，实部包含正负波峰。每个像素对应实际格点，不作平滑插值。C在两个方向载波周期均4a，A每轴约8.98a。Repsi不是单磁子数态的横向自旋均值，后者为零。');
await g('g06_initial_carriers',39,130,1200,382);
block('包络相同','三组初始概率都为同一个 Gaussian。\n每个方向的 RMS 宽度为 6a。',49,533,573,22);
block('载波不同','A、B、C 具有不同格点相位。\nReψ 显示振幅波纹，P 显示概率。',663,533,567,22);

start('同初宽、同时间：末态概率的二维比较',main+'，τ=180',commonNotes+
 '图中均减去各自实际质心，未缩放宽度，未逐图重标峰值。固定共同P0=maxP(0)。虚线为初始半径2sigma。末态宽度和F均来自完整离散概率矩与谱相位。');
await g('g07_final_probability',39,117,1200,376);
table([['τ=180','A 普通点','B 零曲率线','C 零曲率交点'],['(σₓ/a, σᵧ/a)',...keys.map(k=>`(${metric(k,'wx')}, ${metric(k,'wy')})`)]],48,512,1180,89,[278,300,300,302],23);
conclude('B 仍沿 y 明显展宽，C 在两个方向的有限时间展宽都较弱。');

start('载波波纹在传播过程中的演化',main+'，动画 τ=0–180，共 61 个演化时刻',commonNotes+
 'GIF为61个完整色散演化时刻，Repsi固定色标，各自共动坐标。固定初态相位并移除EF公共相位，没有逐帧重定相位。固定数单磁子态<Sy>=<Sz>=0，<Sx>=1/2-P。动画在静态PDF中只显示首帧。');
await g('g13_real_animation',43,112,1194,439);
note('每个像素表示实际格点，载波实部保留正负波峰。图中减去各自质心位移。\nReψ 是固定相位约定下的振幅分量，固定单磁子数态的横向自旋均值为零。',48,553,1182,22);
conclude('波纹显示格点相位结构，前后形变再结合概率宽度与复振幅重叠衡量。');

start('概率矩量化两个方向的展宽','主比较：相同初宽 6a、相同时间，行进距离并不相同',commonNotes+
 '利用谱平均速度和速度方差独立核验：均值位置=均值速度tau，sigma_i²(tau)=sigma_i²(0)+Var(u_i)tau²，初态无chirp。C在两个方向宽度均6.064309a，tau180均值位置179.376084a。');
chart(series(keys,'wx',labels),37,135,592,367,'x 方向 RMS 宽度',{xLabel:'时间 τ',yLabel:'σₓ/a',xMin:0,xMax:180,xStep:60,yMin:6,yMax:14,yStep:2},'rms_x');
chart(series(keys,'wy',labels),650,135,592,367,'y 方向 RMS 宽度',{xLabel:'时间 τ',yLabel:'σᵧ/a',xMin:0,xMax:180,xStep:60,yMin:6,yMax:14,yStep:2},'rms_y');
note('x 图中 B 与 C 重合，y 图中 A 与 B 重合。\nC 在 τ=180 时两个方向宽度均为 6.064a，比初始宽度增加约 1.07%。',50,540,1181,24);
conclude('局部二阶项是否消失，与完整色散下的有限时间展宽形成一致的对应。');

start('保形还需检查剩余谱相位','F 为复振幅与“以自身谱平均速度平移的初态”的重叠平方',commonNotes+
 '定义deltae=e-ubar.q-C0，C0是谱均值，去掉公共相位。F=|sum power exp(-i deltae tau)|²。该指标包含相位，并非只比较概率图像。图上为tau180的剩余相位，统一正负3rad饱和显示。');
await g('g12_phase_budget',44,111,1189,234);
math('δe = e−ū·q−〈e−ū·q〉谱，F(τ) = |〈exp(−iδeτ)〉谱|²',80,350,1140,40,24);
chart(series(keys,'fidelity',labels),45,389,734,225,'相对平移初态的重叠 F',{xLabel:'时间 τ',yLabel:'F',xMin:0,xMax:180,xStep:60,yMin:.5,yMax:1,yStep:.1,yFormat:'0.00'},'fidelity_main');
table([['τ=180','F'],...keys.map((k,i)=>[labels[i],metric(k,'fidelity',4)])],816,396,411,201,[270,141],22);
conclude('C 的剩余谱相位较小，F≈0.9965。该结论对应当前初宽与传播时间。');

start('频宽设计：较宽初态可以延长保形时间','C 点 q₀=(π/2,π/2)，η=1，1024×1024，τ=0–360',
 commonNotes+'本页是资源变化对照，初始sigma分别4、6、8a，不能说同初宽。初态空间较宽对应谱较窄，高阶相位更小。各自相对自身平移初态计算F，初始总概率同为1。');
const ck=['C_sigma4','C_sigma6','C_sigma8'];
chart(series(ck,'fidelity',['σ=4a','σ=6a','σ=8a']),39,137,761,388,'同一载波中心，不同初始宽度',{xLabel:'时间 τ',yLabel:'F',xMin:0,xMax:360,xStep:120,yMin:.88,yMax:1,yStep:.04,yFormat:'0.00'},'fidelity_width');
table([['初宽 σ/a','Δq≈a/(2σ)','F(360)'],...ck.map(k=>[String(cases[k].sigma_a),(1/(2*cases[k].sigma_a)).toFixed(4),metric(k,'fidelity',4)])],820,162,414,261,[127,154,133],20);
note('较宽的初态需要更大的空间范围，\n换来更窄频谱与更小的高阶形变。',830,471,391,23);
conclude('初步设计需要同时选择中心波矢与初始宽度，比较时明确所用空间资源。');

start('交点仍有三阶色散：更长时间下的形变','C 点，η=1，σ=4a，1024×1024，τ=0、180、360',
 '在C点展开，线性项减去后剩余-(deltaqx³+eta deltaqy³)/6+O(|deltaq|^5)。图为完整余弦演化的概率边际，不是仅由三阶截断求解。sigma4是展示高阶效应的单独控制实验，不能混成主比较sigma6。');
math('e(q₀+δq)−e₀−u₀·δq = −(δqₓ³+ηδqᵧ³)/6 + O(|δq|⁵)',49,115,1180,56,28);
await g('g09_higher_order_limit',38,201,1202,379);
conclude('二阶项消失后仍保留三阶项，有限带宽波包在更长时间内仍会偏斜和展宽。');

start('各向异性作为零曲率线上的辅助调节','B 点 q₀=(π/2,0.7)，相同 σ=6a、τ=180，η=1 与 0.3',
 commonNotes+'此页固定同中心同初宽同时间，Hyy=eta cos .7。eta降低同时降低y平均群速度和y速度方差。不是等行进距离性能比较。eta1的sigma_y12.924a,F.722110，eta.3的sigma_y6.913a,F.959741。');
await g('g10_anisotropic_design',35,124,777,337);
chart(series(['B_eta1','B_eta03'],'wy',['η=1','η=0.3']),826,139,413,319,'y 方向宽度',{xLabel:'时间 τ',yLabel:'σᵧ/a',xMin:0,xMax:180,xStep:60,yMin:6,yMax:14,yStep:2},'anisotropy_rms');
note('η=0.3 时，σᵧ(180)=6.913a，F(180)=0.9597。\ny 向平均速度同时由 0.642 降为 0.193，传播方向也随之改变。',51,508,1177,25);
conclude('减小 Jᵧ 可以减弱剩余的 y 向色散，设计时还需满足目标传播方向与距离。');

start('波包初步方案与下一步检验','当前范围：均匀、零外场、无耗散的自旋 1/2 铁磁单磁子模型',
 commonNotes+'本阶段完成图面曲率解析、3×3扩展BZ图、三类中心对照、宽度控制与各向异性控制。数值检查通过归一化、谱概率矩、扩大盒、曲率差分和周期性。实际材料参数、阻尼、多磁子和制备需要后续工作。等距离的优化尚未完成。');
table([['设计环节','当前初步方案','依据与边界'],['中心波矢','优先 C=(π/2,π/2)','两个方向二阶色散同时为零'],['初始宽度','先取 σ=6a，可扩展至 8a','较窄频谱减少高阶相位，初态占用空间更大'],['本阶段传播','η=1，τ≤180 的主比较','σ=6a 时 F(180)=0.9965，宽度增加约 1.07%'],['调节与检验','结合 η、宽度、传播距离继续优化','明确比较条件，检查三阶项、边界与真实材料参数']],47,130,1185,320,[193,407,585],22);
block('已完成','解析曲率、扩展能带图和 9 组受控模拟。\n完整色散演化与扩大盒检查相互核验。',50,491,576,22);
block('下一阶段','给定目标距离和初态空间范围，\n优化保形程度并加入实际制备与耗散。',668,491,557,22);
conclude('当前方案支持有限时间的低展宽传播，尚不构成永久无色散波包。');

if(P.slides.items.length!==18)throw new Error('Expected 18 slides');
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
const release=`中期报告_能带曲率与波包设计-r${revision}.pptx`;
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
