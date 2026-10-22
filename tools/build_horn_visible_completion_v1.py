"""Photo-constrained JV401602 front envelope, no hidden electrical internals."""
import bpy,bmesh,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/workspace/wewa');K='horn-visible-completion-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;D=R/'creative/research'/K
sys.path.insert(0,str(R/'tools'));from powertrain_completion_common_open_v1 import mesh_object,look,digest
from powertrain_continuation_shapes_v2 import boolean,cyl,clean,recalc
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def mat(name,c,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;return m
def prism(name,poly,z0,z1):
 n=len(poly);ob=mesh_object(name,[(x,y,z)for z in [z0,z1]for x,y in poly],[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]);recalc(ob);return ob
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;black=mat('Estimated clean black coated horn steel',(.012,.014,.016),.25,.34);steel=mat('Estimated exposed terminal/centre metal',(.32,.32,.27),.8,.32)
# Observed outer return, rolled bead and cupped front. Back edge deliberately open.
control=[(.034,-.013),(.037,-.010),(.0385,-.006),(.039,-.001),(.0388,.001),(.0378,.002),(.0365,.0015),(.035,.0002),(.031,-.0015),(.026,-.0035),(.020,-.0045),(.014,-.004),(.008,-.003),(.0045,-.0025)]
profile=[]
for a,b in zip(control,control[1:]):
 for j in range(5):t=j/5;profile.append((a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t))
profile.append(control[-1]);n=128;V=[(r*math.cos(j*math.tau/n),r*math.sin(j*math.tau/n),z)for r,z in profile for j in range(n)];F=[]
for i in range(len(profile)-1):
 for j in range(n):F.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
# Central near face terminates at visible boss, no invented rear diaphragm.
body=mesh_object('HORN_JV401602_CUPPED_FRONT_ROLLED_RIM_OPEN_BACK',V,F);recalc(body);body.data.materials.append(black)
boss=cyl((0,0,-.0035),(0,0,.0005),.0047,80);boss.name='HORN_OBSERVED_CENTRAL_EXTERNAL_BUTTON';boss.data.materials.append(steel)
strap=prism('HORN_OBSERVED_PIERCED_MOUNT_STRAP',[(-.084,-.009),(-.080,-.012),(-.044,-.012),(-.030,-.008),(-.030,.008),(-.080,.009),(-.084,.006)],-.012,-.010)
boolean(strap,cyl((-.077,0,-.020),(-.077,0,0),.0043,64),'DIFFERENCE','Actual photographed strap hole');clean(strap);strap.data.materials.append(black)
objects=[body,boss,strap]
for i,x in enumerate([-.030,-.022]):
 tab=prism('HORN_VISIBLE_TERMINAL_TAB_'+str(i+1),[(x-.0022,.017),(x+.0022,.017),(x+.0022,.029),(x-.0022,.029)],-.012,-.0112);tab.data.materials.append(steel);objects.append(tab)
# Local face normal+Z -> native forward-Y; local-X -> native-up+Z, strap extends up.
M=Matrix(((0,1,0,0), (0,0,-1,0),(-1,0,0,0),(0,0,0,1)));M.translation=Vector((.030,-.130,-.395))
col=bpy.data.collections.new('WEWA_HORN_VISIBLE_COMPLETION_V1');bpy.context.scene.collection.children.link(col)
rows=[]
for o in objects:
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.matrix_world=M.copy();m=o.data;m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m);boundary=sum(e.is_boundary for e in bm.edges);bad=sum(not e.is_manifold and not e.is_boundary for e in bm.edges);bm.free();assert bad==0;assert boundary==(256 if o==body else 0),(o.name,boundary);assert min(t.area for t in m.loop_triangles)>1e-14;rows.append(dict(object=o.name,vertices=len(m.vertices),triangles=len(m.loop_triangles),boundary_edges=boundary,back_deliberately_unmodeled=o==body,geometry_digest=digest(m)))
write(O/'geometry-check.json',dict(objects=rows,art_accepted=False))
params=dict(identity='JV401602 visible exterior prototype',collection=col.name,objects=[o.name for o in objects],nominal_radius_m=.039,all_dimensions_estimated=True,global_matrix=[list(v)for v in M],position_uncertainty_m=.020,orientation_uncertainty_deg=15,hidden_rear_face_omitted=True,internal_electrics_modeled=False,art_accepted=False);write(H/'parameters.json',params)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=96;s.render.resolution_x=720;s.render.resolution_y=540;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
w=bpy.data.worlds.new('Neutral white horn review');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.5,.5,.5,1);w.node_tree.nodes['Background'].inputs[1].default_value=.6;s.world=w;target=M@Vector((-.020,0,-.004))
for name,offset,power in [('Key',(.2,-.25,.3),8),('Fill',(-.2,-.15,.1),4),('Rim',(.12,.15,.2),6)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.size=.2;ob=bpy.data.objects.new(name,l);s.collection.objects.link(ob);ob.location=target+Vector(offset);look(ob,target)
cam=bpy.data.objects.new('Horn full exterior camera',bpy.data.cameras.new('Horn full exterior camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.17;cam.data.clip_start=.001;cam.data.clip_end=5;cam.location=target+Vector((.14,-.3,.12));look(cam,target)
bpy.ops.wm.save_as_mainfile(filepath=str(H/'horn-visible.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=body;bpy.ops.export_scene.gltf(filepath=str(H/'horn-visible.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_tangents=False)
row=dict(key='horn-visible-jv401602',source=str((H/'horn-visible.blend').relative_to(R)),sha256=sha(H/'horn-visible.blend'),collection=col.name,selected_objects=[o.name for o in objects],translation_m=[0,0,0],rotation_degrees=[0,0,0],scale=[1,1,1],matrix_world=[list(v)for v in Matrix.Identity(4)],placement_status='Photo-bounded estimated front-downmember location. Objects already globally posed; parent identity. Bracket mount/hidden terminals not received.',renderable_meshes=5)
write(H/'integration-fragment.json',dict(parents_to_remove=[],additions=[row],baseline_parent_count=151,add_count=1,art_accepted=False));write(D/'export-routes.json',dict(rows=[dict(key=row['key'],source_blend=row['source'],glb=str((H/'horn-visible.glb').relative_to(R)),selected_objects=row['selected_objects'])]));write(D/'new-parent-only.json',dict(parents=[row]))
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'horn-exterior96.exr');bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/'horn-exterior96.png'),scene=s);write(O/'render-report.json',dict(source_sha256=sha(H/'horn-visible.blend'),samples=96,resolution_px=[720,540],png='horn-exterior96.png',exr='horn-exterior96.exr',art_accepted=False))
