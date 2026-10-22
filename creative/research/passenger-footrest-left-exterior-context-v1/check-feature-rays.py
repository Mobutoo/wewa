import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');K='passenger-footrest-left-exterior-context-v1';H=R/'assets-src/moto-components'/K;D=R/'creative/research'/K;bpy.ops.wm.open_mainfile(filepath=str(H/(K+'.blend')));bpy.context.view_layer.update();rows=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob['source_parent']=='passenger-footrest-rubber-jk113008-v1':continue
 m=ob.data;ps=[ob.matrix_world@v.co for v in m.vertices];tree=BVHTree.FromPolygons(ps,[list(p.vertices)for p in m.polygons],all_triangles=False);center=Vector((-.006,.239,.0145 if ob['source_parent']=='passenger-footrest-stay-left-v1'else .0195));direction=Vector((0,1,0));clear=tree.ray_cast(center-direction*.035,direction,.07)[0]is None
 rows.append({'parent':ob['source_parent'],'declared_hole_axis_center_context_m':list(center),'axis':[0,1,0],'actual_axis_ray_clear_in_own_mesh':clear,'ray_scope':'Individual source only, not a pin through both components or hidden-seat fit'});assert clear
(D/'feature-axis-ray-check.json').write_text(json.dumps({'sources':rows,'axes_parallel_not_coaxial':True,'axis_center_offset_m':.005,'no_pin_created':True,'fit_qualified':False},indent=2)+'\n')
