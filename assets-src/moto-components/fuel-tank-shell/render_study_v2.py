"""Short whole gray/reflection checks of original skin study; source never saved here."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector,Quaternion
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/fuel-tank-shell-study-v2';W=Path('/workspace/wewa-assets/work-in-progress/fuel-tank-shell-study-v2/previews');W.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();j=json.loads((O/'build-report.json').read_text());source=H/'fuel-tank-shell-study-v2.blend';assert sha(source)==j['source_sha256'];studies=json.loads((R/'creative/research/reference-camera-studies/camera-studies.json').read_text());sys.path.insert(0,str(R/'tools'));from blender_component_camera_preflight import check_component_camera
views=[{'name':'upper-oblique-gray','eye':[-.78,-.70,.42],'target':[0,.12,-.23],'resolution':[1000,800]},{'name':'mouth-gray','eye':[-.14,-.02,.16],'target':[0,.112,-.11],'resolution':[1000,800],'crop':True},{'name':'mouth-reflection','eye':[-.14,-.02,.16],'target':[0,.112,-.11],'resolution':[1000,800],'crop':True,'reflection':True}]
only=next((a.split('=',1)[1]for a in sys.argv if a.startswith('--view=')),None);cp=W/'render-checkpoints.json';report=json.loads(cp.read_text())if cp.exists()else{'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'views':{},'art_accepted':False}
for v in views:
 if only and v['name']!=only:continue
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;cam=s.camera;cam.data.clip_start=.001;cam.data.clip_end=20;cam.data.dof.use_dof=False;cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36
 if 'native'in v:
  c=next(a for a in studies['views']if a['id']==v['native'])['selected_working_camera'];cam.location=c['location_m'];cam.rotation_mode='QUATERNION';cam.rotation_quaternion=Quaternion(c['rotation_quaternion_wxyz']);cam.data.type='ORTHO';cam.data.ortho_scale=c['ortho_scale_m'];camlimits=c.get('working_camera_limits','Working ORTHO hypothesis; not calibration')
 else:
  cam.location=v['eye'];cam.rotation_mode='QUATERNION';cam.rotation_quaternion=(Vector(v['target'])-cam.location).to_track_quat('-Z','Y');cam.data.type='PERSP';cam.data.lens=60;camlimits='Illustrative whole camera, not matched photograph'
 if v.get('reflection'):
  bs=bpy.data.materials['Neutral gray inspection - not final tankpaint'].node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.09
 s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.resolution_x,s.render.resolution_y=v['resolution'];s.render.resolution_percentage=100;bpy.context.view_layer.update();frame=check_component_camera(s,[bpy.data.objects[j['object']]],margin=.005,allow_crop=v.get('crop',False))
 cfg={'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'protocol_sha256':sha(Path(__file__)),'view':v,'camera_matrix':[list(a)for a in cam.matrix_world],'near_far_m':[.001,20],'samples':12,'renderer':'Blender4.3.2 Cycles/OIDN CPU','camera_limits':camlimits,'source_unchanged':True};cs=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest();png=W/(v['name']+'.png');exr=W/(v['name']+'.exr');old=report['views'].get(v['name'])
 if old and old['config_sha256']==cs and png.exists()and exr.exists()and old['PNG_sha256']==sha(png)and old['EXR_sha256']==sha(exr):continue
 s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(exr);bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(png),scene=s);report['views'][v['name']]={'configuration':cfg,'config_sha256':cs,'PNG_private_path':str(png),'PNG_sha256':sha(png),'EXR_private_path':str(exr),'EXR_sha256':sha(exr),'frame_check':frame,'actually_saved':True};cp.write_text(json.dumps(report,indent=2)+'\n');print('SAVED',v['name'])
assert sha(source)==j['source_sha256']
