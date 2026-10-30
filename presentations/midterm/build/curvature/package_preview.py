"""Create the static preview from final exported-PPTX renders and verify delivery."""
from pathlib import Path
from zipfile import ZipFile
from PIL import Image,ImageDraw,ImageFont
import pymupdf as fitz
import hashlib,io,json,numpy as np
B=Path(__file__).resolve().parent
W=B.parent.parent
meta=json.loads((B/'build_result.json').read_text(encoding='utf-8'))
receipt=json.loads((B/f"validation-r{meta['revision']}.json").read_text(encoding='utf-8'))
ppt=W/'output'/meta['release']
assert hashlib.sha256(ppt.read_bytes()).hexdigest()==receipt['finalSha256']
assert receipt['packageIntegrity']['slide_count']==18
assert receipt['presentationLayout']['finding_count']==0
assert receipt['presentationLayout']['warning_count']==0
frames=[]
with ZipFile(ppt) as z:
    for name in z.namelist():
        if name.endswith('.gif'):
            im=Image.open(io.BytesIO(z.read(name)))
            for j in range(im.n_frames):im.seek(j);im.load()
            frames.append(im.n_frames)
assert frames==[61]
renders=sorted((B/'final-renders').glob('slide-*.png'))
assert len(renders)==18
doc=fitz.open();deltas=[]
for imfile in renders:
    page=doc.new_page(width=960,height=540);page.insert_image(page.rect,filename=str(imfile))
    with Image.open(imfile) as x, Image.open(B/'renders'/imfile.name) as y:
        deltas.append(float(np.abs(np.asarray(x.convert('RGB'),dtype=float)-np.asarray(y.convert('RGB'),dtype=float)).mean()))
doc.set_metadata({'title':'能带高斯曲率与波包初步设计','subject':'曲率解析、波包设计与受控传播模拟','author':''})
pdf=W/'output/中期报告_能带曲率与波包设计_预览.pdf';doc.save(pdf,garbage=4,deflate=True);doc.close()
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
for start in range(0,len(renders),6):
    sheet=Image.new('RGB',(1600,3*487),'#EAF0F3');draw=ImageDraw.Draw(sheet)
    for j,imfile in enumerate(renders[start:start+6]):
        with Image.open(imfile) as im:
            im=im.convert('RGB');im.thumbnail((780,439));x=(j%2)*800+10;y=(j//2)*487+8
            sheet.paste(im,(x,y));draw.text((x,y+448),str(start+j+1).zfill(2),font=font,fill='#203648')
    sheet.save(B/f'contact-{start//6+1:02d}.jpg',quality=95)
checks={'passed':True,'slides':18,'user_maximum':20,'gif_frames':frames,'sha256':receipt['finalSha256'],
 'native_charts':receipt['packageIntegrity']['chart_count'],'roundtrip_max_pixel_mae':max(deltas),
 'preview_pages':len(renders),'powerpoint_application_playback_tested':False}
assert max(deltas)<.01
(B/'delivery_check.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks,indent=2))

with fitz.open(pdf) as check:
    assert len(check)==18
    check[4].get_pixmap(matrix=fitz.Matrix(2,2)).save(B/'preview-pdf-page05.png')
