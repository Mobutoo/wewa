import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');K='rear-brake-exterior-completion-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
sys.path.insert(0,str(R/'tools'));from powertrain_completion_common_open_v1 import look,digest
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(H/'rear-brake-exterior.blend'));s=bpy.context.scene;P=json.loads((H/'parameters.json').read_text());A=Vector(P['rod_start_lug_hole_m']);B=Vector(P['lever_barrel_world_m']);C=Vector(P['cam_bore_world_m']);mid=(A+B)/2
s.camera.location=(-1,.6,-.67);look(s.camera,mid);s.camera.data.ortho_scale=.83
bpy.ops.wm.save_as_mainfile(filepath=str(H/'rear-brake-exterior.blend'),compress=True)
p=H/'integration-fragment.json';f=json.loads(p.read_text())
for row in f['additions']:row['sha256']=sha(H/'rear-brake-exterior.blend')
p.write_text(json.dumps(f,indent=2)+'\n');(R/'creative/research'/K/'new-parents-only.json').write_text(json.dumps(dict(parents=f['additions']),indent=2)+'\n')
# Whole frame + two explicitly cropped context details; no extra source/world copies.
views=[('whole',(-1,.6,-.67),mid,.83),('cam-front',(-.45,.92,-.78),(B+C)/2,.17),('cam-reverse',(.25,.92,-.78),(B+C)/2,.17)]
rows=[];before={o.name:digest(o.data)for o in s.objects if o.type=='MESH'}
for label,eye,target,scale in views:
 s.camera.location=eye;look(s.camera,target);s.camera.data.ortho_scale=scale;s.cycles.samples=96;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100
 s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.filepath=str(O/(label+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(label+'.png')),scene=s)
 rows.append(dict(view=label,samples=96,resolution_px=[960,640],png=label+'.png',exr=label+'.exr',source_sha256=sha(H/'rear-brake-exterior.blend'),intentional_context_crop=label!='whole'))
assert before=={o.name:digest(o.data)for o in s.objects if o.type=='MESH'}
(O/'render-report.json').write_text(json.dumps(dict(views=rows,source_geometry_unchanged=True,fit_qualified=False,art_accepted=False),indent=2)+'\n')
