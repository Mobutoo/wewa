"""Shape-study cameras; no material/geometry edit. Actual checkpoints after each view."""
import bpy,json,hashlib,sys,struct
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PUBLIC=ROOT/'creative/reviews/instrument-visor-shell-study-v1';preview='--preview'in sys.argv;OUT=Path('/workspace/wewa-assets/work-in-progress/instrument-visor/shell-study-v1-preview-r2')if preview else PUBLIC;RAW=OUT if preview else Path('/workspace/wewa-assets/renders/instrument-visor-shell-study-v1');OUT.mkdir(parents=True,exist_ok=True);RAW.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();j=json.loads((PUBLIC/'source-geometry-check.json').read_text());g=json.loads((PUBLIC/'export-detail-check.json').read_text());i=json.loads((PUBLIC/'instrument-interface-check.json').read_text());source=HERE/'instrument-visor-shell-study-v1.blend';assert sha(source)==j['source_sha256']==g['source_sha256']==i['source_sha256']and sha(HERE/'instrument-visor-shell-study-v1.glb')==j['export_sha256']==g['export_sha256']and g['exact_zero_area_triangles']==0 and i['all_sampled_interfaces_clear']
if not preview:
 r=json.loads((PUBLIC/'preview-review.json').read_text());assert r['source_sha256']==j['source_sha256']and r['read_by_agent']and r['passed_for_final_render']
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.view_settings.exposure=-2.5;bpy.data.objects['VISOR neutral floor'].hide_render=True;backlight=bpy.data.lights.new('TEMP low rear diffuse inspection area','AREA');backlight.energy=80;backlight.shape='DISK';backlight.size=.45;backobj=bpy.data.objects.new(backlight.name,backlight);s.collection.objects.link(backobj);backobj.location=(-.3,.45,-.3);backobj.rotation_euler=(Vector((0,-.18,.11))-backobj.location).to_track_quat('-Z','Y').to_euler();s.cycles.samples=8 if preview else 96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.view_layers[0].cycles.denoising_store_passes=True;s.cycles.max_bounces=12;s.cycles.transmission_bounces=8;s.render.resolution_x=600 if preview else 1000;s.render.resolution_y=650 if preview else 1100;s.render.resolution_percentage=100;s.camera.data.clip_start=.001;s.camera.data.clip_end=10;s.camera.data.dof.use_dof=False;U=Vector(j['frame']['U']);V=Vector(j['frame']['up_V']);N=Vector(j['frame']['front_N']);objects=[o for o in bpy.data.collections[j['collection']].all_objects if o.type=='MESH'];allverts=[o.matrix_world@v.co for o in objects for v in o.data.vertices];target=Vector([(min(v[k]for v in allverts)+max(v[k]for v in allverts))/2 for k in range(3)]);views={'whole-front':{'location':list(target+N*.75),'target':list(target),'lens':70},'whole-profile':{'location':list(target+U*.68+N*.13),'target':list(target),'lens':70},'whole-inside':{'location':list(target-N*.75),'target':list(target),'lens':70}};sys.path.insert(0,str(ROOT/'tools'));from blender_component_camera_preflight import check_component_camera

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
if '--front-only'in sys.argv:views={k:v for k,v in views.items()if k=='whole-front'}
q=OUT/'render-checkpoints.json';report=json.loads(q.read_text())if q.exists()else{'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'views':{},'art_accepted':False};assert report['source_sha256']==j['source_sha256']
for name,v in views.items():
 s.camera.location=v['location'];s.camera.rotation_euler=(Vector(v['target'])-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=v['lens'];bpy.context.view_layer.update();frame=check_component_camera(s,objects,allow_crop=False,margin=.025);cfg={'view':v,'samples':s.cycles.samples,'resolution_px':[s.render.resolution_x,s.render.resolution_y],'renderer':'Blender4.3.2 Cycles/OpenImageDenoise CPU','protocol_sha256':sha(Path(__file__)),'camera_clip_m':[.001,10],'depth_of_field':False,'exposure_EV':-2.5,'studio_floor_hidden':True,'temporary_rear_area':{'location':[-.3,.45,-.3],'energy_W':80,'size_m':.45},'AgX':s.view_settings.look,'max_bounces':12,'transmission_bounces':8,'denoising_store_passes':True,'scope':'Neutral shape study only; edge rounding/fixings/smoked optics not represented.'};cs=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest();png=OUT/(name+'.png');exr=RAW/(name+'.exr');old=report['views'].get(name)
 if old and old['config_sha256']==cs and png.exists()and exr.exists()and sha(png)==old['PNG_sha256']and sha(exr)==old['EXR_sha256']:print('CHECKPOINT_SKIP_VALID',name);continue
 s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(exr);bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.image_settings.color_mode='RGBA';bpy.data.images['Render Result'].save_render(str(png),scene=s);report['views'][name]={'source_sha256':j['source_sha256'],'config':cfg,'config_sha256':cs,'PNG_path':str(png)if preview else str(png.relative_to(ROOT)),'PNG_sha256':sha(png),'EXR_private_path':str(exr),'EXR_sha256':sha(exr),'EXR_channels_actual_header':channels(exr),'actual_frame_check':frame,'actually_saved':True};tmp=q.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(q);print('CHECKPOINT_SAVED',name)
assert sha(source)==j['source_sha256']
