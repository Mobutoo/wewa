"""Isolated observed underface/stem, explicitly unknown crown and conditional pair."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'exhaust-heatshield-fastener-v1.blend';b=json.loads((H/'build-report.json').read_text());e=json.loads((R/'creative/reviews/exhaust-heatshield-fastener-v1/export-check.json').read_text());assert sha(source)==b['source_sha256']==e['source_sha256']and sha(H/'exhaust-heatshield-fastener-inspection.glb')==e['sha256']and e['glTF_errors']==0
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;gray='--gray'in args;reflection='--reflection'in args;mode='reflection'if reflection else'gray'if gray else'pbr';sys.path.insert(0,str(H));from render_checkpoint import checkpoint_view
from camera_preflight import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;objects=[bpy.data.objects[q['name']]for q in b['geometry']];guides=bpy.data.collections['SHIELD_FASTENER_IMMUTABLE_GUIDES'];guides.hide_viewport=False;bpy.context.view_layer.update();keepouts=[q for q in guides.all_objects if q.type=='MESH'];a=objects[0].matrix_world.translation.copy();centre=sum((q.matrix_world.translation for q in objects),Vector())/2;s.cycles.samples=24 if preview else 96;s.render.resolution_x=1100 if preview else 1440;s.render.resolution_y=850 if preview else 1080;s.camera.data.clip_start=.0001;mat=bpy.data.materials.new('Temporary fastener '+mode+' control');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.35,.35,.35,1);p.inputs['Metallic'].default_value=1 if reflection else 0;p.inputs['Roughness'].default_value=.17 if reflection else .45;s.view_layers[0].material_override=mat if gray or reflection else None
views=[('bearing-underface-quarter',a+Vector((.035,-.025,.020)),a+Vector((.001,0,0)),False,False,70),('stem-thread-detail',a+Vector((.045,-.027,.015)),a+Vector((.003,0,0)),False,True,160),('plain-crown-unknown-drive',a+Vector((-.035,-.015,.012)),a+Vector((-.0005,0,0)),False,False,70),('two-conditional-fixings-context',centre+Vector((-.8,.3,.15)),centre,True,True,50)]
if'--view'in args:
 wanted=args[args.index('--view')+1];views=[q for q in views if q[0]==wanted];assert views
out=Path('/workspace/wewa-assets/work-in-progress/exhaust-heatshield-fastener')/sha(source)[:12]/mode/'native24'if preview else R/'creative/reviews/exhaust-heatshield-fastener-v1';report={'source_sha256':sha(source),'export_sha256':e['sha256'],'samples':s.cycles.samples,'diagnostic_mode':mode,'camera_calibrated':False,'crown_and_drive_unobserved':True,'views':[],'art_accepted':False}
for name,position,aim,context,crop,lens in views:
 guides.hide_render=not context;objects[1].hide_render=not context;s.camera.location=position;s.camera.rotation_euler=(aim-position).to_track_quat('-Z','Y').to_euler();s.camera.data.type='PERSP';s.camera.data.lens=lens
 for lightname,offset,power,size in [('CONTROL_KEY',(-.035,-.035,.050),.04,.045),('CONTROL_FILL',(.045,.025,.020),.035,.035),('CONTROL_EDGE',(-.020,.035,-.010),.03,.030)]:
  light=bpy.data.objects[lightname];light.location=aim+Vector(offset)* (14 if context else 1);light.data.energy=power*(200 if context else 1);light.data.size=size*(14 if context else 1);light.rotation_euler=(aim-light.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update();frame=check_component_camera(s,objects+(keepouts if context else[])if context else[objects[0]],allow_crop=crop,margin=.005)
 if'--preflight-only'in args:report['views'].append({'name':name,'camera_preflight':frame,'rendered':False})
 else:
  q=checkpoint_view(s,out,source,name);report['views'].append({'name':name,'camera_preflight':frame,'outputs':q['outputs']})
 out.mkdir(parents=True,exist_ok=True);(out/('camera-layout-preflight.json'if'--preflight-only'in args else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==b['source_sha256']
