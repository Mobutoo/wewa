"""Reopen standalone derivative, verify source A/N/UV parity, dump actual export-reference corners."""
import bpy,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/workspace/wewa');K='right-side-cover-coordinate-conversion-v1';D=R/'creative/research'/K;O=R/'creative/reviews'/K;H=R/'assets-src/moto-components'/K;sys.path.insert(0,str(H));import build as protocol
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Source snapshot from original native, in memory only. No save.
bpy.ops.wm.open_mainfile(filepath=str(protocol.SOURCE));source_sha=sha(protocol.SOURCE);old={}
for name in protocol.NAMES:
 ob=bpy.data.objects[name];m=ob.data
 old[name]=dict(positions=[v.co.copy()for v in m.vertices],normals={(f.index,m.loops[i].vertex_index):m.corner_normals[i].vector.copy()for f in m.polygons for i in f.loop_indices},uv=[{(f.index,m.loops[i].vertex_index):tuple(uv.data[i].uv)for f in m.polygons for i in f.loop_indices}for uv in m.uv_layers],faces=[tuple(f.vertices)for f in m.polygons],materials=protocol.material_proof(ob))
bpy.ops.wm.open_mainfile(filepath=str(H/'child-candidate.blend'));assert not bpy.data.libraries;assert bpy.context.scene.view_layers[0].material_override is None
rows=[]
for name in protocol.NAMES:
 ob=bpy.data.objects[name];m=ob.data;o=old[name];assert ob.matrix_world==Matrix.Identity(4);assert list(ob.location)==[0,0,0];assert ob.name in bpy.data.collections[protocol.COLLECTION].objects
 pe=max((v.co-protocol.A@old).length for v,old in zip(m.vertices,o['positions']));ne=max((m.corner_normals[i].vector-protocol.A@o['normals'][(f.index,m.loops[i].vertex_index)]).length for f in m.polygons for i in f.loop_indices);assert pe<1e-7 and ne<.0003
 for f,orig in zip(m.polygons,o['faces']):
  rev=list(reversed(orig));now=list(f.vertices);assert any(now==rev[i:]+rev[:i]for i in range(len(now)))
 for uv,values in zip(m.uv_layers,o['uv']):assert all(tuple(uv.data[i].uv)==values[(f.index,m.loops[i].vertex_index)]for f in m.polygons for i in f.loop_indices)
 assert protocol.material_proof(ob)==o['materials'];m.calc_loop_triangles()
 if m.uv_layers:m.calc_tangents(uvmap=m.uv_layers.active.name)
 def C(v):return(v[0],v[2],-v[1])
 data=bytearray()
 for t in m.loop_triangles:
  for i in t.loops:
   loop=m.loops[i];pos=C(m.vertices[loop.vertex_index].co);normal=C(m.corner_normals[i].vector);uv=tuple(m.uv_layers.active.data[i].uv)if m.uv_layers else(0,0);tan=(*C(loop.tangent),loop.bitangent_sign)if m.uv_layers else(0,0,0,0)
   data.extend(struct.pack('<12f',*pos,*normal,*uv,*tan))
 file=D/(name+'-native-corners.bin');file.write_bytes(data)
 rows.append(dict(object=name,mesh=m.name,vertices=len(m.vertices),triangles=len(m.loop_triangles),has_uv=bool(m.uv_layers),has_tangent=bool(m.uv_layers),maximum_position_A_error_m=pe,maximum_normal_A_error=ne,uv_and_materials_preserved=True,matrix_world=[list(r)for r in ob.matrix_world],corners=str(file.relative_to(R)),corners_sha256=sha(file),bounds_m={'min':[min(v.co[i]for v in m.vertices)for i in range(3)],'max':[max(v.co[i]for v in m.vertices)for i in range(3)]}))
assert sha(protocol.SOURCE)==source_sha
(D/'native-reopen-check.json').write_text(json.dumps(dict(source_sha256=sha(H/'child-candidate.blend'),historical_source_sha256=source_sha,source_independent=True,source_unchanged=True,objects=rows,corner_layout='Little-endian Float32 per oriented triangle corner: glTFposition3, glTFnormal3, nativeUV2 (GLB V convention checked explicitly), glTFtangentXYZ+W4',art_accepted=False),indent=2)+'\n')
