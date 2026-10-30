"""Extract existing and newly computed trajectories for native presentation charts."""
from pathlib import Path
import numpy as np,json
root=Path(__file__).resolve().parents[4]
new=root/'figures/midterm-report/dense-wave'
d=np.load(new/'dense_wave_data.npz')
out={'source':str(new/'dense_wave_data.npz'),'cases':{}}
for name in ['x_eta1','x_eta03','diagonal_eta1','diagonal_eta03']:
    out['cases'][name]={k:d[name+'_trajectory_'+k].tolist() for k in ['t','cx','cy','wx','wy','norm']}
out['checks']=json.loads((new/'checks.json').read_text(encoding='utf-8'))
Path(__file__).with_name('dense_chart_data.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved exact dense-wave chart trajectories')
