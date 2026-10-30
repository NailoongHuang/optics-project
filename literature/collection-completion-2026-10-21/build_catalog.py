"""Consolidate the existing paper records without changing their source files."""
from pathlib import Path
import csv
import hashlib
import json
import re
import unicodedata

import pymupdf

OUT = Path(__file__).resolve().parent
PROJECT = OUT.parents[1]
LIT = PROJECT / "literature"
records = []
aliases = {}


def load(relative):
    return json.loads((LIT / relative).read_text(encoding="utf-8"))


def first(value):
    if isinstance(value, list):
        return value[0] if value else ""
    return value or ""


def arxiv_base(value):
    match = re.search(r"(?:\d{4}\.\d{4,5}|[a-z-]+/\d{7})(?:v\d+)?",
                      str(value), flags=re.I)
    return re.sub(r"v\d+$", "", match.group(0)) if match else ""


def title_key(value):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", value).lower())


def add(title, authors=None, year=None, doi="", arxiv="", source="", local=None,
        topic="", why="", edition="", metadata_source=""):
    doi = str(first(doi)).replace("https://doi.org/", "").strip()
    aid = arxiv_base(arxiv)
    keys = ["title:" + title_key(title)]
    if doi:
        keys.append("doi:" + doi.lower())
    if aid:
        keys.append("arxiv:" + aid)
    rec = next((aliases[k] for k in keys if k in aliases), None)
    if rec is None:
        rec = dict(title=title, authors=authors or [], year=year, doi=doi,
                   arxiv_id=aid, topic=topic, why_read=why,
                   sources=[], metadata_sources=[], files=[])
        records.append(rec)
    for k in keys:
        aliases[k] = rec
    for name, value in (("authors", authors), ("year", year), ("doi", doi),
                        ("arxiv_id", aid), ("topic", topic), ("why_read", why)):
        if value and not rec.get(name):
            rec[name] = value
    if source and source not in rec["sources"]:
        rec["sources"].append(source)
    if metadata_source and metadata_source not in rec["metadata_sources"]:
        rec["metadata_sources"].append(metadata_source)
    if local:
        local = Path(local)
        if not local.is_absolute():
            local = PROJECT / local
        if local.exists():
            rel = local.relative_to(PROJECT).as_posix()
            if not any(f["path"] == rel for f in rec["files"]):
                rec["files"].append(dict(path=rel, source_url=source,
                                         edition=edition or "versioned source"))
    return rec


