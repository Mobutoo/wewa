import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');out=R/'creative/research/p29-lower-front-sheath-evidence-v1/native-audit.json';rows=[]
for rel in ['assets-src/moto-components/cockpit-cables/cockpit-cables-v3.blend','assets-src/moto-components/front-brake-plate/front-brake-plate-v2.blend','assets-src/moto-components/front-completion-p03-wire-guide-front12-v2/wire-guide-material.blend']:
 p=R/rel;bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();objects=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.library:continue
  coords=[o.matrix_world@Vector(q)for q in o.bound_box];objects.append({'name':o.name,'vertices':len(o.data.vertices),'matrix_world':[list(x)for x in o.matrix_world],'bounds_world':[[min(v[i]for v in coords)for i in range(3)],[max(v[i]for v in coords)for i in range(3)]],'properties':{k:str(o[k])for k in o.keys()},'materials':[x.name if x else None for x in o.data.materials]})
 rows.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects':objects})
out.write_text(json.dumps({'sources':rows,'read_only':True,'function_not_inferred_from_names':True},indent=2))
