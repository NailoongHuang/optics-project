"""Dated, bounded OpenAlex citation expansion and arXiv API checks."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import re
import urllib.parse
from retrieve_metadata import curl_bytes

ROOT=Path(__file__).resolve().parent
SEEDS=[
    ("he_2022", "10.1002/lpor.202100634"),
    ("review_2022", "10.1364/AOP.450016"),
    ("spp_2020", "10.1021/acsphotonics.0c00293"),
    ("inverse_2023", "10.1103/PhysRevApplied.19.064085"),
    ("bessel_2020", "10.1063/5.0018519"),
]


def chase(seed):
    key,doi=seed
    rec=dict(seed=key,doi=doi,date="2026-10-21",direction="forward citations",max_pages=3)
    try:
        url="https://api.openalex.org/works/https://doi.org/"+doi
        work=json.loads(curl_bytes(url))
        (ROOT/"raw"/f"seed-{key}.json").write_text(json.dumps(work,ensure_ascii=False,indent=2),encoding="utf-8")
        wid=work["id"].rsplit("/",1)[1]
        cursor="*"
        records=[]
        page_counts=[]
        for page in range(3):
            query=urllib.parse.urlencode({"filter":f"cites:{wid},to_publication_date:2026-10-21","per-page":200,"cursor":cursor,"select":"id,doi,title,publication_date,abstract_inverted_index,primary_location"})
            page_url="https://api.openalex.org/works?"+query
            data=json.loads(curl_bytes(page_url))
            (ROOT/"raw"/f"citations-{key}-{page+1}.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
            records.extend(data["results"])
            page_counts.append(len(data["results"]))
            cursor=data["meta"].get("next_cursor")
            if not cursor or not data["results"] or len(records)>=data["meta"]["count"]:
                break
        rec.update(status="retrieved",openalex_id=wid,index_total=data["meta"]["count"],returned=len(records),pages=page_counts,truncated=len(records)<data["meta"]["count"],records=records)
    except Exception as exc:
        rec.update(status="failed",error=str(exc))
    return rec


def main():
    out=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for future in as_completed([pool.submit(chase,seed) for seed in SEEDS]):
            rec=future.result();out.append(rec)
            print(rec["seed"],rec["status"],rec.get("returned",rec.get("error")),"of",rec.get("index_total"),flush=True)
            for row in rec.get("records",[]):
                words=" ".join((row.get("abstract_inverted_index") or {}).keys())
                if re.search(r"magnon|spin.wave|ferromagnet",row.get("title","")+" "+words,re.I):
                    print("  CANDIDATE",row.get("doi"),"|",row["title"],flush=True)
    (ROOT/"citation-chasing.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    arxiv_log=[]
    for i,query in enumerate(['all:"space-time" AND (all:"spin-wave" OR all:magnon)', 'all:"spin wave" AND (all:nondiffracting OR all:"spectral correlation")'],1):
        url="https://export.arxiv.org/api/query?"+urllib.parse.urlencode({"search_query":query,"start":0,"max_results":100,"sortBy":"submittedDate","sortOrder":"descending"})
        rec=dict(query=query,url=url,date="2026-10-21")
        try:
            raw=curl_bytes(url)
            path=ROOT/"raw"/f"arxiv-search-{i}.xml";path.write_bytes(raw)
            rec.update(status="retrieved",file=path.relative_to(ROOT).as_posix(),bytes=len(raw))
        except Exception as exc:
            rec.update(status="failed",error=str(exc))
        arxiv_log.append(rec);print("arxiv",i,rec["status"],flush=True)
    (ROOT/"arxiv-api-log.json").write_text(json.dumps(arxiv_log,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
