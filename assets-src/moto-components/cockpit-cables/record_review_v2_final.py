"""Bind current local loop correction to its two actual final96 views."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/cockpit-cables-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();mf=H/'preflight-final-supplement-v2.json';pre=json.loads(mf.read_text());src=H/'cockpit-cables-v2.blend';glb=H/'cockpit-cables-v2-inspection.glb';render=json.loads((O/'render-report.json').read_text());assert sha(src)==pre['source_sha256']==render['source_sha256'];assert sha(glb)==pre['export_sha256']==render['export_sha256'];assert render['samples']==96 and {v['name']for v in render['views']}=={'ignition-pigtail-free-end','ignition-interface-current'}
files=[mf,O/'render-report.json']
for row in pre['files']:
 p=R/row['path'];assert sha(p)==row['sha256'];files.append(p)
for row in render['views']:
 p=O/(row['name']+'.checkpoint.json');cp=json.loads(p.read_text());assert cp['source_sha256']==sha(src)and cp['configuration']['samples']==96 and cp['configuration']['protocol_sha256']==sha(H/'render_checkpoint_v2.py')and cp['configuration']['render_script_sha256']==sha(H/'render_v2_final.py');assert cp['configuration_sha256']==hashlib.sha256(json.dumps(cp['configuration'],sort_keys=True).encode()).hexdigest();files.append(p)
 for x in cp['outputs']:
  p=O/x['file'];assert sha(p)==x['sha256'];files.append(p)
result={'component_id':'MOTO-COCKPIT-CABLES-001','revision':'cockpit-cables-v2','source_sha256':sha(src),'export_sha256':sha(glb),'scope':'Localconditionalcontactloop correction, actual2checkpointed96views.2lowerexportbuffers invariant, no fullharness/connector orOEMqualification.','files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'art_accepted':False,'physical_iphone_tested':False};(O/'review-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print('Bound cablesv2',len(result['files']),'files')
