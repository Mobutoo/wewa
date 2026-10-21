"""Isolated metallic stub and immutable cover context, candidate only."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'engine-ohc-stub-v1.blend';build=json.loads((H/'build-report.json').read_text());ex=json.loads((R/'creative/reviews/engine-ohc-stub-v1/export-check.json').read_text());assert sha(source)==build['source_sha256']==ex['source_sha256'];assert sha(H/'engine-ohc-stub-inspection.glb')==ex['sha256'];assert ex['glTF_errors']==0
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;mode='gray'if'--gray'in args else'reflection'if'--reflection'in args else'preview';out=Path('/workspace/wewa-assets/work-in-progress/engine-ohc-stub')/sha(source)[:12]/mode if preview else R/'creative/reviews/engine-ohc-stub-v1';out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(H));from render_checkpoint import checkpoint_view
from camera_preflight import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.cycles.samples=8 if preview else 96;s.render.resolution_x=850 if preview else 1100;s.render.resolution_y=657 if preview else 850;s.camera.data.clip_start=.0005;tube=bpy.data.objects[build['geometry'][0]['name']];datum=tube.parent;guides=bpy.data.collections['OHC_STUB_IMMUTABLE_GUIDES'];guides.hide_viewport=False;bpy.context.view_layer.update();cover=bpy.data.objects['UG5 OHC cast cover body - conditional candidate'];head=next(o for o in guides.objects if o.type=='MESH'and o.name.startswith('Engine UG5 head'));head.hide_render=True
if preview and mode!='preview':
 m=bpy.data.materials.new('Temporary stub diagnostic '+mode);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.38,.38,.38,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.15 if mode=='reflection'else .45;s.view_layers[0].material_override=m
stage=bpy.data.collections['OHC_STUB_STUDIO_NOT_EXPORTED'];target=datum.matrix_world@Vector((-.009,0,0))
# Compact area-light placement in tube coordinates; fixed spectra, original PBR.
for name,offset,energy,size in [('CONTROL_KEY',(.035,-.045,.065),1.0,.055),('CONTROL_FILL',(-.05,.03,.045),.5,.045),('CONTROL_EDGE',(.025,.035,.02),.8,.025)]:
 o=bpy.data.objects[name];o.location=target+datum.matrix_world.to_3x3()@Vector(offset);o.data.energy=energy*.12;o.data.size=size;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
views=[('tube-quarter',(.085,-.105,.07),False),('mouth-end',(.115,-.015,.012),False),('cover-interface',(.18,-.18,.14),True)]
if '--view'in args:
 wanted=args[args.index('--view')+1];views=[v for v in views if v[0]==wanted];assert views,wanted
report={'component_id':build['component_id'],'revision':'engine-ohc-stub-v1','source_sha256':sha(source),'export_sha256':ex['sha256'],'samples':s.cycles.samples,'actual_blender_render':True,'diagnostic_mode':mode if preview else'originalPBR','views':[],'all_dimensions_estimated':True,'art_accepted':False}
for name,offset,context in views:
 guides.hide_render=not context;head.hide_render=True;cover.hide_render=not context;point=cover.matrix_world@Vector((-.025,.004,.012))if context else target
 s.camera.location=point+datum.matrix_world.to_3x3()@Vector(offset);s.camera.rotation_euler=(point-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=60
 bpy.context.view_layer.update();frame=check_component_camera(s,[tube,cover]if context else[tube],allow_crop=False,margin=.005);cp=checkpoint_view(s,out,source,name);report['views'].append({'name':name,'context_cover':context,'camera_preflight':frame,'outputs':cp['outputs']});(out/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
