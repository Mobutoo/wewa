"""Close only actual final rendered views against every immutable input pin."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-insulator-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pre=H/'preflight-manifest.json';m=json.loads(pre.read_text());source=H/'engine-intake-insulator-v1.blend';glb=H/'engine-intake-insulator-inspection.glb'
r=json.loads((O/'render-report.json').read_text());assert sha(source)==m['source_sha256']==r['source_sha256'];assert sha(glb)==m['export_sha256']==r['export_sha256']
assert r['samples']==96 and {v['name']for v in r['views']}=={'front-face','front-quarter','estimated-reverse','groove-ear-detail','conditional-head-context'}
files=[pre,O/'render-report.json']
for row in m['files']:
    p=R/row['path'];assert sha(p)==row['sha256'];files.append(p)
for row in r['views']:
    p=O/(row['name']+'.checkpoint.json');q=json.loads(p.read_text());assert q['source_sha256']==sha(source)and q['configuration']['samples']==96
    assert q['configuration']['render_script_sha256']==sha(H/'render.py')and q['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py')
    assert q['configuration_sha256']==hashlib.sha256(json.dumps(q['configuration'],sort_keys=True).encode()).hexdigest();files.append(p)
    for item in q['outputs']:
        p=O/item['file'];assert sha(p)==item['sha256'];files.append(p)
result={'component_id':m['component_id'],'revision':m['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),
        'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],
        'scope':'Five actual96 views, including intentionally estimated reverse and conditional head3 context. No measured material, metric/RDC/OEM fit, mobile hardware or artistic reception.',
        'all_dimensions_estimated':True,'exact_RDC_identity_confirmed':False,'art_accepted':False,'physical_iphone_tested':False}
(O/'review-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print('Bound intake insulator',len(result['files']),'files')
