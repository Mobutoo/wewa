"""Separate related-variant filter-cap candidate; every dimension/ear station estimated."""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/engine-filter-cap-v1';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(HERE.parent/'throttle-control'));from control_geometry import material,mesh_object,cylinder,csg,check_mesh,tree_world,export,studio
sys.path.insert(0,str(HERE.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
P=json.loads((HERE/'parameters.json').read_text());parent=HERE.parent/'engine-cover-right/engine-cover-right-v1.blend';parent_sha=hashlib.sha256(parent.read_bytes()).hexdigest();assert parent_sha=='185274d117291007e185fba8209abac91153ece3ae9e4a0a8ce5a67667c4331f'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_ENGINE_FILTER_CAP');s.collection.children.link(source)
construction=bpy.data.collections.new('ENGINE_FILTER_CAP_RETAINED_CONSTRUCTION');s.collection.children.link(construction)
guides=bpy.data.collections.new('ENGINE_FILTER_CAP_IMMUTABLE_CASE_GUIDE');s.collection.children.link(guides)
stage=bpy.data.collections.new('ENGINE_FILTER_CAP_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
paint=material('Engine filter cap silver coating - estimated PBR',(.43,.45,.47),.20,.40);u,v=P['centre_local_uv_m'];back=P['rear_seat_w_working_m'];front=P['face_front_w_working_m'];rear=P['spigot_rear_w_working_m']
def revolve(name,profile,n=192):
 verts=[];indices=[];faces=[]
 for w,r in profile:
  if r==0:indices.append([len(verts)]*n);verts.append((u,v,w))
  else:
   indices.append(list(range(len(verts),len(verts)+n)))
   verts.extend((u+r*math.cos(math.tau*i/n),v+r*math.sin(math.tau*i/n),w) for i in range(n))
 for k in range(len(profile)):
  a=indices[k];b=indices[(k+1)%len(profile)]
  if profile[k][1]==0 and profile[(k+1)%len(profile)][1]==0:continue
  for i in range(n):
   j=(i+1)%n;face=list(dict.fromkeys([a[i],b[i],b[j],a[j]]))
   if len(face)>=3:faces.append(tuple(face))
 return mesh_object(name,verts,faces,construction,paint)
profile=[(front-.0028,0),(front-.0028,.0253),(rear,.0253),(rear,.0275),(back,.0275),(back,.039),(back+.0006,.040),(front-.001,.040),(front,.039),(front,.0305),(front+.0004,.030),(front+.0004,.0275),(front,.027),(front,0)]
base=revolve('Continuous cup face ring and rear spigot construction',profile)
features=[];drills=[]
for k,angle in enumerate(P['fastening_angles_working_degrees']):
 a=math.radians(angle);x=u+.038*math.cos(a);y=v+.038*math.sin(a)
 ear=cylinder('Related catalogue fastening ear estimate '+str(k+1),(x,y,(back+front)/2),.0055,front-back,construction,paint,axis=(0,0,1),n=96)
 bevel=ear.modifiers.new('Moulded ear lip radius estimate','BEVEL');bevel.width=.00045;bevel.segments=3;features.append(ear)
 drills.append(cylinder('Ear screw bore estimate '+str(k+1),(x,y,.040),.0032,.030,construction,axis=(0,0,1),n=96))
bpy.context.view_layer.update();cap,operations=csg(base,features,drills,source,paint,ROOT,'RH oil filter cap - editable candidate')
normal=cap.modifiers.new('Preserve cap face plane and ear curves','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=50
cleanup=clean_evaluated(cap,construction)
cap.modifiers.clear()
bpy.ops.object.select_all(action='DESELECT');cap.select_set(True);bpy.context.view_layer.objects.active=cap
bpy.ops.mesh.customdata_custom_splitnormals_clear();cap.data.update()
# Real plate planes stay flat; smooth only curved cup/ring/ear surfaces.
for polygon in cap.data.polygons:polygon.use_smooth=abs(polygon.normal.z)<.99999
datum=bpy.data.objects.new('RH oil filter cap provisional datum',None);source.objects.link(datum);x,y,z=P['parent_datum_world_m'];datum.matrix_world=Matrix(((0,0,-1,x),(-1,0,0,y),(0,1,0,z),(0,0,0,1)));cap.parent=datum
cap['all_dimensions_estimated']=True;cap['three_ears_current_RDC_certified']=False;cap['art_accepted']=False
with bpy.data.libraries.load(str(parent),link=True) as (available,loaded):loaded.objects=['Engine RH cover provisional datum','RH clutch cover hollow casting - editable candidate']
for o in loaded.objects:guides.objects.link(o)
bpy.context.view_layer.update();case=bpy.data.objects['RH clutch cover hollow casting - editable candidate'];crossings=len(tree_world(case).overlap(tree_world(cap)));assert crossings==0,('Cap/case intersection',crossings)
checks=check_mesh(cap);construction.hide_render=True;construction.hide_viewport=True;guides.hide_render=True;guides.hide_viewport=True
export(HERE/'engine-filter-cap-inspection.glb',[datum,cap]);points=[cap.matrix_world@Vector(c) for c in cap.bound_box];target=sum(points,Vector())/len(points);studio(s,stage,target)
for o in stage.objects:
 if o.type=='MESH':o.location.z=min(c.z for c in points)-.002
 if o.type=='LIGHT':o.data.energy*=.08
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'engine-filter-cap-v1.blend'),compress=True)
report={'component_id':P['component_id'],'source_sha256':hashlib.sha256((HERE/'engine-filter-cap-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'engine-filter-cap-inspection.glb').read_bytes()).hexdigest(),'parent_source_sha256':parent_sha,'collection':source.name,'geometry':[checks],'cleanup':cleanup,'interface_case_surface_crossings':crossings,'radial_spigot_to_parent_bore_gap_working_m':.0005,'axial_gasket_gap_working_m':.0005,'gasket_or_filter_element_fabricated':False,'three_ears_only_documented_related_variant':True,'normal_policy':'Inherited baked weighted custom normals explicitly cleared; plate planes flat and curved zones interpolated','custom_normals_present':cap.data.has_custom_normals,'matching_case_screw_stations_certified':False,'datum_world_m_estimated':P['parent_datum_world_m'],'cap_centre_local_uvw_m':[u,v,(front+rear)/2],'bounds_world_m':{'min':[min(c[i] for c in points) for i in range(3)],'max':[max(c[i] for c in points) for i in range(3)]},'all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps({'preflight':report,'CSG':{k:v for k,v in operations.items() if k not in ['vertices','triangles']}},indent=2)+'\n');print('WEWA_FILTER_CAP_PREFLIGHT',json.dumps(report))
