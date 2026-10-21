"""Bind a new isolated body folder, its explicit views and original dependencies.
Coordinator captures remain outside this manifest. No mutation of older component folders.
"""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[3];folder=sys.argv[1] if len(sys.argv)>1 else 'engine-cover-left';HERE=ROOT/'assets-src/moto-components'/folder;OUT=ROOT/'creative/reviews'/(folder+'-v1');COMMON=ROOT/'assets-src/moto-components/throttle-control';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=HERE/(folder+'-v1.blend');glb=HERE/(folder+'-inspection.glb');source_sha=sha(source);check=json.loads((OUT/'source-geometry-check.json').read_text());export=json.loads((OUT/'export-check.json').read_text());render=json.loads((OUT/'render-report.json').read_text());assert source_sha==check['source_sha256']==render['source_sha256'];assert sha(glb)==export['sha256'] and not export['glTF_errors'];assert all(not x['zeroAreaTriangles'] for x in export['meshes']);assert render['samples']==96
paths=[p for p in HERE.rglob('*') if p.is_file() and p.suffix in ['.py','.json','.md','.blend','.glb','.png'] and '__pycache__' not in str(p)]
paths += [OUT/p for p in ['README.md','source-geometry-check.json','export-check.json','render-report.json']]+[ROOT/'creative/research'/folder/'reference-observations.json',Path(__file__),COMMON/'control_geometry.py',COMMON/'render_checkpoint.py',ROOT/'assets-src/moto-components/clutch-control/topology_cleanup_v2.py',ROOT/'assets-src/moto-components/front-brake-plate/csg.py']
for optional in ['visual-audit-note.json','normal-policy-observation.json']:
 if (OUT/optional).exists():paths.append(OUT/optional)
for view in render['views']:
 cp=OUT/(view['name']+'.checkpoint.json');j=json.loads(cp.read_text());assert j['complete'] and j['source_sha256']==source_sha;assert j['configuration']['samples']==96;assert j['configuration']['protocol_sha256']==sha(COMMON/'render_checkpoint.py');paths.append(cp)
 assert j['configuration_sha256']==hashlib.sha256(json.dumps(j['configuration'],sort_keys=True).encode()).hexdigest()
 for output in j['outputs']:
  p=OUT/output['file'];assert sha(p)==output['sha256'] and p.stat().st_size==output['bytes'];paths.append(p)
rows=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(paths))]
(OUT/'review-manifest.json').write_text(json.dumps({'revision':folder+'-v1','source_sha256':source_sha,'export_sha256':sha(glb),'files':rows,'scope':'Original isolated body, technical preflight and checkpointed96 PNG/EXR views; coordinator engine proof separate','all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False},indent=2)+'\n');print('Bound',folder,len(rows),'files')
