"""RH full mirror final-camera preview then96, with restartable actual saved checkpoints."""
import bpy,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PUBLIC=ROOT/'creative/reviews/mirror-right-v3';preview='--preview'in sys.argv;OUT=Path('/workspace/wewa-assets/work-in-progress/mirrors/right-full-preview-v3')if preview else PUBLIC;RAW=OUT if preview else Path('/workspace/wewa-assets/renders/mirrors/mirror-right-v3');OUT.mkdir(parents=True,exist_ok=True);RAW.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(ROOT/'tools'));from blender_component_camera_preflight import check_component_camera
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=HERE/'mirror-right-v3.blend';export=HERE/'mirror-right-v3.glb';j=json.loads((PUBLIC/'source-geometry-check.json').read_text());g=json.loads((PUBLIC/'final-export-check.json').read_text());uv=json.loads((PUBLIC/'final-UV-tangent-check.json').read_text());motion=json.loads((PUBLIC/'motion-mount-check.json').read_text());assert sha(source)==j['source_sha256']==motion['source_sha256']and sha(export)==j['export_sha256']==g['sha256']==uv['sha256']and g['glTF_errors']==0 and g['zero_area_triangles']==0 and uv['errors']==0 and motion['all_sampled_interfaces_clear']
if not preview:
 r=json.loads((PUBLIC/'full-preview-review.json').read_text());assert r['read_by_agent']and r['passed_for_final_render']and r['source_sha256']==j['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.cycles.samples=8 if preview else 96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.view_layers[0].cycles.denoising_store_passes=True;s.cycles.max_bounces=12;s.cycles.transmission_bounces=8;s.render.resolution_x=700 if preview else 1000;s.render.resolution_y=560 if preview else 800;s.render.resolution_percentage=100;s.camera.data.clip_start=.001;s.camera.data.clip_end=10;s.camera.data.dof.use_dof=False
f=j['head_frame_world'];U=Vector(f['outward_U']);N=Vector(f['normal_toward_rider_N']);Z=Vector((0,0,1));objects=[o for o in bpy.data.collections['WEWA_MIRROR_RIGHT'].all_objects if o.type=='MESH'];verts=[o.matrix_world@v.co for o in objects for v in o.data.vertices];target=Vector([(min(v[k]for v in verts)+max(v[k]for v in verts))/2 for k in range(3)]);ball=Vector(j['ball_world_m']);mount=Vector(j['mount_boss_world_m']);views={
'whole-front':{'location':list(target+N*.72+U*.10+Z*.04),'target':list(target),'lens':70,'crop':False},
'whole-back':{'location':list(target-N*.72+U*.10+Z*.04),'target':list(target),'lens':70,'crop':False},
'joint-close':{'location':list(ball-N*.22+U*.05+Z*.04),'target':list(ball),'lens':80,'crop':True,'details':['RH fixed hollow lower neck cover - estimated','RH moving hollow upper neck cover - estimated']},
'base-close':{'location':list(mount+N*.14+U*.04+Z*.062),'target':list(mount+Z*.020),'lens':75,'crop':True,'details':['RH mirror base washer - estimated','RH mirror base hex nut - estimated thread-free bore','RH hollow mirror mounting cover - estimated']}}
views={k:v for k,v in views.items()if k in ['whole-front','base-close']}
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
   n=zstr()
   if not n:return[]
   typ=zstr();size=struct.unpack('<I',f.read(4))[0];v=f.read(size)
   if typ=='chlist':
    out=[];k=0
    while k<len(v)and v[k]:
     end=v.index(0,k);out.append(v[k:end].decode());k=end+17
    return out
q=OUT/'render-checkpoints.json';report=json.loads(q.read_text())if q.exists()else{'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'views':{},'art_accepted':False};assert report['source_sha256']==j['source_sha256'],'Retain older checkpoints before source revision'
for name,v in views.items():
 s.camera.location=v['location'];s.camera.rotation_euler=(Vector(v['target'])-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=v['lens'];bpy.context.view_layer.update();frame=check_component_camera(s,objects,allow_crop=v['crop'],margin=.025);detailframe=check_component_camera(s,[bpy.data.objects[n]for n in v['details']],allow_crop=False,margin=.015)if v.get('details')else None;cfg={'view':v,'samples':s.cycles.samples,'resolution_px':[s.render.resolution_x,s.render.resolution_y],'renderer':'Blender4.3.2 Cycles/OpenImageDenoise CPU','camera_clip_m':[.001,10],'depth_of_field':False,'AgX':s.view_settings.look,'max_bounces':12,'transmission_bounces':8,'denoising_store_passes':True};cs=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest();png=OUT/(name+'.png');exr=RAW/(name+'.exr');old=report['views'].get(name)
 if old and old['config_sha256']==cs and png.exists()and exr.exists()and sha(png)==old['PNG_sha256']and sha(exr)==old['EXR_sha256']:print('CHECKPOINT_SKIP_VALID',name);continue
 s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.image_settings.exr_codec='ZIP';s.render.filepath=str(exr);bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.image_settings.color_mode='RGBA';bpy.data.images['Render Result'].save_render(str(png),scene=s);report['views'][name]={'source_sha256':j['source_sha256'],'config':cfg,'config_sha256':cs,'PNG_path':str(png)if preview else str(png.relative_to(ROOT)),'PNG_sha256':sha(png),'EXR_private_path':str(exr),'EXR_sha256':sha(exr),'EXR_channels_actual_header':channels(exr),'actual_frame_check':frame,'required_detail_frame_check':detailframe,'actually_saved':True};tmp=q.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(q);print('CHECKPOINT_SAVED',name)
assert sha(source)==j['source_sha256']
