"""Verify the exact released PPTX, embedded media, and final round-trip renders."""
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
import io,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parent.parent
p=ROOT/'output/中期报告_单磁子传播.pptx'
receipt=json.loads((ROOT/'build/中期报告_单磁子传播.pptx.validation.json').read_text(encoding='utf-8'))
assert hashlib.sha256(p.read_bytes()).hexdigest()==receipt['finalSha256']
assert receipt['packageIntegrity']['slide_count']==35
assert receipt['packageIntegrity']['finding_count']==0
assert receipt['presentationLayout']['finding_count']==0
assert receipt['presentationLayout']['warning_count']==0
gifs=[]
with ZipFile(p) as z:
    for name in z.namelist():
        if name.endswith('.gif'):
            im=Image.open(io.BytesIO(z.read(name)))
            for k in range(im.n_frames): im.seek(k);im.load()
            gifs.append({'part':name,'frames':im.n_frames})
assert sorted(g['frames'] for g in gifs)==[61,65,73]
differences=[]
for f in sorted((ROOT/'build/renders').glob('slide-*.png')):
    a=np.array(Image.open(f).convert('RGB'),dtype=float)
    b=np.array(Image.open(ROOT/'build/final-renders'/f.name).convert('RGB'),dtype=float)
    differences.append(float(np.abs(a-b).mean()))
assert len(differences)==35 and max(differences)<.01
result={'status':'passed','final_sha256':receipt['finalSha256'],'slides':35,
 'charts':receipt['packageIntegrity']['chart_count'],'embedded_gifs':gifs,
 'final_render_count':len(differences),'max_roundtrip_pixel_mae':max(differences),
 'powerpoint_application_playback_tested':False}
(ROOT/'build/delivery_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
