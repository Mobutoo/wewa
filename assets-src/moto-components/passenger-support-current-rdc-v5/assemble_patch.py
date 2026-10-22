import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix
O=Path(__file__).resolve().parent;R=O.parents[2];A=R/'assets-src/moto-components/passenger-support-current-rdc-v4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda n,d:(O/n).write_text(json.dumps(d,indent=2)+'\n')
bpy.ops.wm.open_mainfile(filepath=str(A/'context-material-linked.blend'));bpy.context.preferences.filepaths.save_version=0;group=bpy.data.collections['CURRENT_RDC_PASSENGER_SUPPORT_V4'];group.name='CURRENT_RDC_PASSENGER_SUPPORT_V5';changed=[];patch=[];old=json.loads((A/'integration-fragment.json').read_text());combined=old['additions'];src=O/'upper-cut-correction-v5.blend'
for side in ['LH','RH']:
 key=side+' CURRENT_RDC forward-peg-support observed';ob=bpy.data.objects[key];before=[list(r)for r in ob.matrix_world]
 with bpy.data.libraries.load(str(src),link=True)as(a,b):b.objects=[key]
 ob.data=b.objects[0].data;ob['source_file']=str(src.relative_to(R));assert before==[list(r)for r in ob.matrix_world];changed.append(ob)
 row={'key':key,'source':str(src.relative_to(R)),'sha256':sha(src),'selected_objects':[key],'matrix_world':before,'nested':[],'source_class':'photo_inferred / estimated X at concealed upper cut','revision_delta':'Only first source-trace X +/-145mm -> +/-120mm. All Y/Z controls, subsequent X controls, section and matrices unchanged.'};patch.append(row)
 combined=[row if r['key']==key else r for r in combined]
write('integration-fragment-v5.json',{'id':'passenger-support-current-rdc-v5','parents_to_remove':[r['key']for r in patch],'additions':patch,'retained_from_v4':[r for r in combined if r['key']not in[r['key']for r in patch]],'complete_candidate_inventory':combined,'count':{'replacement_meshes':2,'retained_v4_meshes':6,'combined_meshes':8},'convention':old['convention'],'scope':'Minimal two-stem upper-cut depth correction after native96 visual defect. No guard/peg/rubber changes, no hidden connectors.','fit_qualified':False,'art_accepted':False})
bpy.context.view_layer.update();s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();native=[]
for ob in changed:
 ev=ob.evaluated_get(dg);me=ev.to_mesh();points=[ob.matrix_world@v.co for v in me.vertices];native.append({'name':ob.name,'bounds':[[min(v[i]for v in points)for i in range(3)],[max(v[i]for v in points)for i in range(3)]],'matrix_world':[list(r)for r in ob.matrix_world]});ev.to_mesh_clear()
write('native-evaluated-world.json',native)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'context-material-linked.blend'),compress=True,relative_remap=False);bpy.ops.object.select_all(action='DESELECT')
for ob in changed:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'upper-cuts-material.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
gray=bpy.data.materials.new('v5 neutral upper-cut diagnostic');gray.use_nodes=True;gray.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.25,.25,.25,1);gray.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.45
for ob in changed:
 ob.data=ob.data.copy()
 for i in range(len(ob.data.materials)):ob.data.materials[i]=gray
bpy.ops.export_scene.gltf(filepath=str(O/'upper-cuts-gray.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
s.view_layers[0].material_override=gray;bpy.ops.wm.save_as_mainfile(filepath=str(O/'context-gray-linked.blend'),compress=True,relative_remap=False)
print('V5_PATCH_READY',sha(src))
