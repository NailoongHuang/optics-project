# 自旋波时空波包：老师指导原文与课题依据

保存日期：2026-10-21（Asia/Shanghai）。会议本身的日期未在所提供内容中明确。

来源：用户在当前对话中提供的 WeMeet 会议记录及随后给出的研究要求。当前没有原始录音或经过发言人确认的逐字稿。下面完整保留用户提供的文本；其中包括会议秘书的总结、评价性文字，以及用户随附的问题。

## Research authority and preservation

- This file is the canonical project source for the supervisor's guidance on spin-wave space-time wave packets. Read it before planning, resuming, or redirecting this topic.
- Follow the research direction explicitly reaffirmed by the user: frequency–wavevector matching, spin-wave space-time wave-packet construction, and literature-based assessment of originality and paper potential.
- Preserve the supplied source text. Keep interpretations, scientific qualifications, and subsequent decisions outside the original-text block.
- Treat the supplied meeting notes as a record of guidance, not a verified verbatim transcript. The secretary's evaluations are not established scientific results or independently verified statements by the supervisor.
- Resolve ambiguous physical statements through explicit definitions, derivations, and primary literature while retaining the supervisor's research objective. Do not silently replace this project with Gaussian-width optimization, caustics, backflow, disorder studies, or another topic.
- Later explicit instructions from the user or supervisor may revise the direction. Record the date, source, and affected decisions rather than silently rewriting this record.
- The implementation plan is maintained separately in [paper-research-plan.md](paper-research-plan.md). Planning does not authorize executing the research.

## 用户提供的原文

以下代码块保留原文，包括原有反斜杠、Markdown 标记及纪要评价。

```text
石茉熙向车确认色散特性，车澄清所选点虽无二次项，但存在三次项，并非线性色散，​**​可见两人前期对物理模型的认知存在细微偏差，需先拉齐基础概念​**​。\
随后石茉熙指出扩大频率范围必然引发衍射，并建议车在现有方法上做加法，​**​这其实是在引导对方跳出固有框架，寻找更具创新性的研究切入点​**​。\
针对车对“完美不变”实现难度的疑问，石茉熙点明关键在于让频率与波矢精准匹配，​**​一语道破了物理机制的核心，直接给出了破局的理论抓手​**​。\
WeMeet Secretary12:18\
石茉熙指出实现无衍射的关键在于建立欧米伽与K的匹配关系，并建议车查阅相关文献，​**​这相当于给了核心思路，把具体的推导过程留给学生自己探索​**​。\
随后，石茉熙明确了该研究的学术价值，要求车调研自旋波时空波包的研究现状，若无人做过，即可产出一篇优质小论文，​**​可见导师不仅提供技术指导，更在帮学生提前锚定论文的创新点​**​。\
最终，车准确理解了需重新设置非高斯波包的任务，并确认了后续调研方向，双方顺利结束通话。自旋波时空波包研究研讨\
发言人：石茉熙、车\
主题摘要：本次会议围绕自旋波时空波包的色散特性展开研讨，明确了避免波包发散的色散关系条件，并建议查阅相关文献以评估该研究的创新性与论文价值。\
\
一、自旋波时空波包色散特性研讨\
1\. 非线性色散关系分析\
​​存在高次项色散​​：当前选取的色散点并非完全线性，其二次项虽消失，但仍存在三次项及更高次项。\
​​波包必然发生衍射发散​​：在纯线性色散的假设下，若频率（欧米伽）范围扩大，波包依然会发生衍射发散。\
2\. 避免波包发散的核心条件\
​​需建立频率与波矢的耦合关系​​：若想实现波包在传播过程中的形状不变，必须打破独立的高斯分布，使频率（欧米伽）与波矢（K）满足特定的映射关系。\
​​采用非高斯分布的波包​​：传统的独立高斯分布会导致发散，需重新设计频率与波矢相关的非高斯波包以抑制发散。\
二、研究价值评估与后续建议\
1\. 查阅相关文献确认研究空白\
​​检索无衍射/形状不变相关研究​​：建议查阅关于无衍射或形状不变波包的文献，了解现有理论基础。\
​​确认自旋波时空波包研究现状​​：重点确认在自旋波领域是否有关于时空波包在传播过程中不发散的相关讨论。\
2\. 潜在学术价值评估\
​​具备发表高水平论文的潜力​​：若目前自旋波领域尚未有人做过该方向的时空波包研究，此课题有望产出一篇高质量的小论文。\
三、待办事项\
查阅无衍射或形状不变波包的相关文献，确认自旋波时空波包的研究现状及空白。 @车 你去记录一下，未来的研究方向是这个             这是要我干什么，什么意思
```

