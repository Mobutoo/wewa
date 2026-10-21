"""Original finned barrel casting. Exact125RDC identity/dimensions not certified.
RDC black exterior, related bare photos used only for decomposition. No piston/liner.
"""
from pathlib import Path
import bpy,json,math,sys,hashlib
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-cylinder-v1';O.mkdir(parents=True,exist_ok=True);P=json.loads((H/'parameters.json').read_text());sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,mesh_object,cylinder,box,csg,check_mesh,studio,export,tree_world
sys.path.insert(0,str(H.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_ENGINE_CYLINDER');s.collection.children.link(source);construction=bpy.data.collections.new('CYLINDER_RETAINED_CONSTRUCTION');s.collection.children.link(construction);guides=bpy.data.collections.new('CYLINDER_IMMUTABLE_INTERFACE_GUIDES');s.collection.children.link(guides);stage=bpy.data.collections.new('CYLINDER_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
black=material('Cylinder clean black coating - unmeasured original PBR',(.017,.020,.023),.03,.44)
# Closed original curved perimeter, no photograph texture or square stacked plates.
controls=[Vector(p)for p in P['fin_perimeter_controls_xy_m']]
def cat(a,b,c,d,t):return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
perimeter=[]
for i in range(len(controls)):
 for j in range(12):perimeter.append(cat(controls[(i-1)%len(controls)],controls[i],controls[(i+1)%len(controls)],controls[(i+2)%len(controls)],j/12))
assert sum(a.x*b.y-b.x*a.y for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]))>0
# Explicit rounded rim section, attached to flat fin faces; no post-union global bevel.
def rounded_fin(name,z,thickness,scale=1,edge=None):
 edge=min(edge or P['fin_edge_radius_working_m'],thickness*.45);profile=[]
 for j in range(13):
  a=-math.pi/2+math.pi/2*j/12;profile.append((z-thickness/2+edge+edge*math.sin(a),edge-edge*math.cos(a)))
 for j in range(13):
  a=math.pi/2*j/12;profile.append((z+thickness/2-edge+edge*math.sin(a),edge-edge*math.cos(a)))
 verts=[];faces=[];N=len(perimeter)
 for height,inset in profile:
  for i,p in enumerate(perimeter):
   tangent=(perimeter[(i+1)%N]-perimeter[(i-1)%N]).normalized();q=p*scale+Vector((-tangent.y,tangent.x))*inset;verts.append((q.x,q.y,height))
 for j in range(len(profile)-1):
  for i in range(N):k=(i+1)%N;faces.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
 faces.extend([tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]);return mesh_object(name,verts,faces,construction,black)
height=P['barrel_height_working_m'];core=cylinder('Barrel core closed original',(0,0,height/2),P['core_outer_radius_working_m'],height,construction,black,axis=(0,0,1),n=192)
features=[]
for index,(z,factor)in enumerate(zip(P['fin_centres_z_m'],P['fin_reach_factors_working'])):features.append(rounded_fin('Curved cooling fin original '+str(index+1),z,P['fin_thickness_working_m'],factor))
features.extend([rounded_fin('Base mating flange integral',.0035,.007,1.015,.0008),rounded_fin('Head mating deck integral',height-.0035,.007,.94,.0007)])
for i,(x,y)in enumerate(P['stud_centres_xy_working_m']):features.append(cylinder('Integral stud column '+str(i+1),(x,y,height/2),P['stud_boss_radius_working_m'],height,construction,black,axis=(0,0,1),n=96))
# Sidewell is a conditional related casting feature, hidden section not engineered.
tx,ty=P['timing_housing_centre_xy_working_m'];tw,td=P['timing_housing_size_xy_working_m'];features.append(box('Rounded side timing housing original',(tx,ty,height/2),(tw,td,height),construction,black,bevel=.003))
ax,ay,az=P['conditional_rear_accessory_seat_centre_xyz_working_m'];features.append(box('Conditional rear seat cast neck',(.040,.040,.024),(.035,.040,.036),construction,black,bevel=.003))
seat=cylinder('Conditional rear accessory annular seat',(ax,ay,az),P['conditional_rear_accessory_seat_radius_working_m'],.012,construction,black,axis=(0,1,0),n=128);bev=seat.modifiers.new('Original seat edge radius before CSG','BEVEL');bev.width=.00065;bev.segments=6;features.append(seat)
# Actual material passages; no fake dark discs or painted cooling gaps.
drills=[cylinder('True barrel material void',(0,0,height/2),P['material_bore_void_radius_working_m'],height+.04,construction,axis=(0,0,1),n=192)]
for i,(x,y)in enumerate(P['stud_centres_xy_working_m']):drills.append(cylinder('True stud passage '+str(i+1),(x,y,height/2),P['stud_through_bore_radius_working_m'],height+.04,construction,axis=(0,0,1),n=96))
wx,wy=P['timing_well_centre_xy_working_m'];ww,wd=P['timing_well_size_xy_working_m'];drills.append(box('True rounded timing throughwell',(wx,wy,height/2),(ww,wd,height+.04),construction,bevel=.002))
drills.append(cylinder('True conditional rear accessory bore',(ax,ay-.018,az),P['accessory_main_bore_radius_working_m'],.060,construction,axis=(0,1,0),n=128))
for i,x in enumerate(P['front_fin_notch_centres_x_working_m']):drills.append(cylinder('Conditional fin edge interruption '+str(i+1),(x,-.054,height/2),P['front_fin_notch_radius_working_m'],height+.04,construction,axis=(0,0,1),n=64))
body,ops=csg(core,features,drills,source,black,R,'Engine cylinder finned hollow casting - editable candidate');cleanup=clean_evaluated(body,construction);body.modifiers.clear();bpy.context.view_layer.objects.active=body;body.select_set(True);bpy.ops.mesh.customdata_custom_splitnormals_clear();check=check_mesh(body)
# Bare mating planes and cylindrical liner seat are unpainted interfaces.
# The pressed liner itself is a separate absent part, not fabricated as this casting.
machined=material('Cylinder unpainted mating surface - estimated aluminium PBR',(.43,.45,.47),.95,.32);body.data.materials.append(machined);machined_faces=0
for poly in body.data.polygons:
 c=poly.center;r=math.hypot(c.x,c.y);radial=Vector((c.x,c.y,0)).normalized() if r>1e-9 else Vector()
 plane=(abs(c.z)<2e-7 and poly.normal.z<-.999)or(abs(c.z-height)<2e-7 and poly.normal.z>.999)
 inner=abs(r-P['material_bore_void_radius_working_m'])<.000015 and poly.normal.dot(radial)<-.99
 if plane or inner:poly.material_index=1;machined_faces+=1
