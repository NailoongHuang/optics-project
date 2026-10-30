"""Preserve newly inspected public primary full texts and page-tagged text."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import hashlib
import json
import subprocess
import pymupdf as fitz

ROOT = Path(__file__).resolve().parent
SOURCES = [
    ("spp_2020_2003.02105v1", "https://arxiv.org/pdf/2003.02105v1"),
    ("electron_2026_2610.08391v1", "https://arxiv.org/pdf/2610.08391v1"),
    ("magnonics_roadmap_2024", "https://iris.cnr.it/retrieve/4fa5b9dc-a22e-4411-a421-464851833b9f/Flebus_2024_J._Phys.__Condens._Matter_36_363501.pdf"),
    ("ultrafast_caustic_2013", "https://link.aps.org/pdf/10.1103/PhysRevLett.110.097201"),
]


def collect(key, url):
    rec = dict(key=key, source_url=url, accessed="2026-10-21")
    try:
        pdf_path = ROOT / "pdfs" / f"{key}.pdf"
        text_path = ROOT / "extracted" / f"{key}.txt"
        if pdf_path.exists():
            raw = pdf_path.read_bytes()
            rec["reused_existing"] = True
        else:
            proc = subprocess.run(["curl.exe", "--location", "--fail", "--silent", "--show-error", "--connect-timeout", "10", "--max-time", "55", url], capture_output=True)
            if proc.returncode:
                raise RuntimeError(proc.stderr.decode("utf-8", errors="replace").strip())
            raw = proc.stdout
        if not raw.startswith(b"%PDF"):
            raise ValueError("The response is not a PDF")
        pdf_path.parent.mkdir(exist_ok=True)
        text_path.parent.mkdir(exist_ok=True)
        pdf_path.write_bytes(raw)
        with fitz.open(stream=raw, filetype="pdf") as doc:
            pages = [p.get_text() for p in doc]
            text_path.write_text("\n\n".join(f"=== PDF PAGE {i+1} ===\n{t}" for i,t in enumerate(pages)), encoding="utf-8")
            rec.update(status="downloaded-and-readable", pages=len(doc), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), pdf=pdf_path.relative_to(ROOT).as_posix(), extracted=text_path.relative_to(ROOT).as_posix())
    except Exception as exc:
        rec.update(status="unavailable", error=str(exc))
    return rec


def main():
    records=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(collect,*source) for source in SOURCES]):
            rec=future.result()
            records.append(rec)
            print(rec["key"], rec["status"], rec.get("pages",rec.get("error")), flush=True)
    (ROOT / "fulltext-acquisition.json").write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__ == "__main__":
    main()
