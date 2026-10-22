"""Actual close context for every changed group, keeping neighbouring parts visible."""
import base64
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parents[1];O=R/'creative/reviews/motorcycle-exterior-v5/context';O.mkdir(parents=True,exist_ok=True)
plan=json.loads((R/'creative/research/motorcycle-exterior-v5/parents.json').read_text())
inputs=['tools/motorcycle-exterior-review-v5/viewer.js','assets-src/moto-components/motorcycle-exterior-v5/lod/motorcycle-lod.glb','tools/capture_motorcycle_exterior_context_v5.py'];hashes={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in inputs}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=b.new_page(viewport={'width':1280,'height':900});errors=[];failures=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:failures.append({'url':r.url,'status':r.status})if r.status>=400 else None)
    page.goto('http://127.0.0.1:4143/tools/motorcycle-exterior-review-v5/?capture=1',wait_until='domcontentloaded')
    page.wait_for_function('window.__MOTO_EXTERIOR__?.report().textures_ready',timeout=180000);files=[]
    for change in plan['changes']:
        key=change['key'];page.evaluate('k=>{const m=window.__MOTO_EXTERIOR__;m.restore();m.select(k);m.focus(k);m.camera.radius*=2.5;m.camera.maxZ=20;m.scene.render()}',key)
        raw=base64.b64decode(page.evaluate("document.querySelector('canvas').toDataURL('image/png').split(',')[1]"));path=O/f'{key}.png';path.write_bytes(raw)
        files.append({'key':key,'path':str(path.relative_to(R)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'camera':page.evaluate('window.__MOTO_EXTERIOR__.report().camera'),'scope':'Actual assembled context; a surface may remain naturally occluded. Isolated evidence is separate.'})
    assert not errors and not failures,(errors,failures);b.close()
assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
(O/'report.json').write_text(json.dumps({'files':files,'input_sha256':hashes,'page_errors':errors,'http_failures':failures,'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'art_accepted':False},indent=2)+'\n')
print('CHANGED_CONTEXT_VIEWS',len(files))
