"""Only photographed exposed sheath sections. Missing spans remain absent.
No brake/speedometer assignment, false hub connection or invented pinout.
"""
import bpy,bmesh,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector,Euler
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE.parent/'throttle-control'))
from control_geometry import material,mesh_object,check_mesh,tree_world,studio,export
P=json.loads((HERE/'parameters-v2.json').read_text());OUT=ROOT/'creative/reviews/cockpit-cables-v2';OUT.mkdir(parents=True,exist_ok=True)
assert hashlib.sha256((ROOT/P['guide_source']).read_bytes()).hexdigest()==P['guide_source_sha256'],'Shared guide changed: re-read its study before fabrication'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_COCKPIT_CABLES_PARTIAL');scene.collection.children.link(source)
guides=bpy.data.collections.new('CABLES_IMMUTABLE_INTERFACE_GUIDES');scene.collection.children.link(guides)
stage=bpy.data.collections.new('CABLES_STUDIO_NOT_EXPORTED');scene.collection.children.link(stage)
rubber=material('Cable sheath original black polymer - estimated',(.008,.010,.012),0,.48)
parts=[];curvature=[]
def tube(name,landmarks,outer,inner):
 land=[Vector(v) for v in landmarks];points=[]
 for i in range(len(land)-1):
  a,b,c,d=[land[max(0,min(len(land)-1,j))] for j in [i-1,i,i+1,i+2]]
  for k in range(18):
   t=k/18;points.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 points.append(land[-1]);n=48;verts=[];faces=[];normal=None
 for i,p in enumerate(points):
  tangent=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
  if normal is None:
   normal=tangent.cross(Vector((1,0,0)))
   if normal.length<.01:normal=tangent.cross(Vector((0,1,0)))
  normal=(normal-tangent*normal.dot(tangent)).normalized();binormal=tangent.cross(normal).normalized()
  for radius in [outer,inner]:
   for j in range(n):a=math.tau*j/n;verts.append(tuple(p+radius*(normal*math.cos(a)+binormal*math.sin(a))))
 for i in range(len(points)-1):
  for side in [0,1]:
   for j in range(n):
    a=i*2*n+side*n+j;b=i*2*n+side*n+(j+1)%n;c=(i+1)*2*n+side*n+(j+1)%n;d=(i+1)*2*n+side*n+j;faces.append((a,b,c,d) if not side else (d,c,b,a))
 for endpoint in [0,len(points)-1]:
  offset=endpoint*2*n
  for j in range(n):faces.append((offset+j,offset+(j+1)%n,offset+n+(j+1)%n,offset+n+j))
 o=mesh_object(name,verts,faces,source,rubber);o['truncated_visible_study']=True;o['not_a_factory_closed_terminal']=True;o['all_dimensions_estimated']=True;o['art_accepted']=False
 bm=bmesh.new();bm.from_mesh(o.data)
 for e in bm.edges:e.smooth=e.is_manifold and e.calc_face_angle(0)<.70
 bm.to_mesh(o.data);bm.free()
 radii=[]
 for a,b,c in zip(points,points[1:],points[2:]):
  x=(b-a).length;y=(c-b).length;z=(c-a).length;cross=(b-a).cross(c-a).length
  if cross>1e-12:radii.append(x*y*z/(2*cross))
 curvature.append({'name':name,'length_m_estimated':sum((b-a).length for a,b in zip(points,points[1:])),'min_discrete_centreline_radius_m':min(radii),'radius_is_manufacturer_limit':False,'outer_radius_m_estimated':outer,'inner_radius_m_estimated':inner,'free_end_centres_world_m':[list(points[0]),list(points[-1])]})
 parts.append(o);return o
for item in P['front_sheaths']:
 pts=[(item['depth_X_m_estimated'],P['guide_front_axle_world_yz_m'][0]+(u-P['photo04_front_axle_px'][0])*P['baseline_guide_m_per_px'],P['guide_front_axle_world_yz_m'][1]-(v-P['photo04_front_axle_px'][1])*P['baseline_guide_m_per_px']) for u,v in item['source_native_pixel_trace']]
 o=tube(item['name'],pts,item['outer_radius_m_estimated'],item['inner_radius_m_estimated']);o['function']='Unassigned: brake vs speedometer unresolved';o['hub_connection_certified']=False
