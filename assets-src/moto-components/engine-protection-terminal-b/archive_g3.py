"""Preserve exact neutral master before original material, never overwrite it."""
from pathlib import Path
import json,hashlib,shutil
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-protection-terminal-b-v1';base=H/'g3-master-v1';base.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();q=json.loads((O/'gray-review.json').read_text());assert q['ready_for_partial_surface_material_candidate'];s=json.loads((O/'self-surface-check.json').read_text());assert s['nonadjacent_noncoplanar_surface_crossings']==0
for p in [H/'engine-protection-terminal-b-v1.blend',H/'engine-protection-terminal-b-inspection.glb']+[O/(n+'.json')for n in ['source-geometry-check','geometry-check','source-interface-check','self-surface-check']]:
 target=base/p.name
 if target.exists():assert sha(target)==sha(p),'Never replace a G3master'
 else:shutil.copyfile(p,target)
(base/'README.md').write_text('Neutral independently constructed terminalB master. Rebuild with ../build.py then ../check_export.mjs and ../inspect_interfaces.py and ../inspect_self.py, compare the recorded hashes/digests. This additive master is the explicit geometry input to ../material.py. The working lower envelope is not a claim of absent OEM lower hole. No photo pixels or parent runtime proofs.\n')
print('TERMINAL_B_G3_ARCHIVED')
