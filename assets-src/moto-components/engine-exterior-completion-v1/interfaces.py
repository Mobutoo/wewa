import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');O=R/'assets-src/moto-components/engine-exterior-completion-v1';out=[]
for row in json.loads((O/'native-inventory.json').read_text()):
 if 'crankcase' in row['source']:continue
 bpy.ops.wm.open_mainfile(filepath=str(R/row['source']))
 for c in bpy.data.collections:
  if c.name.startswith('WEWA_ENGINE'):
   obs=[o for o in c.all_objects if o.type=='MESH'];out.append(dict(source=row['source'],collection=c.name,objects=[dict(name=o.name,bounds=[[min((o.matrix_world@Vector(v))[i] for v in o.bound_box) for i in range(3)],[max((o.matrix_world@Vector(v))[i] for v in o.bound_box) for i in range(3)]]) for o in obs]))
(O/'interfaces.json').write_text(json.dumps(out,indent=2))
