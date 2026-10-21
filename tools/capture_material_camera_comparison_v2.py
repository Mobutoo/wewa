"""Explicit HDR sampling rotation with actual Babylon pixels; not a material-parity claim."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('camera_spec', type=Path)
p.add_argument('output', type=Path)
p.add_argument('--port', type=int, default=4143)
p.add_argument('--rotation-y', type=float, required=True)
p.add_argument('--orientation-report', type=Path, required=True)
a = p.parse_args()
camera_spec, out = a.camera_spec.resolve(), a.output.resolve()
spec = json.loads(camera_spec.read_text())
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert spec['schema'] == 'wewa.material-camera-comparison.v1'
assert not out.exists(), 'Use a new capture revision'
assert math.isfinite(a.rotation_y)
orientation_report = a.orientation_report.resolve()
inputs = {str(camera_spec.relative_to(ROOT)): sha(camera_spec), str(orientation_report.relative_to(ROOT)): sha(orientation_report)}
for key in ['source', 'export', 'HDR', 'native_spec', 'native_report', 'native_neutral_PNG', 'tool']:
    assert sha(ROOT / spec[key]) == spec[key + '_sha256'], key
    inputs[spec[key]] = spec[key + '_sha256']
for path in [Path(__file__).resolve(), ROOT / 'tools/motorcycle-material-camera-lab-v1/index.html',
             ROOT / 'tools/motorcycle-material-camera-lab-v1/review.js',
             ROOT / 'tools/motorcycle-material-camera-lab-v2/index.html', ROOT / 'tools/motorcycle-material-camera-lab-v2/review.js']:
    inputs[str(path.relative_to(ROOT))] = sha(path)
width, height = spec['resolution_px']
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=[
        '--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
    errors, failures = [], []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('response', lambda response: failures.append({'url': response.url, 'status': response.status})
            if response.status >= 400 else None)
    url = f'http://127.0.0.1:{a.port}/tools/motorcycle-material-camera-lab-v2/?spec=/' + str(camera_spec.relative_to(ROOT)) + f'&rotation_y={a.rotation_y}'
    page.goto(url, wait_until='networkidle', timeout=120000)
    page.wait_for_function('window.__MATERIAL_CAMERA_REVIEW__?.orientation_variant_ready && window.__MATERIAL_CAMERA_REVIEW__.scene.isReady() && window.__MATERIAL_CAMERA_REVIEW__.report().textures_ready', timeout=120000)
    for key in ['export', 'HDR']:
        response = page.request.get(f'http://127.0.0.1:{a.port}/' + spec[key])
        assert response.ok and hashlib.sha256(response.body()).hexdigest() == spec[key + '_sha256'], key
    page.evaluate('window.__MATERIAL_CAMERA_REVIEW__.engine.stopRenderLoop()')
    pixel = page.evaluate('''async ()=>{
      const {engine,scene}=window.__MATERIAL_CAMERA_REVIEW__;engine.resize();scene.render();
      const width=engine.getRenderWidth(),height=engine.getRenderHeight();
      const p=await engine.readPixels(0,0,width,height),bg=Array.from(p.slice(0,3));let changed=0;
      for(let i=0;i<p.length;i+=4)if(Math.max(...[0,1,2].map(k=>Math.abs(p[i+k]-bg[k])))>8)changed++;
      return {width,height,background_rgb:bg,changed_pixels:changed,changed_fraction:changed/(width*height)};
    }''')
    state = page.evaluate('window.__MATERIAL_CAMERA_REVIEW__.report()')
    assert state['actual_environment_rotation_y_radians'] == a.rotation_y
    assert not errors and not failures, {'page_errors': errors, 'http_failures': failures}
    assert pixel['width'] == width and pixel['height'] == height
    assert pixel['changed_pixels'] > 100 and pixel['changed_fraction'] > .0001
    differences = [w['pixel_difference'] for w in state['projection_witnesses']]
    assert len(differences) == 8
    # This is a software projection comparison, not a photographic fit tolerance.
    assert max(differences) < .05, differences
    assert all(sha(ROOT / path) == digest for path, digest in inputs.items())
    out.mkdir(parents=True)
    png = out / 'actual-babylon-same-camera.png'
    page.locator('canvas').screenshot(path=str(png))
    state.update(input_hashes=inputs, actual_canvas=pixel, PNG=str(png.relative_to(ROOT)), PNG_sha256=sha(png),
                 projection_max_pixel_difference=max(differences), software_projection_bound_px=.05,
                 HTTP_export_and_HDR_bytes_verified=True, page_errors=errors, http_failures=failures,
                 orientation_report=str(orientation_report.relative_to(ROOT)), orientation_report_sha256=sha(orientation_report),
                 public_game_unchanged=True, art_accepted=False, physical_iphone_tested=False)
    (out / 'engine-check.json').write_text(json.dumps(state, indent=2) + '\n')
    browser.close()
print(json.dumps({'output': str(out), 'projection_max_pixel_difference': max(differences),
                  'changed_pixels': pixel['changed_pixels'], 'rotation_y_radians': a.rotation_y, 'errors': errors}))
