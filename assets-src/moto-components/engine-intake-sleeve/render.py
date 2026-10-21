"""Uncalibrated isolated gray/reflection comparison, never changes source geometry."""
from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'build-report.json').read_text());source=H/'engine-intake-sleeve-v1.blend';assert sha(source)==B['source_sha256'];E=json.loads((R/'creative/reviews/engine-intake-sleeve-v1/export-check.json').read_text());assert E['glTF_errors']==0 and E['source_sha256']==sha(source)
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];native='--preview'in args;mode='reflection'if'--reflection'in args else'gray'if'--gray'in args else'pbr';sys.path.insert(0,str(H));from camera_preflight import check_component_camera
from render_checkpoint import checkpoint_view
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;o=bpy.data.objects[B['geometry'][0]['name']];s.cycles.samples=24 if native else 96;s.render.resolution_x=1100 if native else 1440;s.render.resolution_y=850 if native else 1080;s.camera.data.clip_start=.0001
mat=bpy.data.materials.new('Temporary geometry review '+mode);mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.35,.35,.35,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.17 if mode=='reflection'else .45;s.view_layers[0].material_override=mat if mode!='pbr'else None
views=[('front-quarter',(.105,-.140,.100),(0,0,.002),False,65),('opposite-quarter-estimated',(-.105,-.130,-.100),(0,0,-.002),False,65),('front-mouth-normal',(0,0,.190),(0,0,0),False,75),('inner-lip-detail',(.045,-.060,.090),(0,0,.010),True,130),('fork-and-seam-detail',(-.080,.080,.070),(0,.019,.015),True,130),('rear-mouth-normal',(0,0,-.190),(0,0,0),False,75),('grain-raking-control',(.025,-.090,.030),(0,-.0228,.008),True,180)]
if'--view'in args:views=[q for q in views if q[0]==args[args.index('--view')+1]]
out=Path('/workspace/wewa-assets/work-in-progress/engine-intake-sleeve')/sha(source)[:12]/mode/'native24'if native else R/'creative/reviews/engine-intake-sleeve-v1';report={'source_sha256':sha(source),'export_sha256':E['sha256'],'samples':s.cycles.samples,'camera_calibrated':False,'isolated_unmounted':True,'views':[],'art_accepted':False}
initial_lights={q.name:(q.matrix_world.copy(),q.data.energy,q.data.size)for q in bpy.data.objects if q.type=='LIGHT'}
for name,position,aim,crop,lens in views:
 for light_name,(matrix,energy,size)in initial_lights.items():
  light=bpy.data.objects[light_name];light.matrix_world=matrix.copy();light.data.energy=energy;light.data.size=size
 if name in ['opposite-quarter-estimated','rear-mouth-normal']:
  key=bpy.data.objects['CONTROL_KEY'];key.location=(.035,-.045,-.080);key.data.energy=.25;key.data.size=.10;key.rotation_euler=(Vector(aim)-key.location).to_track_quat('-Z','Y').to_euler()
 if name=='grain-raking-control':
  key=bpy.data.objects['CONTROL_KEY'];key.location=(.005,-.048,.008);key.data.energy=.025;key.data.size=.015;key.rotation_euler=(Vector(aim)-key.location).to_track_quat('-Z','Y').to_euler();bpy.data.objects['CONTROL_FILL'].data.energy=.03;bpy.data.objects['CONTROL_EDGE'].data.energy=.03
 s.camera.location=position;s.camera.rotation_euler=(Vector(aim)-Vector(position)).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;bpy.context.view_layer.update();frame=check_component_camera(s,[o],allow_crop=crop,margin=.005)
 row={'name':name,'camera_preflight':frame,'rendered':False}
 if'--preflight-only'not in args:row['outputs']=checkpoint_view(s,out,source,name)['outputs'];row['rendered']=True
 report['views'].append(row);out.mkdir(parents=True,exist_ok=True);(out/('camera-preflight.json'if'--preflight-only'in args else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==B['source_sha256']
