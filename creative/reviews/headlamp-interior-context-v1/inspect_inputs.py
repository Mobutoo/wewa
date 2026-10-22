import bpy,json,pathlib,hashlib
from mathutils import Vector
root=pathlib.Path('/workspace/wewa'); out=root/'creative/reviews/headlamp-interior-context-v1'
inputs={'housing':'assets-src/moto-components/headlamp/housing/headlamp-housing-v2.blend','cage':'assets-src/moto-components/front-completion-p06-holder-cage-front16-v2/holder-cage-material.blend','cap':'assets-src/moto-components/front-completion-p06-holder-cap-front12-v1/holder-cap-material.blend','base':'assets-src/moto-components/front-completion-p06-bulb-base-front16-v1/bulb-base-material.blend','flange':'assets-src/moto-components/front-completion-p06-bulb-flange-front15-v4/bulb-flange-material.blend','capsule':'assets-src/moto-components/front-completion-p06-bulb-capsule-front15-v1/bulb-capsule-material.blend'}
a={}
for key,rel in inputs.items():
 p=root/rel;bpy.ops.wm.open_mainfile(filepath=str(p));objs=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  objs.append({'name':o.name,'vertices':len(o.data.vertices),'bounds':[ [min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]],'matrix':[list(r) for r in o.matrix_world]})
 a[key]={'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects':objs}
(out/'native-inputs.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a))
