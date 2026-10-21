"""Compare an independently evaluated Blender edge vertex with the loaded Babylon vertex.

Requires an explicit frozen source-axis spec and a catalog key; changes no inspector.
The spec must contain rest and at least three nonzero combined two-axis poses.
"""
import argparse
import datetime
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def convert(point):
    return [point[0], point[2], -point[1]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog-key', required=True)
    parser.add_argument('--spec', required=True)
    parser.add_argument('--out-dir', required=True)
    parser.add_argument('--url', default='http://127.0.0.1:4143/tools/motorcycle-lab/v4.html')
    parser.add_argument('--catalog', default='tools/motorcycle-lab/catalog.json')
    parser.add_argument('--inspector', default='tools/motorcycle-lab/review-v4.js')
    parser.add_argument('--blender', default='/workspace/wewa-tools/blender-4.3.2-linux-x64/blender')
    parser.add_argument('--chromium', default='/usr/bin/chromium')
    parser.add_argument('--cpu', type=int, help='Explicit available CPU for the short threads1 source extraction')
    parser.add_argument('--tolerance-m', type=float, default=2e-7)
    args = parser.parse_args()
    from playwright.sync_api import sync_playwright
    spec_path = Path(args.spec).resolve()
    spec = json.loads(spec_path.read_text())
    catalog_path = ROOT / args.catalog
    config = json.loads(catalog_path.read_text())['assets'][args.catalog_key]
    entry_bytes = json.dumps(config, sort_keys=True).encode()
    assert config['source'] == spec['source'].removeprefix('assets-src/moto-components/')
    assert config['files'] == [spec['export'].removeprefix('assets-src/moto-components/')]
    assert not config.get('placements'), 'Explicit placements require a separate source contract'
    for field in ['source', 'export', 'source_parameters']:
        assert digest(ROOT / spec[field]) == spec[field + '_sha256'], 'Unfrozen ' + field
    rotations = spec['source_rotation_order']
    ids = [r['control_id'] for r in rotations]
    assert len(ids) == 2
    rigs = {r['id']: r for r in config['rigs']}
    for key in ids:
        assert rigs[key]['node'] == spec['pivot']
    assert all(set(p['controls']) == set(ids) for p in spec['poses'])
    assert any(all(v == 0 for v in p['controls'].values()) for p in spec['poses'])
    combined = [p for p in spec['poses'] if all(abs(p['controls'][k]) > 0 for k in ids)]
    assert len(combined) >= 3, 'Need at least three genuinely combined rotations'
    assert len({tuple(p['controls'][k] for k in ids) for p in combined}) >= 3
    assert len({p['name'] for p in spec['poses']}) == len(spec['poses'])
    for item in spec['poses']:
        for key, value in item['controls'].items():
            assert rigs[key]['min'] <= value <= rigs[key]['max'], 'Pose would be clamped'
    output = Path(args.out_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    witness_path = output / 'Blender-source-witness.json'
    report_path = output / 'browser-source-motion-parity.json'
    log = output / 'Blender-source-extraction.log'
    assert not any(p.exists() for p in [witness_path, report_path, log]), 'Use a fresh output directory'
    extractor = ROOT / 'tools/extract_blender_rotation_witness.py'
    inspector_path = ROOT / args.inspector
    inspector_hash = digest(inspector_path)
    cmd = [args.blender, '--background', '--threads', '1', '--python-exit-code', '1',
           '--python', str(extractor), '--', '--spec', str(spec_path), '--out', str(witness_path)]
    if args.cpu is not None:
        cmd = ['taskset', '-c', str(args.cpu), *cmd]
    with log.open('w') as handle:
        subprocess.run(cmd, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, check=True, timeout=180)
    witness = json.loads(witness_path.read_text())
    assert witness['spec_sha256'] == digest(spec_path)
    assert witness['source_sha256'] == spec['source_sha256']
    assert witness['export_sha256'] == spec['export_sha256']
    assert witness['extractor_sha256'] == digest(extractor)
    states_by_name = {s['name']: s for s in witness['states']}
    assert all(states_by_name[p['name']]['order_separation_m'] > args.tolerance_m * 10
               for p in combined), 'The witness must distinguish rotation order'
    neutral = next(s for s in witness['states'] if all(v == 0 for v in s['controls'].values()))
    expected_rest = convert(neutral['evaluated_Blender_world_m'])
    javascript_errors, http_errors, glb_responses = [], [], []
    path_suffix = '/assets-src/moto-components/' + config['files'][0]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=args.chromium, args=[
            '--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        page = browser.new_page()
        page.on('pageerror', lambda error: javascript_errors.append(str(error)))

        def response_seen(response):
            if response.status >= 400:
                http_errors.append({'url': response.url, 'status': response.status})
            if urlsplit(response.url).path == path_suffix:
                glb_responses.append(response)

        page.on('response', response_seen)
        separator = '&' if '?' in args.url else '?'
        page.goto(args.url + separator + 'asset=' + quote(args.catalog_key),
                  wait_until='networkidle', timeout=120000)
        page.wait_for_function('window.__MOTO_LAB__?.scene.isReady()', timeout=90000)
        page.evaluate('window.__MOTO_LAB__.engine.stopRenderLoop()')
        assert glb_responses, 'No actual loaded GLB response captured'
        loaded_hashes = [hashlib.sha256(r.body()).hexdigest() for r in glb_responses]
        assert all(h == spec['export_sha256'] for h in loaded_hashes)
        loaded_config = page.evaluate('window.__MOTO_LAB__.config')
        assert loaded_config == config, 'Browser catalog differs from local selected entry'
        page.evaluate('p => window.__MOTO_LAB__.setPose(p)', neutral['controls'])
        match = page.evaluate('''args => {
          const meshes = window.__MOTO_LAB__.scene.meshes.filter(m => m.name === args.mesh && m.getTotalVertices());
          if (meshes.length !== 1) throw Error('Expected one actual named edge mesh');
          const mesh = meshes[0], positions = mesh.getVerticesData('position'), matrix = mesh.computeWorldMatrix(true).asArray();
          let best = {distance:Infinity}, equivalent = 0;
          for (let i=0;i<positions.length;i+=3) {
            const [x,y,z] = positions.slice(i,i+3);
            const world = [x*matrix[0]+y*matrix[4]+z*matrix[8]+matrix[12],x*matrix[1]+y*matrix[5]+z*matrix[9]+matrix[13],x*matrix[2]+y*matrix[6]+z*matrix[10]+matrix[14]];
            const distance = Math.hypot(...world.map((v,j)=>v-args.expected[j]));
            if(distance < args.tolerance) equivalent++;
            if(distance < best.distance) best={mesh:mesh.name,vertex_index:i/3,distance,rest_world_glTF_m:world};
          }
          return {...best,coincident_exported_vertices_within_tolerance:equivalent};
        }''', {'mesh': spec.get('browser_mesh', spec['witness_mesh']), 'expected': expected_rest,
               'tolerance': args.tolerance_m})
        assert match['distance'] < args.tolerance_m, match
        results = []
        for state in witness['states']:
            actual_controls = page.evaluate('p => window.__MOTO_LAB__.setPose(p)', state['controls'])
            assert all(abs(actual_controls[k] - state['controls'][k]) < 1e-10 for k in ids)
            actual = page.evaluate('''a => {
              const mesh=window.__MOTO_LAB__.scene.getMeshByName(a.mesh), p=mesh.getVerticesData('position');
              const m=mesh.computeWorldMatrix(true).asArray(), i=a.vertex_index*3, [x,y,z]=p.slice(i,i+3);
              return [x*m[0]+y*m[4]+z*m[8]+m[12],x*m[1]+y*m[5]+z*m[9]+m[13],x*m[2]+y*m[6]+z*m[10]+m[14]];
            }''', match)
            expected = convert(state['evaluated_Blender_world_m'])
            reverse = convert(state['reverse_order_Blender_world_m'])
            results.append({'name': state['name'], 'controls': state['controls'],
                            'actual_Babylon_world_glTF_m': actual,
                            'evaluated_Blender_world_glTF_m': expected,
                            'distance_m': math.dist(actual, expected),
                            'reverse_order_Blender_world_glTF_m': reverse,
                            'distance_to_reverse_order_m': math.dist(actual, reverse),
                            'source_order_separation_m': state['order_separation_m']})
        browser.close()
    assert digest(inspector_path) == inspector_hash, 'Inspector changed during test'
    assert json.dumps(json.loads(catalog_path.read_text())['assets'][args.catalog_key], sort_keys=True).encode() == entry_bytes
    for field in ['source', 'export', 'source_parameters']:
        assert digest(ROOT / spec[field]) == spec[field + '_sha256']
    maximum = max(s['distance_m'] for s in results)
    passed = maximum < args.tolerance_m and not javascript_errors and not http_errors
    report = {'schema': 'wewa.blender-babylon-ordered-rotation-parity.v1',
              'date_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'catalog_key': args.catalog_key, 'spec_sha256': digest(spec_path),
              'source_sha256': spec['source_sha256'], 'export_sha256': spec['export_sha256'],
              'loaded_GLTF_response_sha256': loaded_hashes,
              'extractor_sha256': digest(extractor), 'tool_sha256': digest(__file__),
              'inspector_sha256': inspector_hash,
              'catalog_selected_entry_sha256': hashlib.sha256(entry_bytes).hexdigest(),
              'source_witness_path': str(witness_path), 'source_witness_sha256': digest(witness_path),
              'actual_source_vertex': {'mesh': witness['witness_mesh'],
                                       'evaluated_index': witness['source_evaluated_vertex_index']},
              'actual_matched_Babylon_vertex': match, 'states': results,
              'tolerance_m': args.tolerance_m, 'max_error_m': maximum,
              'combined_states': len(combined), 'javascript_errors': javascript_errors,
              'http_errors': http_errors, 'Blender_cpu_requested': args.cpu,
              'technical_passed': passed, 'art_accepted': False,
              'scope': 'Same real edge vertex evaluated independently in Blender and loaded Babylon, rest plus combined two-axis poses with reverse-order counter-witness. Not all vertices, optical parity, mechanical travel, OEM fit or physical iPhone validation.'}
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'states': len(results), 'max_error_m': maximum, 'technical_passed': passed}))
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
