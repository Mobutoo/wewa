import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');D=R/'creative/research/right-side-cover-world-pose-audit-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=['assets-src/moto-components/side-cover-right-v1/side-cover-right-candidate-v1.blend','assets-src/moto-components/side-cover-right-v2/child-candidate.blend'];rows=[]
for file in paths:
 p=R/file;before=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();obs=[]
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  m=ob.data;m.calc_loop_triangles();pts=[ob.matrix_world@v.co for v in m.vertices];faces=[t for t in m.loop_triangles if all(m.vertices[i].co.z>.001 for i in t.vertices)];av=sum((t.normal*t.area for t in faces),Vector())
  obs.append(dict(name=ob.name,collections=[c.name for c in ob.users_collection],matrix_world=[list(r)for r in ob.matrix_world],matrix_determinant=ob.matrix_world.determinant(),vertices=len(m.vertices),triangles=len(m.loop_triangles),bounds_native_m=dict(min=[min(v[i]for v in pts)for i in range(3)],max=[max(v[i]for v in pts)for i in range(3)]),vertex0_local=list(m.vertices[0].co),vertex0_world=list(pts[0]),vertex0_normal=list(m.vertices[0].normal),positive_z_surface_area_weighted_normal=list(av.normalized()),positive_z_surface_triangles=len(faces),mesh_coordinates_digest=hashlib.sha256(repr([tuple(v.co)for v in m.vertices]).encode()).hexdigest()))
 rows.append(dict(path=file,sha256=before,objects=obs,collections=[c.name for c in bpy.data.collections]));assert sha(p)==before
(D/'native-read.json').write_text(json.dumps(dict(sources=rows,no_render=True,no_source_writes=True),indent=2)+'\n')
