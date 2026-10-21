"""Blender CLI verify a moved checkout: all actual loaded Library targets must stay in it.
Does not save, render or export. Imports generic fingerprint helper from --helper.
"""
import argparse,sys,json,importlib.util
from pathlib import Path
import bpy
p=argparse.ArgumentParser(description=__doc__)
for v in ['source','checkout-root','baseline-report','helper','report']:p.add_argument('--'+v,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(a.checkout_root).resolve();src=Path(a.source).resolve();baseline=json.loads(Path(a.baseline_report).read_text());assert src.is_relative_to(root);spec=importlib.util.spec_from_file_location('portable_helper',a.helper);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
bpy.ops.wm.open_mainfile(filepath=str(src));fp=m.fingerprint(baseline['component_collection']);links=m.libraries();expected={e['target_repo_relative']:e['target_sha256']for e in baseline['remaps']};checks=[]
for e in links:
 resolved=Path(e['resolved']).resolve();assert resolved.is_relative_to(root),(e,'Library escaped relocated checkout');rel=str(resolved.relative_to(root));assert e['exists']and e['sha256']==expected[rel],e;checks.append({'name':e['name'],'filepath':e['filepath'],'resolved_test_tree_relative':rel,'actual_resolved_path':str(resolved),'sha256':e['sha256'],'inside_test_tree':True})
assert len(links)==len(expected)
context=[]
for o in bpy.data.objects:
 if not o.library:continue
 target=Path(bpy.path.abspath(o.library.filepath,library=o.library.parent)).resolve();assert target.is_relative_to(root)and target.is_file();assert not o.is_missing
 row={'object':o.name,'type':o.type,'owner_library_resolved':str(target),'missing':o.is_missing}
 if o.type=='MESH':
  assert not o.data.is_missing and len(o.data.vertices)>0;data_owner=Path(bpy.path.abspath(o.data.library.filepath,library=o.data.library.parent)).resolve();assert data_owner.is_relative_to(root);row.update({'vertices':len(o.data.vertices),'mesh_data_owner_resolved':str(data_owner),'mesh_missing':o.data.is_missing})
 context.append(row)
result={'source':str(src),'source_sha256':m.sha(src),'checkout_root':str(root),'libraries':checks,'loaded_linked_context_objects':context,'all_libraries_inside_moved_tree':True,'component_exact_vs_original':fp==baseline['before'],'actual_component_fingerprint':fp,'tool_sha256':m.sha(__file__),'helper_sha256':m.sha(a.helper),'baseline_report_sha256':m.sha(a.baseline_report),'no_render_export_save':True};Path(a.report).write_text(json.dumps(result,indent=2)+'\n');assert result['component_exact_vs_original'];print('RELOCATED_OPEN_EXACT',len(links),'LIBRARIES_INSIDE_TEST_TREE',flush=True)
