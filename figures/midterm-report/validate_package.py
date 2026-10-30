"""Decode every export and render the assembled PDF for final visual QA."""
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET
import numpy as np
import pymupdf as fitz
from PIL import Image,ImageDraw,ImageFont
from common import ROOT,write_json
from build_catalog import load_items,FONT

def main():
    items=load_items();qa=ROOT/'qa';qa.mkdir(exist_ok=True)
    checks=[];animations=[]
    for item in items:
        record={'id':item['id'],'formats':[]}
        for ext,relative in item['files'].items():
            path=ROOT/relative
            assert path.is_file() and path.stat().st_size>100
            if ext=='png':
                with Image.open(path) as im:
                    im.load();record['pixels']=im.size
                    small=im.convert('RGB');small.thumbnail((200,200))
                    assert np.std(np.asarray(small))>4
            elif ext=='svg': ET.parse(path)
            elif ext=='pdf':
                with fitz.open(path) as doc: assert len(doc)==1
            elif ext=='gif':
                with Image.open(path) as im:
                    count=im.n_frames
                    assert count>2
                    duration_ms=0
                    for f in range(count):
                        im.seek(f);im.load();duration_ms+=im.info.get('duration',0)
                    chosen=[]
                    for f in [0,count//2,count-1]: im.seek(f);chosen.append(im.convert('RGB'))
                    animations.append((item,count,chosen))
                    record['all_frames_decoded']=count
                    record['seconds_per_loop']=duration_ms/1000
            record['formats'].append(ext)
        checks.append(record)
    font=ImageFont.truetype(str(FONT),18)
    for start in range(0,len(animations),4):
        sheet=Image.new('RGB',(1260,1180),'#eaf0f3');draw=ImageDraw.Draw(sheet)
        for row,(item,count,frames) in enumerate(animations[start:start+4]):
            y=row*295
            draw.text((14,y+8),item['id']+' · 首帧 / 中间帧 / 末帧',font=font,fill='#203648')
            for col,im in enumerate(frames):
                im.thumbnail((410,245));sheet.paste(im,(col*420+(420-im.width)//2,y+40))
        sheet.save(qa/f'animations-{start//4+1:02d}.jpg',quality=94)
    pdf=ROOT/'midterm-figure-atlas.pdf'
    renderer=shutil.which('pdftoppm')
    bundled=Path('C:/Users/xuanm/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe')
    if renderer is None and bundled.is_file(): renderer=str(bundled)
    renderdir=qa/'pdf-render';renderdir.mkdir(exist_ok=True)
    if renderer:
        proc=subprocess.run([renderer,'-r','90','-png',str(pdf),str(renderdir/'page')],capture_output=True,text=True)
        if proc.returncode: raise RuntimeError(proc.stderr)
        rendering_engine='Poppler pdftoppm'
    else:
        with fitz.open(pdf) as doc:
            for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(renderdir/f'page-{i+1:02d}.png')
        rendering_engine='PyMuPDF fallback'
    pages=sorted(renderdir.glob('page-*.png'))
    with fitz.open(pdf) as doc:
        assert len(pages)==len(doc)==40
        outside=[]
        for i,page in enumerate(doc):
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        r=fitz.Rect(span['bbox'])
                        if r.x0 < -1 or r.y0 < -1 or r.x1 > page.rect.width+1 or r.y1>page.rect.height+1:
                            outside.append({'page':i+1,'text':span['text'],'box':list(r)})
        assert not outside,outside
    for start in range(0,len(pages),6):
        sheet=Image.new('RGB',(1440,3*550),'#eaf0f3');draw=ImageDraw.Draw(sheet)
        for j,p in enumerate(pages[start:start+6]):
            with Image.open(p) as im:
                im=im.convert('RGB');im.thumbnail((704,500))
                x=(j%2)*720;y=(j//2)*550;sheet.paste(im,(x+(720-im.width)//2,y+5))
                draw.text((x+12,y+512),f'PDF page {start+j+1}',font=font,fill='#203648')
        sheet.save(qa/f'pdf-contact-{start//6+1:02d}.jpg',quality=94)
    result=dict(status='passed',static_figures=sum('png' in i['files'] for i in items),
        animations=len(animations),decoded_animation_frames=sum(n for _,n,_ in animations),
        pdf_pages=len(pages),pdf_renderer=rendering_engine,pdf_text_outside_page=outside,exports=checks,
        visual_review='Contact sheets and selected full pages require human/model visual inspection in addition to these mechanical checks.')
    write_json(ROOT/'checks_exports.json',result)
    print('Export checks passed:',result['static_figures'],'figures,',result['decoded_animation_frames'],'animation frames,',len(pages),'PDF pages.')

if __name__=='__main__':main()
