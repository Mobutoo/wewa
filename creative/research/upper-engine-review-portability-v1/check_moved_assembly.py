"""Blender CLI: open a genuine review assembly in original and moved trees.
Reuse the published component fingerprint helper; no save/render/export/geometry authoring.
Copies only assembly+missing selected libraries into an existing closed moved fixture.
"""
import argparse,sys,json,hashlib,shutil,importlib.util
from pathlib import Path
import bpy
p=argparse.ArgumentParser(description=__doc__)
for s in ['assembly','repository-root','moved-root','source-proof','helper','report']:p.add_argument('--'+s,required=True)
p.add_argument('--collection',default='MOTORCYCLE18_LINKED_REVIEW_COPIES')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(a.repository_root).resolve();moved=Path(a.moved_root).resolve();source=Path(a.assembly).resolve();assert source.is_relative_to(root)and moved.is_dir()and not moved.is_relative_to(root);reportpath=Path(a.report).resolve();reportpath.parent.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();proof=json.loads(Path(a.source_proof).read_text());assert sha(source)==proof['source_sha256'];spec=importlib.util.spec_from_file_location('portable_fingerprint',a.helper);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);expected={e['source']:e['sha256']for e in proof['linked_sources']};preparation=[]
for rel,expected_sha in [(str(source.relative_to(root)),proof['source_sha256']),*expected.items()]:
 src=root/rel;dst=moved/rel;assert sha(src)==expected_sha;existed=dst.exists()
 if existed:assert sha(dst)==expected_sha,(dst,'Existing moved fixture file differs; refusing overwrite')
 else:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 assert sha(dst)==expected_sha;preparation.append({'path':rel,'sha256':expected_sha,'already_in_closed_fixture':existed,'newly_copied':not existed})

def snapshot(path,base):
 bpy.ops.wm.open_mainfile(filepath=str(path));component=helper.fingerprint(a.collection);libraries=[];outside=[];copy_rows=[]
 for lib in bpy.data.libraries:
  target=Path(bpy.path.abspath(lib.filepath,library=lib.parent)).resolve();inside=target.is_relative_to(base);rel=str(target.relative_to(base))if inside else None
  row={'name':lib.name,'stored_path':lib.filepath,'parent':lib.parent.name if lib.parent else None,'resolved':str(target),'inside_opened_tree':inside,'tree_relative':rel,'missing':lib.is_missing,'sha256':sha(target)if target.is_file()else None};libraries.append(row)
  if not inside:outside.append(row)
 for o in bpy.data.collections[a.collection].all_objects:
  if o.type!='MESH':continue
  library=o.data.library;target=Path(bpy.path.abspath(library.filepath,library=library.parent)).resolve()if library else None;inside=bool(target and target.is_relative_to(base));row={'object':o.name,'mesh':o.data.name,'vertices':len(o.data.vertices),'mesh_data_library_resolved':str(target)if target else None,'inside_opened_tree':inside,'library_tree_relative':str(target.relative_to(base))if inside else None,'object_missing':o.is_missing,'mesh_missing':o.data.is_missing};copy_rows.append(row)
  if not inside:outside.append(row)
 world=[]
 if bpy.context.scene.world and bpy.context.scene.world.use_nodes:
  for n in bpy.context.scene.world.node_tree.nodes:
   if hasattr(n,'image')and n.image:world.append({'name':n.image.name,'stored_path':n.image.filepath,'packed':bool(n.image.packed_file),'packed_sha256':hashlib.sha256(n.image.packed_file.data).hexdigest()if n.image.packed_file else None})
 return {'path':str(path),'sha256':sha(path),'component_fingerprint':component,'libraries':libraries,'copied_meshes':copy_rows,'outside_tree':outside,'world_images':world}
original=snapshot(source,root);actual=snapshot(moved/source.relative_to(root),moved);fingerprints_equal=original['component_fingerprint']==actual['component_fingerprint'];actual_sources={e['tree_relative']:e['sha256']for e in actual['libraries']};copy_owners=[e['library_tree_relative']for e in actual['copied_meshes']];result={'schema':1,'tool_sha256':sha(__file__),'helper_sha256':sha(a.helper),'source_proof':str(Path(a.source_proof).resolve()),'source_proof_sha256':sha(a.source_proof),'original_root':str(root),'moved_root':str(moved),'preparation':preparation,'original':original,'moved':actual,'actual_original_source_sha256_preserved':sha(source)==proof['source_sha256'],'component_fingerprint_exact':fingerprints_equal,'selected_library_set_and_SHA_exact':actual_sources==expected,'physical_mesh_copies':len(actual['copied_meshes']),'every_mesh_has_selected_library_owner':all(v in expected for v in copy_owners),'no_library_or_mesh_owner_outside_moved_tree':not actual['outside_tree'],'all_physical_meshes_nonmissing':all(not e['object_missing']and not e['mesh_missing']and e['vertices']>0 for e in actual['copied_meshes']),'world_image_payloads_exact':original['world_images']==actual['world_images'],'no_save_render_export':True}
reportpath.write_text(json.dumps(result,indent=2)+'\n')
assert result['component_fingerprint_exact'],'Actual component fingerprint differs';assert result['selected_library_set_and_SHA_exact'],'Actual selected library set/SHA differs';assert result['physical_mesh_copies']==12;assert result['every_mesh_has_selected_library_owner'];assert result['all_physical_meshes_nonmissing'];assert result['world_image_payloads_exact'];assert result['no_library_or_mesh_owner_outside_moved_tree'],'Actual Library or owner escaped moved tree (diagnostic preserved)';assert result['actual_original_source_sha256_preserved'];print('ACTUAL_MOVED_ASSEMBLY_PASSED',len(actual['libraries']),result['physical_mesh_copies'],flush=True)
