"""Actual saved carrier/spool only, plus a second working-pose close-up."""
import json,hashlib,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'throttle-control'))
from render_checkpoint import checkpoint_view
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/throttle-control-v1'
source=HERE/'throttle-control-v1.blend';check=json.loads((OUT/'source-geometry-check.json').read_text());gltf=json.loads((OUT/'export-check.json').read_text())
assert check['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest();assert not gltf['glTF_errors'];assert gltf['sha256']==hashlib.sha256((ROOT/gltf['path']).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;bpy.data.collections['THROTTLE_LINKED_INTERFACE_GUIDES'].hide_render=True
for o in scene.objects:
 if o.type=='LIGHT':o.data.energy*=.08
points=[o.matrix_world@Vector(v) for o in bpy.data.collections['WEWA_THROTTLE_CONTROL'].objects if o.type=='MESH' for v in o.bound_box]
for o in bpy.data.collections['THROTTLE_STUDIO_NOT_EXPORTED'].objects:
 if o.type=='MESH':o.location.z=min(v.z for v in points)-.001
report={'source_sha256':check['source_sha256'],'samples':96,'denoising':'OpenImageDenoise','resolution_px':[1100,850],'actual_blender_render':True,'studio_area_energy_multiplier':.08,'guides_visible':False,'views':[],'art_accepted':False}
for name,frame,target,offset,lens in [('quarter-rest',1,(-.280,.059,.105),(-.16,-.19,.14),65),('spool-working-50deg',49,(-.225,.035,.105),(.10,-.12,.11),80)]:
 scene.frame_set(frame);scene.camera.location=Vector(target)+Vector(offset);scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=lens;scene.render.filepath=str(OUT/(name+'.png'));scene.render.image_settings.file_format='PNG';checkpoint_view(scene,OUT,source,name);report['views'].append({'name':name,'frame':frame,'working_angle_degrees':0 if frame==1 else 50,'location':list(scene.camera.location),'target':target,'lens_mm':lens})
(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
