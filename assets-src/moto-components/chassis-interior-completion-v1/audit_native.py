import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');O=R/'assets-src/moto-components/chassis-interior-completion-v1'
bpy.ops.wm.open_mainfile(filepath=str(R/'assets-src/moto-components/whole-exterior-coverage-v14/whole-exterior-coverage-v14.blend'))
rows=[]
for o in bpy.context.scene.objects:
 if o.instance_collection and any(x in o.name for x in ['frame-','swingarm','air-cleaner','seat-envelope']):
  pts=[o.matrix_world@a.matrix_world@Vector(v) for a in o.instance_collection.all_objects if a.type=='MESH' for v in a.bound_box]
  rows.append(dict(name=o.name,collection=o.instance_collection.name,location=list(o.location),bounds=[[min(p[i] for p in pts)for i in range(3)],[max(p[i] for p in pts)for i in range(3)]],objects=[a.name for a in o.instance_collection.all_objects]))
for part in ['pivot-shaft','pivot-bush','chain-slider']:
 p=next((R/'assets-src/moto-components/swingarm'/part).glob('*.blend'))
 with bpy.data.libraries.load(str(p),link=True)as(a,b): b.collections=[n for n in a.collections if not any(x in n for x in ['STUDIO','Collection'])]
 for c in b.collections:
  rows.append(dict(source=str(p.relative_to(R)),collection=c.name,objects=[dict(name=o.name,type=o.type,bounds=[list(v)for v in o.bound_box])for o in c.all_objects]))
(O/'native-audit.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows))
