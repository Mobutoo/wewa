"""Load an exact linked-review export through the preserved Babylon inspector.

An explicit, saved single-review catalogue is supplied only to this browser
session. It never adds an assembly to the physical-component registry.
"""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('proof', type=Path)
parser.add_argument('--port', type=int, default=4143)
args = parser.parse_args()
proof = args.proof.resolve()
source = json.loads(proof.read_text())
assert source['kind'] == 'linked_review_assembly_not_gameplay_or_installed_certification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
export = ROOT / source['inspection_export']['path']
assert sha(export) == source['inspection_export']['sha256']
assert sha(ROOT / source['editable_source']) == source['source_sha256']
for row in source['linked_sources']:
    assert sha(ROOT / row['source']) == row['sha256']
out = proof.parent / 'inspection-linked-v1'
out.mkdir(exist_ok=True)
assert not (out / 'engine-check.json').exists(), 'Use a new inspection revision'
config = {'label': 'Assemblage de contrôle — sources courantes',
          'review': proof.parent.name, 'files': [str(export.relative_to(ROOT / 'assets-src/moto-components'))],
          'rigs': [], 'details': 'Pièces et câbles incomplets ; vue de revue, aucun conducteur, montage ou jeu reçu.'}
catalog = {'assets': {'linked-review': config}}
(out / 'session-catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
inspector = ROOT / 'tools/motorcycle-lab/review-v4.js'
inputs = {str(p.relative_to(ROOT)): sha(p) for p in [proof, export, inspector, Path(__file__).resolve()]}
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=[
        '--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    page = browser.new_page(viewport={'width': 1280, 'height': 900})
    errors, failures = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('response', lambda r: failures.append({'url': r.url, 'status': r.status}) if r.status >= 400 else None)
    page.route('**/tools/motorcycle-lab/catalog.json', lambda route: route.fulfill(json=catalog))
    page.goto(f'http://127.0.0.1:{args.port}/tools/motorcycle-lab/v4.html?asset=linked-review', wait_until='networkidle', timeout=120000)
    page.wait_for_function('window.__MOTO_LAB__?.scene.isReady() && window.__MOTO_LAB__.report().textures_ready', timeout=120000)
    downloaded = page.request.get(f'http://127.0.0.1:{args.port}/' + str(export.relative_to(ROOT)))
    assert downloaded.ok and hashlib.sha256(downloaded.body()).hexdigest() == source['inspection_export']['sha256']
    page.evaluate('window.__MOTO_LAB__.engine.stopRenderLoop()')
    checks = []
    for view in ['quarter', 'driver', 'reverse']:
        page.evaluate('(v)=>{window.__MOTO_LAB__.engine.resize();window.__MOTO_LAB__.view(v);window.__MOTO_LAB__.scene.render();}', view)
        page.wait_for_timeout(100)
        pixel = page.evaluate('''async ()=>{
          const {engine,scene}=window.__MOTO_LAB__;scene.render();
          const width=engine.getRenderWidth(),height=engine.getRenderHeight();
          const p=await engine.readPixels(0,0,width,height),bg=Array.from(p.slice(0,3));let changed=0;
          for(let i=0;i<p.length;i+=4)if(Math.max(...[0,1,2].map(k=>Math.abs(p[i+k]-bg[k])))>8)changed++;
          return {width,height,background_rgb:bg,changed_pixels:changed,changed_fraction:changed/(width*height)};
        }''')
        assert pixel['changed_pixels'] > 100 and pixel['changed_fraction'] > .0001
        state = page.evaluate('window.__MOTO_LAB__.report()')
        assert all(v >= .015 for v in state['framing']['min']) and all(v <= .985 for v in state['framing']['max'])
        image = out / ('engine-' + view + '.png')
        page.screenshot(path=str(image))
        checks.append({'view': view, 'actual_canvas': pixel, 'camera': state['camera'], 'framing': state['framing'],
                       'PNG': str(image.relative_to(ROOT)), 'PNG_sha256': sha(image)})
    report = page.evaluate('window.__MOTO_LAB__.report()')
    assert report['config'] == config and not errors and not failures
    assert all(sha(ROOT / p) == digest for p, digest in inputs.items())
    for row in source['linked_sources']:
        assert sha(ROOT / row['source']) == row['sha256']
    report.update(source_geometry_report=str(proof.relative_to(ROOT)), source_geometry_report_sha256=sha(proof),
                  source_sha256=source['source_sha256'], export_sha256=source['inspection_export']['sha256'],
                  HTTP_export_bytes_verified=True, session_catalog_override=True,
                  session_catalog_sha256=sha(out/'session-catalog.json'), input_hashes=inputs,
                  pixel_checks=checks, page_errors=errors, http_failures=failures,
                  scope='Actual desktop Chromium softwareWebGL linked-export load and pixels; static source pose, no controls exercised, fit, appearance parity, mobile performance or art reception.',
                  art_accepted=False, physical_iphone_tested=False, public_game_unchanged=True)
    (out/'engine-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    browser.close()
print(json.dumps({'linked_sources': len(source['linked_sources']), 'meshes': report['meshes'],
                  'triangles': report['triangles'], 'actual_canvas_pixel_checks': len(checks), 'errors': errors}))
