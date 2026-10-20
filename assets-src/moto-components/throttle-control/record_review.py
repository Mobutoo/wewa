"""Bind a control's final source, export, dependencies and isolated actual renders."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3];folder=sys.argv[1] if len(sys.argv)>1 else 'throttle-control';HERE=ROOT/'assets-src/moto-components'/folder;OUT=ROOT/'creative/reviews'/(folder+'-v1');research=ROOT/'creative/research'/folder
paths=[HERE/p for p in ['parameters.json','build.py','build-report.json','provenance.json','README.md',folder+'-v1.blend',folder+'-inspection.glb']]
paths += [OUT/p for p in ['README.md','source-geometry-check.json','export-check.json','render-report.json','quarter-rest.png',('spool-working-50deg.png' if folder=='throttle-control' else 'pivot-working-12deg.png')]]
paths += [research/'reference-observations.json',Path(__file__),ROOT/'assets-src/moto-components/throttle-control/control_geometry.py',ROOT/'assets-src/moto-components/throttle-control/check_export.mjs',ROOT/'assets-src/moto-components/front-brake-plate/csg.py']
paths += [ROOT/'assets-src/moto-components/throttle-control/render.py'] if folder=='throttle-control' else [ROOT/'assets-src/moto-components/clutch-control/lever_builder.py',ROOT/'assets-src/moto-components/clutch-control/render_control.py']
files=sorted(set(paths));rows=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
source_sha=hashlib.sha256((HERE/(folder+'-v1.blend')).read_bytes()).hexdigest();check=json.loads((OUT/'source-geometry-check.json').read_text());render=json.loads((OUT/'render-report.json').read_text());gltf=json.loads((OUT/'export-check.json').read_text())
assert source_sha==check['source_sha256']==render['source_sha256']
assert gltf['sha256']==hashlib.sha256((HERE/(folder+'-inspection.glb')).read_bytes()).hexdigest() and not gltf['glTF_errors']
(OUT/'review-manifest.json').write_text(json.dumps({'revision':folder+'-v1','scope':'Fabrication and isolated review only; coordinator engine proofs separate','files':rows,'source_sha256':source_sha,'all_dimensions_estimated':True,'exact_RDC_identity_confirmed':False,'art_accepted':False,'physical_iphone_tested':False},indent=2)+'\n')
print('Bound',len(rows),folder,'files')
