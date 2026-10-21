"""Inspect the reopened material .blend, keeping original geometry and UVs explicit."""
import bpy,hashlib,json
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/side-cover-left';O=R/'creative/reviews/side-cover-left-study-v1'
p=H/'side-cover-left-candidate-v1.blend';assert Path(bpy.data.filepath).resolve()==p.resolve();ob=bpy.data.objects['LEFT_COVER_OUTER_SKIN'];m=ob.data;m.calc_loop_triangles()
digest=hashlib.sha256(repr(([(tuple(v.co))for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],[(tuple(u.uv))for u in m.uv_layers.active.data])).encode()).hexdigest()
base=json.loads((O/'geometry-check.json').read_text());assert digest==base['geometry_digest'];counts=Counter(tuple(sorted((a,b))) for f in m.polygons for a,b in zip(list(f.vertices),list(f.vertices[1:])+[f.vertices[0]]));assert sum(n==1 for n in counts.values())==240;assert all(n<=2 for n in counts.values());assert min(t.area for t in m.loop_triangles)>0
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(O/'source-geometry-check.json').write_text(json.dumps(dict(source_sha256=sha(p),export_sha256=sha(H/'side-cover-left-candidate-v1.glb'),source_reopened=True,triangles=len(m.loop_triangles),geometry_digest=digest,gray_material_geometry_uv_identical=True,open_review_boundary_edges=240,protocol_sha256=sha(Path(__file__)),scope='Actual reopened source and gray/material UV+geometry equality; not hidden fit, exact sections or artistic reception'),indent=2)+'\n')
