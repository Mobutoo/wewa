"""Bind four actual96 views to frozen original conditional UG5 head candidate."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-head-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();manifest=H/'preflight-manifest-v2.json';pre=json.loads(manifest.read_text());source=H/'engine-head-v2.blend';glb=H/'engine-head-v2-inspection.glb';render=json.loads((O/'render-report.json').read_text());assert sha(source)==pre['source_sha256']==render['source_sha256'];assert sha(glb)==pre['export_sha256']==render['export_sha256'];assert render['samples']==96;assert{v['name']for v in render['views']}=={'OHC-side-quarter','opposite-plug-well','top-fork-and-stud-columns','lower-mating-passages'}
files=[manifest,O/'render-report.json']
for row in pre['files']:
 p=R/row['path'];assert sha(p)==row['sha256'];files.append(p)
for v in render['views']:
 p=O/(v['name']+'.checkpoint.json');j=json.loads(p.read_text());assert j['source_sha256']==sha(source)and j['configuration']['samples']==96 and j['configuration']['protocol_sha256']==sha(H/'render_checkpoint_v2.py')and j['configuration']['render_script_sha256']==sha(H/'render_v2.py');assert j['configuration_sha256']==hashlib.sha256(json.dumps(j['configuration'],sort_keys=True).encode()).hexdigest();files.append(p)
 for row in j['outputs']:
  p=O/row['file'];assert sha(p)==row['sha256'];files.append(p)
(O/'review-manifest.json').write_text(json.dumps({'component_id':'MOTO-ENGINE-HEAD-001','revision':'engine-head-v2','source_sha256':sha(source),'export_sha256':sha(glb),'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'scope':'Exterior UG5 head estimated casting candidate, actual4checkpointed96views, no OEM/art acceptance','all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False},indent=2)+'\n');print('Bound head',len(set(files)),'files')
