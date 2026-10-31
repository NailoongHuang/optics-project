# 自旋波时空波包：研究入口

本专题围绕老师提出的频率—波矢关联、时空波包构造与论文研究展开。[老师指导原文](teacher-dialogue.md)长期保留为课题依据；方法与阶段安排见[研究规划](paper-research-plan.md)。本页是本专题当前状态与后续问题的唯一维护入口。

## 当前记录

本页于 2026-10-30 根据既有文件整理；科学结果沿用各自原记录的日期。本次只做仓库维护。

| 部分 | 已有材料与状态 |
| --- | --- |
| 文献调研 | [文献与创新性评估](literature-2026-10-21/literature-review.md) · [证据矩阵](literature-2026-10-21/evidence-matrix.json)；最近邻工作的全文重合判断仍有未决项。 |
| 匹配理论 | [完整余弦色散上的谱匹配](theory/matching-foundations/matching-foundations.md) · [代数检查记录](theory/matching-foundations/symbolic-checks.json)。 |
| 有限波包 | [首轮匹配包与同尺寸高斯比较](experiments/finite-matched-packet-2026-10-21/report.md)；保留该谱族的负向结果及资源代价，不推广到所有关联谱。 |
| 实际磁学平台 | 材料、有限激发器与容差验证尚待研究；后续执行按新的具体请求确定。 |
| 决策过程 | [按日期保存的研究历史](progress.md)，包含授权原话、实际工作与后续修正。 |

## 后续问题

1. PRB 113, 054423（2026）的全文获取按既有指示暂停；新颖性判断仍需明确其与本课题的重合范围。
2. 结合现有匹配理论和有限包的负结果，讨论谱构造、局域化及资源约束的下一步选择。
3. 需要继续执行时，先确定具体问题、对照与验证证据，再更新本页。研究规划本身不启动计算。

[自旋波类比引力灵感](../ideas/2026-10-25-spin-wave-analogue-gravity.md)另行保留为候选问题。早期四项探索测试见[原测试记录](../wavepacket-prospects/README.md)。


## Contributed precompensation material (2026-10-31)

[PR #1](https://github.com/NailoongHuang/optics-project/pull/1) supplies a
separate classical Gaussian-packet simulation, authored output figures and
a cubic-phase precompensation derivation. See the
[integration and model notes](../../code/README.md#contributed-classical-precompensation-example-2026-10-31)
and [compensation comparison](../../code/classical_simulation/compensation/20261028_233550/compensation_M2.png).
This is contributed exploratory material for refocusing near a selected time,
not established evidence of continuous shape preservation. Integration used
static source review; no new research simulation was run. Its field convention
and amplitude assumptions remain to be reconciled with the current model.
