"""PBR whole/detail views: cheap preview first, then exact same final cameras.
Private EXR/preview originals; final PNG and checkpoints only after actual saves.
"""
import bpy,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PUBLIC=ROOT/'creative/reviews/instruments-usb-v2-material-study';preview='--preview' in sys.argv
OUT=Path('/workspace/wewa-assets/work-in-progress/instruments-usb-v2-material-study/preview')if preview else PUBLIC;OUT.mkdir(parents=True,exist_ok=True);RAW=OUT if preview else Path('/workspace/wewa-assets/renders/instruments-usb-v2-material-study');RAW.mkdir(parents=True,exist_ok=True)
j=json.loads((PUBLIC/'source-geometry-check.json').read_text());g=json.loads((PUBLIC/'export-buffer-check.json').read_text());source=HERE/'instruments-usb-v2-material-study.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)==j['source_sha256']==g['source_sha256'] and sha(HERE/'instruments-usb-v2-material-study.glb')==j['export_sha256']==g['export_sha256'] and g['exact_zero_area_triangles']==0 and g['glTF_errors']==0
if not preview:
 read=json.loads((PUBLIC/'preview-review.json').read_text());assert read['source_sha256']==j['source_sha256'] and read['read_by_agent'] and read['passed_for_final_material_render']
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.cycles.samples=8 if preview else 96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.view_layers[0].cycles.denoising_store_passes=True;s.render.resolution_x=600 if preview else 1000;s.render.resolution_y=540 if preview else 900;s.render.resolution_percentage=100;s.camera.data.clip_start=.001;s.camera.data.clip_end=10;s.camera.data.dof.use_dof=False
root=bpy.data.objects['INSTRUMENT_USB_MATERIAL_STUDY_MOUNT'];q=root.matrix_world.to_3x3();N=q@Vector((0,0,1));U=q@Vector((1,0,0));V=q@Vector((0,1,0));target=root.matrix_world@Vector((0,.038,.0345));cap=root.matrix_world@Vector((0,.038,.0351));views={'material-whole-front':{'location':list(target+N*.14+U*.025+V*.015),'target':list(target),'lens':70,'entire_part':True},'material-lip-detail':{'location':list(cap+N*.070+U*.032-V*.010),'target':list(cap),'lens':80,'entire_part':False}}

def channels(path):
 with path.open('rb')as f:
  assert struct.unpack('<I',f.read(4))[0]==20000630;f.read(4)
  def zstr():
   a=bytearray()
   while True:
    b=f.read(1)
    if not b or b==b'\0':return a.decode('utf8','replace')
    a.extend(b)
  while True:
   name=zstr()
   if not name:return[]
   typ=zstr();size=struct.unpack('<I',f.read(4))[0];v=f.read(size)
   if typ=='chlist':
    out=[];k=0
    while k<len(v)and v[k]:
     end=v.index(0,k);out.append(v[k:end].decode());k=end+17
    return out
reportpath=OUT/'render-checkpoints.json';report=json.loads(reportpath.read_text())if reportpath.exists()else{'schema':1,'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'views':{},'art_accepted':False}
assert report['source_sha256']==j['source_sha256'],'Source changed: archive earlier preview/checkpoints before rendering new revision'
for name,view in views.items():
 s.camera.location=view['location'];s.camera.rotation_euler=(Vector(view['target'])-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=view['lens'];bpy.context.view_layer.update();checks=[]
 for o in [bpy.data.objects[x['object']]for x in j['bodies']if view['entire_part'] or 'capsule' in x['object']]:
  points=[world_to_camera_view(s,s.camera,o.matrix_world@v.co)for v in o.data.vertices];b=[[min(p[k]for p in points),max(p[k]for p in points)]for k in range(3)];assert b[0][0]>.025 and b[0][1]<.975 and b[1][0]>.025 and b[1][1]<.975 and b[2][0]>.001 and b[2][1]<10,(name,o.name,b);checks.append({'object':o.name,'projected_bounds_xyz':b,'passed':True})
 config={'view':view,'samples':s.cycles.samples,'resolution_px':[s.render.resolution_x,s.render.resolution_y],'renderer':'Blender4.3.2 Cycles/OpenImageDenoise CPU','camera_clip_m':[.001,10],'depth_of_field':False,'AgX':s.view_settings.look,'denoising_store_passes':True};cs=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();png=OUT/(name+'.png');exr=RAW/(name+'.exr');old=report['views'].get(name)
 if old and old['config_sha256']==cs and png.exists()and exr.exists()and sha(png)==old['PNG_sha256']and sha(exr)==old['EXR_sha256']:print('CHECKPOINT_SKIP_VALID',name);continue
 s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.image_settings.exr_codec='ZIP';s.render.filepath=str(exr);bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.image_settings.color_mode='RGBA';bpy.data.images['Render Result'].save_render(str(png),scene=s)
 report['views'][name]={'source_sha256':j['source_sha256'],'config':config,'config_sha256':cs,'PNG_path':str(png)if preview else str(png.relative_to(ROOT)),'PNG_sha256':sha(png),'EXR_private_path':str(exr),'EXR_sha256':sha(exr),'EXR_channels_actual_header':channels(exr),'actual_frame_checks':checks,'actually_saved':True};tmp=reportpath.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(reportpath);print('CHECKPOINT_SAVED',name)
