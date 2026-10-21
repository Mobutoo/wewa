"""Before first freeze only: relative direct library, unchanged working geometry."""
from pathlib import Path
import bpy,json,hashlib,array
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-insulator-v1'
assert not (H/'preflight-manifest.json').exists(),'Do not mutate a frozen source'
source=H/'engine-intake-insulator-v1.blend';old=H/'engine-intake-insulator-v1-unrelocated.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)==sha(old)
build=json.loads((H/'build-report.json').read_text());assert sha(source)==build['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source))
def fingerprint():
    rows=[]
    for name in [build['root'],build['geometry'][0]['name']]:
        o=bpy.data.objects[name];row={'name':name,'local_matrix':[list(r)for r in o.matrix_local],'world_matrix':[list(r)for r in o.matrix_world]}
        if o.type=='MESH':
            m=o.data;m.calc_loop_triangles();row.update(vertices=[list(v.co)for v in m.vertices],triangles=[list(t.vertices)for t in m.loop_triangles],
                    normals=[list(v.vector)for v in m.corner_normals],UV={u.name:[list(x.uv)for x in u.data]for u in m.uv_layers},
                    materials=[{'name':mat.name,'inputs':{k:list(p.default_value)if hasattr(p.default_value,'__len__')else p.default_value for k in ['Base Color','Metallic','Roughness']if(p:=mat.node_tree.nodes['Principled BSDF'].inputs.get(k))is not None}}for mat in m.materials])
        rows.append(row)
    return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
before=fingerprint();links=[]
for lib in bpy.data.libraries:
    if lib.parent is not None:continue
    absolute=bpy.path.abspath(lib.filepath);relative=bpy.path.relpath(absolute,start=str(H))
    links.append({'previous':lib.filepath,'relative':relative,'target_sha256':sha(Path(absolute))});lib.filepath=relative
bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False)
bpy.ops.wm.open_mainfile(filepath=str(source));after=fingerprint();assert before==after
assert all(lib.filepath.startswith('//')for lib in bpy.data.libraries if lib.parent is None)
report={'previous_working_source_sha256':sha(old),'source_sha256':sha(source),'export_sha256':build['export_sha256'],
        'direct_library_relocations':links,'full_geometry_normals_UV_materials_and_matrices_before_after_sha256':before,
        'reopened_source_signature_exact':True,'original_direct_link_was_already_relative':all(x['previous']==x['relative']for x in links),'operation_scope':'Verify and resave working source; do not claim a relocation when paths already agree','export_not_modified':True,'frozen_source_modified':False,'art_accepted':False}
build['source_sha256']=sha(source);build['direct_libraries_relative_before_freeze']=True
(H/'build-report.json').write_text(json.dumps(build,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(build,indent=2)+'\n')
(O/'working-packaging-check.json').write_text(json.dumps(report,indent=2)+'\n');print('WORKING_RELATIVE',json.dumps(report))
