"""Estimated outside/inside/edge cameras for one rear closure only."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'exhaust-silencer-end-v1.blend';b=json.loads((H/'build-report.json').read_text());e=json.loads((R/'creative/reviews/exhaust-silencer-end-v1/export-check.json').read_text());assert sha(source)==b['source_sha256']==e['source_sha256']and sha(H/'exhaust-silencer-end-inspection.glb')==e['sha256']and e['glTF_errors']==0
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;mode='reflection'if'--reflection'in args else'gray'if'--gray'in args else'pbr';sys.path.insert(0,str(H));from render_checkpoint import checkpoint_view
from camera_preflight import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;o=bpy.data.objects[b['geometry'][0]['name']];guides=bpy.data.collections['SILENCER_END_IMMUTABLE_GUIDES'];guides.hide_viewport=False;bpy.context.view_layer.update();keepouts=[q for q in guides.all_objects if q.type=='MESH'];target=o.parent.matrix_world.translation+Vector((0,.001,0));s.cycles.samples=24 if preview else 96;s.render.resolution_x=1100 if preview else 1440;s.render.resolution_y=850 if preview else 1080;s.camera.data.clip_start=.0005;mat=bpy.data.materials.new('Temporary rear closure '+mode+' control');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.35,.35,.35,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.17 if mode=='reflection'else .45;s.view_layers[0].material_override=mat if mode!='pbr'else None
for name,offset,energy,size in [('CONTROL_KEY',(-.15,.20,.18),3,.20),('CONTROL_FILL',(.15,-.12,.08),2,.18),('CONTROL_EDGE',(-.08,-.10,-.10),2,.14)]:
 light=bpy.data.objects[name];light.location=target+Vector(offset);light.data.energy=energy;light.data.size=size;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
views=[('outside-rear-quarter',target+Vector((-.14,.25,.10)),target,False,False,65),('estimated-inner-front',target+Vector((.12,-.22,.05)),target,False,False,65),('small-outlet-detail',target+Vector((.012,.12,.015)),target,False,True,110),('peripheral-edge-detail',target+Vector((-.074,.14,.02)),target+Vector((-.034,0,0)),False,True,180),('conditional-rear-shell-context',target+Vector((-.18,.32,.12)),target,True,True,75)]
if'--view'in args:
 wanted=args[args.index('--view')+1];views=[v for v in views if v[0]==wanted];assert views
if not preview and '--view'not in args:views=[v for v in views if v[0]in ['outside-rear-quarter','estimated-inner-front','small-outlet-detail','conditional-rear-shell-context']]
out=Path('/workspace/wewa-assets/work-in-progress/exhaust-silencer-end')/sha(source)[:12]/mode/'native24'if preview else R/'creative/reviews/exhaust-silencer-end-v1';r={'source_sha256':sha(source),'export_sha256':e['sha256'],'samples':s.cycles.samples,'diagnostic_mode':mode,'camera_calibrated':False,'all_dimensions_estimated':True,'views':[],'art_accepted':False}
for name,position,aim,context,crop,lens in views:
 guides.hide_render=not context;s.camera.location=position;s.camera.rotation_euler=(aim-position).to_track_quat('-Z','Y').to_euler();s.camera.data.type='PERSP';s.camera.data.lens=lens;bpy.context.view_layer.update();frame=check_component_camera(s,[o]+(keepouts if context else[]),allow_crop=crop,margin=.005)
 if'--preflight-only'in args:r['views'].append({'name':name,'camera_preflight':frame,'rendered':False})
 else:
  cp=checkpoint_view(s,out,source,name);r['views'].append({'name':name,'camera_preflight':frame,'outputs':cp['outputs']})
 out.mkdir(parents=True,exist_ok=True);(out/('camera-layout-preflight.json'if'--preflight-only'in args else'render-report.json')).write_text(json.dumps(r,indent=2)+'\n')
assert sha(source)==b['source_sha256']
