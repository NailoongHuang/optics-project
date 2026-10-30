"""Refresh the non-destructive research delivery snapshot and verify its bytes.

This publisher utility preserves source-relative paths and never deletes files.
Use an explicit source root; the bundle destination is this script's directory.
Installed dependencies, reparse points and identified rebuild caches are omitted.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import stat
import zipfile

SCOPE_ROOTS = ("code", "figures", "research", "Note", "literature",
               "presentations", "tmp")
SKIP_DIR_NAMES = {"node_modules", "__pycache__", ".git", ".codex"}
TEX_CACHE_SUFFIXES = {
    ".aux", ".fdb_latexmk", ".fls", ".log", ".out", ".xdv", ".toc",
    ".nav", ".snm", ".vrb", ".synctex.gz",
}
SERIALIZATION_FILES = {
    "presentations/midterm/build/deck.proto.json",
    "presentations/midterm/build/compact/deck.proto.json",
    "presentations/midterm/build/curvature/deck.proto.json",
    "presentations/midterm/build/notation/deck.proto.json",
}
CURRENT = {
    "current_derivation": "Note/single_magnon_derivation/main.pdf",
    "current_derivation_source": "Note/single_magnon_derivation/main.tex",
    "current_presentation": (
        "presentations/midterm/output/中期报告_统一符号与传播优化版.pptx"),
    "current_presentation_preview": (
        "presentations/midterm/output/中期报告_统一符号与传播优化版_预览.pdf"),
    "latest_demo_gallery": "research/wavepacket-prospects/index.html",
    "latest_research_report": "research/wavepacket-prospects/README.md",
    "prior_research_audit": "literature/cosine-lattice-wavepacket-audit/README.md",
    "figure_gallery": "figures/midterm-report/index.html",
    "figure_atlas": "figures/midterm-report/midterm-figure-atlas.pdf",
    "library_catalog": "literature/collection-completion-2026-10-21/README.md",
}
SCIENTIFIC_PACKAGES = ("numpy", "scipy", "matplotlib", "pillow", "sympy",
                       "mpmath", "pymupdf")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(2**20), b""):
            digest.update(block)
    return digest.hexdigest()


def inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def reparse(path: Path) -> bool:
    info = path.lstat()
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) & flag)


def file_exclusion(relative: str) -> str:
    path = Path(relative)
    if path.suffix.lower() in {".pyc", ".pyo"}:
        return "Python bytecode cache"
    if relative in SERIALIZATION_FILES:
        return "Generated presentation serialization; no read dependency located"
    if relative.startswith("Note/"):
        if any(relative.lower().endswith(suffix) for suffix in TEX_CACHE_SUFFIXES):
            return "TeX rebuild cache; source and PDF are retained"
    return ""


def source_inventory(source: Path):
    """Yield files plus exclusions without entering any reparse directory."""
    for name in SCOPE_ROOTS:
        base = source / name
        if not base.is_dir():
            continue
        if reparse(base):
            yield None, name + "/", "Reparse directory is outside snapshot scope"
            continue
        for directory, dirs, files in os.walk(base, topdown=True, followlinks=False):
            folder = Path(directory)
            retained = []
            for child in sorted(dirs):
                path = folder / child
                relative = path.relative_to(source).as_posix() + "/"
                if child in SKIP_DIR_NAMES:
                    yield None, relative, "Installed dependency or cache directory"
                elif reparse(path):
                    yield None, relative, "Reparse directory; external target not traversed"
                elif not inside(path, source):
                    yield None, relative, "Resolved directory is outside the source root"
                else:
                    retained.append(child)
            dirs[:] = retained
            for child in sorted(files):
                path = folder / child
                relative = path.relative_to(source).as_posix()
                if reparse(path):
                    yield None, relative, "Reparse file; target not copied"
                elif not inside(path, source):
                    yield None, relative, "Resolved file is outside the source root"
                else:
                    reason = file_exclusion(relative)
                    yield path, relative, reason


def copy_verified(source: Path, target: Path, destination: Path) -> tuple[str, bool]:
    if not inside(target, destination):
        raise ValueError(f"Destination escapes delivery root: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        source_hash = sha256(source)
        changed = not target.is_file() or sha256(target) != source_hash
        if changed:
            shutil.copy2(source, target)
        destination_hash = sha256(target)
        if source_hash == destination_hash:
            return source_hash, changed
    raise RuntimeError(f"Source kept changing while copied: {source}")


def write_indexes(destination: Path):
    (destination / "00_先读这里.md").write_text("""# 自旋波研究资料包

