"""Seal this revision's own checked source renders; no implicit artistic reception."""
import json,hashlib
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/fork-bellows-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((OUT/n).read_text())
s=read('source-geometry-check.json');g=read('geometry-check.json');r=read('render-report.json')
assert s['source_sha256']==r['source_sha256']==sha(HERE/'fork-bellows-v2.blend')
assert s['export_sha256']==r['export_sha256']==g['sha256']==sha(HERE/'fork-bellows-v2-inspection.glb') and g['technical_passed']
assert r['samples']==96 and {v['name']for v in r['views']}=={'quarter','lower-opening','compression-estimated','extension-estimated'}
for v in r['views']:
 p=OUT/(v['name']+'.png');c=read('checkpoint-'+v['name']+'.json')
 assert c['PNG_sha256']==sha(p) and c['source_sha256']==s['source_sha256'] and c['export_sha256']==g['sha256']
 assert c['samples']==96 and c['view']['morph_weights']==v['morph_weights']
 assert c['fixture']['render_script_sha256']==sha(HERE/'render.py')
 with Image.open(p)as im:assert im.size==(1000,1200)
for n in ['material-preview-review.json','source-render-review.json']:
 q=read(n);assert q['source_sha256']==s['source_sha256'] and q['export_sha256']==g['sha256'] and q['actually_opened_and_read']
assert read('v1-preservation-end.json')['all_files_verified_unchanged']
assert read('material-preservation-check.json')['geometry_normals_UV_baseTangentW_allMorphDeltas_and_transforms_identical']
assert read('actual-buffer-sections.json')['export_sha256']==g['sha256']
files=[p for p in HERE.rglob('*')if p.is_file()and p.suffix not in['.blend1','.pyc']and'__pycache__'not in p.parts]
files +=[p for p in OUT.rglob('*')if p.is_file()and p.name!='manifest.json']
files +=[ROOT/'creative/research/front-fork/bellows-v2-plan.json']
m={'component_id':s['component_id'],'revision':s['revision'],'scope':'Single revised isolated bellows with grooved mouth, original rubber material and two estimated review-length morphs. Own Blender/actual GLB/source-render checks; parent runtime/independent audits excluded. Historical v1 immutable.','source_sha256':s['source_sha256'],'export_sha256':g['sha256'],'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'all_metric_dimensions_estimated':True,'RDC_code_and_contact_verified':False,'manufacturer_travel_verified':False,'art_accepted':False,'physical_iphone_tested':False}
(OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('BELLOWS_V2_SEALED',len(files),sha(OUT/'manifest.json'))
