"""Read actual historical A boundary only; no historical model write."""
from pathlib import Path
import bpy,json,hashlib
R=Path('/workspace/wewa');p=R/'assets-src/moto-components/p29-lower-front-sheath-observed-a-v1/sheath-material.blend'
bpy.ops.wm.open_mainfile(filepath=str(p));o=next(o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render)
v=[list(x.co) for x in list(o.data.vertices)[-64:]]
out=R/'creative/research/front-brake-cable-visible-continuity-v1/actual-original-A-upper-ring.json'
out.write_text(json.dumps({'source':str(p.relative_to(R)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'object':o.name,'actual_boundary_positions_local_m':v,'scope':'Only64 coincident interface positions, not copied old route; preserves actual final sampled-ring tilt.'},indent=2))
