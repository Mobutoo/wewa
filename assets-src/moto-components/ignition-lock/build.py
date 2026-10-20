"""Related PF232605 external lock/key candidate, never a recovered functional lock.
All physical dimensions, hidden sections and installed placement remain estimates.
"""
import json,sys,math,hashlib
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Euler
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE.parent/'throttle-control'))
from control_geometry import material,mesh_object,lathe,cylinder,box,csg,check_mesh,tree_world,studio,export
P=json.loads((HERE/'parameters.json').read_text());OUT=ROOT/'creative/reviews/ignition-lock-v1';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_IGNITION_LOCK');scene.collection.children.link(source)
construction=bpy.data.collections.new('IGNITION_RETAINED_CONSTRUCTION');scene.collection.children.link(construction)
stage=bpy.data.collections.new('IGNITION_STUDIO_NOT_EXPORTED');scene.collection.children.link(stage)
guides=bpy.data.collections.new('IGNITION_IMMUTABLE_INTERFACE_GUIDES');scene.collection.children.link(guides)
black=material('Ignition black coated housing - estimated',(.011,.013,.016),.12,.31)
plastic=material('Key moulded black polymer - estimated',(.008,.009,.011),0,.46)
steel=material('Key and rotor satin metal - estimated',(.42,.45,.48),.92,.25)
white=material('Ignition original printed marks',(.66,.69,.70),0,.54)
datum=bpy.data.objects.new('Ignition provisional lower cockpit datum',None);source.objects.link(datum);datum.location=P['datum_origin_world_m_estimated'];datum.rotation_euler=tuple(math.radians(x) for x in P['datum_rotation_euler_xyz_degrees_estimated'])
def latheZ(name,section,collection,mat,n=128):
 o=lathe(name,section,collection,mat,n);o.rotation_euler.y=-math.pi/2;return o
section=[(-.066,.008),(-.066,.013),(-.062,.0145),(-.042,.0145),(-.038,.016),(-.003,.016),(-.001,.0165),(0,.0165),(0,.011),(-.002,.011),(-.003,.0108),(-.059,.0108),(-.059,.008)]
casebase=latheZ('Lock hollow stepped housing construction',section,construction,black,160)
features=[]
for i in range(P['rear_rib_count_estimated']):
 a=math.tau*i/P['rear_rib_count_estimated'];r=.0144
 o=box('Observed rear rib section - hidden dimensions estimated',(r*math.cos(a),r*math.sin(a),-.051),(.0027,.0025,.022),construction,bevel=.0006);o.rotation_euler.z=a;features.append(o)
