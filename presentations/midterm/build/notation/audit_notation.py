"""Check rendered-label contracts, unchanged chart data and embedded GIF identities."""
from pathlib import Path
from zipfile import ZipFile
import re,json,hashlib
import numpy as np
B=Path(__file__).resolve().parent;PROJECT=B.parents[3]
spec=json.loads((B/'slide_spec.json').read_text())
data=json.loads((PROJECT/'figures/midterm-report/curvature-design/chart_data.json').read_text())['cases']
assert len(spec)==19
bad=re.compile(r'q[ₓᵧ₀]|n[ₓᵧ]|\bq_[xy]\b|\bn_[xy]\b|\bq[xy]\b|[ητ]|s\s*=\s*σ|Eꜰ')
for slide in spec:
    strings=[slide['title'],slide['source'],*slide['text']]
    for text in strings:assert not bad.search(text),(slide['number'],text)
    for chart in slide['charts']:
        field={'rms_x':'wx','rms_y':'wy','fidelity_main':'fidelity','fidelity_width':'fidelity','anisotropy_rms':'wy'}[chart['key']]
        keys=['C_sigma4','C_sigma6','C_sigma8'] if chart['key']=='fidelity_width' else ['B_eta1','B_eta03'] if chart['key']=='anisotropy_rms' else ['A_eta1','B_eta1','C_eta1']
        for series,key in zip(chart['series'],keys):
            assert np.array_equal(series['xValues'],data[key]['track']['t'])
            assert np.array_equal(series['values'],data[key]['track'][field])
    for asset in slide['assets']:
        path=Path(asset['path']);svg=path.with_suffix('.svg')
        if svg.exists():
            labels='\n'.join(re.findall(r'<!--(.*?)-->',svg.read_text(encoding='utf-8'),re.S))
            assert not bad.search(labels),(slide['number'],str(svg),bad.search(labels).group(0))
meta=json.loads((B/'build_result.json').read_text());ppt=B.parent.parent/'output'/meta['release']
groot=PROJECT/'figures/midterm-report/notation'
expected={hashlib.sha256((groot/f'{name}.gif').read_bytes()).hexdigest() for name in ['g14_lab_probability_animation','g15_lab_real_animation']}
with ZipFile(ppt) as z:
    actual={hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist() if name.endswith('.gif')}
assert actual==expected
checks=json.loads((groot/'checks_lab_animation.json').read_text());assert checks['passed']
for item in checks['items']:
    assert item['laboratory_limits_a']==[-35,225]
    assert item['min_mass_in_view']>.99999999
result=dict(passed=True,slides=19,unchanged_native_chart_count=sum(len(s['charts']) for s in spec),
    forbidden_aliases_absent=True,embedded_gifs_match_fixed_lab_assets=True,
    min_probability_in_fixed_view=min(i['min_mass_in_view'] for i in checks['items']),
    numerical_source_unchanged_sha256=hashlib.sha256((PROJECT/'figures/midterm-report/curvature-design/design_data.npz').read_bytes()).hexdigest())
(B/'notation_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
