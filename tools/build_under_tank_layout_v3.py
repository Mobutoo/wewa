"""Photo-guided placement correction; wrapper transforms preserve original geometry."""
import bpy,json,hashlib,sys
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from under_tank_layout_fields_v3 import field
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'creative/research/under-tank-layout-v3/plan.json'
OUT=ROOT/'assets-src/moto-components/under-tank-layout-v3'
REV=ROOT/'creative/reviews/under-tank-layout-v3'
plan=json.loads(PLAN.read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/plan['source_blend']));bpy.context.preferences.filepaths.save_version=0
rows=[]
for c in plan['changes']:
 ob=bpy.data.objects[c['name']];assert ob.parent is None,ob.name
 before=ob.matrix_world.copy();p=Vector(c['pivot_blender_m']);delta=Matrix.Translation(Vector(c['translation_blender_m']))@Matrix.Translation(p)@Matrix.Diagonal((*c['scale'],1))@Matrix.Translation(-p)
 wrapper=bpy.data.objects.new('LAYOUT ['+ob.name+']',None);bpy.context.collection.objects.link(wrapper);wrapper.matrix_world=delta
 ob.parent=wrapper;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=before
 bpy.context.view_layer.update()
 rows.append({'name':ob.name,'before_blender':[list(r) for r in before],'after_blender':[list(r) for r in ob.matrix_world],'delta_blender':[list(r) for r in delta]})
deformations=[]
for spec in plan['deformations']:
 objects=[bpy.data.objects[spec['mesh']]] if 'mesh' in spec else [o for o in bpy.data.objects[spec['root']].children_recursive if o.type=='MESH']
 for ob in objects:
  mesh=ob.data.copy();ob.data=mesh;M=np.array(ob.matrix_world);inv=np.linalg.inv(M)
  positions=np.array([v.co[:] for v in mesh.vertices]);world=positions@M[:3,:3].T+M[:3,3]
  adjusted,J=field(world,spec);local=(adjusted-M[:3,3])@inv[:3,:3].T
  normals=np.array([n.vector[:] for n in mesh.corner_normals]);indices=np.array([l.vertex_index for l in mesh.loops]);localJ=np.einsum('ij,njk,kl->nil',inv[:3,:3],J,M[:3,:3]);normalJ=np.linalg.inv(localJ).transpose(0,2,1)
  normals=np.einsum('nij,nj->ni',normalJ[indices],normals);normals/=np.linalg.norm(normals,axis=1)[:,None]
  for v,p in zip(mesh.vertices,local):v.co=p
  mesh.update();mesh.normals_split_custom_set(normals.tolist())
  deformations.append({'name':ob.name,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'max_displacement_m':float(np.linalg.norm(adjusted-world,axis=1).max()),'minimum_jacobian':float(np.linalg.det(J).min())})
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'motorcycle-layout.blend'),compress=True)
(REV/'native-check.json').write_text(json.dumps({'changes':rows,'deformations':deformations,'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
print('LAYOUT_NATIVE',len(rows))
