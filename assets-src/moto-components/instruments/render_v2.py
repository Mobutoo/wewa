"""Integrated original instrument candidate: same-camera preview before96.
Checks actual evaluated meshes with shared read-only preflight. Never saves poses.
"""
import bpy,json,hashlib,struct,sys,math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PUBLIC=ROOT/'creative/reviews/instruments-v2';preview='--preview'in sys.argv;OUT=Path('/workspace/wewa-assets/work-in-progress/instruments-v2/preview')if preview else PUBLIC;OUT.mkdir(parents=True,exist_ok=True);RAW=OUT if preview else Path('/workspace/wewa-assets/renders/instruments-v2');RAW.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(ROOT/'tools'));from blender_component_camera_preflight import check_component_camera
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();j=json.loads((PUBLIC/'source-geometry-check.json').read_text());g=json.loads((PUBLIC/'export-detail-check-v2.json').read_text());i=json.loads((PUBLIC/'interface-motion-check.json').read_text());source=HERE/'instruments-v2.blend';assert sha(source)==j['source_sha256']==g['source_sha256']==i['source_sha256']and sha(HERE/'instruments-v2-inspection.glb')==j['export_sha256']==g['export_sha256']and g['exact_zero_area_triangles']==0 and i['passed']
if not preview:
 review=json.loads((PUBLIC/'preview-review.json').read_text());assert review['source_sha256']==j['source_sha256']and review['read_by_agent']and review['passed_for_final_render']
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.cycles.samples=8 if preview else 96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.view_layers[0].cycles.denoising_store_passes=True;s.render.resolution_x=700 if preview else 1400;s.render.resolution_y=500 if preview else 1000;s.render.resolution_percentage=100;s.camera.data.clip_start=.001;s.camera.data.clip_end=10;s.camera.data.dof.use_dof=False;s.cycles.max_bounces=12;s.cycles.transmission_bounces=8
assembly=bpy.data.objects['INSTRUMENT_CLUSTER_MOUNT'];normal=assembly.matrix_world.to_3x3()@Vector((0,0,1));target=assembly.matrix_world@Vector((0,.001,.008));views={'whole-front':{'location':list(target+normal*.52),'target':list(target),'lens':70,'speed_kmh':0,'fuel_fraction':.65},'driver-42':{'location':[.13,.36,.36],'target':[0,-.12,.085],'lens':70,'speed_kmh':42,'fuel_fraction':.65}};objects=list(bpy.data.collections[j['collection']].objects)

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
reportpath=OUT/'render-checkpoints.json';report=json.loads(reportpath.read_text())if reportpath.exists()else{'schema':1,'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'views':{},'art_accepted':False};assert report['source_sha256']==j['source_sha256'],'New source: retain/archive earlier checkpoints and use a new review revision'
for name,view in views.items():
 s.camera.location=view['location'];s.camera.rotation_euler=(Vector(view['target'])-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=view['lens'];bpy.data.objects['SPEED_NEEDLE_PIVOT'].rotation_euler.z=math.radians(225-view['speed_kmh']*270/140);bpy.data.objects['FUEL_NEEDLE_PIVOT'].rotation_euler.z=math.radians(225-view['fuel_fraction']*80);bpy.context.view_layer.update();frame=check_component_camera(s,objects,allow_crop=False,margin=.025)
 config={'view':view,'samples':s.cycles.samples,'resolution_px':[s.render.resolution_x,s.render.resolution_y],'renderer':'Blender4.3.2 Cycles/OpenImageDenoise CPU','camera_clip_m':[.001,10],'depth_of_field':False,'AgX':s.view_settings.look,'transmission_bounces':8,'max_bounces':12,'denoising_store_passes':True,'pose_saved_to_source':False};cs=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();png=OUT/(name+'.png');exr=RAW/(name+'.exr');old=report['views'].get(name)
 if old and old['config_sha256']==cs and png.exists()and exr.exists()and sha(png)==old['PNG_sha256']and sha(exr)==old['EXR_sha256']:print('CHECKPOINT_SKIP_VALID',name);continue
 s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.image_settings.exr_codec='ZIP';s.render.filepath=str(exr);bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.image_settings.color_mode='RGBA';bpy.data.images['Render Result'].save_render(str(png),scene=s)
 report['views'][name]={'source_sha256':j['source_sha256'],'config':config,'config_sha256':cs,'PNG_path':str(png)if preview else str(png.relative_to(ROOT)),'PNG_sha256':sha(png),'EXR_private_path':str(exr),'EXR_sha256':sha(exr),'EXR_channels_actual_header':channels(exr),'actual_frame_check':frame,'actually_saved':True};tmp=reportpath.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(reportpath);print('CHECKPOINT_SAVED',name)
assert sha(source)==j['source_sha256'],'Rendering must not save source poses'
