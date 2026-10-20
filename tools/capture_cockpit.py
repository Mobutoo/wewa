"""Real Babylon.js cockpit review, actual exported pointers and touch-size viewport.
Start local Vite on4142 first. No game deployment or hardware qualification.
"""
import argparse,json,hashlib,math
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
pa=argparse.ArgumentParser();pa.add_argument('--asset',choices=['instruments','handlebar','grips','cockpit'],default='instruments');args=pa.parse_args()
paths={'instruments':'instruments/instruments-inspection.glb','handlebar':'handlebar/handlebar-inspection.glb','grips':'handlebar-grips/handlebar-grips-inspection.glb'}
review={'instruments':'instruments-v1','handlebar':'handlebar-v1','grips':'handlebar-grips-v1','cockpit':'cockpit-v1'}[args.asset]
OUT=ROOT/'creative/reviews'/review;OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1400,'height':1000},device_scale_factor=1);errors=[];failures=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:failures.append({'url':r.url,'status':r.status}) if r.status>=400 else None)
 page.goto('http://127.0.0.1:4142/tools/asset-lab/?asset='+args.asset,wait_until='networkidle',timeout=120000)
 page.wait_for_function('window.__ASSET_LAB__?.scene.isReady() && window.__ASSET_LAB__.report().textures_ready',timeout=90000)
 page.evaluate('window.__ASSET_LAB__.engine.stopRenderLoop();window.__ASSET_LAB__.scene.render()')
 def capture(name):
  page.evaluate('window.__ASSET_LAB__.scene.render()');page.wait_for_timeout(100);page.screenshot(path=str(OUT/name),timeout=90000)
 for view in ['quarter','side','tread']:
  page.evaluate('(view)=>window.__ASSET_LAB__.view(view)',view);page.wait_for_timeout(1500);capture('engine-'+view+'.png')
 states=[]
 if args.asset in ['instruments','cockpit']:
  page.evaluate("window.__ASSET_LAB__.view('side')")
  for speed,fuel,gear in [(0,0,0),(42,.65,3),(70,.5,4),(140,1,5),(-50,-1,-1),(190,2,8)]:
   page.evaluate('(pose)=>window.__ASSET_LAB__.setInstrumentPose(pose)',{'speed_kmh':speed,'fuel_fraction':fuel,'gear':gear});page.wait_for_timeout(250)
   page.evaluate('window.__ASSET_LAB__.scene.render()');states.append(page.evaluate('window.__ASSET_LAB__.report()'))
   if speed in [0,42,140]:capture('engine-pose-'+str(speed)+'.png')
  assert states[-2]['instrument_pose']=={'speed_kmh':0,'fuel_fraction':0,'gear':0}
  assert states[-1]['instrument_pose']=={'speed_kmh':140,'fuel_fraction':1,'gear':5}
  def distance(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
  assert distance(states[0]['pointer_tips_world_m']['speed'],states[3]['pointer_tips_world_m']['speed'])>.04
  assert distance(states[0]['pointer_tips_world_m']['fuel'],states[3]['pointer_tips_world_m']['fuel'])>.03
  page.evaluate('window.__ASSET_LAB__.setInstrumentPose({speed_kmh:42,fuel_fraction:.65,gear:3})')
  page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(1200);capture('engine-landscape-844x390.png')
 report=page.evaluate('window.__ASSET_LAB__.report()');report.update(page_errors=errors,http_failures=failures,pointer_pose_checks=states,scope='Actual exported candidates in Chromium softwareWebGL2; 844x390 is a viewport, not a physical iPhone test',public_game_unchanged=True,qa_render_loop_mode='manual frames for deterministic capture; no FPS benchmark')
 exports=paths.values() if args.asset=='cockpit' else [paths[args.asset]]
 report['exports']=[{'file':'assets-src/moto-components/'+name,'sha256':hashlib.sha256((ROOT/'assets-src/moto-components'/name).read_bytes()).hexdigest()} for name in exports]
 (OUT/'engine-check.json').write_text(json.dumps(report,indent=2)+'\n')
 assert not errors and not failures,(errors,failures)
 print('WEWA_COCKPIT_BROWSER',json.dumps({k:report[k] for k in ['asset','meshes','vertices','indices','textures_ready','page_errors','http_failures']}));browser.close()
