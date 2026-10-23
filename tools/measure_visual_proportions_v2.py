"""Read actual saved Blender vertices before/after, independently of the construction plan."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REV=ROOT/'creative/reviews/visual-proportions-v2'
def bounds(name):
 ob=bpy.data.objects[name];objects=[ob]+list(ob.children_recursive);p=[c.matrix_world@v.co for c in objects if c.type=='MESH' for v in c.data.vertices]
 return {'min':[min(v[i] for v in p) for i in range(3)],'max':[max(v[i] for v in p) for i in range(3)]}
def centroid_bounds(name):
 b=bounds(name);return [(x+y)/2 for x,y in zip(b['min'],b['max'])]
rows=[]
for stage,path in [('before','assembly-alignment-v1/motorcycle-aligned.blend'),('after','visual-proportions-v2/motorcycle-proportions.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets-src/moto-components'/path));bpy.context.view_layer.update()
 pivot=centroid_bounds('PARENT [WEWA_SWINGARM_PIVOT_SHAFT_ISOLATED]');axle=centroid_bounds('PARENT [reuse-rear-axle]');lamp=bounds('PARENT [headlamp-housing-v2]')
 cowl=next(o for o in bpy.context.scene.objects if o.type=='MESH' and (o.name=='Reprofiled headlamp cowl shell' if stage=='after' else o.name.startswith('Headlamp cowl shell')))
 rows.append({'stage':stage,'pivot_blender_m':pivot,'rear_axle_blender_m':axle,'swingarm_pivot_axis_slope_deg':math.degrees(math.atan2(pivot[2]-axle[2],axle[1]-pivot[1])),'housing_depth_m':lamp['max'][1]-lamp['min'][1],'cowl_vertices':len(cowl.data.vertices),'cowl_faces':len(cowl.data.polygons),'cowl_bounds':bounds(cowl.name),'front_wheel_bounds':bounds('PARENT [front-tyre]'),'rear_wheel_bounds':bounds('PARENT [rear-tyre]')})
assert rows[0]['rear_axle_blender_m']==rows[1]['rear_axle_blender_m']
assert rows[0]['front_wheel_bounds']==rows[1]['front_wheel_bounds'] and rows[0]['rear_wheel_bounds']==rows[1]['rear_wheel_bounds']
assert rows[0]['cowl_vertices']==rows[1]['cowl_vertices'] and rows[0]['cowl_faces']==rows[1]['cowl_faces']
assert 8.9 < rows[1]['swingarm_pivot_axis_slope_deg']-rows[0]['swingarm_pivot_axis_slope_deg'] < 9.1
assert rows[1]['housing_depth_m']>rows[0]['housing_depth_m']*1.6
(REV/'measured-check.json').write_text(json.dumps({'measurements':rows,'rear_axle_and_wheels_fixed':True,'native_cowl_topology_preserved':True,'export_zero_area_cleanup':'triangle-cleanup.json','tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
print('PROPORTIONS_MEASURED',[(r['stage'],r['swingarm_pivot_axis_slope_deg'],r['housing_depth_m']) for r in rows])
