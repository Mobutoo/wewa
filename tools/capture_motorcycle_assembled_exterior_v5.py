"""Actual Chromium/Babylon captures, every parent isolated, and source/LOD comparison."""
import base64
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'creative/reviews/motorcycle-exterior-v5'
VIEWS=['quarter','left','right','front','rear','cockpit','underside']
ADDED=['fuel-tap-visible-body','fuel-tap-visible-lever','throttle-visible-assembly','instrument-support-visible','centre-stand-operating-arm','centre-stand-pivot-exterior','side-stand-return-spring','side-stand-spring-anchor','side-stand-spring-sleeve','steering-cap-visible','exhaust-heatshield-fasteners','plate-captive-nut-left','plate-captive-nut-right','rear-indicator-washer-left','rear-indicator-washer-right','mirror-left','mirror-right']

def save_canvas(page,path):
    data=base64.b64decode(page.evaluate("document.querySelector('canvas').toDataURL('image/png').split(',')[1]"));path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    return {'path':str(path.relative_to(ROOT)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

def render(page,mask=False):
    page.evaluate("async mask=>{const m=window.__MOTO_EXTERIOR__;m.silhouette(mask);await m.scene.whenReadyAsync();m.scene.render()}",mask)

def pixels(path):
    a=np.array(Image.open(path).convert('RGB'));return a[:,:,0]>128

def run():
    OUT.mkdir(parents=True,exist_ok=True);results={}
    inputs=['tools/motorcycle-exterior-review-v5/index.html','tools/motorcycle-exterior-review-v5/viewer.js','tools/capture_motorcycle_assembled_exterior_v5.py','creative/research/motorcycle-exterior-v5/parents.json','assets-src/moto-components/motorcycle-exterior-v5/lod/build-report.json','assets-src/moto-components/motorcycle-exterior-v5/lod/motorcycle-lod.glb','assets-src/moto-components/motorcycle-exterior-v5.gltf']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--js-flags=--max-old-space-size=8192'])
        for model in ['lod','source']:
            page=browser.new_page(viewport={'width':1280,'height':900});errors=[];failures=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('response',lambda r:failures.append({'url':r.url,'status':r.status}) if r.status>=400 else None)
            page.goto(f'http://127.0.0.1:4143/tools/motorcycle-exterior-review-v5/?model={model}&capture=1',wait_until='domcontentloaded',timeout=120000)
            page.wait_for_function("document.querySelector('#error').textContent || (window.__MOTO_EXTERIOR__?.scene.isReady() && window.__MOTO_EXTERIOR__.report().textures_ready)",timeout=300000)
            assert not page.locator('#error').inner_text(),page.locator('#error').inner_text()
            report=page.evaluate('window.__MOTO_EXTERIOR__.report()');assert report['groups']==177
            files=[];isolation=[];renderable_checks=[]
            for view in VIEWS:
                page.evaluate('v=>window.__MOTO_EXTERIOR__.view(v)',view);render(page);files.append(save_canvas(page,OUT/f'{model}-{view}.png'))
                render(page,True);files.append(save_canvas(page,OUT/f'{model}-{view}-mask.png'))
                print('WHOLE',model,view,flush=True)
            if model=='lod':
                render(page);page.screenshot(path=str(OUT/'inspector-desktop.png'))
                # Exercise actual controls and prove reset restores all authored matrices.
                page.locator('#search').fill('Robinet');assert page.locator('#parts option').count()==2
                page.locator('#parts').select_option('fuel-tap-visible-body');page.locator('#isolate').click();assert page.evaluate('window.__MOTO_EXTERIOR__.report().isolated')=='fuel-tap-visible-body'
                options=page.locator('#subparts option');assert options.count()==4
                subpart=options.nth(1).get_attribute('value');page.locator('#subparts').select_option(subpart);page.locator('#isolate').click();assert len(page.evaluate('window.__MOTO_EXTERIOR__.report().renderables.filter(p=>p.visible)'))==1
                page.locator('#restore').click();page.locator('#search').fill('')
                page.evaluate('window.__MOTO_EXTERIOR__.explode(.75)');render(page);files.append(save_canvas(page,OUT/'lod-exploded.png'))
                page.locator('#restore').click()
                restored=page.evaluate('window.__MOTO_EXTERIOR__.report()');assert report['parents']==restored['parents']
                for i,parent in enumerate(report['parents']):
                    key=parent['key'];page.evaluate('k=>{const m=window.__MOTO_EXTERIOR__;m.isolate(k);m.focus(k)}',key)
                    render(page,True);path=OUT/'isolation'/f'{key}-mask.png';files.append(save_canvas(page,path));mask=pixels(path);count=int(mask.sum());assert count>20,(key,count)
                    edge=int(mask[0,:].sum()+mask[-1,:].sum()+mask[:,0].sum()+mask[:,-1].sum());assert edge==0,(key,'clipped',edge)
                    active=page.evaluate('window.__MOTO_EXTERIOR__.report().parents.filter(p=>p.enabled).map(p=>p.key)');assert active==[key]
                    isolation.append({'key':key,'visible_mask_pixels':count,'edge_pixels':edge,'only_this_parent_enabled':True})
                    render(page);files.append(save_canvas(page,OUT/'isolation'/f'{key}.png'))
                    if i%20==0:print('ISOLATED',i+1,'/',len(report['parents']),flush=True)
                # Composite parents can occlude their own exterior children. Verify
                # every actual Babylon renderable independently as well.
                for i,element in enumerate(report['renderables']):
                    page.evaluate('id=>{const m=window.__MOTO_EXTERIOR__;m.isolateRenderable(id);m.focusRenderable(id)}',element['id']);render(page,True)
                    raw=base64.b64decode(page.evaluate("document.querySelector('canvas').toDataURL('image/png').split(',')[1]"));a=np.array(Image.open(io.BytesIO(raw)).convert('RGB'))[:,:,0]>128;count=int(a.sum());edge=int(a[0,:].sum()+a[-1,:].sum()+a[:,0].sum()+a[:,-1].sum());assert count>0 and edge==0,(element,count,edge)
                    visible=page.evaluate('window.__MOTO_EXTERIOR__.report().renderables.filter(p=>p.visible).map(p=>p.id)');assert visible==[element['id']]
                    renderable_checks.append({**element,'visible_mask_pixels':count,'edge_pixels':edge,'only_this_renderable_visible':True,'mask_sha256':hashlib.sha256(raw).hexdigest()})
                    if i%100==0:print('SUBPARTS',i+1,'/',len(report['renderables']),flush=True)
                # Real narrow touch viewport, same inspect/restore controls.
                page.set_viewport_size({'width':390,'height':844});page.locator('#search').fill('Robinet');page.locator('#parts').select_option('fuel-tap-visible-body');page.locator('#isolate').click();render(page);page.screenshot(path=str(OUT/'inspector-touch.png'))
                assert page.evaluate('window.__MOTO_EXTERIOR__.report().isolated')=='fuel-tap-visible-body';page.locator('#restore').click();assert all(p['enabled'] for p in page.evaluate('window.__MOTO_EXTERIOR__.report().parents'))
                page.set_viewport_size({'width':1280,'height':900})
            else:
                for key in ADDED:
                    page.evaluate('k=>{window.__MOTO_EXTERIOR__.isolate(k);window.__MOTO_EXTERIOR__.focus(k)}',key);render(page);files.append(save_canvas(page,OUT/'source-details'/f'{key}.png'));render(page,True);files.append(save_canvas(page,OUT/'source-details'/f'{key}-mask.png'))
            assert not errors and not failures,(errors,failures)
            report.update(files=files,isolation_checks=isolation,renderable_visibility_checks=renderable_checks,page_errors=errors,http_failures=failures,input_sha256=hashes,actual_browser='Chromium software WebGL, not physical iPhone')
            (OUT/f'{model}-engine-report.json').write_text(json.dumps(report,indent=2)+'\n');results[model]=report;page.close()
        browser.close()
    a={p['key']:p['matrix'] for p in results['source']['parents']};b={p['key']:p['matrix'] for p in results['lod']['parents']};assert a.keys()==b.keys()
    delta=max(abs(x-y)for k in a for x,y in zip(a[k],b[k]));assert delta<2e-6
    comparisons=[]
    for view in VIEWS:
        aa=pixels(OUT/f'source-{view}-mask.png');bb=pixels(OUT/f'lod-{view}-mask.png');comparisons.append({'view':view,'silhouette_iou':float((aa&bb).sum()/(aa|bb).sum()),'meaning':'Canvas mask overlap only, not artistic acceptance or dimensional validation'})
    for start in range(0,177,36):
        keys=[p['key'] for p in results['lod']['parents']][start:start+36];sheet=Image.new('RGB',(6*240,6*248),(25,33,42));draw=ImageDraw.Draw(sheet)
        for j,key in enumerate(keys):
            im=Image.open(OUT/'isolation'/f'{key}.png');im.thumbnail((238,220));x=(j%6)*240;y=(j//6)*248;sheet.paste(im,(x+(240-im.width)//2,y));draw.text((x+4,y+222),key[:32],fill='white');draw.text((x+4,y+234),key[32:64],fill='white')
        sheet.save(OUT/f'parts-contact-sheet-{start//36+1}.jpg',quality=91)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items()),'Capture inputs changed during execution'
    (OUT/'comparison.json').write_text(json.dumps({'schema':1,'input_sha256':hashes,'all_177_parents_isolated_and_visible':True,'individually_checked_renderables':len(results['lod']['renderable_visibility_checks']),'all_restored_matrices_exact':True,'source_lod_max_matrix_delta':delta,'whole_silhouette_comparison':comparisons,'art_accepted':False,'physical_iphone_tested':False},indent=2)+'\n')
    print('EXTERIOR_VISIBILITY_PASS',177,flush=True)

if __name__=='__main__':run()
