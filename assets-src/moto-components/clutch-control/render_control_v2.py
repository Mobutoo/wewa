"""Saved geometry only: isolated mechanical lever, resting and inspection pull."""
import hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
folder=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'clutch-control'
HERE=ROOT/'assets-src/moto-components'/folder;OUT=ROOT/'creative/reviews'/(folder+'-v2')
source=HERE/(folder+'-v2.blend');check=json.loads((OUT/'source-geometry-check.json').read_text());gltf=json.loads((OUT/'export-check.json').read_text())
assert check['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert not gltf['glTF_errors'] and gltf['sha256']==hashlib.sha256((ROOT/gltf['path']).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
for o in scene.objects:
 if o.type=='LIGHT':o.data.energy*=.08
prefix='Clutch' if folder=='clutch-control' else 'Front cable brake'
bpy.data.collections[prefix+' immutable interface guides'].hide_render=True
source_collection=bpy.data.collections['WEWA_'+folder.upper().replace('-','_')]
points=[o.matrix_world@Vector(v) for o in source_collection.objects if o.type=='MESH' for v in o.bound_box]
minz=min(v.z for v in points)
for o in bpy.data.collections[prefix+' studio not exported'].objects:
 if o.type=='MESH':o.location.z=minz-.001
centre=Vector(check['pivot_world_m']);outward=Vector((1 if folder=='clutch-control' else -1,0,0));target=Vector([(min(v[i] for v in points)+max(v[i] for v in points))/2 for i in range(3)])
report={'source_sha256':check['source_sha256'],'samples':96,'denoising':'OpenImageDenoise','resolution_px':[1100,850],'actual_blender_render':True,'guides_visible':False,'studio_area_energy_multiplier':.08,'first_overexposed_cropped_view_rejected':True,'views':[],'art_accepted':False}
for name,frame,offset,lens in [('quarter-rest',1,Vector((outward.x*.20,.27,.25)),58),('pivot-working-12deg',25,Vector((outward.x*.16,.17,.22)),65)]:
 scene.frame_set(frame);viewtarget=target if frame==1 else centre+outward*.025
 scene.camera.location=viewtarget+offset;scene.camera.rotation_euler=(viewtarget-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=lens
 scene.render.filepath=str(OUT/(name+'.png'));scene.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
 report['views'].append({'name':name,'frame':frame,'working_pull_degrees':0 if frame==1 else 12,'location':list(scene.camera.location),'target':list(viewtarget),'lens_mm':lens})
(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
