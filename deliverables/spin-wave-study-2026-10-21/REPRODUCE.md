# 复现说明

## 直接查看

PDF、PNG、SVG、GIF 和 PPTX 成品可直接打开。离线 HTML 使用同目录下的图片与动画，不需要联网下载界面库。

## Python 计算

在仓库根目录打开终端。下面的依赖文件保留 2026-10-21 环境版本：

```powershell
python -m pip install -r deliverables/spin-wave-study-2026-10-21/requirements-science.txt
python -m unittest discover -s code -v
```

四个历史测试的原始入口如下。后续实质性研究计算按 [AGENTS.md](../../AGENTS.md) 使用 Ubuntu/WSL 工作区；这些命令用于识别已有程序及其作用范围：

```powershell
python research/wavepacket-prospects/demos/finite-source-caustic/run.py
python research/wavepacket-prospects/demos/backflow-resolution/run.py
python research/wavepacket-prospects/demos/loss-aware-pulse/run.py
python research/wavepacket-prospects/demos/transport-disorder/run.py
```

程序可能覆盖自己的派生数据和图像。若要保留交付时的结果，请先复制一份资料包再重算。

## 讲义与汇报

讲义使用 XeLaTeX 和 `ctexart`。当前 TeX 源文件与相应 PDF 都已保留。

PowerPoint 成品可以独立查看和编辑；其构建脚本使用本机 Codex 的 artifact-tool 运行时，并含绝对项目路径。安装依赖没有打入资料包，换机器重建需要重新配置这些路径。`presentations/midterm/build` 中的编辑源和历史源稿保留，不要把整个目录当成缓存删除。

部分绘图和检查脚本使用 Windows 中文字体路径。换系统时可替换为可用的中文字体。

## 文件核对与报告源

`manifest.json` 和 `inventory.csv` 保留原快照的路径、大小与 SHA-256。本目录不再重复整套工作区；路径归并见[维护记录](../../admin/maintenance/README.md)。

报告的文字、插图和 PDF 生成脚本保留在 `report/`。需要重建报告时，从仓库根目录指定输出文件：

```powershell
python deliverables/spin-wave-study-2026-10-21/report/build_report.py --output report-rebuilt.pdf
```

原 `package_delivery.py` 已作为历史工具归档。日常改动通过 Git 记录；仓库结构核对使用 `python admin/maintenance/check_workspace.py`。换机器重建汇报时需按汇报 README 配置可用的 authoring runtime。