def add_existing():
    for r in load("linear-spin-wave-packets/manifest.json"):
        add(r["title"], r["authors"], None, r["doi"],
            r["arxiv_id"], r["pdf_url"],
            "literature/linear-spin-wave-packets/" + r["local_path"],
            edition=f"arXiv {r['arxiv_id']}{r['version']}",
            metadata_source="literature/linear-spin-wave-packets/manifest.json")
    for r in load("cosine-lattice-wavepacket-audit/spin-chain/papers.json")["records"]:
        add(r["title"], r["authors"], r["year"], r["doi"],
            r["arxiv_version"], r["pdf_url"],
            "literature/cosine-lattice-wavepacket-audit/spin-chain/" + r["file"],
            edition="arXiv " + r["arxiv_version"],
            metadata_source="literature/cosine-lattice-wavepacket-audit/spin-chain/papers.json")
    d = load("cosine-lattice-wavepacket-audit/discrete-optics/search_records.json")
    for r in d["records"]:
        local = ("literature/cosine-lattice-wavepacket-audit/discrete-optics/" +
                 r["local_pdf"]) if r.get("local_pdf") else None
        add(r["title"], r["authors"], r["year"], r["doi"],
            r.get("arxiv", ""), r.get("full_text_url", r["url"]), local,
            edition=("arXiv " + r["arxiv"]) if r.get("arxiv") else "journal article",
            metadata_source="literature/cosine-lattice-wavepacket-audit/discrete-optics/search_records.json")
    add("Nonlinear Effects in Waveguide Arrays", ["Hagai Eisenberg"], 2002,
        source="https://openscholar.huji.ac.il/sites/default/files/hagai/files/hagaielectronicthesis.pdf",
        local="literature/cosine-lattice-wavepacket-audit/discrete-optics/eisenberg_thesis.pdf",
        edition="PhD thesis; distinct from the 2000 PRL article")
    d = load("cosine-lattice-wavepacket-audit/magnonics/papers.json")
    for r in d["papers"]:
        matches = list(LIT.rglob(r["arxiv"] + "*.pdf"))
        add(r["title"], [r["authors_short"]], r["year"], r["doi"],
            r["arxiv"], "https://arxiv.org/pdf/" + r["arxiv"],
            matches[0] if matches else None, edition="arXiv " + r["arxiv"],
            metadata_source="literature/cosine-lattice-wavepacket-audit/magnonics/papers.json")
    for r in d["supplemental_leads"]:
        add(r["title"], [r["authors_short"]], r["year"], r.get("doi", ""),
            r.get("arxiv", ""), r["url"], metadata_source=
            "literature/cosine-lattice-wavepacket-audit/magnonics/papers.json")
    for aid, title, authors, year, doi in [
        ("2511.16867v2", "Quantum backflow in biased tight-binding systems",
         ["Francisco Ricardo Torres Arvizu", "Adrian Ortega", "Hernán Larralde"], 2026,
         "10.1103/v49b-zz68"),
        ("2511.10155v2", "General quantum backflow in realistic wave packets",
         ["Tomasz Paterek", "Arseni Goussev"], 2026, "10.1103/tm9s-pkg5"),
        ("2504.12489v2", "Searching for Bloch wave packets with almost definite momentum direction",
         ["Arseni Goussev", "Gregory V. Morozov"], 2025, "10.1103/k9km-k3dm"),
    ]:
        add(title, authors, year, doi, aid, "https://arxiv.org/pdf/" + aid,
            "literature/cosine-lattice-wavepacket-audit/backflow/" + aid + ".pdf",
            edition="arXiv " + aid,
            metadata_source="literature/cosine-lattice-wavepacket-audit/backflow/assessment.txt")
    for r in load("wavepacket-prospects-2026-10/outlooks/backflow/later-work/records.json")["records"]:
        aid = r["arxiv"]
        local = r.get("local_pdf")
        if local and not Path(local).is_absolute() and not local.startswith("literature/"):
            local = "literature/wavepacket-prospects-2026-10/outlooks/backflow/later-work/" + local
        add(r["title"], r.get("authors"), r.get("year"), r.get("doi", ""),
            aid, r.get("full_text_url", r.get("abstract_url", "")), local,
            edition="arXiv " + aid, metadata_source=
            "literature/wavepacket-prospects-2026-10/outlooks/backflow/later-work/records.json")
    for r in load("wavepacket-prospects-2026-10/outlooks/magnon-design/outlook-evidence.json")["records"]:
        if "2607.07324" in str(r):
            add(r["title"], r.get("authors"), 2026, r.get("doi", ""),
                "2607.07324v1", "https://arxiv.org/pdf/2607.07324v1",
                "literature/wavepacket-prospects-2026-10/outlooks/magnon-design/2607.07324v1_perspectives.pdf",
                edition="arXiv 2607.07324v1; perspective preprint",
                metadata_source="literature/wavepacket-prospects-2026-10/outlooks/magnon-design/outlook-evidence.json")
    for r in load("wavepacket-prospects-2026-10/outlooks/transport-clock/outlook_evidence.json"):
        add(r["title"], r.get("authors"), r.get("year"), r.get("doi", ""),
            r.get("arxiv", r.get("url", "")), r.get("published_url", r.get("url", "")),
            metadata_source="literature/wavepacket-prospects-2026-10/outlooks/transport-clock/outlook_evidence.json")
    downloads = load("wavepacket-prospects-2026-10/outlooks/transport-clock/downloads.json")
    for r in downloads:
        if "meier" in r["file"]:
            add("Precision is not limited by the second law of thermodynamics",
                year=2025, doi="10.1038/s41567-025-02929-2",
                source=r["source_url"],
                local="literature/wavepacket-prospects-2026-10/outlooks/transport-clock/"+r["file"],
                edition="Published version of record with institutional cover")
        else:
            add("Inverse engineering for robust state transport along a spin chain via low-energy subspaces",
                ["Yunlan Ji", "Ze Wu", "Ran Liu", "Yuchen Li", "Fangzhou Jin", "Hui Zhou", "Xinhua Peng"],
                2024, "10.1088/1367-2630/ad19fd", source=r["source_url"],
                local="literature/wavepacket-prospects-2026-10/outlooks/transport-clock/"+r["file"],
                edition="Published open-access article")
    for r in load("wavepacket-prospects-2026-10/outlooks/discrete-optics/outlook_evidence.json")["followup_checks"]:
        add(r["title"], r.get("authors"), r.get("year"), r.get("doi", ""),
            r.get("arxiv", ""), r["url"], metadata_source=
            "literature/wavepacket-prospects-2026-10/outlooks/discrete-optics/outlook_evidence.json")
    add("Nondiffractive Subwavelength Wave Beams in a Medium with Externally Controlled Anisotropy",
        ["T. Schneider", "A. A. Serga", "A. V. Chumak", "C. W. Sandweg", "S. Trudel",
         "S. Wolff", "M. P. Kostylev", "V. S. Tiberkevich", "A. N. Slavin", "B. Hillebrands"],
        2010, "10.1103/PhysRevLett.104.197203",
        source="https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.104.197203",
        metadata_source="literature/linear-spin-wave-packets/README.md")


