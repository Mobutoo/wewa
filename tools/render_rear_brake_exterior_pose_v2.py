import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');K='rear-brake-exterior-completion-v1';H=R/'assets-src/moto-components'/K/'pose-correction-v2';O=R/'creative/reviews'/K/'pose-correction-v2';sys.path.insert(0,str(R/'tools'));from powertrain_completion_common_open_v1 import look,digest
bpy.ops.wm.open_mainfile(filepath=str(H/'rear-brake-exterior-pose-v2.blend'));s=bpy.context.scene;P=json.loads((H/'parameters.json').read_text());A=Vector(P['rod_start_lug_hole_m']);B=Vector(P['lever_barrel_world_m']);C=Vector(P['cam_bore_world_m']);rows=[];before={o.name:digest(o.data)for o in s.objects if o.type=='MESH'}
for label,eye,target,scale in [('whole',(-1,.6,-.67),(A+B)/2,.83)]:
 s.camera.location=eye;look(s.camera,target);s.camera.data.ortho_scale=scale;s.cycles.samples=96;s.render.resolution_x=720;s.render.resolution_y=480;s.render.resolution_percentage=100
 s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.filepath=str(O/(label+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(label+'.png')),scene=s);rows.append(dict(view=label,samples=96,resolution_px=[720,480],png=label+'.png',exr=label+'.exr',source_sha256=hashlib.sha256((H/'rear-brake-exterior-pose-v2.blend').read_bytes()).hexdigest()))
assert before=={o.name:digest(o.data)for o in s.objects if o.type=='MESH'}
(O/'render-report.json').write_text(json.dumps(dict(views=rows,source_not_saved_or_modified=True,geometry_unchanged=True,mechanical_fit_received=False,art_accepted=False),indent=2)+'\n')