先读 [研究整理报告](自旋波研究整理报告.pdf)，再按下面的入口查看原文、代码和成果。

| 要找什么 | 入口 |
|---|---|
| 下载的论文与阅读顺序 | [文献索引](01_文献索引.md) |
| 程序、数据、图表和动画 | [代码与结果索引](02_代码与结果索引.md) |
| 当前讲义、最新汇报和历史版本 | [讲义与汇报索引](03_讲义与汇报索引.md) |
| 四个最新测试 | [离线 Demo 页](research/wavepacket-prospects/index.html) |
| 逐文件来源与核对结果 | [文件清单 CSV](inventory.csv) · [机器可读清单](manifest.json) |
| 安装环境与复现提示 | [复现说明](REPRODUCE.md) |

资料按原路径保存，方便程序找到相邻数据。`code`、`figures`、`research`、`Note`、`literature`、`presentations` 是工作内容；`tmp` 保存早期草稿和审阅记录。`report` 保存本报告的可编辑文字、插图和生成脚本。

当前推导是 `Note/single_magnon_derivation/main.pdf`。当前汇报是“统一符号与传播优化版”，共 19 页。早期 toy model 笔记和其他汇报版本保留供追溯，不是默认入口。

没有复制安装依赖、Python／TeX 缓存和四个大型中间序列化文件。原工作区中的这些文件没有被移动或删除。完整排除说明在 `manifest.json`。

本轮整理修正了 `code/README.md` 的版本说明：当前单磁子推导与两份旧 toy model 笔记已明确区分。数值代码、讲义 PDF、汇报和图片没有因此改动。

## 最简单的使用方式

1. 阅读报告。
2. 打开 Demo 页或各个 GIF，看图中变化。
3. 按文献索引选几篇先读的文章。
4. 需要重算时，再使用相应目录里的 `run.py`。
""", encoding="utf-8")
    (destination / "01_文献索引.md").write_text("""# 文献索引

[统一文献目录](literature/collection-completion-2026-10-21/README.md) 是阅读入口。它按问题分类，记录每篇文章的题目、作者、年份、DOI、可用版本和本地 PDF；缺少公开全文的条目也单独标明。

- [文献表 CSV](literature/collection-completion-2026-10-21/catalog.csv)
- [完整目录 JSON](literature/collection-completion-2026-10-21/catalog.json)

## 建议先读

| 问题 | 原文 |
|---|---|
| 自旋链中波包怎样少一些展宽 | [Osborne 与 Linden，2004](literature/cosine-lattice-wavepacket-audit/spin-chain/osborne_linden_2004_quant-ph_0312141v1.pdf) |
| 二维传播与两个方向的比较 | [Chen 等，2007](literature/cosine-lattice-wavepacket-audit/discrete-optics/chen2007_two-dimensional-discrete-diffraction.pdf) |
| 离散光学中展宽和形状的理论 | [Longhi，2009](literature/cosine-lattice-wavepacket-audit/discrete-optics/longhi2009_1001.0997v1_discrete-diffraction.pdf) |
| 磁性波导中的短脉冲实验 | [Divinskiy 等，2021](literature/linear-spin-wave-packets/spin-wave/2108.08054v1_dispersionless-pulses.pdf) |
| 定向窄波束 | [Wartelle 等，2023](literature/linear-spin-wave-packets/spin-wave/2301.01220v1_caustic-classification.pdf) |
| 反过来设计输入脉冲 | [Casulleras 等，2023](literature/cosine-lattice-wavepacket-audit/magnonics/2209.06608v1_inverse-design.pdf) |
| 怎样判断实际波包中的反流 | [Paterek 与 Goussev，2026](literature/cosine-lattice-wavepacket-audit/backflow/2511.10155v2.pdf) |
| 低展宽传播的量子时钟应用 | [Meier 等，2025 正式版](literature/wavepacket-prospects-2026-10/outlooks/transport-clock/meier2025_published.pdf) |

