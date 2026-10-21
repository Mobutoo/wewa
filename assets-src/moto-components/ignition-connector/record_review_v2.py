"""Bind actual isolated native finals; no acceptance inherited by other parts."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/ignition-connector-v2';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not(O/'review-manifest.json').exists()
pre=H/'preflight-manifest-v2.json';M=read(pre);report=read(O/'render-report.json');reads=read(O/'author-final-read-progress.json');names={'whole-housing','empty-mouth-not-contacts','wire-shoulder-context','retaining-surface-control'}
assert report['source_sha256']==M['source_sha256']==reads['source_sha256'] and report['export_sha256']==M['export_sha256'] and report['samples']==96
assert {q['name']for q in report['views']}==names and {q['view']for q in reads['actual_images_opened']}==names
assert reads['all_four_read'] and reads['worker_exit_code']==0
files=[pre,O/'render-report.json',O/'author-final-read-progress.json',O/'completion-review.json']
for row in M['files']:
    p=R/row['path'];assert sha(p)==row['sha256'];files.append(p)
for row in report['views']:
    cp=O/(row['name']+'.checkpoint.json');j=read(cp);assert j['source_sha256']==M['source_sha256'] and j['configuration']['samples']==96
    assert j['configuration']['render_script_sha256']==sha(H/'render_v2.py') and j['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py')
    assert j['configuration_sha256']==hashlib.sha256(json.dumps(j['configuration'],sort_keys=True).encode()).hexdigest();files.append(cp)
    for output in j['outputs']:
        p=O/output['file'];assert sha(p)==output['sha256'];files.append(p)
    rowread=next(q for q in reads['actual_images_opened']if q['view']==row['name']);assert rowread['actually_opened'] and rowread['png_sha256']==sha(O/(row['name']+'.png'))
result={k:v for k,v in M.items()if k!='files'};result['files']=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))]
(O/'review-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print('BOUND_CONNECTOR_V2',len(result['files']))
