"""Assemble an offline figure gallery, vector PDF atlas, and reproducibility index."""
from pathlib import Path
import json
import html
import hashlib
import platform
import re
import pymupdf as fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from common import ROOT, PROJECT, write_json

FONT=Path('C:/Windows/Fonts/msyh.ttc')
PDF_TEXT_FONT=fitz.Font(fontfile=str(FONT))
GROUPS={'a-dispersion':'A · 模型、色散与群速度',
        'b-local-flip':'B · 单格点翻转怎样传播',
        'c-gaussian':'C · Gaussian 波包怎样移动和展宽'}

def load_items():
    items=[]
    for g in 'abc':
        obj=json.loads((ROOT/f'manifest_{g}.json').read_text(encoding='utf-8'))
        part=obj if isinstance(obj,list) else obj.get('items',obj.get('figures',[]))
        if not part: raise ValueError(f'Empty group {g}')
        items.extend(part)
    return items

def esc(x): return html.escape(str(x),quote=True)

def figure_card(item):
    files=item['files']; anim='gif' in files
    ext='gif' if anim else 'png'; url=files[ext]
    label='动画' if anim else ('延伸' if item.get('role')=='extension' else '基础')
    params=json.dumps(item.get('parameters',{}),ensure_ascii=False,indent=2)
    downloads=' · '.join(f'<a href="{esc(v)}" download>{esc(k.upper())}</a>' for k,v in files.items())
    media=(f'<div class="anim-placeholder"><span>▶</span><p>点击播放 · 固定色标</p></div>' if anim else
           f'<img src="{esc(url)}" loading="lazy" alt="{esc(item["title"])}">')
    return f'''<article class="card" data-group="{esc(item['group'])}" data-kind="{label}" id="{esc(item['id'])}">
      <div class="card-head"><span class="id">{esc(item['id'])}</span><span class="tag">{label}</span></div>
      <h3>{esc(item['title'])}</h3>
      <button class="figure" data-url="{esc(url)}" data-title="{esc(item['title'])}" aria-label="放大查看：{esc(item['title'])}">{media}</button>
      <p class="caption">{esc(item['caption'])}</p>
      <div class="downloads">{downloads}</div>
      <details><summary>计算参数</summary><pre>{esc(params)}</pre></details>
    </article>'''

