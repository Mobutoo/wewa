"""Bind finished isolated views to the actual source and export, no art promotion."""
import hashlib,json,re
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/handlebar-grips-v1'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
source=HERE/'handlebar-grips-v1.blend';export=HERE/'handlebar-grips-inspection.glb'
check=json.loads((OUT/'source-geometry-check.json').read_text());gltf=json.loads((OUT/'export-check.json').read_text());render=json.loads((OUT/'render-report.json').read_text())
assert sha(source)==check['source_sha256']==render['source_sha256']
assert sha(export)==check['export_sha256']==gltf['sha256']
assert not gltf['glTF_errors'] and all(row['closed_connected_shells']==1 and not row['non_manifold_edges'] for row in check['checks'])
assert {v['name'] for v in render['views']}=={'left-quarter','right-quarter'}
for name in ['left-quarter','right-quarter']:
 with Image.open(OUT/(name+'.png')) as image:assert image.size==(1100,850)
for doc in [HERE/'README.md',OUT/'README.md',ROOT/'creative/research/handlebar-grips/README.md']:
 for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
  if '://' not in target and not target.startswith('#'):assert (doc.parent/target.split('#')[0]).exists(),(doc,target)
files=[p for folder in [HERE,OUT,ROOT/'creative/research/handlebar-grips'] for p in folder.rglob('*') if p.is_file() and p.suffix not in ['.blend1','.pyc'] and '__pycache__' not in p.parts and p.name!='manifest.json']
manifest={'revision':'handlebar-grips-v1','component_id':'MOTO-HANDLEBAR-GRIPS-001','files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)],'real_blender_views':2,'art_accepted':False,'physical_iphone_tested':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('WEWA_GRIP_MANIFEST',len(files),'files')
