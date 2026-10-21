"""Real Cycles renders, restartable by source/config/image hashes after each view."""
import bpy,json,hashlib,sys,struct
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];side=args[0] if args else 'left';stage=args[1] if len(args)>1 else 'head';stem='mirror-'+side+('-head-study' if stage=='head' else '-v1');OUT=ROOT/('creative/reviews/mirror-'+side+'-v1');RAW=Path('/workspace/wewa-assets/renders/mirrors')/stem;RAW.mkdir(parents=True,exist_ok=True);path=HERE/(stem+'.blend');source_sha=hashlib.sha256(path.read_bytes()).hexdigest();check=json.loads((OUT/(stage+'-export-check.json')).read_text());assert not check['glTF_errors'] and not check['zero_area_triangles'];j=json.loads((OUT/('head-study-check.json' if stage=='head' else 'source-geometry-check.json')).read_text());assert j['source_sha256']==source_sha and check['sha256']==hashlib.sha256((HERE/(stem+'.glb')).read_bytes()).hexdigest()==j['export_sha256']
bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;frame=j['head_frame_world'];C=Vector(frame['centre_m']);U=Vector(frame['outward_U']);V=Vector(frame['up_V']);N=Vector(frame['normal_toward_rider_N']);Z=Vector((0,0,1));scene.cycles.samples=96;scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE';scene.cycles.denoising_use_gpu=False;scene.view_layers[0].cycles.denoising_store_passes=True;scene.cycles.max_bounces=12;scene.cycles.transmission_bounces=8;scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100
if stage=='head':views={'head-glass-reflections':{'location':list(C+N*.47+U*.06+Z*.025),'target':list(C),'lens':75},'head-back-grain':{'location':list(C-N*.46+U*.10+Z*.10),'target':list(C),'lens':75}}
else:
 vertices=[o.matrix_world@v.co for o in bpy.data.collections['WEWA_MIRROR_'+side.upper()].all_objects if o.type=='MESH' for v in o.data.vertices];target=Vector(tuple((min(v[k]for v in vertices)+max(v[k]for v in vertices))*.5 for k in range(3)));views={'whole-front':{'location':list(target+N*.72+U*.10+Z*.04),'target':list(target),'lens':70},'whole-back':{'location':list(target-N*.72+U*.10+Z*.04),'target':list(target),'lens':70},'joint-close':{'location':list(Vector(j['ball_world_m'])-N*.22+U*.05+Z*.04),'target':j['ball_world_m'],'lens':80}}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exr_channels(p):
 with p.open('rb') as f:
  if struct.unpack('<I',f.read(4))[0]!=20000630:return[]
  f.read(4)
  def zstr():
   out=bytearray()
   while True:
    b=f.read(1)
    if not b or b==b'\0':break
    out.extend(b)
   return out.decode('utf8','replace')
  while True:
   name=zstr()
   if not name:return[]
   typ=zstr();size=struct.unpack('<I',f.read(4))[0];value=f.read(size)
   if typ=='chlist':
    names=[];k=0
    while k<len(value) and value[k]:
     end=value.index(0,k);names.append(value[k:end].decode());k=end+1+16
    return names
reportpath=OUT/(stage+'-render-checkpoints.json');report=json.loads(reportpath.read_text()) if reportpath.exists() else {'schema':1,'source_sha256':source_sha,'export_sha256':check['sha256'],'views':{},'art_accepted':False}
if report['source_sha256']!=source_sha:report={'schema':1,'source_sha256':source_sha,'export_sha256':check['sha256'],'views':{},'art_accepted':False}
for name,view in views.items():
 config={'view':view,'renderer':'Blender4.3.2 Cycles96 OpenImageDenoise CPU','resolution':[1000,800],'AgX':scene.view_settings.look,'transmission_bounces':8,'max_bounces':12,'denoising_store_passes':True};configsha=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();png=OUT/(name+'.png');exr=RAW/(name+'.exr');old=report['views'].get(name)
 if old and old['config_sha256']==configsha and png.exists() and exr.exists() and old['PNG_sha256']==sha(png) and old['EXR_sha256']==sha(exr):print('CHECKPOINT_SKIP_VALID',name);continue
 scene.camera.location=view['location'];scene.camera.rotation_euler=(Vector(view['target'])-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=view['lens'];scene.render.image_settings.file_format='OPEN_EXR_MULTILAYER';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP';scene.render.filepath=str(exr);bpy.ops.render.render(write_still=True);scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(png),scene=scene)
 report['views'][name]={'source_sha256':source_sha,'config':config,'config_sha256':configsha,'PNG_path':str(png.relative_to(ROOT)),'PNG_sha256':sha(png),'EXR_private_path':str(exr),'EXR_sha256':sha(exr),'EXR_channels_actual_header':exr_channels(exr),'actually_saved':True};tmp=reportpath.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(reportpath);print('CHECKPOINT_SAVED',name)
