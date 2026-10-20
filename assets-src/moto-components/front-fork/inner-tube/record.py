"""Seal this isolated component, excluding mutable independent/runtime reports."""
import json,hashlib
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/front-fork-inner-tube-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((OUT/'source-geometry-check.json').read_text());g=json.loads((OUT/'geometry-check.json').read_text());r=json.loads((OUT/'render-report.json').read_text());assert s['source_sha256']==r['source_sha256']==sha(HERE/'front-fork-inner-tube-v1.blend');assert s['export_sha256']==r['export_sha256']==g['sha256']==sha(HERE/'front-fork-inner-tube-inspection.glb') and g['technical_passed'];assert r['samples']==96 and {v['name'] for v in r['views']}=={'whole','upper-thread','lower-machining'}
for v in r['views']:
 p=OUT/(v['name']+'.png');cp=json.loads((OUT/('checkpoint-'+v['name']+'.json')).read_text());assert cp['PNG_sha256']==sha(p) and cp['source_sha256']==s['source_sha256']
 with Image.open(p) as im:assert im.size==(1000,1200)
files=[p for p in HERE.rglob('*') if p.is_file() and p.suffix not in ['.blend1','.pyc'] and '__pycache__' not in p.parts];files+=[ROOT/'creative/research/front-fork/inner-tube-v1.json'];files+=[OUT/f for f in ['README.md','source-geometry-check.json','geometry-check.json','material-build-report.json','material-buffer-check.json','render-report.json']];files+=[OUT/(v['name']+ext) for v in r['views'] for ext in ['.png']];files+=[OUT/('checkpoint-'+v['name']+'.json') for v in r['views']];m={'component_id':s['component_id'],'revision':s['revision'],'scope':'Single isolated related tube, original source + actual GLB + source renders. Independent/runtime parent reports excluded.','files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)],'art_accepted':False,'physical_iphone_tested':False};(OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('WEWA_TUBE_SEALED',len(files))
