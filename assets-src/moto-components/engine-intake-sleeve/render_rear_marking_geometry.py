"""Uncalibrated isolated gray/reflection comparison, never changes source geometry."""
from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'geometry-report.json').read_text());source=H/'engine-intake-sleeve-v1-geometry.blend';assert sha(source)==B['source_sha256'];E=json.loads((R/'creative/reviews/engine-intake-sleeve-v1/export-check.json').read_text());assert E['glTF_errors']==0 and E['source_sha256']==sha(source)
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];mode='reflection'if'--reflection'in args else'gray';sys.path.insert(0,str(H));from camera_preflight import check_component_camera
from render_checkpoint import checkpoint_view
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;o=bpy.data.objects[B['geometry'][0]['name']];s.cycles.samples=24 if mode=='reflection'else 8;s.render.resolution_x=1100;s.render.resolution_y=850;s.camera.data.clip_start=.0001
mat=bpy.data.materials.new('Temporary geometry review '+mode);mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.35,.35,.35,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.17 if mode=='reflection'else .45;s.view_layers[0].material_override=mat
views=[('rear-mouth-normal',(0,0,-.190),(0,0,0),False,75)]
if'--view'in args:views=[q for q in views if q[0]==args[args.index('--view')+1]]
out=Path('/workspace/wewa-assets/work-in-progress/engine-intake-sleeve')/sha(source)[:12]/mode/'rear-control';report={'source_sha256':sha(source),'export_sha256':E['sha256'],'camera_calibrated':False,'isolated_unmounted':True,'views':[],'art_accepted':False}
for name,position,aim,crop,lens in views:
 key=bpy.data.objects['CONTROL_KEY'];key.location=(.035,-.045,-.080);key.data.energy=.25;key.data.size=.10;key.rotation_euler=(Vector(aim)-key.location).to_track_quat('-Z','Y').to_euler()
 s.camera.location=position;s.camera.rotation_euler=(Vector(aim)-Vector(position)).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;bpy.context.view_layer.update();frame=check_component_camera(s,[o],allow_crop=crop,margin=.005)
 row={'name':name,'camera_preflight':frame,'rendered':False}
 if'--preflight-only'not in args:row['outputs']=checkpoint_view(s,out,source,name)['outputs'];row['rendered']=True
 report['views'].append(row);out.mkdir(parents=True,exist_ok=True);(out/('camera-preflight.json'if'--preflight-only'in args else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==B['source_sha256']
