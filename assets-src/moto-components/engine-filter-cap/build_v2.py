"""Original v2 cap: continuous blended ear outline and real section radii.
No global bevel afterCSG, all new radii estimated and related variant conditional.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-filter-cap-v2';O.mkdir(exist_ok=True);P=json.loads((H/'parameters-v2.json').read_text());E=P['edge_revision'];sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,mesh_object,csg,check_mesh,tree_world,export,studio
sys.path.insert(0,str(H.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_ENGINE_FILTER_CAP');s.collection.children.link(source);construction=bpy.data.collections.new('ENGINE_FILTER_CAP_V2_RETAINED_CONSTRUCTION');s.collection.children.link(construction);guides=bpy.data.collections.new('ENGINE_FILTER_CAP_V2_IMMUTABLE_CASE_GUIDE');s.collection.children.link(guides);stage=bpy.data.collections.new('ENGINE_FILTER_CAP_V2_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
paint=material('Engine filter cap silver coating - estimated PBR',(.43,.45,.47),.20,.40);u,v=P['centre_local_uv_m'];back=P['rear_seat_w_working_m'];front=P['face_front_w_working_m'];rear=P['spigot_rear_w_working_m'];baseR=P['face_radius_working_m'];earR=P['fastening_ear_radius_working_m'];distance=P['fastening_ear_centre_radius_working_m'];blend=E['ear_union_C1_radial_blend_width_working_m'];angles=[math.radians(a) for a in P['fastening_angles_working_degrees']]
def smooth(t):t=min(1,max(0,t));return t*t*(3-2*t)
def radius(theta):
 radius=baseR
 for a in angles:
  dt=math.atan2(math.sin(theta-a),math.cos(theta-a));rad=earR*earR-distance*distance*math.sin(dt)**2
  if rad<0 or math.cos(dt)<0:continue
  other=distance*math.cos(dt)+math.sqrt(rad);h=max(blend-abs(radius-other),0)/blend;radius=max(radius,other)+.25*blend*h*h
 return radius
# Preserve previous angular pitch away from ears, refine the actual new tangent blends.
samples={round(math.tau*i/192,12) for i in range(192)}
for a in angles:
 for i in range(-96,97):samples.add(round((a+math.radians(i*.125))%math.tau,12))
samples=sorted(samples);outline=[];normals=[]
for a in samples:
 r=radius(a);dr=(radius(a+1e-6)-radius(a-1e-6))/2e-6;q=Vector((r*math.cos(a),r*math.sin(a)));t=Vector((dr*math.cos(a)-r*math.sin(a),dr*math.sin(a)+r*math.cos(a)));outline.append(q);normals.append(Vector((t.y,-t.x)).normalized())
N=len(outline);rf=E['front_section_true_radius_working_m'];rr,rw=E['rear_section_elliptic_radii_working_m'];K=E['section_arc_intervals'];profile=[]
# Offset outline is inward: the rounded lip does not inflate maximum envelope.
profile.append((back,None));profile.append((back,rr))
for i in range(1,K+1):
 a=math.pi*.5*i/K;profile.append((back+rw*(1-math.cos(a)),rr*(1-math.sin(a))))
profile.append((front-rf,0))
for i in range(1,K+1):
 a=math.pi*.5*i/K;profile.append((front-rf+rf*math.sin(a),rf*(1-math.cos(a))))
profile.append((front,None));verts=[];rings=[];faces=[]
for w,d in profile:
 if d is None:rings.append([len(verts)]*N);verts.append((u,v,w))
 else:
  points=[q-normal*d for q,normal in zip(outline,normals)]
  assert all(points[i].x*points[(i+1)%N].y-points[i].y*points[(i+1)%N].x>0 for i in range(N)),('Offset contour ceases to be star-shaped',d)
  rings.append(list(range(len(verts),len(verts)+N)));verts.extend((u+p.x,v+p.y,w) for p in points)
for j in range(len(rings)):
 if profile[j][1] is None and profile[(j+1)%len(rings)][1] is None:continue
 for i in range(N):
  k=(i+1)%N;f=list(dict.fromkeys([rings[j][i],rings[(j+1)%len(rings)][i],rings[(j+1)%len(rings)][k],rings[j][k]]))
  if len(f)>=3:faces.append(f)
base=mesh_object('Original continuous cap plate with rounded blended ears',verts,faces,construction,paint)
def revolve(name,section,cx=u,cy=v,n=192):
 vv=[];rr=[];ff=[]
 for w,r in section:
  if r==0:rr.append([len(vv)]*n);vv.append((cx,cy,w))
  else:rr.append(list(range(len(vv),len(vv)+n)));vv.extend((cx+r*math.cos(math.tau*i/n),cy+r*math.sin(math.tau*i/n),w) for i in range(n))
 for j in range(len(section)):
  if section[j][1]==0 and section[(j+1)%len(section)][1]==0:continue
  for i in range(n):
   k=(i+1)%n;f=list(dict.fromkeys([rr[j][i],rr[(j+1)%len(rr)][i],rr[(j+1)%len(rr)][k],rr[j][k]]))
   if len(f)>=3:ff.append(f)
 return mesh_object(name,vv,ff,construction,paint)
spigot=revolve('Original solid spigot blank before true rear bore',[(rear,0),(rear,.0275),(back+.001,.0275),(back+.001,0)])
ring=[(front-.0002,.027),(front-.0002,.0305),(front,.0305)]
for i in range(1,11):t=i/10;ring.append((front+.0004*smooth(t),.0305-.0005*t))
ring.append((front+.0004,.0275))
for i in range(1,11):t=i/10;ring.append((front+.0004*(1-smooth(t)),.0275-.0005*t))
raised=revolve('Original shallow annular face relief with tangent transitions',ring)
from mathutils.bvhtree import BVHTree
# Single cavity subtraction avoids coincident duplicate inner spigot surfaces.
from control_geometry import cylinder
cavity=cylinder('Rear cavity and true spigot bore cutter',(u,v,(front-.0028)-.05),.0253,.10,construction,axis=(0,0,1),n=192);drills=[cavity];mouth=E['front_bore_mouth_true_radius_working_m'];hole=P['ear_hole_radius_working_m']
for k,a in enumerate(angles):
 x=u+distance*math.cos(a);y=v+distance*math.sin(a);section=[(back-.02,0),(back-.02,hole),(front-mouth,hole)]
 for i in range(1,11):t=math.pi*.5*i/10;section.append((front-mouth+mouth*math.sin(t),hole+mouth*(1-math.cos(t))))
 section.extend([(front+.02,hole+mouth),(front+.02,0)]);drills.append(revolve('Original rounded front ear bore cutter '+str(k+1),section,x,y,n=96))
bpy.context.view_layer.update();cap,operations=csg(base,[spigot,raised],drills,source,paint,R,'RH oil filter cap - editable candidate');cleanup=clean_evaluated(cap,construction);cap.modifiers.clear();bpy.ops.object.select_all(action='DESELECT');cap.select_set(True);bpy.context.view_layer.objects.active=cap;bpy.ops.mesh.customdata_custom_splitnormals_clear();cap.data.update()
for p in cap.data.polygons:p.use_smooth=abs(p.normal.z)<.99999
checks=check_mesh(cap);datum=bpy.data.objects.new('RH oil filter cap provisional datum',None);source.objects.link(datum);x,y,z=P['parent_datum_world_m'];datum.matrix_world=Matrix(((0,0,-1,x),(-1,0,0,y),(0,1,0,z),(0,0,0,1)));cap.parent=datum
parent=H.parent/'engine-cover-right/engine-cover-right-v2.blend';parent_sha=hashlib.sha256(parent.read_bytes()).hexdigest();assert parent_sha=='2558ea2479a02caf14e9feddad3f953f5587269083ae7b125a177acd4621515a'
with bpy.data.libraries.load(str(parent),link=True) as (available,loaded):loaded.objects=['Engine RH cover provisional datum','RH clutch cover hollow casting - editable candidate']
for ob in loaded.objects:guides.objects.link(ob)
bpy.context.view_layer.update();case=bpy.data.objects['RH clutch cover hollow casting - editable candidate'];crossings=len(tree_world(case).overlap(tree_world(cap)));assert not crossings
mesh=cap.to_mesh();tree=BVHTree.FromPolygons([a.co for a in mesh.vertices],[tuple(f.vertices) for f in mesh.polygons]);cap.to_mesh_clear();hole_clear=[]
for a in angles:
 p=Vector((u+distance*math.cos(a),v+distance*math.sin(a),back-.01));hit=tree.ray_cast(p,Vector((0,0,1)),.04);hole_clear.append(hit[0] is None)
assert all(hole_clear);construction.hide_render=True;construction.hide_viewport=True;guides.hide_render=True;guides.hide_viewport=True;cap['all_dimensions_estimated']=True;cap['three_ears_current_RDC_certified']=False;cap['art_accepted']=False;export(H/'engine-filter-cap-v2-inspection.glb',[datum,cap]);points=[cap.matrix_world@Vector(p) for p in cap.bound_box];target=sum(points,Vector())/len(points);studio(s,stage,target);s.camera.data.clip_start=.001
for ob in stage.objects:
 if ob.type=='MESH':ob.location.z=min(p.z for p in points)-.002
 if ob.type=='LIGHT':ob.data.energy*=.08
sourcefile=H/'engine-filter-cap-v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(sourcefile),compress=True);j={'component_id':P['component_id'],'revision':'engine-filter-cap-v2','source_sha256':hashlib.sha256(sourcefile.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((H/'engine-filter-cap-v2-inspection.glb').read_bytes()).hexdigest(),'parent_source_sha256':parent_sha,'geometry':[checks],'cleanup':cleanup,'custom_normals_present':cap.data.has_custom_normals,'profile_outline_points':N,'ear_outline_C1_blended_before_plate_loft':True,'section_true_radii_built_before_CSG':True,'ear_bores_actually_ray_clear':hole_clear,'interface_case_surface_crossings':crossings,'cap_centre_local_uvw_m':[u,v,(front+rear)/2],'bounds_world_m':{'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]},'all_dimensions_estimated':True,'new_radii_measured':False,'three_ears_only_documented_related_variant':True,'art_accepted':False,'physical_iphone_tested':False};(O/'source-geometry-check.json').write_text(json.dumps(j,indent=2)+'\n');(H/'build-report-v2.json').write_text(json.dumps(j,indent=2)+'\n');print('WEWA_CAP_V2_PREFLIGHT',json.dumps(j))
