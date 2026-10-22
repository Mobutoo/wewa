import bpy,json
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(O/'diagnostic-linked-v3.blend'));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=640;s.render.resolution_y=540;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
s.world=bpy.data.worlds.new('Neutral');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.13,.13,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
for loc,p in [((1,-1,1),140),((-1,.3,.6),100),((0,1,0),70)]:
 d=bpy.data.lights.new('Softbox','AREA');d.energy=p;d.size=1.5;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,.19,-.54))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Diagnostic');cam=bpy.data.objects.new('Diagnostic',d);s.collection.objects.link(cam);s.camera=cam;d.type='ORTHO';d.ortho_scale=.57;d.clip_start=.01;d.clip_end=10
reports=[]
for label,loc in [('right-quarter',(-1,-.7,.05)),('left-rear',(1,.9,-.05))]:
 target=Vector((0,.18,-.54));cam.location=loc;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 for state in ['before','after']:
  bpy.data.objects['UPPER_REAR_CRANKCASE_EXTERIOR_CAST_SHELL_ESTIMATED'].hide_render=state=='before'
  s.render.image_settings.file_format='PNG';s.render.filepath=str(O/(label+'-'+state+'.png'));bpy.ops.render.render(write_still=True)
  reports.append(dict(view=label,state=state,camera=list(cam.location),target=list(target),samples=20,resolution=[640,540]))
(O/'render-report.json').write_text(json.dumps(reports,indent=2))
