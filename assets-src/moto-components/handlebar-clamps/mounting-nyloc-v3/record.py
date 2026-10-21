"""Seal own source and proofs; exclude independently maintained parent reports."""
import json,hashlib
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/handlebar-mount-nyloc-v3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((OUT/'source-geometry-check.json').read_text());g=json.loads((OUT/'geometry-check.json').read_text());r=json.loads((OUT/'render-report.json').read_text());assert s['source_sha256']==r['source_sha256']==sha(HERE/'handlebar-mount-nyloc-v3.blend');assert s['export_sha256']==r['export_sha256']==g['sha256']==sha(HERE/'handlebar-mount-nyloc-v3-inspection.glb')and g['technical_passed'];assert r['samples']==96 and {v['name']for v in r['views']}=={'quarter','underside-thread','crown-material'}
for v in r['views']:
 p=OUT/(v['name']+'.png');cp=json.loads((OUT/('checkpoint-'+v['name']+'.json')).read_text());assert cp['PNG_sha256']==sha(p)and cp['source_sha256']==s['source_sha256']and cp['view']['camera_preflight']['technical_preflight_passed']
 with Image.open(p)as im:assert im.size==(1200,1000)
files=[p for p in HERE.rglob('*')if p.is_file()and p.suffix not in['.blend1','.pyc']and'__pycache__'not in p.parts]
files +=[OUT/n for n in['README.md','source-geometry-check.json','geometry-check.json','gray-review.json','material-preview-review.json','geometry-preservation-check.json','material-build-report.json','material-buffer-check.json','render-report.json','helical-edge-buffer-check.json','chamfer-edge-buffer-check.json','insert-normal-buffer-check.json','local-revision-buffer-check.json','material-recipe-preservation-check.json','source-render-review.json']]
files +=list(OUT.glob('gray-*.png'))+list(OUT.glob('preview-*.png'))+list(OUT.glob('preview-*.json'))+list(OUT.glob('reflection-*.png'))+list(OUT.glob('gray-*.json'))+list(OUT.glob('reflection-*.json'))+[OUT/(v['name']+'.png')for v in r['views']]+[OUT/('checkpoint-'+v['name']+'.json')for v in r['views']]+[ROOT/'creative/research/handlebar-clamps/mounting-nyloc-v3.json',ROOT/'creative/research/handlebar-clamps/helical-thread-meshing-note.md']
files +=[p for p in(OUT/'lower-entry-diagnostic').rglob('*')if p.is_file()]
files +=[ROOT/'creative/research/handlebar-clamps/axial-runout-meshing-note-v1.md']
m={'component_id':s['component_id'],'revision':s['revision'],'scope':'One isolated conditional locknut, two solids:metal+nonmetalinsert. Original source/GLB/renders, parent runtime and independent audits excluded.','files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'current_RDC_identity_verified':False,'thread_fit_verified':False,'art_accepted':False,'physical_iphone_tested':False};(OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('WEWA_NYLOC_SEALED',len(set(files)),sha(OUT/'manifest.json'))