def supplement_acquisitions():
    for path in OUT.rglob("acquisitions.json"):
        d = json.loads(path.read_text(encoding="utf-8"))
        rows = d if isinstance(d, list) else d.get("records", d.get("items", []))
        for r in rows:
            if not r.get("title"):
                continue
            local = r.get("file", r.get("local_path"))
            if local and not Path(local).is_absolute() and not str(local).startswith("literature/"):
                local = path.parent / local
            add(r["title"], r.get("authors"), r.get("year"), r.get("doi", ""),
                r.get("arxiv", ""), r.get("source_url", r.get("url", "")),
                local, edition=r.get("edition", r.get("version", "downloaded source")),
                metadata_source=path.relative_to(PROJECT).as_posix())
    path = OUT / "new-downloads" / "acquisition.json"
    if path.exists():
        d = json.loads(path.read_text(encoding="utf-8"))
        rows = d if isinstance(d, list) else d.get("records", d.get("items", []))
        for r in rows:
            if r.get("title"):
                rec = add(r["title"], r.get("authors"), r.get("year"), r.get("doi", ""),
                          source=r.get("publisher_url", r.get("url", "")),
                          metadata_source=path.relative_to(PROJECT).as_posix())
                rec["acquisition_status_detail"] = r.get("status", "No original PDF obtained")


