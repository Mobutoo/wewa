"""Photo-like side comparison and RH volume, never a calibrated camera reconstruction."""
import json,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'throttle-control'))
from render_checkpoint import checkpoint_view
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/handlebar-grips-v3';source=HERE/'handlebar-grips-v3.blend'
check=json.loads((OUT/'source-geometry-check.json').read_text());export=json.loads((OUT/'export-check.json').read_text());P=json.loads((HERE/'parameters-v3.json').read_text())
assert check['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest();assert not export['glTF_errors'];assert export['sha256']==hashlib.sha256((ROOT/export['path']).read_bytes()).hexdigest();assert all(not m['zeroAreaTriangles'] for m in export['meshes'])
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE'
for o in scene.objects:
 if o.type=='LIGHT':o.data.energy*=.08
report={'source_sha256':check['source_sha256'],'actual_blender_render':True,'samples':96,'resolution_px':[1100,850],'denoising':'OpenImageDenoise','studio_area_energy_multiplier':.08,'albedo_changed_to_compensate_light':False,'documentary_camera_calibrated':False,'views':[],'art_accepted':False}
for side,name in [('left','left-reference-side'),('right','right-quarter')]:
 for other in ['left','right']:bpy.data.objects[other.title()+' rubber grip - editable candidate'].hide_render=other!=side
 axis=Vector(P[side+'_axis_inward_vector']).normalized();end=Vector(P[side+'_bar_endpoint_m']);b=axis.cross(Vector((0,0,1))).normalized();target=end+axis*.058
 offset=b*.34-axis*.015+Vector((0,0,.085)) if side=='left' else axis*.07+b*.26+Vector((0,0,.16))
 scene.camera.location=target+offset;scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=65
 scene.render.filepath=str(OUT/(name+'.png'));scene.render.image_settings.file_format='PNG';checkpoint_view(scene,OUT,source,name)
 report['views'].append({'name':name,'physical_side':side,'camera_location_m':list(scene.camera.location),'target_m':list(target),'lens_mm':65,'projection_scope':'Approximate documentary direction only; no metric overlay','other_grip_hidden':True})
(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
