"""Bind four actual finals with explicit author reads; no artistic acceptance."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/front-brake-upper-sheath-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not(O/'review-manifest.json').exists();pre=H/'preflight-manifest.json';m=json.loads(pre.read_text());source=H/'front-brake-upper-sheath-v1.blend';glb=H/'front-brake-upper-sheath-inspection.glb';report=json.loads((O/'render-report.json').read_text());reads=json.loads((O/'author-final-read-progress.json').read_text());names={'whole-short-departure','control-gap-context','bend-profile','distal-REVIEW-CUT-not-terminal'};assert sha(source)==m['source_sha256']==report['source_sha256']==reads['source_sha256']and sha(glb)==m['export_sha256']==report['export_sha256'];assert report['samples']==96 and{v['name']for v in report['views']}==names;assert reads['all_four_read']and reads['worker_exit_code']==0 and{v['view']for v in reads['actual_images_opened']}==names;files=[pre,O/'render-report.json',O/'author-final-read-progress.json',O/'completion-review.json']
for row in m['files']:
 p=R/row['path'];assert sha(p)==row['sha256'];files.append(p)
for row in report['views']:
 cp=O/(row['name']+'.checkpoint.json');j=json.loads(cp.read_text());assert j['source_sha256']==sha(source)and j['configuration']['samples']==96 and j['configuration']['render_script_sha256']==sha(H/'render.py')and j['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py');assert j['configuration_sha256']==hashlib.sha256(json.dumps(j['configuration'],sort_keys=True).encode()).hexdigest();files.append(cp)
 for out in j['outputs']:
  p=O/out['file'];assert sha(p)==out['sha256'];files.append(p)
 read=next(v for v in reads['actual_images_opened']if v['view']==row['name']);assert read['actually_opened']and read['png_sha256']==sha(O/(row['name']+'.png'))
r={**{k:m[k]for k in ['component_id','revision','source_sha256','export_sha256','scope','all_dimensions_estimated','automatic_attachment_allowed','art_accepted','physical_iphone_tested']},'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))]};(O/'review-manifest.json').write_text(json.dumps(r,indent=2)+'\n');print('BOUND_FRONT_BRAKE_UPPER_SHEATH',len(r['files']))
