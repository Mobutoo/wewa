import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');old='front-completion-p03-flap-v2';key='front-completion-p03-flap-material-v2';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);source=R/'assets-src/moto-components'/old/'gray.blend';bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
mat=bpy.data.materials.new('Original clean black flap appearance estimate');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.008,.009,.010,1);p.inputs['Roughness'].default_value=.48;p.inputs['Metallic'].default_value=0
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.data.objects:
 if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(mat);ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.wm.save_as_mainfile(filepath=str(H/'flap-material.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'flap-material.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
(O/'material-plan.json').write_text(json.dumps({'gray_source':str(source.relative_to(R)),'gray_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'gray_images_actually_read':['front-completion-p03-flap-v2/preview/gray-quarter.png','front-completion-p03-flap-v2/preview/reflection.png'],'read_for':'limited exterior appearance study, not geometry fidelity acceptance','parameters':{'base_color_linear':[.008,.009,.010,1],'roughness':.48,'metallic':0,'grain':'none invented','textures':'none'},'measured':False,'art_accepted':False},indent=2))
