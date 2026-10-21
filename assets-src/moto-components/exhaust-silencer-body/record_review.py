"""Close actual finals against frozen inputs; reception remains separate."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-silencer-body-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pre=H/'preflight-manifest.json';m=json.loads(pre.read_text());source=H/'exhaust-silencer-body-v1.blend';glb=H/'exhaust-silencer-body-inspection.glb';r=json.loads((O/'render-report.json').read_text());assert sha(source)==m['source_sha256']==r['source_sha256']and sha(glb)==m['export_sha256']==r['export_sha256'];assert r['samples']==96 and {v['name']for v in r['views']}=={'right-profile','rear-quarter','front-neck-detail','conditional-header-context'};files=[pre,O/'render-report.json']
for row in m['files']:
 p=R/row['path'];assert sha(p)==row['sha256'];files.append(p)
for row in r['views']:
 p=O/(row['name']+'.checkpoint.json');q=json.loads(p.read_text());assert q['source_sha256']==sha(source)and q['configuration']['samples']==96;assert q['configuration']['render_script_sha256']==sha(H/'render.py')and q['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py');assert q['configuration_sha256']==hashlib.sha256(json.dumps(q['configuration'],sort_keys=True).encode()).hexdigest();files.append(p)
 for item in q['outputs']:
  p=O/item['file'];assert sha(p)==item['sha256'];files.append(p)
x={'component_id':m['component_id'],'revision':m['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'scope':'Four actual96 views of the main shell with unchanged conditional header context. Rear closure/outlet, mounts and heatshield are separate. Sections/local dimensions/hidden expansion, finish and physical fit unreceived. No art/OEM/physical iPhone reception.','all_dimensions_estimated':True,'exact_RDC_identity_confirmed':False,'art_accepted':False,'physical_iphone_tested':False};(O/'review-manifest.json').write_text(json.dumps(x,indent=2)+'\n');print('BOUND_SILENCER_BODY',len(x['files']))
