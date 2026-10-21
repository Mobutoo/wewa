"""Actual isolated front/reverse/raised region; cameras uncalibrated."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'exhaust-header-gasket-v2.blend';b=json.loads((H/'build-report-v2.json').read_text());e=json.loads((R/'creative/reviews/exhaust-header-gasket-v2/export-check.json').read_text());assert sha(source)==b['source_sha256']==e['source_sha256']and sha(H/'exhaust-header-gasket-v2-inspection.glb')==e['sha256']and e['glTF_errors']==0
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];native='--preview'in args;mode='reflection'if'--reflection'in args else'gray'if'--gray'in args else'pbr';sys.path.insert(0,str(H));from render_checkpoint import checkpoint_view
from camera_preflight import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;o=bpy.data.objects[b['geometry'][0]['name']];s.cycles.samples=24 if native else 96;s.render.resolution_x=1100 if native else 1440;s.render.resolution_y=850 if native else 1080;s.camera.data.clip_start=.0001;mat=bpy.data.materials.new('Temporary isolated gasket '+mode);mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.35,.35,.35,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.17 if mode=='reflection'else .45;s.view_layers[0].material_override=mat if mode!='pbr'else None
for name,position,power,size in [('CONTROL_KEY',(.04,-.04,.06),.04,.035),('CONTROL_FILL',(-.04,.03,.03),.025,.040),('CONTROL_EDGE',(.03,.03,-.02),.02,.030)]:
 light=bpy.data.objects[name];light.location=position;light.data.energy=power;light.data.size=size;light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
views=[('front-near-normal',Vector((0,-.012,.075)),Vector((0,0,0)),False,55),('front-quarter',Vector((.045,-.045,.040)),Vector((0,0,0)),False,55),('estimated-reverse',Vector((.025,.025,-.060)),Vector((0,0,0)),False,55),('annular-raised-region-detail',Vector((.032,-.015,.040)),Vector((.014,0,.0006)),True,180)]
if'--view'in args:
 wanted=args[args.index('--view')+1];views=[q for q in views if q[0]==wanted];assert views
out=Path('/workspace/wewa-assets/work-in-progress/exhaust-header-gasket')/sha(source)[:12]/mode/'native24'if native else R/'creative/reviews/exhaust-header-gasket-v2';report={'source_sha256':sha(source),'export_sha256':e['sha256'],'samples':s.cycles.samples,'camera_calibrated':False,'frame_isolated_unmounted':True,'views':[],'art_accepted':False}
for name,position,aim,crop,lens in views:
 s.camera.location=position;s.camera.rotation_euler=(aim-position).to_track_quat('-Z','Y').to_euler();s.camera.data.type='PERSP';s.camera.data.lens=lens;bpy.context.view_layer.update();frame=check_component_camera(s,[o],allow_crop=crop,margin=.005)
 if'--preflight-only'in args:report['views'].append({'name':name,'camera_preflight':frame,'rendered':False})
 else:
  q=checkpoint_view(s,out,source,name);report['views'].append({'name':name,'camera_preflight':frame,'outputs':q['outputs']})
 out.mkdir(parents=True,exist_ok=True);(out/('camera-layout-preflight.json'if'--preflight-only'in args else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==b['source_sha256']
