"""Gray/reflection of the explicit first conditional placement, including a failed context."""
from pathlib import Path
import bpy, json, hashlib, sys
from mathutils import Matrix, Vector
H=Path(__file__).resolve().parent; R=H.parents[2]
O=R/'creative/reviews/ignition-connector-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=json.loads((H/'geometry-report-v2.json').read_text())
source=H/'ignition-connector-v2-geometry.blend'
assert sha(source)==B['source_sha256']
E=json.loads((O/'geometry-export-check.json').read_text())
assert E['glTF_errors']==0 and E['source_sha256']==sha(source)
sys.path.insert(0,str(H))
from camera_preflight import check_component_camera
from render_checkpoint import checkpoint_view
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[]
mode='reflection'
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene; s.cycles.samples=24 if mode=='reflection'else 8
s.render.resolution_x=1100; s.render.resolution_y=850
s.camera.data.clip_start=.0001
objects=[bpy.data.objects[q['name']]for q in B['geometry']]
M=Matrix(B['conditional_root_world_matrix'])
G=bpy.data.collections['CONNECTOR_OWN_WORLD_SNAPSHOTS_NOT_EXPORTED'];G.hide_viewport=False
context_study=True
target=Vector((.04,-.10,.025))
for name,pos,power,size in [('CONTROL_KEY',(.16,.08,.28),.7,.20),('CONTROL_FILL',(-.18,-.17,.12),.4,.18),('CONTROL_EDGE',(.18,-.26,.05),.4,.16),('CONTROL_UNDER_FILL',(.08,-.20,-.14),.4,.16)]:
    light=bpy.data.objects.get(name)
    if light is None:
        data=bpy.data.lights.new(name,'AREA');data.shape='DISK';light=bpy.data.objects.new(name,data);s.collection.objects.link(light)
    light.location=pos;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=power;light.data.size=size
for g in G.objects:
    if g.type=='MESH':
        p=g.data.materials[0].node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.18,.18,.18,1);p.inputs['Metallic'].default_value=.85;p.inputs['Roughness'].default_value=.24

INPUTS=json.loads((H/'current-context-inputs-v2.json').read_text())
for key in ['body','instruments','pigtail']:assert sha(R/INPUTS[key+'_source'])==INPUTS[key+'_source_sha256']
actual_collections=[];actual_objects=[]
for key in ['instruments','pigtail']:
    with bpy.data.libraries.load(str(R/INPUTS[key+'_source']),link=False)as(a,l):l.collections=[INPUTS[key+'_collection']]
    c=l.collections[0];s.collection.children.link(c);c.hide_render=False;c.hide_viewport=False;actual_collections.append(c)
    local_objects=list(c.all_objects);assert all(q is not None for q in local_objects)
    actual_objects+=local_objects
    for q in local_objects:
        if q.type=='MESH':q.hide_render=key=='pigtail'and q.name!=INPUTS['pigtail_object']
s.frame_set(1);bpy.context.view_layer.update()
# Neutral geometry override uses the actual current surface normals, no texture or opacity imitation.
neutral=bpy.data.materials.new('Current source neutral geometry override');neutral.use_nodes=True
p=neutral.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.23,.23,.23,1);p.inputs['Metallic'].default_value=.85;p.inputs['Roughness'].default_value=.24
s.view_layers[0].material_override=neutral
for o in objects:
    p=o.data.materials[0].node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(.23,.23,.23,1)
    p.inputs['Metallic'].default_value=.85 if mode=='reflection'else 0
    p.inputs['Roughness'].default_value=.24 if mode=='reflection'else .48
views=[('whole-housing',(.055,.065,.045),(0,0,0),False,65,False),
       ('wire-shoulder-context',(.13,.18,.18),(0,0,.008),True,160,True),
       ('empty-mouth-not-contacts',(0,0,-.090),(0,0,-.010),False,85,False),
       ('retaining-like-projection',(.028,.050,-.010),(0,.005,-.005),True,90,False)]
if context_study:
    Mi=M.inverted()
    views=[('user-context',tuple(Mi@Vector((0,.85,.55))),tuple(Mi@Vector((0,-.03,.08))),False,45,True),('under-instrument-context',tuple(Mi@Vector((.14,-.27,-.12))),tuple(Mi@Vector((.05,-.10,0))),True,65,True)]
if'--view'in args:views=[q for q in views if q[0]==args[args.index('--view')+1]]
out=Path('/workspace/wewa-assets/work-in-progress/ignition-connector')/sha(source)[:12]/'reflection-current-instruments5-context'
report={'source_sha256':sha(source),'export_sha256':B['export_sha256'],
        'samples':s.cycles.samples,'conditional_context_rejected':not B['conditional_interfaces_passed'],
        'camera_calibrated':False,'actual_reference_sources':INPUTS,'views':[],'art_accepted':False}
for name,pos,aim,crop,lens,context in views:
    G.hide_render=not context
    for g in G.objects:
        g.hide_render=not(context and(context_study or g['snapshot_group']=='pigtail'or g['source_object']in[
            'Ignition ribbed hollow housing and mounting ears - candidate','Shaped central cluster cover']))
    for g in G.objects:
        if g.get('snapshot_group')in['instruments','pigtail']:g.hide_render=True
    s.camera.location=M@Vector(pos)
    s.camera.rotation_euler=(M@Vector(aim)-s.camera.location).to_track_quat('-Z','Y').to_euler()
    s.camera.data.lens=lens;bpy.context.view_layer.update()
    shown=objects+[g for g in G.objects if context and not g.hide_render]+[q for q in actual_objects if q.type=='MESH'and not q.hide_render]
    frame=check_component_camera(s,shown,allow_crop=crop,margin=.005)
    row={'name':name,'camera_preflight':frame,'context_is_rejected':context and not B['conditional_interfaces_passed'],
         'outputs':checkpoint_view(s,out,source,name)['outputs']}
    report['views'].append(row);out.mkdir(parents=True,exist_ok=True)
    (out/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==B['source_sha256']

for key in ['body','instruments','pigtail']:assert sha(R/INPUTS[key+'_source'])==INPUTS[key+'_source_sha256']
