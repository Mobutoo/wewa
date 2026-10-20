"""Actual isolated outer and rear-cavity views, each independently restartable."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/engine-cover-right-v1';source=HERE/'engine-cover-right-v1.blend'
sys.path.insert(0,str(HERE.parent/'throttle-control'));from render_checkpoint import checkpoint_view
check=json.loads((OUT/'source-geometry-check.json').read_text());gltf=json.loads((OUT/'export-check.json').read_text());assert hashlib.sha256(source.read_bytes()).hexdigest()==check['source_sha256'];assert hashlib.sha256((HERE/'engine-cover-right-inspection.glb').read_bytes()).hexdigest()==gltf['sha256'];assert not gltf['glTF_errors'] and not any(m['zeroAreaTriangles'] for m in gltf['meshes'])
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;datum=bpy.data.objects['Engine RH cover provisional datum'];target=datum.matrix_world@Vector((0,-.005,.021))
report={'source_sha256':check['source_sha256'],'export_sha256':gltf['sha256'],'samples':96,'denoising':'OpenImageDenoise','resolution_px':[1100,850],'actual_blender_render':True,'guides_visible':False,'all_dimensions_estimated':True,'views':[],'art_accepted':False}
for name,offset,lens in [('outer-bosses',(.0,.16,.58),65),('rear-hollow-shell',(-.308,.182,-.504),65)]:
 scene.camera.location=target+datum.matrix_world.to_3x3()@Vector(offset);scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=lens
 cp=checkpoint_view(scene,OUT,source,name);report['views'].append({'name':name,'camera_m':list(scene.camera.location),'target_m':list(target),'lens_mm':lens,'checkpoint':name+'.checkpoint.json','outputs':cp['outputs']})
(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
