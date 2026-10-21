"""Hash-bound component renders; short neutral/reflection diagnostics precede96."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/fork-outer-right-v1';sys.path.insert(0,str(ROOT/'tools'))
from blender_component_camera_preflight import check_component_camera
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((OUT/'source-geometry-check.json').read_text());b=json.loads((OUT/'geometry-check.json').read_text());assert a['source_sha256']==sha(HERE/'fork-outer-right-v1.blend');assert a['export_sha256']==b['sha256']==sha(HERE/'fork-outer-right-inspection.glb')and b['technical_passed']
bpy.ops.wm.open_mainfile(filepath=str(HERE/'fork-outer-right-v1.blend'));s=bpy.context.scene;objects=list(bpy.data.collections['WEWA_FORK_OUTER_RIGHT_ISOLATED'].objects);preview='--preview'in sys.argv;reflection='--reflection'in sys.argv;assert not reflection or preview
s.cycles.samples=24 if preview else 96;s.render.resolution_percentage=50 if preview else 100
if reflection:
 s.render.resolution_percentage=100
 m=bpy.data.materials.new('RAM-only diagnostic reflection - not finalfinish');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.30,.32,.35,1);p.inputs['Metallic'].default_value=.85;p.inputs['Roughness'].default_value=.08
 for o in objects:o.data.materials.clear();o.data.materials.append(m)
 s.world.node_tree.nodes['Background'].inputs[1].default_value=.08
 for o in bpy.data.collections['STUDIO_NOT_EXPORTED'].objects:
  if o.type=='LIGHT':o.data.shape='RECTANGLE';o.data.size=.5;o.data.size_y=.035
views={'outer-quarter':((-.60,.14,.30),(0,0,.15),.40,False),'inboard-quarter':((.60,.16,.28),(0,0,.15),.40,False),'outer-foot':((-.12,.045,.045),(-.005,0,.014),.105,True),'top-opening':((-.08,.10,.47),(0,0,.300),.11,True)}
report={'source_sha256':a['source_sha256'],'export_sha256':b['sha256'],'renderer':'Blender4.3.2 CyclesCPU OIDN','samples':96,'resolution_px':[1000,1400],'views':[],'art_accepted':False}
for name,(location,target,scale,crop)in views.items():
 if any(v.startswith('--view=')for v in sys.argv)and'--view='+name not in sys.argv:continue
 s.camera.location=location;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;bpy.context.view_layer.update();preflight=check_component_camera(s,objects,allow_crop=crop);preflight['helper_sha256']=sha(ROOT/'tools/blender_component_camera_preflight.py')
 view={'name':name,'camera_location_m':list(location),'camera_target_m':list(target),'ortho_scale_m':scale,'allow_deliberate_macro_crop':crop,'camera_preflight':preflight};config={'source_sha256':a['source_sha256'],'export_sha256':b['sha256'],'view':view,'samples':96,'resolution_px':[1000,1400]};config_sha=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();cp=OUT/('checkpoint-'+name+'.json');png=OUT/(name+'.png');reuse=False
 if not preview and cp.exists()and png.exists():
  prior=json.loads(cp.read_text());reuse=prior.get('config_sha256')==config_sha and prior.get('PNG_sha256')==sha(png)
 s.render.filepath='/tmp/wewa-fork-right-'+('reflection-'if reflection else'')+name+'.png'if preview else str(png)
 if not reuse:bpy.ops.render.render(write_still=True)
 if preview:
  p=Path(s.render.filepath);p.with_suffix('.json').write_text(json.dumps({'source_sha256':a['source_sha256'],'export_sha256':b['sha256'],'samples':s.cycles.samples,'resolution_percentage':s.render.resolution_percentage,'reflection_override':reflection,'view':view,'PNG_sha256':sha(p)},indent=2)+'\n')
 if not preview:
  checkpoint={**config,'config_sha256':config_sha,'PNG_sha256':sha(png),'PNG_bytes':png.stat().st_size,'EXR_saved':False,'art_accepted':False}
  if not reuse:
   temp=cp.with_suffix('.tmp');temp.write_text(json.dumps(checkpoint,indent=2)+'\n');temp.replace(cp)
  view['PNG_sha256']=sha(png);view['checkpoint_file']=cp.name;view['reused_verified_checkpoint']=reuse
 report['views'].append(view)
if not preview:(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
