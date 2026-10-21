"""Seal own finished proofs only; root runtime and independent reports excluded."""
import json,hashlib
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/fork-bellows-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((OUT/'source-geometry-check.json').read_text());g=json.loads((OUT/'geometry-check.json').read_text());r=json.loads((OUT/'render-report.json').read_text())
assert s['source_sha256']==r['source_sha256']==sha(HERE/'fork-bellows-v1.blend')
assert s['export_sha256']==r['export_sha256']==g['sha256']==sha(HERE/'fork-bellows-inspection.glb') and g['technical_passed']
assert r['samples']==96 and {v['name']for v in r['views']}=={'quarter','lower-opening','compression-estimated','extension-estimated'}
for v in r['views']:
 p=OUT/(v['name']+'.png');cp=json.loads((OUT/('checkpoint-'+v['name']+'.json')).read_text())
 assert cp['PNG_sha256']==sha(p) and cp['source_sha256']==s['source_sha256'] and cp['view']['morph_weights']==v['morph_weights']
 with Image.open(p)as im:assert im.size==(1000,1200)
files=[p for p in HERE.rglob('*')if p.is_file()and p.suffix not in['.blend1','.pyc']and'__pycache__'not in p.parts]
names=['README.md','source-geometry-check.json','geometry-check.json','meridian-preflight.json','morph-tangent-compatibility-check.json','converter-preservation-check.json','material-preservation-check.json','gray-review.json','material-preview-review.json','material-build-report.json','material-buffer-check.json','render-report.json']
files +=[OUT/n for n in names]+list(OUT.glob('gray-*.png'))+list(OUT.glob('preview-*.png'))
files +=[OUT/(v['name']+'.png')for v in r['views']]+[OUT/('checkpoint-'+v['name']+'.json')for v in r['views']]
files +=[ROOT/'creative/research/front-fork/bellows-v1.json']
m={'component_id':s['component_id'],'revision':s['revision'],'scope':'Single isolated original bellows; Blender source, GLB buffers, estimated review morphs and source renders. Root runtime and independent audit excluded.','files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(files)],'manufacturer_travel_verified':False,'art_accepted':False,'physical_iphone_tested':False}
(OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('WEWA_BELLOWS_SEALED',len(files),sha(OUT/'manifest.json'))
