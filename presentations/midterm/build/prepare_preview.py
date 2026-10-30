"""Assemble a preview PDF and contact sheets from the authored slide renders."""
from pathlib import Path
import pymupdf as fitz
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
renders=sorted((ROOT/'renders').glob('slide-*.png'))
assert len(renders)>=30
doc=fitz.open()
for p in renders:
    page=doc.new_page(width=960,height=540)
    page.insert_image(page.rect,filename=str(p))
doc.set_metadata({'title':'二维铁磁体中的单磁子传播：中期报告','subject':'PPT逐页预览','author':''})
doc.save(ROOT.parent/'output'/'midterm-report-preview.pdf',garbage=4,deflate=True)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
for begin in range(0,len(renders),6):
    board=Image.new('RGB',(1600,3*487),'#E8EEF2');draw=ImageDraw.Draw(board)
    for j,p in enumerate(renders[begin:begin+6]):
        with Image.open(p) as im:
            im.thumbnail((780,439));x=(j%2)*800+10;y=(j//2)*487+8
            board.paste(im,(x,y));draw.text((x,y+448),f'{begin+j+1:02d}',font=font,fill='#203648')
    board.save(ROOT/f'contact-{begin//6+1:02d}.jpg',quality=95)
print('Preview PDF and contact sheets:',len(renders),'slides')
