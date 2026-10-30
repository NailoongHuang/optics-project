"""Publish the verified exact bytes while detecting intervening source edits."""
from pathlib import Path
import hashlib,json,shutil
B=Path(__file__).resolve().parent
W=B.parent.parent
out=W/'output'
meta=json.loads((B/'build_result.json').read_text())
receipt=json.loads((B/f"validation-r{meta['revision']}.json").read_text())
delivery=json.loads((B/'delivery_check.json').read_text())
assert delivery['passed'] and delivery['slides']==18
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
old_sha=sha(B/'source-before-curvature.pptx')
old_pdf_sha=sha(B/'source-before-curvature.pdf')
for name in ['中期报告_18页优化版.pptx','中期报告_单磁子传播.pptx']:
    assert sha(out/name)==old_sha, 'Intervening human edit: '+name
for name in ['中期报告_18页优化版_预览.pdf','midterm-report-preview.pdf']:
    assert sha(out/name)==old_pdf_sha, 'Intervening human edit: '+name
ppt=out/meta['release']
assert sha(ppt)==receipt['finalSha256']
for name in ['中期报告_能带曲率与波包设计.pptx','中期报告_18页优化版.pptx','中期报告_单磁子传播.pptx']:
    shutil.copyfile(ppt,out/name)
    assert sha(out/name)==receipt['finalSha256']
pdf=out/'中期报告_能带曲率与波包设计_预览.pdf'
for name in ['中期报告_18页优化版_预览.pdf','midterm-report-preview.pdf']:
    shutil.copyfile(pdf,out/name)
    assert sha(out/name)==sha(pdf)
review=dict(passed=True,reviewed_slides=list(range(1,19)),
 visual_review='Full-size exported-PPTX renders, changed pages rechecked after revision 2; preview PDF rendered and inspected; embedded animation initial/middle/end inspected',
 science_checks=['checks_symbolic.json','checks.json','checks_independent.json'],
 scope='18 slides including cover, exact 3x3 extended-zone maps and 9 controlled propagation cases',
 removed_from_deck=['single-site excitation','front propagation','Bessel validation appendix','redundant wave animations','extended microscopic matrix derivation'],
 retained_source='Source PDF, raw simulations and previous PPTX/PDF preserved',
 caveats=['dimensionless graph curvature, not Berry curvature','same width/time, unequal distances','finite spectrum and cubic residual remain','PowerPoint application playback not tested'],
 pptx_sha256=sha(out/'中期报告_能带曲率与波包设计.pptx'),pdf_sha256=sha(pdf))
(B/'review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'published':True,'slides':18,'pptx_sha256':review['pptx_sha256'],'pdf_sha256':review['pdf_sha256']},indent=2))
