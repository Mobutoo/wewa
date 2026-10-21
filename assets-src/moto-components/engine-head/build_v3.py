"""Bare exterior UG5 conditional head, original casting from8real related views.
No broad standard cover, valves, camshaft, rockers, manufacturer labels or source pixels.
"""
from pathlib import Path
import bpy,json,math,sys,hashlib
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-head-v3';O.mkdir(parents=True,exist_ok=True);P=json.loads((H/'parameters-v3.json').read_text());sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,mesh_object,cylinder,box,csg,lathe,check_mesh,tree_world,studio,export
sys.path.insert(0,str(H));from topology_cleanup_head_v2 import clean_evaluated
sys.path.insert(0,str(H));import head_geometry_v3 as geo
from csg_driver_v2 import csg
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_ENGINE_HEAD');s.collection.children.link(source);construction=bpy.data.collections.new('HEAD_RETAINED_CONSTRUCTION');s.collection.children.link(construction);guides=bpy.data.collections.new('HEAD_IMMUTABLE_INTERFACE_GUIDES');s.collection.children.link(guides);stage=bpy.data.collections.new('HEAD_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
black=material('Head black coated casting - original unmeasured PBR',(.017,.020,.023),.03,.44);metal=material('Head unpainted mating planes - original unmeasured PBR',(.43,.45,.47),.95,.32);geo.configure(P,construction,black,mesh_object)
# Curved section main tower; real plateaus/columns/separate openings, no generic cuboid.
verts=[];faces=[];N=128;station=[Vector(a)for a in P['upper_tower_sections_z_rx_ry_m']];sections=[]
for k in range(len(station)-1):
 for sample in range(12):sections.append(geo.cat(station[max(0,k-1)],station[k],station[k+1],station[min(len(station)-1,k+2)],sample/12))
sections.append(station[-1])
for z,rx,ry in sections:
 for i in range(N):
  a=math.tau*i/N;c=math.cos(a);d=math.sin(a);verts.append((rx*math.copysign(abs(c)**.73,c),ry*math.copysign(abs(d)**.73,d),z))
for j in range(len(sections)-1):
 for i in range(N):k=(i+1)%N;faces.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
faces +=[tuple(reversed(range(N))),tuple(range((len(sections)-1)*N,len(sections)*N))];core=mesh_object('Original upper head tower sections',verts,faces,construction,black)
# Generic closed original profile extrusion with explicit rim sections, no global fillet.
def profile_solid(name,outline,levels,axis=(1,0,0),u=(0,1,0),v=(0,0,1),centre=(0,0,0),mat=black):
 outline=[Vector(p)for p in outline];n=len(outline);axis,u,v,centre=map(Vector,[axis,u,v,centre]);vertices=[];faces=[]
 for x,inset in levels:
  for i,p in enumerate(outline):
   tangent=(outline[(i+1)%n]-outline[(i-1)%n]).normalized();q=p+Vector((-tangent.y,tangent.x))*inset;vertices.append(centre+axis*x+u*q.x+v*q.y)
 for j in range(len(levels)-1):
  for i in range(n):k=(i+1)%n;faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
 faces +=[tuple(reversed(range(n))),tuple(range((len(levels)-1)*n,len(levels)*n))];return mesh_object(name,vertices,faces,construction,mat)
def ellipse(rx,ry,n=128):return[(rx*math.cos(math.tau*i/n),ry*math.sin(math.tau*i/n))for i in range(n)]
def ellipsoid(name,centre,scale):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=128,ring_count=64,radius=1,location=centre);o=bpy.context.object;o.name=name;o.scale=scale
 for c in list(o.users_collection):c.objects.unlink(o)
 construction.objects.link(o);return o
features=[]
# Rounded integral port roots connect observed underside wings to side gas flanges.
for index,point in enumerate(P['intake_exhaust_seat_centres_local_m']):
 x,y,z=point;features.append(ellipsoid('Rounded integral gasport casting root '+str(index),(x,y-math.copysign(.015,y),.026),(.026,.021,.021)))
