"""Bind six actual96 views to this frozen candidate, art reception remains separate."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/front-footrest-left-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pre=H/'preflight-manifest.json';m=json.loads(pre.read_text());source=H/'front-footrest-left-v1.blend';glb=H/'front-footrest-left-inspection.glb';r=json.loads((O/'render-report.json').read_text());assert sha(source)==m['source_sha256']==r['source_sha256']and sha(glb)==m['export_sha256']==r['export_sha256'];assert r['samples']==96 and{v['name']for v in r['views']}=={'outer-quarter','plate-reverse','tube-tabs-side','formed-base-weld-detail','tube-open-rim-detail','grain-raking-control'};files=[pre,O/'render-report.json']
for row in m['files']:
 p=R/row['path'];assert sha(p)==row['sha256'];files.append(p)
for row in r['views']:
 cp=O/(row['name']+'.checkpoint.json');q=json.loads(cp.read_text());assert q['source_sha256']==sha(source)and q['configuration']['samples']==96;assert q['configuration']['render_script_sha256']==sha(H/'render.py')and q['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py');assert q['configuration_sha256']==hashlib.sha256(json.dumps(q['configuration'],sort_keys=True).encode()).hexdigest();files.append(cp)
 for item in q['outputs']:
  p=O/item['file'];assert sha(p)==item['sha256'];files.append(p)
x={'component_id':m['component_id'],'revision':m['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'scope':'Six actual96 isolated views, uncalibrated. CurrentRDC identity/dimensions, hidden sections/post function/weld strength and frame/rubber fit unreceived. Original coating grain scale/optical finish remain G4open; no source photo pixels. One physical metal support assembly only.','all_dimensions_estimated':True,'automatic_attachment_allowed':False,'art_accepted':False,'physical_iphone_tested':False};(O/'review-manifest.json').write_text(json.dumps(x,indent=2)+'\n');print('BOUND_FOOTREST_LH',len(x['files']))
