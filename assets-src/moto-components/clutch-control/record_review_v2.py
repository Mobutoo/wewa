from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[3];folder=sys.argv[1] if len(sys.argv)>1 else 'clutch-control';HERE=ROOT/'assets-src/moto-components'/folder;OUT=ROOT/'creative/reviews'/(folder+'-v2');COMMON=ROOT/'assets-src/moto-components/clutch-control'
paths=[HERE/f for f in ['parameters-v2.json','build_v2.py','build-report-v2.json','provenance-v2.json','README_v2.md',folder+'-v2.blend',folder+'-v2-inspection.glb']]
paths += [OUT/f for f in ['README.md','source-geometry-check.json','export-check.json','render-report.json','quarter-rest.png','pivot-working-12deg.png']]
paths += [COMMON/f for f in ['lever_builder_v2.py','topology_cleanup_v2.py','render_control_v2.py','check_export_v2.mjs','record_review_v2.py']]
paths += [ROOT/'assets-src/moto-components/throttle-control/control_geometry.py',ROOT/'assets-src/moto-components/front-brake-plate/csg.py',ROOT/'creative/research'/folder/'reference-observations.json']
check=json.loads((OUT/'source-geometry-check.json').read_text());render=json.loads((OUT/'render-report.json').read_text());export=json.loads((OUT/'export-check.json').read_text());sha=hashlib.sha256((HERE/(folder+'-v2.blend')).read_bytes()).hexdigest()
assert sha==check['source_sha256']==render['source_sha256'];assert not export['glTF_errors'];assert all(m['zeroAreaTriangles']==0 for m in export['meshes']);assert export['sha256']==hashlib.sha256((HERE/(folder+'-v2-inspection.glb')).read_bytes()).hexdigest()
files=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(paths))]
(OUT/'review-manifest.json').write_text(json.dumps({'revision':folder+'-v2','source_sha256':sha,'files':files,'scope':'Fabrication and isolated actual renders; coordinator engine captures tracked separately','supersedes_rejected_v1':True,'all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False},indent=2)+'\n');print('Bound',folder,len(files),'v2 files')
