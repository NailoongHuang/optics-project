"""Collect public access metadata; never change authentication or access controls."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import subprocess
import urllib.parse

ROOT=Path(__file__).resolve().parent
DOI="10.1103/7zfd-p48s"
SOURCES=[
    ("semantic-scholar", "https://api.semanticscholar.org/graph/v1/paper/DOI:"+DOI+"?fields=title,authors,year,openAccessPdf,externalIds,url"),
    ("openaire", "https://api.openaire.eu/search/publications?"+urllib.parse.urlencode({"doi":DOI,"format":"json"})),
    ("openalex", "https://api.openalex.org/works/https://doi.org/"+DOI),
    ("crossref", "https://api.crossref.org/works/"+DOI),
    ("author-orcid", "https://pub.orcid.org/v3.0/0000-0001-8603-900X/works"),
    ("corresponding-author-orcid", "https://pub.orcid.org/v3.0/0000-0001-9349-5556/works"),
    ("aps-supplemental", "https://journals.aps.org/prb/supplemental/"+DOI),
    ("author-homepage", "https://faculty.ustc.edu.cn/gaonan/zh_CN/zdylm/937828/list/index.htm"),
]


def fetch(item):
    key,url=item
    rec=dict(key=key,url=url,date="2026-10-21")
    proc=subprocess.run(["curl.exe","--location","--silent","--show-error","--connect-timeout","10","--max-time","40","--header","Accept: application/json", "--write-out","\n%{http_code}\n%{url_effective}",url],capture_output=True)
    if proc.returncode:
        rec.update(status="transport-failed",error=proc.stderr.decode("utf-8",errors="replace"))
        return rec
    body,http,effective=proc.stdout.rsplit(b"\n",2)
    rec.update(http_status=int(http),effective_url=effective.decode("utf-8",errors="replace"))
    target=ROOT/(key+".response")
    target.write_bytes(body)
    rec.update(bytes=len(body),saved_file=target.name)
    try:
        data=json.loads(body)
        (ROOT/(key+".json")).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        rec["json_file"]=key+".json"
    except (ValueError,UnicodeError):
        pass
    rec["status"]="retrieved" if rec["http_status"]==200 else "access-unavailable"
    return rec


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    records=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(fetch,x) for x in SOURCES]):
            rec=future.result();records.append(rec)
            print(rec["key"],rec["status"],rec.get("http_status"),rec.get("bytes"),flush=True)
    (ROOT/"access-records.json").write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__=="__main__": main()
