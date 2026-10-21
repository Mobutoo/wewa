"""Revision-specific source/GLB-bound whole views and intentional fixation macros."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];source=H/'engine-cover-left-v2.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=json.loads((R/'creative/reviews/engine-cover-left-v2/source-geometry-check.json').read_text());gltf=json.loads((R/'creative/reviews/engine-cover-left-v2/export-check.json').read_text());assert sha(source)==checks['source_sha256'];assert sha(H/'engine-cover-left-v2-inspection.glb')==gltf['sha256'];assert not gltf['glTF_errors'] and not any(m['zeroAreaTriangles']for m in gltf['meshes'])
a=sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[];preview=True;gray=False;O=Path('/workspace/wewa-assets/work-in-progress/engine-cover-left-v2')/sha(source)[:12]/('gray'if gray else'preview')if preview else R/'creative/reviews/engine-cover-left-v2';O=Path('/workspace/wewa-assets/work-in-progress/engine-cover-left-v2')/sha(source)[:12]/'reflection';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(H));from render_checkpoint_v2 import checkpoint_view
from camera_preflight_v2 import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.camera.data.clip_start=.001;s.cycles.samples=8 if preview else 96;s.render.resolution_x=850 if preview else 1100;s.render.resolution_y=700 if preview else 850;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False
body=bpy.data.objects['LH magneto cover hollow casting - editable candidate'];datum=bpy.data.objects['Engine LH cover provisional datum'];bpy.data.collections['ENGINE_COVER_LEFT_V2_IMMUTABLE_INTERFACE_GUIDES'].hide_render=True
m=body.data.materials[0];principled=m.node_tree.nodes.get('Principled BSDF');principled.inputs['Base Color'].default_value=(.5,.5,.5,1);principled.inputs['Metallic'].default_value=1;principled.inputs['Roughness'].default_value=.12
if gray:
 m=body.data.materials[0];p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.38,.38,.38,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.4
views=[('outer-forward-boss',(0,.005,.021),(0,.13,.48),False),('rear-hollow-shell',(0,.005,.021),(-.20,.16,-.48),False),('front-fixation-transition',(-.07409,.041676,.010306),(-.032,.037,.11),True),('rear-fixation-root',(.060198,-.048622,.005016),(.025,-.035,-.10),True)]
if '--view'in a:
 name=a[a.index('--view')+1];views=[v for v in views if v[0]==name];assert views,('Unknown view',name)
report={'source_sha256':sha(source),'export_sha256':gltf['sha256'],'samples':s.cycles.samples,'denoising':'OpenImageDenoise','actual_blender_render':True,'all_dimensions_estimated':True,'reference_camera_calibrated':False,'gray_material_override':gray,'diagnostic_reflection_override':{'metallic':1,'roughness':.12,'base_color_linear':[.5,.5,.5],'scope':'RAM-only diagnostic, not exported game PBR'},'intentional_macro_crops':True,'views':[],'art_accepted':False}
for name,local,offset,detail in views:
 t=datum.matrix_world@Vector(local);s.camera.location=t+datum.matrix_world.to_3x3()@Vector(offset);s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=65;bpy.context.view_layer.update();frame=check_component_camera(s,[body],allow_crop=detail);cp=checkpoint_view(s,O,source,name);report['views'].append({'name':name,'camera_m':list(s.camera.location),'target_m':list(t),'lens_mm':65,'camera_preflight':frame,'checkpoint':name+'.checkpoint.json','outputs':cp['outputs']});(O/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
