"""Seal local component evidence without promoting artistic acceptance."""
import json,hashlib,re
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/handlebar-v1';RESEARCH=ROOT/'creative/research/handlebar'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
source=json.loads((OUT/'source-geometry-check.json').read_text());export=json.loads((OUT/'geometry-check.json').read_text());render=json.loads((OUT/'render-report.json').read_text())
assert source['source_sha256']==sha(HERE/'handlebar-v1.blend')==render['source_sha256']
assert source['export_sha256']==sha(HERE/'handlebar-inspection.glb')==export['sha256']==render['export_sha256']
assert source['connected_wall_shells']==1 and source['non_manifold_edges']==0 and export['technical_passed']
assert {v['name'] for v in render['views']}=={'quarter','cockpit','clamp-detail'}
for view in render['views']:
 with Image.open(OUT/(view['name']+'.png')) as image:assert image.size==(1400,900)
for path in [HERE/'README.md',OUT/'README.md',RESEARCH/'README.md']:
 for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
  if '://' not in target:assert (path.parent/target).exists(),(path,target)
files=sorted(p for folder in [HERE,OUT,RESEARCH] for p in folder.rglob('*') if p.is_file() and p.name!='manifest.json' and p.suffix not in ['.blend1','.pyc'] and '__pycache__' not in p.parts)
manifest={'component_id':'MOTO-HANDLEBAR-001','revision':'handlebar-v1','scope':'Bare tube source, actual isolated source renders and checked GLB, no user reception','files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files],'art_accepted':False,'physical_iphone_tested':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('WEWA_HANDLEBAR_EVIDENCE',len(files),'hashed files')
