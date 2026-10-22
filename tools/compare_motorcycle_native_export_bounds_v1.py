"""Compare independently evaluated native and imported glTF world bounds; no mechanical-measurement claim."""
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument('native');p.add_argument('gltf');p.add_argument('output');a=p.parse_args();n=json.loads(Path(a.native).read_text());g=json.loads(Path(a.gltf).read_text());lookup={r['key']:r for r in g['parents']};rows=[]
assert len(lookup)==len(n['parents'])
for r in n['parents']:
 b=lookup[r['key']]['export_bounds_gltf'];x=[b['min'],b['max']];delta=max(abs(r['bounds_gltf'][i][j]-x[i][j])for i in range(2)for j in range(3));assert delta<1e-5,(r['key'],delta);rows.append(dict(key=r['key'],max_abs_world_bound_delta_m=delta))
Path(a.output).write_text(json.dumps(dict(scope='Actual evaluated native and independently imported glTF world bounds. Export/placement consistency only; not physical dimensions or per-triangle parity',native_report=a.native,gltf_proof=a.gltf,parents=rows,maximum_delta_m=max(r['max_abs_world_bound_delta_m']for r in rows)),indent=2)+'\n');print('BOUNDS_AGREE',len(rows),max(r['max_abs_world_bound_delta_m']for r in rows))
