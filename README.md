# Optics：自旋波研究工作区

从本页进入。各专题 README 维护自己的当前状态、下一步与证据索引；同一主题的讨论持续更新同一份记录。

| 要找什么 | 入口 |
| --- | --- |
| 老师指导下的主课题：频率—波矢关联与时空波包 | [研究入口](research/spin-wave-spacetime-wavepackets/README.md) |
| 当前单磁子推导及可编辑源 | [讲义 PDF](Note/single_magnon_derivation/main.pdf) · [TeX](Note/single_magnon_derivation/main.tex) |
| 中期汇报的当前版本、预览与编辑入口 | [汇报说明](presentations/midterm/README.md) |
| 完整色散、波包传播图像与数据 | [图像与计算资料](figures/midterm-report/README.md) |
| 基础模型与回归检查 | [代码说明](code/README.md) |
| 文献与阅读线索 | [文献目录](literature/collection-completion-2026-10-21/README.md) |
| 既有四项探索测试 | [历史测试与 Demo](research/wavepacket-prospects/README.md) |
| 自旋波类比引力灵感 | [原话与讨论记录](research/ideas/2026-10-25-spin-wave-analogue-gravity.md) |
| 2026-10-21 研究整理报告 | [报告与来源说明](deliverables/spin-wave-study-2026-10-21/00_先读这里.md) |

统一维护规则在 [AGENTS.md](AGENTS.md#research-record-maintenance)。新讨论、推导、测试与草稿放在所属专题；已有绑定程序路径和校验和的材料保持原位。保留原始指导、失败与负结果，用链接连接资料。

仓库为 [NailoongHuang/optics-project](https://github.com/NailoongHuang/optics-project)。日常核对：

```powershell
python admin/maintenance/check_workspace.py
python -m unittest discover -s code -v
git status --short --branch
```

研究模拟按项目规则放在 Ubuntu/WSL；Windows 保存展示成果和可编辑源。上述单元测试用于现有基础教学模型。

[本次整理与文件去向](admin/maintenance/README.md) · [历史导航和审阅档案](admin/archive/README.md)
