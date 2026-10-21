"""Combine unchanged author checkpoint with additive identity/report sidecars, then prepare review."""
import json,sys,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];child=sys.argv[1];numbers={'nut':'12','front-axle':'11','fork-cap':'08','bow':'13','carrier-gray':'20'};B=R/'creative/reviews/front-completion-front9-integration-sidecars-v1';F=B/(child+'-catalog-fragment.json');f=json.loads(F.read_text());assert f['admit_to_catalog'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=R/('creative/reviews/front-completion-freeze-'+numbers[child]+'/frozen-checkpoint.json');new=B/'frozen-checkpoint.json';files={}
for p in [old,new]:
 d=json.loads(p.read_text())
 for row in d['frozen_files']:
  q=R/row['path'];assert q.is_file()and sha(q)==row['sha256'],row['path'];assert row['path']not in files or files[row['path']]['sha256']==row['sha256'];files[row['path']]=row
 for q in [p]:files[str(q.relative_to(R))]=dict(path=str(q.relative_to(R)),bytes=q.stat().st_size,sha256=sha(q))
assert f['source']in files and sha(R/f['source'])==f['source_sha256']
O=R/'creative/reviews/front-completion-coordination-freezes-v1'/child;O.mkdir(exist_ok=True,parents=True);out=O/'frozen-checkpoint.json';out.write_text(json.dumps(dict(scope='Union of historical immutable source/render checkpoint and new additive sidecars; no source modifications',author_checkpoint=str(old.relative_to(R)),sidecar_checkpoint=str(new.relative_to(R)),frozen_files=list(files.values())),indent=2)+'\n')
report='../front-completion-front9-integration-sidecars-v1/'+child+'-render-report.json';subprocess.run([sys.executable,str(R/'tools/prepare_exterior_worker_review_v2.py'),str(F.relative_to(R)),'--author-report',report,'--freeze',str(out.relative_to(R))],cwd=R,check=True)
