"""Real browser comparison; desktop and touch emulation are not physical Safari tests."""
import base64
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'creative/reviews/handlebar-registration-v2'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    inputs = ['tools/handlebar-registration-review-v2/index.html',
              'tools/handlebar-registration-review-v2/viewer.js',
              'creative/reviews/handlebar-registration-v2/derivation-check.json',
              'assets-src/moto-components/handlebar-registration-v2/motorcycle-registration-candidate.glb',
              'app/public/materials/kloppenheim_06_puresky_1k.hdr']
    hashes = {p: sha(ROOT / p) for p in inputs}
    files, errors, failures, comparisons = [], [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=[
            '--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('response', lambda r: failures.append({'url': r.url, 'status': r.status}) if r.status >= 400 else None)
        page.goto('http://127.0.0.1:4143/tools/handlebar-registration-review-v2/?capture=1', wait_until='domcontentloaded')
        page.wait_for_function('window.__REGISTRATION__?.report().textures_ready', timeout=180000)
        report = page.evaluate('window.__REGISTRATION__.report()')
        assert report['groups'] == 177 and report['triangles'] == 944683, report
        original_parents = report['parent_matrices']

        def capture(name):
            page.evaluate('window.__REGISTRATION__.scene.render()')
            raw = base64.b64decode(page.evaluate("document.querySelector('canvas').toDataURL('image/png').split(',')[1]"))
            path = OUT / (name + '.png')
            path.write_bytes(raw)
            files.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': len(raw)})
            return np.array(Image.open(io.BytesIO(raw)).convert('RGB'))

        for view in ['underside', 'top', 'whole']:
            page.locator('#' + view).click()
            page.locator('#before').click()
            before = page.evaluate('window.__REGISTRATION__.report()')
            assert not before['corrected']
            assert before['parent_matrices'] == original_parents
            a = capture(view + '-before')
            page.locator('#after').click()
            after = page.evaluate('window.__REGISTRATION__.report()')
            assert after['corrected']
            assert after['parent_matrices'] == original_parents
            for old, new in zip(before['parts'], after['parts']):
                assert abs(abs(old['position'][0] - new['position'][0]) - .0065) < 1e-7
                assert old['position'][1:] == new['position'][1:]
            b = capture(view + '-candidate')
            different = int(np.count_nonzero(np.max(np.abs(a.astype(int) - b.astype(int)), axis=2) > 8))
            assert different > 5, (view, different)
            comparisons.append({'view': view, 'changed_pixels_above_8': different,
                                'parent_poses_unchanged': True, 'eight_part_translations_checked': True})
        page.close()
        page = browser.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('response', lambda r: failures.append({'url': r.url, 'status': r.status}) if r.status >= 400 else None)
        page.goto('http://127.0.0.1:4143/tools/handlebar-registration-review-v2/?capture=1', wait_until='domcontentloaded')
        page.wait_for_function('window.__REGISTRATION__?.report().textures_ready', timeout=180000)
        page.locator('#underside').tap()
        page.locator('#before').tap()
        assert page.locator('#before').get_attribute('aria-pressed') == 'true'
        page.locator('#after').tap()
        assert page.locator('#after').get_attribute('aria-pressed') == 'true'
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(OUT / 'inspector-narrow.png'))
        files.append({'path': str((OUT / 'inspector-narrow.png').relative_to(ROOT)),
                      'sha256': sha(OUT / 'inspector-narrow.png'), 'bytes': (OUT / 'inspector-narrow.png').stat().st_size})
        capture('underside-narrow')
        assert not errors and not failures, (errors, failures)
        browser.close()
    assert all(sha(ROOT / p) == h for p, h in hashes.items())
    output = {'schema': 1, 'input_sha256': hashes, 'files': files, 'comparisons': comparisons,
              'page_errors': errors, 'http_failures': failures, 'runtime': report,
              'narrow_controls_tested': True, 'chromium_touch_emulation': True, 'physical_iphone_tested': False,
              'art_accepted': False, 'tool_sha256': sha(Path(__file__))}
    (OUT / 'browser-check.json').write_text(json.dumps(output, indent=2) + '\n')
    print('REGISTRATION_BROWSER_CHECK', len(files), 'captures; no JS/HTTP errors')


if __name__ == '__main__':
    main()
