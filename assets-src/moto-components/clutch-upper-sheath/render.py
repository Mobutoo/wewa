"""Representative black short sheath, same G3 cameras and conditional context; no source mutation."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/clutch-upper-sheath-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'build-report.json').read_text());source=H/'clutch-upper-sheath-v1.blend';assert sha(source)==B['source_sha256'];E=json.loads((O/'export-check.json').read_text());assert E['glTF_errors']==0 and E['source_sha256']==sha(source);sys.path.insert(0,str(H));from camera_preflight import check_component_camera
from render_checkpoint import checkpoint_view
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;mode='pbr';preflight='--preflight-only'in args;bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;objects=[bpy.data.objects[q['name']]for q in B['geometry']];G=bpy.data.collections['CLUTCH_UPPER_IMMUTABLE_WORLD_SNAPSHOTS_NOT_EXPORTED'];G.hide_viewport=False;s.cycles.samples=24 if preview else 96;s.render.resolution_x=1100 if preview else 1440;s.render.resolution_y=850 if preview else 1080;s.camera.data.clip_start=.0001
S=Vector(B['centreline_first_world_m']);E=Vector(B['centreline_last_REVIEW_CUT_world_m']);T=Vector(B['first_tangent_world']);Te=Vector(B['last_tangent_world']);middle=(S+E)/2;up=Vector((0,0,1));views=[('whole-short-departure',(.26,-.24,.27),tuple(middle),False,65,False),('control-gap-context',tuple(S-T*.080+up*.045),tuple(S+T*.008),True,85,True),('bend-profile',(.165,-.115,.145),(.153,-.070,.104),True,110,False),('distal-REVIEW-CUT-not-terminal',tuple(E+Te*.025+up*.014),tuple(E),True,110,False)]
if'--view'in args:views=[q for q in views if q[0]==args[args.index('--view')+1]]
out=Path('/workspace/wewa-assets/work-in-progress/clutch-upper-sheath')/sha(source)[:12]/'pbr/native24'if preview else O;report={'source_sha256':sha(source),'export_sha256':B['export_sha256'],'samples':s.cycles.samples,'camera_calibrated':False,'complete_Bowden_cable_created':False,'views':[],'art_accepted':False}
for name,pos,aim,crop,lens,context in views:
 G.hide_render=not context
 for g in G.objects:g.hide_render=not(context and g['source_object']in['Clutch cast perch - fixed candidate','Clutch hollow cable barrel adjuster','Clutch adjuster locknut'])
 s.camera.location=pos;s.camera.rotation_euler=(Vector(aim)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;bpy.context.view_layer.update();shown=objects+[g for g in G.objects if context and not g.hide_render];frame=check_component_camera(s,shown,allow_crop=crop,margin=.005);row={'name':name,'camera_preflight':frame,'conditional_control_context':context,'rendered':False}
 if not preflight:row['outputs']=checkpoint_view(s,out,source,name)['outputs'];row['rendered']=True
 report['views'].append(row);out.mkdir(parents=True,exist_ok=True);(out/('camera-preflight.json'if preflight else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==B['source_sha256']
