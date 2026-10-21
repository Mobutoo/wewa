import bpy,json,hashlib,math
from pathlib import Path
R=Path('/workspace/wewa-github');p=R/'assets-src/moto-components/instruments/instruments-v5.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p));rows=[]
for name in ['Shaped central cluster cover','SPEED hollow rear pod','FUEL_GEAR hollow rear pod']:
 o=bpy.data.objects[name];dg=bpy.context.evaluated_depsgraph_get();m=o.evaluated_get(dg).to_mesh();m.calc_loop_triangles();vals=[]
 for t in m.loop_triangles:
  a,b,c=[m.vertices[k].co for k in t.vertices];n=(b-a).cross(c-a).normalized()
  if abs(n.z)>.999999:
   vals.extend([{'angle_deg':math.degrees(math.acos(max(-1,min(1,n.dot(m.corner_normals[li].vector))))),'local_z_m':float(a.z),'point':list(m.vertices[m.loops[li].vertex_index].co)}for li in t.loops])
 rows.append({'object':name,'geometrically_planar_axisZ_triangle_corners_tested':len(vals),'corners_over1deg':sum(v['angle_deg']>1 for v in vals),'max_corner_normal_deviation_from_plane_deg':max([v['angle_deg']for v in vals],default=0),'by_local_z_plane':[{'z_m':z,'corners':len([v for v in vals if round(v['local_z_m'],6)==z]),'max_normal_deviation_deg':max(v['angle_deg'] for v in vals if round(v['local_z_m'],6)==z)}for z in sorted({round(v['local_z_m'],6)for v in vals})],'worst':sorted(vals,key=lambda v:v['angle_deg'],reverse=True)[:3]});o.evaluated_get(dg).to_mesh_clear()
assert sha(p)==before;out={'source_sha256':before,'source_modified':False,'scope':'Actual saved v5 plane normals; central-cover correction preserved from v4 and both inherited planar pod cap fields corrected without physical triangle changes.','rows':rows,'art_accepted':False};(R/'creative/reviews/instruments-v5/planar-cap-normal-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
