"""Cable throttle carrier alone. Hidden geometry and travel are bounded estimates.
External switchgear shell is a different component. Never a hydraulic control.
"""
import sys,json,math,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
from control_geometry import material,lathe,cylinder,csg,check_mesh,tree_world,frame_matrix,studio,export
P=json.loads((HERE/'parameters.json').read_text());OUT=ROOT/'creative/reviews/throttle-control-v1';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_THROTTLE_CONTROL');scene.collection.children.link(source)
construction=bpy.data.collections.new('THROTTLE_CONSTRUCTION_RETAINED');scene.collection.children.link(construction)
guides=bpy.data.collections.new('THROTTLE_LINKED_INTERFACE_GUIDES');scene.collection.children.link(guides)
stage=bpy.data.collections.new('THROTTLE_STUDIO_NOT_EXPORTED');scene.collection.children.link(stage)
polymer=material('Throttle carrier pale polymer - estimated',(.55,.53,.45),0,.42);black=material('Throttle cable guide polymer - estimated',(.012,.014,.017),0,.55)
section=[(.002,.01125),(.002,.01235),(.003,.0125),(.120,.0125),(.121,.0125),(.122,.0140),(.122,.0182),(.1225,.0185),(.124,.0185),(.1246,.0174),(.1274,.0174),(.128,.0185),(.1295,.0185),(.130,.0180),(.130,.01125)]
base=lathe('Carrier sleeve and cable-spool construction',section,construction,polymer,n=192)
drill=cylinder('Estimated cable nipple seat',(.126,-.0108,.0132),.0022,.006,construction,axis=(1,0,0),n=64)
rotor,csg_report=csg(base,[],[drill],source,polymer,ROOT,'Throttle sleeve and cable spool - moving candidate')
# Small fixed hollow receiver, separate from the external electrical housing.
guide=lathe('Throttle fixed hollow cable guide - estimated',[(-.009,.0012),(-.009,.0028),(-.007,.0032),(.006,.0032),(.009,.004),(.010,.004),(.010,.0012)],source,black,n=96)
guide.rotation_euler.z=math.pi/2;guide.location=(.126,-.024,.022)
fixed=bpy.data.objects.new('Throttle datum - physical RIGHT -X',None);source.objects.link(fixed);fixed.matrix_world=frame_matrix(P['endpoint_m'],P['axis_inward_vector'])
rotor.parent=fixed;guide.parent=fixed
rotor['scope']='Carrier/spool only, rubber grip separate; actual cam hidden in photo and estimated';rotor['art_accepted']=False
for frame,angle in [(1,0),(25,25),(49,50)]:
 rotor.rotation_euler.x=-math.radians(angle);rotor.keyframe_insert(data_path='rotation_euler',frame=frame)
rotor.animation_data.action.name='Throttle working range 0 to 50 degrees - estimated'
scene.frame_start=1;scene.frame_end=49;scene.render.fps=24;scene.frame_set(1);bpy.context.view_layer.update()
checks=[check_mesh(o) for o in [rotor,guide]]
# Linked guide sources are immutable; only these selected geometry objects load.
def link_object(path,name):
 with bpy.data.libraries.load(str(path),link=True) as (available,loaded):
  assert name in available.objects,(path,name);loaded.objects=[name]
 obj=loaded.objects[0];guides.objects.link(obj);obj.hide_render=True;return obj
grip=link_object(HERE.parent/'handlebar-grips/handlebar-grips-v2.blend','Right rubber grip - editable candidate')
bar=link_object(HERE.parent/'handlebar/handlebar-v1.blend','Handlebar bare continuous tube - editable candidate')
bpy.context.view_layer.update();grip_tree=tree_world(grip);bar_tree=tree_world(bar);guide_tree=tree_world(guide)
poses=[]
for angle in P['working_rotation_degrees']:
 scene.frame_set(1);rotor.animation_data.action=None;rotor.rotation_euler.x=-math.radians(angle);bpy.context.view_layer.update();tree=tree_world(rotor)
 row={'opening_degrees':angle,'local_X_rotation_degrees':-angle,'surface_crossings_grip':len(tree.overlap(grip_tree)),'surface_crossings_bar':len(tree.overlap(bar_tree)),'surface_crossings_fixed_guide':len(tree.overlap(guide_tree))};poses.append(row);assert not any(v for k,v in row.items() if k.startswith('surface_crossings')),row
# Test a real mesh point on the upper sleeve, not a guessed mathematical axis.
vertex=max((v for v in rotor.data.vertices if .003<v.co.x<.120),key=lambda v:v.co.y)
direction_points=[]
for angle in [0,50]:
 rotor.rotation_euler.x=-math.radians(angle);bpy.context.view_layer.update();direction_points.append(list(rotor.matrix_world@vertex.co))
direction={'actual_mesh_vertex_index':vertex.index,'local_mesh_position_m':list(vertex.co),'world_position_closed_m':direction_points[0],'world_position_open50_m':direction_points[1],'delta_world_Y_m':direction_points[1][1]-direction_points[0][1],'opening_rotation_axis_local':[-1,0,0],'opening_angle_range_degrees':[0,50]}
assert direction['delta_world_Y_m']>0,direction
# Recreate the demonstration animation after read-only pose tests.
for frame,angle in [(1,0),(25,25),(49,50)]:rotor.rotation_euler.x=-math.radians(angle);rotor.keyframe_insert(data_path='rotation_euler',frame=frame)
rotor.animation_data.action.name='Throttle working range 0 to 50 degrees - estimated'
scene.frame_set(1);bpy.context.view_layer.update()
guides.hide_render=True
for obj in guides.objects:obj.hide_set(True)
export(HERE/'throttle-control-inspection.glb',[fixed,rotor,guide],animations=True)
target=Vector(P['endpoint_m'])+Vector(P['axis_inward_vector']).normalized()*.065;studio(scene,stage,target)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'throttle-control-v1.blend'),compress=True)
report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':hashlib.sha256((HERE/'throttle-control-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'throttle-control-inspection.glb').read_bytes()).hexdigest(),'geometry':checks,'motion_poses':poses,'scope':'Actual meshes and six working poses; not measured cable actuation or exact RDC throttle','candidate_clearances_m':{'tube_to_sleeve_radial':.00015,'sleeve_to_rubber_radial':.0002,'spool_to_reserved_housing_radial':.0005},'all_dimensions_and_motion_estimated':True,'linked_grip_revision':'handlebar-grips-v2 corrected handedness','external_housing_created':False,'full_cable_modelled':False,'physical_iphone_tested':False,'art_accepted':False}
report['opening_direction_geometry_test']=direction
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps({'preflight':report,'CSG':{k:v for k,v in csg_report.items() if k not in ['vertices','triangles']}},indent=2)+'\n');print('WEWA_THROTTLE_PREFLIGHT',json.dumps(report))