## 用户随后明确的规划与保存要求

以下均是用户在本次对话中的直接要求，按出现顺序保存。

> 那你先基于这个做一些最基本的研究，你先拟定最最基础的方案，不要具体去做

> 我是说详细的规划，写在一个md里面，不要做所谓最小闭合，考虑一个paper级别的研究

> 请你按照老师的指导来，这个对话是你研究的bible，务必长期保存

这些要求共同确定当前工作范围：以老师指导为主线，形成足够详细的论文级研究规划并保存原始依据；本轮不启动新的研究计算、仿真、实验或系统文献检索。

## 从原文提取的研究任务

| 编号 | 原文中的依据 | 规划中必须回答的问题 |
|---|---|---|
| T1 | 二次项消失，但仍有三次项及更高项 | 在完整色散关系下，原有波包为什么仍变形？谱关联构造怎样处理这些项？ |
| T2 | 在现有方法上做加法 | 保留已建立的自旋波模型与传播方法，增加频谱结构设计，建立与现有结果的直接比较。 |
| T3 | 让频率与波矢精准匹配 | 匹配关系的数学形式、存在条件、谱几何及其导出的保形性质是什么？ |
| T4 | 重新设置频率与波矢相关的非高斯波包 | 怎样从相关频谱构造实际波形，并说明结构、局域化、归一化和激发方式？ |
| T5 | 查无衍射、形状不变及自旋波时空波包文献 | 哪些机制已有研究？本课题与最近邻工作的实质差异在哪里？ |
| T6 | 评估论文价值 | 需要哪些理论结果、数值证据和物理实现分析才能支撑论文，而不是仅展示一种波形？ |

这里的任务提取是对原文的工作性解释。它不把“非高斯”当作保形的充分条件，不把“扩大频率范围必然衍射”当作无条件定理，也不把纪要中的论文期待当作已经完成的创新性判断。这些物理表述的适用条件需要在沿着原指导开展的研究中澄清。

## 后续指导记录

截至本文件建立时，没有追加的老师答复或新研究结果。后续在此处按日期追加指导来源和决策变化；原文保持不变。

### 2026-10-21：用户授权开始文献研究

> 那就按这个规划开始，先做文献调研，重点查清有没有人通过频率与波矢匹配构造自旋波时空波包，以及我们还能做出什么新的东西，严格围绕老师的指导。

本条将工作从“只拟定规划”推进到文献研究阶段。研究方向保持为上述老师指导；执行进展与文献判断见 [progress.md](progress.md)，不写入原始纪要。

### 2026-10-21：用户要求暂不处理受限论文，继续研究

> 你先别管这篇文章，接着做先

此处“这篇文章”指 PRB 113, 054423（2026）。本阶段暂停追索其全文，继续规划中不依赖该全文的工作；其内容与本课题的重合程度仍未决。后续研究保持老师提出的频率—波矢匹配和自旋波时空波包主线。

### 2026-10-21：用户授权有限波包传播与公平对照

> 那就继续，选一个合适的非等频匹配分支，构造纵横都局域的有限波包，用完整色散做传播模拟，和相同初始尺寸的优化高斯波包比较，看看保形效果和代价到底怎样，严格沿着老师的指导来。

本条授权进入有限初态构造、完整能带传播、同尺寸高斯优化和资源代价分析。结果记录在实验报告与进展文件中，原始老师纪要保持不变。
