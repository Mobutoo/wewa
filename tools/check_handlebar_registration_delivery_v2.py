"""Verify the exact candidate delivery and its evidence; do not award acceptance."""
import argparse
import hashlib
import json
from pathlib import Path

from derive_handlebar_registration_v2 import derive

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'creative/reviews/handlebar-registration-v2'
MANIFEST = REVIEW / 'production-manifest.json'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text())


def check():
    plan = ROOT / 'creative/research/handlebar-registration-v2/plan.json'
    native = read(REVIEW / 'native-check.json')
    exports = read(REVIEW / 'derivation-check.json')
    probe = read(REVIEW / 'export-check.json')
    browser = read(REVIEW / 'browser-check.json')
    render = read(REVIEW / 'native-render-check.json')
    portable = read(REVIEW / 'portability-check.json')
    for report in [native, exports, probe, browser, render]:
        assert report['art_accepted'] is False
    for path, expected in native['input_sha256'].items():
        assert sha(ROOT / path) == expected, path
    for key in ['source', 'context']:
        assert sha(ROOT / native[key]) == native[key + '_sha256']
    assert native['tool_sha256'] == sha(ROOT / 'tools/build_handlebar_registration_v2.py')
    assert exports['tool_sha256'] == sha(ROOT / 'tools/derive_handlebar_registration_v2.py')
    assert exports['plan_sha256'] == probe['plan_sha256'] == sha(plan)
    assert len(native['changes']) == 8
    assert len(native['native_triangle_intersections']) == 2
    for row in native['native_triangle_intersections']:
        assert row['old_intersecting_triangle_pairs'] > 0
        assert row['candidate_intersecting_triangle_pairs'] == 0
    for row in exports['files']:
        assert sha(ROOT / row['input']) == row['input_sha256']
        assert sha(ROOT / row['output']) == row['output_sha256']
        assert (ROOT / row['output']).stat().st_size == row['output_bytes']
        expected, proof = derive((ROOT / row['input']).read_bytes(), read(plan)['translation_per_side_m'],
                                 row['output'].endswith('motorcycle-registration-candidate.glb'))
        assert expected == (ROOT / row['output']).read_bytes()
        assert proof['binary_sha256'] == row['binary_sha256']
    assert sha(ROOT / probe['plate_glb']) == probe['plate_sha256']
    assert len(probe['validations']) == 2
    for row in probe['validations']:
        assert sha(ROOT / row['path']) == row['sha256']
        assert row['issues']['numErrors'] == 0
    assert all(p['blocked_samples'] > 0 for p in probe['probes'][:2])
    assert all(p['blocked_samples'] == 0 and p['samples'] == 129 for p in probe['probes'][2:])
    for path, expected in browser['input_sha256'].items():
        assert sha(ROOT / path) == expected, path
    for row in browser['files']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
        assert (ROOT / row['path']).stat().st_size == row['bytes']
    assert browser['runtime']['groups'] == 177
    assert browser['runtime']['triangles'] == 944683
    assert not browser['page_errors'] and not browser['http_failures']
    assert browser['narrow_controls_tested'] and browser['chromium_touch_emulation']
    assert not browser['physical_iphone_tested']
    assert browser['tool_sha256'] == sha(ROOT / 'tools/capture_handlebar_registration_v2.py')
    assert len(render['views']) == 4 and sha(ROOT / render['source']) == render['source_sha256']
    assert render['tool_sha256'] == sha(ROOT / 'tools/render_handlebar_registration_v2.py')
    for row in render['views']:
        assert sha(REVIEW / (row['name'] + '.png')) == row['png_sha256']
        assert sha(REVIEW / 'raw' / (row['name'] + '.exr')) == row['exr_sha256']
        assert row['samples'] == 24 and not row['denoised']
    assert len(portable['sources']) == 2
    assert portable['tool_sha256'] == sha(ROOT / 'tools/check_handlebar_registration_portability_v2.py')
    for row in portable['sources']:
        assert sha(ROOT / row['source']) == row['source_sha256']
        assert row['opened_from_unrelated_directory'] and row['linked_libraries'] == 0
        assert all(image['packed'] and image['pixels_available'] for image in row['images'])
    return {'valid': True, 'groups': 177, 'triangles': 944683,
            'native_plate_intersections_after': 0, 'gltf_errors': 0,
            'browser_errors': 0, 'art_accepted': False,
            'whole_motorcycle_complete': False, 'physical_iphone_tested': False}


def files():
    folders = ['assets-src/moto-components/handlebar-registration-v2',
               'creative/research/handlebar-registration-v2',
               'creative/reviews/handlebar-registration-v2',
               'tools/handlebar-registration-review-v2']
    result = {p for folder in folders for p in (ROOT / folder).rglob('*') if p.is_file()}
    result.update(ROOT / p for p in [
        'tools/build_handlebar_registration_v2.py', 'tools/derive_handlebar_registration_v2.py',
        'tools/check_handlebar_registration_v2.mjs', 'tools/test_handlebar_registration_v2.py',
        'tools/render_handlebar_registration_v2.py', 'tools/capture_handlebar_registration_v2.py',
        'tools/check_handlebar_registration_delivery_v2.py',
        'tools/check_handlebar_registration_portability_v2.py',
        'creative/workflow/motorcycle-finishing-plan-2026-10-22.md',
        'creative/workflow/records/moto-handlebar-registration-002.json'])
    result.discard(MANIFEST)
    return [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': sha(p)}
            for p in sorted(result)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = check()
    inventory = files()
    if args.write:
        MANIFEST.write_text(json.dumps({'schema': 1, 'files': inventory, 'checks': report,
                                       'scope': 'Candidate registration and evidence only; historical source revisions unchanged.'},
                                      indent=2) + '\n')
    else:
        stored = read(MANIFEST)
        assert stored['files'] == inventory, 'Candidate inventory/hash mismatch'
        assert stored['checks'] == report
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
