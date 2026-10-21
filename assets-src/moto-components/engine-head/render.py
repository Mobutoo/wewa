"""Candidate barrel whole views, explicit bare passages and cropped fin edge.
Short gray/reflection checks precede final96; immutable checkpoints bind effective scene.
"""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'engine-head-v1.blend';check=json.loads((R/'creative/reviews/engine-head-v1/source-geometry-check.json').read_text());ex=json.loads((R/'creative/reviews/engine-head-v1/export-check.json').read_text());assert sha(source)==check['source_sha256']==ex['source_sha256'];assert sha(H/'engine-head-inspection.glb')==ex['sha256'];assert not ex['glTF_errors']and not any(m['zeroAreaTriangles']for m in ex['meshes'])
a=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in a;mode='gray'if'--gray'in a else'reflection'if'--reflection'in a else'preview';O=Path('/workspace/wewa-assets/work-in-progress/engine-head')/sha(source)[:12]/mode if preview else R/'creative/reviews/engine-head-v1';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(H));from render_checkpoint import checkpoint_view
from camera_preflight import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.cycles.samples=8 if preview else 96;s.render.resolution_x=850 if preview else 1100;s.render.resolution_y=700 if preview else 850;s.camera.data.clip_start=.001;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;body=bpy.data.objects['Engine UG5 head hollow exterior casting - editable candidate'];datum=bpy.data.objects['Engine head base provisional datum'];bpy.data.collections['HEAD_IMMUTABLE_INTERFACE_GUIDES'].hide_render=True
if preview and mode!='preview':
 m=bpy.data.materials.new('Temporary diagnostic '+mode);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.38,.38,.38,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.15 if mode=='reflection'else .45;s.view_layers[0].material_override=m
views=[('OHC-side-quarter',(0,0,.070),(.30,-.26,.21),False),('opposite-plug-well',(0,0,.070),(-.34,.14,.18),False),('top-fork-and-stud-columns',(0,0,.070),(.10,.05,.39),False),('lower-mating-passages',(0,0,.070),(.13,.12,-.39),False)]
if preview:views +=[('tappet-seat-detail',(0,-.040,.078),(.05,-.18,.05),True),('OHC-face-normal',(0,0,.070),(.42,0,.025),False)]
if '--view'in a:
 n=a[a.index('--view')+1];views=[v for v in views if v[0]==n];assert views,n
report={'component_id':'MOTO-ENGINE-HEAD-001','source_sha256':sha(source),'export_sha256':ex['sha256'],'samples':s.cycles.samples,'actual_blender_render':True,'reference_camera_calibrated':False,'all_dimensions_estimated':True,'material_diagnostic':mode if preview else'original-PBR','art_accepted':False,'views':[]}
for name,point,offset,detail in views:
 for o in bpy.data.collections['HEAD_STUDIO_NOT_EXPORTED'].objects:
  if o.type=='MESH':o.hide_render=name=='lower-mating-passages'
 target=datum.matrix_world@Vector(point);s.camera.location=target+datum.matrix_world.to_3x3()@(Vector(offset)*(1 if detail else 1.20));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=65;bpy.context.view_layer.update();frame=check_component_camera(s,[body],allow_crop=detail,margin=.005);cp=checkpoint_view(s,O,source,name);report['views'].append({'name':name,'camera_m':list(s.camera.location),'target_m':list(target),'lens_mm':65,'camera_preflight':frame,'checkpoint':name+'.checkpoint.json','outputs':cp['outputs']});(O/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
