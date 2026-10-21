"""Explicit neutral master for material reconstruction, never replace a closed input."""
from pathlib import Path
import json,hashlib,shutil
H=Path(__file__).resolve().parent;O=H.parents[2]/'creative/reviews/engine-protection-end-weld-a-v1';base=H/'g3-master-v1';base.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();q=json.loads((O/'gray-review.json').read_text());assert q['ready_for_partial_surface_material_candidate'];a=json.loads((O/'self-surface-check.json').read_text());assert a['nonadjacent_noncoplanar_surface_crossings']==0
for p in [H/'engine-protection-end-weld-a-v1.blend',H/'engine-protection-end-weld-a-inspection.glb']+[O/(n+'.json')for n in ['source-geometry-check','geometry-check','self-surface-check','source-interface-check']]:
 t=base/p.name
 if t.exists():assert sha(t)==sha(p),'Never replace neutral master'
 else:shutil.copyfile(p,t)
(base/'README.md').write_text('Original neutral partial external weld-A master. Rebuild build.py/check_export.mjs/inspect_self.py then preserve these neutral files before material.py. No rearcontinuation or penetration, actualattenuatedwindowendcaps are constructionboundaries not measuredweldends. Guide/context never exported.\n')
print('WELD_A_G3_ARCHIVED')
