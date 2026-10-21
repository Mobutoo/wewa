"""Packed original images and direct input pins, no relocated checkout claim."""
from pathlib import Path
import bpy,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-header-gasket-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'build-report-v2.json').read_text());source=H/'exhaust-header-gasket-v2.blend';assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));assert len(bpy.data.libraries)==0;rows=[]
for im in bpy.data.images:
 if im.name.startswith('gasket-original-'):
  assert im.packed_file and im.filepath.startswith('//textures/');p=Path(bpy.path.abspath(im.filepath));assert p.is_file();rows.append({'name':im.name,'stored_path':im.filepath,'resolved_sha256':sha(p),'packed':True,'colorspace':im.colorspace_settings.name})
assert len(rows)==3
P=json.loads((H/'parameters-v2.json').read_text());inputs=[]
for key in ['header_interfaces','header_parameters']:
 p=R/P[key];assert sha(p)==P[key+'_sha256'];inputs.append({'path':P[key],'sha256':sha(p)})
x={'source_sha256':sha(source),'export_sha256':B['export_sha256'],'packed_original_maps':rows,'source_libraries':[],'isolated_no_source_library_guides':True,'actual_recipe_input_pins':inputs,'actual_paths_valid':True,'source_changed':False,'scope':'Current relative packed-map resolution and fixed input pins, no relocated checkout experiment or universal portability claim.','art_accepted':False};(O/'reference-path-check.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x))
