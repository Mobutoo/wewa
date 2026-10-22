import bpy,pathlib,json,sys
R=pathlib.Path('/workspace/wewa');D=R/'creative/reviews/headlamp-interior-context-v1';A=R/'assets-src/moto-components/headlamp-interior-context-v1';bpy.ops.wm.open_mainfile(filepath=str(A/'headlamp-context.blend'));s=bpy.context.scene
mode=sys.argv[-1];s.cycles.samples=12 if mode=='preview' else 96
s.render.image_settings.file_format='PNG';s.render.resolution_percentage=50 if mode=='preview' else 100
s.render.filepath=str(D/(mode+'-source.png'));bpy.ops.render.render(write_still=True)
if mode!='preview':
 s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';bpy.data.images['Render Result'].save_render(str(D/'native96-source.exr'),scene=s)
 for o in list(s.objects):
  if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=str(A/'bulb-provisional.glb'))
 s.render.image_settings.file_format='PNG';s.render.filepath=str(D/'native96-export.png');bpy.ops.render.render(write_still=True)
 s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';bpy.data.images['Render Result'].save_render(str(D/'native96-export.exr'),scene=s)
(D/(mode+'-render.json')).write_text(json.dumps({'samples':s.cycles.samples,'engine':'CYCLES','device':'CPU','threads':2,'resolution':[s.render.resolution_x*s.render.resolution_percentage//100,s.render.resolution_y*s.render.resolution_percentage//100],'source_export_same_camera_lights':mode!='preview','G6_engine_babylon_executed':False},indent=2)+'\n')
