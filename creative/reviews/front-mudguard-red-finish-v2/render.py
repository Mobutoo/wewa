import bpy,pathlib,json,sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=pathlib.Path('/workspace/wewa');D=R/'creative/reviews/front-mudguard-red-finish-v2';A=R/'assets-src/moto-components/front-mudguard-red-finish-v2';bpy.ops.wm.open_mainfile(filepath=str(A/'front-mudguard-red-finish-v2.blend'))
s=bpy.context.scene;mode=sys.argv[-1];report=[]
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
views=[('neutral-quarter',(.73,-.83,.67),{'KEY':65,'FILL':35,'RAKE':0}),('neutral-reverse',(-.73,.91,.64),{'KEY':35,'FILL':65,'RAKE':0}),('raking',(.73,-.83,.50),{'KEY':8,'FILL':6,'RAKE':65})]
if mode=='preview':views=views[:1];s.cycles.samples=12
else:s.cycles.samples=96
for label,loc,powers in views:
 s.camera.location=loc;aim(s.camera,(0,.06,.18))
 for n,energy in powers.items():bpy.data.objects[n].data.energy=energy
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();points=[]
 for o in bpy.data.collections['WEWA_FRONT_MUDGUARD_RED_FINISH_V2'].objects:
  ev=o.evaluated_get(dg);me=ev.to_mesh();points += [world_to_camera_view(s,s.camera,ev.matrix_world@v.co) for v in me.vertices];ev.to_mesh_clear()
 frame={'min':[min(v[i] for v in points)for i in range(3)],'max':[max(v[i] for v in points)for i in range(3)]};assert all(.01<v.x<.99 and .01<v.y<.99 and s.camera.data.clip_start<v.z<s.camera.data.clip_end for v in points),frame
 s.render.image_settings.file_format='PNG';prefix='preview12'if mode=='preview'else'native96';s.render.filepath=str(D/(prefix+'-'+label+'.png'));bpy.ops.render.render(write_still=True)
 if mode!='preview':
  s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';bpy.data.images['Render Result'].save_render(str(D/(prefix+'-'+label+'.exr')),scene=s)
 report.append({'view':label,'samples':s.cycles.samples,'camera':list(s.camera.location),'target':[0,.06,.18],'lens_mm':s.camera.data.lens,'light_energy':powers,'frame':frame,'size':[s.render.resolution_x,s.render.resolution_y],'raw_format':None if mode=='preview'else'OPEN_EXR RGBA float32','source_geometry':'linked immutable mesh; object material override only','look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma})
(D/(mode+'-render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
