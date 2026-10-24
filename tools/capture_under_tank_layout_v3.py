"""Render original pixels at requested resolution, never upscale a previous picture."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'creative/reviews/under-tank-layout-v3'
parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--before',action='store_true');parser.add_argument('--views',default='front,rear,centre,centre-right,left,right,plate');args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
errors=[];failures=[];rows=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1280,'height':960})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:failures.append(r.url) if r.status>=400 else None)
    page.goto('http://127.0.0.1:4143/tools/under-tank-layout-review-v3/?capture=1'+('&before=1' if args.before else ''),wait_until='domcontentloaded')
    page.wait_for_function('window.__PROPORTIONS__?.report().textures_ready',timeout=180000)
    for view in args.views.split(','):
        width,height=(1280,960) if args.preview else ((3840,2880) if view in ['front','rear'] else (2560,1920))
        page.set_viewport_size({'width':width,'height':height})
        page.evaluate('v=>{window.__PROPORTIONS__.engine.resize();window.__PROPORTIONS__.view(v)}',view)
        report=page.evaluate('window.__PROPORTIONS__.report()');assert [report['width'],report['height']]==[width,height]
        assert set(report['text_meshes'])=={'Plate text Art.','Plate text 015'},report['text_meshes']
        data=base64.b64decode(page.evaluate("document.querySelector('canvas').toDataURL('image/png').split(',')[1]"))
        filename=('before-' if args.before else '')+view+('-preview' if args.preview else '-high-resolution')+'.png'
        target=OUT/filename;target.write_bytes(data)
        rows.append({'file':filename,'sha256':hashlib.sha256(data).hexdigest(),'runtime':report})
        print('CAPTURE',filename,width,height,flush=True)
    browser.close()
assert not errors and not failures,(errors,failures)
if not args.preview and not args.before:
    (OUT/'browser-check.json').write_text(json.dumps({'captures':rows,'page_errors':errors,'http_failures':failures,
       'method':'Direct Babylon WebGL framebuffer at native output resolution; no image generation or upscaling',
       'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
