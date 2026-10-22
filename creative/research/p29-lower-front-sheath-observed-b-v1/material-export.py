# Reused protocol source SHA256 e1035c4ccc6bff06b1d162bfebb98e10e58913b0dd3433cda0f63419c8f62eb2; own namespace/observed controls.
"""Material stage only after gray images actually read; geometry retained exactly."""
import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');K='p29-lower-front-sheath-observed-b-v1';D=R/'creative/research'/K;H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert (O/'gray-read.json').exists();bpy.ops.wm.open_mainfile(filepath=str(H/'sheath-gray.blend'));bpy.context.preferences.filepaths.save_version=0
objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objects)==1;ob=objects[0];before=[tuple(v.co)for v in ob.data.vertices];faces=[tuple(f.vertices)for f in ob.data.polygons];m=ob.data.materials[0];m.name='Unmeasured black polymer sheath proposal';p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.009,.011,.012,1);p.inputs['Roughness'].default_value=.43;p.inputs['Metallic'].default_value=0;m.diffuse_color=(.009,.011,.012,1);assert before==[tuple(v.co)for v in ob.data.vertices] and faces==[tuple(f.vertices)for f in ob.data.polygons]
bpy.ops.wm.save_as_mainfile(filepath=str(H/'sheath-material.blend'),compress=True);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.gltf(filepath=str(H/(K+'-inspection.glb')),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
(O/'material-geometry-check.json').write_text(json.dumps({'gray_source_sha256':sha(H/'sheath-gray.blend'),'material_source_sha256':sha(H/'sheath-material.blend'),'positions_faces_unchanged':True,'black_polymer_hypothesis_not_measured':True,'no_texture_or_fabricated_grain':True,'art_accepted':False},indent=2))
# A direct collection instance for the unchanged stock whole checker.
source=H/'sheath-material.blend';COL='P29_LOWER_FRONT_SHEATH_OBSERVED_B';bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(source),link=True)as(a,b):b.collections=[COL]
inst=bpy.data.objects.new('COVERAGE_PARENT ['+K+']',None);bpy.context.scene.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=b.collections[0]
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
ex=H/'coord-exemplar.blend';bpy.ops.wm.save_as_mainfile(filepath=str(ex),compress=True)
(O/'linked-parents-check.json').write_text(json.dumps({'source':str(ex.relative_to(R)),'source_sha256':sha(ex),'parent_count':1,'parents':[{'key':K,'source':str(source.relative_to(R)),'sha256':sha(source),'collection':COL,'selected_objects':[],'translation_m':[0,0,0],'rotation_degrees':[0,0,0],'scale':[1,1,1],'nested_sources':[]}],'scope':'Isolated review frame, no certified placement'},indent=2))
