"""Compare exact native gray/material geometry before reusing original dark shell in whole layout."""
import bpy,numpy as np,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'creative/research/whole-exterior-coverage-v7';rows=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['rear-mudguard-shell-features-v1.blend','rear-mudguard-shell-v1.blend']:
 p=R/'assets-src/moto-components/rear-mudguard-shell'/name;before=sha(p)
 with bpy.data.libraries.load(str(p),link=True)as(a,b):assert 'WEWA_REAR_MUDGUARD_SHELL_ISOLATED'in a.collections;b.collections=['WEWA_REAR_MUDGUARD_SHELL_ISOLATED']
 objects=[o for o in b.collections[0].all_objects if o.type=='MESH'and not o.hide_render];assert len(objects)==1;m=objects[0].data;h=hashlib.sha256()
 for collection,prop,n,dt in [(m.vertices,'co',3,np.float32),(m.loops,'vertex_index',1,np.int32),(m.corner_normals,'vector',3,np.float32),(m.uv_layers.active.data,'uv',2,np.float32)]:
  data=np.empty(len(collection)*n,dt);collection.foreach_get(prop,data);h.update(data.tobytes())
 rows.append(dict(source=str(p.relative_to(R)),source_sha256=before,source_unchanged=sha(p)==before,mesh_name=objects[0].name,vertices=len(m.vertices),loops=len(m.loops),geometry_cornerNormals_UV_digest=h.hexdigest()))
assert rows[0]['geometry_cornerNormals_UV_digest']==rows[1]['geometry_cornerNormals_UV_digest'];(O/'rear-fender-material-reuse-check.json').write_text(json.dumps(dict(protocol_sha256=sha(Path(__file__)),sources=rows,exact_geometry_cornerNormals_UV_equal=True,scope='Original material source reused without source geometry edits; no fidelity/material/installed receipt'),indent=2)+'\n');print('EXACT_REAR_SHELL_GEOMETRY_REUSED')
