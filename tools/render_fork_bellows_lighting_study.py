"""Separate lighting diagnostic; frozen asset/materials unchanged, no source save."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from blender_component_camera_preflight import check_component_camera
source=R/'assets-src/moto-components/front-fork/bellows/fork-bellows-v1.blend';hdr=R/'app/public/materials/kloppenheim_06_puresky_1k.hdr';O=R/'creative/reviews/fork-bellows-lighting-study-v1';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_sha=sha(source);assert source_sha=='fc97e6507c8a757698c39c794fdb38f4ecfc2eab7278d3b1f97a83c66bd7da2c'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;asset=bpy.data.collections['WEWA_FORK_BELLOWS_ISOLATED'].objects[0]
for obj in s.objects:
 if obj.type=='LIGHT':obj.hide_render=True
for key in asset.data.shape_keys.key_blocks:key.value=0
world=bpy.data.worlds.new('Outdoor common HDR diagnostic');world.use_nodes=True;n=world.node_tree.nodes;n.clear();env=n.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(str(hdr));bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.3;out=n.new('ShaderNodeOutputWorld');world.node_tree.links.new(env.outputs['Color'],bg.inputs['Color']);world.node_tree.links.new(bg.outputs[0],out.inputs['Surface']);s.world=world
cam=s.camera;cam.location=(.14,.22,.14);target=Vector((0,0,.0625));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.205;cam.data.clip_start=.001;cam.data.clip_end=10
cards=[];right=cam.rotation_euler.to_quaternion()@Vector((1,0,0))
for name,offset,albedo in [('18 percent gray',-.063,.18),('80 percent white',.063,.8)]:
 bpy.ops.mesh.primitive_plane_add(size=.025,location=target+right*offset);obj=bpy.context.object;obj.name='Diagnostic card '+name;obj.rotation_euler=cam.rotation_euler;mat=bpy.data.materials.new(obj.name);mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(albedo,albedo,albedo,1);p.inputs['Roughness'].default_value=1;p.inputs['Specular IOR Level'].default_value=0;obj.data.materials.append(mat);cards.append(obj)
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=800;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=1
# Preserve the source's display transform and exposure, only light contributions change.
preflight=check_component_camera(s,[asset,*cards]);s.render.image_settings.file_format='PNG';s.render.filepath=str(O/'outdoor-hdr-reference-cards.png');bpy.ops.render.render(write_still=True)
assert sha(source)==source_sha
report={'source_sha256':source_sha,'export_sha256':sha(R/'assets-src/moto-components/front-fork/bellows/fork-bellows-inspection.glb'),'render_script_sha256':sha(Path(__file__)),'source_saved':False,'asset_materials_changed':False,'lights':'Source area lights hidden locally; common outdoor HDR only, strength0.3','HDR_path':str(hdr.relative_to(R)),'HDR_sha256':sha(hdr),'reference_cards':{'left_linear_diffuse':.18,'right_linear_diffuse':.8,'specular':0,'scope':'Lighting references, not calibrated camera or measured HDR radiometry'},'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'samples':16,'resolution_px':[800,900],'preview_only':True,'camera_preflight':preflight,'PNG_sha256':sha(Path(s.render.filepath)),'actual_blender_render':True,'art_accepted':False,'scope':'Independent neutral-light diagnostic to distinguish broad studio reflections from source albedo; no shader parity or photographic certification'}
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('WEWA_LIGHTING_STUDY',report['PNG_sha256'])
