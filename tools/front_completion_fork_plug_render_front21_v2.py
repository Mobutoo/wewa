# Parent SHA256 b7ec22e8ecb58858eb4d9e8625c9870e39d079fb0940374264501fa9f2010228; native render explicitly culls observed skin backfaces, matching single-sided GLB, no hidden wall.
# Parent SHA256 86605d1aa568be0d4ef2c9ed951d015d56b4abd0d3ddfdac5ac785f3352460e7; upright plug and actual mouth macro views, no parent edits.
# Parent SHA256 0e0a43d8fe75ab386540f4491d09cc11d430c538d345788902ab2bc18a8b700a; backside fill added for actual exposed reverse readability, parent immutable.
# Parent exact SHA256 238eea78efe03a97adec4f65359c92c0cbee84c9e815e6150da3990699c83c06; new front/reverse exposed-casting four-view protocol, parent unchanged.
# Parent SHA256 c11ecf2c5aad3fb31f50730bae6316bfa2a41e6a0c726985634d7a89b33cb3b3; native dimensions corrected in report only, existing parent unchanged.
# Small isolated unit protocol, native900x750 EXR/PNG96 samples, no resize. Parent SHA256 3e28844cbd59e242af02a13a790342c5f432d954f53aacc11860554ca6f0c425
# New round-part framing; historical v1 unchanged. Parent SHA256 4fdc276f0da09f208dcbf3af41b2e29e98973fea995c05bca65cd126d2a2233f
"""New front10 isolated protocol, reuses versioned camera preflight. Never overwrites historical proofs."""
import bpy,sys,json,hashlib,runpy
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');key,stem,stage,quality=sys.argv[sys.argv.index('--')+1:][:4];H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key/(stage+('-96' if quality=='final' else '-preview-f21-v2'));(O/'raw').mkdir(parents=True,exist_ok=False);source=H/(stem+'-'+stage+'.blend');bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
check=runpy.run_path(str(R/'tools/blender_component_camera_preflight.py'))['check_component_camera'];objects=[o for o in bpy.data.objects if o.type=='MESH'];coords=[o.matrix_world@Vector(p)for o in objects for p in o.bound_box];low=Vector([min(p[i]for p in coords)for i in range(3)]);high=Vector([max(p[i]for p in coords)for i in range(3)]);target=(low+high)/2;size=max(high-low)
for ob in list(bpy.data.objects):
 if ob.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(ob,do_unlink=True)
w=bpy.data.worlds.new('Neutral studio estimate');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.2,.2,.2,1);w.node_tree.nodes['Background'].inputs[1].default_value=.5;s.world=w
for name,direction,power,scale in [('KEY',(-1,-1,2),500,.9),('FILL',(1,2,1),250,.9),('RIM',(0,-2,.5),150,.6),('BACK',(.7,1,-2),350,.9)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power*size*size;d.size=size*scale;ob=bpy.data.objects.new(name,d);s.collection.objects.link(ob);ob.location=target+size*Vector(direction);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Isolated camera',bpy.data.cameras.new('Isolated camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.50;cam.data.clip_start=size*.001;cam.data.clip_end=size*100
s.render.engine='CYCLES';s.cycles.samples=96 if quality=='final' else 24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=900;s.render.resolution_y=750;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.use_stamp=False
views=[('whole-quarter',(1,-2,1.6)),('whole-side',(0,-2,.2)),('reflection',(1,-2,1)),('mouth-macro',(.4,-.8,2))]if stage=='gray'else[('whole-quarter',(1,-2,1.6)),('whole-side',(-1,-2,.3)),('neutral',(1,-2,1.6)),('mouth-macro',(.4,-.8,2))];rows=[]

def native_single_sided(mat):
 # Cycles does not enforce raster backface-culling; transparent backfaces replicate it.
 nt=mat.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');links=list(out.inputs['Surface'].links)
 if not links:return
 prior=links[0].from_socket;nt.links.remove(links[0]);geo=nt.nodes.new('ShaderNodeNewGeometry');transparent=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(geo.outputs['Backfacing'],mix.inputs[0]);nt.links.new(prior,mix.inputs[1]);nt.links.new(transparent.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
for mat in bpy.data.materials:
 if mat.use_nodes:native_single_sided(mat)

for name,direction in views:
 if name=='reflection':
  mat=bpy.data.materials.new('Temporary reflection diagnostic');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.3,.3,.3,1);p.inputs['Metallic'].default_value=.8;p.inputs['Roughness'].default_value=.12
  native_single_sided(mat)
  for ob in objects:ob.data.materials.clear();ob.data.materials.append(mat)
 if name=='neutral':
  for light in bpy.data.lights:light.energy=0
  nt=s.world.node_tree;tex=nt.nodes.new('ShaderNodeTexEnvironment');tex.image=bpy.data.images.load(str(R/'app/public/materials/kloppenheim_06_puresky_1k.hdr'));nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs[0]);nt.nodes['Background'].inputs[1].default_value=.65
 cam.data.ortho_scale=size*(.76 if name=='mouth-macro' else 1.50);viewtarget=target+Vector((0,0,size*.24)) if name=='mouth-macro' else target;cam.location=viewtarget+size*Vector(direction);cam.rotation_euler=(viewtarget-cam.location).to_track_quat('-Z','Y').to_euler();s.view_layers[0].update();preflight=check(s,objects,allow_crop=name=='mouth-macro');s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';exr=O/'raw'/(name+'.exr');png=O/(name+'.png');s.render.filepath=str(exr);bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(png),scene=s)
 rows.append({'view':name,'samples':s.cycles.samples,'resolution':[900,750],'camera':list(cam.location),'target':list(viewtarget),'ortho_scale':cam.data.ortho_scale,'camera_preflight':preflight,'PNG':str(png.relative_to(R)),'EXR':str(exr.relative_to(R))});(O/'render-report.json').write_text(json.dumps({'source':str(source.relative_to(R)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'protocol':'tools/front_completion_fork_plug_render_front21_v2.py','protocol_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'views':rows,'observed_skin_backfaces':'Transparent in native renderer to match single-sided GLB; no hidden geometry added','denoising':False,'material_stage':stage=='material','art_accepted':False},indent=2))
