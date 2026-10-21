"""Report actual direct library path resolution before first freeze; no save."""
from pathlib import Path
import bpy,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-heatshield-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();b=json.loads((H/'build-report.json').read_text());source=H/'exhaust-heatshield-v1.blend'
assert sha(source)==b['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));rows=[]
for lib in bpy.data.libraries:
    path=Path(bpy.path.abspath(lib.filepath,library=lib.parent))
    assert path.is_file(),path
    if lib.parent is None:assert lib.filepath.startswith('//'),lib.filepath
    rows.append({'stored_path':lib.filepath,'parent_library':lib.parent.filepath if lib.parent else None,
                 'resolved_path':str(path),'sha256':sha(path),'direct':lib.parent is None})
P=json.loads((H/'parameters.json').read_text());expected=[P['body_source_sha256']];assert all(any(x['sha256']==key for x in rows)for key in expected)
maps=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.name.startswith('heatshield-original-'):
        assert im.packed_file and im.filepath.startswith('//textures/'),(im.name,im.filepath)
        p=Path(bpy.path.abspath(im.filepath));assert p.is_file()
        maps.append({'name':im.name,'path':im.filepath,'packed':True,'file_sha256':sha(p),'colorspace':im.colorspace_settings.name})
assert len(maps)==2
report={'maps':maps,'source_sha256':sha(source),'export_sha256':b['export_sha256'],'actual_loaded_libraries':rows,
        'direct_libraries_relative':True,'all_loaded_targets_exist':True,'source_modified':False,
        'test_scope':'Actual current resolution and relative direct links. No relocated-checkout test or universal portability claim.',
        'art_accepted':False}
(O/'reference-path-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(source)==b['source_sha256'];print('REFERENCE_PATHS',json.dumps(report))
