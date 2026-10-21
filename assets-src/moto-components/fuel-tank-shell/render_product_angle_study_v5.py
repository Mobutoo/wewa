"""Short gray/reflection of both actualtab candidates and whole tank; source fixed."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/fuel-tank-shell-study-v5';W=Path('/workspace/wewa-assets/work-in-progress/fuel-tank-shell-study-v5/product-camera-exploration');W.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();j=json.loads((O/'build-report.json').read_text());source=H/'fuel-tank-shell-study-v5.blend';assert sha(source)==j['source_sha256'];sys.path.insert(0,str(R/'tools'));from blender_component_camera_preflight import check_component_camera
views=[{'name':'whole-product-angle-gray','all':True}];cp=W/'render-checkpoints.json';report=json.loads(cp.read_text())if cp.exists()else{'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'views':{},'art_accepted':False}
for v in views:
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;cam=s.camera;cam.data.type='PERSP';cam.data.lens=60;cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36;cam.data.clip_start=.001;cam.data.clip_end=20;cam.data.dof.use_dof=False
 if v.get('all'):
  objects=[bpy.data.objects[n]for n in j['objects']];target=Vector((0,.12,-.23));eye=Vector((-.95,-.20,.27))
 else:
  obj=bpy.data.objects[v['object']];objects=[obj]
  for n in j['objects']:bpy.data.objects[n].hide_render=n!=obj.name
  target=obj.matrix_world@Vector(v['local_target']);m=obj.matrix_world.to_3x3();eye=target+m@Vector((.035,.025,.16))
 cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler()
 if v.get('reflection'):bpy.data.materials['Neutral gray inspection - not final tankpaint'].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.09
 s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;bpy.context.view_layer.update();pre=check_component_camera(s,objects,margin=.005);cfg={'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'protocol_sha256':sha(Path(__file__)),'view':v,'camera_eye_m':list(eye),'target_m':list(target),'actual_camera_matrix':[list(a)for a in cam.matrix_world],'near_far_m':[.001,20],'resolution_px':[1000,800],'samples':12,'renderer':'Blender4.3.2 Cycles/OIDN CPU','source_unchanged':True,'camera_is_uncalibrated_illustrative_hypothesis':True};cs=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest();png=W/(v['name']+'.png');exr=W/(v['name']+'.exr');old=report['views'].get(v['name'])
 if old and old['config_sha256']==cs and png.exists()and exr.exists()and sha(png)==old['PNG_sha256']and sha(exr)==old['EXR_sha256']:continue
 s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(exr);bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(png),scene=s);report['views'][v['name']]={'configuration':cfg,'config_sha256':cs,'PNG_private_path':str(png),'PNG_sha256':sha(png),'EXR_private_path':str(exr),'EXR_sha256':sha(exr),'frame_check':pre,'actually_saved':True};cp.write_text(json.dumps(report,indent=2)+'\n');print('SAVED',v['name'])
assert sha(source)==j['source_sha256']
