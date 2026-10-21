from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'geometry-report.json').read_text());source=H/'engine-intake-clamp-band-v1-geometry.blend';assert sha(source)==B['source_sha256'];E=json.loads((R/'creative/reviews/engine-intake-clamp-band-v1/geometry-export-check.json').read_text());assert E['glTF_errors']==0 and E['source_sha256']==sha(source);sys.path.insert(0,str(H));from camera_preflight import check_component_camera
from render_checkpoint import checkpoint_view
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];mode='reflection'if'--reflection'in args else'gray';bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;o=bpy.data.objects[B['geometry'][0]['name']];s.cycles.samples=24 if mode=='reflection'else 8;s.render.resolution_x=1100;s.render.resolution_y=850;s.camera.data.clip_start=.0001
mat=bpy.data.materials.new('Temporary formed band '+mode);mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.35,.35,.35,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.17 if mode=='reflection'else .45;s.view_layers[0].material_override=mat
views=[('front-quarter',(.105,-.130,.105),(0,-.004,0),False,65),('opposite-quarter',(-.105,.130,.105),(0,-.004,0),False,65),('lug-fold-and-hole-detail',(.070,-.085,.045),(0,-.026,0),True,130),('inner-band-contact-detail',(.030,.015,.120),(0,.012,0),True,130)]
if'--view'in args:views=[q for q in views if q[0]==args[args.index('--view')+1]]
out=Path('/workspace/wewa-assets/work-in-progress/engine-intake-clamp-band')/sha(source)[:12]/mode;report={'source_sha256':sha(source),'export_sha256':E['sha256'],'camera_calibrated':False,'isolated_unmounted':True,'assembly_incomplete_screw_and_bridge_separate':True,'views':[],'art_accepted':False}
for name,position,aim,crop,lens in views:
 s.camera.location=position;s.camera.rotation_euler=(Vector(aim)-Vector(position)).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;bpy.context.view_layer.update();frame=check_component_camera(s,[o],allow_crop=crop,margin=.005);row={'name':name,'camera_preflight':frame,'rendered':False}
 if'--preflight-only'not in args:row['outputs']=checkpoint_view(s,out,source,name)['outputs'];row['rendered']=True
 report['views'].append(row);out.mkdir(parents=True,exist_ok=True);(out/('camera-preflight.json'if'--preflight-only'in args else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==B['source_sha256']
