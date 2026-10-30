"""Download selected public arXiv papers, preserving version and provenance."""
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import html
import json
import re
import time
import pymupdf

ROOT = Path(__file__).resolve().parent
PAPERS = [
    ('2108.08054', 'spin-wave', 'dispersionless-pulses'),
    ('2111.02236', 'spin-wave', 'geometrical-control'),
    ('1906.02301', 'spin-wave', 'bessel-gaussian-fourier-optics'),
    ('1703.05548', 'spin-wave', 'all-angle-collimation'),
    ('2301.01220', 'spin-wave', 'caustic-classification'),
    ('2404.15011', 'spin-wave', 'nonreciprocal-caustic-beams'),
    ('2109.00782', 'optical-method', 'space-time-dispersive-media'),
    ('2201.08297', 'optical-method', 'space-time-review'),
    ('1711.04027', 'optical-method', 'airy-bessel-pulsed-beams'),
]

def fetch(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'AcademicLiteratureRetrieval/1.0'}), timeout=45) as r:
                return r.read(), r.geturl()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(3)

def meta(source, name):
    return [html.unescape(x) for x in re.findall(r'<meta\s+name="' + re.escape(name) + r'"\s+content="([^"]*)"', source)]

def main():
    records = []
    for arxiv_id, category, slug in PAPERS:
        rec = {'arxiv_id': arxiv_id, 'category': category, 'retrieved_date': '2026-10-19', 'abstract_url': f'https://arxiv.org/abs/{arxiv_id}'}
        try:
            source, _ = fetch(rec['abstract_url'])
            source = source.decode('utf-8')
            versions = re.findall(re.escape(arxiv_id) + r'v(\d+)', source)
            version = 'v' + str(max(map(int, versions)))
            rec.update(version=version, title=meta(source, 'citation_title')[0], authors=meta(source, 'citation_author'), date=meta(source, 'citation_date'), doi=meta(source, 'citation_doi'))
            stem = f'{arxiv_id}{version}_{slug}'
            folder = ROOT / category
            folder.mkdir(parents=True, exist_ok=True)
            (ROOT / 'metadata').mkdir(exist_ok=True)
            (ROOT / 'extracted').mkdir(exist_ok=True)
            (ROOT / 'metadata' / f'{arxiv_id}.html').write_text(source, encoding='utf-8')
            path = folder / f'{stem}.pdf'
            url = f'https://arxiv.org/pdf/{arxiv_id}{version}'
            if path.exists():
                raw = path.read_bytes()
                final_url = url
            else:
                raw, final_url = fetch(url)
                if not raw.startswith(b'%PDF-'):
                    raise ValueError('Response is not a PDF')
                with pymupdf.open(stream=raw, filetype='pdf') as doc:
                    if not len(doc) or not doc[0].get_text().strip():
                        raise ValueError('PDF has no readable first page')
                path.write_bytes(raw)
            with pymupdf.open(path) as doc:
                text = '\n\n'.join(f'=== PDF PAGE {i+1} ===\n{p.get_text()}' for i, p in enumerate(doc))
                (ROOT / 'extracted' / f'{arxiv_id}{version}.txt').write_text(text, encoding='utf-8')
                rec.update(pages=len(doc), pdf_metadata=doc.metadata, first_page_excerpt=doc[0].get_text()[:600])
            rec.update(pdf_url=url, final_url=final_url, local_path=path.relative_to(ROOT).as_posix(), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), status='downloaded-and-readable')
            print(f'OK {arxiv_id}{version}: {rec["pages"]} pages | {rec["title"]}', flush=True)
        except Exception as exc:
            rec.update(status='failed', error=str(exc))
            print(f'FAILED {arxiv_id}: {exc}', flush=True)
        records.append(rec)
        (ROOT / 'manifest.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Complete: {sum(r["status"] == "downloaded-and-readable" for r in records)}/{len(records)}', flush=True)

if __name__ == '__main__':
    main()