features.append(box('Rear mounting bridge',(0,.006,-.060),(.050,.014,.007),construction,bevel=.0018))
for side in [-1,1]:features.append(cylinder('Rounded mounting lug',(side*.019,.006,-.060),.007,.007,construction,axis=(0,0,1),n=80))
drills=[cylinder('Estimated mounting bore',(side*.019,.006,-.060),.0031,.022,construction,axis=(0,0,1),n=80) for side in [-1,1]]
# Small visible rectangular relief: not a connector/pinout assertion.
drills.append(box('Side rectangular housing window',(.0158,0,-.017),(.004,.004,.0035),construction,bevel=.00025))
bpy.context.view_layer.update();case,case_csg=csg(casebase,features,drills,source,black,ROOT,'Ignition ribbed hollow housing and mounting ears - candidate')
rotorbase=cylinder('Front metallic rotor construction',(0,0,-.0015),.0106,.005,construction,axis=(0,0,1),n=160)
slot=box('Actual rotor key slit',(0,0,-.001),(.009,.0020,.012),construction,bevel=.00015)
bpy.context.view_layer.update();rotor,rotor_csg=csg(rotorbase,[],[slot],source,steel,ROOT,'Ignition front rotor - presentation states')
# The generic blade uses an openly estimated tooth outline; it is not a real key code.
def extrude_xz(name,outline,halfthick,collection,mat):
 n=len(outline);verts=[(x,y,z) for y in [-halfthick,halfthick] for x,z in outline]
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh_object(name,verts,faces,collection,mat)
bladeoutline=[(-.0038,-.008),(.0038,-.008),(.0038,.008),(.0024,.010),(.0036,.012),(.0019,.015),(.0036,.018),(.0023,.021),(.0038,.024),(.0038,.030),(-.0038,.030)]
bladebase=extrude_xz('Generic key blade construction',bladeoutline,.00078,construction,steel)
groove=box('Estimated blade longitudinal groove',(-.0017,-.0008,.013),(.0009,.0005,.030),construction,bevel=.00015)
bpy.context.view_layer.update();blade,blade_csg=csg(bladebase,[],[groove],source,steel,ROOT,'Key metal blade - generic nonfunctional cut')
headoutline=[(-.006,.027),(.006,.027),(.014,.047),(.010,.056),(-.010,.056),(-.014,.047)]
headbase=extrude_xz('Key bevelled head construction',headoutline,.0020,construction,plastic)
bevel=headbase.modifiers.new('Moulded head edge roll estimate','BEVEL');bevel.width=.0011;bevel.segments=4
hole=extrude_xz('Key head polygonal ring opening',[(-.0068,.040),(.0068,.040),(.0076,.048),(.0058,.051),(-.0058,.051),(-.0076,.048)],.006,construction,None)
grooves=[]
for sign in [-1,1]:
 for i in range(3):
  o=box('Head diagonal grip groove',(-.006+i*.004,sign*.002,.033+i*.001),(.001,.0011,.008),construction,bevel=.0003);o.rotation_euler.y=-.55;grooves.append(o)
