"""Two targeted real views of immutable v4: whole rear and exact cable-context fixture.
Only preview8 or final96; no source, fitting matrices, materials or saved poses edited.
"""
import bpy,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];P=R/'creative/reviews/instruments-v4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();j=json.loads((P/'source-geometry-check.json').read_text());e=json.loads((P/'export-detail-check-v4.json').read_text());i=json.loads((P/'interface-motion-check.json').read_text());src=H/'instruments-v4.blend';assert sha(src)==j['source_sha256']==e['source_sha256']==i['source_sha256']and i['passed']and not e['exact_zero_area_triangles']and not e['glTF_errors'];assert sha(H/'instruments-v4-inspection.glb')==j['export_sha256']
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;OUT=Path('/workspace/wewa-assets/work-in-progress/instruments-v4/preview-r2')if preview else P;OUT.mkdir(parents=True,exist_ok=True);RAW=OUT if preview else Path('/workspace/wewa-assets/renders/instruments-v4');RAW.mkdir(parents=True,exist_ok=True)
if not preview:
 read=json.loads((P/'preview-review.json').read_text());assert read['read_by_agent']and read['passed_for_final_render']and read['source_sha256']==j['source_sha256']
sys.path.insert(0,str(R/'tools'));from blender_component_camera_preflight import check_component_camera
B=R/'assets-src/moto-components/cockpit-cables/cockpit-cables-v2.blend';bs=sha(B);bc=json.loads((R/'creative/reviews/cockpit-cables-v2/ignition-interface-current.checkpoint.json').read_text())['configuration'];bcheck=json.loads((R/'creative/reviews/cockpit-cables-v2/source-geometry-check.json').read_text());assert bs==bcheck['source_sha256'];rep=OUT/'render-checkpoints.json';report=json.loads(rep.read_text())if rep.exists()else{'schema':1,'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'views':{},'art_accepted':False};assert report['source_sha256']==j['source_sha256']
def whole():
 bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;parts=bpy.data.collections[j['collection']];root=bpy.data.objects[j['root']];objects=[o for o in parts.objects if o.type in ['MESH','CURVE','FONT']];target=root.matrix_world@Vector((0,0,.006));normal=root.matrix_world.to_3x3()@Vector((0,0,1));s.camera.location=target-normal*.65+Vector((.16,0,.06));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=65
 for o in s.objects:
  if o.type=='LIGHT':o.hide_render=True
  elif o.type in ['MESH','CURVE','FONT']and o not in objects:o.hide_render=True
 T=bpy.data.collections.new('INSTRUMENT_V4_REAR_LIGHTING_RAM_ONLY');s.collection.children.link(T)
 for name,offset,power,size in [('key',(-.20,-.12,-.22),20,.25),('fill',(.25,0,-.12),14,.30),('edge',(0,.25,.10),16,.20)]:
  data=bpy.data.lights.new('V4 rear '+name,'AREA');data.energy=power*.08;data.size=size;o=bpy.data.objects.new(data.name,data);T.objects.link(o);o.location=target+root.matrix_world.to_3x3()@Vector(offset);o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 return s,objects,{'fixture':'Whole saved instrumentv4 rear, temporary neutral studio lights and no floor. No asset changes.','target_world_m':list(target)}
def context():
 bpy.ops.wm.open_mainfile(filepath=str(B));s=bpy.context.scene;guides=bpy.data.collections['CABLES_IMMUTABLE_INTERFACE_GUIDES'];guides.hide_viewport=False;bpy.context.view_layer.update();original=bpy.data.objects['Shaped central cluster cover'];world=original.matrix_world.copy();T=bpy.data.collections.new('V4_CURRENT_CASE_CONTEXT_RAM_ONLY');s.collection.children.link(T)
 with bpy.data.libraries.load(str(src),link=False)as(fr,to):to.objects=['Shaped central cluster cover']
 new=to.objects[0];pending=new
 while pending:
  if not pending.users_collection:T.objects.link(pending)
  pending=pending.parent
 bpy.context.view_layer.update();delta=max(abs(new.matrix_world[a][b]-world[a][b])for a in range(4)for b in range(4));assert delta<1e-7,delta
 shown=[]
 for obj,label in [(new,'revised central cover'),(bpy.data.objects['Ignition ribbed hollow housing and mounting ears - candidate'],'unchanged ignition case')]:
  dg=bpy.context.evaluated_depsgraph_get();mesh=bpy.data.meshes.new_from_object(obj.evaluated_get(dg),depsgraph=dg);copy=bpy.data.objects.new('Context copy '+label,mesh);copy.matrix_world=obj.matrix_world.copy();T.objects.link(copy);shown.append(copy)
 loop=next(o for o in bpy.data.collections['WEWA_COCKPIT_CABLES_PARTIAL'].objects if'ignition'in o.name.lower());shown.append(loop)
 for obj in s.objects:
  if obj.type in ['MESH','CURVE','FONT']:obj.hide_render=obj not in shown
 guides.hide_render=True
 for l in bc['lights']:
  obj=bpy.data.objects[l['name']];obj.data.energy=l['energy'];obj.data.size=l['size'];obj.matrix_world=Matrix(l['matrix']);obj.hide_render=False
 s.camera.matrix_world=Matrix(bc['camera_world_matrix']);s.camera.data.lens=bc['lens_mm'];s.camera.data.sensor_width=bc['sensor_width_mm'];s.camera.data.sensor_height=bc['sensor_height_mm'];s.camera.data.sensor_fit=bc['sensor_fit'];s.camera.data.shift_x,s.camera.data.shift_y=bc['camera_shift_xy'];s.view_settings.view_transform=bc['view']['transform'];s.view_settings.look=bc['view']['look'];s.view_settings.exposure=bc['view']['exposure'];s.view_settings.gamma=bc['view']['gamma'];bpy.context.view_layer.update()
 return s,shown,{'fixture':'Actual unchanged cockpit-cablesv2 ignition loop/case context plus evaluated instrumentv4 cover; old checkpoint camera/lights reused exactly.','fixture_source_sha256':bs,'baseline_context_checkpoint_sha256':sha(R/'creative/reviews/cockpit-cables-v2/ignition-interface-current.checkpoint.json'),'cover_context_world_matrix_max_difference_m':delta,'context_not_a_new_assembled_asset':True}
views={'whole-rear':whole,'cover-context':context};selected=[args[args.index('--view')+1]]if'--view'in args else list(views)
for name in selected:
 s,objects,fixture=views[name]();s.render.engine='CYCLES';s.cycles.samples=8 if preview else 96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.view_layers[0].cycles.denoising_store_passes=True;s.render.resolution_x=1100;s.render.resolution_y=850;s.render.resolution_percentage=100;s.camera.data.clip_start=.001;s.camera.data.clip_end=10;s.camera.data.dof.use_dof=False;bpy.context.view_layer.update();assert s.view_layers[0].material_override is None;frame=check_component_camera(s,objects,allow_crop=False,margin=.005)
 cfg={'fixture':fixture,'camera_world_matrix':[list(row)for row in s.camera.matrix_world],'camera':{'location':list(s.camera.location),'lens_mm':s.camera.data.lens,'near_far_m':[.001,10]},'renderer':'Blender4.3.2 Cycles/OpenImageDenoise CPU','samples':s.cycles.samples,'resolution_px':[1100,850],'view_settings':{'transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma},'lights':[{'name':o.name,'matrix':[list(r)for r in o.matrix_world],'energy':o.data.energy,'size':o.data.size}for o in s.objects if o.type=='LIGHT'and not o.hide_render],'material_override':False,'protocol_sha256':sha(Path(__file__))};cs=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest();png=OUT/(name+'.png');exr=RAW/(name+'.exr');old=report['views'].get(name)
 if old and old['config_sha256']==cs and png.exists()and exr.exists()and sha(png)==old['PNG_sha256']and sha(exr)==old['EXR_sha256']:print('CHECKPOINT_SKIP_VALID',name);continue
 s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(exr);bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(png),scene=s);report['views'][name]={'name':name,'config':cfg,'config_sha256':cs,'PNG_path':str(png)if preview else str(png.relative_to(R)),'PNG_sha256':sha(png),'EXR_private_path':str(exr),'EXR_sha256':sha(exr),'actual_frame_check':frame,'actually_saved':True};tmp=rep.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(rep);print('CHECKPOINT_SAVED',name)
assert sha(src)==j['source_sha256']and sha(B)==bs
