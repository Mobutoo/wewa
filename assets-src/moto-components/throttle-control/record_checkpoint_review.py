"""Bind final frozen candidate, actual isolated PNG/EXR and restart checkpoints.
Deliberately excludes coordinator-owned engine screenshots and export-buffer reports.
"""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[3];folder=sys.argv[1];HERE=ROOT/'assets-src/moto-components'/folder;COMMON=ROOT/'assets-src/moto-components/throttle-control';rev='v3' if folder=='handlebar-grips' else 'v1';OUT=ROOT/'creative/reviews'/(folder+'-'+rev)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if folder=='handlebar-grips':
 names=['build_v3.py','parameters-v3.json','provenance-v3.json','README_v3.md','build-report-v3.json','handlebar-grips-v3.blend','handlebar-grips-v3-inspection.glb','check_export_v3.mjs','render_v3.py','record_review_v3.py','textures-v3/rubber-metallic-roughness.png'];research=['reference-observations.json','footprint-v3.json'];views=['left-reference-side','right-quarter']
else:
 names=['parameters.json','build.py','build-report.json','provenance.json','README.md',folder+'-v1.blend',folder+'-inspection.glb','render.py','check_export.mjs'];research=['reference-observations.json'];views={'throttle-control':['quarter-rest','spool-working-50deg'],'ignition-lock':['quarter-off','rear-mount-on'],'cockpit-cables':['descending-visible-sections','ignition-pigtail-free-end'],'engine-cover-right':['outer-bosses','rear-hollow-shell'],'engine-filter-cap':['outer-face','rear-spigot']}[folder]
paths=[HERE/p for p in names]+[ROOT/'creative/research'/folder/p for p in research]+[OUT/p for p in ['README.md','source-geometry-check.json','export-check.json','render-report.json']]+[COMMON/'render_checkpoint.py',Path(__file__)]
for optional in [HERE/'preflight-manifest.json',OUT/'visual-audit-note.json',OUT/'normal-policy-observation.json']:
 if optional.exists():paths.append(optional)
if folder!='handlebar-grips':paths.append(COMMON/'control_geometry.py')
if folder in ['throttle-control','ignition-lock','engine-filter-cap']:paths.append(ROOT/'assets-src/moto-components/front-brake-plate/csg.py')
if folder in ['ignition-lock','engine-cover-right','engine-filter-cap']:paths.append(ROOT/'assets-src/moto-components/clutch-control/topology_cleanup_v2.py')
if folder=='engine-cover-right':paths.append(HERE/'cover_csg.py')
if folder in ['ignition-lock','cockpit-cables']:paths += [ROOT/'assets-src/moto-components/clutch-control/inspect_export_areas.mjs',OUT/'export-area-check.json']
source=HERE/(folder+'-'+rev+'.blend');glb=HERE/(folder+'-'+rev+'-inspection.glb' if folder=='handlebar-grips' else folder+'-inspection.glb');source_sha=sha(source);check=json.loads((OUT/'source-geometry-check.json').read_text());export=json.loads((OUT/'export-check.json').read_text());render=json.loads((OUT/'render-report.json').read_text());assert source_sha==check['source_sha256']==render['source_sha256'];assert sha(glb)==export['sha256'] and not export['glTF_errors'];assert len(render['views'])==len(views)
for name in views:
 cp=OUT/(name+'.checkpoint.json');j=json.loads(cp.read_text());assert j['complete'] and j['source_sha256']==source_sha;assert j['configuration_sha256']==hashlib.sha256(json.dumps(j['configuration'],sort_keys=True).encode()).hexdigest();assert j['configuration']['protocol_sha256']==sha(COMMON/'render_checkpoint.py');assert j['configuration']['samples']==96
 paths.append(cp)
 for output in j['outputs']:
  p=OUT/output['file'];assert sha(p)==output['sha256'] and p.stat().st_size==output['bytes'];paths.append(p)
rows=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(paths))]
(OUT/'review-manifest.json').write_text(json.dumps({'revision':folder+'-'+rev,'source_sha256':source_sha,'export_sha256':sha(glb),'scope':'Original isolated fabrication, actual PNG/linearEXR and independently restartable checkpoints; coordinator engine proof separate','files':rows,'all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False},indent=2)+'\n');print('Bound',folder,len(rows),'files with checkpoints')
