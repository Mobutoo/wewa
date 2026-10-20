import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'throttle-control'))
from render_checkpoint import checkpoint_view
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/cockpit-cables-v1';source=HERE/'cockpit-cables-v1.blend';check=json.loads((OUT/'source-geometry-check.json').read_text());gltf=json.loads((OUT/'export-check.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest()==check['source_sha256'];assert not gltf['glTF_errors'];assert gltf['sha256']==hashlib.sha256((HERE/'cockpit-cables-inspection.glb').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;bpy.data.collections['CABLES_IMMUTABLE_INTERFACE_GUIDES'].hide_render=True
for o in scene.objects:
 if o.type=='LIGHT':o.data.energy*=.08
sourceobjects=list(bpy.data.collections['WEWA_COCKPIT_CABLES_PARTIAL'].objects);stage=bpy.data.collections['CABLES_STUDIO_NOT_EXPORTED']
light_offsets={o.name:o.location-Vector((.105,-.22,-.54)) for o in stage.objects if o.type=='LIGHT'}
report={'source_sha256':check['source_sha256'],'actual_blender_render':True,'samples':96,'denoising':'OpenImageDenoise','resolution_px':[1100,850],'guides_visible':False,'studio_area_energy_multiplier':.08,'views':[],'art_accepted':False}
for name,wanted,offset,lens in [('descending-visible-sections','descending',(.55,.75,.45),60),('ignition-pigtail-free-end','ignition',(.13,.18,.12),70)]:
 objects=[o for o in sourceobjects if wanted in o.name.lower()]
 for o in sourceobjects:o.hide_render=o not in objects
 points=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box];target=Vector([(min(v[i] for v in points)+max(v[i] for v in points))/2 for i in range(3)])
 for o in stage.objects:
  if o.type=='MESH':o.location.z=min(v.z for v in points)-.002
  if o.type=='LIGHT':
   o.location=target+light_offsets[o.name];o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 scene.camera.location=target+Vector(offset);scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=lens;scene.render.filepath=str(OUT/(name+'.png'));checkpoint_view(scene,OUT,source,name)
 report['views'].append({'name':name,'shown_objects':[o.name for o in objects],'target_m':list(target),'camera_m':list(scene.camera.location),'lens_mm':lens})
(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
