import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p23-endplate-front9-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
p=H/'endplate-gray.blend';bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.preferences.filepaths.save_version=0
m=bpy.data.materials.new('Clean plated metal estimate no measured finish');m.use_nodes=True;n=m.node_tree.nodes['Principled BSDF'];n.inputs['Base Color'].default_value=(.62,.64,.66,1);n.inputs['Metallic'].default_value=1;n.inputs['Roughness'].default_value=.28
for ob in bpy.data.objects:
 if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(m)
bpy.ops.wm.save_as_mainfile(filepath=str(H/'endplate-material.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'endplate-material.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
(O/'material-plan.json').write_text(json.dumps({'gray_source':str(p.relative_to(R)),'gray_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'appearance':{'base_color_linear':[.62,.64,.66,1],'metallic':1,'roughness':.28,'textures':'none','grain':'none invented'},'measured':False,'limits':['Uniform clean metal study only; yellow conversion coating, wear and exact alloy not reproduced','No material fidelity or OEM reflectance claimed','No calibrated color/roughness measurements'],'gray_preview_actually_read':['preview/gray-quarter.png','preview/reflection.png'],'art_accepted':False},indent=2))
