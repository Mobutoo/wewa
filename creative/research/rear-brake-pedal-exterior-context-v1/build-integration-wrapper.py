"""Same context geometry/poses; direct mesh-object wrapper for stock coordinator checker. No mesh/material copy or edit."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix
R=Path('/workspace/wewa');K='rear-brake-pedal-exterior-context-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;D=R/'creative/research'/K;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();meta=json.loads((D/'native-links-and-transforms.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
COL='REAR_BRAKE_PEDAL_EXTERIOR_INTEGRATION_V1';col=bpy.data.collections.new(COL);bpy.context.scene.collection.children.link(col);root=bpy.data.objects.new('REAR_BRAKE_PEDAL_EXTERIOR_CONTEXT_ROOT',None);col.objects.link(root);root['physical_count_increment']=0;root['fit_qualified']=False;rows=[]
for row in meta['parents']:
 p=R/row['source'];assert sha(p)==row['sha256']
 with bpy.data.libraries.load(str(p),link=True)as(a,b):b.objects=list(row['objects'])
 for original in b.objects:
  ob=original.copy();col.objects.link(ob);ob.parent=root;ob.matrix_basis=Matrix(row['matrix'])@original.matrix_world;ob['source_native_object']=original.name;ob['role']=row['role'];assert ob.data==original.data and all(a.material==b.material for a,b in zip(ob.material_slots,original.material_slots));assert ob.data.library and ob.library is None
  rows.append(dict(parent=row['parent'],object=ob.name,source_object=original.name,source=row['source'],source_sha256=row['sha256'],shared_exact_source_mesh_datablock=True,source_materials_unchanged=True,matrix=[list(r)for r in ob.matrix_basis],role=row['role']))
assert len(rows)==4
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
bpy.context.scene.unit_settings.system='METRIC';source=H/'integration-wrapper.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
(D/'integration-wrapper-equivalence.json').write_text(json.dumps(dict(source=str(source.relative_to(R)),sha256=sha(source),collection=COL,root=root.name,objects=rows,same_as_review_source='Original linked mesh datablocks and exact same four rigid matrices; object wrappers only, no geometry/material changes',review_source_sha256=sha(H/(K+'.blend')),physical_count_increment=0,fit_qualified=False),indent=2)+'\n')
# A single linked exemplar tests the actual stock coordinator contract, identity local review pose.
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(source),link=True)as(a,b):b.collections=[COL]
inst=bpy.data.objects.new('COVERAGE_PARENT ['+K+']',None);bpy.context.scene.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=b.collections[0]
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
ex=H/'coord-exemplar.blend';bpy.ops.wm.save_as_mainfile(filepath=str(ex),compress=True)
(O/'linked-parents-check.json').write_text(json.dumps(dict(source=str(ex.relative_to(R)),source_sha256=sha(ex),parent_count=1,parents=[dict(key=K,source=str(source.relative_to(R)),sha256=sha(source),collection=COL,selected_objects=[],translation_m=[0,0,0],rotation_degrees=[0,0,0],scale=[1,1,1])],scope='Identity local context, stock checker compatibility only; no world mounting/fit'),indent=2)+'\n')
