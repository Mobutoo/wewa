"""Two real targeted glyph correction renders with per-view restart checkpoints."""
import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/switchgear-left-v3';RAW=Path('/workspace/wewa-assets/renders/switchgear-left-v3');RAW.mkdir(parents=True,exist_ok=True);path=HERE/'switchgear-left-v3.blend';source_sha=hashlib.sha256(path.read_bytes()).hexdigest();j=json.loads((OUT/'source-geometry-check.json').read_text());check=json.loads((OUT/'geometry-check.json').read_text());areas=json.loads((OUT/'actual-triangle-area-check.json').read_text());proof=json.loads((OUT/'annotation-only-change-check.json').read_text());assert source_sha==j['source_sha256'] and check['sha256']==j['export_sha256']==hashlib.sha256((HERE/'switchgear-left-v3-inspection.glb').read_bytes()).hexdigest() and areas['passed'] and proof['only_photo_traced_icon_contours_changed']
bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.cycles.samples=96;scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE';scene.cycles.denoising_use_gpu=False;scene.view_layers[0].cycles.denoising_store_passes=True;scene.camera.data.clip_start=.001;scene.camera.data.clip_end=10;scene.cycles.max_bounces=12;scene.cycles.transmission_bounces=8;scene.render.resolution_x=1100;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;E=Vector(j['datum']['endpoint_m']);I=Vector(j['datum']['inward_axis']);T=Vector(j['datum']['thumb_side_radial']);Z=Vector((0,0,1));trees=[BVHTree.FromPolygons([v.co for v in o.data.vertices],[tuple(f.vertices)for f in o.data.polygons])for o in bpy.data.collections['WEWA_SWITCHGEAR_LEFT'].objects if o.type=='MESH'and 'shell - editable'in o.name]
def surface(q,z):
 hits=[t.ray_cast(E+I*q+Z*z+T*.10,-T,.15)for t in trees];hits=[h for h in hits if h[0]is not None];return min(hits,key=lambda h:h[3])[0]
a=surface(.143,.0125);b=surface(.1325,-.0215);views={'symbols-high-low':{'location':list(a+T*.085),'target':list(a),'lens':90},'symbol-horn':{'location':list(b+T*.070+I*.008+Z*.002),'target':list(b),'lens':90}}
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
reportpath=OUT/'render-checkpoints.json';report=json.loads(reportpath.read_text()) if reportpath.exists() else {'schema':1,'source_sha256':source_sha,'export_sha256':check['sha256'],'views':{},'art_accepted':False}
if report['source_sha256']!=source_sha:report={'schema':1,'source_sha256':source_sha,'export_sha256':check['sha256'],'views':{},'art_accepted':False}
for name,view in views.items():
 config={'view':view,'renderer':'Blender4.3.2 Cycles96 OpenImageDenoise CPU','resolution':[1100,1000],'AgX':scene.view_settings.look,'transmission_bounces':8,'max_bounces':12,'denoising_store_passes':True,'camera_clip_m':[.001,10]};configsha=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();png=OUT/(name+'.png');exr=RAW/(name+'.exr');old=report['views'].get(name)
 if old and old['config_sha256']==configsha and png.exists() and exr.exists() and old['PNG_sha256']==sha(png) and old['EXR_sha256']==sha(exr):print('CHECKPOINT_SKIP_VALID',name);continue
 scene.camera.location=view['location'];scene.camera.rotation_euler=(Vector(view['target'])-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=view['lens'];bpy.context.view_layer.update()
 selected=['LH print high_beam smooth contours v3','LH print low_beam smooth contours v3'] if name=='symbols-high-low' else ['LH print horn smooth contours v3'];frame=[]
 for objname in selected:
  obj=bpy.data.objects[objname];points=[world_to_camera_view(scene,scene.camera,obj.matrix_world@v.co)for v in obj.data.vertices];bbox=[[min(p[k]for p in points),max(p[k]for p in points)]for k in range(3)];assert bbox[0][0]>.02 and bbox[0][1]<.98 and bbox[1][0]>.02 and bbox[1][1]<.98 and bbox[2][0]>scene.camera.data.clip_start and bbox[2][1]<scene.camera.data.clip_end,(name,objname,bbox);frame.append({'node':objname,'projected_bounds_xyz':bbox,'clip_and_frame_passed':True})
 scene.render.image_settings.file_format='OPEN_EXR_MULTILAYER';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP';scene.render.filepath=str(exr);bpy.ops.render.render(write_still=True);scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(png),scene=scene)
 report['views'][name]={'source_sha256':source_sha,'config':config,'config_sha256':configsha,'PNG_path':str(png.relative_to(ROOT)),'PNG_sha256':sha(png),'EXR_private_path':str(exr),'EXR_sha256':sha(exr),'EXR_channels_actual_header':exr_channels(exr),'actually_saved':True,'actual_ink_frame_checks':frame};tmp=reportpath.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(reportpath);print('CHECKPOINT_SAVED',name)
