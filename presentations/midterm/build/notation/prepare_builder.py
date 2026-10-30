from pathlib import Path
B=Path(__file__).resolve().parent
s=(B.parent/'curvature/curvature.mjs').read_text(encoding='utf-8-sig').split('const GROOT=')[0]
s=s.replace("const BUILD=WORK+'/build/curvature'","const BUILD=WORK+'/build/notation'")
s=s.replace("BUILD+'/source-before-curvature.pptx'","BUILD+'/source-before-notation.pptx'")
s=s[:s.index('function nativeChart(')]+s[s.index('function chart('):]
(B/'notation.mjs').write_text(s+(B/'content.mjs').read_text(encoding='utf-8'),encoding='utf-8')
for name in ['render_release.mjs','package_preview.py']:
    s=(B.parent/'curvature'/name).read_text(encoding='utf-8-sig')
    s=s.replace("'/build/curvature'","'/build/notation'")
    s=s.replace('中期报告_能带曲率与波包设计_预览.pdf','中期报告_统一物理符号版_预览.pdf')
    s=s.replace('能带高斯曲率与波包初步设计','能带几何与波包设计：统一物理符号')
    s=s.replace('!==18','!==19').replace('rendered 18 slides','rendered 19 slides')
    s=s.replace("['slide_count']==18","['slide_count']==19").replace('len(renders)==18','len(renders)==19').replace('len(check)==18','len(check)==19')
    s=s.replace("'slides':18","'slides':19").replace('assert frames==[61]','assert frames==[61,61]')
    s=s.replace('中期报告_统一物理符号版_预览.pdf','中期报告_统一符号与传播优化版_预览.pdf')
    (B/name).write_text(s,encoding='utf-8')
