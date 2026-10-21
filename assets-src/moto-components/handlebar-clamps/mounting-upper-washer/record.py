"""Seal original source and component proofs only after all final images are read."""
import json,hashlib
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/handlebar-mount-upper-washer-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((OUT/'source-geometry-check.json').read_text());g=json.loads((OUT/'geometry-check.json').read_text());r=json.loads((OUT/'render-report.json').read_text());v=json.loads((OUT/'source-render-review.json').read_text());ss=sha(HERE/'handlebar-mount-upper-washer-v1.blend');es=sha(HERE/'handlebar-mount-upper-washer-inspection.glb');assert s['source_sha256']==g['source_sha256']==r['source_sha256']==v['source_sha256']==ss and s['export_sha256']==g['sha256']==r['export_sha256']==v['export_sha256']==es and g['technical_passed'];names={'quarter','reverse','face-material'};assert r['samples']==96 and{q['name']for q in r['views']}==names and set(v['images_actually_read'])==names
for name in names:
 p=OUT/(name+'.png');cp=json.loads((OUT/('checkpoint-'+name+'.json')).read_text());assert cp['source_sha256']==ss and cp['export_sha256']==es and cp['PNG_sha256']==sha(p)and cp['view']['camera_preflight']['technical_preflight_passed']
 with Image.open(p)as im:assert im.size==(1200,1000)
files=[p for p in HERE.rglob('*')if p.is_file()and p.suffix not in['.blend1','.pyc']and'__pycache__'not in p.parts];files +=[OUT/n for n in['README.md','source-geometry-check.json','geometry-check.json','gray-review.json','material-preview-review.json','material-build-report.json','material-buffer-check.json','geometry-preservation-check.json','render-report.json','source-render-review.json']]
for pattern in['gray-*.png','gray-*.json','reflection-*.png','reflection-*.json','preview-*.png','preview-*.json']:files+=list(OUT.glob(pattern))
for name in names:files +=[OUT/(name+'.png'),OUT/('checkpoint-'+name+'.json')]
files +=[ROOT/'creative/research/handlebar-clamps/mounting-upper-washer-v1.json'];files=sorted(set(files));m={'component_id':s['component_id'],'revision':s['revision'],'scope':'One isolated conditional upper washer, not lowerwasher or damper. All physical dimensions and unseen lower face estimated. Parent runtime and independent documentary matrix excluded.','files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in files],'current_RDC_identity_verified':False,'all_physical_dimensions_estimated':True,'lower_face_observed':False,'installed_orientation_or_stack_fit_verified':False,'art_accepted':False,'physical_iphone_tested':False};(OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('WEWA_UPPER_WASHER_SEALED',len(files),sha(OUT/'manifest.json'))
