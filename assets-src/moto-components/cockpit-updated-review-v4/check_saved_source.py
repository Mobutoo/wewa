"""Read-only check of the actual saved18-source composition and its rest matrices."""
from pathlib import Path
import bpy,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/cockpit-updated-review-v4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((O/'source-geometry-check.json').read_text());source=H/'cockpit-updated-review-v4.blend';assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
assert len(B['linked_sources'])==18
library_rows=[]
for lib in bpy.data.libraries:
 assert lib.filepath.startswith('//'),lib.filepath
 path=Path(bpy.path.abspath(lib.filepath));assert path.is_file();expected=next((r for r in B['actual_libraries']if r['path']==str(path.relative_to(R))),None);assert expected and sha(path)==expected['sha256'];library_rows.append({'path':str(path.relative_to(R)),'stored_relative_path':lib.filepath,'sha256':sha(path)})
rows=[]
for row in B['linked_sources']:
 c=next(c for c in s.collection.children if c.name==row['source_collection']);actual=[]
 for o in c.all_objects:
  if o.type!='MESH':continue
  before=next(q['matrix']for q in row['actual_rest_world_matrices']if q['object']==o.name);after=[list(q)for q in o.matrix_world];assert before==after,(row['asset'],o.name);actual.append(o.name)
 assert len(actual)==row['mesh_objects'];rows.append({'asset':row['asset'],'source_sha256':row['sha256'],'actual_meshes':len(actual),'all_saved_rest_world_matrices_identical':True})
for image in B['material_file_images']:
 if image['packed']:continue
 path=R/image['path'];assert sha(path)==image['sha256']
report={'source_sha256':sha(source),'linked_primary_source_count':len(rows),'actual_library_count':len(library_rows),'libraries':library_rows,'collections':rows,'all_library_paths_relative':True,'source_rest_matrices_preserved':True,'new_physical_geometry_created':False,'relocated_checkout_tested':False,'scope':'Actual same-checkout reopen and relative library resolution, not a claim of moved-checkout execution or accepted assembly fit. No source modified.','art_accepted':False};(O/'saved-source-link-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(source)==B['source_sha256'];print('ACTUAL_COCKPIT_SAVED_LINKS18_PASS')