def apply_curated_notes():
    notes = {
        "10.1103/physreva.69.052315": ("01 自旋链与波包传播", "先读：最直接对应本项目的 Gaussian 波包与三阶展宽。", True),
        "10.1103/physreva.72.062326": ("01 自旋链与波包传播", "了解怎样选择更适合发送和接收的初态。", False),
        "10.1103/physreva.75.032331": ("01 自旋链与波包传播", "看少量自旋怎样制备、停止和重新发射波包。", False),
        "10.1103/physreva.85.052319": ("01 自旋链与波包传播", "对比自由传播与实际端到端传输的区别。", False),
        "10.1140/epjp/i2013-13137-6": ("01 自旋链与波包传播", "作为弹道传输和已有方案的综述入口。", False),
        "10.1088/1367-2630/18/7/073044": ("01 自旋链与波包传播", "查 Gaussian 波包近似平移的误差界。", True),
        "10.1038/s41567-025-02929-2": ("01 自旋链与波包传播", "先读正式版；看低展宽传播如何用于量子时钟。", True),
        "10.1088/1367-2630/ad19fd": ("01 自旋链与波包传播", "对比稳健输运的已有设计方法。", False),
        "10.1109/cdc.2017.8264584": ("01 自旋链与波包传播", "了解参数不确定时，传输控制会怎样变化。", False),
        "10.1016/j.optcom.2006.10.031": ("02 离散光学与色散设计", "先读 Fig.3；它直接比较单方向和双方向的低展宽传播。", True),
        "10.1103/physreva.79.033847": ("02 离散光学与色散设计", "先读：用统一框架理解展宽、波前和近似保形。", True),
        "10.1103/physrevlett.85.1863": ("02 离散光学与色散设计", "衍射管理的早期实验；原论文与博士论文分别保存状态。", False),
        "10.1103/physrevlett.88.093901": ("02 离散光学与色散设计", "入射条件控制衍射的实验先例。", False),
        "10.1103/physreva.77.043804": ("02 离散光学与色散设计", "查远邻耦合怎样改变二维传播。", False),
        "10.3390/dynamics5030025": ("02 离散光学与色散设计", "扩展阅读：多邻居耦合的解析传播。", False),
        "10.3390/dynamics5040051": ("02 离散光学与色散设计", "扩展阅读：半无限阵列的第二邻居传播。", False),
        "10.1103/physrevapplied.16.024028": ("03 磁性波束与脉冲", "先读：实际 YIG 波导中短脉冲低展宽的实验。", True),
        "10.1103/physrevb.107.144431": ("03 磁性波束与脉冲", "先读 Fig.13；本轮高阶波束 demo 的主要来源。", True),
        "10.1103/qz9q-bp9j": ("03 磁性波束与脉冲", "看有限激发源怎样形成并调节真实自旋波束。", True),
        "10.1103/physrevapplied.19.064085": ("03 磁性波束与脉冲", "先读：用天线驱动设计目标脉冲。", True),
        "10.1103/wt14-t3dj": ("03 磁性波束与脉冲", "作为不同机制的对照：利用非线性减轻脉冲展宽。", False),
        "10.1063/5.0071757": ("03 磁性波束与脉冲", "看波导几何怎样改变波长和传播速度。", False),
        "10.1063/5.0018519": ("03 磁性波束与脉冲", "了解自旋波中的光学元件和 Bessel 型波束。", False),
        "10.1109/lmag.2015.2494558": ("03 磁性波束与脉冲", "了解单色波束准直，与短脉冲保形作区分。", False),
        "10.1103/physrevlett.104.197203": ("03 磁性波束与脉冲", "定向窄自旋波束的早期实验。", False),
        "10.1088/0953-8984/11/17/305": ("03 磁性波束与脉冲", "历史线索：零二阶色散附近的高阶传播。", False),
        "10.1038/s41563-025-02282-y": ("03 磁性波束与脉冲", "看材料加工怎样把色散调节变成实际器件。", False),
        "10.1103/v49b-zz68": ("04 反流与测量", "先读：与本项目最近邻晶格反流直接对应。", True),
        "10.1103/tm9s-pkg5": ("04 反流与测量", "先读：含少量反向速度成分时怎样认证反流。", True),
        "10.1103/k9km-k3dm": ("04 反流与测量", "厘清 Bloch 波矢、真实动量和速度的区别。", False),
    }
    by_arxiv = {
        "2602.12767": ("04 反流与测量", "先读：反流态的制备和成像困难。", True),
        "2607.10281": ("04 反流与测量", "扩展阅读：量子关联对光学反流的影响。", False),
        "2607.07324": ("03 磁性波束与脉冲", "先读展望：激发端设计、参数误差和可实现性。", True),
        "2107.08518": ("01 自旋链与波包传播", "理解随机耦合链的带中心行为，避免把已知机制当作新发现。", False),
        "1101.2101": ("01 自旋链与波包传播", "了解无序系统中扩展态与动力学之间的关系。", False),
        "2504.05505": ("02 离散光学与色散设计", "扩展阅读：芯片网络中的色散设计；不是同一种晶格能带。", False),
        "2109.00782": ("05 可迁移的光学方法", "看频率与空间方向的关联怎样帮助保形。", False),
        "2201.08297": ("05 可迁移的光学方法", "需要时查阅的长综述，不必从头读完。", False),
        "1711.04027": ("05 可迁移的光学方法", "了解 Airy、Bessel 型时空脉冲的构造。", False),
        "2211.09057": ("04 反流与测量", "了解耗散和退相干怎样削弱反流。", False),
        "2309.02245": ("04 反流与测量", "作为量子计算机模拟反流的已有实现对照。", False),
    }
    for rec in records:
        note = notes.get(rec["doi"].lower()) or by_arxiv.get(rec["arxiv_id"])
        if rec["title"] == "Nonlinear Effects in Waveguide Arrays":
            note = ("02 离散光学与色散设计", "作者博士论文，补充衍射管理及色散合成的说明。", False)
        if "Magnetically tunable Airy-like" in rec["title"]:
            note = ("03 磁性波束与脉冲", "扩展阅读：通过激发相位塑造弯曲的自旋波束。", False)
        if note:
            rec["topic"], rec["why_read"], rec["priority_read"] = note
        else:
            rec.setdefault("priority_read", False)
            rec["topic"] = rec["topic"] or "06 扩展参阅"
            rec["why_read"] = rec["why_read"] or "作为相邻研究方向的背景材料。"


