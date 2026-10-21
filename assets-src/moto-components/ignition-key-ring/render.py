"""Gray/reflection isolated ring and deliberate key-opening context, no source mutation."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/ignition-key-ring-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'build-report.json').read_text());source=H/'ignition-key-ring-v1.blend';assert sha(source)==B['source_sha256'];E=json.loads((O/'export-check.json').read_text());assert E['glTF_errors']==0 and E['source_sha256']==sha(source);sys.path.insert(0,str(H));from camera_preflight import check_component_camera
from render_checkpoint import checkpoint_view
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;mode='pbr';preflight='--preflight-only'in args;bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;objects=[bpy.data.objects[q['name']]for q in B['geometry']];M=Matrix(B['rest_keypivot_world_matrix']);G=bpy.data.collections['KEYRING_IMMUTABLE_WORLD_GEOMETRY_SNAPSHOTS_NOT_EXPORTED'];G.hide_viewport=False;s.cycles.samples=24 if preview else 96;s.render.resolution_x=1100 if preview else 1440;s.render.resolution_y=850 if preview else 1080;s.camera.data.clip_start=.0001
for name,pos,power,size in [('CONTROL_KEY',(.07,-.09,.12),.15,.10),('CONTROL_FILL',(-.06,.07,.09),.10,.08),('CONTROL_EDGE',(.06,.06,.03),.10,.07)]:
 o=bpy.data.objects[name];o.location=M@Vector(pos);o.rotation_euler=(M@Vector((0,0,.053))-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=power;o.data.size=size
views=[('whole-ring',(.060,.025,.080),(0,0,.053),False,65,False),('split-end-detail',(.016,.028,.066),(0,.0114,.0547),True,110,False),('two-turn-strip-profile',(.014,-.018,.075),(0,-.0115,.053),True,110,False),('key-opening-context',(.050,-.070,.090),(0,0,.045),True,75,True)]
if'--view'in args:views=[q for q in views if q[0]==args[args.index('--view')+1]]
out=Path('/workspace/wewa-assets/work-in-progress/ignition-key-ring')/sha(source)[:12]/'pbr/native24'if preview else O;report={'source_sha256':sha(source),'export_sha256':B['export_sha256'],'samples':s.cycles.samples,'camera_calibrated':False,'views':[],'art_accepted':False}
for name,pos,aim,crop,lens,context in views:
 G.hide_render=not context
 for g in G.objects:g.hide_render=not(context and g['source_object']in['Key black moulded head - estimated','Key metal blade - generic nonfunctional cut'])
 s.camera.location=M@Vector(pos);s.camera.rotation_euler=(M@Vector(aim)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;bpy.context.view_layer.update();shown=objects+[g for g in G.objects if context and not g.hide_render];frame=check_component_camera(s,shown,allow_crop=crop,margin=.005);row={'name':name,'camera_preflight':frame,'keycontext_snapshot_visible':context,'rendered':False}
 if not preflight:row['outputs']=checkpoint_view(s,out,source,name)['outputs'];row['rendered']=True
 report['views'].append(row);out.mkdir(parents=True,exist_ok=True);(out/('camera-preflight.json'if preflight else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==B['source_sha256']
