"""Read actual renderer loop triangles, separate from BMesh nonplanar quad volume."""
from pathlib import Path
import bpy,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];source=H/'engine-spark-cap-v2-geometry.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=json.loads((H/'geometry-report-v2.json').read_text());assert sha(source)==build['geometry_source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for src in build['geometry']:
 obj=bpy.data.objects[src['name']];ev=obj.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();volume=0.
 for t in m.loop_triangles:
  a,b,c=[tuple(m.vertices[i].co)for i in t.vertices];volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
 rows.append({'name':obj.name,'triangles':len(m.loop_triangles),'actual_render_triangle_volume_m3':volume,'BMesh_source_volume_m3':src['signed_volume_m3'],'relative_BMesh_vs_renderer_difference':abs(src['signed_volume_m3']/volume-1),'reason':'Nonplanar helical contact quads use actual renderer loop triangulation as export reference. BMesh diagnostic retained; no vertex, normal, index or tolerance repair.'});ev.to_mesh_clear()
assert sha(source)==build['geometry_source_sha256'];report={'source_sha256':sha(source),'export_sha256':build['geometry_export_sha256'],'meshes':rows,'source_modified':False};(R/'creative/reviews/engine-spark-cap-v2/geometry-render-triangulation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