contact=HERE.parent/'ignition-lock/ignition-lock-v1.blend';contactsha=hashlib.sha256(contact.read_bytes()).hexdigest();assert contactsha==P['fixed_source_hashes']['contact'];contactP=json.loads((HERE.parent/'ignition-lock/parameters.json').read_text());rotation=Euler(tuple(math.radians(v) for v in contactP['datum_rotation_euler_xyz_degrees_estimated'])).to_matrix();origin=Vector(contactP['datum_origin_world_m_estimated'])
item=P['ignition_pigtail'];loop=tube(item['name'],[origin+rotation@Vector(v) for v in item['local_control_points_m_estimated']],item['outer_radius_m_estimated'],item['inner_radius_m_estimated']);loop['connector_created']=False;loop['pinout_known']=False
with bpy.data.libraries.load(str(contact),link=True) as (available,loaded):loaded.objects=['Ignition provisional lower cockpit datum','Ignition ribbed hollow housing and mounting ears - candidate']
for o in loaded.objects:guides.objects.link(o)
bpy.context.view_layer.update();case=loaded.objects[-1];crossings=len(tree_world(case).overlap(tree_world(loop)));assert not crossings,crossings
# Current immutable cockpit cases linked with their existing matrices, never repositioned.
interface_rows=[];interface_sources=[]
for key,relative,collection in [('instruments','instruments/instruments-v3.blend','WEWA_INSTRUMENTS_SEPARATE_PARTS'),('visor','instrument-visor/instrument-visor-v1.blend','WEWA_INSTRUMENT_VISOR')]:
 path=HERE.parent/relative;before=hashlib.sha256(path.read_bytes()).hexdigest();assert before==P['fixed_source_hashes'][key]
 with bpy.data.libraries.load(str(path),link=True)as(available,loaded):loaded.collections=[collection]
 linked=loaded.collections[0];guides.children.link(linked);bpy.context.view_layer.update()
 guide_objects=list(linked.all_objects);loop_tree=tree_world(loop)
 for obj in guide_objects:
  if obj.type!='MESH':continue
  count=len(loop_tree.overlap(tree_world(obj)));row={'guide_group':key,'object':obj.name,'actual_BVH_triangle_crossings':count};interface_rows.append(row);assert count==0,row
 assert hashlib.sha256(path.read_bytes()).hexdigest()==before
 interface_sources.append({'group':key,'path':str(path.relative_to(ROOT)),'sha256':before,'source_modified':False,'matrices_preserved':True})
checks=[check_mesh(o) for o in parts];pair_crossings=[]
for i,a in enumerate(parts):
 for b in parts[i+1:]:
  count=len(tree_world(a).overlap(tree_world(b)));pair_crossings.append({'a':a.name,'b':b.name,'crossings':count});assert not count
guides.hide_render=True;guides.hide_viewport=True
export(HERE/'cockpit-cables-v2-inspection.glb',parts,animations=False)
target=Vector((.105,-.22,-.54));studio(scene,stage,target)
points=[o.matrix_world@Vector(v) for o in parts for v in o.bound_box]
for o in stage.objects:
 if o.type=='MESH':o.location.z=min(v.z for v in points)-.002
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'cockpit-cables-v2.blend'),compress=True)
report={'component_id':P['component_id'],'source_sha256':hashlib.sha256((HERE/'cockpit-cables-v2.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'cockpit-cables-v2-inspection.glb').read_bytes()).hexdigest(),'contact_guide_sha256':contactsha,'geometry':checks,'centreline_studies':curvature,'pair_surface_crossings':pair_crossings,'pigtail_to_contact_case_surface_crossings':crossings,'current_cockpit_interfaces':interface_rows,'immutable_interface_sources':interface_sources,'fixed_endpoint_delta_world_m':[0,0,-.008],'bounds_world_m':{'min':[min(v[i] for v in points) for i in range(3)],'max':[max(v[i] for v in points) for i in range(3)]},'lower_sheath_functions_confirmed':False,'free_cut_ends_not_factory_terminals':True,'complete_harness_created':False,'full_steering_motion_tested':False,'JA_DS_terminal_certified':False,'all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report-v2.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_PARTIAL_CABLES_PREFLIGHT',json.dumps(report))
