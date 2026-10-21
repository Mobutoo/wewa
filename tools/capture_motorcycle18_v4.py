"""Capture real exported components; technical proof with actual nonblank canvas check, no art/hardware acceptance.
Run Vite at repository root on4143. Catalog must list actual built GLBs only.
"""
import argparse,hashlib,json,math
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('asset');p.add_argument('--port',type=int,default=4143);a=p.parse_args()
catalog=json.loads((ROOT/'tools/motorcycle-lab/catalog.json').read_text());config=catalog['assets'][a.asset]
out=ROOT/'creative/reviews'/config['review']/'inspection-v4';out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inspector_hash=sha(ROOT/'tools/motorcycle-lab/review-v3.js');capture_hash=sha(Path(__file__))
export_hashes={s:sha(ROOT/'assets-src/moto-components'/s) for s in config['files']}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1280,'height':900});errors=[];failures=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('response',lambda r:failures.append({'status':r.status,'url':r.url}) if r.status>=400 else None)
 page.goto(f'http://127.0.0.1:{a.port}/tools/motorcycle-lab/v3.html?asset='+a.asset,wait_until='networkidle',timeout=120000)
 page.wait_for_function('window.__MOTO_LAB__?.scene.isReady() && window.__MOTO_LAB__.report().textures_ready',timeout=90000)
 page.evaluate('window.__MOTO_LAB__.engine.stopRenderLoop()')
 pixel_checks=[]
 def frame(label):
  page.evaluate('window.__MOTO_LAB__.engine.resize()')
  page.wait_for_timeout(100)
  page.evaluate('window.__MOTO_LAB__.scene.render()')
  proof=page.evaluate("""async ()=>{
   const {scene,engine}=window.__MOTO_LAB__;scene.render();
   const w=engine.getRenderWidth(),h=engine.getRenderHeight(),p=await engine.readPixels(0,0,w,h);
   const bg=Array.from(p.slice(0,3));let changed=0;const rgbMin=[255,255,255],rgbMax=[0,0,0];
   for(let i=0;i<p.length;i+=4){let delta=0;for(let j=0;j<3;j++){delta=Math.max(delta,Math.abs(p[i+j]-bg[j]));rgbMin[j]=Math.min(rgbMin[j],p[i+j]);rgbMax[j]=Math.max(rgbMax[j],p[i+j]);}if(delta>8)changed++;}
   return {width:w,height:h,background_rgb:bg,changed_pixels:changed,changed_fraction:changed/(w*h),rgb_min:rgbMin,rgb_max:rgbMax,scope:'Actual WebGL canvas pixels; DOM controls excluded, not a shape/material reception'};
  }""")
  assert proof['changed_pixels']>100 and proof['changed_fraction']>.0001,('Blank actual canvas',label,proof)
  pixel_checks.append({'view':label,**proof})
  bounds=page.evaluate('window.__MOTO_LAB__.report().framing')
  assert all(v>=.015 for v in bounds['min']) and all(v<=.985 for v in bounds['max']),('Cropped actual component bounding boxes',bounds)
 for view in ['quarter','driver','reverse']:
  page.evaluate('(v)=>window.__MOTO_LAB__.view(v)',view);frame(view);page.screenshot(path=str(out/('engine-'+view+'.png')),timeout=90000)
 pose_checks=[]
 for rig in [*config.get('rigs',[]),*config.get('morph_controls',[])]:
  states=[]
  for value in [rig['min'],rig['max'],rig['min']-1000,rig['max']+1000]:
   page.evaluate('(p)=>window.__MOTO_LAB__.setPose(p)',{rig['id']:value});frame(rig['id']+':'+str(value))
   r=page.evaluate('window.__MOTO_LAB__.report()');states.append({'requested':value,'rig_states':r['rig_states'],'rig':next(v for v in r['rigs'] if v['id']==rig['id'])})
  assert states[2]['rig_states'][rig['id']]==rig['min'] and states[3]['rig_states'][rig['id']]==rig['max']
  first=states[0]['rig']['actual_geometry'];last=states[1]['rig']['actual_geometry'];assert first and len(first)==len(last),'Rig has no actual child geometry'
  travel=max(math.dist(x['point_world'],y['point_world']) for x,y in zip(first,last));assert travel>1e-5,('No actual geometry movement',rig['id'],travel)
  pose_checks.append({'rig':rig['id'],'states':states,'actual_vertex_travel_m':travel})
  page.screenshot(path=str(out/('engine-motion-'+rig['id']+'.png')),timeout=90000)
  page.evaluate('(p)=>window.__MOTO_LAB__.setPose(p)',{rig['id']:rig.get('initial',0)})
 page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(150);page.evaluate("window.__MOTO_LAB__.engine.resize();window.__MOTO_LAB__.view('driver')");frame('landscape-844x390');page.screenshot(path=str(out/'engine-landscape-844x390.png'),timeout=90000)
 report=page.evaluate('window.__MOTO_LAB__.report()')
 assert report['config']==config==json.loads((ROOT/'tools/motorcycle-lab/catalog.json').read_text())['assets'][a.asset],'Selected configuration changed during capture'
 assert inspector_hash==sha(ROOT/'tools/motorcycle-lab/review-v3.js') and capture_hash==sha(Path(__file__)),'Inspection code changed during capture'
 assert all(h==sha(ROOT/'assets-src/moto-components'/s) for s,h in export_hashes.items()),'Actual export changed during capture'
 report.update(pixel_checks=pixel_checks,page_errors=errors,http_failures=failures,pose_checks=pose_checks,scope='Actual Babylon imports and vertex motion in Chromium softwareWebGL; not Safari/iPhone/FPS qualification',render_mode='Manual frames after scene readiness',exports=[{'path':'assets-src/moto-components/'+s,'sha256':h} for s,h in export_hashes.items()],inspector_sha256=inspector_hash,capture_tool_sha256=capture_hash,inspector_path='tools/motorcycle-lab/review-v3.js',capture_tool_path='tools/capture_motorcycle18_v4.py',inputs_unchanged_during_capture=True)
 assert not errors and not failures,(errors,failures)
 (out/'engine-check.json').write_text(json.dumps(report,indent=2)+'\n');browser.close()
 print(json.dumps({'asset':a.asset,'meshes':report['meshes'],'triangles':report['triangles'],'rigs_checked':len(pose_checks),'errors':errors,'actual_canvas_pixel_checks':len(pixel_checks),'physical_iphone_tested':False}))
