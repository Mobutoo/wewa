"""Bind three isolated actual96 views; no acceptance of failed head interfaces."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-tappet-cap-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();mf=H/'preflight-manifest.json';pre=json.loads(mf.read_text());src=H/'engine-tappet-cap-v1.blend';glb=H/'engine-tappet-cap-inspection.glb';render=json.loads((O/'render-report.json').read_text());assert sha(src)==pre['source_sha256']==render['source_sha256'];assert sha(glb)==pre['export_sha256']==render['export_sha256'];assert render['samples']==96 and {v['name']for v in render['views']}=={'front-quarter','front-normal','rear-cavity'}
files=[mf,O/'render-report.json']
for row in pre['files']:
 p=R/row['path'];assert sha(p)==row['sha256'];files.append(p)
for row in render['views']:
 p=O/(row['name']+'.checkpoint.json');cp=json.loads(p.read_text());assert cp['source_sha256']==sha(src)and cp['configuration']['samples']==96 and cp['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py')and cp['configuration']['render_script_sha256']==sha(H/'render.py');assert cp['configuration_sha256']==hashlib.sha256(json.dumps(cp['configuration'],sort_keys=True).encode()).hexdigest();files.append(p)
 for x in cp['outputs']:
  p=O/x['file'];assert sha(p)==x['sha256'];files.append(p)
result={'component_id':'MOTO-ENGINE-TAPPET-CAP-001','revision':'engine-tappet-cap-v1','source_sha256':sha(src),'export_sha256':sha(glb),'scope':'Isolatedconditionalcap,2instances,3checkpointed96views. Headinterfaces501/453BLOCKED; nofullfit/OEM/artacceptance.','files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'head_interface_blocked':True,'art_accepted':False,'physical_iphone_tested':False};(O/'review-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print('Bound tappetcap',len(result['files']),'files')
