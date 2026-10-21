"""Four useful isolated native material views; estimated route context is separate."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Matrix,Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/ignition-connector-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=json.loads((H/'build-report-v2.json').read_text());I=json.loads((H/'current-context-inputs-v2.json').read_text())
source=H/'ignition-connector-v2.blend';assert sha(source)==B['source_sha256']
assert sha(H/'ignition-connector-v2-inspection.glb')==B['export_sha256']
assert json.loads((O/'export-check-v2.json').read_text())['glTF_errors']==0
for key in ['pigtail','instruments']:assert sha(R/I[key+'_source'])==I[key+'_source_sha256']
sys.path.insert(0,str(H));from camera_preflight import check_component_camera
from render_checkpoint import checkpoint_view
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[]
preview='--preview'in args;preflight='--preflight-only'in args
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.cycles.samples=24 if preview else 96
s.render.resolution_x=1100 if preview else 1440;s.render.resolution_y=850 if preview else 1080;s.camera.data.clip_start=.0001
body=bpy.data.objects[B['geometry'][0]['name']];M=Matrix(B['conditional_root_world_matrix'])
G=bpy.data.collections['CONNECTOR_OWN_WORLD_SNAPSHOTS_NOT_EXPORTED'];G.hide_render=True
for q in list(G.all_objects):q.hide_render=True
context=[]
gray=bpy.data.materials.new('Neutral current context only');gray.use_nodes=True;p=gray.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.18,.18,.18,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.5
for key in ['pigtail','instruments']:
    with bpy.data.libraries.load(str(R/I[key+'_source']),link=False)as(a,l):l.collections=[I[key+'_collection']]
    c=l.collections[0];s.collection.children.link(c);c.hide_render=False;c.hide_viewport=False
    for q in list(c.all_objects):
        if q.type=='MESH':
            q.hide_render=True
            if key=='pigtail' and q.name!='Visible ignition pigtail loop - connector omitted - free end':continue
            if key=='instruments':q.data.materials.clear();q.data.materials.append(gray)
            context.append(q)
target=Vector((.04,-.10,.025))
for name,pos,power,size in [('CONTROL_KEY',(.16,.08,.28),.7,.20),('CONTROL_FILL',(-.18,-.17,.12),.4,.18),('CONTROL_EDGE',(.18,-.26,.05),.4,.16),('CONTROL_UNDER_FILL',(.08,-.20,-.14),.4,.16)]:
    light=bpy.data.objects.get(name)
    if light is None:
        data=bpy.data.lights.new(name,'AREA');data.shape='DISK';light=bpy.data.objects.new(name,data);s.collection.objects.link(light)
    light.location=pos;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=power;light.data.size=size
views=[('whole-housing',(.055,.065,.045),(0,0,0),False,65,False),('empty-mouth-not-contacts',(0,0,-.090),(0,0,-.010),False,85,False),('wire-shoulder-context',(.13,.18,.18),(0,0,.008),True,160,True),('retaining-surface-control',(.028,.050,-.010),(0,.005,-.005),True,90,False)]
if'--view'in args:views=[v for v in views if v[0]==args[args.index('--view')+1]]
out=Path('/workspace/wewa-assets/work-in-progress/ignition-connector')/sha(source)[:12]/'native24'if preview else O
report={'source_sha256':sha(source),'export_sha256':B['export_sha256'],'samples':s.cycles.samples,'actual_context_inputs':I,'camera_calibrated':False,'views':[],'art_accepted':False}
for name,pos,aim,crop,lens,usecontext in views:
    for q in context:q.hide_render=not usecontext
    s.camera.location=M@Vector(pos);s.camera.rotation_euler=(M@Vector(aim)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens
    bpy.context.view_layer.update();frame=check_component_camera(s,[body]+(context if usecontext else[]),allow_crop=crop,margin=.005)
    row={'name':name,'camera_preflight':frame,'rendered':False}
    if not preflight:row['outputs']=checkpoint_view(s,out,source,name)['outputs'];row['rendered']=True
    report['views'].append(row);out.mkdir(parents=True,exist_ok=True);(out/('camera-preflight-v2.json'if preflight else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
for key in ['pigtail','instruments']:assert sha(R/I[key+'_source'])==I[key+'_source_sha256']
assert sha(source)==B['source_sha256']
