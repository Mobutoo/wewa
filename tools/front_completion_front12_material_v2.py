# Parent SHA256 7b0077ed6afb1d8e82ef9b5a34b32a29c8f16ffcc54e3e05f6618f743c1e8e7e; clean opaque-plastic/warm-metal author hypotheses added, parent unchanged.
# Parent SHA256 4aa979e079f5a31bff897f5e3e717f0592db4afaa18fddd588a074ab18bc029e; explicit clean rubber/offwhite collar appearance hypotheses only.
"""Uniform clean material hypothesis after explicit gray preview review, geometry unmodified."""
import bpy,sys,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');key,stem,kind=sys.argv[sys.argv.index('--')+1:][:3];H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;review=json.loads((O/'gray-preview-review.json').read_text());assert review['images_actually_read'] and review['proceed_to_material_hypothesis']
p=H/(stem+'-gray.blend');bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.preferences.filepaths.save_version=0
appearance=[]
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 if kind=='black-plastic':color,metal,rough=(.018,.020,.019,1),0,.38
 elif kind=='warm-metal':color,metal,rough=(.48,.40,.20,1),1,.30
 elif kind=='rubber':color,metal,rough=(.022,.024,.021,1),0,.68
 elif kind=='white-collar' and 'SLEEVE' not in ob.name:color,metal,rough=(.65,.64,.57,1),0,.38
 elif kind=='white-collar':color,metal,rough=(.15,.16,.17,1),1,.30
 else:color,metal,rough=(.62,.64,.66,1),1,.28
 m=bpy.data.materials.new(kind+' clean appearance hypothesis '+ob.name);m.use_nodes=True;n=m.node_tree.nodes['Principled BSDF'];n.inputs['Base Color'].default_value=color;n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough;ob.data.materials.clear();ob.data.materials.append(m);appearance.append({'object':ob.name,'color_linear':color,'metallic':metal,'roughness':rough})
bpy.ops.wm.save_as_mainfile(filepath=str(H/(stem+'-material.blend')),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/(stem+'-material.glb')),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
(O/'material-plan.json').write_text(json.dumps({'gray_source':str(p.relative_to(R)),'gray_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'appearance':{'kind':kind,'base_color_linear':color,'metallic':metal,'roughness':rough,'per_object':appearance,'textures':'none','grain':'none invented'},'measured':False,'limits':['Uniform clean hypothesis only','No exact alloy, treatment, wear, surface grain or calibrated reflectance claim'],'gray_preview_actually_read':review['images_actually_read'],'art_accepted':False},indent=2))
