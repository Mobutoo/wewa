"""CastOHCcoverbody isolated, metalstub remains separateunmade; interfaces candidateonly."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'engine-ohc-cover-v1.blend';build=json.loads((H/'build-report.json').read_text());ex=json.loads((R/'creative/reviews/engine-ohc-cover-v1/export-check.json').read_text());assert sha(source)==build['source_sha256']==ex['source_sha256'];assert sha(H/'engine-ohc-cover-inspection.glb')==ex['sha256'];assert ex['glTF_errors']==0
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;mode='gray'if'--gray'in args else'reflection'if'--reflection'in args else'preview';out=Path('/workspace/wewa-assets/work-in-progress/engine-ohc-cover')/sha(source)[:12]/('pbr-exposure-review'if mode=='preview'else mode) if preview else R/'creative/reviews/engine-ohc-cover-v1';out.mkdir(exist_ok=True,parents=True);sys.path.insert(0,str(H));from render_checkpoint import checkpoint_view
from camera_preflight import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.cycles.samples=8 if preview else 96;s.render.resolution_x=850 if preview else 1100;s.render.resolution_y=657 if preview else 850;s.camera.data.clip_start=.001;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.view_settings.exposure+=1.5 if mode=='preview'else 0;cap=bpy.data.objects['UG5 OHC cast cover body - conditional candidate']
if preview and mode!='preview':
 m=bpy.data.materials.new('Temporary cap diagnostic '+mode);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.38,.38,.38,1);p.inputs['Metallic'].default_value=1 if mode=='reflection'else 0;p.inputs['Roughness'].default_value=.15 if mode=='reflection'else .45;s.view_layers[0].material_override=m
stage=bpy.data.collections['OHC_COVER_STUDIO_NOT_EXPORTED'];oldtarget=sum([cap.matrix_world@Vector(v)for v in cap.bound_box],Vector())/8;target=cap.matrix_world@Vector((0,0,.005));lightoffset={o.name:o.location-oldtarget for o in stage.objects if o.type=='LIGHT'}
for o in stage.objects:
 if o.type=='LIGHT':o.location=target+lightoffset[o.name];o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 if o.type=='MESH':o.hide_render=True
views=[('front-quarter',(.18,-.22,.36),False),('front-normal',(0,0,.46),False),('rear-cavity',(.12,.18,-.44),False)]
if preview:views +=[('shoulder-ear-detail',(.08,-.05,.24),True)]
if'--view'in args:
 wanted=args[args.index('--view')+1];views=[v for v in views if v[0]==wanted];assert views,wanted
# Backfill only for reverse inspection. All effective lights are checkpointed.
ld=bpy.data.lights.new('Tappet cap reverse inspection fill','AREA');ld.energy=0;ld.size=.16;lo=bpy.data.objects.new(ld.name,ld);stage.objects.link(lo);lo.location=cap.matrix_world@Vector((.02,.03,-.15));lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler()
report={'component_id':'MOTO-ENGINE-OHC-COVER-001','revision':'engine-ohc-cover-v1','source_sha256':sha(source),'export_sha256':ex['sha256'],'samples':s.cycles.samples,'actual_blender_render':True,'material_diagnostic':mode if preview else'originalPBR','metallic_stub_separate_unmade':True,'head_interface_blocked':True,'all_dimensions_estimated':True,'art_accepted':False,'views':[]}
for name,offset,detail in views:
 point=cap.matrix_world@Vector((.018,0,.006)if detail else(0,0,.005));s.camera.location=point+cap.matrix_world.to_3x3()@Vector(offset);s.camera.rotation_euler=(point-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=65;ld.energy=.5 if name=='rear-cavity'else 0;bpy.context.view_layer.update();frame=check_component_camera(s,[cap],allow_crop=detail,margin=.005);cp=checkpoint_view(s,out,source,name);report['views'].append({'name':name,'camera_preflight':frame,'outputs':cp['outputs']});(out/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
