"""Retrieve the already-discussed public follow-up literature and verify PDFs."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import urllib.request
import pymupdf

OUT = Path(__file__).resolve().parent

RECORDS = [
    dict(id="oneil2017", title="Sensitivity and Robustness of Quantum Spin-1/2 Rings to Parameter Uncertainty",
         authors=["Sean O'Neil","Edmond Jonckheere","Sophie Schirmer","Frank Langbein"],
         year=2017, doi="10.1109/CDC.2017.8264584", arxiv="1708.09649v1",
         version="arXiv v1", file="1708.09649v1_spin-ring-robustness.pdf",
         urls=["https://arxiv.org/pdf/1708.09649v1"]),
    dict(id="krishna2021", title="Beyond the universal Dyson singularity for 1-D chains with hopping disorder",
         authors=["Akshay Krishna","R. N. Bhatt"], year=2021,
         doi="10.1016/j.aop.2021.168537", arxiv="2107.08518v1",
         version="arXiv v1", file="2107.08518v1_dyson-disorder.pdf",
         urls=["https://arxiv.org/pdf/2107.08518v1"]),
    dict(id="krapivsky2011", title="Dynamics of a quantum particle in low-dimensional disordered systems with extended states",
         authors=["P. L. Krapivsky","J. M. Luck"], year=2011,
         doi="10.1088/1742-5468/2011/02/P02031", arxiv="1101.2101v2",
         version="arXiv v2", file="1101.2101v2_disordered-dynamics.pdf",
         urls=["https://arxiv.org/pdf/1101.2101v2"]),
    dict(id="gorgulu2025", title="On-chip arbitrary dispersion engineering with deep photonic networks",
         authors=["Kazim Gorgulu","Aycan Deniz Vit","Ali Najjar Amiri","Emir Salih Magden"],
         year=2025, doi="10.1364/OL.564441", arxiv="2504.05505v2",
         version="arXiv v2", file="2504.05505v2_photonic-dispersion.pdf",
         urls=["https://arxiv.org/pdf/2504.05505v2"]),
    dict(id="tapia_many2025", title="Waveguide Arrays: Interaction to Many Neighbors",
         authors=["Marco A. Tapia-Valerdi","Irán Ramos-Prieto","Francisco Soto-Eguibar","Héctor M. Moya-Cessa"],
         year=2025, doi="10.3390/dynamics5030025", preprint_doi="10.20944/preprints202505.1458.v1",
         version="publisher PDF if available; otherwise preprint v1", file="tapia2025_many-neighbors.pdf",
         urls=["https://mdpi-res.com/d_attachment/dynamics/dynamics-05-00025/article_deploy/dynamics-05-00025.pdf",
               "https://www.preprints.org/manuscript/202505.1458/download/final_file"]),
    dict(id="tapia_second2025", title="Waveguide Arrays Interaction to Second Neighbors: Semi-Infinite Case",
         authors=["Marco A. Tapia-Valerdi","Irán Ramos-Prieto","Francisco Soto-Eguibar","Héctor M. Moya-Cessa"],
         year=2025, doi="10.3390/dynamics5040051",
         version="publisher PDF", file="tapia2025_second-neighbors.pdf",
         urls=["https://mdpi-res.com/d_attachment/dynamics/dynamics-05-00051/article_deploy/dynamics-05-00051.pdf"]),
    dict(id="bensmann2025", title="Dispersion-tunable low-loss implanted spin-wave waveguides for large magnonic networks",
         authors=["Jannis Bensmann","Robert Schmidt","Kirill O. Nikolaev","Dimitri Raskhodchikov",
                  "Shraddha Choudhary","Richa Bhardwaj","Shabnam Taheriniya","Akhil Varri",
                  "Sven Niehues","Ahmad El Kadri","Johannes Kern","Wolfram H. P. Pernice",
                  "Sergej O. Demokritov","Vladislav E. Demidov",
                  "Steffen Michaelis de Vasconcellos","Rudolf Bratschitsch"],
         year=2025, doi="10.1038/s41563-025-02282-y",
         version="publisher PDF", file="bensmann2025_implanted-waveguides.pdf",
         urls=["https://www.nature.com/articles/s41563-025-02282-y.pdf"]),
]


def retrieve(item):
    item = dict(item)
    item["role"] = "supporting follow-up already discussed; not an additional core-result claim"
    item["retrieved_date"] = "2026-10-21"
    item["attempts"] = []
    path = OUT / item["file"]
    for url in item.pop("urls"):
        try:
            if path.exists():
                content = path.read_bytes()
                final = url
            else:
                request = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=35) as response:
                    content = response.read()
                    final = response.url
            if not content.startswith(b"%PDF"):
                raise ValueError("Response is not a PDF")
            doc = pymupdf.open(stream=content, filetype="pdf")
            pages = [p.get_text().replace("\x00", "") for p in doc]
            if not pages or len(pages[0].strip()) < 30:
                raise ValueError("Missing readable first-page text")
            path.write_bytes(content)
            (OUT / (path.stem + ".txt")).write_text(
                "\n\n".join(f"=== PDF PAGE {i+1} ===\n{s}" for i,s in enumerate(pages)),
                encoding="utf-8")
            doc[0].get_pixmap(matrix=pymupdf.Matrix(.7,.7)).save(
                OUT / (path.stem + "-first-page.png"))
            item.update(status="downloaded-and-readable", source_url=url,
                        final_url=final, pages=len(doc), bytes=len(content),
                        sha256=hashlib.sha256(content).hexdigest(),
                        first_page_excerpt=pages[0][:1500])
            if "mdpi-res" in url:
                item["version"] = "publisher PDF"
            elif "preprints.org" in url:
                item["version"] = "preprint v1"
            item["attempts"].append(dict(url=url, outcome="success"))
            doc.close()
            return item
        except Exception as exc:
            item["attempts"].append(dict(url=url, outcome=str(exc)))
    item["status"] = "not-downloaded"
    return item


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(retrieve, RECORDS))
    (OUT / "acquisitions.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps([{"id":r["id"],"status":r["status"],"pages":r.get("pages"),
                       "attempts":r["attempts"]} for r in records],
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
