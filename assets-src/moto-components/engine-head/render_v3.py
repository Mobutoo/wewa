"""Candidate barrel whole views, explicit bare passages and cropped fin edge.
Short gray/reflection checks precede final96; immutable checkpoints bind effective scene.
"""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'engine-head-v3.blend';check=json.loads((R/'creative/reviews/engine-head-v3/source-geometry-check.json').read_text());ex=json.loads((R/'creative/reviews/engine-head-v3/export-check.json').read_text());assert sha(source)==check['source_sha256']==ex['source_sha256'];assert sha(H/'engine-head-v3-inspection.glb')==ex['sha256'];assert not ex['glTF_errors']and not any(m['zeroAreaTriangles']for m in ex['meshes'])
a=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in a;mode='gray'if'--gray'in a else'reflection'if'--reflection'in a else'preview';O=Path('/workspace/wewa-assets/work-in-progress/engine-head')/sha(source)[:12]/mode if preview else R/'creative/reviews/engine-head-v3';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(H));from render_checkpoint_v3 import checkpoint_view
from camera_preflight import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.data.collections['HEAD_IMMUTABLE_INTERFACE_GUIDES'].hide_viewport=False;bpy.context.view_layer.update();s=bpy.context.scene;s.cycles.samples=8 if preview else 96;s.render.resolution_x=850 if preview else 1100;s.render.resolution_y=657 if preview else 850;s.camera.data.clip_start=.001;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;body=bpy.data.objects['Engine UG5 head hollow exterior casting - editable candidate'];datum=bpy.data.objects['Engine head base provisional datum'];bpy.data.collections['HEAD_IMMUTABLE_INTERFACE_GUIDES'].hide_render=True
if preview and mode!='preview':
 m=bpy.data.materials.new('Temporary diagnostic '+mode);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.38,.38,.38,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.15 if mode=='reflection'else .45;s.view_layers[0].material_override=m
views=[('OHC-side-quarter',(0,0,.070),(.30,-.26,.21),False),('opposite-plug-well',(0,0,.070),(-.34,.14,.18),False),('joint-front-quarter',(0,0,.070),(.30,-.26,.21),False),('joint-rear-quarter',(0,0,.070),(.30,.26,.21),False)]
if preview:views +=[('top-fork-and-stud-columns',(0,0,.070),(.10,.05,.39),False),('lower-mating-passages',(0,0,.020),(-.16,.04,-.48),False),('tappet-seat-detail',(0,-.040,.078),(.05,-.18,.05),True),('OHC-face-normal',(0,0,.070),(.42,0,.025),False),('underside-plane-normal',(0,0,0),(0,0,-.55),False),('underside-OHC-oblique',(0,0,.015),(-.16,-.015,-.48),False)]
if '--view'in a:
 n=a[a.index('--view')+1];views=[v for v in views if v[0]==n];assert views,n
report={'component_id':'MOTO-ENGINE-HEAD-001','source_sha256':sha(source),'export_sha256':ex['sha256'],'samples':s.cycles.samples,'actual_blender_render':True,'reference_camera_calibrated':False,'all_dimensions_estimated':True,'material_diagnostic':mode if preview else'original-PBR','art_accepted':False,'views':[]}
# Exact evaluated cap copies for unsaved assembly review only.
context=bpy.data.collections.new('HEAD3_CAP_CONTEXT_RAM_ONLY');s.collection.children.link(context);capcopies=[];dg=bpy.context.evaluated_depsgraph_get()
for group,wanted in [('visit','WEWA_ENGINE_TAPPET_CAP'),('OHC','WEWA_ENGINE_OHC_COVER_BODY')]:
 linked=next(c for c in bpy.data.collections if c.name==wanted)
 for original in list(linked.all_objects):
  if original.type!='MESH':continue
  evaluated=original.evaluated_get(dg);mesh=bpy.data.meshes.new_from_object(evaluated,depsgraph=dg);copy=bpy.data.objects.new('Context exact '+group+' '+original.name,mesh);context.objects.link(copy);copy.matrix_world=original.matrix_world.copy();capcopies.append(copy)
assert body.library is None and len(capcopies)==3
bottom_data=bpy.data.lights.new('HEAD_UNDERSIDE_REVIEW_FILL','AREA');bottom_data.energy=0;bottom_data.shape='DISK';bottom_data.size=.30;bottom=bpy.data.objects.new(bottom_data.name,bottom_data);bpy.data.collections['HEAD_STUDIO_NOT_EXPORTED'].objects.link(bottom);bottom.location=datum.matrix_world@Vector((.02,.01,-.25));bottom.rotation_euler=((datum.matrix_world@Vector((0,0,.01)))-bottom.location).to_track_quat('-Z','Y').to_euler()
for name,point,offset,detail in views:
 for copy in capcopies:copy.hide_render=not name.startswith('joint-')
 shown=[body]+(capcopies if name.startswith('joint-')else[])
 bottom_data.energy=.9 if name in ['lower-mating-passages','underside-plane-normal','underside-OHC-oblique']else 0
 for o in bpy.data.collections['HEAD_STUDIO_NOT_EXPORTED'].objects:
  if o.type=='MESH':o.hide_render=name in ['lower-mating-passages','underside-plane-normal','underside-OHC-oblique']
 target=datum.matrix_world@Vector(point);s.camera.location=target+datum.matrix_world.to_3x3()@(Vector(offset)*(1 if detail else 1.55));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=65
 if name=='underside-plane-normal':
  from mathutils import Matrix
  s.camera.rotation_euler=(datum.matrix_world.to_3x3()@Matrix(((-1,0,0),(0,1,0),(0,0,-1)))).to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=.290
 bpy.context.view_layer.update();frame=check_component_camera(s,shown,allow_crop=detail,margin=.005);cp=checkpoint_view(s,O,source,name);report['views'].append({'name':name,'camera_m':list(s.camera.location),'target_m':list(target),'lens_mm':65,'camera_preflight':frame,'shown_objects':[o.name for o in shown],'cap_world_matrices_unchanged':True,'checkpoint':name+'.checkpoint.json','outputs':cp['outputs']});(O/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
