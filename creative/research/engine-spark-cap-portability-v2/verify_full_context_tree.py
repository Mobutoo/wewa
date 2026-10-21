"""Blender CLI: open EVERY moved source of a public context graph, assert all actual Library/data paths remain in moved tree. No save/render/export."""
import bpy,argparse,sys,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for s in ['tree-plan','report']:p.add_argument('--'+s,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);plan=json.loads(Path(a.tree_plan).read_text());root=Path(plan['test_root']).resolve();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();expected={r['source']:r['sha256']for r in plan['files']};rows=[]
for entry in plan['files']:
 source=root/entry['source'];assert sha(source)==entry['sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));libraries=[]
 for lib in bpy.data.libraries:
  resolved=Path(bpy.path.abspath(lib.filepath,library=lib.parent)).resolve();assert resolved.is_relative_to(root),(entry['source'],lib.filepath,'escaped moved tree',resolved);rel=str(resolved.relative_to(root));assert resolved.is_file()and sha(resolved)==expected[rel];assert not lib.is_missing
  libraries.append({'name':lib.name,'stored_path':lib.filepath,'parent':lib.parent.name if lib.parent else None,'target':rel,'actual_resolved':str(resolved),'sha256':sha(resolved),'missing':lib.is_missing})
 direct=sorted(l['target']for l in libraries if l['parent']is None);assert direct==entry['expected_direct_link_targets'],(entry['source'],'direct closure differs',direct,entry['expected_direct_link_targets'])
 linked_objects=[]
 for o in bpy.data.objects:
  if o.library:
   owner=Path(bpy.path.abspath(o.library.filepath,library=o.library.parent)).resolve();assert owner.is_relative_to(root)and not o.is_missing
   if o.type=='MESH':assert not o.data.is_missing and len(o.data.vertices)>0
   linked_objects.append({'name':o.name,'type':o.type,'library_target':str(owner.relative_to(root)),'missing':o.is_missing,'mesh_vertices':len(o.data.vertices)if o.type=='MESH'else None})
 rows.append({'source':entry['source'],'source_sha256':sha(source),'libraries':libraries,'actual_direct_link_count':len(direct),'linked_objects':linked_objects,'every_loaded_library_inside_moved_tree':True});assert sha(source)==entry['sha256'];print('CHECKED_MOVED_CONTEXT',entry['source'],len(direct),flush=True)
report={'tree_plan_sha256':sha(a.tree_plan),'tool_sha256':sha(__file__),'sources_opened':len(rows),'direct_links_verified':sum(r['actual_direct_link_count']for r in rows),'test_root':str(root),'sources':rows,'all_direct_and_indirect_libraries_resolved_inside_moved_tree':True,'all_linked_objects_nonmissing':True,'originals_or_test_sources_saved':False,'no_render_export':True};Path(a.report).write_text(json.dumps(report,indent=2)+'\n');print('FULL_MOVED_CONTEXT_CHECK_PASSED',len(rows),report['direct_links_verified'],flush=True)
