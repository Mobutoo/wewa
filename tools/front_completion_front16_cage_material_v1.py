"""DF201058 gray-white molded polymer appearance hypothesis; geometry unchanged."""
from pathlib import Path
import bpy,sys,json,hashlib
R=Path('/workspace/wewa');key,stem=sys.argv[sys.argv.index('--')+1:][:2];H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key
d=json.loads((O/'gray-preview-review.json').read_text());assert d['images_actually_read'] and d['proceed_to_material_hypothesis']
p=H/(stem+'-gray.blend');bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.preferences.filepaths.save_version=0
m=bpy.data.materials.new('DF201058 gray-white molded polymer hypothesis, no certified resin');m.use_nodes=True;n=m.node_tree.nodes['Principled BSDF'];n.inputs['Base Color'].default_value=(.48,.50,.49,1);n.inputs['Metallic'].default_value=0;n.inputs['Roughness'].default_value=.45
for ob in bpy.data.objects:
 if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(m)
bpy.ops.wm.save_as_mainfile(filepath=str(H/(stem+'-material.blend')),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/(stem+'-material.glb')),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
(O/'material-plan.json').write_text(json.dumps({'gray_source':str(p.relative_to(R)),'gray_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'base_color_linear':[.48,.50,.49,1],'metallic':0,'roughness':.45,'textures':[],'measured':False,'limits':['Uncalibrated source lighting and white balance','No resin, grain, aging or exact roughness certification','G4 held'],'gray_preview_actually_read':d['images_actually_read'],'art_accepted':False},indent=2))