for i,(z,factor)in enumerate(zip(P['fin_centres_z_m'],P['fin_reach_factors_working'])):features.append(geo.rounded_fin('Head curved cooling fin '+str(i+1),z,P['fin_thickness_working_m'],factor))
# Generic v1gasket plate deliberately omitted: new asymmetric underside replaces it.
for i,(x,y)in enumerate(P['stud_centres_xy_working_m']):
 z0,z1=P['stud_column_root_z_range_working_m'];rr=P['stud_column_root_radius_working_m'];ro=P['stud_column_radius_working_m'];profile=[(z0,0),(z0,rr)]
 for k in range(1,33):
  t=k/32;profile.append((z0+(z1-z0)*t,ro+(rr-ro)*(1-t)**2))
 profile.extend([(P['stud_column_top_z_working_m'],ro),(P['stud_column_top_z_working_m'],0)]);v=[];f=[];rings=[];nn=128
 for z,r in profile:
  if r==0:rings.append([len(v)]*nn);v.append((x,y,z))
  else:
   rings.append(list(range(len(v),len(v)+nn)));v.extend((x+r*math.cos(math.tau*k/nn),y+r*math.sin(math.tau*k/nn),z)for k in range(nn))
 for k in range(len(profile)):
  if profile[k][1]==0 and profile[(k+1)%len(profile)][1]==0:continue
  for a in range(nn):
   b=(a+1)%nn;face=list(dict.fromkeys([rings[k][a],rings[(k+1)%len(profile)][a],rings[(k+1)%len(profile)][b],rings[k][b]]))
   if len(face)>=3:f.append(face)
 features.append(mesh_object('Head flared integral stud column '+str(i+1),v,f,construction,black))
from housing_sections_v3 import build as build_housing_sections, add_visible_ribs
outer=geo.curve(P['side_OHC_outer_YZ_controls_m']);features.append(build_housing_sections(P,outer,construction,black,mesh_object));features.extend(add_visible_ribs(P,outer,construction,black,mesh_object))
# Upper high fork, two separate tabs truly joined to main head at their bases.
fork=geo.curve([[-.025,.103],[-.008,.141],[.008,.141],[.025,.103]],n=18)
for i,x in enumerate(P['upper_frame_fork_tab_centres_x_m']):
 t=P['upper_frame_fork_tab_thickness_m'];features.append(profile_solid('Upper frame fork tab '+str(i+1),fork,[(x-t/2,.0005),(x-t/2+.0006,0),(x+t/2-.0006,0),(x+t/2,.0005)]))
# Opposed elongated inspection seats and their two genuine fastener ears.
seat_frames=[]
for i,(point,axis)in enumerate(zip(P['tappet_port_centres_local_m'],P['tappet_port_axes_local'])):
 centre=Vector(point);axis=Vector(axis);u=Vector((1,0,0));v=Vector((0,0,1));depth=P['tappet_seat_depth_working_m'];rx,ry=P['tappet_oval_outer_radii_working_m'];features.append(profile_solid('Oblong tappet casting seat '+str(i+1),ellipse(rx,ry),[(-depth/2,.0007),(-depth/2+.001,0),(depth/2-.0007,0),(depth/2,.0007)],axis,u,v,centre));seat_frames.append((centre,axis,u,v))
 for k,(a,b)in enumerate(P['tappet_bolt_centres_seat_uv_working_m']):features.append(cylinder('Tappet seat cast ear '+str(i+1)+'-'+str(k+1),centre+u*a+v*b,.0067,depth,construction,black,axis=axis,n=96))
# The port flange contour follows a central aperture plus two diagonal lugs.
from mathutils.geometry import convex_hull_2d
flange_points=[Vector(p)for p in ellipse(.020,.020)];dx,dz=P['intake_exhaust_bolt_offset_XZ_working_m']
for sign in[-1,1]:flange_points +=[Vector((sign*dx+p[0],sign*dz+p[1]))for p in ellipse(.007,.007,64)]
flange=[flange_points[i]for i in convex_hull_2d(flange_points)]
for i,point in enumerate(P['intake_exhaust_seat_centres_local_m']):
 axis=Vector((0,-1 if i==0 else 1,0));features.append(profile_solid('Diagonal gas port cast flange '+str(i+1),flange,[(-.012,.0007),(-.011,0),(.006,0),(.007,.0007)],axis,(1,0,0),(0,0,1),point))
# Material voids. Internal spaces are simplified casting surfaces, no mechanism.
drills=[ellipsoid('Shallow lower chamber casting bowl',(0,0,-.002),(.028,.028,.010)),ellipsoid('Upper casting space simplification',(0,0,.078),(.035,.043,.027))]
for i,sign in enumerate([-1,1]):drills.append(cylinder('Visible valve port casting passage '+str(i+1),(0,sign*.016,.016),.0105,.054,construction,axis=(0,sign*.18,1),n=128))
for i,(x,y)in enumerate(P['stud_centres_xy_working_m']):
 if i==0:drills.append(cylinder('Fourth upper column access - lower connection unresolved',(x,y,.0775),P['stud_hole_radius_working_m'],.105,construction,axis=(0,0,1),n=96))
 else:drills.append(cylinder('Observed lower body bore candidate '+str(i+1),(x,y,.055),P['stud_hole_radius_working_m'],.15,construction,axis=(0,0,1),n=96))
