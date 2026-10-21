"""Original external folding kick: shape from currentRDC plus related photos.
Internal engine shaft/ratchet deliberately not fabricated. All lengths estimated.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/kickstarter-v1';OUT.mkdir(exist_ok=True);P=json.loads((HERE/'parameters.json').read_text());sys.path.insert(0,str(HERE.parent/'throttle-control'));from control_geometry import material,mesh_object,cylinder,box,csg,check_mesh,tree_world,studio,export
sys.path.insert(0,str(HERE.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_KICKSTARTER');scene.collection.children.link(source);construction=bpy.data.collections.new('KICK_RETAINED_CONSTRUCTION');scene.collection.children.link(construction);guides=bpy.data.collections.new('KICK_IMMUTABLE_INTERFACE_GUIDES');scene.collection.children.link(guides);stage=bpy.data.collections.new('KICK_STUDIO_NOT_EXPORTED');scene.collection.children.link(stage)
chrome=material('Kick chromed forged steel - unmeasured PBR',(.64,.67,.70),1,.19);rubber=material('Kick ribbed black rubber - unmeasured PBR',(.009,.0105,.012),0,.68);zinc=material('Kick zinc fasteners - estimated PBR',(.38,.40,.43),1,.31)
cleanup=[]
def finish(o):
 cleanup.append(clean_evaluated(o,construction));o.modifiers.clear();bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.mesh.customdata_custom_splitnormals_clear();o.data.update();return o
# Closed section revolutions with true poles: no coincident pole rings.
def revolve(name,section,axis,centre,mat,n=128,col=None):
 col=col or construction;axis=Vector(axis).normalized();a=axis.orthogonal().normalized();b=axis.cross(a);centre=Vector(centre);verts=[];rings=[];faces=[]
 for x,r in section:
  if r==0:rings.append([len(verts)]*n);verts.append(centre+axis*x)
  else:rings.append(list(range(len(verts),len(verts)+n)));verts.extend(centre+axis*x+(a*math.cos(math.tau*i/n)+b*math.sin(math.tau*i/n))*r for i in range(n))
 for j in range(len(section)):
  if section[j][1]==0 and section[(j+1)%len(section)][1]==0:continue
  for i in range(n):
   k=(i+1)%n;f=list(dict.fromkeys([rings[j][i],rings[(j+1)%len(section)][i],rings[(j+1)%len(section)][k],rings[j][k]]))
   if len(f)>=3:faces.append(f)
 return mesh_object(name,verts,faces,col,mat)
def collar(name,v0,v1,r,mat=chrome):
 q=Vector(P['fold_axis_local_point_m']);q.y=0
 return revolve(name,[(v0,.0035),(v0,r-.0005),(v0+.0005,r),(v1-.0005,r),(v1,r-.0005),(v1,.0035)],(0,1,0),q,mat)
# Rounded clamp with a real splined candidate bore and open pinch slit.
base=box('Original rounded split hub blank',(0,0,.004),P['clamp_size_u_v_w_working_m'],construction,chrome,bevel=.0045)
verts=[];n=224
for w in [-.06,.06]:
 for i in range(n):
  a=math.tau*i/n;r=P['clamp_shaft_bore_radius_working_m']+P['cosmetic_bore_spline_depth_working_m']*.5*(1+math.cos(P['cosmetic_bore_spline_count_working']*a));verts.append((r*math.cos(a),r*math.sin(a),w))
faces=[]
for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
faces += [tuple(reversed(range(n))),tuple(range(n,2*n))];bore=mesh_object('Estimated shaft bore and cosmetic spline cutter',verts,faces,construction)
slit=box('Visible pinch slit cutter',(0,-.016,.004),(.0013,.034,.10),construction,bevel=0);bolt_hole=cylinder('Pinch bolt true bore cutter',(0,-.0125,.004),.0032,.09,construction,axis=(1,0,0),n=96)
hq=P['fold_axis_local_point_m'];hinge_cut=cylinder('True fixed clevis pin bore through connecting webs',(hq[0],hq[1],hq[2]),.0037,.10,construction,axis=(0,1,0),n=96)
fixed,ops=csg(base,[collar('Lower fixed folding clevis',-.005,-.001,.013),collar('Upper fixed folding clevis',.015,.019,.013),box('Lower estimated clevis connecting web',(-.001,-.003,.025),(.012,.004,.028),construction,chrome,bevel=.0008),box('Upper estimated clevis connecting web',(-.001,.017,.025),(.012,.004,.028),construction,chrome,bevel=.0008)],[bore,slit,bolt_hole,hinge_cut],source,chrome,ROOT,'Kick split mounting clamp and clevis - fixed candidate');finish(fixed)
# Continuous variable-section forged arm, not a chain of separate cylinders.
controls=[Vector(p[:3]) for p in P['arm_sections_u_v_w_halfwidth_halfdepth_m']];radii=[p[3:] for p in P['arm_sections_u_v_w_halfwidth_halfdepth_m']]
def cat(p0,p1,p2,p3,t):return .5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
centres=[];sizes=[]
for k in range(len(controls)-1):
 for i in range(12):
  t=i/12;centres.append(cat(controls[max(0,k-1)],controls[k],controls[k+1],controls[min(len(controls)-1,k+2)],t));sizes.append([(1-t)*radii[k][j]+t*radii[k+1][j] for j in [0,1]])
centres.append(controls[-1]);sizes.append(radii[-1]);verts=[];faces=[];N=48
for k,(point,rad) in enumerate(zip(centres,sizes)):
 tangent=(centres[min(k+1,len(centres)-1)]-centres[max(0,k-1)]).normalized();normal=Vector((0,0,1));normal=(normal-tangent*tangent.dot(normal)).normalized();side=normal.cross(tangent).normalized()
 # Rounded rectangular forging section gradually becomes circular at pedal end.
 exponent=1 if point.x>.050 and point.y>.269 else 2/3
 for i in range(N):
  a=math.tau*i/N;c=math.cos(a);s=math.sin(a);c=math.copysign(abs(c)**exponent,c);s=math.copysign(abs(s)**exponent,s);verts.append(point+side*c*rad[0]+normal*s*rad[1])
for k in range(len(centres)-1):
 for i in range(N):j=(i+1)%N;faces.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
faces.extend([tuple(reversed(range(N))),tuple(range((len(centres)-1)*N,len(centres)*N))]);forging=mesh_object('Original continuous forged arm sweep',verts,faces,construction,chrome)
q=Vector(P['fold_axis_local_point_m']);eye=revolve('Moving base hinge eye original',[(0,.0036),(0,.0085),(.0005,.009),(.0135,.009),(.014,.0085),(.014,.0036)],(0,1,0),(q.x,0,q.z),chrome)
cut=cylinder('Actual folding eye bore',(q.x,.007,q.z),.0036,.07,construction,axis=(0,1,0),n=96);arm,armops=csg(forging,[eye],[cut],source,chrome,ROOT,'Kick forged arm and base hinge eye - moving candidate');finish(arm)
# Closed ribbed rubber tube, original working eleven rounded rings.
start=P['rubber_start_u_m'];length=P['rubber_length_working_m'];ri=P['rubber_inner_radius_working_m'];ro=P['rubber_outer_radius_working_m'];section=[(start,ri),(start,ro-.001),(start+.001,ro)]
for i in range(1,11*12):
 x=start+.001+(length-.002)*i/(11*12);t=i/12;profile=.5+.5*math.cos(math.tau*t);r=ro-.0009*profile;section.append((x,r))
section.extend([(start+length-.001,ro),(start+length,ro-.001),(start+length,ri)]);boot=revolve('Kick ribbed pedal rubber - fixed to arm',section,(1,0,0),(0,*P['pedal_centre_v_w_working_m']),rubber,col=source,n=128);finish(boot)
endcap=revolve('Kick closed chrome pedal end',[(.1224,.0056),(.1224,.0085),(.123,.0091),(.1252,.0091),(.1258,.0085),(.126,0),(.1242,0),(.1242,.0056)],(1,0,0),(0,*P['pedal_centre_v_w_working_m']),chrome,col=source,n=96);finish(endcap)
# Separate hardware, actual bores left open, no pretending to exact threads.
shaft=cylinder('Kick original round pinch shaft',(0,-.0125,.004),.0029,.047,construction,zinc,axis=(1,0,0),n=96);head=cylinder('Kick original hex pinch head',(-.0193,-.0125,.004),.00577,.004,construction,zinc,axis=(1,0,0),n=6);hb=head.modifiers.new('Original hex head edge chamfer before CSG','BEVEL');hb.width=.00035;hb.segments=3;bolt,bolt_ops=csg(shaft,[head],[],source,zinc,ROOT,'Kick clamp pinch bolt - estimated unthreaded');finish(bolt)
nut_blank=cylinder('Original hex nut blank',(.0201,-.0125,.004),.00577,.0054,construction,zinc,axis=(1,0,0),n=6);nb=nut_blank.modifiers.new('Original nut edge chamfer before CSG','BEVEL');nb.width=.0004;nb.segments=3;nut_bore=cylinder('Actual circular nut bore',(.0201,-.0125,.004),.0034,.03,construction,axis=(1,0,0),n=96);nut,nut_ops=csg(nut_blank,[],[nut_bore],source,zinc,ROOT,'Kick clamp pinch nut - estimated cosmetic');finish(nut)
for obj in [bolt,nut]:
 for polygon in obj.data.polygons:
  c=polygon.center;rad=math.hypot(c.y+.0125,c.z-.004)
  if abs(polygon.normal.x)>.999 or(rad>.0046 and abs(polygon.normal.x)<.001):polygon.use_smooth=False

pin=revolve('Kick vertical folding pivot pin - estimated',[( -.006,0),(-.006,.0048),(-.0055,.0048),(-.005,.0032),(.0195,.0032),(.020,.0048),(.022,.0048),(.0225,0)],(0,1,0),(q.x,0,q.z),zinc,col=source,n=96);finish(pin)
# Parenting preserves the source construction coordinates at rest.
x,y,z=P['datum_world_m'];datum=bpy.data.objects.new('Kick engine shaft provisional datum',None);source.objects.link(datum);datum.matrix_world=Matrix(((0,0,-1,x),(-1,0,0,y),(0,1,0,z),(0,0,0,1)))
fold=bpy.data.objects.new('Kick base folding pivot - inspection range estimated',None);source.objects.link(fold);fold.parent=datum;fold.location=q
for o in [fixed,bolt,nut,pin]:o.parent=datum
for o in [arm,boot,endcap]:o.parent=fold;o.location=-q
hardware=[fixed,arm,boot,endcap,bolt,nut,pin];checks=[check_mesh(o) for o in hardware]
# True world source guides remain immutable and hidden locally.
parent=HERE.parent/'engine-cover-right/engine-cover-right-v1.blend';parent_sha=hashlib.sha256(parent.read_bytes()).hexdigest();assert parent_sha=='185274d117291007e185fba8209abac91153ece3ae9e4a0a8ce5a67667c4331f'
with bpy.data.libraries.load(str(parent),link=True) as (available,loaded):loaded.objects=['Engine RH cover provisional datum','RH clutch cover hollow casting - editable candidate']
for o in loaded.objects:guides.objects.link(o)
bpy.context.view_layer.update();cover=bpy.data.objects['RH clutch cover hollow casting - editable candidate'];poses=[]
cover_tree=tree_world(cover);static_trees={o.name:tree_world(o) for o in hardware};static_trees[cover.name]=cover_tree;static_crossings=[]
for i,a in enumerate(hardware):
 for b in hardware[i+1:]+[cover]:
  hits=len(static_trees[a.name].overlap(static_trees[b.name]))
  if hits:static_crossings.append({'a':a.name,'b':b.name,'surface_crossings':hits})
for stroke in [0,30,60]:
 datum.rotation_mode='QUATERNION';datum.rotation_quaternion=datum.matrix_world.to_quaternion() if stroke==0 else initial_rotation
 if stroke==0:initial_rotation=datum.rotation_quaternion.copy()
 from mathutils import Quaternion
 datum.rotation_quaternion=initial_rotation@Quaternion((0,0,1),math.radians(stroke))
 bpy.context.view_layer.update();fixed_trees={o.name:tree_world(o) for o in [fixed,pin]};fixed_trees[cover.name]=cover_tree
 for angle in range(0,91,5):
  fold.rotation_euler.y=-math.radians(angle);bpy.context.view_layer.update();pairs=[]
  for a in [arm,boot,endcap]:
   moving_tree=tree_world(a)
   for b in [fixed,pin,cover]:
    hits=len(moving_tree.overlap(fixed_trees[b.name]))
    if hits:pairs.append({'a':a.name,'b':b.name,'surface_crossings':hits})
  poses.append({'stroke_deg':stroke,'fold_deg':angle,'crossings':pairs})
datum.rotation_quaternion=initial_rotation;fold.rotation_euler.y=0;bpy.context.view_layer.update()
sample=max(boot.data.vertices,key=lambda v:v.co.x);rest_point=boot.matrix_world@sample.co;fold.rotation_euler.y=-math.radians(90);bpy.context.view_layer.update();open_point=boot.matrix_world@sample.co;datum.rotation_quaternion=initial_rotation@Quaternion((0,0,1),math.radians(60));bpy.context.view_layer.update();stroked_point=boot.matrix_world@sample.co;datum.rotation_quaternion=initial_rotation;fold.rotation_euler.y=0;bpy.context.view_layer.update();actual_direction_probe={'actual_vertex_index':sample.index,'rest_world_m':list(rest_point),'fold90_world_m':list(open_point),'fold90_delta_world_m':list(open_point-rest_point),'stroke60_world_m':list(stroked_point),'stroke60_delta_world_m':list(stroked_point-open_point),'expected_fold_outward_negativeX':open_point.x<rest_point.x,'expected_stroke_down_and_back':stroked_point.z<open_point.z and stroked_point.y>open_point.y};assert actual_direction_probe['expected_fold_outward_negativeX'] and actual_direction_probe['expected_stroke_down_and_back']
construction.hide_render=True;construction.hide_viewport=True;guides.hide_render=True;guides.hide_viewport=True
assert not static_crossings,static_crossings
assert not any(p['crossings'] for p in poses),[p for p in poses if p['crossings']]
export(HERE/'kickstarter-inspection.glb',[datum,fold]+hardware);points=[o.matrix_world@Vector(p) for o in hardware for p in o.bound_box];target=sum(points,Vector())/len(points);studio(scene,stage,target);scene.camera.data.clip_start=.001
for o in stage.objects:
 if o.type=='MESH':o.location.z=min(p.z for p in points)-.002
 if o.type=='LIGHT':o.data.energy*=.08
for o in hardware:o['all_dimensions_estimated']=True;o['art_accepted']=False
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'kickstarter-v1.blend'),compress=True)
report={'component_id':P['component_id'],'source_sha256':hashlib.sha256((HERE/'kickstarter-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'kickstarter-inspection.glb').read_bytes()).hexdigest(),'collection':source.name,'parent_datum':datum.name,'fold_parent':fold.name,'geometry':checks,'cleanup':cleanup,'fold_axis_parent_local':list(q),'fold_direction_local':[0,-1,0],'actual_direction_probe':actual_direction_probe,'stroke_axis_local':[0,0,1],'rest_all_hardware_and_cover_surface_crossings':static_crossings,'pose_surface_tests':poses,'related_cover_source_sha256':parent_sha,'bounds_world_m':{'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]},'all_dimensions_estimated':True,'kinematics_exact_certified':False,'art_accepted':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_KICK_PREFLIGHT',json.dumps(report))
