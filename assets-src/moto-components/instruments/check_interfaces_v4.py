"""Read-only conditional interfaces/motion check of the saved v3 candidate."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/instruments-v4';j=json.loads((O/'source-geometry-check.json').read_text());source=H/'instruments-v4.blend';assert hashlib.sha256(source.read_bytes()).hexdigest()==j['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));assembly=bpy.data.objects['INSTRUMENT_CLUSTER_MOUNT'];bpy.context.view_layer.update();inverse=assembly.matrix_world.inverted()
def evaluated(o):
 deps=bpy.context.evaluated_depsgraph_get();m=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);matrix=inverse@o.matrix_world;points=[matrix@v.co for v in m.vertices];faces=[tuple(f.vertices)for f in m.polygons];bpy.data.meshes.remove(m);return points,faces

def tree(o):
 points,faces=evaluated(o);return BVHTree.FromPolygons(points,faces),points
new=[bpy.data.objects[n]for n in['USB contoured surround - closed v2','USB inset capsule face - closed v2']];newtrees=[tree(o)for o in new];parts=bpy.data.collections[j['collection']];fixed=[o for o in parts.objects if o.get('structural_closed_volume')and(o.name.startswith('SPEED ')or o.name.startswith('FUEL_GEAR ')or o.name.startswith('FUEL pointer'))];rows=[]
for other in fixed:
 t,_=tree(other)
 for o,(n,points)in zip(new,newtrees):
  overlap=len(n.overlap(t));distances=[t.find_nearest(p)[3]for p in points];assert overlap==0,(o.name,other.name,overlap);rows.append({'USB_object':o.name,'existing_object':other.name,'surface_triangle_intersections':overlap,'sampled_USB_vertex_nearest_distance_m':min(distances)})
bridge=bpy.data.objects['Shaped central cluster cover'];bridge_points,_=evaluated(bridge);maxbridge=max(p.z for p in bridge_points);plane=[]
for o,(t,points)in zip(new,newtrees):
 minz=min(p.z for p in points);nano=max(0,maxbridge-minz);assert nano<1e-8,(o.name,nano);plane.append({'USB_object':o.name,'USB_min_local_z_m':minz,'bridge_max_local_z_m':maxbridge,'bounding_plane_numerical_overlap_m':nano,'interpretation':'Surround bottom intentionally seated on bridge front plane; nanometre-scale Float32 representation difference permitted, no designed volume penetration. Insert stays above pocket floor.'})
poses=[]
for speed in[0,28,56,84,112,140]:
 for fuel in[0,.65,1]:
  bpy.data.objects['SPEED_NEEDLE_PIVOT'].rotation_euler.z=math.radians(225-speed*270/140);bpy.data.objects['FUEL_NEEDLE_PIVOT'].rotation_euler.z=math.radians(225-fuel*80);bpy.context.view_layer.update();counts=[]
  for name in['SPEED red needle','FUEL red needle']:
   t,_=tree(bpy.data.objects[name])
   for o,(n,_)in zip(new,newtrees):
    overlap=len(t.overlap(n));assert overlap==0,(speed,fuel,name,o.name,overlap);counts.append({'needle':name,'USB_object':o.name,'intersections':overlap})
  poses.append({'speed_kmh':speed,'fuel_fraction':fuel,'pairs':counts})
report={'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'fixed_source_surface_checks':rows,'bridge_seating_plane_checks':plane,'needle_pose_checks':poses,'source_file_modified':False,'needle_and_gear_contract':'Same original v1 speed/fuel angles, pivots and gear ring/digit nodes; gear4 only had zero-area FONT faces removed. Electrical behaviour/calibration is not physically measured.','compatibility_limit':'These are estimated component sources in their working frame. No currentRDC part-number, OEM mount, hidden USB socket/hinge or measured real motorcycle compatibility is certified.','passed':True,'art_accepted':False};(O/'interface-motion-check.json').write_text(json.dumps(report,indent=2)+'\n');print('INSTRUMENTS_V2_INTERFACES',len(rows),'fixed pairs;',len(poses),'needle poses; no surface crossings')
