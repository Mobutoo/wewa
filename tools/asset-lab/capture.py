"""Capture actual isolated exported tyre in local Babylon.js. Start Vite port4142 first."""
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'creative/reviews/front-tyre-v1'
with sync_playwright() as playwright:
    browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1200,'height':1000},device_scale_factor=1)
    errors=[]
    failures=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.on('response',lambda response:failures.append({'url':response.url,'status':response.status}) if response.status>=400 else None)
    page.goto('http://127.0.0.1:4142/tools/asset-lab/',wait_until='networkidle',timeout=90000)
    page.wait_for_function('window.__ASSET_LAB__?.report().textures_ready',timeout=60000)
    for name in ['quarter','side','tread']:
        page.evaluate('(name)=>window.__ASSET_LAB__.view(name)',name)
        page.wait_for_timeout(1200)
        page.screenshot(path=str(OUT/('engine-'+name+'.png')))
    report=page.evaluate('window.__ASSET_LAB__.report()')
    report.update(page_errors=errors,http_failures=failures,scope='Actual isolated exported tyre in Babylon.js9.31.0; Chromium software renderer, not public integration or physical Safari performance measurement',micrograin_parity_passed=False,export_sha256=hashlib.sha256((ROOT/'assets-src/moto-components/front-tyre/front-tyre-inspection.glb').read_bytes()).hexdigest())
    (OUT/'engine-check.json').write_text(json.dumps(report,indent=2)+'\n')
    assert not errors and not failures,(errors,failures)
    print(json.dumps(report,indent=2))
    browser.close()
