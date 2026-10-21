"""Hash-bound source views; real camera preflight and per-view checkpoints."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/fork-bellows-v2';sys.path.insert(0,str(ROOT/'tools'))
from blender_component_camera_preflight import check_component_camera
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=json.loads((OUT/'source-geometry-check.json').read_text());b=json.loads((OUT/'geometry-check.json').read_text());assert a['source_sha256']==sha(HERE/'fork-bellows-v2.blend')and a['export_sha256']==b['sha256']==sha(HERE/'fork-bellows-v2-inspection.glb')and b['technical_passed'];bpy.ops.wm.open_mainfile(filepath=str(HERE/'fork-bellows-v2.blend'));s=bpy.context.scene;objects=list(bpy.data.collections['WEWA_FORK_BELLOWS_V2_ISOLATED'].objects);o=objects[0];preview='--preview'in sys.argv;reflection='--reflection'in sys.argv;assert not reflection or preview;s.cycles.samples=24 if preview else 96;s.render.resolution_percentage=100 if reflection or'--native-preview'in sys.argv else 50 if preview else 100
if reflection:
 m=bpy.data.materials.new('RAM-only reflection diagnostic, not final rubber');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.30,.32,.35,1);p.inputs['Metallic'].default_value=.85;p.inputs['Roughness'].default_value=.08;o.data.materials.clear();o.data.materials.append(m);s.world.node_tree.nodes['Background'].inputs[1].default_value=.08
 for x in bpy.data.collections['STUDIO_NOT_EXPORTED'].objects:
  if x.type=='LIGHT':x.data.shape='RECTANGLE';x.data.size=.16;x.data.size_y=.012
views={'quarter':((.14,.22,.14),(0,0,.0625),.18,[0,0],False),'lower-opening':((.065,.085,-.065),(0,0,.006),.082,[0,0],True),'lower-rim-detail':((.035,.045,-.030),(.015,.005,.002),.045,[0,0],True),'compression-estimated':((.14,.22,.14),(0,0,.0625),.18,[1,0],False),'extension-estimated':((.14,.22,.14),(0,0,.0625),.18,[0,1],False)}
def fixture():return{'render_script_sha256':sha(Path(__file__)),'lights':[{'name':x.name,'location_m':list(x.location),'rotation_euler_rad':list(x.rotation_euler),'energy_W':x.data.energy,'shape':x.data.shape,'size_m':x.data.size}for x in bpy.data.collections['STUDIO_NOT_EXPORTED'].objects if x.type=='LIGHT'],'world_color_linear':list(s.world.node_tree.nodes['Background'].inputs[0].default_value),'world_strength':s.world.node_tree.nodes['Background'].inputs[1].default_value}
report={'source_sha256':a['source_sha256'],'export_sha256':b['sha256'],'renderer':'Blender4.3.2 CyclesCPU OIDN','samples':96,'resolution_px':[1000,1200],'views':[],'manufacturer_travel_verified':False,'art_accepted':False}
for name,(location,target,scale,weights,crop)in views.items():
 if any(q.startswith('--view=')for q in sys.argv)and'--view='+name not in sys.argv:continue
 for i,w in enumerate(weights):o.data.shape_keys.key_blocks[i+1].value=w
 if reflection and name in['lower-opening','lower-rim-detail']:
  key=bpy.data.objects['LOWER'];key.location=(.07,.09,-.07);key.data.energy=.30;key.data.size=.10;key.data.size_y=.015;key.rotation_euler=(Vector((0,0,.003))-key.location).to_track_quat('-Z','Y').to_euler()
 s.camera.location=location;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;bpy.context.view_layer.update();preflight=check_component_camera(s,objects,allow_crop=crop);preflight['helper_sha256']=sha(ROOT/'tools/blender_component_camera_preflight.py');view={'name':name,'camera_location_m':list(location),'camera_target_m':list(target),'ortho_scale_m':scale,'morph_weights':weights,'allow_deliberate_macro_crop':crop,'camera_preflight':preflight};config={'source_sha256':a['source_sha256'],'export_sha256':b['sha256'],'view':view,'samples':96,'resolution_px':[1000,1200],'fixture':fixture()};config_sha=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();cp=OUT/('checkpoint-'+name+'.json');png=OUT/(name+'.png');reuse=False
 if not preview and cp.exists()and png.exists():
  prior=json.loads(cp.read_text());reuse=prior.get('config_sha256')==config_sha and prior.get('PNG_sha256')==sha(png)
 s.render.filepath='/tmp/wewa-bellows-v2-'+('reflection-'if reflection else'')+name+'.png'if preview else str(png)
 if not reuse:bpy.ops.render.render(write_still=True)
 if preview:
  p=Path(s.render.filepath);p.with_suffix('.json').write_text(json.dumps({**config,'actual_samples':24,'actual_resolution_percentage':s.render.resolution_percentage,'reflection_override':reflection,'PNG_sha256':sha(p)},indent=2)+'\n')
 else:
  checkpoint={**config,'config_sha256':config_sha,'PNG_sha256':sha(png),'PNG_bytes':png.stat().st_size,'EXR_saved':False,'art_accepted':False}
  if not reuse:
   tmp=cp.with_suffix('.tmp');tmp.write_text(json.dumps(checkpoint,indent=2)+'\n');tmp.replace(cp)
  view.update(PNG_sha256=sha(png),checkpoint_file=cp.name,reused_verified_checkpoint=reuse)
 report['views'].append(view)
if not preview:(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
