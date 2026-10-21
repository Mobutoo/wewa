"""Three gray checks, then an explicitly separate whole-cockpit existing-material study."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/cockpit-updated-review-v4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=json.loads((O/'source-geometry-check.json').read_text());source=H/'cockpit-updated-review-v4.blend';assert sha(source)==B['source_sha256']
for row in B['linked_sources']:assert sha(R/row['source'])==row['sha256']
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];material='--material'in args;preflight_only='--preflight-only'in args
if material:assert json.loads((O/'gray-actual-read.json').read_text())['all_three_actually_opened']
sys.path.insert(0,str(H.parent/'ignition-connector'));from camera_preflight import check_component_camera
from render_checkpoint import checkpoint_view
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24 if material else 8;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Original neutral studio context');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.14,.14,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
cam=bpy.data.objects.new('Estimated rider review camera',bpy.data.cameras.new('Estimated rider review camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_start=.001;cam.data.clip_end=50
for name,pos,power,size in [('Neutral key',(1.4,1.8,2.0),400,2.0),('Neutral fill',(-1.6,.5,1.2),220,2.0),('Neutral edge',(.6,-1.5,1.3),260,1.4),('Under controls fill',(0,-.5,-.15),25,.7)]:
 d=bpy.data.lights.new(name,'AREA');d.shape='DISK';d.energy=power;d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.12))-o.location).to_track_quat('-Z','Y').to_euler()
if not material:
 gray=bpy.data.materials.new('Temporary diffuse gray form override - sources unchanged');gray.use_nodes=True;p=gray.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.22,.22,.22,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.5;s.view_layers[0].material_override=gray
objects=[o for o in s.objects if o.type=='MESH'and not o.hide_render]
assert len(objects)>200
views=[('whole-rider-cockpit',(0,1.15,.70),(0,-.03,.13),45),('upper-control-departures',(0,.85,.45),(0,.025,.100),75),('key-contact-connector',(.04,.82,.44),(.025,-.08,.02),140)]
if material:views=views[:1]
if'--view'in args:views=[q for q in views if q[0]==args[args.index('--view')+1]]
mode='existing-material24'if material else'gray8';out=O/mode;out.mkdir(parents=True,exist_ok=True);report={'source_sha256':sha(source),'mode':mode,'samples':s.cycles.samples,'linked_source_count':len(B['linked_sources']),'linked_sources':B['linked_sources'],'camera_is_estimated':True,'views':[],'art_accepted':False,'physical_iphone_tested':False}
for name,pos,aim,lens in views:
 cam.location=pos;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;bpy.context.view_layer.update()
 # Cropping long lower sheaths and unrelated controls is intentional in cockpit/macros;
 # no near/far clipping is permitted for any rendered object.
 pre=check_component_camera(s,objects,allow_crop=True,margin=.005)
 row={'name':name,'camera_preflight':pre,'rendered':False}
 if name=='whole-rider-cockpit':
  critical=[o for o in objects if not o.name.startswith('Visible descending front sheath')]
  row['whole_cockpit_critical_components_in_frame']=check_component_camera(s,critical,allow_crop=False,margin=.005)
 if not preflight_only:row['outputs']=checkpoint_view(s,out,source,name)['outputs'];row['rendered']=True
 report['views'].append(row);(out/('camera-preflight.json'if preflight_only else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
for row in B['linked_sources']:assert sha(R/row['source'])==row['sha256']
assert sha(source)==B['source_sha256']
print('COCKPIT_CURRENT_REVIEW_COMPLETE',mode)
