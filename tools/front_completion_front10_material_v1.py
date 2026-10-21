"""Uniform clean material hypothesis after explicit gray preview review, geometry unmodified."""
import bpy,sys,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');key,stem,kind=sys.argv[sys.argv.index('--')+1:][:3];H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;review=json.loads((O/'gray-preview-review.json').read_text());assert review['images_actually_read'] and review['proceed_to_material_hypothesis']
p=H/(stem+'-gray.blend');bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.preferences.filepaths.save_version=0
color,metal,rough=((.018,.022,.019,1),0,.32)if kind=='black-coating'else((.62,.64,.66,1),1,.28)
m=bpy.data.materials.new('Uniform '+kind+' hypothesis, no measured finish');m.use_nodes=True;n=m.node_tree.nodes['Principled BSDF'];n.inputs['Base Color'].default_value=color;n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough
for ob in bpy.data.objects:
 if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(m)
bpy.ops.wm.save_as_mainfile(filepath=str(H/(stem+'-material.blend')),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/(stem+'-material.glb')),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
(O/'material-plan.json').write_text(json.dumps({'gray_source':str(p.relative_to(R)),'gray_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'appearance':{'kind':kind,'base_color_linear':color,'metallic':metal,'roughness':rough,'textures':'none','grain':'none invented'},'measured':False,'limits':['Uniform clean hypothesis only','No exact alloy, treatment, wear, surface grain or calibrated reflectance claim'],'gray_preview_actually_read':review['images_actually_read'],'art_accepted':False},indent=2))
