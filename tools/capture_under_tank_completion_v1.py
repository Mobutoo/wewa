"""Paired actual Babylon renders, with same camera and light for both states."""
import base64
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'creative/reviews/under-tank-completion-v1'
URL='http://127.0.0.1:4143/tools/under-tank-review-v1/?capture=1'


def main():
    errors=[];failures=[];captures=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=[
            '--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        page=browser.new_page(viewport={'width':1480,'height':1050})
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda r:failures.append({'url':r.url,'status':r.status}) if r.status>=400 else None)
        page.goto(URL,wait_until='domcontentloaded')
        page.wait_for_function('window.__UNDER_TANK__?.report().textures_ready',timeout=180000)
        for view in ['whole','left','right','detailLeft','detailRight','isolated']:
            page.locator('[data-view='+view+']').click()
            poses=[]
            for version in ['before','after']:
                page.locator('#'+version).click()
                page.evaluate('window.__UNDER_TANK__.scene.render()')
                report=page.evaluate('window.__UNDER_TANK__.report()')
                poses.append(report['camera'])
                assert report['completed']==(version=='after')
                raw=base64.b64decode(page.evaluate("document.querySelector('canvas').toDataURL().split(',')[1]"))
                path=OUT/f'{view}-{version}.png';path.write_bytes(raw)
                captures.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'runtime':report})
            assert poses[0]==poses[1],view
        page.close()
        page=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(URL,wait_until='domcontentloaded')
        page.wait_for_function('window.__UNDER_TANK__?.report().textures_ready',timeout=180000)
        page.locator('#before').tap();assert not page.evaluate('window.__UNDER_TANK__.report().completed')
        page.locator('#after').tap();assert page.evaluate('window.__UNDER_TANK__.report().completed')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(OUT/'mobile-review.png'))
        browser.close()
    assert not errors and not failures,(errors,failures)
    (OUT/'browser-check.json').write_text(json.dumps({'captures':captures,'page_errors':errors,
        'http_failures':failures,'touch_controls_checked':True,'physical_iphone_tested':False,
        'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'art_accepted':False},indent=2)+'\n')
    print('UNDER_TANK_BROWSER',len(captures),'paired captures, touch controls OK')


if __name__=='__main__':main()
