"""Seal only this agent's verified evidence; runtime proofs are maintained by parent."""
import json,hashlib,re
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instrument-bracket-v1';RESEARCH=ROOT/'creative/research/instrument-bracket'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((OUT/'source-geometry-check.json').read_text());g=json.loads((OUT/'geometry-check.json').read_text());r=json.loads((OUT/'render-report.json').read_text())
assert s['source_sha256']==sha(HERE/'instrument-bracket-v1.blend')==r['source_sha256']
assert s['export_sha256']==sha(HERE/'instrument-bracket-inspection.glb')==g['sha256'] and g['technical_passed']
assert {v['name'] for v in r['views']}==set(['front-quarter', 'reverse-quarter']) and r['samples']==96
for view in ['front-quarter', 'reverse-quarter']:
 with Image.open(OUT/(view+'.png')) as img:assert list(img.size)==[1200, 1000]
for p in [HERE/'README.md',OUT/'README.md',RESEARCH/'README.md']:
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if '://' not in target:assert (p.parent/target).exists(),(p,target)
# The rendered scene is the Blender source. Associated GLB is separately checked,
# never represented as a source render or substituted for engine captures.
r['rendered_scene']='source_blend';r['associated_export_sha256']=g['sha256'];(OUT/'render-report.json').write_text(json.dumps(r,indent=2)+'\n')
files=[p for folder in [HERE,RESEARCH] for p in folder.rglob('*') if p.is_file() and p.suffix not in ['.blend1','.pyc'] and '__pycache__' not in p.parts]
files += [OUT/f for f in ['README.md','source-geometry-check.json','geometry-check.json','render-report.json','material-build-report.json','material-buffer-check.json']+[v+'.png' for v in ['front-quarter', 'reverse-quarter']]]
manifest={'component_id':'MOTO-INSTRUMENT-BRACKET-001','revision':'instrument-bracket-v1','scope':'Independent candidate source, checked actual GLB, source renders; parent engine proofs excluded intentionally','files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)],'art_accepted':False,'physical_iphone_tested':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('WEWA_SEALED','instrument-bracket',len(files),'files')