## 调研记录

- [第一轮线性自旋波文献导读](literature/linear-spin-wave-packets/README.md)
- [余弦晶格传播的已有工作对照](literature/cosine-lattice-wavepacket-audit/README.md)
- [四项研究展望的来源](literature/wavepacket-prospects-2026-10/outlooks/)

正文 PDF 保留原文件名和版本。正式版与预印本可能属于同一篇文章；作者博士论文也不会被冒充成未取得的期刊原文。
""", encoding="utf-8")
    (destination / "02_代码与结果索引.md").write_text("""# 代码与结果索引

这些目录保留了原来的层级。请不要把所有 `.py` 文件单独移到一个平面文件夹，否则共享代码和相邻数据的路径会失效。

## 基础模型

- [模型说明与运行方式](code/README.md)
- [二维传播程序](code/spin_wave_2d.py)
- [模型测试](code/test_spin_wave_2d.py)
- [早期程序与动画备份](code/backups/2026-10-19-before-spin-wave-fix/)

## 单磁子传播图组

- [图表总入口](figures/midterm-report/index.html)
- [图集 PDF](figures/midterm-report/midterm-figure-atlas.pdf)
- [共享色散与传播代码](figures/midterm-report/common.py)
- [单点翻转图](figures/midterm-report/generate_local_flip.py)
- [Gaussian 波包图](figures/midterm-report/generate_gaussian.py)
- [交点波包的数据与生成代码](figures/midterm-report/curvature-design/)
- [统一物理符号的动画](figures/midterm-report/notation/README.md)

## 后续追踪

- [红蓝闪烁与概率的对照图](figures/midterm-report/crossing-diagnostics/phase_probability_comparison.png)
- [闪烁追踪代码与结果](figures/midterm-report/crossing-diagnostics/dynamics/)
- [长时间传播与初宽标度](figures/midterm-report/wavepacket-audit/tracking/)
- [概率流、反流和失谐检查](figures/midterm-report/wavepacket-audit/robustness/)

## 四个最新测试

[研究笔记](research/wavepacket-prospects/README.md) · [离线 Demo 总览](research/wavepacket-prospects/index.html)

| 测试 | 代码 | 动画 | 数据 |
|---|---|---|---|
| 有限源定向波束 | [run.py](research/wavepacket-prospects/demos/finite-source-caustic/run.py) | [GIF](research/wavepacket-prospects/demos/finite-source-caustic/demo.gif) | [JSON](research/wavepacket-prospects/demos/finite-source-caustic/results.json) |
| 有限分辨率反流 | [run.py](research/wavepacket-prospects/demos/backflow-resolution/run.py) | [GIF](research/wavepacket-prospects/demos/backflow-resolution/demo.gif) | [JSON](research/wavepacket-prospects/demos/backflow-resolution/results.json) |
| 受限损耗补偿 | [run.py](research/wavepacket-prospects/demos/loss-aware-pulse/run.py) | [GIF](research/wavepacket-prospects/demos/loss-aware-pulse/demo.gif) | [JSON](research/wavepacket-prospects/demos/loss-aware-pulse/results.json) |
| 两类无序对照 | [run.py](research/wavepacket-prospects/demos/transport-disorder/run.py) | [GIF](research/wavepacket-prospects/demos/transport-disorder/demo.gif) | [JSON](research/wavepacket-prospects/demos/transport-disorder/results.json) |

各测试的 `report.txt` 说明了模型、比较方式和结果。CSV、NPZ 和 JSON 保留了可再利用的数据；PNG、SVG 和 GIF 是查看结果的入口。
""", encoding="utf-8")
    (destination / "03_讲义与汇报索引.md").write_text("""# 讲义与汇报索引

## 当前讲义

[从库仑交换到二维铁磁体的单磁子色散](Note/single_magnon_derivation/main.pdf) · [TeX 源码](Note/single_magnon_derivation/main.tex) · [审阅记录](Note/single_magnon_derivation/review.md)

