# 复现说明

## 直接查看

PDF、PNG、SVG、GIF 和 PPTX 成品可直接打开。离线 HTML 使用同目录下的图片与动画，不需要联网下载界面库。

## Python 计算

在资料包根目录打开终端。下面是当前环境的科学计算依赖记录：

```powershell
python -m pip install -r requirements-science.txt
python -m unittest discover -s code -v
```

四个最新测试可单独运行，不必重建整套图表：

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

## 文件核对与快照更新

`manifest.json` 和 `inventory.csv` 记录每个复制文件的原路径、资料包内路径、大小与 SHA-256。复制后已逐文件比对。

`package_delivery.py` 是整理工具，不是科学计算程序。只有需要从原工作区刷新这个资料包时才使用：

```powershell
python package_delivery.py --source-root C:/Users/xuanm/Desktop/optics
```

它不会删除原文件，不会进入依赖目录或 Windows Junction，也不会更改 `report/` 与报告 PDF。
