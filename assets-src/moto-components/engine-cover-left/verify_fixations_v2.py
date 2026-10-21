"""Actual integrated source rays; local W planes are historical estimates, not OEM."""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];p=H/'engine-cover-left-v2.blend';check=json.loads((H/'build-report-v2.json').read_text());assert hashlib.sha256(p.read_bytes()).hexdigest()==check['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(p));body=bpy.data.objects['LH magneto cover hollow casting - editable candidate'];m=body.to_mesh();tree=BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(f.vertices)for f in m.polygons]);body.to_mesh_clear();rows=[]
for j,pad in enumerate(check['pads']):
 c=pad['centre'];errors=[];miss=0;max_tilt=0
 for r in [.0035,.0045,.0055,.006]:
  for k in range(96):
   a=math.tau*k/96;x=c[0]+r*math.cos(a);y=c[1]+r*math.sin(a);hit=tree.ray_cast(Vector((x,y,.10)),Vector((0,0,-1)),.15)
   if hit[0]is None:miss+=1;continue
   errors.append(abs(hit[0].z-pad['top']));max_tilt=max(max_tilt,math.degrees(math.acos(min(1,abs(hit[1].z)))))
 row={'station':j+1,'sampled_radii_m':[.0035,.0045,.0055,.006],'front_annulus_samples':384,'front_annulus_ray_misses':miss,'max_front_plane_error_m':max(errors),'max_face_geometric_normal_tilt_from_pad_axis_degrees':max_tilt,'working_plane_w_m':pad['top']};assert not miss and max(errors)<5e-6,row;rows.append(row)
report={'source_sha256':check['source_sha256'],'actual_source_test':True,'historical_source_not_modified':True,'flat_pad_annuli':rows,'all_three_through_bore_clear':check['all_three_bores_ray_clear'],'rear_output_cover_surface_crossings':check['rear_output_cover_surface_crossings'],'working_planes_retained_not_measured':True,'angular_measurement_scope':'BVH face normals diagnostic only; float triangulation and boundary interpolation can magnify small height error. Plane acceptance is direct sampled coordinate error under5micrometres, not a physical machining tolerance.','source_fix_correctness_not_OEM_receipt':True,'art_accepted':False};(R/'creative/reviews/engine-cover-left-v2/fixation-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
