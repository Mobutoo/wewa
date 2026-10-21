"""Explicit author source freeze/final review only; parent owns global admissions."""
from pathlib import Path
import json,hashlib,datetime,sys
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/front-tyre-v3';D=R/'creative/research/front-tyre-material-v3';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();put=lambda p,j:p.write_text(json.dumps(j,indent=2)+'\n')
b=json.loads((O/'material-build-report.json').read_text());check=json.loads((O/'geometry-material-buffer-check.json').read_text());assert check['technical_passed']and check['export_sha256']==b['export_sha256'];assert sha(H/'front-tyre-v3.blend')==b['source_sha256']and sha(H/'front-tyre-v3-inspection.glb')==b['export_sha256']
views=['quarter','reverse-quarter','tread-detail','sidewall-detail'];compare=['compare-'+k+'-'+v for v in ['tread-detail','sidewall-detail']for k in ['native','atlas']]+['compare-atlas-whole-quarter']
if '--freeze'in sys.argv:
 read=json.loads((O/'material-preview-review.json').read_text());assert read['all_five_read']and read['ready_for_final96']and read['source_sha256']==b['source_sha256']
 g3path=O/'g3-source-freeze-v1.json';g3=json.loads(g3path.read_text());assert all(sha(R/q['path'])==q['sha256']for q in g3['files'])
 files=[R/q['path']for q in g3['files']]+[g3path]
 files +=[H/n for n in ['parameters.json','build.py','camera_preflight.py','check_export.mjs','check_texture_data.py','render_compare.py','render.py','run_final.py','record.py','requirements.txt','README.md','provenance.json','front-tyre-v3.blend','front-tyre-v3-inspection.glb']]
 files +=list((H/'textures').glob('*.png'))+[D/'G0-G4-transfer-plan-v1.json',D/'README.md']
 files +=[O/n for n in ['transfer-preflight.json','material-build-report.json','material-geometry-preservation-check.json','geometry-material-buffer-check.json','texture-pixel-data-check.json','source-portability-check.json','checkpoint-bake-normal.json','checkpoint-bake-emit.json','comparison-render-report.json','material-preview-review.json']]
 for v in compare:files +=[O/(v+'.png'),O/(v+'.json')]
 rows=[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(set(files))]
 target=O/'source-freeze.json';j={'component_id':b['component_id'],'revision':b['revision'],'frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':b['source_sha256'],'export_sha256':b['export_sha256'],'files':rows,'scope':'Corrected original tyre, new real material bakes and actual five native/atlas reads; no artistic/fit/mobile reception','art_accepted':False}
 if target.exists():
  old=json.loads(target.read_text());assert old['files']==rows and old['source_sha256']==j['source_sha256']and old['export_sha256']==j['export_sha256'],'Never overwrite a closed source freeze'
 else:put(target,j)
 print('FRONT_TYRE_V3_SOURCE_FROZEN',len(rows),sha(target),flush=True);raise SystemExit
freeze=O/'source-freeze.json';f=json.loads(freeze.read_text());assert all(sha(R/q['path'])==q['sha256']for q in f['files']);worker=json.loads((O/'render-worker.json').read_text());render=json.loads((O/'render-report.json').read_text());read=json.loads((O/'source-render-review.json').read_text());assert worker['state']=='completed'and worker['exit_code']==0 and worker['source_unchanged']and worker['source_sha256']==b['source_sha256'];assert render['status']=='completed'and len(render['views'])==4;assert read['all_four_actually_opened_native']and read['source_sha256']==b['source_sha256']
actual={q['view']:q['PNG_sha256']for q in read['views']};files=[R/q['path']for q in f['files']]+[freeze]
for v in views:
 png=O/(v+'.png');exr=O/(v+'.exr');cp=O/('checkpoint-'+v+'.json');q=json.loads(cp.read_text());assert q['source_sha256']==b['source_sha256']and q['samples']==96 and q['PNG_sha256']==sha(png)==actual[v]and q['EXR_sha256']==sha(exr);files +=[png,exr,cp]
files +=[O/n for n in ['render-worker.json','render-report.json','source-render-review.json','README.md']];rows=[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(set(files))];target=O/'manifest.json';j={'component_id':b['component_id'],'revision':b['revision'],'source_sha256':b['source_sha256'],'export_sha256':b['export_sha256'],'closed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'scope':'Author source+four actual96 reads and PNG/EXR checkpoints; parent independent QA separate; tyre identity/mould/fit/LOD/mobile/art unreceived','art_accepted':False}
if target.exists():
 old=json.loads(target.read_text());assert old['files']==rows,'Never overwrite a closed review manifest'
else:put(target,j)
print('FRONT_TYRE_V3_AUTHOR_REVIEW_CLOSED',len(rows),sha(target),flush=True)
