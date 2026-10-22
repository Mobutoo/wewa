"""One unchanged lens/hood pair only, no repetition; isolated review prerequisite for a concrete replication proposal."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];K='indicator-exemplar-context-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(exist_ok=True);O.mkdir(exist_ok=True);stage=sys.argv[sys.argv.index('--')+1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cat=json.loads((R/'tools/motorcycle-lab/catalog.json').read_text())['assets'];gray=H/(K+'-gray.blend');material=H/(K+'-material.blend')
def settings():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.view_layers[0].cycles.denoising_store_passes=True;s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1;bpy.context.preferences.filepaths.save_version=0;return s
if stage=='build':
 bpy.ops.wm.read_factory_settings(use_empty=True);s=settings();s.unit_settings.system='METRIC';rows=[]
 for k in ['indicator-front-lens','indicator-front-housing']:
  c=cat[k];p=R/'assets-src/moto-components'/c['source'];before=sha(p)
  with bpy.data.libraries.load(str(p),link=True)as(a,b):assert c['collection']in a.collections;b.collections=[c['collection']]
  ob=bpy.data.objects.new('REVIEW_PARENT ['+k+']',None);s.collection.objects.link(ob);ob.instance_type='COLLECTION';ob.instance_collection=b.collections[0];rows.append(dict(key=k,source=str(p.relative_to(R)),source_sha256=before,collection=c['collection'],transform='Identity: existing source lens/hood shared review frame, not an installed vehicle pose',export_files=c['files'],source_unchanged=sha(p)==before))
 w=bpy.data.worlds.new('Neutral artistic HDRI');w.use_nodes=True;nt=w.node_tree;tex=nt.nodes.new('ShaderNodeTexEnvironment');tex.image=bpy.data.images.load(str(R/'app/public/materials/kloppenheim_06_puresky_1k.hdr'));nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs['Color']);nt.nodes['Background'].inputs['Strength'].default_value=.65;s.world=w;cam=bpy.data.objects.new('Whole pair camera',bpy.data.cameras.new('Whole pair camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.13;cam.data.clip_start=.0001;cam.data.clip_end=10;g=bpy.data.materials.new('Temporary uniform gray override');g.use_nodes=True;bs=g.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.35;s.view_layers[0].material_override=g
 for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
 bpy.ops.wm.save_as_mainfile(filepath=str(gray),compress=True);(O/'parents.json').write_text(json.dumps(dict(scope='One lens and one housing only, unchanged original sources. No physical ID increment or repetitions; stalk/root/bulb/reflector remain outside this pair.',parents=rows,gray_source_sha256=sha(gray),protocol_sha256=sha(Path(__file__)),art_accepted=False),indent=2)+'\n')
else:
 assert stage in ['gray','material','preview','final'];bpy.ops.wm.open_mainfile(filepath=str(material if stage in ['preview','final']else gray));s=settings()
 if stage=='material':
  assert json.loads((O/'gray-review.json').read_text())['actually_read'];s.view_layers[0].material_override=None;bpy.ops.wm.save_as_mainfile(filepath=str(material),compress=True)
 else:
  if stage=='final':assert json.loads((O/'preview-review.json').read_text())['actually_read']
  views=[('pair-front',(0,-.2,0)),('pair-quarter',(.14,-.20,.095)),('pair-reverse',(-.14,.2,.05))]if stage!='preview'else[('pair-preview',(.14,-.20,.095))];raw=O/'raw';raw.mkdir(exist_ok=True);rows=[]
  for n,eye in views:
   name=stage+'-'+n;target=Vector((0,.01,0));s.camera.location=Vector(eye);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.cycles.samples=96 if stage=='final' else 16;s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(raw/(name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s);rows.append(dict(name=name,samples=s.cycles.samples,PNG_sha256=sha(O/(name+'.png')),EXR_sha256=sha(raw/(name+'.exr')),actually_saved=True))
  (O/(stage+'-render-report.json')).write_text(json.dumps(dict(source_sha256=sha(material if stage in ['preview','final']else gray),views=rows,protocol_sha256=sha(Path(__file__)),scope='Single existing exterior pair review, original materials retained; no fitted indicator unit, source morphology receipt or duplication',art_accepted=False),indent=2)+'\n')
