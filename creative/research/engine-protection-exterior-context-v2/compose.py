# Template SHA256 abe6d2cf53402881eb3fa45af2d6fb56e3fc0c8fd964dd169889b3a68b646755; recovered guide pose revision.
"""Four exact linked parent meshes/materials; identity hoop, explicitly parked accessories."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/workspace/wewa');K='engine-protection-exterior-context-v2';D=R/'creative/research'/K;H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parents=json.loads((D/'parent-native-read.json').read_text())['parents'];plan=json.loads((D/'plan.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
COL='ENGINE_PROTECTION_EXISTING_KIT_CONTEXT_V2';col=bpy.data.collections.new(COL);bpy.context.scene.collection.children.link(col);root=bpy.data.objects.new('ENGINE_PROTECTION_HOOP_IDENTITY_ROOT',None);col.objects.link(root);root['component_id']='MOTO-ENGINE-PROTECTION-HOOP-001';root['new_physical_ids']=0;root['mounted_kit_ready']=False;rows=[]
for p in parents:
 assert sha(R/p['source'])==p['sha256'];row=p['objects'][0];pose=plan['poses'][p['key']];T=Matrix(pose['common_transform']);world=Matrix(row['matrix_world']);mat=T@world
 with bpy.data.libraries.load(str(R/p['source']),link=True)as(a,b):b.objects=[row['name']]
 original=b.objects[0];ob=original.copy();ob.animation_data_clear();col.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=mat;assert ob.data==original.data and ob.data.library;assert all(a.material==b.material for a,b in zip(ob.material_slots,original.material_slots));ob['pose_role']=pose['role'];ob['mounted_fit_qualified']=False
 rows.append({'object':ob.name,'source_object':row['name'],'key':p['key'],'source':p['source'],'source_sha256':p['sha256'],'glb':p['glb'],'glb_sha256':p['glb_sha256'],'matrix_source_world':[list(v)for v in world],'common_transform':[list(v)for v in T],'matrix_context':[list(v)for v in mat],'shared_exact_linked_mesh':True,'materials_unchanged':True,'role':pose['role']})
bpy.context.view_layer.update()
for r in rows:assert max(abs(bpy.data.objects[r['object']].matrix_world[i][j]-r['matrix_context'][i][j])for i in range(4)for j in range(4))<1e-6
# Actual positive AABB display separations; no posed contact/surface claim.
gaps=[]
for i,a in enumerate(rows):
 va=[bpy.data.objects[a['object']].matrix_world@Vector(x)for x in bpy.data.objects[a['object']].bound_box]
 for b in rows[i+1:]:
  vb=[bpy.data.objects[b['object']].matrix_world@Vector(x)for x in bpy.data.objects[b['object']].bound_box];delta=[max(0,max(min(v[k]for v in va)-max(v[k]for v in vb),min(v[k]for v in vb)-max(v[k]for v in va)))for k in range(3)];distance=Vector(delta).length;gaps.append({'a':a['key'],'b':b['key'],'AABB_display_separation_m':distance,'not_joint_clearance':True})
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
bpy.context.scene.unit_settings.system='METRIC';source=H/'integration-wrapper.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
(D/'native-links-and-transforms.json').write_text(json.dumps({'source':str(source.relative_to(R)),'source_sha256':sha(source),'root':root.name,'collection':COL,'objects':rows,'hoop_exact_identity':True,'recovered_guide_pose_hypothesis':True,'nominal_joint_display_gap_m':.003,'display_separations':gaps,'new_physical_ids':0,'fit_qualified':False,'art_accepted':False},indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(source),link=True)as(a,b):b.collections=[COL]
inst=bpy.data.objects.new('COVERAGE_PARENT ['+K+']',None);bpy.context.scene.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=b.collections[0]
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
ex=H/'coord-exemplar.blend';bpy.ops.wm.save_as_mainfile(filepath=str(ex),compress=True)
(O/'linked-parents-check.json').write_text(json.dumps({'source':str(ex.relative_to(R)),'source_sha256':sha(ex),'parent_count':1,'parents':[{'key':K,'source':str(source.relative_to(R)),'sha256':sha(source),'collection':COL,'selected_objects':[],'translation_m':[0,0,0],'rotation_degrees':[0,0,0],'scale':[1,1,1],'nested_sources':[{'source':p['source'],'sha256':p['sha256']}for p in parents]}],'scope':'Four-parent separated review, not mounted accessory transforms'},indent=2))
