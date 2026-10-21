"""Decode actual GLB accessors independently and compare Babylon morph arrays.

Versioned successor to the frozen v1 checker; selected catalogue asset required.
This checks CPU target arrays/influences, not GPU feedback or mechanical travel.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('asset')
parser.add_argument('--port', type=int, default=4143)
args = parser.parse_args()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
catalog = json.loads((ROOT/'tools/motorcycle-lab/catalog.json').read_text())
config = catalog['assets'][args.asset]
assert len(config['files']) == len(config['morph_controls']) == 1
control = config['morph_controls'][0]
source = ROOT/'assets-src/moto-components'/config['source']
export = ROOT/'assets-src/moto-components'/config['files'][0]
review = ROOT/'creative/reviews'/config['review']
report_path = review/'source-geometry-check.json'
source_report = json.loads(report_path.read_text())
assert sha(source) == source_report['source_sha256']
assert sha(export) == source_report['export_sha256']
data = export.read_bytes()
assert struct.unpack_from('<III', data)[:2] == (0x46546C67, 2)
length, chunk_type = struct.unpack_from('<II', data, 12)
assert chunk_type == 0x4E4F534A
doc = json.loads(data[20:20+length])
binary_size, binary_type = struct.unpack_from('<II', data, 20+length)
assert binary_type == 0x004E4942
blob = data[28+length:28+length+binary_size]
node = next(n for n in doc['nodes'] if n.get('name') == control['node'])
mesh = doc['meshes'][node['mesh']]
assert len(mesh['primitives']) == 1
primitive = mesh['primitives'][0]
assert mesh['extras']['targetNames'] == [control['target_low'], control['target_high']]


sparse_accessors = []


def accessor(index):
    entry = doc['accessors'][index]
    assert entry['componentType'] == 5126 and entry['type'] == 'VEC3'
    assert not entry.get('normalized', False)
    if 'bufferView' in entry:
        view = doc['bufferViews'][entry['bufferView']]
        values = np.ndarray((entry['count'], 3), dtype='<f4', buffer=blob,
                            offset=view.get('byteOffset', 0)+entry.get('byteOffset', 0),
                            strides=(view.get('byteStride', 12), 4)).astype(float)
    else:
        values = np.zeros((entry['count'], 3), dtype=float)
    if 'sparse' in entry:
        sparse = entry['sparse']
        ids, replacements = sparse['indices'], sparse['values']
        iview, vview = doc['bufferViews'][ids['bufferView']], doc['bufferViews'][replacements['bufferView']]
        assert 'byteStride' not in iview and 'byteStride' not in vview
        dtype = {5121: '<u1', 5123: '<u2', 5125: '<u4'}[ids['componentType']]
        selected = np.frombuffer(blob, dtype=dtype, count=sparse['count'],
                                 offset=iview.get('byteOffset', 0)+ids.get('byteOffset', 0)).astype(np.int64)
        assert len(selected) and selected[0] >= 0 and selected[-1] < entry['count']
        assert np.all(np.diff(selected) > 0)
        replacement_values = np.frombuffer(blob, dtype='<f4', count=sparse['count']*3,
                                           offset=vview.get('byteOffset', 0)+replacements.get('byteOffset', 0))
        values[selected] = replacement_values.reshape(-1, 3)
        sparse_accessors.append({'accessor': index, 'count': entry['count'],
                                 'sparse_count': sparse['count'], 'implicit_zero_base': 'bufferView' not in entry})
    assert np.isfinite(values).all()
    return values


base = accessor(primitive['attributes']['POSITION'])
deltas = [accessor(t['POSITION']) for t in primitive['targets']]
indices = np.unique(np.linspace(0, len(base)-1, 61, dtype=int))
states = []
for state in source_report['morph_states']:
    positions = base + sum(w*d for w, d in zip(state['weights'], deltas))
    lower, upper = state['bounds_min_m'], state['bounds_max_m']
    expected = {'min': [lower[0], lower[2], -upper[1]],
                'max': [upper[0], upper[2], -lower[1]]}
    for key, values in [('min', positions.min(0)), ('max', positions.max(0))]:
        assert np.max(abs(values-expected[key])) < 2e-8
    value = (control['rest'] + state['weights'][0]*(control['min']-control['rest'])
             + state['weights'][1]*(control['max']-control['rest']))
    states.append({'name': state['name'], 'weights': state['weights'], 'value': value,
                   'min': positions.min(0).tolist(), 'max': positions.max(0).tolist(),
                   'samples': positions[indices].tolist()})
assert len(states) == 5
inspector = ROOT/'tools/motorcycle-lab/review-v3.js'
pins = {str(p.relative_to(ROOT)): sha(p) for p in [source, export, report_path, inspector, Path(__file__)]}
results = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=[
        '--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    page = browser.new_page()
    page.goto(f'http://127.0.0.1:{args.port}/tools/motorcycle-lab/v3.html?asset='+args.asset,
              wait_until='networkidle', timeout=120000)
    page.wait_for_function('window.__MOTO_LAB__?.scene.isReady()', timeout=90000)
    downloaded = page.request.get(f'http://127.0.0.1:{args.port}/'+str(export.relative_to(ROOT)))
    assert downloaded.ok and hashlib.sha256(downloaded.body()).hexdigest() == sha(export)
    page.evaluate('window.__MOTO_LAB__.engine.stopRenderLoop()')
    for state in states:
        page.evaluate('(p)=>window.__MOTO_LAB__.setPose(p)', {control['id']: state['value']})
        actual = page.evaluate('''({name, ids})=>{
          const m=window.__MOTO_LAB__.scene.getMeshByName(name);
          const base=m.getVerticesData('position'),manager=m.morphTargetManager;
          const positions=Float64Array.from(base),weights=[];
          for(let k=0;k<manager.numTargets;k++){
            const target=manager.getTarget(k),p=target.getPositions();weights.push(target.influence);
            for(let i=0;i<positions.length;i++)positions[i]+=target.influence*(p[i]-base[i]);
          }
          const low=[Infinity,Infinity,Infinity],high=[-Infinity,-Infinity,-Infinity];
          for(let i=0;i<positions.length;i+=3)for(let j=0;j<3;j++){
            low[j]=Math.min(low[j],positions[i+j]);high[j]=Math.max(high[j],positions[i+j]);
          }
          return {min:low,max:high,weights,samples:ids.map(i=>Array.from(positions.slice(i*3,i*3+3))),
                  matrix:m.computeWorldMatrix(true).asArray()};
        }''', {'name': control['node'], 'ids': indices.tolist()})
        error = max(float(np.max(abs(np.array(actual[k])-state[k]))) for k in ['min', 'max', 'samples'])
        assert error < 2e-8, (state['name'], error)
        assert actual['weights'] == state['weights']
        assert np.max(abs(np.array(actual['matrix']).reshape(4, 4)-np.eye(4))) < 1e-7
        results.append({'state': state['name'], 'value_mm': state['value'], 'weights': actual['weights'],
                        'actual_bounds_glTF_m': {'min': actual['min'], 'max': actual['max']},
                        'all_vertex_bounds_and_61_samples_max_difference_m': error})
    browser.close()
assert all(sha(ROOT/p) == digest for p, digest in pins.items())
report = {'asset': args.asset, 'revision': config['review'], 'input_hashes': pins,
          'source_sha256': sha(source), 'export_sha256': sha(export),
          'tool_path': str(Path(__file__).relative_to(ROOT)), 'tool_sha256': sha(Path(__file__)),
          'inspector_path': str(inspector.relative_to(ROOT)), 'inspector_sha256': sha(inspector),
          'HTTP_export_bytes_verified': True, 'samples_per_state': len(indices), 'states': results,
          'decoded_sparse_accessors': sparse_accessors,
          'scope': 'Independent Python binary accessor decoder versus actual Babylon absolute target arrays and influences. Five states; all-vertex bounds also match source report. CPU target-array parity, not GPU feedback, mechanical travel, elastic fit, shader parity or physical iPhone qualification.',
          'technical_passed': True, 'art_accepted': False}
(review/'browser-morph-parity-v2.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'states': len(results), 'max_difference_m': max(
    x['all_vertex_bounds_and_61_samples_max_difference_m'] for x in results)}))
