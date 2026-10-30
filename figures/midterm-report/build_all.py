"""Reproduce every simulation, figure, animation, and catalog from the project root."""
from pathlib import Path
import sys
import subprocess
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]

def run(command,name):
    print('Running:',name,flush=True)
    result=subprocess.run(command,cwd=PROJECT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    (ROOT/'logs').mkdir(exist_ok=True)
    (ROOT/'logs'/f'{name}.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
    if result.returncode:
        print(result.stdout);print(result.stderr);raise SystemExit(result.returncode)
    print(result.stdout[-800:],flush=True)

def main():
    run([sys.executable,'-m','unittest','discover','-s','code','-v'],'original-model-tests')
    for name in ['verify_numerics','generate_dispersion','generate_local_flip','generate_gaussian','build_catalog','validate_package']:
        run([sys.executable,str(ROOT/f'{name}.py')],name)
    print('Done. Open',ROOT/'index.html')

if __name__=='__main__':main()