assert machined_faces>0
# Actual local through passage rays before estimated world placement.
from mathutils.bvhtree import BVHTree
tree=BVHTree.FromPolygons([v.co for v in body.data.vertices],[tuple(p.vertices)for p in body.data.polygons]);probe=[]
for name,x,y in [('centre bore',0,0)]+[('stud'+str(i+1),*p)for i,p in enumerate(P['stud_centres_xy_working_m'])]+[('timing well',wx,wy)]:
 hit,_,_,dist=tree.ray_cast(Vector((x,y,-.005)),Vector((0,0,1)),height+.01);assert hit is None,(name,hit,dist);probe.append({'name':name,'local_xy_m':[x,y],'through_clear':True})
# Candidate fit only: side datum and tilt estimates never derive from displacement124.45cm3.
datum=bpy.data.objects.new('Engine cylinder base provisional datum',None);source.objects.link(datum);datum.location=P['datum_world_working_m'];datum.rotation_euler.x=math.radians(P['forward_tilt_working_deg']);body.parent=datum;bpy.context.view_layer.update()
linked=[]
for folder,file,sha_expected,names in [('engine-cover-right','engine-cover-right-v2.blend','2558ea2479a02caf14e9feddad3f953f5587269083ae7b125a177acd4621515a',['Engine RH cover provisional datum','RH clutch cover hollow casting - editable candidate']),('engine-cover-left','engine-cover-left-v2.blend','f168aa9ef3e3c6e9b7bc2e884309d69da6fab736660ec6c8d1eaa29e7ecffe74',['Engine LH cover provisional datum','LH magneto cover hollow casting - editable candidate'])]:
 p=H.parent/folder/file;assert hashlib.sha256(p.read_bytes()).hexdigest()==sha_expected
 with bpy.data.libraries.load(str(p),link=True)as(a,b):b.objects=names
 for o in b.objects:guides.objects.link(o)
 linked.append({'source':str(p.relative_to(R)),'sha256':sha_expected})
bpy.context.view_layer.update();bt=tree_world(body);interfaces=[]
for o in guides.objects:
 if o.type=='MESH':interfaces.append({'guide':o.name,'surface_crossings':len(bt.overlap(tree_world(o))),'fit_certified':False})
construction.hide_render=True;construction.hide_viewport=True;guides.hide_render=True;guides.hide_viewport=True
export(H/'engine-cylinder-inspection.glb',[datum,body]);points=[body.matrix_world@Vector(p)for p in body.bound_box];target=sum(points,Vector())/len(points);studio(s,stage,target);s.camera.data.clip_start=.001
for o in stage.objects:
 if o.type=='MESH':o.location.z=min(p.z for p in points)-.002
 if o.type=='LIGHT':o.data.energy*=.08
body['all_dimensions_estimated']=True;body['art_accepted']=False;body['current_RDC_identity_certified']=False
bpy.ops.wm.save_as_mainfile(filepath=str(H/'engine-cylinder-v1.blend'),compress=True)
r={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':hashlib.sha256((H/'engine-cylinder-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((H/'engine-cylinder-inspection.glb').read_bytes()).hexdigest(),'collection':source.name,'parent_datum':datum.name,'geometry':[check],'cleanup':[cleanup],'actual_passage_probes':probe,'estimated_guide_surface_tests':interfaces,'linked_immutable_sources':linked,'machined_interface_face_count':machined_faces,'pressed_liner_manufactured':False,'fin_count_estimated':P['fin_count_working'],'boundaries_world_m':{'min':[min(p[i]for p in points)for i in range(3)],'max':[max(p[i]for p in points)for i in range(3)]},'all_dimensions_estimated':True,'current_RDC_identity_certified':False,'art_accepted':False};(H/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');print('CYLINDER_PREFLIGHT',json.dumps(r))
