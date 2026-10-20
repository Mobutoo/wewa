"""Bind only this revision's fabrication evidence, never the historical v1 or coordinator captures."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;OUT=ROOT/'creative/reviews/handlebar-grips-v2'
local=['parameters-v2.json','build_v2.py','render_v2.py','check_export_v2.mjs','record_review_v2.py','README_v2.md','provenance-v2.json','build-report-v2.json','handlebar-grips-v2.blend','handlebar-grips-v2-inspection.glb','textures-v2/rubber-metallic-roughness.png']
proof=['README.md','source-geometry-check.json','export-check.json','render-report.json','left-quarter.png','right-quarter.png']
files=[HERE/p for p in local]+[OUT/p for p in proof]
rows=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
source=json.loads((OUT/'source-geometry-check.json').read_text());render=json.loads((OUT/'render-report.json').read_text())
assert source['source_sha256']==render['source_sha256']==hashlib.sha256((HERE/'handlebar-grips-v2.blend').read_bytes()).hexdigest()
(OUT/'review-manifest.json').write_text(json.dumps({'revision':'handlebar-grips-v2','scope':'Explicit fabrication whitelist; coordinator engine captures tracked separately','files':rows,'art_accepted':False,'physical_iphone_tested':False},indent=2)+'\n')
print('Bound',len(rows),'v2 files; no v1 files mutated')
