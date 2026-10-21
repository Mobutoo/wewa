"""Separate observed molded cap/contact; estimated orientation and blind backs."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'engine-spark-cap-v1.blend';build=json.loads((H/'build-report.json').read_text());ex=json.loads((R/'creative/reviews/engine-spark-cap-v1/export-check.json').read_text());assert sha(source)==build['source_sha256']==ex['source_sha256'];assert sha(H/'engine-spark-cap-inspection.glb')==ex['sha256']and ex['glTF_errors']==0
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;mode='gray'if'--gray'in args else'reflection'if'--reflection'in args else'preview';out=Path('/workspace/wewa-assets/work-in-progress/engine-spark-cap')/sha(source)[:12]/mode if preview else R/'creative/reviews/engine-spark-cap-v1';out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(H));from render_checkpoint import checkpoint_view
from camera_preflight import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.cycles.samples=8 if preview else 96;s.render.resolution_x=850 if preview else 1100;s.render.resolution_y=657 if preview else 850;s.camera.data.clip_start=.0005;objects=[bpy.data.objects[x['name']]for x in build['geometry']];datum=objects[0].parent;guides=bpy.data.collections['SPARK_CAP_IMMUTABLE_GUIDES'];guides.hide_viewport=False;bpy.context.view_layer.update();head=next(o for o in guides.objects if o.type=='MESH'and o.name.startswith('Engine UG5'));plugobjects=[o for o in guides.objects if o.type=='MESH'and o!=head]
if preview and mode!='preview':
 m=bpy.data.materials.new('Temporary cap diagnostic '+mode);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.38,.38,.38,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.15 if mode=='reflection'else .45;s.view_layers[0].material_override=m
stage=bpy.data.collections['SPARK_CAP_STUDIO_NOT_EXPORTED'];target=datum.matrix_world@Vector((.053,0,0))
for name,offset,energy,size in [('CONTROL_KEY',(.06,-.09,.10),.40,.075),('CONTROL_FILL',(-.08,.07,.07),.25,.065),('CONTROL_EDGE',(.04,.08,.03),.30,.045)]:
 o=bpy.data.objects[name];o.location=target+datum.matrix_world.to_3x3()@Vector(offset);o.data.energy=energy;o.data.size=size;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
views=[('cap-quarter',(.09,.14,.11),(.053,0,0),False,False),('main-socket-mouth',(-.15,.035,.035),(.035,0,0),False,False),('short-port-contact',(.015,.105,.015),(.075,.006,0),False,True),('installed-context',(.30,-.34,.22),None,True,False)]
if '--view'in args:
 wanted=args[args.index('--view')+1];views=[v for v in views if v[0]==wanted];assert views,wanted
report={'component_id':build['component_id'],'revision':'engine-spark-cap-v1','source_sha256':sha(source),'export_sha256':ex['sha256'],'samples':s.cycles.samples,'actual_blender_render':True,'diagnostic_mode':mode if preview else'originalPBR','views':[],'no_HTlead_or_internal_electrical_mechanism':True,'all_dimensions_estimated':True,'art_accepted':False}
for name,offset,aim,context,detail in views:
 guides.hide_render=not context
 for o in plugobjects+[head]:o.hide_render=not context
 point=head.matrix_world@Vector((-.045,0,.048))if context else datum.matrix_world@Vector(aim);s.camera.location=point+datum.matrix_world.to_3x3()@Vector(offset);s.camera.rotation_euler=(point-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=65;bpy.context.view_layer.update();frame=check_component_camera(s,objects+plugobjects+[head]if context else objects,allow_crop=detail,margin=.005);cp=checkpoint_view(s,out,source,name);report['views'].append({'name':name,'context_head_plug':context,'camera_preflight':frame,'outputs':cp['outputs']});(out/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
