"""Actual saved native-instance versus imported composed GLB oriented triangles/normals; source never saved."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from collections import defaultdict,Counter
R=Path('/workspace/wewa');K='rear-brake-exterior-completion-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def cycle(ids):return min(tuple(ids[i:]+ids[:i])for i in range(3))
bpy.ops.wm.open_mainfile(filepath=str(H/'rear-brake-exterior.blend'));bpy.context.view_layer.update();source={}
for inst in bpy.context.evaluated_depsgraph_get().object_instances:
 ob=inst.object
 if ob.type!='MESH':continue
 m=ob.data;M=inst.matrix_world;m.calc_loop_triangles();pos=[M@v.co for v in m.vertices];normal=M.to_3x3().inverted().transposed();equiv={};indices=[]
 for p in pos:
  key=tuple(p);indices.append(equiv.setdefault(key,len(equiv)))
 kd=KDTree(len(pos))
 for i,p in enumerate(pos):kd.insert(p,i)
 kd.balance();tris=defaultdict(list)
 for t in m.loop_triangles:
  ids=[indices[m.loops[i].vertex_index]for i in t.loops];ns={ids[j]:(normal@m.corner_normals[i].vector).normalized()for j,i in enumerate(t.loops)};tris[cycle(ids)].append(ns)
 source[ob.name]=dict(kd=kd,indices=indices,tris=tris,count=len(m.loop_triangles))
prior={o.as_pointer()for o in bpy.data.objects};bpy.ops.import_scene.gltf(filepath=str(H/'rear-brake-exterior.glb'));imports=[o for o in bpy.data.objects if o.as_pointer()not in prior and o.type=='MESH'];assert len(imports)==8;rows=[]
for ob in imports:
 key=ob.name.split('.')[0];assert key in source,key;s=source[key];m=ob.data;M=ob.matrix_world;m.calc_loop_triangles();nm=M.to_3x3().inverted().transposed();mapped=[];pe=0
 for v in m.vertices:
  point,index,dist=s['kd'].find(M@v.co);pe=max(pe,dist);mapped.append(s['indices'][index])
 assert pe<1e-6,(key,pe)
 ne=0
 for t in m.loop_triangles:
  ids=[mapped[m.loops[i].vertex_index]for i in t.loops];ci=cycle(ids);assert s['tris'][ci],(key,'Winding/connectivity mismatch');expected=s['tris'][ci].pop()
  for j,i in enumerate(t.loops):ne=max(ne,((nm@m.corner_normals[i].vector).normalized()-expected[ids[j]]).length)
 assert not any(s['tris'].values()) and ne<.001,(key,ne)
 rows.append(dict(object=key,triangles=len(m.loop_triangles),maximum_native_imported_glb_vertex_distance_m=pe,maximum_corner_normal_vector_distance=ne,oriented_triangle_connectivity_identical=True))
(O/'native-glb-parity.json').write_text(json.dumps(dict(native_sha256=sha(H/'rear-brake-exterior.blend'),glb_sha256=sha(H/'rear-brake-exterior.glb'),actual_glb_imported=True,objects=rows,geometry_material_source_reuse='Eight exterior components including four copied unchanged hardware meshes; saved native versus actual imported GLB, no source writes',fit_qualified=False,art_accepted=False),indent=2)+'\n')