def make_html(items):
    static=[x for x in items if 'png' in x['files']]; animations=[x for x in items if 'gif' in x['files']]
    sections=''.join(f'<section class="group" id="{g}"><h2>{title}</h2><div class="grid">'+
                     ''.join(figure_card(i) for i in items if i['group']==g)+'</div></section>' for g,title in GROUPS.items())
    document='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>自旋激发的传播 | 中期报告图像与模拟</title><style>
    :root{--ink:#203648;--muted:#526476;--accent:#246b9a;--line:#dbe3e8;--bg:#f4f7f9}
    *{box-sizing:border-box}body{margin:0;color:var(--ink);background:var(--bg);font:16px/1.75 'Microsoft YaHei',system-ui,sans-serif}
    a{color:#17628c;text-underline-offset:3px}a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid #c07722;outline-offset:3px}
    header{padding:52px max(5vw,24px) 36px;background:#fff;border-bottom:1px solid var(--line)}.eyebrow{letter-spacing:.1em;color:#326e72;font-size:13px}
    h1{font-size:clamp(30px,3.6vw,48px);line-height:1.3;margin:12px 0 18px;font-weight:750}h2{font-size:25px;margin:42px 0 18px}h3{font-size:20px;line-height:1.55;margin:8px 0 16px}
    .intro{max-width:920px;color:var(--muted)}.count{display:flex;gap:32px;margin:24px 0}.count strong{font-size:30px;display:block;color:var(--ink)}
    .links{display:flex;gap:12px;flex-wrap:wrap}.links a{border:1px solid var(--line);padding:8px 16px;border-radius:7px;text-decoration:none;background:#fff}
    main{max-width:1500px;margin:auto;padding:10px 4vw 70px}.note{padding:18px 24px;border-left:4px solid #388a78;background:white;margin:28px 0;color:var(--muted)}
    .equation{font-family:'Cambria Math','Times New Roman',serif;font-size:21px;color:var(--ink);overflow-x:auto;padding:10px 0}
    .toolbar{position:sticky;top:0;z-index:5;background:#f4f7f9f5;border-bottom:1px solid var(--line);padding:13px 0;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
    .toolbar button{border:1px solid #b7c8d2;border-radius:20px;padding:7px 16px;background:white;color:var(--ink);font:inherit;cursor:pointer}.toolbar button.active{background:#203648;color:white;border-color:#203648}
    input{font:inherit;border:1px solid #b7c8d2;border-radius:7px;padding:7px 12px;max-width:100%;margin-left:auto}
    .grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}.card{background:white;border:1px solid var(--line);border-radius:12px;padding:22px;overflow:hidden}
    .card-head{display:flex;justify-content:space-between;font-size:12px;gap:10px}.id{font-family:ui-monospace,monospace;color:#536776;overflow-wrap:anywhere}.tag{border-radius:3px;padding:1px 8px;background:#eaf3f1;white-space:nowrap}
    .figure{display:block;width:100%;border:1px solid #e4e9ec;background:white;padding:0;cursor:zoom-in;border-radius:5px;overflow:hidden}.figure img{display:block;width:100%;height:auto}
    .caption{font-size:15px;line-height:1.9}.downloads{font-size:14px;margin-bottom:10px}details{font-size:13px;color:var(--muted)}summary{cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f7f9;padding:12px;border-radius:5px}
    .anim-placeholder{height:235px;display:grid;place-content:center;color:var(--muted);background:linear-gradient(135deg,#eff5f8,#f5f8f5)}.anim-placeholder span{font-size:42px;text-align:center;color:var(--accent)}
    dialog{width:min(1400px,96vw);max-height:95vh;border:0;border-radius:10px;padding:18px;background:white}dialog::backdrop{background:#10202ed9}dialog header{padding:0 0 12px;display:flex;justify-content:space-between;gap:20px}dialog img{display:block;max-width:100%;max-height:78vh;margin:auto;object-fit:contain}dialog button{font:inherit;border:1px solid #b7c8d2;background:white;border-radius:5px;padding:5px 14px;cursor:pointer}
    dialog button{white-space:nowrap;flex-shrink:0}[hidden]{display:none!important}.empty{padding:40px;color:var(--muted)}footer{border-top:1px solid var(--line);padding-top:25px;color:var(--muted);font-size:14px}
    @media(max-width:900px){.grid{grid-template-columns:1fr}.toolbar{position:static}input{margin-left:0;width:100%}.card{padding:16px}.count{gap:20px}h2{font-size:22px}}
    @media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
    </style></head><body><header><div class="eyebrow">中期报告 · 物理图像与原理</div><h1>自旋激发怎样传播？</h1>
    <p class="intro">从交换耦合与单磁子色散出发，依次观察局域翻转、Gaussian 波包、群速度与展宽。每张图回答一个具体问题；参数、可复现数据和数值核验一并保留。图中展示的是模型计算。</p>
    <div class="count"><div><strong>STATIC_COUNT</strong>张独立静态图</div><div><strong>ANIM_COUNT</strong>段传播动画</div><div><strong>3</strong>条讲述主线</div></div>
    <div class="links"><a href="midterm-figure-atlas.pdf">完整图册 PDF</a><a href="README.md">阅读与复现说明</a><a href="THEORY.md">物理原理与公式</a><a href="checks_independent.json">独立数值核验</a><a href="REVIEW.md">独立科学审查</a></div></header>
    <main><div class="note"><strong>统一约定</strong><div class="equation">ε / J<sub>x</sub> = 1 − cos q<sub>x</sub> + η(1 − cos q<sub>y</sub>)</div>
    q = ka，τ = J<sub>x</sub>t / ℏ，η = J<sub>y</sub> / J<sub>x</sub>。位置以晶格常数 a 为单位。所有传播态满足 ΣP = 1，P = |ψ|² 表示翻转概率；σ 是初始概率的均方根宽度。</div>
    <p><strong>建议讲述：</strong>先用 A 组建立模型和色散图像，再用 B 组解释局域激发如何展开，最后用 C 组解释载波、群速度与展宽。标记“延伸”的图可用于结尾展望。动画点击后播放，最后一帧停留后循环重播。</p>
    <nav class="toolbar" aria-label="图组筛选"><button class="active" data-filter="all">全部</button><button data-filter="a-dispersion">色散</button><button data-filter="b-local-flip">单点传播</button><button data-filter="c-gaussian">波包</button><button data-filter="动画">动画</button><button data-filter="延伸">延伸</button><input id="search" type="search" placeholder="搜索图名或物理概念" aria-label="搜索图名或物理概念"></nav>
    SECTIONS<div class="empty" hidden>没有匹配的图，请换一个关键词。</div><footer>所有图均从保存的参数与数据生成。FFT 采用周期晶格；所展示时间内的边界影响通过边缘概率与扩大晶格对照检查。完整核验与模型适用范围见说明文件。</footer></main>
    <dialog id="viewer"><header><strong id="viewer-title"></strong><button id="close">关闭 ×</button></header><img id="viewer-image" alt=""></dialog>
    <script>
    const cards=[...document.querySelectorAll('.card')];let selected='all';
    function filter(){let visible=0;const q=document.querySelector('#search').value.trim().toLowerCase();cards.forEach(c=>{const match=(selected==='all'||c.dataset.group===selected||c.dataset.kind===selected)&&c.textContent.toLowerCase().includes(q);c.hidden=!match;if(match)visible++;});document.querySelectorAll('.group').forEach(g=>g.hidden=![...g.querySelectorAll('.card')].some(c=>!c.hidden));document.querySelector('.empty').hidden=visible>0;}
    document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{selected=b.dataset.filter;document.querySelectorAll('[data-filter]').forEach(x=>x.classList.toggle('active',x===b));filter();}));document.querySelector('#search').addEventListener('input',filter);
    const viewer=document.querySelector('#viewer'),vi=document.querySelector('#viewer-image');document.querySelectorAll('.figure').forEach(b=>b.addEventListener('click',()=>{vi.src=b.dataset.url;vi.alt=b.dataset.title;document.querySelector('#viewer-title').textContent=b.dataset.title;viewer.showModal();}));document.querySelector('#close').onclick=()=>viewer.close();viewer.addEventListener('close',()=>vi.removeAttribute('src'));viewer.addEventListener('click',e=>{if(e.target===viewer)viewer.close();});
    </script></body></html>'''
    document=document.replace('STATIC_COUNT',str(len(static))).replace('ANIM_COUNT',str(len(animations))).replace('SECTIONS',sections)
    (ROOT/'index.html').write_text(document,encoding='utf-8')

def text(page,rect,s,size=13,color=(.13,.21,.28)):
    # YaHei has no U+210F glyph; prose uses the standard ASCII spelling.
    # Mathematical hbar in the original vector figures retains its math font.
    s=s.replace('ℏ','hbar')
    missing={c for c in s if not c.isspace() and not PDF_TEXT_FONT.has_glyph(ord(c))}
    if missing: raise ValueError(f'Missing PDF text glyphs: {missing}')
    page.insert_font(fontname='YaHei',fontfile=str(FONT))
    result=page.insert_textbox(fitz.Rect(rect),s,fontname='YaHei',fontsize=size,lineheight=1.6,color=color)
    if result<0: raise RuntimeError(f'PDF text overflow ({result}): {s[:80]}')

def make_pdf(items):
    figures=[x for x in items if 'pdf' in x['files']]
    doc=fitz.open(); cover=doc.new_page(width=960,height=680)
    cover.draw_rect(fitz.Rect(0,0,960,680),fill=(.96,.98,.99),color=None)
    text(cover,(58,65,890,110),'中期报告 · 图像与模拟资料',18)
    text(cover,(58,135,890,230),'自旋激发的传播',37)
    text(cover,(58,240,880,360),'交换作用 → 色散关系 → 局域激发传播 → 波包移动与展宽\n\n'+f'{len(figures)} 张静态图，按概念引入顺序排列；动画请打开同目录 index.html。',18)
    text(cover,(58,420,875,600),'模型：自旋 1/2，均匀最近邻铁磁交换，零外场。\n约定：q = ka，τ = Jx t / ℏ，η = Jy / Jx。\n观测量：P = |ψ|² 为归一化的单磁子翻转概率。\n数值方法：周期晶格上的精确 Fourier 相位演化。\n核验：独立矩阵推进、Bessel 解析解、解析矩与扩大晶格对照。',15)
    toc=[[1,'阅读说明',1]]
    lastgroup=None
    for index,item in enumerate(figures,1):
        page=doc.new_page(width=960,height=680)
        source=fitz.open(ROOT/item['files']['pdf'])
        page.show_pdf_page(fitz.Rect(0,0,960,540),source,0,keep_proportion=True);source.close()
        page.draw_line((44,543),(916,543),color=(.84,.89,.92),width=.7)
        caption=item['caption']
        # Plain captions are preserved verbatim; one caption accompanies every figure.
        text(page,(46,552,914,642),caption,12)
        text(page,(46,650,860,677),f'{item["id"]}  ·  {GROUPS[item["group"]]}',9,color=(.35,.43,.49))
        text(page,(890,650,938,677),str(index),9)
        if item['group']!=lastgroup:
            toc.append([1,GROUPS[item['group']],len(doc)]);lastgroup=item['group']
        toc.append([2,item['title'],len(doc)])
    doc.set_toc(toc)
    doc.set_metadata({'title':'自旋激发的传播：中期报告图像与模拟','subject':'单磁子色散、局域翻转与 Gaussian 波包','author':''})
    path=ROOT/'midterm-figure-atlas.pdf';doc.save(path,garbage=4,deflate=True);doc.close()
    with fitz.open(path) as check:
        assert len(check)==len(figures)+1
        assert all(len(page.get_text().strip())>20 for page in check)
    return len(figures)+1

def make_contact_sheets(items):
    qa=ROOT/'qa';qa.mkdir(exist_ok=True)
    font=ImageFont.truetype(str(FONT),19)
    figures=[x for x in items if 'png' in x['files']]
    for start in range(0,len(figures),8):
        selected=figures[start:start+8];sheet=Image.new('RGB',(1400,4*450),'#e9eef2');draw=ImageDraw.Draw(sheet)
        for j,item in enumerate(selected):
            x=(j%2)*700;y=(j//2)*450
            with Image.open(ROOT/item['files']['png']) as im:
                im=im.convert('RGB');im.thumbnail((684,394));sheet.paste(im,(x+(700-im.width)//2,y+12))
            draw.text((x+15,y+410),item['id'],fill='#203648',font=font)
        sheet.save(qa/f'contact-{start//8+1:02d}.jpg',quality=93)

def make_index(items,pdf_pages):
    data=[]
    for item in items:
        for kind,rel in item['files'].items():
            path=ROOT/rel
            assert path.exists() and path.stat().st_size>0,path
            data.append(dict(path=rel,kind=kind,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    sources=[]
    for path in [PROJECT/'Note/single_magnon_derivation/main.tex',PROJECT/'code/spin_wave_2d.py',*sorted(ROOT.glob('*.py'))]:
        sources.append(dict(path=path.relative_to(PROJECT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    datasets=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,
        sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(ROOT.rglob('*.npz'))]
    write_json(ROOT/'package_manifest.json',dict(static_figures=sum('png' in i['files'] for i in items),
        animations=sum('gif' in i['files'] for i in items),pdf_pages=pdf_pages,files=data,sources=sources,datasets=datasets,
        environment=dict(python=platform.python_version(),numpy=np.__version__,pymupdf=fitz.VersionBind)))
    lines=['# 逐图索引','','完整浏览请打开 [离线图库](index.html) 或 [PDF 图册](midterm-figure-atlas.pdf)。','']
    for group,title in GROUPS.items():
        lines.extend(['## '+title,''])
        for item in [i for i in items if i['group']==group]:
            links=' · '.join(f'[{kind.upper()}]({rel})' for kind,rel in item['files'].items())
            lines.extend([f'### {item["id"]} · {item["title"]}','','**用途：** '+item['caption'],'',links,''])
    (ROOT/'FIGURE_INDEX.md').write_text('\n'.join(lines),encoding='utf-8')

def main():
    items=load_items();make_html(items);pages=make_pdf(items);make_contact_sheets(items);make_index(items,pages)
    print(f'Assembled {len(items)} items, {pages} PDF pages, offline gallery, and contact sheets.')

if __name__=='__main__': main()
