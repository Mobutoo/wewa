import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
O=Path(__file__).resolve().parent;B=O/'engine-exterior-completion-v2-linked.blend';bpy.ops.wm.open_mainfile(filepath=str(B));s=bpy.context.scene;preview='--preview' in sys.argv
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12 if preview else 96;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=540;s.render.resolution_y=480;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
s.world=bpy.data.worlds.new('Neutral world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.11,.11,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for loc,power,size in [((1,-1,1),160,2),((-1,.2,.5),100,1.6),((0,1,0),80,1)]:
 d=bpy.data.lights.new('Engine softbox','AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,.17,-.55))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Engine comparison');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);s.camera=cam;d.type='ORTHO';d.ortho_scale=.70;d.clip_start=.01;d.clip_end=20
reports=[];target=Vector((0,.18,-.51))
for label,loc in [('left',(1,.18,-.51)),('right',(-1,.18,-.51)),('quarter',(1,-.8,.18))]:
 cam.location=loc;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();projected=[]
 for inst in bpy.context.evaluated_depsgraph_get().object_instances:
  if inst.object.type!='MESH':continue
  for co in inst.object.bound_box:projected.append(world_to_camera_view(s,cam,inst.matrix_world@Vector(co)))
 lo=[min(p[i]for p in projected)for i in range(3)];hi=[max(p[i]for p in projected)for i in range(3)];assert min(lo[:2])>.01 and max(hi[:2])<.99 and lo[2]>.01 and hi[2]<20,(label,lo,hi)
 prefix='preview-' if preview else 'native-';s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.filepath=str(O/(prefix+label+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(filepath=str(O/(prefix+label+'.png')),scene=s);reports.append(dict(view=label,samples=s.cycles.samples,device='CPU',threads=2,resolution=[540,480],camera=list(cam.location),target=list(target),ortho_scale=.70,vertex_frame_bounds=[lo,hi],linked_source=B.name,sha256=hashlib.sha256(B.read_bytes()).hexdigest()))
(O/('preview-report.json' if preview else 'native-render-report.json')).write_text(json.dumps(reports,indent=2))
