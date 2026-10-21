"""Actual retained wall rays: near-mouth lumens and finite working wall only."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-silencer-body-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'build-report.json').read_text());P=json.loads((H/'parameters.json').read_text());source=H/'exhaust-silencer-body-v1.blend';assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));o=bpy.data.objects[B['geometry'][0]['name']];m=o.data;m.calc_loop_triangles();tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True);first=Vector(P['working_front_centre_world_m']);last=Vector((first.x,P['working_sections_world'][-1]['y_m'],P['working_sections_world'][-1]['centre_z_m']));axis=Vector((0,1,0));rows=[];wall=[]
for name,origin,direction,length in [('header-authoring-mouth',first,axis,.030),('rear-closure-authoring-end',last,Vector((0,-1,0)),.08)]:
 A=Vector((1,0,0));A=(A-direction*A.dot(direction)).normalized();C=direction.cross(A)
 for i,offset in enumerate([Vector((0,0,0)),A*.004,-A*.004,C*.004,-C*.004]):
  start=origin-direction*.001+offset;hit=tree.ray_cast(start,direction,length+.001);row={'mouth':name,'sample':i,'origin_world_m':list(start),'direction_world':list(direction),'length_m':length+.001,'wall_hit':hit[0]is not None};rows.append(row);assert hit[0]is None,row
# First declared straight portion has constant true annular section.
centre=first+axis*.020;A=Vector((1,0,0));C=axis.cross(A);outer=P['working_sections_world'][0]['rx_m'];inner=outer-P['working_section_wall_m']
for j in range(4):
 radial=A*math.cos(j*math.pi/2)+C*math.sin(j*math.pi/2);start=centre+radial*(inner-.001);hit=tree.ray_cast(start,radial,.01);assert hit[0]is not None;innerpoint=hit[0];exit=tree.ray_cast(innerpoint+radial*1e-6,radial,.01);assert exit[0]is not None;thickness=(exit[0]-innerpoint).length;row={'angle_rad':j*math.pi/2,'sampled_wall_m':thickness,'working_nominal_wall_m':outer-inner,'difference_m':thickness-(outer-inner)};wall.append(row);assert abs(row['difference_m'])<2e-6,row
r={'component_id':B['component_id'],'source_sha256':sha(source),'export_sha256':B['export_sha256'],'lumen_rays':rows,'actual_wall_rays':wall,'scope':'Near-end true lumens and finite working wall in the retained authored mesh only. No exhaust flow, internal catalyst, real thickness or engine insertion certified.','all_dimensions_estimated':True,'art_accepted':False};(O/'opening-wall-check.json').write_text(json.dumps(r,indent=2)+'\n');print('SILENCER_OPENINGS',json.dumps(r))
