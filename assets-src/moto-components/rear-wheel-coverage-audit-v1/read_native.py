import bpy,json,hashlib,re
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent;whole=json.loads((R/'creative/reviews/whole-exterior-coverage-v15/linked-parents-check.json').read_text())['parents'];paths={r['source'] for r in whole if r['key']in['front-rim','rear-rim','rear-tyre','swingarm-body','chaincase-upper','chaincase-lower','rear-brake-panel-ds151069','fuel-tank-shell']}
for r in json.loads((O/'catalog-candidates.json').read_text()):
 if any(k in r['source']for k in ['material','front10-v8','rear-axle-v2','p22-']):paths.add(r['source'])
paths|={'assets-src/moto-components/front-completion-p23-rear-axle-material-v2/material.blend','assets-src/moto-components/chaincase-front-ear-root-v2/child-candidate.blend','assets-src/moto-components/fuel-tap-stepped-hex-cap-visible-v1/fuel-tap-stepped-hex-cap-visible-v1.blend','assets-src/moto-components/brake-actuation-rod-v1/child-candidate.blend'}
out=[]
for s in sorted(paths):
 p=R/s
 if not p.exists():out.append(dict(source=s,exists=False));continue
 bpy.ops.wm.open_mainfile(filepath=str(p));collections=[]
 for c in bpy.data.collections:
  objects=[dict(name=o.name,type=o.type,matrix_world=[list(x)for x in o.matrix_world],hide_render=o.hide_render)for o in c.objects if o.type in ['MESH','CURVE']]
  if objects:collections.append(dict(name=c.name,hide_render=c.hide_render,objects=objects))
 direct=[dict(name=o.name,type=o.type,matrix_world=[list(x)for x in o.matrix_world])for o in bpy.context.scene.collection.objects if o.type in ['MESH','CURVE']]
 out.append(dict(source=s,exists=True,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),collections=collections,scene_root_objects=direct,libraries=[bpy.path.abspath(l.filepath)for l in bpy.data.libraries]))
(O/'native-source-read.json').write_text(json.dumps(out,indent=2))
for row in out:
 print('\nSOURCE',row['source']);print([(c['name'],[o['name']for o in c['objects']])for c in row.get('collections',[])]);print('ROOT',[o['name']for o in row.get('scene_root_objects',[])])
