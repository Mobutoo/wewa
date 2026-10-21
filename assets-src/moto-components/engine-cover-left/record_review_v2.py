from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-cover-left-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();manifest=H/'preflight-manifest-v2.json';pre=json.loads(manifest.read_text());source=H/'engine-cover-left-v2.blend';glb=H/'engine-cover-left-v2-inspection.glb';render=json.loads((O/'render-report.json').read_text());assert pre['source_sha256']==sha(source)==render['source_sha256'];assert pre['export_sha256']==sha(glb)==render['export_sha256'];assert render['samples']==96;assert {v['name']for v in render['views']}=={'outer-forward-boss','rear-hollow-shell','front-fixation-transition','rear-fixation-root'},'All four final views are required'
paths=[manifest,O/'render-report.json']
for row in pre['files']:
 p=R/row['path'];assert sha(p)==row['sha256'];paths.append(p)
for v in render['views']:
 p=O/(v['name']+'.checkpoint.json');j=json.loads(p.read_text());assert j['source_sha256']==sha(source) and j['configuration']['samples']==96 and j['configuration']['protocol_sha256']==sha(H/'render_checkpoint_v2.py');assert j['configuration']['render_script_sha256']==sha(H/'render_v2.py');paths.append(p)
 for row in j['outputs']:
  p=O/row['file'];assert sha(p)==row['sha256'];paths.append(p)
(O/'review-manifest.json').write_text(json.dumps({'revision':'engine-cover-left-v2','source_sha256':sha(source),'export_sha256':sha(glb),'scope':'Integrated fixation patch geometry revision, retained estimated collar planes and centres, checkpointed96 proofs; no art reception','files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(paths))],'art_accepted':False,'physical_iphone_tested':False},indent=2)+'\n');print('Bound LH coverv2',len(set(paths)),'files')
