"""Check pinned sources, preserved GLB bytes, cleanup and native-resolution captures."""
import argparse
import copy
import hashlib
import json
import struct
from pathlib import Path
from derive_handlebar_registration_v2 import decode

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'creative/reviews/visual-proportions-v2'
ASSETS = ROOT / 'assets-src/moto-components/visual-proportions-v2'
def read(path):
    return json.loads(path.read_text())
def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument('--write', action='store_true')
args = parser.parse_args()
paths = []
for folder in [ASSETS, OUT, ROOT/'creative/research/visual-proportions-v2', ROOT/'tools/visual-proportions-review-v2']:
    paths.extend(p for p in folder.rglob('*') if p.is_file() and p.name != 'manifest.json')
paths.extend((ROOT/'tools').glob('*visual_proportions*v2.*'))
paths.append(ROOT/'creative/workflow/records/moto-visual-proportions-002.json')
if args.write:
    (OUT/'manifest.json').write_text(json.dumps({'files': [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(set(paths))]}, indent=2)+'\n')
manifest = read(OUT/'manifest.json')
assert {r['path'] for r in manifest['files']} == {str(p.relative_to(ROOT)) for p in paths}
for row in manifest['files']:
    path = ROOT/row['path']
    assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], row['path']
plan = read(ROOT/'creative/research/visual-proportions-v2/plan.json')
report = read(OUT/'composition-check.json')
native = read(OUT/'native-check.json')
base, bb = decode((ROOT/plan['source_glb']).read_bytes())
new, nb = decode((ASSETS/'motorcycle-proportions.glb').read_bytes())
add, ab = decode((ASSETS/'proportion-additions.glb').read_bytes())
assert nb == bb + ab
assert len(native['changes']) == len(plan['changes']) == len(report['changed_parent_nodes']) == 21
assert sha(ROOT/plan['source_glb']) == report['source_sha256']
assert sha(ASSETS/'motorcycle-proportions.glb') == report['output_sha256']
for table in ['nodes', 'meshes', 'materials', 'accessors', 'bufferViews', 'images', 'textures', 'samplers']:
    original = copy.deepcopy(new[table][:len(base[table])])
    if table == 'nodes':
        for index in report['changed_parent_nodes']:
            original[index] = base[table][index]
    assert original == base[table], table
removed = {i for i, n in enumerate(base['nodes']) if n.get('name') in plan['deactivated_roots']}
assert len(removed) == 1
assert new['scenes'][0]['nodes'] == [i for i in base['scenes'][0]['nodes'] if i not in removed] + [i+len(base['nodes']) for i in add['scenes'][0]['nodes']]
def mul(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
C = [[1,0,0,0], [0,0,1,0], [0,-1,0,0], [0,0,0,1]]
Ci = list(map(list, zip(*C)))
for change in native['changes']:
    node = next(n for n in new['nodes'] if n.get('name') == change['name'])
    expected = mul(mul(C, change['after_blender']), Ci)
    assert max(abs(node['matrix'][j*4+i]-expected[i][j]) for i in range(4) for j in range(4)) < 1e-6, change['name']
# Reconstruct the raw index streams and prove cleanup changed nothing else.
raw, rb = decode((ASSETS/'proportion-additions-raw.glb').read_bytes())
cleanup = read(OUT/'triangle-cleanup.json')
assert sha(ASSETS/'proportion-additions-raw.glb') == cleanup['raw_sha256']
assert sha(ASSETS/'proportion-additions.glb') == cleanup['clean_sha256']
restored, restored_binary = copy.deepcopy(add), bytearray(ab)
assert sum(r['removed_triangles'] for r in cleanup['removed']) == 125
for row in cleanup['removed']:
    mesh = next(m for m in raw['meshes'] if m['name'] == row['mesh'])
    index = mesh['primitives'][row['primitive']]['indices']
    accessor = raw['accessors'][index]
    view_index = accessor['bufferView']
    view = raw['bufferViews'][view_index]
    start = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
    size, fmt = {5123: (2, 'H'), 5125: (4, 'I')}[accessor['componentType']]
    indices = struct.unpack_from('<'+fmt*accessor['count'], rb, start)
    excluded = set(row['triangle_indices'])
    assert len(excluded) == row['removed_triangles']
    kept = [v for i, v in enumerate(indices) if i//3 not in excluded]
    expected = struct.pack('<'+fmt*len(kept), *kept)
    assert ab[start:start+len(expected)] == expected
    assert add['accessors'][index]['count'] == len(kept)
    restored_binary[start:start+size*len(indices)] = rb[start:start+size*len(indices)]
    restored['accessors'][index] = accessor
    restored['bufferViews'][view_index] = view
assert restored == raw and bytes(restored_binary) == rb
procedural = [r for r in native['new_meshes'] if r['name'] not in native['replacement_meshes']]
assert len(procedural) == 30 and all(r['non_manifold_edges'] == 0 and r['volume_m3'] > 0 for r in procedural)
export = read(OUT/'export-check.json')
assert all(r['issues']['numErrors'] == 0 and sha(ROOT/r['path']) == r['sha256'] for r in export['validations'])
assert len(export['parts']) == 31 and export['triangles'] == 193909
measured = read(OUT/'measured-check.json')
assert measured['rear_axle_and_wheels_fixed'] and measured['native_cowl_topology_preserved']
before, after = measured['measurements']
assert abs(after['swingarm_pivot_axis_slope_deg']-before['swingarm_pivot_axis_slope_deg']-9) < .01
assert after['housing_depth_m']/before['housing_depth_m'] > 1.6
browser = read(OUT/'browser-check.json')
assert not browser['page_errors'] and not browser['http_failures'] and len(browser['captures']) == 10
for row in browser['captures']:
    data = (OUT/row['file']).read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    expected = (3840, 2880) if row['file'].startswith(('front', 'rear')) else (2560, 1920)
    assert struct.unpack('>II', data[16:24]) == expected and hashlib.sha256(data).hexdigest() == row['sha256']
    assert row['runtime']['textures_ready'] and set(row['runtime']['text_meshes']) == {'Plate text Art.', 'Plate text 015'}
print(json.dumps({'valid': True, 'pinned_files': len(manifest['files']), 'registrations': 21, 'closed_new_meshes': 30, 'reprofiled_cowl': 1, 'captures': 10, 'art_accepted': False}, indent=2))
