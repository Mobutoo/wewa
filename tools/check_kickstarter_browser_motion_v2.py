"""V2 frozen candidate only; preserve the historical v1 checker.
Compare real Babylon moving vertex with frozen Blender direction witness; no source writes."""
import json,hashlib,math
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];folder=R/'assets-src/moto-components/kickstarter';contract=json.loads((folder/'gltf-node-map-v2.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(folder/'kickstarter-v2.blend')==contract['source_sha256'] and sha(folder/'kickstarter-v2-inspection.glb')==contract['export_sha256']
witness=contract['actual_direction_proof'];convert=lambda v:[v[0],v[2],-v[1]]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']);page=browser.new_page();page.goto('http://127.0.0.1:4143/tools/motorcycle-lab/v4.html?asset=kickstarter-v2',wait_until='networkidle',timeout=120000);page.wait_for_function('window.__MOTO_LAB__?.scene.isReady()',timeout=90000);page.evaluate('window.__MOTO_LAB__.engine.stopRenderLoop();window.__MOTO_LAB__.setPose({kick_fold:0,kick_stroke:0})')
 match=page.evaluate('''expected=>{let best={distance:Infinity};for(const mesh of window.__MOTO_LAB__.scene.meshes){if(!mesh.getTotalVertices())continue;const p=mesh.getVerticesData('position'),m=mesh.computeWorldMatrix(true).asArray();for(let i=0;i<p.length;i+=3){const [x,y,z]=p.slice(i,i+3),q=[x*m[0]+y*m[4]+z*m[8]+m[12],x*m[1]+y*m[5]+z*m[9]+m[13],x*m[2]+y*m[6]+z*m[10]+m[14]],distance=Math.hypot(...q.map((v,j)=>v-expected[j]));if(distance<best.distance)best={mesh:mesh.name,vertex_index:i/3,distance,point:q};}}return best;}''',convert(witness['rest_world_m']))
 assert match['distance']<2e-7,match
 states=[]
 for name,pose,key in [('rest',{'kick_fold':0,'kick_stroke':0},'rest_world_m'),('fold90',{'kick_fold':90,'kick_stroke':0},'fold90_world_m'),('stroke60',{'kick_fold':90,'kick_stroke':60},'stroke60_world_m')]:
  page.evaluate('(p)=>window.__MOTO_LAB__.setPose(p)',pose)
  actual=page.evaluate('''a=>{const mesh=window.__MOTO_LAB__.scene.getMeshByName(a.mesh),p=mesh.getVerticesData('position'),m=mesh.computeWorldMatrix(true).asArray(),i=a.vertex_index*3,[x,y,z]=p.slice(i,i+3);return [x*m[0]+y*m[4]+z*m[8]+m[12],x*m[1]+y*m[5]+z*m[9]+m[13],x*m[2]+y*m[6]+z*m[10]+m[14]];}''',match);expected=convert(witness[key]);error=math.dist(actual,expected);assert error<2e-7,(name,error);states.append({'state':name,'pose':pose,'actual_glTF_world_m':actual,'Blender_witness_glTF_world_m':expected,'distance_m':error})
 browser.close()
report={'source_sha256':contract['source_sha256'],'export_sha256':contract['export_sha256'],'contract_sha256':sha(folder/'gltf-node-map-v2.json'),'inspector_path':'tools/motorcycle-lab/review-v4.js','inspector_sha256':sha(R/'tools/motorcycle-lab/review-v4.js'),'tool_path':str(Path(__file__).relative_to(R)),'tool_sha256':sha(Path(__file__)),'actual_matched_vertex':match,'states':states,'max_error_m':max(s['distance_m']for s in states),'technical_passed':True,'scope':'Three actual moving vertex states versus frozen Blender direction witness; not full mechanics, estimated joint stops or physical iPhone qualification','art_accepted':False};(R/'creative/reviews/kickstarter-v2/browser-source-motion-parity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'states':len(states),'max_error_m':report['max_error_m']}))