这份两页讲义是当前单磁子模型的推导入口。

## 当前汇报

[中期报告：统一符号与传播优化版](presentations/midterm/output/中期报告_统一符号与传播优化版.pptx) · [静态预览 PDF](presentations/midterm/output/中期报告_统一符号与传播优化版_预览.pdf)

当前版本共 19 页，含可编辑文字、图表和表格，以及两段传播动画。“能带曲率与波包设计”和“单磁子传播”两个稳定文件名目前指向同一版内容，不是三项不同成果。

[汇报说明与编辑入口](presentations/midterm/README.md)

## 保留的早期材料

- [早期 toy model 笔记](Note/toy_model/)
- [早期运动方程笔记](Note/toy_model_EOM/)
- [历次汇报成品](presentations/midterm/output/)
- [汇报编辑源文件、导入源稿和历史修改](presentations/midterm/build/)
- [早期推导稿和审阅记录](tmp/)

文件名中含 `18页`、`candidate`、`source-before`、`revisions` 的资料属于不同编辑阶段。它们保留供追溯，阅读时优先使用上面的当前入口。
""", encoding="utf-8")
    (destination / "REPRODUCE.md").write_text("""# 复现说明

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
""", encoding="utf-8")
    versions = []
    for package in SCIENTIFIC_PACKAGES:
        try:
            versions.append(f"{package}=={importlib.metadata.version(package)}")
        except importlib.metadata.PackageNotFoundError:
            versions.append(package)
    (destination / "requirements-science.txt").write_text(
        "# Versions observed in the scientific Python environment.\n"
        + "\n".join(versions) + "\n", encoding="utf-8")


def check_index_links(destination: Path) -> list[dict]:
    import re
    records = []
    for name in ("00_先读这里.md", "01_文献索引.md",
                 "02_代码与结果索引.md", "03_讲义与汇报索引.md"):
        path = destination / name
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            resolved = destination / target
            # The report is authored concurrently by the parent, not by packaging.
            status = "present" if resolved.exists() else "pending-parent-report"
            if not resolved.exists() and target != "自旋波研究整理报告.pdf":
                raise FileNotFoundError(f"{name}: {target}")
            records.append({"index": name, "target": target, "status": status})
    return records


def make_zip(destination: Path) -> Path:
    archive = destination.parent / (destination.name + ".zip")
    report = destination / "自旋波研究整理报告.pdf"
    if not report.is_file():
        raise FileNotFoundError("The final report PDF must exist before ZIP creation")
    if archive.exists():
        raise FileExistsError(f"Archive already exists; it has not been overwritten: {archive}")
    if inside(archive, destination):
        raise ValueError("ZIP cannot be written inside the directory it archives")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=3, allowZip64=True) as bundle:
        for directory, dirs, files in os.walk(destination, topdown=True,
                                               followlinks=False):
            folder = Path(directory)
            dirs[:] = [d for d in sorted(dirs)
                       if d not in SKIP_DIR_NAMES and not reparse(folder / d)]
            for name in sorted(files):
                path = folder / name
                if not reparse(path) and path.suffix.lower() not in {".pyc", ".pyo"}:
                    arcname = Path(destination.name) / path.relative_to(destination)
                    bundle.write(path, arcname.as_posix())
    with zipfile.ZipFile(archive) as bundle:
        bad = bundle.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC check failed: {bad}")
        count = len(bundle.infolist())
    print(json.dumps({"zip": str(archive), "entries": count,
                      "bytes": archive.stat().st_size,
                      "sha256": sha256(archive)}, ensure_ascii=False))
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--zip", action="store_true",
                        help="Create a fresh sibling ZIP after verification")
    args = parser.parse_args()
    source = args.source_root.resolve()
    destination = Path(__file__).resolve().parent
    expected = source / "deliverables" / "spin-wave-study-2026-10-21"
    if destination != expected.resolve():
        raise ValueError("This publisher must run in the intended deliverable directory")
    if source == destination or not inside(destination, source):
        raise ValueError("Invalid source/destination relationship")
    for sentinel in ("code/spin_wave_2d.py", "figures/midterm-report/common.py"):
        if not (source / sentinel).is_file():
            raise FileNotFoundError(f"Source is not the expected project: {sentinel}")

    rows, exclusions = [], []
    copied = skipped = copied_bytes = 0
    for path, relative, reason in source_inventory(source):
        if reason:
            exclusions.append({
                "source_path": relative,
                "destination_path": "",
                "bytes": path.stat().st_size if path else None,
                "sha256": "",
                "status": "excluded",
                "exclusion_reason": reason,
            })
            continue
        target = destination / relative
        digest, changed = copy_verified(path, target, destination)
        size = target.stat().st_size
        copied += int(changed)
        skipped += int(not changed)
        copied_bytes += size
        rows.append({
            "source_path": relative,
            "destination_path": relative,
            "bytes": size,
            "sha256": digest,
            "status": "copied-and-verified" if changed else "unchanged-and-verified",
            "exclusion_reason": "",
        })
    write_indexes(destination)
    generated_files = []
    copied_paths = {row["destination_path"] for row in rows}
    manifest_names = {"manifest.json", "inventory.csv", "index-validation.json"}
    for directory, dirs, files in os.walk(destination, topdown=True, followlinks=False):
        folder = Path(directory)
        dirs[:] = [name for name in sorted(dirs)
                   if name not in SKIP_DIR_NAMES and not reparse(folder / name)]
        for name in sorted(files):
            path = folder / name
            relative = path.relative_to(destination).as_posix()
            if (relative in copied_paths or relative in manifest_names
                    or reparse(path) or path.suffix.lower() in {".pyc", ".pyo"}):
                continue
            old_snapshot_file = relative.split("/", 1)[0] in SCOPE_ROOTS
            generated_files.append({
                "source_path": relative if old_snapshot_file else "",
                "destination_path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "status": ("retained-from-earlier-snapshot" if old_snapshot_file
                           else "delivery-generated"),
                "exclusion_reason": "",
            })
    # Write the manifests before checking links that point to them.
    timestamp = datetime.now(timezone.utc).astimezone(
        timezone(timedelta(hours=8))).isoformat()
    manifest = {
        "snapshot_time": timestamp,
        "source_root": str(source),
        "destination_root": str(destination),
        "scope_roots": SCOPE_ROOTS,
        "copied_file_count": len(rows),
        "copied_bytes": copied_bytes,
        "changed_this_run": copied,
        "unchanged_this_run": skipped,
        "packaging_writes_source_files": False,
        "organization_source_edits": [{
            "path": "code/README.md",
            "description": "The parent updated the note-version description: "
                           "single_magnon_derivation is current; only the two "
                           "older toy-model notes are historical.",
        }],
        "hash_algorithm": "SHA-256",
        "verification": "Every file listed under files matches its current source hash; "
                        "delivery-generated and retained older files are hashed separately",
        "current_entrypoints": CURRENT,
        "files": rows,
        "delivery_generated_files": generated_files,
        "exclusions": exclusions,
        "publisher_outputs": [
            "00_先读这里.md", "01_文献索引.md", "02_代码与结果索引.md",
            "03_讲义与汇报索引.md", "REPRODUCE.md", "requirements-science.txt",
            "package_delivery.py", "inventory.csv", "manifest.json",
        ],
        "parent_owned_outputs": ["report/", "自旋波研究整理报告.pdf"],
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    with (destination / "inventory.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        fields = ("source_path", "destination_path", "bytes", "sha256",
                  "status", "exclusion_reason")
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows + generated_files + exclusions)
    link_records = check_index_links(destination)
    (destination / "index-validation.json").write_text(
        json.dumps(link_records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "destination": str(destination), "files_verified": len(rows),
        "MiB": round(copied_bytes / 2**20, 2), "changed": copied,
        "unchanged": skipped, "excluded_entries": len(exclusions),
        "delivery_generated_files": len(generated_files),
        "index_links": len(link_records),
    }, ensure_ascii=False, indent=2))
    if args.zip:
        make_zip(destination)


if __name__ == "__main__":
    main()
