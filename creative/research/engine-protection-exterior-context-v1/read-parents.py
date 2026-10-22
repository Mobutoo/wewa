"""Read actual evaluated saved parents without saving them; do not use cold linked matrices."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');D=R/'creative/research/engine-protection-exterior-context-v1';cat=json.loads((R/'tools/motorcycle-lab/catalog.json').read_text())['assets'];rows=[]
for key in ['engine-protection-hoop-tube','engine-protection-centre-plate','engine-protection-terminal-a','engine-protection-terminal-b']:
 c=cat[key];p=R/'assets-src/moto-components'/c['source'];bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();col=bpy.data.collections[c['collection']];objects=[]
 for o in col.all_objects:
  bounds=None
  if o.type=='MESH':
   v=[o.matrix_world@Vector(q)for q in o.bound_box];bounds=[[min(q[i]for q in v)for i in range(3)],[max(q[i]for q in v)for i in range(3)]]
  objects.append({'name':o.name,'type':o.type,'data':o.data.name if o.data else None,'matrix_world':[list(q)for q in o.matrix_world],'matrix_local':[list(q)for q in o.matrix_local],'parent':o.parent.name if o.parent else None,'bounds_world':bounds,'properties':{k:str(o[k])for k in o.keys()},'materials':[m.name if m else None for m in o.data.materials]if o.type=='MESH'else[]})
 rows.append({'key':key,'component_id':c['component_id'],'source':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'glb':'assets-src/moto-components/'+c['files'][0],'glb_sha256':hashlib.sha256((R/'assets-src/moto-components'/c['files'][0]).read_bytes()).hexdigest(),'collection':c['collection'],'catalog_snapshot':c,'objects':objects,'all_scene_datums':[{'name':o.name,'type':o.type,'matrix_world':[list(q)for q in o.matrix_world],'properties':{k:str(o[k])for k in o.keys()}}for o in bpy.context.scene.objects if o.type=='EMPTY'],'images':[{'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file)}for im in bpy.data.images if im.type=='IMAGE']})
(D/'parent-native-read.json').write_text(json.dumps({'parents':rows,'read_only':True},indent=2)+'\n')
