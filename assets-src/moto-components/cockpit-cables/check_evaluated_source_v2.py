"""Read-only evaluated loop triangles and actual sheath topology, no source rewrite."""
from pathlib import Path
import bpy,json,math,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];source=H/'cockpit-cables-v2.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));rows=[]
for obj in list(bpy.data.collections['WEWA_COCKPIT_CABLES_PARTIAL'].objects):
 if obj.type!='MESH':continue
 deps=bpy.context.evaluated_depsgraph_get();evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();terms=[]
 for tri in mesh.loop_triangles:
  a,b,c=[tuple(mesh.vertices[index].co)for index in tri.vertices];terms.append((a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6)
 rows.append({'name':obj.name,'actual_loop_triangles':len(mesh.loop_triangles),'signed_volume_source_loop_triangles_m3':math.fsum(terms),'world_matrix':[list(row)for row in obj.matrix_world],'source_quad_faces':sum(len(face.vertices)==4 for face in mesh.polygons)});evaluated.to_mesh_clear()
assert hashlib.sha256(source.read_bytes()).hexdigest()==before;report={'source_sha256':before,'geometry':rows,'scope':'Renderer/exporter evaluated triangulation of nonplanar sweep quads. Separate from bmesh quadvolume; no arbitrary volume tolerance or mesh repair.','source_modified':False};(R/'creative/reviews/cockpit-cables-v2/evaluated-source-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
