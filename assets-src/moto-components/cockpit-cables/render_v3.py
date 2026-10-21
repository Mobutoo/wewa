"""Actual unchanged black pigtail finish, neutral current context; lower two protected."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/cockpit-cables-v3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=json.loads((H/'render-inputs-v3.json').read_text());B=json.loads((H/'build-report-v3.json').read_text())
for k in ['source','export','connector_guide','instruments_guide']:assert sha(R/P[k])==P[k+'_sha256']
source=R/P['source'];assert sha(source)==B['source_sha256']
E=json.loads((O/'export-check.json').read_text());assert E['glTF_errors']==0
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[]
preview='--preview'in args;preflight='--preflight-only'in args
sys.path.insert(0,str(H));from camera_preflight_v3 import check_component_camera
from render_checkpoint_v3 import checkpoint_view
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
s.cycles.samples=24 if preview else 96
s.render.resolution_x=1100 if preview else 1440;s.render.resolution_y=850 if preview else 1080
s.camera.data.clip_start=.0001
C=bpy.data.collections['WEWA_COCKPIT_CABLES_PARTIAL'];loop=bpy.data.objects[P['loop_object']]
for o in list(C.all_objects):o.hide_render=o!=loop
G=bpy.data.collections['CABLES_V3_OWN_WORLD_SNAPSHOTS_NOT_EXPORTED'];G.hide_viewport=False;G.hide_render=False
for g in G.objects:g.hide_render=g['snapshot_group']=='instruments'
guide=bpy.data.materials.new('Neutral context only - no finish reception');guide.use_nodes=True
p=guide.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.18,.18,.18,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.5
actual=[]
for key in ['connector','instruments']:
    with bpy.data.libraries.load(str(R/P[key+'_guide']),link=False)as(a,l):l.collections=[P[key+'_collection']]
    c=l.collections[0];s.collection.children.link(c);c.hide_render=False;c.hide_viewport=False
    local=list(c.all_objects);assert all(o is not None for o in local)
    for o in local:
        if o.type=='MESH':
            o.hide_render=False;o.data.materials.clear();o.data.materials.append(guide);actual.append(o)
s.frame_set(1);bpy.context.view_layer.update()
target=Vector((.04,-.10,.025))
for name,pos,power,size in [('CONTROL_KEY',(.16,.08,.28),.7,.20),('CONTROL_FILL',(-.18,-.17,.12),.4,.18),('CONTROL_EDGE',(.18,-.26,.05),.4,.16),('CONTROL_UNDER_FILL',(.08,-.20,-.14),.4,.16)]:
    light=bpy.data.objects.get(name)
    if light is None:
        data=bpy.data.lights.new(name,'AREA');data.shape='DISK';light=bpy.data.objects.new(name,data);s.collection.objects.link(light)
    light.location=pos;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=power;light.data.size=size
views=[('loop-current-under-context',(.14,-.27,-.12),(.05,-.10,0),65),
       ('wireentry-gap-current',(.231,-.284,.017),(.069,-.116,.003),200)]
if'--view'in args:views=[q for q in views if q[0]==args[args.index('--view')+1]]
out=Path('/workspace/wewa-assets/work-in-progress/cockpit-cables-v3')/sha(source)[:12]/'native24'if preview else O
report={'source_sha256':sha(source),'export_sha256':P['export_sha256'],'samples':s.cycles.samples,
        'actual_context_inputs':P,'two_lower_meshes_protected_not_rerendered':True,
        'camera_calibrated':False,'views':[],'art_accepted':False}
for name,pos,aim,lens in views:
    s.camera.location=pos;s.camera.rotation_euler=(Vector(aim)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens
    bpy.context.view_layer.update();shown=[loop]+[g for g in G.objects if not g.hide_render]+actual
    frame=check_component_camera(s,shown,allow_crop=True,margin=.005)
    row={'name':name,'camera_preflight':frame,'rendered':False}
    if not preflight:row['outputs']=checkpoint_view(s,out,source,name)['outputs'];row['rendered']=True
    report['views'].append(row);out.mkdir(parents=True,exist_ok=True)
    (out/('camera-preflight.json'if preflight else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
for k in ['source','export','connector_guide','instruments_guide']:assert sha(R/P[k])==P[k+'_sha256']