bpy.context.view_layer.update();head,head_csg=csg(headbase,[],[hole]+grooves,source,plastic,ROOT,'Key black moulded head - estimated')
moving=bpy.data.objects.new('Ignition rotor and key state pivot',None);source.objects.link(moving);moving.parent=datum
rotor.parent=moving;blade.parent=moving;head.parent=moving;case.parent=datum
for obj in [rotor,blade,head,case]:obj['art_accepted']=False;obj['all_dimensions_estimated']=True
for obj in [rotor,blade,head,case]:
 bm=bmesh.new();bm.from_mesh(obj.data)
 for e in bm.edges:e.smooth=e.is_manifold and e.calc_face_angle(0)<.70
 bm.to_mesh(obj.data);bm.free()
 normal=obj.modifiers.new('Preserve flat machined and moulded faces','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=50;normal.mode='FACE_AREA_WITH_ANGLE'
blade['not_functional_key_code']=True
# Text is original scene lettering in ordinary font, not photograph/stamp reuse.
marks=[]
for text,angle in [('LOCK',-135),('PUSH',180),('IGNITION',-35),('O',90)]:
 a=math.radians(angle);data=bpy.data.curves.new('Original '+text+' marking','FONT');data.body=text;data.align_x='CENTER';data.size=.0018;data.extrude=0
 o=bpy.data.objects.new('Ignition '+text+' label - original geometry',data);source.objects.link(o);o.parent=datum;o.location=(.0137*math.cos(a),.0137*math.sin(a),.00016);o.rotation_euler.z=a-math.pi/2;data.materials.append(white);o['structural_closed_volume']=False;marks.append(o)
sys.path.insert(0,str(HERE.parent/'clutch-control'))
from topology_cleanup_v2 import clean_evaluated
mark_cleanup=[]
for mark in marks:
 editable=mark.copy();editable.data=mark.data.copy();editable.name='Editable font construction '+mark.name;construction.objects.link(editable);editable.hide_render=True;editable.hide_set(True)
 bpy.ops.object.select_all(action='DESELECT');mark.select_set(True);bpy.context.view_layer.objects.active=mark;bpy.ops.object.convert(target='MESH');bpy.context.view_layer.update()
 mark_cleanup.append(clean_evaluated(mark,construction,require_closed=False))
for frame,angle in [(1,0),(13,-35),(25,45)]:moving.rotation_euler.z=math.radians(angle);moving.keyframe_insert(data_path='rotation_euler',frame=frame)
moving.animation_data.action.name='Ignition OFF LOCK ON presentation states - angles estimated'
scene.frame_start=1;scene.frame_end=25;scene.render.fps=24;scene.frame_set(1);bpy.context.view_layer.update()
checks=[check_mesh(o) for o in [case,rotor,blade,head]]
case_tree=tree_world(case);poses=[]
for label,angle in P['rotor_states_degrees_estimated'].items():
 moving.animation_data.action=None;moving.rotation_euler.z=math.radians(angle);bpy.context.view_layer.update()
 crossings={o.name:len(case_tree.overlap(tree_world(o))) for o in [rotor,blade,head]};poses.append({'state':label,'presentation_angle_deg':angle,'surface_crossings_case':crossings});assert not any(crossings.values()),poses[-1]
for frame,angle in [(1,0),(13,-35),(25,45)]:moving.rotation_euler.z=math.radians(angle);moving.keyframe_insert(data_path='rotation_euler',frame=frame)
moving.animation_data.action.name='Ignition OFF LOCK ON presentation states - angles estimated'
scene.frame_set(1);bpy.context.view_layer.update()
# Read-only cockpit reference; locally masked collection survives save/reload.
guidecheck=json.loads((ROOT/'creative/reviews/instruments-v1/source-geometry-check.json').read_text())
guide_names=[r['name'] for r in guidecheck['closed_structural_bodies']]+['INSTRUMENT_CLUSTER_MOUNT']
with bpy.data.libraries.load(str(HERE.parent/'instruments/instruments-v1.blend'),link=True) as (available,loaded):loaded.objects=guide_names
guideobjects=list(loaded.objects)
for o in guideobjects:guides.objects.link(o)
bpy.context.view_layer.update();interface=[]
for obj in guideobjects:
 if obj.type=='MESH' and obj.get('structural_closed_volume',False):
  tree=tree_world(obj)
  row={'instrument':obj.name,'crossings':{o.name:len(tree.overlap(tree_world(o))) for o in [case,rotor,blade,head]}}
  interface.append(row)
  assert not any(row['crossings'].values()),row
guides.hide_render=True;guides.hide_viewport=True
construction.hide_render=True;construction.hide_viewport=True
export(HERE/'ignition-lock-inspection.glb',[datum,moving,case,rotor,blade,head]+marks,animations=True)
target=Vector(P['datum_origin_world_m_estimated']);studio(scene,stage,target)
points=[o.matrix_world@Vector(v) for o in [case,rotor,blade,head] for v in o.bound_box]
for o in stage.objects:
 if o.type=='MESH':o.location.z=min(v.z for v in points)-.001
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'ignition-lock-v1.blend'),compress=True)
report={'component_id':P['component_id'],'source_sha256':hashlib.sha256((HERE/'ignition-lock-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'ignition-lock-inspection.glb').read_bytes()).hexdigest(),'geometry':checks,'state_poses':poses,'datum_world_m_estimated':P['datum_origin_world_m_estimated'],'datum_rotation_euler_xyz_degrees_estimated':P['datum_rotation_euler_xyz_degrees_estimated'],'rotor_axis_local':[0,0,1],'bounds_world_m':{'min':[min(v[i] for v in points) for i in range(3)],'max':[max(v[i] for v in points) for i in range(3)]},'functional_lock_created':False,'generic_key_not_real_cut_code':True,'full_harness_created':False,'mount_interface_certified':False,'installed_125HD_position_confirmed':False,'all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False}
report['instrument_interface_rest_BVH']=interface
report['printed_mark_topology_cleanup']=mark_cleanup
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps({'preflight':report,'CSG':[{'name':name,**{k:v for k,v in row.items() if k not in ['vertices','triangles']}} for name,row in [('housing',case_csg),('rotor',rotor_csg),('blade',blade_csg),('head',head_csg)]]},indent=2)+'\n')
print('WEWA_IGNITION_PREFLIGHT',json.dumps(report))
