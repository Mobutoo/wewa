"""Bind the two changed-pigtail finals, preserving the lower historical proofs."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/cockpit-cables-v3';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert not(O/'review-manifest.json').exists()
pre=H/'preflight-manifest-v3.json';M=read(pre);I=read(H/'render-inputs-v3.json');report=read(O/'render-report.json');reads=read(O/'author-final-read-progress.json')
names={'loop-current-under-context','wireentry-gap-current'}
assert report['source_sha256']==M['source_sha256']==reads['source_sha256'] and report['export_sha256']==M['export_sha256']
assert report['samples']==96 and {q['name'] for q in report['views']}==names
assert reads['all_two_read'] and reads['worker_exit_code']==0 and {q['view'] for q in reads['actual_images_opened']}==names
files=[pre,O/'render-report.json',O/'author-final-read-progress.json',O/'completion-review.json']
for row in M['files']:
    p=R/row['path'];assert sha(p)==row['sha256'];files.append(p)
for row in report['views']:
    cp=O/(row['name']+'.checkpoint.json');j=read(cp);assert j['source_sha256']==M['source_sha256']
    assert j['configuration']['samples']==96 and j['configuration']['render_script_sha256']==sha(H/'render_v3.py') and j['configuration']['protocol_sha256']==sha(H/'render_checkpoint_v3.py')
    assert j['configuration_sha256']==hashlib.sha256(json.dumps(j['configuration'],sort_keys=True).encode()).hexdigest();files.append(cp)
    for output in j['outputs']:
        p=O/output['file'];assert sha(p)==output['sha256'];files.append(p)
    actual=next(q for q in reads['actual_images_opened']if q['view']==row['name']);assert actual['actually_opened']and actual['png_sha256']==sha(O/(row['name']+'.png'))
for key in ['source','export','connector_guide','instruments_guide']:assert sha(R/I[key])==I[key+'_sha256']
result={k:v for k,v in M.items() if k!='files'};result['files']=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(files))]
(O/'review-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print('BOUND_COCKPIT_CABLES_V3',len(result['files']))
