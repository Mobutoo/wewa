"""Integration checks with actual Chromium. Software rendering is not an iPhone benchmark."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import json, shutil, os

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'WEWA_Developpement_Web/validation/browser'
OUTPUT.mkdir(parents=True,exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')))
thread=Thread(target=server.serve_forever,daemon=True);thread.start()
url=f'http://127.0.0.1:{server.server_port}/'
results=[]
try:
    with sync_playwright() as p:
        executable=shutil.which('chromium')
        browser=p.chromium.launch(**({'executable_path':executable} if executable else {}),headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        for label,viewport,mobile in [('desktop',{'width':1440,'height':900},False),('iphone-landscape-emulation',{'width':852,'height':393},True)]:
            context=browser.new_context(viewport=viewport,has_touch=mobile,is_mobile=mobile,device_scale_factor=1)
            page=context.new_page();errors=[];failed=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('response',lambda response:failed.append({'url':response.url,'status':response.status}) if response.status>=400 else None)
            page.goto(url,wait_until='networkidle');page.screenshot(path=str(OUTPUT/f'{label}-home.png'))
            page.locator('#play').click()
            page.wait_for_selector('#hud:not(.hidden)',timeout=60000)
            page.wait_for_function('window.__WEWA__?.snapshot()?.loadedCells > 0',timeout=45000)
            page.wait_for_timeout(800)
            if page.locator('#pause-panel').is_visible():page.locator('#resume').click()
            # Countdown is advanced through the local-only QA fixture to keep CI quick.
            page.evaluate('''() => {const s=window.__WEWA__.sim();s.paused=false;for(let i=0;i<180;i++)s.step({gas:false,brake:false,left:false,right:false,nitro:false,horn:false});}''')
            page.wait_for_timeout(200)
            before=page.evaluate('window.__WEWA__.snapshot()')
            assert before['phase']=='running',before
            if mobile:
                gas=page.locator('[data-input="gas"]').bounding_box();left=page.locator('[data-input="left"]').bounding_box()
                session=context.new_cdp_session(page)
                points=[{'id':i+1,'x':r['x']+r['width']/2,'y':r['y']+r['height']/2} for i,r in enumerate([gas,left])]
                session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':points})
                pressed=page.evaluate('window.__WEWA__.snapshot().controls');assert pressed['gas'] and pressed['left'],pressed
                page.wait_for_timeout(120)
                session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
                assert not any(page.evaluate('window.__WEWA__.snapshot().controls').values())
            else:
                page.keyboard.down('w');page.wait_for_timeout(800);page.keyboard.up('w')
                after=page.evaluate('window.__WEWA__.snapshot()');assert after['vehicle']['speed']>before['vehicle']['speed'],after
            page.locator('#camera').click();assert page.evaluate('window.__WEWA__.world().firstPerson')
            page.wait_for_timeout(300);page.screenshot(path=str(OUTPUT/f'{label}-first-person.png'))
            page.locator('#camera').click();page.wait_for_timeout(300);page.screenshot(path=str(OUTPUT/f'{label}-game.png'))
            page.locator('#pause').click();assert page.evaluate('window.__WEWA__.snapshot().paused')
            frozen=page.evaluate('window.__WEWA__.snapshot().elapsed');page.wait_for_timeout(200);assert page.evaluate('window.__WEWA__.snapshot().elapsed')==frozen
            assert not any(page.evaluate('window.__WEWA__.snapshot().controls').values())
            page.locator('#resume').click()
            page.evaluate('window.dispatchEvent(new Event("blur"))');assert page.evaluate('window.__WEWA__.snapshot().paused')
            page.locator('#resume').click()
            page.evaluate('''() => {const s=window.__WEWA__.sim();s.ticks=1799;s.step({gas:false,brake:false,left:false,right:false,nitro:false,horn:false});}''')
            page.wait_for_selector('#results:not(.hidden)',timeout=5000)
            final=page.evaluate('window.__WEWA__.snapshot()');assert final['elapsed']==30 and final['finishCount']==1,final
            page.locator('#replay').click();page.wait_for_timeout(200);replayed=page.evaluate('window.__WEWA__.snapshot()');assert replayed['score']==0 and replayed['vehicle']['nitro']==100 and replayed['cargo']==[],replayed
            if errors or failed:raise AssertionError({'errors':errors,'failed_requests':failed})
            results.append({'profile':label,'rendered':True,'camera_switch':True,'pause_and_blur':True,'rush_finish_once':True,'restart_clean':True,'javascript_errors':errors,'http_errors':failed,'note':'Chromium software GPU, not physical iPhone Safari'})
            context.close()
        browser.close()
finally:
    server.shutdown();server.server_close();thread.join()
(OUTPUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
