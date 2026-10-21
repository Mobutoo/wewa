"""Refresh this resume's new deliveries after the requested independent neutral96 view."""
import json,sys,subprocess,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];name=sys.argv[1]
assert name in ['brake-pedal-textured-pad-v1','carburettor-upper-casting-v1','crankcase-lh-output-panel-v1','centre-stand-main-frame-v1']
O=R/'creative/reviews'/name;d=json.loads((O/'delivery.json').read_text());report=json.loads((O/'final-render-report.json').read_text());review=json.loads((O/'final-review.json').read_text())
assert len(report['views'])>=3 and all(v['samples']==96 for v in report['views'])
assert 'final-neutral-independent.png' in review['views_read']
archive=O/'delivery-before-neutral96.json'
if not archive.exists():shutil.copyfile(O/'delivery.json',archive)
fragment=json.loads((O/'catalog-fragment.json').read_text());cmd=[sys.executable,str(R/'tools/powertrain_completion_freeze.py'),name,d['package'],d['component_id'],name]
for p in [*[r['path']for r in d['exact_build_scripts']],'tools/powertrain_resumption_neutral96_v1.py','tools/powertrain_resumption_refreeze_v1.py']:
 cmd.extend(['--script',p])
for p in fragment['children_delivered']:cmd.extend(['--child',p])
for p in fragment['remaining']:cmd.extend(['--remaining',p])
subprocess.run(cmd,cwd=R,check=True)
new=json.loads((O/'delivery.json').read_text());bad=[p['path']for p in new['files']if hashlib.sha256((R/p['path']).read_bytes()).hexdigest()!=p['sha256']];assert not bad
print(json.dumps({'review':name,'native96_views':len(report['views']),'files':len(new['files']),'hash_mismatches':bad}))
