import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'throttle-control'))
from render_checkpoint import checkpoint_view
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/ignition-lock-v1';source=HERE/'ignition-lock-v1.blend'
check=json.loads((OUT/'source-geometry-check.json').read_text());gltf=json.loads((OUT/'export-check.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest()==check['source_sha256'];assert not gltf['glTF_errors'];assert gltf['sha256']==hashlib.sha256((HERE/'ignition-lock-inspection.glb').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;bpy.data.collections['IGNITION_IMMUTABLE_INTERFACE_GUIDES'].hide_render=True
for o in scene.objects:
 if o.type=='LIGHT':o.data.energy*=.08
datum=bpy.data.objects['Ignition provisional lower cockpit datum'];target=datum.matrix_world@Vector((0,0,-.006))
report={'source_sha256':check['source_sha256'],'actual_blender_render':True,'samples':96,'denoising':'OpenImageDenoise','resolution_px':[1100,850],'guides_visible':False,'studio_area_energy_multiplier':.08,'views':[],'art_accepted':False}
for name,frame,localoffset,lens in [('quarter-off',1,(.15,.07,.22),55),('rear-mount-on',25,(-.15,.24,-.10),65)]:
 scene.frame_set(frame);scene.camera.location=target+datum.matrix_world.to_3x3()@Vector(localoffset);scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=lens;scene.render.filepath=str(OUT/(name+'.png'));checkpoint_view(scene,OUT,source,name);report['views'].append({'name':name,'frame':frame,'camera_m':list(scene.camera.location),'target_m':list(target),'lens_mm':lens})
(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
