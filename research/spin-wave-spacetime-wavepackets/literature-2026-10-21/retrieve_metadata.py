"""Retrieve public scholarly records for this dated literature investigation.

Mechanical retrieval only; relevance and scientific interpretation are assessed
from primary sources in the accompanying report. Uses Windows curl for TLS.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import re
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
QUERIES = [
    '"spin wave" "space-time" wave packet',
    '"magnon" "space-time" wave packet',
    '"spin wave" "spatiotemporal" spectral correlation',
    '"spin wave" "nondiffracting" pulse',
    '"spin wave" "frequency" "wavevector" matching',
    '"spin wave" "X wave"',
]


def curl_bytes(url):
    run = subprocess.run(
        ["curl.exe", "--location", "--fail", "--silent", "--show-error",
         "--connect-timeout", "10", "--max-time", "40", url],
        capture_output=True, check=False,
    )
    if run.returncode:
        raise RuntimeError(run.stderr.decode("utf-8", errors="replace").strip())
    return run.stdout


def retrieve(provider, index, query):
    if provider == "crossref":
        url = "https://api.crossref.org/works?" + urllib.parse.urlencode({
            "query.bibliographic": query, "rows": 30,
            "filter": "until-pub-date:2026-10-21",
            "select": "DOI,title,author,published,abstract,URL,type",
        })
    else:
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
            "search": query, "per-page": 30,
            "filter": "to_publication_date:2026-10-21",
            "select": "id,doi,title,publication_date,primary_location,abstract_inverted_index,referenced_works,cited_by_count",
        })
    record = dict(provider=provider, query_id=f"{provider}-{index:02d}",
                  query=query, date="2026-10-21", url=url)
    try:
        data = json.loads(curl_bytes(url))
        target = ROOT / "raw" / f"{provider}-{index:02d}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        items = data["message"]["items"] if provider == "crossref" else data["results"]
        record.update(status="retrieved", returned=len(items), raw_file=target.relative_to(ROOT).as_posix())
        normalized = []
        for item in items:
            normalized.append(dict(
                title=(item.get("title", [""])[0] if provider == "crossref" else item.get("title", "")),
                doi=(item.get("DOI", "").lower() if provider == "crossref" else (item.get("doi") or "").replace("https://doi.org/", "").lower()),
                provider=provider, source_query=record["query_id"], metadata=item,
            ))
        return record, normalized
    except Exception as exc:
        record.update(status="failed", error=str(exc))
        return record, []


def main():
    log, all_records = [], []
    jobs = [(provider, i, q) for provider in ("crossref", "openalex")
            for i, q in enumerate(QUERIES, 1)]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(retrieve, *job) for job in jobs]
        for future in as_completed(futures):
            rec, items = future.result()
            log.append(rec)
            all_records.extend(items)
            print(rec["query_id"], rec["status"], rec.get("returned", rec.get("error")), flush=True)
    unique = {}
    for item in all_records:
        key = item["doi"] or re.sub(r"\W+", "", item["title"].casefold())
        if key in unique:
            unique[key]["retrievals"].append(dict(provider=item["provider"], source_query=item["source_query"]))
            unique[key]["provider_records"].append(item["metadata"])
        else:
            unique[key] = dict(title=item["title"], doi=item["doi"],
                               retrievals=[dict(provider=item["provider"], source_query=item["source_query"])],
                               provider_records=[item["metadata"]])
    (ROOT / "metadata-search-log.json").write_text(json.dumps(sorted(log, key=lambda r:r["query_id"]), ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "metadata-candidates.json").write_text(json.dumps(list(unique.values()), ensure_ascii=False, indent=2), encoding="utf-8")
    print("Retrieved rows:", len(all_records), "DOI/title-deduplicated:", len(unique))
    for item in unique.values():
        if re.search(r"spin.?wave|magnon", item["title"], re.I):
            print(item["doi"], "|", item["title"])


if __name__ == "__main__":
    main()
