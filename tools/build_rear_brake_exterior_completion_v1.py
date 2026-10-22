"""Independent visible rear brake linkage; estimated installation, no hidden brake mechanism."""
import bpy,bmesh,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Euler
R=Path('/workspace/wewa');K='rear-brake-exterior-completion-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;D=R/'creative/research'/K
sys.path.insert(0,str(R/'tools'));from powertrain_completion_common_open_v1 import mesh_object,look,digest
from powertrain_continuation_shapes_v2 import cyl,boolean,clean,recalc
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def basis(x,z):
 x=Vector(x).normalized();z=Vector(z);z=(z-x*x.dot(z)).normalized();y=z.cross(x).normalized();return Matrix((x,y,z)).transposed().to_4x4()
def matrix(row):return Matrix.LocRotScale(Vector(row['translation_m']),Euler(tuple(math.radians(a)for a in row['rotation_degrees']),'XYZ').to_quaternion(),Vector(row['scale']))
def material(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;return m
def loft(name,sections):
 V=[];F=[]
 for x,cy,w,z,t in sections:V.extend([(x,cy-w,z-t),(x,cy+w,z-t),(x,cy+w,z+t),(x,cy-w,z+t)])
 F=[(3,2,1,0),(len(V)-4,len(V)-3,len(V)-2,len(V)-1)]
 for i in range(len(sections)-1):
  for j in range(4):a=i*4+j;b=i*4+(j+1)%4;F.append((a,b,b+4,a+4))
 ob=mesh_object(name,V,F);recalc(ob);return ob
def bevel(ob,w):
 bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new('Bounded visible rolled edge','BEVEL');m.width=w;m.segments=3;m.limit_method='ANGLE';bpy.ops.object.modifier_apply(modifier=m.name);clean(ob)
def imported(family,name):
 p=R/'assets-src/moto-components'/family/'child-candidate.blend'
 with bpy.data.libraries.load(str(p),link=False)as(src,dst):dst.objects=[name]
 ob=dst.objects[0];ob.name='RBE_'+family.replace('-v1','').upper().replace('-','_');bpy.context.scene.collection.objects.link(ob);return ob,p
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
parents=json.loads((R/'creative/reviews/whole-exterior-coverage-v19/linked-parents-check.json').read_text())['parents'];pmap={v['key']:v for v in parents}
mp=matrix(pmap['rear-brake-pedal-three-observed-parents']);panelM=matrix(pmap['rear-brake-panel-ds151069'])
A=mp@Vector((.07434000074863434,-.11340000212192535,.009999999776482582))
C=panelM@Vector((-.045,-.0255,.020));B=C+Vector((0,-.015,-math.sqrt(.09**2-.015**2)))
rodD=(B-A).normalized();normal=Vector((-1,0,0));rodframe=basis(rodD,normal);pinN=rodframe.col[2].to_3d()
black=material('JW131601 proposed clean black coated steel',(.014,.016,.018),.18,.32);steel=material('Estimated clean plated linkage steel',(.38,.38,.34),.8,.31)
# Doubled end cheeks and curved strap; all geometry original and dimensional estimates.
lever=loft('JW131601_OBSERVED_CURVED_STRAP_AND_DOUBLE_EYES',[(x,.003*math.sin(math.pi*x/.09),.008-.0015*x/.09,0,.0015)for x in [.014,.025,.04,.055,.07,.078]])
for end,xc,zc,r in [('cam',0,.0035,.010),('rod',.09,.008,.0085)]:
 for sign in [-1,1]:
  ring=cyl((xc,0,sign*zc-.00125),(xc,0,sign*zc+.00125),r,96);boolean(lever,ring,'UNION','Observed doubled '+end+' cheek')
  if end=='cam':sec=[(.004,0,.008,sign*zc,.00125),(.012,.001,.008,sign*.002,.00125),(.027,.002,.0075,0,.00125)]
  else:sec=[(.065,.002,.007,0,.00125),(.08,.001,.007,sign*.005,.00125),(.093,0,.007,sign*zc,.00125)]
  boolean(lever,loft('Cheek transition',sec),'UNION','Estimated folded strap transition')
for xc,r in [(0,.0058),(.09,.0055)]:boolean(lever,cyl((xc,0,-.03),(xc,0,.03),r,96),'DIFFERENCE','Observed actual through-eye')
bevel(lever,.0002);lever.data.materials.append(black)
lever.matrix_world=basis(B-C,normal);lever.matrix_world.translation=C
# Short EXPOSED shaft only; catalogue identifies cam shaft but hidden shoes/cam omitted.
camstub=cyl(tuple(panelM@Vector((-.045,-.0255,.006))),tuple(C+normal*.006),.0055,80);camstub.name='RBE_EXPOSED_CAM_SHAFT_STUB_ONLY';camstub.data.materials.append(steel)
rod=cyl(tuple(A+rodD*.028),tuple(B+rodD*.024),.00275,96);rod.name='RBE_PF161001_ESTIMATED_INSTALLED_ROD';bevel(rod,.00015);rod.data.materials.append(steel)
old=json.loads((D/'native-input-geometry.json').read_text());srcmap={v['family']:v for v in old};added=[lever,camstub,rod];reuse=[]
for family in ['brake-rod-clevis-v1','brake-linkage-headed-pin-v1','brake-rod-barrel-pin-v1','brake-rod-compression-spring-v1']:
 ob,p=imported(family,srcmap[family]['object']);before=digest(ob.data)
 if 'clevis' in family:
  M=basis(-rodD,pinN);M.translation=A+rodD*.020
 elif 'headed-pin' in family:
  M=rodframe.copy();M.translation=A-pinN*.010
 elif 'barrel' in family:
  M=rodframe.copy();M.translation=B-pinN*.010
 else:
  # Existing spring longitudinal Y, preserve all geometry and winding.
  x=pinN;y=rodD;z=x.cross(y).normalized();M=Matrix((x,y,z)).transposed().to_4x4();M.translation=B-rodD*.055
 ob.matrix_world=M;added.append(ob);reuse.append(dict(object=ob.name,source=str(p.relative_to(R)),source_sha256=sha(p),old_object=srcmap[family]['object'],old_mesh_digest=before,copied_mesh_digest=digest(ob.data),shape_unchanged=True))
# Shaped adjuster exterior from actual30191036 photo, NOT a generic hex nut.
# Rounded polygon flange + narrower round barrel; plain passage, no hidden thread/seat.
V=[];F=[];N=96
for x,r,hexmix in [(-.001,.0058,1),(0,.0068,1),(.0025,.0068,1),(.0035,.0052,0),(.010,.0052,0),(.011,.0048,0)]:
 for j in range(N):
  t=2*math.pi*j/N;hexr=math.cos(math.pi/6)/math.cos((t+math.pi/6)%(math.pi/3)-math.pi/6);rad=r*((1-hexmix)+hexmix*(.5+.5*hexr));V.append((x,rad*math.cos(t),rad*math.sin(t)))
F=[tuple(reversed(range(N))),tuple(5*N+j for j in range(N))]
for i in range(5):
 for j in range(N):F.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
nut=mesh_object('RBE_30191036_SHAPED_SHOULDER_ADJUSTER_EXTERIOR',V,F);recalc(nut);boolean(nut,cyl((-.01,0,0),(.025,0,0),.0029,80),'DIFFERENCE','Visible passage without invented thread');bevel(nut,.00015);nut.data.materials.append(steel);nut.matrix_world=rodframe.copy();nut.matrix_world.translation=B+rodD*.0058;added.append(nut)
col=bpy.data.collections.new('WEWA_REAR_BRAKE_EXTERIOR_COMPLETION_V1');bpy.context.scene.collection.children.link(col)
for ob in added:
 for oldcol in list(ob.users_collection):oldcol.objects.unlink(ob)
 col.objects.link(ob);ob['qualification']='Photo-constrained estimated exterior; mechanical travel/fit not received'
# Context copies only, not additional exports/deliveries.
context=bpy.data.collections.new('CONTEXT_ONLY_EXISTING_V19_PANEL_PEDAL');bpy.context.scene.collection.children.link(context)
for key in ['rear-brake-panel-ds151069','rear-brake-pedal-three-observed-parents']:
 row=pmap[key]
 with bpy.data.libraries.load(str(R/row['source']),link=False)as(src,dst):dst.objects=list(row['selected_objects'])
 for ob in dst.objects:context.objects.link(ob);ob.matrix_world=matrix(row)@ob.matrix_world;ob.name='CONTEXT_ONLY_'+ob.name
# Independent mesh topology/bounds before rendering.
checks=[]
for ob in added:
 me=ob.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me);boundary=sum(e.is_boundary for e in bm.edges);nonman=sum(not e.is_manifold for e in bm.edges);bm.free();assert boundary==0 and nonman==0,(ob.name,boundary,nonman)
 assert min(t.area for t in me.loop_triangles)>1e-14
 checks.append(dict(object=ob.name,vertices=len(me.vertices),triangles=len(me.loop_triangles),boundary_edges=boundary,nonmanifold_edges=nonman,min_area=min(t.area for t in me.loop_triangles),geometry_digest=digest(me)))
