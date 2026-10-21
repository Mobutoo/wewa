"""Actual final source geometry with explicit G3 lineage; no new shape fabricated by G4."""
from pathlib import Path
import bpy,json,hashlib,sys
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/ignition-key-ring-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'build-report.json').read_text());source=H/'ignition-key-ring-v1.blend';assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import check_mesh
objects=[bpy.data.objects[q['name']]for q in B['geometry']];rows=[check_mesh(o)for o in objects];assert rows==B['geometry'];count=0
for o in objects:
 assert not o.modifiers;o.data.calc_loop_triangles();assert all(t.area>0 for t in o.data.loop_triangles);count+=len(o.data.loop_triangles)
assert count==B['triangles'];q=json.loads((O/'protected-export-invariants.json').read_text());assert q['source_sha256']==sha(source)and all(r['actual_native_bytes_identical']for r in q['attributes']);r={**B,'geometry':rows,'source_all_faces_are_triangles':True,'current_material_only_revision':True,'lineage':'G3splithelix is protected exactly in native buffers and source signatures; current check confirms retained final source closure/area/count, not new CSG or gauge compliance.','art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==B['source_sha256'];print(json.dumps({'source_sha256':sha(source),'triangles':count,'geometry':rows}))
