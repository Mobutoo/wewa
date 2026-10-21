"""Photograph-like camera roll in the part frame; never reposition the casting."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];source=H/'engine-intake-manifold-v1.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=json.loads((H/'build-report.json').read_text())
ex=json.loads((R/'creative/reviews/engine-intake-manifold-v1/export-check.json').read_text())
assert sha(source)==build['source_sha256']==ex['source_sha256'];assert sha(H/'engine-intake-manifold-inspection.glb')==ex['sha256']and ex['glTF_errors']==0
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;mode='gray'if'--gray'in args else'reflection'if'--reflection'in args else'PBR';native='--native24'in args
sys.path.insert(0,str(H));from render_checkpoint import checkpoint_view
from camera_preflight import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;body=bpy.data.objects[build['geometry'][0]['name']];datum=body.parent;rot=datum.matrix_world.to_3x3()
s.cycles.samples=24 if native else 8 if preview else 96
s.render.resolution_x=1100 if native or not preview else 850;s.render.resolution_y=850 if native or not preview else 657;s.camera.data.clip_start=.0005
if preview and mode!='PBR':
    mat=bpy.data.materials.new('Temporary manifold geometric control '+mode);mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.34,.34,.34,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.18 if mode=='reflection'else .45;s.view_layers[0].material_override=mat
target=datum.matrix_world@Vector((0,0,.020))
for name,offset,energy,size in [('CONTROL_KEY',(-.06,-.09,.11),.4,.08),('CONTROL_FILL',(.08,.05,.06),.25,.07),('CONTROL_EDGE',(-.04,.07,.03),.25,.05)]:
    o=bpy.data.objects[name];o.location=target+rot@Vector(offset);o.data.energy=energy;o.data.size=size;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
views=[('reference-like-quarter',(-.10,-.13,.10),(0,0,.019),False),('opposite-quarter',(.11,.12,.10),(0,0,.019),False),('mouth-bands-detail',(-.035,-.065,.055),(0,0,.029),True),('estimated-base-reverse',(.02,-.05,-.19),(0,0,.010),False)]
if'--view'in args:
    wanted=args[args.index('--view')+1];views=[v for v in views if v[0]==wanted];assert views
out=Path('/workspace/wewa-assets/work-in-progress/engine-intake-manifold')/sha(source)[:12]/mode/('native24'if native else'preview8')if preview else R/'creative/reviews/engine-intake-manifold-v1'
report={'source_sha256':sha(source),'export_sha256':ex['sha256'],'geometry_stage_only':False,'component_id':build['component_id'],'revision':build['revision'],'mode':mode,'samples':s.cycles.samples,'camera_calibrated':False,'views':[],'art_accepted':False}
for name,offset,aim,detail in views:
    target=datum.matrix_world@Vector(aim);s.camera.location=target+rot@Vector(offset);forward=(target-s.camera.location).normalized();up=rot@Vector((0,0,1))
    if abs(forward.dot(up))>.95:up=rot@Vector((0,1,0))
    right=forward.cross(up).normalized();vertical=right.cross(forward).normalized();s.camera.rotation_euler=Matrix(((right.x,vertical.x,-forward.x),(right.y,vertical.y,-forward.y),(right.z,vertical.z,-forward.z))).to_euler();s.camera.data.lens=65
    bpy.context.view_layer.update();frame=check_component_camera(s,[body],allow_crop=detail,margin=.005)
    if'--preflight-only'in args:report['views'].append({'name':name,'camera_preflight':frame,'rendered':False})
    else:
        cp=checkpoint_view(s,out,source,name);report['views'].append({'name':name,'camera_preflight':frame,'outputs':cp['outputs']})
    out.mkdir(parents=True,exist_ok=True);(out/('camera-layout-preflight.json'if'--preflight-only'in args else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==build['source_sha256']
