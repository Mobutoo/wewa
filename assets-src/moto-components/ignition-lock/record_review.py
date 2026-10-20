from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[3];folder=sys.argv[1] if len(sys.argv)>1 else 'ignition-lock';HERE=ROOT/'assets-src/moto-components'/folder;OUT=ROOT/'creative/reviews'/(folder+'-v1')
proof=['quarter-off.png','rear-mount-on.png'] if folder=='ignition-lock' else ['descending-visible-sections.png','ignition-pigtail-free-end.png']
paths=[HERE/f for f in ['parameters.json','build.py','render.py','check_export.mjs','build-report.json','provenance.json','README.md',folder+'-v1.blend',folder+'-inspection.glb']]
paths += [OUT/f for f in ['README.md','source-geometry-check.json','export-check.json','export-area-check.json','render-report.json']+proof]
paths += [ROOT/'creative/research'/folder/'reference-observations.json',ROOT/'assets-src/moto-components/throttle-control/control_geometry.py',ROOT/'assets-src/moto-components/clutch-control/inspect_export_areas.mjs',Path(__file__)]
if folder=='ignition-lock':paths += [ROOT/'assets-src/moto-components/clutch-control/topology_cleanup_v2.py',ROOT/'assets-src/moto-components/front-brake-plate/csg.py']
check=json.loads((OUT/'source-geometry-check.json').read_text());render=json.loads((OUT/'render-report.json').read_text());export=json.loads((OUT/'export-check.json').read_text());areas=json.loads((OUT/'export-area-check.json').read_text());sha=hashlib.sha256((HERE/(folder+'-v1.blend')).read_bytes()).hexdigest();glbsha=hashlib.sha256((HERE/(folder+'-inspection.glb')).read_bytes()).hexdigest()
assert sha==check['source_sha256']==render['source_sha256'];assert glbsha==areas['sha256']==export['sha256'];assert not export['glTF_errors'] and areas['zeroAreaTriangles']==0
rows=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(paths))]
(OUT/'review-manifest.json').write_text(json.dumps({'revision':folder+'-v1','source_sha256':sha,'files':rows,'scope':'Fabrication and actual isolated renders; coordinator engine captures tracked separately','all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False},indent=2)+'\n');print('Bound',folder,len(rows),'files')
