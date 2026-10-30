"""Fetch version-pinned primary sources for the cosine-band packet audit."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import html
import json
import re
import urllib.request

import pymupdf

OUT = Path(__file__).resolve().parent
PAPERS = [
    ("osborne_linden_2004", "quant-ph/0312141v1"),
    ("haselgrove_2005", "quant-ph/0404152v2"),
    ("gong_brumer_2007", "quant-ph/0702265v1"),
    ("apollaro_2012", "1203.5516v1"),
    ("banchi_2013", "1309.0069v2"),
    ("thompson_2016", "1511.05656v3"),
    ("meier_2025", "2407.07948v1"),
]


def fetch(entry):
    name, identifier = entry
    abstract_url = f"https://arxiv.org/abs/{identifier}"
    pdf_url = f"https://arxiv.org/pdf/{identifier}"
    headers = {"User-Agent": "LiteratureEvidenceAudit/1.0"}
    raw = urllib.request.urlopen(
        urllib.request.Request(abstract_url, headers=headers), timeout=50
    ).read()
    source = raw.decode("utf-8")
    (OUT / f"{name}_abstract.html").write_text(source, encoding="utf-8")
    metadata = {}
    for meta_name, content in re.findall(
            r'<meta name="([^"]+)" content="([^"]*)"\s*/?>', source):
        if meta_name.startswith("citation_"):
            metadata.setdefault(meta_name, []).append(html.unescape(content))
    data = urllib.request.urlopen(
        urllib.request.Request(pdf_url, headers=headers), timeout=80
    ).read()
    if not data.startswith(b"%PDF"):
        raise ValueError(f"Non-PDF response: {pdf_url}")
    target = OUT / f"{name}_{identifier.replace('/', '_')}.pdf"
    target.write_bytes(data)
    with pymupdf.open(target) as pdf:
        texts = [page.get_text().replace("\x00", "") for page in pdf]
        count = len(pdf)
        if not texts[0].strip():
            raise ValueError(f"No readable first page: {name}")
        (OUT / f"{name}_text.txt").write_text(
            "\n\n".join(f"[PDF PAGE {i+1}]\n{text}"
                        for i, text in enumerate(texts)), encoding="utf-8")
    return dict(key=name, arxiv_version=identifier,
                abstract_url=abstract_url, pdf_url=pdf_url,
                file=target.name, bytes=len(data), pages=count,
                sha256=hashlib.sha256(data).hexdigest(),
                metadata=metadata, status="downloaded-and-text-readable")


def main():
    records = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for entry, result in zip(PAPERS, pool.map(fetch, PAPERS)):
            records.append(result)
            print(result["key"], result["pages"], result["bytes"], flush=True)
    (OUT / "download_manifest.json").write_text(
        json.dumps(dict(retrieved_date="2026-10-20", sources=records),
                   ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
