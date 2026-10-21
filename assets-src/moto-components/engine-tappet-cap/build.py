"""Original two-ear oblong tappet cap with rounded section loft, qty2 instances.
All scale/back sections estimated; related52JV0144 photos precede geometry.
"""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,sys
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-tappet-cap-v1';O.mkdir(exist_ok=True);P=json.loads((H/'parameters.json').read_text());sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,mesh_object,csg,check_mesh,tree_world,export,studio
sys.path.insert(0,str(H.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parent=R/P['parent_source'];assert sha(parent)==P['parent_source_sha256'];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_ENGINE_TAPPET_CAP');s.collection.children.link(source);construction=bpy.data.collections.new('TAPPET_CAP_RETAINED_CONSTRUCTION');s.collection.children.link(construction);guides=bpy.data.collections.new('TAPPET_CAP_IMMUTABLE_HEAD_GUIDE');s.collection.children.link(guides);stage=bpy.data.collections.new('TAPPET_CAP_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
paint=material('Original clean dark engine cap coating - conditional RDC estimate',(.012,.014,.016),.12,.39);N=512;angles=[math.tau*i/N for i in range(N)];ru,rv=P['plate_oval_radii_uv_working_m'];earR=P['ear_radius_working_m'];blend=P['ear_outline_blend_working_m']
def oval(a,rx,ry):return 1/math.sqrt((math.cos(a)/rx)**2+(math.sin(a)/ry)**2)
def outer(a):
 r=oval(a,ru,rv)
 for c in P['ear_centres_u_working_m']:
  d=earR**2-c*c*math.sin(a)**2
  if d<=0:continue
  other=c*math.cos(a)+math.sqrt(d)
  if other<=0:continue
  h=max(blend-abs(r-other),0)/blend;r=max(r,other)+.25*blend*h*h
 return r
def pad(a):
 x,y=P['raised_pad_radii_uv_working_m'];n=P['raised_pad_superellipse_exponent_working'];return (abs(math.cos(a)/x)**n+abs(math.sin(a)/y)**n)**(-1/n)
# Curvature is built in section before booleans; no global bevel on thin shell.
th=P['plate_thickness_working_m'];ed=P['plate_edge_round_working_m'];sh=P['raised_pad_shoulder_radial_blend_working_m'];top=P['raised_pad_total_height_from_back_working_m'];tr=P['raised_pad_top_round_working_m'];profiles=[]
profiles.append((0,lambda a:outer(a)-ed))
for i in range(1,13):
 a=math.pi*.5*i/12;profiles.append((ed*(1-math.cos(a)),lambda t,a=a:outer(t)-ed*(1-math.sin(a))))
profiles.append((th-ed,outer))
for i in range(1,13):
 a=math.pi*.5*i/12;profiles.append((th-ed+ed*math.sin(a),lambda t,a=a:outer(t)-ed*(1-math.cos(a))))
profiles.append((th,lambda a:pad(a)+sh))
for i in range(1,17):
 a=math.pi*.5*i/16;profiles.append((th+sh*(1-math.cos(a)),lambda t,a=a:pad(t)+sh*(1-math.sin(a))))
profiles.append((top-tr,pad))
for i in range(1,17):
 a=math.pi*.5*i/16;profiles.append((top-tr+tr*math.sin(a),lambda t,a=a:pad(t)-tr*(1-math.cos(a))))
verts=[];rings=[];faces=[]
for w,fun in profiles:
 rings.append(list(range(len(verts),len(verts)+N)));verts.extend((fun(a)*math.cos(a),fun(a)*math.sin(a),w)for a in angles)
for j in range(len(rings)-1):
 for i in range(N):k=(i+1)%N;faces.append((rings[j][i],rings[j][k],rings[j+1][k],rings[j+1][i]))
for j in [0,len(rings)-1]:
 centre=len(verts);verts.append((0,0,profiles[j][0]))
 for i in range(N):k=(i+1)%N;faces.append((centre,rings[j][k],rings[j][i])if j==0 else(centre,rings[j][i],rings[j][k]))
base=mesh_object('Original oblong cap with rounded central pad and opposed ears',verts,faces,construction,paint)
def cutter_loft(name,ringspec,cx=0,n=128):
 vv=[];ff=[];rr=[]
 for w,rx,ry in ringspec:
  rr.append(list(range(len(vv),len(vv)+n)));vv.extend((cx+rx*math.cos(math.tau*i/n),ry*math.sin(math.tau*i/n),w)for i in range(n))
 for j in range(len(rr)-1):
  for i in range(n):k=(i+1)%n;ff.append((rr[j][i],rr[j][k],rr[j+1][k],rr[j+1][i]))
 for j in [0,len(rr)-1]:
  centre=len(vv);vv.append((cx,0,ringspec[j][0]))
  for i in range(n):k=(i+1)%n;ff.append((centre,rr[j][k],rr[j][i])if j==0 else(centre,rr[j][i],rr[j][k]))
 return mesh_object(name,vv,ff,construction,paint)
# Invisible underside is intentionally a bounded simplification, not certified casting/O-ring.
cavity=cutter_loft('Estimated blind rear cap cavity', [(-.01,.0125,.021),(.001,.0125,.021),(.006,.0105,.0165),(.0075,.0105,.0165)],n=192);cuts=[cavity];hole=P['ear_bore_radius_working_m'];mouth=.0003
for i,c in enumerate(P['ear_centres_u_working_m']):
 sec=[(-.01,hole,hole),(th-mouth,hole,hole)]
 for k in range(1,13):a=math.pi*.5*k/12;rad=hole+mouth*(1-math.cos(a));sec.append((th-mouth+mouth*math.sin(a),rad,rad))
 sec.append((.02,hole+mouth,hole+mouth));cuts.append(cutter_loft('Rounded actual ear bore cutter '+str(i+1),sec,cx=c))
bpy.context.view_layer.update();cap,ops=csg(base,[],cuts,source,paint,R,'UG5 tappet cap FRONT - editable conditional candidate');cleanup=clean_evaluated(cap,construction);cap.modifiers.clear();bpy.ops.object.select_all(action='DESELECT');cap.select_set(True);bpy.context.view_layer.objects.active=cap;bpy.ops.mesh.customdata_custom_splitnormals_clear();cap.data.update()
for f in cap.data.polygons:f.use_smooth=abs(f.normal.z)<.99999
# A flat blind floor meeting an anisotropic cone must not switch hard/smooth
# solely because its face angle crosses a generic threshold around the ellipse.
bm=bmesh.new();bm.from_mesh(cap.data)
for e in bm.edges:
 if len(e.link_faces)==2:
  f,g=e.link_faces;flatf=abs(f.normal.z)>.99999;flatg=abs(g.normal.z)>.99999
  if flatf!=flatg:e.smooth=False
bm.to_mesh(cap.data);bm.free();cap.data.update()
geometry=check_mesh(cap);localtree=BVHTree.FromPolygons([v.co for v in cap.data.vertices],[tuple(f.vertices)for f in cap.data.polygons]);rays=[]
for c in P['ear_centres_u_working_m']:
 hit=localtree.ray_cast(Vector((c,0,-.005)),Vector((0,0,1)),.03);rays.append(hit[0]is None)
assert all(rays)
with bpy.data.libraries.load(str(parent),link=True)as(available,loaded):loaded.objects=['Engine head base provisional datum','Engine UG5 head hollow exterior casting - editable candidate']
for obj in loaded.objects:guides.objects.link(obj)
bpy.context.view_layer.update();head=bpy.data.objects['Engine UG5 head hollow exterior casting - editable candidate'];datum=bpy.data.objects.new('Tappet caps inherited estimated head datum',None);source.objects.link(datum);datum.matrix_world=bpy.data.objects['Engine head base provisional datum'].matrix_world.copy();gap=P['mount_gap_working_m']+P['parent_seat_depth_working_m']/2;cap.parent=datum;cap.matrix_basis=Matrix(((1,0,0,0),(0,0,-1,-.055-gap),(0,1,0,.078),(0,0,0,1)));rear=cap.copy();rear.data=cap.data;rear.name='UG5 tappet cap REAR - same conditional type';source.objects.link(rear);rear.matrix_basis=Matrix(((-1,0,0,0),(0,0,1,.055+gap),(0,1,0,.078),(0,0,0,1)));bpy.context.view_layer.update();interfaces=[]
for obj in [cap,rear]:
 cross=len(tree_world(head).overlap(tree_world(obj)));interfaces.append({'object':obj.name,'head_surface_crossings':cross,'world_matrix':[list(row)for row in obj.matrix_world]});
 if cross:
  # Localize actual rejected crossing triangles before choosing any geometry change.
  headmesh=head.to_mesh();capmesh=obj.to_mesh();ht=tree_world(head);ct=tree_world(obj);pairs=ht.overlap(ct);headinv=datum.matrix_world.inverted();hpoints=[headinv@(head.matrix_world@headmesh.vertices[i].co)for a,b in pairs for i in headmesh.polygons[a].vertices];cpoints=[obj.matrix_world.inverted()@(obj.matrix_world@capmesh.vertices[i].co)for a,b in pairs for i in capmesh.polygons[b].vertices];loc={'pairs':len(pairs),'headlocal_bounds':{'min':[min(v[i]for v in hpoints)for i in range(3)],'max':[max(v[i]for v in hpoints)for i in range(3)]},'caplocal_bounds':{'min':[min(v[i]for v in cpoints)for i in range(3)],'max':[max(v[i]for v in cpoints)for i in range(3)]}};head.to_mesh_clear();obj.to_mesh_clear();(O/('blocked-interface-'+('front'if obj==cap else'rear')+'.json')).write_text(json.dumps(loc,indent=2)+'\n');interfaces[-1]['fit_status']='blocked_actual_candidate_surface_crossings';interfaces[-1]['localization']=loc

construction.hide_render=True;construction.hide_viewport=True;guides.hide_render=True;guides.hide_viewport=True
for obj in [cap,rear]:obj['all_dimensions_estimated']=True;obj['exact_RDC_identity_certified']=False;obj['back_geometry_simplified']=True;obj['art_accepted']=False
export(H/'engine-tappet-cap-inspection.glb',[datum,cap,rear]);points=[obj.matrix_world@Vector(v)for obj in [cap,rear]for v in obj.bound_box];target=sum(points,Vector())/len(points);studio(s,stage,target);s.camera.data.clip_start=.001
for obj in stage.objects:
 if obj.type=='MESH':obj.location.z=min(v.z for v in points)-.002
 if obj.type=='LIGHT':obj.data.energy*=.08
file=H/'engine-tappet-cap-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True);assert sha(parent)==P['parent_source_sha256'];report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(file),'export_sha256':sha(H/'engine-tappet-cap-inspection.glb'),'parent_source_sha256':sha(parent),'master_geometry':geometry,'type_quantity':2,'shared_mesh_data':cap.data==rear.data,'cleanup':cleanup,'ear_bores_actually_ray_clear':rays,'interfaces':interfaces,'blind_back_cavity_not_measured':True,'source_custom_normals':cap.data.has_custom_normals,'all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False};(H/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('TAPPET_CAP_PREFLIGHT',json.dumps(report))
