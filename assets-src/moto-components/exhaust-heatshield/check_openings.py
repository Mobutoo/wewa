"""Read-only actual small bores and finite technical sheet X-wall rays."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-heatshield-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'build-report.json').read_text());P=json.loads((H/'parameters.json').read_text());source=H/'exhaust-heatshield-v1.blend';assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));o=bpy.data.objects[B['geometry'][0]['name']];m=o.data;m.calc_loop_triangles();tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True);body=json.loads((R/P['body_parameters']).read_text());sys.path.insert(0,str(H.parent/'exhaust-silencer-body'));from loft_geometry import pchip
Y=[q['y_m']for q in body['working_sections_world']];height=pchip(Y,[q['centre_z_m']for q in body['working_sections_world']]);axis=Vector((1,0,0));rows=[];walls=[]
for hole,(u,v)in enumerate(P['working_hole_centres_uv_m']):
 y=P['working_centre_y_m']+u;z=height(y)[0]+v
 for du,dv in [(0,0),(.001,0),(-.001,0),(0,.001),(0,-.001)]:
  start=Vector((-.26,y+du,z+dv));hit=tree.ray_cast(start,axis,.10);q={'hole':hole,'origin_world_m':list(start),'direction_world':list(axis),'length_m':.10,'wall_hit':hit[0]is not None};rows.append(q);assert hit[0]is None,q
for u in [-.06,0,.04]:
 for v in [-.015,.015]:
  y=P['working_centre_y_m']+u;z=height(y)[0]+v;start=Vector((-.26,y,z));entry=tree.ray_cast(start,axis,.10);assert entry[0]is not None;exit=tree.ray_cast(entry[0]+axis*1e-6,axis,.10);assert exit[0]is not None;distance=(exit[0]-entry[0]).length;row={'working_uv_m':[u,v],'sampled_X_sheet_wall_m':distance,'nominal_X_wall_m':P['working_wall_m'],'difference_m':distance-P['working_wall_m']};walls.append(row);assert abs(row['difference_m'])<2e-6,row
report={'component_id':B['component_id'],'source_sha256':sha(source),'export_sha256':B['export_sha256'],'lumen_rays':rows,'actual_wall_rays':walls,'scope':'Ten actual mesh rays through two small finite bores and six X-direction sheet wall samples. Technical working thickness is an X-coordinate difference, not a measured physical normal thickness or manufacturing tolerance. No artistic or real mounting reception.','all_dimensions_estimated':True,'art_accepted':False};(O/'opening-wall-check.json').write_text(json.dumps(report,indent=2)+'\n');print('HEATSHIELD_BORES',json.dumps(report))

rx=pchip(Y,[q['rx_m']for q in body['working_sections_world']]);rz=pchip(Y,[q['rz_m']for q in body['working_sections_world']]);holes=[]
for u,v in P['working_hole_centres_uv_m']:
 y=P['working_centre_y_m']+u;x=-.18-rx(y)[0]*(1-(v/rz(y)[0])**2)**.5-P['working_panel_to_body_airgap_m']+P['working_cup_depth_m'];holes.append({'working_front_seat_centre_world_m':[x,y,height(y)[0]+v],'technical_bore_axis_world':[1,0,0],'working_bore_radius_m':P['working_hole_radius_m'],'actual_metric_mounting_interface_received':False})
(H/'interfaces.json').write_text(json.dumps({'component_id':B['component_id'],'source_sha256':sha(source),'export_sha256':B['export_sha256'],'collection':'WEWA_EXHAUST_HEATSHIELD','root':o.parent.name,'datum_world_matrix':[list(r)for r in o.parent.matrix_world],'working_hole_frames':holes,'scope':'Exact candidate frame from explicit estimated parameters. No true fixing/standoff depth, clamp mechanism or fit approval; no screw heads or hidden mounts fabricated.','all_dimensions_estimated':True,'art_accepted':False},indent=2)+'\n')
