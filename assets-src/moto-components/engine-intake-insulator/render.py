"""Uncalibrated component control views; source never saved or repositioned."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=H/'engine-intake-insulator-v1.blend';build=json.loads((H/'build-report.json').read_text())
ex=json.loads((R/'creative/reviews/engine-intake-insulator-v1/export-check.json').read_text())
assert sha(source)==build['source_sha256']==ex['source_sha256'];assert sha(H/'engine-intake-insulator-inspection.glb')==ex['sha256']and ex['glTF_errors']==0
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[]
preview='--preview'in args;native='--native24'in args
mode='gray'if'--gray'in args else'reflection'if'--reflection'in args else'PBR'
out=Path('/workspace/wewa-assets/work-in-progress/engine-intake-insulator')/sha(source)[:12]/mode/('native24'if native else'preview8')if preview else R/'creative/reviews/engine-intake-insulator-v1'
sys.path.insert(0,str(H));from render_checkpoint import checkpoint_view
from camera_preflight import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;body=bpy.data.objects[build['geometry'][0]['name']];datum=body.parent
guides=bpy.data.collections['INTAKE_INSULATOR_IMMUTABLE_HEAD_GUIDE'];guides.hide_viewport=False;bpy.context.view_layer.update()
head=next(o for o in guides.objects if o.type=='MESH')
s.cycles.samples=24 if native else 8 if preview else 96
s.render.resolution_x=1100 if native or not preview else 850
s.render.resolution_y=850 if native or not preview else 657;s.camera.data.clip_start=.0005
if preview and mode!='PBR':
    m=bpy.data.materials.new('Temporary insulator diagnostic '+mode);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(.35,.35,.35,1);p.inputs['Roughness'].default_value=.16 if mode=='reflection'else .45
    p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;s.view_layers[0].material_override=m
point=datum.matrix_world@Vector((0,0,.002));rot=datum.matrix_world.to_3x3()
for name,offset,energy,size in [('CONTROL_KEY',(.04,-.10,.10),.35,.08),('CONTROL_FILL',(-.09,.04,.07),.20,.07),('CONTROL_EDGE',(.05,.07,-.03),.20,.045)]:
    o=bpy.data.objects[name];o.location=point+rot@Vector(offset);o.data.energy=energy;o.data.size=size
    o.rotation_euler=(point-o.location).to_track_quat('-Z','Y').to_euler()
views=[('front-face',(.010,.015,.20),(0,0,.002),False,False),
       ('front-quarter',(.08,-.10,.14),(0,0,.002),False,False),
       ('estimated-reverse',(-.01,-.02,-.20),(0,0,.002),False,False),
       ('groove-ear-detail',(.015,-.01,.070),(.012,0,.004),False,True),
       ('conditional-head-context',(.24,.32,.20),None,True,False)]
if'--view'in args:
    wanted=args[args.index('--view')+1];views=[v for v in views if v[0]==wanted];assert views,wanted
report={'component_id':build['component_id'],'revision':build['revision'],'source_sha256':sha(source),'export_sha256':ex['sha256'],
        'samples':s.cycles.samples,'diagnostic_mode':mode,'actual_blender_render':True,'views':[],'cameras_calibrated':False,
        'flat_reverse_is_estimated':True,'all_dimensions_estimated':True,'art_accepted':False}
for name,offset,aim,context,detail in views:
    guides.hide_render=not context;head.hide_render=not context
    target=(Vector(tuple((min((o.matrix_world@v.co)[i]for o in [body,head]for v in o.data.vertices)+max((o.matrix_world@v.co)[i]for o in [body,head]for v in o.data.vertices))/2 for i in range(3)))if context else datum.matrix_world@Vector(aim))
    rotation=head.matrix_world.to_3x3()if context else rot
    s.camera.location=target+rotation@(Vector(offset)*1.3 if context else Vector(offset));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=65
    bpy.context.view_layer.update();frame=check_component_camera(s,[body,head]if context else[body],allow_crop=detail,margin=.005)
    if '--preflight-only'in args:
        report['views'].append({'name':name,'camera_preflight':frame,'no_render':True})
        (R/'creative/reviews/engine-intake-insulator-v1/camera-layout-preflight.json').write_text(json.dumps(report,indent=2)+'\n')
        continue
    cp=checkpoint_view(s,out,source,name);report['views'].append({'name':name,'camera_preflight':frame,'outputs':cp['outputs']})
    (out/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==build['source_sha256']