inner=geo.curve(P['side_OHC_inner_YZ_controls_m']);drills.append(profile_solid('Actual large arched OHC opening',inner,[(.022,0),(.110,0)]))
for i,(y,z)in enumerate(P['side_OHC_bolt_YZ_working_m']):drills.append(cylinder('OHC cover mounting bore '+str(i+1),(P['side_OHC_x_outerface_m']-.007,y,z),P['side_OHC_bolt_radius_working_m'],.035,construction,axis=(1,0,0),n=96))
# Rectangular timing passage joins the conditional barrel passage, no chain fabricated.
# Old short timing box omitted: full visible mouth constructed by underside helper.
for i,(centre,axis,u,v)in enumerate(seat_frames):
 rx,ry=P['tappet_oval_inner_radii_working_m'];drills.append(profile_solid('Actual oblong tappet opening '+str(i+1),ellipse(rx,ry),[(-.045,0),(.035,0)],axis,u,v,centre))
 for k,(a,b)in enumerate(P['tappet_bolt_centres_seat_uv_working_m']):drills.append(cylinder('Actual tappet ear bolt bore '+str(i+1)+'-'+str(k+1),centre+u*a+v*b,P['tappet_bolt_radius_working_m'],.060,construction,axis=axis,n=96))
y,z=P['upper_frame_fork_hole_centre_YZ_m'];drills.append(cylinder('Actual shared upper fork mounting bore',(0,y,z),P['upper_frame_fork_hole_radius_m'],.060,construction,axis=(1,0,0),n=128))
for i,point in enumerate(P['intake_exhaust_seat_centres_local_m']):
 centre=Vector(point);axis=Vector((0,-1 if i==0 else 1,0));drills.append(cylinder('Actual gas port opening '+str(i+1),centre-axis*.025,P['intake_exhaust_port_radius_working_m'],.090,construction,axis=axis,n=128))
 for sign in[-1,1]:drills.append(cylinder('Gas port diagonal mounting bore '+str(i+1)+'-'+str(sign),centre+Vector((sign*dx,0,sign*dz)),P['port_stud_radius_working_m'],.060,construction,axis=axis,n=96))
# Opposite side deep plug well interrupts middle fins, lowest fin preserved.
drills.append(box('Actual recessed spark plug well',P['spark_plug_recess_centre_working_m'],P['spark_plug_recess_size_working_m'],construction,bevel=.003));spark_axis=Vector((-1,0,.35)).normalized();drills.append(cylinder('Actual angled spark plug casting bore',P['spark_plug_seat_centre_working_m'],.0055,.095,construction,axis=spark_axis,n=128))
# Complete visible underside before expensive final views.
from underside_geometry_v2 import build as build_underside
under_features,under_drills=build_underside(P,geo,profile_solid,cylinder,box,lathe,construction,black);features.extend(under_features);drills.extend(under_drills)
body,ops=csg(core,features,drills,source,black,R,'Engine UG5 head hollow exterior casting - editable candidate');cleanup=clean_evaluated(body,construction);body.modifiers.clear();bpy.context.view_layer.objects.active=body;body.select_set(True);bpy.ops.mesh.customdata_custom_splitnormals_clear();check=check_mesh(body)
# Visible integral bearing bed/side webs are casting, not a camshaft or bearing part.
first_cleanup=cleanup;body.name='Head retained casting before visible bearing bed';source.objects.unlink(body);construction.objects.link(body)
bx,by,bz=P['casting_bearing_bed_centre_working_m'];ro=P['casting_bearing_bed_outer_radius_working_m'];ri=P['casting_bearing_bed_inner_radius_working_m'];half=P['casting_bearing_bed_axial_depth_working_m']/2
bed=lathe('Visible integral camshaft bearing bed',[(bx-half,ri),(bx-half,ro-.0005),(bx-half+.0005,ro),(bx+half-.0005,ro),(bx+half,ro-.0005),(bx+half,ri)],construction,black,n=192);bed.location.z=bz
rib_inner=ri+.001;rib_outer=.052
webs=[cylinder('Interior bearing web '+str(sign),(bx,sign*(rib_inner+rib_outer)/2,bz),.005,rib_outer-rib_inner,construction,black,axis=(0,1,0),n=96)for sign in[-1,1]]
body,bedops=csg(body,[bed]+webs,[],source,black,R,'Engine UG5 head hollow exterior casting - editable candidate');cleanup=clean_evaluated(body,construction);body.modifiers.clear();bpy.context.view_layer.objects.active=body;body.select_set(True);bpy.ops.mesh.customdata_custom_splitnormals_clear();check=check_mesh(body)
# Machined planes stay material boundaries, never displaced/retouched export buffers.
body.data.materials.append(metal);bare_faces=0
for f in body.data.polygons:
 c=f.center
 plane=(abs(c.z)<2e-7 and f.normal.z<-.999)or(abs(c.x-P['side_OHC_x_outerface_m'])<2e-7 and f.normal.x>.999)or(abs(c.z-P['stud_column_top_z_working_m'])<2e-7 and f.normal.z>.999)
 seat=any(abs(c.y-(point[1]+axis[1]*P['tappet_seat_depth_working_m']/2))<2e-7 and f.normal.dot(Vector(axis))>.999 for point,axis in zip(P['tappet_port_centres_local_m'],P['tappet_port_axes_local']))
 gas=abs(abs(c.y)-.090)<2e-7 and abs(f.normal.y)>.999
 q=Vector((c.x/.035,c.y/.043,(c.z-.078)/.027));inner=.95<q.length_squared<1.05 and f.normal.dot(Vector((c.x,c.y,c.z-.078)).normalized())<-.7
 bearing=.010<c.x<.024 and math.hypot(c.y,c.z-.078)<.020
 if plane or seat or gas or inner or bearing:f.material_index=1;bare_faces+=1