def enrich_metadata():
    cache = OUT / "metadata"
    override_path = OUT / "metadata-overrides.json"
    overrides = json.loads(override_path.read_text(encoding="utf-8")) if override_path.exists() else {}
    for rec in records:
        if rec["doi"]:
            path = cache / (re.sub(r"[^a-zA-Z0-9]+", "_", rec["doi"].lower()) + ".json")
            if path.exists():
                raw = json.loads(path.read_text(encoding="utf-8"))
                m = raw.get("message", raw)
                if m.get("author"):
                    rec["authors"] = [" ".join(filter(None, [a.get("given"), a.get("family")]))
                                      for a in m["author"]]
                dates = m.get("published-print", m.get("published", m.get("published-online", {})))
                parts = dates.get("date-parts", [])
                if parts and parts[0]:
                    rec["year"] = parts[0][0]
                rec["journal"] = first(m.get("container-title"))
                rec["volume"] = m.get("volume", "")
                rec["pages_or_article"] = m.get("page", m.get("article-number", ""))
                rec["metadata_sources"].append(path.relative_to(PROJECT).as_posix())
        if not rec["year"] and rec["arxiv_id"]:
            aid = rec["arxiv_id"].split("/")[-1]
            rec["year"] = 2000 + int(aid[:2]) if int(aid[:2]) < 90 else 1900 + int(aid[:2])
        if rec["arxiv_id"] == "2109.00782":
            rec["year"] = 2022
            rec["journal"] = "Laser & Photonics Reviews"
            rec["pages_or_article"] = "2100634"
            rec["metadata_sources"].append("https://arxiv.org/abs/2109.00782")
        if rec["arxiv_id"] in overrides:
            override = overrides[rec["arxiv_id"]]
            for name, value in override.items():
                if name == "metadata_sources":
                    rec[name] += [s for s in value if s not in rec[name]]
                else:
                    rec[name] = value