write(O/'geometry-check.json',dict(objects=checks,reused_sources=reuse,mechanical_fit_received=False))
params=dict(rod_start_lug_hole_m=list(A),cam_bore_world_m=list(C),lever_barrel_world_m=list(B),rod_direction=list(rodD),new_rod_length_m=(B+rodD*.024-(A+rodD*.028)).length,old_rod_source_unchanged=True,old_rod_length_m=.49,new_length_reason='Pure existingv19 endpoint registration, no measured manufacturer length. New source, no old deformation.',depth_uncertainty_m=.02,cam_clocking_uncertainty_deg=15,lever_centre_span_m=.09,dimensions_estimated=True,objects=[o.name for o in added],hidden_mechanism_invented=False,art_accepted=False)
write(H/'parameters.json',params)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.max_bounces=5;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
w=bpy.data.worlds.new('Neutral uncalibrated environment');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.3,.3,.3,1);w.node_tree.nodes['Background'].inputs[1].default_value=.65;s.world=w
for name,eye,power,size in [('Key',(-.7,.5,-.2),35,.6),('Fill',(.5,.5,-.35),22,.5),('Top',(-.1,.5,.1),25,.4)]:
 light=bpy.data.lights.new(name,'AREA');light.energy=power;light.size=size;ob=bpy.data.objects.new(name,light);s.collection.objects.link(ob);ob.location=eye;look(ob,(A+B)/2)
