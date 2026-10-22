import pathlib,json,hashlib
from playwright.sync_api import sync_playwright
D=pathlib.Path('/workspace/wewa/creative/reviews/front-mudguard-red-finish-v2');errors=[];failures=[]
with sync_playwright()as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--renderer-process-limit=1']);page=b.new_page(viewport={'width':900,'height':720});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:failures.append({'url':r.url,'status':r.status})if r.status>=400 else None)
 page.goto('http://127.0.0.1:4297/creative/reviews/front-mudguard-red-finish-v2/runtime/index.html',timeout=120000);page.wait_for_function('window.__REVIEW__',timeout=120000)
 page.wait_for_timeout(750);report=page.evaluate('window.__REVIEW__.report()');assert report['meshes']==1
 assert all(x>.015 for x in report['frame']['min'])and all(x<.985 for x in report['frame']['max']),report['frame']
 canvas=page.locator('canvas');canvas.screenshot(path=str(D/'babylon-quarter.png'));page.evaluate('window.__REVIEW__.view(true)');page.wait_for_timeout(250);canvas.screenshot(path=str(D/'babylon-reverse.png'))
 report['page_errors']=errors;report['http_failures']=failures;assert not errors and not failures
 report['glb_sha256']=hashlib.sha256(pathlib.Path('/workspace/wewa/assets-src/moto-components/front-mudguard-red-finish-v2/front-mudguard-red-finish-v2.glb').read_bytes()).hexdigest();(D/'babylon-report.json').write_text(json.dumps(report,indent=2)+'\n');b.close();print(json.dumps(report))
