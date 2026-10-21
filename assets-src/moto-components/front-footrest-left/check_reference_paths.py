"""Read-only current source packed relative maps/local frame, no moved-checkout claim."""
from pathlib import Path
import bpy,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/front-footrest-left-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();B=json.loads((H/'build-report.json').read_text());source=H/'front-footrest-left-v1.blend';assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));rows=[]
for row in B['maps']:
 path=H/row['path'];im=next(q for q in bpy.data.images if q.filepath_raw=='//'+row['path']);assert path.exists()and sha(path)==row['sha256']and im.packed_file is not None;rows.append({'relative_path':im.filepath_raw,'exists':True,'packed':True,'sha256':sha(path)})
assert len(bpy.data.libraries)==0;o=bpy.data.objects[B['geometry'][0]['name']];identity=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]];assert[list(q)for q in o.matrix_world]==identity and[list(q)for q in o.parent.matrix_world]==identity;I=json.loads((H/'interfaces.json').read_text());assert not I['automatic_motorcycle_attachment_allowed']and I['suggested_attachment_matrix']is None
r={'source_sha256':sha(source),'export_sha256':B['export_sha256'],'images':rows,'source_libraries':0,'actual_paths_valid':True,'source_mesh_and_datum_identity':True,'automatic_attachment_allowed':False,'frame_role':'isolated inspection, not motorcycle world','moved_checkout_tested':False,'art_accepted':False};(O/'reference-path-check.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==B['source_sha256'];print(json.dumps(r))
