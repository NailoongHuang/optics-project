"""Build a self-contained offline viewer for the verified minimal demos.

Content and claims are supplied in gallery_manifest.json after scientific review.
The viewer does not perform numerical simulations or fetch external libraries.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>波包研究方向 · 最小验证 Demo</title>
<style>
:root{color-scheme:light;--ink:#172d3c;--muted:#556878;--line:#dce4e8;--paper:#f3f6f7;--blue:#12667e;--accent:#bd583d}
*{box-sizing:border-box}body{margin:0;color:var(--ink);font:16px/1.75 "Microsoft YaHei","Segoe UI",sans-serif;background:var(--paper)}
header{padding:34px max(24px,calc((100vw - 1460px)/2));background:#fff;border-bottom:1px solid var(--line)}
.eyebrow{font-size:12px;letter-spacing:.15em;color:var(--blue);font-weight:700}
h1{font-size:30px;line-height:1.3;margin:10px 0 12px;font-weight:650}header p{margin:0;max-width:1000px;color:var(--muted)}
a{color:var(--blue);text-underline-offset:3px}a:hover{color:#0c4557}
.layout{display:grid;grid-template-columns:255px minmax(0,1fr);max-width:1460px;margin:24px auto;gap:24px;padding:0 24px}
aside{position:sticky;top:20px;align-self:start}
.tabs{display:grid;gap:10px}.tab{text-align:left;border:1px solid var(--line);background:#fff;padding:15px 16px;border-radius:9px;cursor:pointer;color:var(--ink);font:inherit}
.tab:hover{border-color:#8eb0bf}.tab[aria-selected=true]{border-color:var(--blue);box-shadow:inset 4px 0 var(--blue);background:#edf5f7}
.tab small{display:block;color:var(--muted);font-size:12px}.tab strong{display:block;font-size:15px}
.aside-note{font-size:13px;color:var(--muted);padding:16px 4px}.aside-links{display:grid;gap:8px;font-size:14px}
main{min-width:0}.panel{background:#fff;border:1px solid var(--line);border-radius:12px;padding:26px}
.tag{display:inline-block;padding:3px 10px;border-radius:20px;background:#e7f1f3;color:#22566a;font-size:12px;font-weight:700}
h2{font-size:25px;line-height:1.4;margin:12px 0 10px}.verdict{font-size:17px;max-width:1000px;margin:0 0 22px}
.context{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:20px}
.context>div{padding:15px 17px;border:1px solid var(--line);border-radius:8px}
.label{font-size:12px;color:var(--muted);font-weight:700;letter-spacing:.04em}
.context p{margin:5px 0 0;font-size:14px}.context a{font-size:13px}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:18px 0}
.metric{padding:14px 16px;background:#f4f7f8;border-radius:8px}.metric strong{display:block;font-size:23px;line-height:1.35}.metric span{display:block;font-size:12px;color:var(--muted);margin-top:5px}
.toolbar{display:flex;flex-wrap:wrap;gap:9px;align-items:center;margin:22px 0 12px}
button.mode{border:1px solid var(--line);background:white;color:var(--ink);border-radius:6px;padding:8px 15px;font:inherit;font-size:14px;cursor:pointer}
button.mode[aria-pressed=true]{background:var(--blue);color:white;border-color:var(--blue)}
.figure{margin:0;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:white}
.figure img{display:block;width:100%;height:auto;cursor:zoom-in}
figcaption{padding:12px 16px;color:var(--muted);font-size:13px;border-top:1px solid var(--line)}
.scope{border-left:3px solid var(--accent);padding:7px 14px;margin:21px 0;color:#5c443c;background:#fbf5f1;font-size:14px}
.evidence{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px}.evidence p{font-size:14px;margin:8px 0}
ul{padding-left:20px;margin:9px 0}li{margin:7px 0;font-size:14px}
.files{display:flex;flex-wrap:wrap;gap:16px;font-size:14px;border-top:1px solid var(--line);padding-top:18px;margin-top:22px}
footer{font-size:12px;color:var(--muted);max-width:1460px;padding:0 24px 32px;margin:auto}
dialog{max-width:96vw;width:1400px;border:0;border-radius:10px;padding:16px;box-shadow:0 15px 70px #0005}dialog::backdrop{background:#14212acf}
dialog img{width:100%;height:auto}dialog button{float:right;position:sticky;top:0;padding:8px 14px;border:1px solid var(--line);background:white;border-radius:6px;cursor:pointer;font:inherit}
.error{padding:30px;background:#fff0ed}
@media(max-width:850px){.layout{grid-template-columns:1fr;margin:16px auto;padding:0 14px;gap:14px}aside{position:static}.tabs{grid-template-columns:1fr 1fr}.aside-note{padding:8px 0}.aside-links{display:flex;flex-wrap:wrap}.panel{padding:18px}.context,.evidence{grid-template-columns:1fr}.metrics{grid-template-columns:1fr 1fr 1fr}h1{font-size:25px}h2{font-size:22px}header{padding:25px 20px}}
@media(max-width:500px){.metrics{grid-template-columns:1fr}.metric strong{font-size:21px}.tabs{grid-template-columns:1fr}.tab{padding:10px 14px}.context{gap:10px}}
</style>
</head>
<body>
<header>
<div class="eyebrow">SOURCE → QUESTION → CONTROL → EVIDENCE</div>
<h1>波包研究方向与最小验证</h1>
<p id="intro"></p>
</header>
<div class="layout">
<aside>
<nav class="tabs" role="tablist" aria-label="选择最小测试" id="tabs"></nav>
<div class="aside-note">可切换结果图与动画；点击图像可放大。所有图来自保存的计算数据。</div>
<div class="aside-links"><a href="README.md" target="_blank">完整研究笔记</a><a href="gallery_manifest.json" target="_blank">目录与来源</a></div>
</aside>
<main id="main" role="tabpanel" aria-live="polite"></main>
</div>
<footer id="footer"></footer>
<dialog id="zoom"><button id="closezoom" type="button">关闭</button><img id="zoomimg" alt="放大的结果图"></dialog>
<script id="manifest" type="application/json">__MANIFEST__</script>
<script>
const data=JSON.parse(document.getElementById('manifest').textContent);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let active=null,mode='summary';
document.getElementById('intro').textContent=data.intro;
document.getElementById('footer').textContent=data.footer;
const tabs=document.getElementById('tabs');
data.demos.forEach((d,i)=>{
 const b=document.createElement('button');b.className='tab';b.type='button';b.setAttribute('role','tab');b.id='tab-'+d.id;
 b.innerHTML=`<small>DEMO ${String(i+1).padStart(2,'0')} · ${esc(d.status)}</small><strong>${esc(d.shortTitle)}</strong>`;
 b.onclick=()=>select(d.id);tabs.append(b);
});
function select(id){
 active=data.demos.find(d=>d.id===id)||data.demos[0];mode='summary';
 document.querySelectorAll('.tab').forEach(b=>b.setAttribute('aria-selected',String(b.id==='tab-'+active.id)));
 history.replaceState(null,'','#'+active.id);render();
}
function render(){
 const d=active, sources=d.sources.map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)}</a>`).join(' · ');
 document.getElementById('main').setAttribute('aria-labelledby','tab-'+d.id);
 document.getElementById('main').innerHTML=`<article class="panel">
 <span class="tag">${esc(d.status)}</span><h2>${esc(d.title)}</h2><p class="verdict">${esc(d.verdict)}</p>
 <div class="context"><div><div class="label">作者留下的问题</div><p>${esc(d.question)}</p><p>${sources}</p></div>
 <div><div class="label">本轮最小测试</div><p>${esc(d.test)}</p></div></div>
 <div class="metrics">${d.metrics.map(m=>`<div class="metric"><strong>${esc(m.value)}</strong><span>${esc(m.label)}</span></div>`).join('')}</div>
 <div class="toolbar"><button class="mode" type="button" data-mode="summary" aria-pressed="${mode==='summary'}">结果图</button>
 <button class="mode" type="button" data-mode="animation" aria-pressed="${mode==='animation'}">播放动画</button></div>
 <figure class="figure"><img id="demo-image" src="${esc(mode==='animation'?d.animation:d.summary)}" alt="${esc(d.title)}">
 <figcaption>${esc(mode==='animation'?d.animationCaption:d.summaryCaption)}</figcaption></figure>
 <div class="scope"><strong>结论适用范围：</strong>${esc(d.scope)}</div>
 <div class="evidence"><div><div class="label">对照与核验</div><ul>${d.checks.map(s=>`<li>${esc(s)}</li>`).join('')}</ul></div>
 <div><div class="label">是否值得继续</div><p>${esc(d.next)}</p></div></div>
 <div class="files"><a href="${esc(d.results)}" target="_blank">原始结果 JSON</a><a href="${esc(d.report)}" target="_blank">该测试说明</a><a href="${esc(d.script)}" target="_blank">复现脚本</a></div>
 </article>`;
 document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;render()});
 document.getElementById('demo-image').onclick=()=>{document.getElementById('zoomimg').src=document.getElementById('demo-image').src;document.getElementById('zoom').showModal()};
}
document.getElementById('closezoom').onclick=()=>document.getElementById('zoom').close();
window.addEventListener('hashchange',()=>select(location.hash.slice(1)));
select(location.hash.slice(1));
</script>
</body></html>
"""


def main():
    manifest = json.loads((ROOT / "gallery_manifest.json").read_text(encoding="utf-8"))
    for item in manifest["demos"]:
        for key in ("summary", "animation", "results", "report", "script"):
            path = ROOT / item[key]
            if not path.is_file():
                raise FileNotFoundError(f"{item['id']}: missing {key}: {path}")
    payload = json.dumps(manifest, ensure_ascii=False).replace("</", "<\\/")
    (ROOT / "index.html").write_text(
        TEMPLATE.replace("__MANIFEST__", payload), encoding="utf-8")
    print(f"Built {ROOT / 'index.html'} with {len(manifest['demos'])} verified entries")


if __name__ == "__main__":
    main()
