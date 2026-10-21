"""Isolated portable material-control views, no tightened or complete clamp implied."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-clamp-band-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'build-report.json').read_text());source=H/'engine-intake-clamp-band-v1.blend';assert sha(source)==B['source_sha256'];E=json.loads((O/'export-check.json').read_text());assert E['glTF_errors']==0 and E['source_sha256']==sha(source);sys.path.insert(0,str(H));from camera_preflight import check_component_camera
from render_checkpoint import checkpoint_view
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;preflight='--preflight-only'in args;bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;o=bpy.data.objects[B['geometry'][0]['name']];s.cycles.samples=24 if preview else 96;s.render.resolution_x=1100 if preview else 1440;s.render.resolution_y=850 if preview else 1080;s.camera.data.clip_start=.0001;lights={q.name:(q.matrix_world.copy(),q.data.energy,q.data.size)for q in s.objects if q.type=='LIGHT'}
views=[('front-quarter',(.105,-.130,.105),(0,-.004,0),False,65),('opposite-quarter',(-.105,.130,.105),(0,-.004,0),False,65),('lug-fold-and-hole-detail',(.070,-.085,.045),(0,-.026,0),True,130),('inner-band-contact-detail',(.015,0,.040),(0,.0228,0),True,110),('finish-raking-control',(.015,0,.040),(0,.0228,0),True,110)]
if preview:views=[q for q in views if q[0]!='opposite-quarter']
if'--view'in args:views=[q for q in views if q[0]==args[args.index('--view')+1]]
out=Path('/workspace/wewa-assets/work-in-progress/engine-intake-clamp-band')/sha(source)[:12]/'pbr/native24'if preview else O;report={'source_sha256':sha(source),'export_sha256':E['sha256'],'samples':s.cycles.samples,'camera_calibrated':False,'isolated_unmounted':True,'assembly_incomplete_screw_bridge_separate':True,'views':[],'art_accepted':False}
for name,position,aim,crop,lens in views:
 for n,(matrix,power,size)in lights.items():q=bpy.data.objects[n];q.matrix_world=matrix.copy();q.data.energy=power;q.data.size=size
 if name=='finish-raking-control':
  key=bpy.data.objects['CONTROL_KEY'];key.location=(.07,.015,.006);key.rotation_euler=(Vector(aim)-key.location).to_track_quat('-Z','Y').to_euler();key.data.size=.025
 s.camera.location=position;s.camera.rotation_euler=(Vector(aim)-Vector(position)).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;bpy.context.view_layer.update();frame=check_component_camera(s,[o],allow_crop=crop,margin=.005);row={'name':name,'camera_preflight':frame,'rendered':False}
 if not preflight:row['outputs']=checkpoint_view(s,out,source,name)['outputs'];row['rendered']=True
 report['views'].append(row);out.mkdir(parents=True,exist_ok=True);(out/('camera-preflight.json'if preflight else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==B['source_sha256']
