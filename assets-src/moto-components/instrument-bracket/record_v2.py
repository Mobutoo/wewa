"""Seal explicit v2 files only; do not modify or re-manifest historical v1."""
import json,hashlib
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instrument-bracket-v2';RESEARCH=ROOT/'creative/research/instrument-bracket'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((ROOT/'creative/reviews/instrument-bracket-v1/manifest.json').read_text())
for f in old['files']:assert sha(ROOT/f['path'])==f['sha256'],f['path']
s=json.loads((OUT/'source-geometry-check.json').read_text());g=json.loads((OUT/'geometry-check.json').read_text());r=json.loads((OUT/'render-report.json').read_text());assert s['source_sha256']==r['source_sha256']==sha(HERE/'instrument-bracket-v2.blend');assert s['export_sha256']==r['export_sha256']==g['sha256']==sha(HERE/'instrument-bracket-v2-inspection.glb') and g['technical_passed'];assert r['samples']==96 and {v['name'] for v in r['views']}=={'front-quarter','reverse-quarter'}
for v in r['views']:
 with Image.open(OUT/(v['name']+'.png')) as im:assert im.size==(1200,1000)
files=[HERE/f for f in ['README_v2.md','parameters-v2.json','provenance-v2.json','build_v2.py','material_v2.py','check_export_v2.mjs','inspect_material_v2.py','render_v2.py','record_v2.py','instrument-bracket-v2.blend','instrument-bracket-v2-inspection.glb','build-report-v2.json']];files+=list((HERE/'textures-v2').glob('*.png'));files+=[RESEARCH/'rib-v2-README.md',RESEARCH/'rib-v2-observations.json'];files+=[OUT/f for f in ['README.md','source-geometry-check.json','geometry-check.json','material-build-report.json','material-buffer-check.json','render-report.json','front-quarter.png','reverse-quarter.png','checkpoint-front-quarter.json','checkpoint-reverse-quarter.json']]
r={'component_id':'MOTO-INSTRUMENT-BRACKET-001','revision':'instrument-bracket-v2','scope':'Independent source, checked GLB, source renders. Parent runtime and independent audit proofs excluded.','historical_v1_files_verified_unchanged':len(old['files']),'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)],'art_accepted':False,'physical_iphone_tested':False};(OUT/'manifest.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_SEALED_BRACKET_V2',len(files))
