"""Publish verified files without overwriting intervening human source edits."""
from pathlib import Path
import hashlib,json,shutil
B=Path(__file__).resolve().parent;W=B.parent.parent;out=W/'output'
meta=json.loads((B/'build_result.json').read_text());delivery=json.loads((B/'delivery_check.json').read_text())
receipt=json.loads((B/f"validation-r{meta['revision']}.json").read_text());audit=json.loads((B/'notation_audit.json').read_text())
assert delivery['passed'] and audit['passed'] and delivery['slides']==19
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['中期报告_能带曲率与波包设计.pptx','中期报告_单磁子传播.pptx']:
    assert sha(out/name)==sha(B/'source-before-notation.pptx'), 'Intervening source edit: '+name
for name in ['中期报告_能带曲率与波包设计_预览.pdf','midterm-report-preview.pdf']:
    assert sha(out/name)==sha(B/'source-before-notation.pdf'), 'Intervening source edit: '+name
ppt=out/meta['release'];assert sha(ppt)==receipt['finalSha256']
for name in ['中期报告_统一符号与传播优化版.pptx','中期报告_能带曲率与波包设计.pptx','中期报告_单磁子传播.pptx']:
    shutil.copyfile(ppt,out/name);assert sha(out/name)==receipt['finalSha256']
pdf=out/'中期报告_统一符号与传播优化版_预览.pdf'
for name in ['中期报告_能带曲率与波包设计_预览.pdf','midterm-report-preview.pdf']:
    shutil.copyfile(pdf,out/name);assert sha(out/name)==sha(pdf)
result=dict(passed=True,slides=19,visual_reviewed_slides=list(range(1,20)),
    inspection='All final exported slides reviewed at full size. Fixed-coordinate GIF initial/middle/end frames reviewed. Both embedded GIF byte hashes match the checked laboratory assets.',
    notation_audit=audit,delivery_check=delivery,pptx_sha256=sha(ppt),pdf_sha256=sha(pdf),
    source_preserved='source-before-notation.pptx and source-before-notation.pdf',
    limitations=['PDF is static','Native PowerPoint playback not tested','Original finite-time scientific scope preserved'])
(B/'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(published=True,slides=19,pptx_sha256=sha(ppt),pdf_sha256=sha(pdf)),indent=2))