cam=bpy.data.objects.new('Rear brake exterior review camera',bpy.data.cameras.new('Rear brake exterior review camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.83;cam.data.clip_start=.001;cam.data.clip_end=20;cam.location=(-1,.60,-.67);look(cam,(A+B)/2)
bpy.ops.wm.save_as_mainfile(filepath=str(H/'rear-brake-exterior.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for ob in added:ob.select_set(True)
bpy.context.view_layer.objects.active=lever;bpy.ops.export_scene.gltf(filepath=str(H/'rear-brake-exterior.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_tangents=False)
rows=[];routes=[]
for ob in added:
 row=dict(key=ob.name,source=str((H/'rear-brake-exterior.blend').relative_to(R)),sha256=sha(H/'rear-brake-exterior.blend'),collection=col.name,selected_objects=[ob.name],translation_m=[0,0,0],rotation_degrees=[0,0,0],scale=[1,1,1],matrix_world=[list(v)for v in Matrix.Identity(4)],placement_status='Object matrix already contains estimated globalv19 registration. Identity parent; do not apply placement twice.',renderable_meshes=1)
 rows.append(row);routes.append(dict(key=ob.name,source_blend=row['source'],glb=str((H/'rear-brake-exterior.glb').relative_to(R)),selected_objects=[ob.name]))
write(H/'integration-fragment.json',dict(parents_to_remove=[],additions=rows,baseline_parent_count=140,new_parent_count=140+len(rows),estimated_placement=True,art_accepted=False));write(D/'export-routes.json',dict(rows=routes));write(D/'new-parents-only.json',dict(parents=rows))
# Cheap preview only, no extra EXR or duplicate source.
s.cycles.samples=8;s.render.resolution_x=720;s.render.resolution_y=480;s.render.image_settings.file_format='PNG';s.render.filepath=str(O/'preview-whole.png');bpy.ops.render.render(write_still=True)
