"""Adapt the existing verification runner to this release, without making a PDF."""
from pathlib import Path
B=Path(__file__).resolve().parent
s=(B.parent/'compact/package_preview.py').read_text(encoding='utf-8')
s=s.replace('assert frames==[61,61]','assert frames==[61]')
s=s.replace('单磁子传播：18页优化版','能带高斯曲率与波包初步设计')
s=s.replace('密集波场、原理与模拟','曲率解析、波包设计与受控传播模拟')
s=s.replace('中期报告_18页优化版_预览.pdf','中期报告_能带曲率与波包设计_预览.pdf')
s += '''
with fitz.open(pdf) as check:
    assert len(check)==18
    check[4].get_pixmap(matrix=fitz.Matrix(2,2)).save(B/'preview-pdf-page05.png')
'''
(B/'package_preview.py').write_text(s,encoding='utf-8')
