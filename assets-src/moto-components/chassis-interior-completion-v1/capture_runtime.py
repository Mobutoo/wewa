from pathlib import Path
import json,hashlib
from playwright.sync_api import sync_playwright
O=Path(__file__).resolve().parent
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']);p=b.new_page(viewport={'width':1000,'height':800});errors=[];http=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('response',lambda r:http.append({'url':r.url,'status':r.status})if r.status>=400 else None)
 p.goto('http://127.0.0.1:4197/assets-src/moto-components/chassis-interior-completion-v1/runtime.html',wait_until='networkidle',timeout=120000);p.wait_for_function('window.kit?.report().ready',timeout=120000);p.evaluate('kit.engine.stopRenderLoop()');views=[]
 for reverse in [False,True]:
  p.evaluate('(r)=>kit.view(r)',reverse)
  proof=p.evaluate('''async()=>{kit.scene.render();let w=kit.engine.getRenderWidth(),h=kit.engine.getRenderHeight(),p=await kit.engine.readPixels(0,0,w,h),bg=[...p.slice(0,3)],n=0;for(let i=0;i<p.length;i+=4)if(Math.max(...bg.map((v,j)=>Math.abs(v-p[i+j])))>8)n++;return {width:w,height:h,changed_pixels:n,fraction:n/(w*h)}}''');assert proof['changed_pixels']>1000
  name='runtime-'+('reverse'if reverse else'quarter')+'.png';p.screenshot(path=str(O/name));views.append({'image':name,'sha256':hashlib.sha256((O/name).read_bytes()).hexdigest(),**proof})
 r=p.evaluate('kit.report()');r.update(views=views,page_errors=errors,http_failures=http,glb_sha256=hashlib.sha256((O/'kit-material.glb').read_bytes()).hexdigest(),scope='Actual Babylon Chromium software WebGL only; no Safari/iPhone/FPS or art acceptance');(O/'runtime-check.json').write_text(json.dumps(r,indent=2));assert not errors and not http;(b.close());print(json.dumps({'meshes':r['mesh_count'],'triangles':r['triangles'],'errors':errors}))
