import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');D=R/'creative/research/gear-selector-exterior-context-v1';H=R/'assets-src/moto-components/gear-selector-exterior-context-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(H/'gear-selector-exterior-context-v1.blend'));bpy.context.view_layer.update();rows=[]
for inst in bpy.context.evaluated_depsgraph_get().object_instances:
 ob=inst.object
 if ob.type!='MESH':continue
 assert inst.is_instance and ob.original.library and ob.data.library
 assert all(m.library for m in ob.data.materials)
 pts=[inst.matrix_world@v.co for v in ob.data.vertices]
 rows.append(dict(object=ob.name,source_library=bpy.path.abspath(ob.original.library.filepath),matrix_world=[list(r) for r in inst.matrix_world],vertices=len(ob.data.vertices),bounds_m=dict(min=[min(p[i] for p in pts) for i in range(3)],max=[max(p[i] for p in pts) for i in range(3)]),materials=[dict(name=m.name,library=bpy.path.abspath(m.library.filepath)) for m in ob.data.materials],geometry_and_materials_external_links=True))
assert len(rows)==7
sources=json.loads((D/'native-links-and-transforms.json').read_text())['parents']
for p in sources:assert sha(R/p['source'])==p['sha256']
assert bpy.context.scene.view_layers[0].material_override is None
(D/'native-context-read.json').write_text(json.dumps(dict(mesh_instances=rows,source_hashes_unchanged=True,original_materials_linked=True,source_gray_override_saved=False,new_physical_ids=0,art_accepted=False),indent=2)+'\n')
