"""Source-hashed right shell interface inspection; no source or linked part saved."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/switchgear-right-v1';path=HERE/'switchgear-right-v1.blend'
bpy.ops.wm.open_mainfile(filepath=str(path));check=json.loads((OUT/'source-geometry-check.json').read_text());assert check['source_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
source=bpy.data.collections['WEWA_SWITCHGEAR_RIGHT'];bodies=[o for o in source.objects if o.type=='MESH' and 'shell - editable' in o.name]
def tree(o):
 deps=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(deps);m=e.to_mesh();t=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return t
bpy.context.view_layer.update();trees=[tree(o) for o in bodies]
red=bpy.data.objects['RH observed red top control - function unknown'];collar=bpy.data.objects['RH estimated black actuator collar'];pivot=red.parent;rest=pivot.matrix_world.copy();poses=[]
for depth in [0,.0004]:
 pivot.matrix_world=Matrix.Translation(Vector((0,0,-depth)))@rest;bpy.context.view_layer.update();t=tree(red);cross=[len(t.overlap(q)) for q in trees];collar_cross=len(t.overlap(tree(collar)));poses.append({'unverified_push_hypothesis_m':depth,'red_to_shell_crossings':cross,'red_to_collar_crossings':collar_cross})
pivot.matrix_world=rest;bpy.context.view_layer.update()
guides=bpy.data.collections.new('QA_READ_ONLY_THROTTLE_INTERFACE');bpy.context.scene.collection.children.link(guides)
throttle=HERE.parent/'throttle-control/throttle-control-v1.blend'
names=['Throttle sleeve and cable spool - moving candidate','Throttle fixed hollow cable guide - estimated','Throttle datum - physical RIGHT -X']
with bpy.data.libraries.load(str(throttle),link=False) as (available,loaded):
 for name in names:assert name in available.objects,name
 loaded.objects=names
for o in loaded.objects:guides.objects.link(o);o.hide_render=True
rotor=bpy.data.objects['Throttle sleeve and cable spool - moving candidate'];guide=bpy.data.objects['Throttle fixed hollow cable guide - estimated']
rotor.animation_data_clear();bpy.context.view_layer.update();guide_crossings=[len(tree(guide).overlap(t)) for t in trees];rotor_checks=[]
for angle in [0,-10,-20,-30,-40,-50]:
 rotor.rotation_euler.x=math.radians(angle);bpy.context.view_layer.update();crossings=[len(tree(rotor).overlap(t)) for t in trees];rotor_checks.append({'throttle_angle_degrees':angle,'rotor_to_shell_crossings':crossings})
result={'source_sha256':check['source_sha256'],'linked_throttle_source_sha256':hashlib.sha256(throttle.read_bytes()).hexdigest(),'scope':'Actual source triangle-crossing tests against separately fabricated estimated throttle components. Red control travel is a geometric hypothesis only; function/type unknown. No part is saved or altered.','red_control_poses':poses,'fixed_guide_to_shell_crossings':guide_crossings,'separate_throttle_rotor_poses':rotor_checks,'all_clear':not any(any(p['red_to_shell_crossings']) or p['red_to_collar_crossings'] for p in poses) and not any(guide_crossings) and not any(any(p['rotor_to_shell_crossings']) for p in rotor_checks),'exact_RDC_installation_verified':False,'art_accepted':False}
(OUT/'interface-check.json').write_text(json.dumps(result,indent=2)+'\n');print('WEWA_RH_INTERFACE',json.dumps(result));assert result['all_clear'],result
