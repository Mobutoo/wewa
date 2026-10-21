"""Read-only actual direct libraries, no relocated checkout claim."""
from pathlib import Path
import bpy,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-heatshield-fastener-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();b=json.loads((H/'build-report.json').read_text());P=json.loads((H/'parameters.json').read_text());source=H/'exhaust-heatshield-fastener-v1.blend';assert sha(source)==b['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));rows=[]
for lib in bpy.data.libraries:
 path=Path(bpy.path.abspath(lib.filepath,library=lib.parent));assert path.is_file()
 if lib.parent is None:assert lib.filepath.startswith('//')
 rows.append({'stored_path':lib.filepath,'parent_library':lib.parent.filepath if lib.parent else None,'resolved_path':str(path),'sha256':sha(path),'direct':lib.parent is None})
for key in ['shield_source','body_source']:assert any(q['sha256']==P[key+'_sha256']for q in rows)
r={'source_sha256':sha(source),'export_sha256':b['export_sha256'],'actual_loaded_libraries':rows,'direct_libraries_relative':True,'all_loaded_targets_exist':True,'test_scope':'Actual direct relative resolution only; no moved checkout claim. Existing guide materials packed, not copied as local screw texture.','art_accepted':False};(O/'reference-path-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
