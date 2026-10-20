"""Render immutable saved candidates after actual source/export preflight."""
import json,hashlib,math
from pathlib import Path
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/handlebar-grips-v1'
source=HERE/'handlebar-grips-v1.blend';check=json.loads((OUT/'source-geometry-check.json').read_text());export=json.loads((OUT/'export-check.json').read_text());P=json.loads((HERE/'parameters.json').read_text())
assert check['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert not export['glTF_errors'] and export['sha256']==hashlib.sha256((ROOT/export['path']).read_bytes()).hexdigest()
assert all(r['closed_connected_shells']==1 and r['non_manifold_edges']==0 for r in check['checks'])
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
report={'source_sha256':check['source_sha256'],'actual_blender_render':True,'samples':96,'resolution_px':[1100,850],'denoising':False,'views':[],'art_accepted':False}
for side in ['left','right']:
 for other in ['left','right']:bpy.data.objects[other.title()+' rubber grip - editable candidate'].hide_render=other!=side
 axis=Vector(P[side+'_axis_inward_vector']).normalized();end=Vector(P[side+'_bar_endpoint_m']);b=axis.cross(Vector((0,0,1))).normalized();target=end+axis*.058
 scene.camera.location=target+axis*.07+b*.26+Vector((0,0,.16));scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=65
 scene.render.filepath=str(OUT/(side+'-quarter.png'));scene.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
 report['views'].append({'name':side+'-quarter','camera_location_m':list(scene.camera.location),'camera_target_m':list(target),'lens_mm':65,'other_grip_hidden_for_isolated_review':True})
(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
