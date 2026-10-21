"""Read-only final source nativegeometry digest and packed/relative dependencies."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/rear-mudguard-shell-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'rear-mudguard-shell-v1.blend';glb=H/'rear-mudguard-shell-inspection.glb';a=json.loads((O/'source-geometry-check.json').read_text());assert a['source_sha256']==sha(src)and a['export_sha256']==sha(glb);bpy.ops.wm.open_mainfile(filepath=str(src));obs=list(bpy.data.collections['WEWA_REAR_MUDGUARD_SHELL_ISOLATED'].objects);assert len(obs)==1 and not obs[0].modifiers;m=obs[0].data;h=hashlib.sha256()
for c,p,n,dt in [(m.vertices,'co',3,np.float32),(m.loops,'vertex_index',1,np.int32),(m.corner_normals,'vector',3,np.float32),(m.uv_layers.active.data,'uv',2,np.float32)]:
 x=np.empty(len(c)*n,dt);c.foreach_get(p,x);h.update(x.tobytes())
assert h.hexdigest()==a['source_geometry_N_UV_digest_preserved'];libraries=[l.filepath for l in bpy.data.libraries];assert not libraries;images=[]
for im in bpy.data.images:
 if im.source!='FILE':continue
 rel=im.filepath.startswith('//');packed=bool(im.packed_file);assert packed and rel and Path(bpy.path.abspath(im.filepath)).exists();images.append({'name':im.name,'filepath':im.filepath,'packed':packed,'relative':rel})
assert len(images)==2
r={'source_sha256':sha(src),'export_sha256':sha(glb),'native_geometry_positions_indices_cornernormals_UV_digest':h.hexdigest(),'native_digest_preserved_after_material_save':True,'external_libraries':libraries,'file_images':images,'packed_relative_images':2,'runtime_export_objects':[o.name for o in obs],'studio_guide_geometry_exported':False,'uninstalled_local_frame':True,'installed_fit_certified':False,'art_accepted':False};(O/'source-portability-check.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(src)==a['source_sha256'];print('REAR_SHELL_SOURCE_PORTABLE',json.dumps(r))