def verify_and_write():
    verified_paths = set()
    for rec in records:
        for f in rec["files"]:
            path = PROJECT / f["path"]
            raw = path.read_bytes()
            if not raw.startswith(b"%PDF-"):
                raise ValueError(f"Not PDF: {path}")
            doc = pymupdf.open(path)
            if len(doc) < 1:
                raise ValueError(f"Empty PDF: {path}")
            first_page = doc[0].get_text().replace("\x00", "")
            f.update(pages=len(doc), bytes=len(raw),
                     sha256=hashlib.sha256(raw).hexdigest(),
                     first_page_excerpt=first_page[:1200],
                     verification="PDF signature, all-page parsing and first-page identity inspection")
            for page in doc:
                page.get_text()
            doc.close()
            verified_paths.add(f["path"])
        rec["status"] = "全文已保存" if rec["files"] else "仅有书目信息，原文PDF未取得"
        rec["preferred_file"] = next((f["path"] for f in rec["files"]
                                      if "Published" in f["edition"]), "")
        if not rec["preferred_file"] and rec["files"]:
            rec["preferred_file"] = rec["files"][0]["path"]
    records.sort(key=lambda r: (r["topic"], not r["priority_read"],
                               r["year"] or 0, r["title"].lower()))
    for i, rec in enumerate(records, 1):
        rec["catalog_id"] = f"P{i:02d}"
    coverage = dict(date="2026-10-21", works=len(records),
                    works_with_pdf=sum(bool(r["files"]) for r in records),
                    pdf_files=len(verified_paths),
                    missing_pdf=sum(not r["files"] for r in records),
                    all_local_pdf_paths=sorted(verified_paths))
    (OUT/"catalog.json").write_text(json.dumps(dict(summary=coverage, records=records),
                                             ensure_ascii=False, indent=2), encoding="utf-8")
    cols = ["catalog_id","topic","priority_read","year","title","authors","doi",
            "arxiv_id","status","preferred_file","why_read"]
    with (OUT/"catalog.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=cols)
        writer.writeheader()
        for rec in records:
            row = {k: rec[k] for k in cols}
            row["authors"] = "; ".join(rec["authors"]) if isinstance(rec["authors"],list) else rec["authors"]
            writer.writerow(row)
    lines = ["# 文献总目录", "",
             f"整理日期：2026-10-21。共 {coverage['works']} 项文献，"
             f"其中 {coverage['works_with_pdf']} 项已有全文，保存 {coverage['pdf_files']} 个 PDF；"
             f"另 {coverage['missing_pdf']} 项尚未取得原文 PDF。不同版本保留在同一条记录下。", "",
             "带“先读”的条目与当前计算或四个 demo 最直接。其余材料用于查背景，不必逐篇读完。", ""]
    topic = None
    for rec in records:
        if rec["topic"] != topic:
            topic = rec["topic"]
            lines += ["## " + topic, ""]
        lines += [f"**{rec['catalog_id']} · {rec['title']}**"
                  + (" · 先读" if rec["priority_read"] else ""), "",
                  f"{'; '.join(rec['authors']) if isinstance(rec['authors'], list) else rec['authors']}（{rec['year']}）。"
                  + (f" DOI: [{rec['doi']}](https://doi.org/{rec['doi']})。" if rec["doi"] else ""), "",
                  rec["why_read"], ""]
        if rec["files"]:
            for f in rec["files"]:
                rel = Path(f["path"]).relative_to("literature").as_posix()
                lines += [f"- [PDF：{f['edition']}]({ '../' + rel}) · {f['pages']} 页"]
        else:
            lines += ["- 原文 PDF 未取得；记录保留，可通过 DOI 或原出版页补取。"]
        lines += [""]
    (OUT/"README.md").write_text("\n".join(lines), encoding="utf-8")
    def bib_escape(value):
        return str(value).replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%")
    bib = []
    for rec in records:
        kind = "phdthesis" if rec["title"] == "Nonlinear Effects in Waveguide Arrays" else "article"
        fields = dict(title=rec["title"], author=" and ".join(rec["authors"]), year=rec["year"])
        if rec.get("journal"):
            fields["journal"] = rec["journal"]
        if rec.get("volume"):
            fields["volume"] = rec["volume"]
        if rec.get("pages_or_article"):
            fields["pages"] = rec["pages_or_article"]
        if rec["doi"]:
            fields["doi"] = rec["doi"]
        if rec["arxiv_id"]:
            fields["eprint"] = rec["arxiv_id"]
            fields["archivePrefix"] = "arXiv"
        if rec["sources"]:
            fields["url"] = rec["sources"][0]
        bib += [f"@{kind}{{{rec['catalog_id']},"] + [
            f"  {key} = {{{bib_escape(value)}}}," for key, value in fields.items() if value
        ] + ["}", ""]
    (OUT/"references.bib").write_text("\n".join(bib), encoding="utf-8")
    missing = [{k: rec[k] for k in ("catalog_id", "title", "year", "doi", "sources", "status")}
               for rec in records if not rec["files"]]
    (OUT/"unavailable.json").write_text(json.dumps(missing, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
    print(json.dumps(coverage,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    add_existing()
    supplement_acquisitions()
    apply_curated_notes()
    enrich_metadata()
    verify_and_write()