# Immutable candidate barrel, shared rest datum plus estimated gasket gap.
p=H.parent/'engine-cylinder/engine-cylinder-v1.blend';barrel_sha=hashlib.sha256(p.read_bytes()).hexdigest();assert barrel_sha=='d78696eb6af8fb23a4917237aa75cfce3389d4759348984a9924fc4845be08c6'
with bpy.data.libraries.load(str(p),link=True)as(a,b):b.objects=['Engine cylinder base provisional datum','Engine cylinder finned hollow casting - editable candidate']
for o in b.objects:guides.objects.link(o)
bpy.context.view_layer.update();barrel=bpy.data.objects['Engine cylinder finned hollow casting - editable candidate'];base=bpy.data.objects['Engine cylinder base provisional datum'];datum=bpy.data.objects.new('Engine head base provisional datum',None);source.objects.link(datum);datum.matrix_world=base.matrix_world@Matrix.Translation((0,0,.073+P['gasket_gap_working_m']));body.parent=datum;bpy.context.view_layer.update();crossings=len(tree_world(body).overlap(tree_world(barrel)));assert not crossings,crossings
interface_rows=[];interface_sources=[]
for key,path,collection in [('visit',H.parent/'engine-tappet-cap/engine-tappet-cap-v1.blend','WEWA_ENGINE_TAPPET_CAP'),('OHC',H.parent/'engine-ohc-cover/engine-ohc-cover-v1.blend','WEWA_ENGINE_OHC_COVER_BODY')]:
 before=hashlib.sha256(path.read_bytes()).hexdigest()
 with bpy.data.libraries.load(str(path),link=True)as(available,loaded):loaded.collections=[collection]
 linked=loaded.collections[0];guides.children.link(linked);bpy.context.view_layer.update();bodytree=tree_world(body)
 for obj in list(linked.all_objects):
  if obj.type=='MESH':interface_rows.append({'group':key,'object':obj.name,'surface_triangle_pairs':len(bodytree.overlap(tree_world(obj))),'world_matrix':[list(row)for row in obj.matrix_world]})
 assert hashlib.sha256(path.read_bytes()).hexdigest()==before;interface_sources.append({'group':key,'source_path':str(path.relative_to(R)),'sha256':before,'matrices_preserved':True,'source_modified':False})
construction.hide_render=True;construction.hide_viewport=True;guides.hide_render=True;guides.hide_viewport=True;export(H/'engine-head-v3-inspection.glb',[datum,body]);points=[body.matrix_world@Vector(p)for p in body.bound_box];target=sum(points,Vector())/len(points);studio(s,stage,target);s.camera.data.clip_start=.001
for o in stage.objects:
 if o.type=='MESH':o.location.z=min(p.z for p in points)-.002
 if o.type=='LIGHT':o.data.energy*=.08
body['all_dimensions_estimated']=True;body['art_accepted']=False;bpy.ops.wm.save_as_mainfile(filepath=str(H/'engine-head-v3.blend'),compress=True)
r={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':hashlib.sha256((H/'engine-head-v3.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((H/'engine-head-v3-inspection.glb').read_bytes()).hexdigest(),'fixed_cap_interface_checks':interface_rows,'immutable_cap_sources':interface_sources,'collection':source.name,'parent_datum':datum.name,'datum_world_matrix':[list(v)for v in datum.matrix_world],'geometry':[check],'cleanup':[first_cleanup,cleanup],'unpainted_interface_face_count':bare_faces,'barrel_source_sha256':barrel_sha,'candidate_barrel_surface_crossings':crossings,'bounds_world_m':{'min':[min(p[i]for p in points)for i in range(3)],'max':[max(p[i]for p in points)for i in range(3)]},'all_dimensions_estimated':True,'current_RDC_identity_certified':False,'internal_mechanisms_manufactured':False,'art_accepted':False};(H/'build-report-v3.json').write_text(json.dumps(r,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');print('UG5_HEAD_PREFLIGHT',json.dumps(r))
