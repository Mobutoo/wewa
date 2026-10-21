"""Gray whole and two actual macros, then specular control; no source mutation."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/control-perch-clamp-bolt-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'build-report.json').read_text());source=H/'control-perch-clamp-bolt-v1.blend';assert sha(source)==B['source_sha256'];E=json.loads((O/'export-check.json').read_text());assert E['glTF_errors']==0 and E['source_sha256']==sha(source);sys.path.insert(0,str(H));from camera_preflight import check_component_camera
from render_checkpoint import checkpoint_view
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;mode='pbr';preflight='--preflight-only'in args;bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;objects=[bpy.data.objects[q['name']]for q in B['geometry']];s.cycles.samples=24 if preview else 96;s.render.resolution_x=1100 if preview else 1440;s.render.resolution_y=850 if preview else 1080;s.camera.data.clip_start=.0001
# Opposite-side key makes the negativeZ head face actually inspectable; initial gray protocol is retained separately.
for name,position,power,size in [('CONTROL_KEY',(-.04,.06,-.045),.0075,.05),('CONTROL_FILL',(-.04,.05,.06),.09,.06),('CONTROL_EDGE',(.08,.04,.02),.12,.03)]:
 light=bpy.data.objects[name];light.location=position;light.rotation_euler=(Vector((0,0,.004))-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=power;light.data.size=size
views=[('opposite-bearing-quarter',(-.045,.065,.045),(0,0,.007),False,60),('whole-bolt',(.045,-.065,-.030),(0,0,.007),False,60),('hex-cone-boundary-detail',(.019,-.027,-.017),(0,0,-.002),True,100),('thread-runout-detail',(.018,-.025,.012),(0,-.0025,.006),True,100)]
if preview:views=[q for q in views if q[0]!='opposite-bearing-quarter']
if'--view'in args:views=[q for q in views if q[0]==args[args.index('--view')+1]]
out=Path('/workspace/wewa-assets/work-in-progress/control-perch-clamp-bolt')/sha(source)[:12]/'pbr/native24'if preview else O;report={'source_sha256':sha(source),'export_sha256':B['export_sha256'],'samples':s.cycles.samples,'camera_calibrated':False,'views':[],'art_accepted':False}
for name,position,aim,crop,lens in views:
 s.camera.location=position;s.camera.rotation_euler=(Vector(aim)-Vector(position)).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;bpy.context.view_layer.update();frame=check_component_camera(s,objects,allow_crop=crop,margin=.005);row={'name':name,'camera_preflight':frame,'rendered':False}
 if not preflight:row['outputs']=checkpoint_view(s,out,source,name)['outputs'];row['rendered']=True
 report['views'].append(row);out.mkdir(parents=True,exist_ok=True);(out/('camera-preflight.json'if preflight else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==B['source_sha256']
