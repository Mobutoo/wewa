"""Bind actual three96 views to an immutable preflight, no source mutation."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-ohc-stub-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();manifest=H/'preflight-manifest.json';pre=json.loads(manifest.read_text());src=H/'engine-ohc-stub-v1.blend';glb=H/'engine-ohc-stub-inspection.glb';render=json.loads((O/'render-report.json').read_text());assert sha(src)==pre['source_sha256']==render['source_sha256'];assert sha(glb)==pre['export_sha256']==render['export_sha256'];assert render['samples']==96 and{v['name']for v in render['views']}=={'tube-quarter','mouth-end','cover-interface'}
files=[manifest,O/'render-report.json']
for row in pre['files']:
 p=R/row['path'];assert sha(p)==row['sha256'];files.append(p)
for v in render['views']:
 p=O/(v['name']+'.checkpoint.json');j=json.loads(p.read_text());assert j['source_sha256']==sha(src)and j['configuration']['samples']==96 and j['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py')and j['configuration']['render_script_sha256']==sha(H/'render.py');assert j['configuration_sha256']==hashlib.sha256(json.dumps(j['configuration'],sort_keys=True).encode()).hexdigest();files.append(p)
 for row in j['outputs']:
  p=O/row['file'];assert sha(p)==row['sha256'];files.append(p)
(O/'review-manifest.json').write_text(json.dumps({'component_id':pre['component_id'],'revision':pre['revision'],'source_sha256':sha(src),'export_sha256':sha(glb),'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'scope':'Three actual checkpointed96 views of original conditional tube; measurements, exact variant and material remain open.','all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False},indent=2)+'\n');print('Bound OHC stub',len(set(files)),'files')
