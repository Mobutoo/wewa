"""Capture the fabricated lot inside the existing engine without replacing public game assets.

Requires the existing local Vite server at 127.0.0.1:5173 and Chromium/Playwright.
Review GLB responses are substituted locally. No deployment.
"""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser()
parser.add_argument('--lot',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    errors=[];failed=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.on('response',lambda response:failed.append({'url':response.url,'status':response.status}) if response.status>=400 else None)
    page.route('**/models/rider.glb',lambda route:route.fulfill(path=str(args.lot/'rider/rider-validation.glb'),content_type='model/gltf-binary'))
    page.route('**/models/motorcycle.glb',lambda route:route.fulfill(path=str(args.lot/'motorcycle/motorcycle-validation.glb'),content_type='model/gltf-binary'))
    page.route('**/models/hero-review-arms.glb',lambda route:route.fulfill(path=str(args.lot/'rider/firstperson-validation.glb'),content_type='model/gltf-binary'))
    cargo_file=args.lot/'cargo/cargo-validation.glb'
    if cargo_file.exists():
        page.route('**/models/hero-review-cargo.glb',lambda route:route.fulfill(path=str(cargo_file),content_type='model/gltf-binary'))
    page.goto('http://127.0.0.1:5173/',wait_until='networkidle')
    page.locator('#play').click();page.wait_for_selector('#hud:not(.hidden)',timeout=60000)
    page.wait_for_function('window.__WEWA__?.world()?.scene.skeletons.some(s=>s.bones.length===53)',timeout=60000)
    page.wait_for_function('window.__WEWA__?.snapshot()?.loadedCells>0',timeout=60000)
    page.wait_for_function('window.__WEWA__.world().scene.getWaitingItemsCount()===0',timeout=60000)
    page.evaluate('''()=>{const s=window.__WEWA__.sim();s.paused=false;for(let i=0;i<180;i++)s.step({gas:false,brake:false,left:false,right:false,nitro:false,horn:false});s.paused=true;const w=window.__WEWA__.world();w.update(s,0);w.scene.animationGroups.forEach(a=>a.pause());}''')
    cargo=None
    if cargo_file.exists():
        cargo=page.evaluate('''async()=>{const url=performance.getEntriesByType('resource').map(r=>r.name).find(n=>n.includes('sceneLoader')&&n.includes('/.vite/deps/'));if(!url)throw Error('Existing loader module not found');const {SceneLoader}=await import(url);const w=window.__WEWA__.world(),V=w.bike.position.constructor;const imported=await SceneLoader.ImportMeshAsync('','/models/','hero-review-cargo.glb',w.scene);imported.meshes.filter(m=>!m.parent).forEach(m=>{m.parent=w.bike;m.position.addInPlace(new V(0,.83,-.67));});w.update(window.__WEWA__.sim(),0);return {meshes:imported.meshes.length,local_position:[0,.83,-.67],status:'loaded_review_variant_not_gameplay_inventory_integration'};}''')
        page.wait_for_function('window.__WEWA__.world().scene.getWaitingItemsCount()===0',timeout=60000)
        page.evaluate('window.__WEWA__.world().update(window.__WEWA__.sim(),0)')
    # Capture an ordinary game view first; overlay and source city remain visible.
    page.wait_for_timeout(400);page.screenshot(path=str(args.out/'engine-context.png'))
    # Model inspection angles use the same engine, materials, sun and live source city.
    for name,offset in [('engine-rear-quarter',[2.2,1.9,-3.4]),('engine-side',[3.7,1.4,.1]),('engine-front-quarter',[2.2,1.8,3.4])]:
        page.evaluate('''({offset})=>{const w=window.__WEWA__.world(),V=w.bike.position.constructor;if(w.__reviewObserver)w.scene.onBeforeRenderObservable.remove(w.__reviewObserver);w.__reviewObserver=w.scene.onBeforeRenderObservable.add(()=>{w.bike.computeWorldMatrix(true);const matrix=w.bike.getWorldMatrix();w.camera.position.copyFrom(V.TransformCoordinates(new V(...offset),matrix));w.camera.setTarget(V.TransformCoordinates(new V(0,.95,0),matrix));w.camera.fov=.65;});w.update(window.__WEWA__.sim(),0);}''',{'offset':offset})
        page.wait_for_timeout(250);page.screenshot(path=str(args.out/(name+'.png')))
    # Review-only first-person proposal, not a change to public camera settings.
    firstperson=page.evaluate('''async()=>{const url=performance.getEntriesByType('resource').map(r=>r.name).find(n=>n.includes('sceneLoader')&&n.includes('/.vite/deps/'));if(!url)throw Error('Existing loader module not found');const {SceneLoader}=await import(url);const w=window.__WEWA__.world();const imported=await SceneLoader.ImportMeshAsync('','/models/','hero-review-arms.glb',w.scene);imported.meshes.filter(m=>!m.parent).forEach(m=>m.parent=w.bike);w.setCamera(true);if(w.__reviewObserver)w.scene.onBeforeRenderObservable.remove(w.__reviewObserver);w.__reviewObserver=w.scene.onBeforeRenderObservable.add(()=>{const V=w.bike.position.constructor,matrix=w.bike.getWorldMatrix();w.camera.position.copyFrom(V.TransformCoordinates(new V(0,1.56,-.16),matrix));w.camera.setTarget(V.TransformCoordinates(new V(0,1.02,2.10),matrix));w.camera.fov=78*Math.PI/180;});w.update(window.__WEWA__.sim(),0);return {meshes:imported.meshes.length,camera_local_position:[0,1.56,-.16],camera_local_target:[0,1.02,2.10],fov_degrees:78,status:'proposed_for_review_not_public_camera_change'};}''')
    page.wait_for_function('window.__WEWA__.world().scene.getWaitingItemsCount()===0',timeout=60000)
    page.evaluate('window.__WEWA__.world().update(window.__WEWA__.sim(),0)')
    page.screenshot(path=str(args.out/'engine-handlebar-proposal.png'))
    page.evaluate('window.__WEWA__.world().setCamera(false)')
    # Check actual skinned actor world movement follows the motorcycle parent.
    movement=page.evaluate('''async()=>{const w=window.__WEWA__.world(),s=window.__WEWA__.sim();const mesh=w.rider.getChildMeshes().find(m=>m.skeleton&&m.name.includes('Garment_male'));if(!mesh)throw Error('Skinned garment missing');const before=mesh.getAbsolutePosition().clone(),x=s.vehicle.x;s.vehicle.x+=3;s.previousPose.x+=3;w.update(s,0);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));const after=mesh.getAbsolutePosition().clone();s.vehicle.x=x;s.previousPose.x=x;w.update(s,0);return {before:before.asArray(),after:after.asArray(),delta:after.subtract(before).asArray()};}''')
    assert abs(movement['delta'][0]-3)<.05,movement
    report=page.evaluate('''()=>{const w=window.__WEWA__.world();return {skeletons:w.scene.skeletons.map(s=>({name:s.name,bones:s.bones.length})),rider_meshes:w.rider.getChildMeshes().length,rider_materials:[...new Set(w.rider.getChildMeshes().map(m=>m.material?.name))],animations:w.scene.animationGroups.map(a=>a.name),renderer:w.engine.getGlInfo(),runtime_textures_loaded:w.scene.getWaitingItemsCount()===0};}''')
    report.update({'qualification':'Local Chromium software renderer; review GLB responses replaced only for asset inspection. Not a deployed game version, iPhone benchmark or acceptance of city graphics.', 'cargo_review_variant':cargo,'firstperson_proposal':firstperson,'skinned_parent_movement':movement,'page_errors':errors,'http_failures':failed,'art_accepted':False})
    (args.out/'engine-check.json').write_text(json.dumps(report,indent=2)+'\n')
    assert not errors and not failed,(errors,failed)
    browser.close()
print(json.dumps({'rider_meshes':report['rider_meshes'],'skeletons':report['skeletons'],'errors':errors,'failed':failed,'parent_movement':movement['delta']}))
