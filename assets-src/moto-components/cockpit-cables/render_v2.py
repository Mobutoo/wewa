"""Isolated changed loop and exact current-case context, without moving source interfaces."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'cockpit-cables-v2.blend';check=json.loads((H/'build-report-v2.json').read_text());ex=json.loads((R/'creative/reviews/cockpit-cables-v2/export-check.json').read_text());assert sha(source)==check['source_sha256']==ex['source_sha256'];assert sha(H/'cockpit-cables-v2-inspection.glb')==ex['sha256'];assert ex['glTF_errors']==0
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;mode='gray'if'--gray'in args else'reflection'if'--reflection'in args else'preview';out=Path('/workspace/wewa-assets/work-in-progress/cockpit-cables-v2')/sha(source)[:12]/mode if preview else R/'creative/reviews/cockpit-cables-v2';out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(H));from render_checkpoint_v2 import checkpoint_view
from camera_preflight_v2 import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.data.collections['CABLES_IMMUTABLE_INTERFACE_GUIDES'].hide_viewport=False;bpy.context.view_layer.update();s=bpy.context.scene;s.cycles.samples=8 if preview else 96;s.render.resolution_x=850 if preview else 1100;s.render.resolution_y=700 if preview else 850;s.camera.data.clip_start=.001;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False
objects=list(bpy.data.collections['WEWA_COCKPIT_CABLES_PARTIAL'].objects);loop=next(o for o in objects if'ignition'in o.name.lower());bpy.data.collections['CABLES_IMMUTABLE_INTERFACE_GUIDES'].hide_render=True
# Exact evaluated copies in this unsaved review scene. Linked libraries and matrices unchanged.
context=bpy.data.collections.new('CURRENT_CASE_CONTEXT_RAM_ONLY');s.collection.children.link(context);context_objects=[];dg=bpy.context.evaluated_depsgraph_get()
for name in ['Shaped central cluster cover','Ignition ribbed hollow housing and mounting ears - candidate']:
 original=bpy.data.objects[name];evaluated=original.evaluated_get(dg);mesh=bpy.data.meshes.new_from_object(evaluated,depsgraph=dg);copy=bpy.data.objects.new('Context exact copy - '+name,mesh);copy.matrix_world=original.matrix_world.copy();context.objects.link(copy);context_objects.append(copy)
if preview and mode!='preview':
 mat=bpy.data.materials.new('Temporary '+mode);mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.38,.38,.38,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.15 if mode=='reflection'else .45;s.view_layers[0].material_override=mat
stage=bpy.data.collections['CABLES_STUDIO_NOT_EXPORTED'];light_offsets={o.name:o.location-Vector((.105,-.22,-.54))for o in stage.objects if o.type=='LIGHT'}
for o in stage.objects:
 if o.type=='LIGHT':o.data.energy*=.08
views=[('ignition-pigtail-free-end',False,(.14,.18,.14),70),('ignition-interface-current',True,(.25,.23,-.17),65)]
if'--view'in args:
 wanted=args[args.index('--view')+1];views=[v for v in views if v[0]==wanted];assert views,wanted
report={'component_id':'MOTO-COCKPIT-CABLES-001','revision':'cockpit-cables-v2','source_sha256':sha(source),'export_sha256':ex['sha256'],'samples':s.cycles.samples,'actual_blender_render':True,'diagnostic_material':mode if preview else'originalPBR','unchanged_lower_sheaths_not_rerendered':True,'all_dimensions_estimated':True,'art_accepted':False,'views':[]}
for name,showcontext,offset,lens in views:
 for o in objects:o.hide_render=o!=loop
 for o in context_objects:o.hide_render=not showcontext
 shown=[loop]+(context_objects if showcontext else[]);points=[o.matrix_world@Vector(v)for o in shown for v in o.bound_box];target=Vector([(min(p[i]for p in points)+max(p[i]for p in points))/2 for i in range(3)])
 for o in stage.objects:
  if o.type=='MESH':o.hide_render=showcontext;o.location.z=min(p.z for p in points)-.003
  if o.type=='LIGHT':o.location=target+light_offsets[o.name];o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 s.camera.location=target+Vector(offset);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;bpy.context.view_layer.update();frame=check_component_camera(s,shown,allow_crop=False,margin=.005);cp=checkpoint_view(s,out,source,name);report['views'].append({'name':name,'shown_objects':[o.name for o in shown],'camera_preflight':frame,'context_case_world_matrices_unchanged':True,'outputs':cp['outputs']});(out/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
