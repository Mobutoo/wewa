"""Estimated section-control cameras, actual evaluated extents before rendering."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'exhaust-silencer-body-v1-geometry.blend';b=json.loads((H/'geometry-report.json').read_text());e=json.loads((R/'creative/reviews/exhaust-silencer-body-v1/geometry-export-check.json').read_text());assert sha(source)==b['source_sha256']==e['source_sha256']and sha(H/'exhaust-silencer-body-v1-geometry.glb')==e['sha256']and e['glTF_errors']==0
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];native='--native24'in args;mode='reflection'if'--reflection'in args else'gray';sys.path.insert(0,str(H));from render_checkpoint import checkpoint_view
from camera_preflight import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;o=bpy.data.objects[b['geometry'][0]['name']];guides=bpy.data.collections['SILENCER_BODY_IMMUTABLE_GUIDES'];guides.hide_viewport=False;bpy.context.view_layer.update();keepouts=[q for q in guides.all_objects if q.type=='MESH'];target=Vector(tuple((min((o.matrix_world@v.co)[i]for v in o.data.vertices)+max((o.matrix_world@v.co)[i]for v in o.data.vertices))/2 for i in range(3)));front=o.parent.matrix_world.translation.copy();end=Vector((front.x,1.045,-.754))
s.cycles.samples=24 if native else 8;s.render.resolution_x=1100 if native else 1000;s.render.resolution_y=850 if native else 773;s.camera.data.clip_start=.0005;mat=bpy.data.materials.new('Temporary casing '+mode+' control');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.35,.35,.35,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.17 if mode=='reflection'else .45;s.view_layers[0].material_override=mat
for name,offset,energy,size in [('CONTROL_KEY',(-.55,-.55,.65),12,.6),('CONTROL_FILL',(.45,.35,.3),7,.5),('CONTROL_EDGE',(-.3,.5,-.1),9,.4)]:
 light=bpy.data.objects[name];light.location=target+Vector(offset);light.data.energy=energy;light.data.size=size;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
views=[('right-profile',target+Vector((-2,0,0)),target,True,False,False,65,.80),('rear-quarter',target+Vector((-.8,.9,.35)),target,False,False,False,65,.80),('front-neck-detail',front+Vector((-.55,-.7,.2)),front+Vector((0,.08,.005)),False,False,True,200,.80),('rear-wall-detail',end+Vector((-.25,.8,.15)),end,False,False,True,180,.80),('conditional-header-context',Vector((-1.2,1.2,.0)),Vector((-.1,.45,-.65)),False,True,False,42,1.25)]
if'--view'in args:
 wanted=args[args.index('--view')+1];views=[v for v in views if v[0]==wanted];assert views
out=Path('/workspace/wewa-assets/work-in-progress/exhaust-silencer-body')/sha(source)[:12]/mode/('native24'if native else'preview8');r={'source_sha256':sha(source),'export_sha256':e['sha256'],'samples':s.cycles.samples,'diagnostic_mode':mode,'camera_calibrated':False,'all_dimensions_estimated':True,'views':[],'art_accepted':False}
for name,position,aim,ortho,context,crop,lens,width in views:
 guides.hide_render=not context;s.camera.location=position;s.camera.rotation_euler=(aim-position).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO'if ortho else'PERSP';s.camera.data.ortho_scale=width;s.camera.data.lens=lens;bpy.context.view_layer.update();frame=check_component_camera(s,[o]+(keepouts if context else[]),allow_crop=crop,margin=.005)
 if'--preflight-only'in args:r['views'].append({'name':name,'camera_preflight':frame,'rendered':False})
 else:
  cp=checkpoint_view(s,out,source,name);r['views'].append({'name':name,'camera_preflight':frame,'outputs':cp['outputs']})
 out.mkdir(parents=True,exist_ok=True);(out/('camera-layout-preflight.json'if'--preflight-only'in args else'render-report.json')).write_text(json.dumps(r,indent=2)+'\n')
assert sha(source)==b['source_sha256']
