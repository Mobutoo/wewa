import {Engine, Scene, ArcRotateCamera, Vector3, Color4, HDRCubeTexture, HemisphericLight, SceneLoader} from '@babylonjs/core';
import '@babylonjs/loaders/glTF';

const canvas=document.querySelector('canvas');
const engine=new Engine(canvas,true,{preserveDrawingBuffer:true});
const scene=new Scene(engine);scene.useRightHandedSystem=true;
scene.clearColor=new Color4(.18,.22,.27,1);
scene.environmentTexture=new HDRCubeTexture('/app/public/materials/kloppenheim_06_puresky_1k.hdr',scene,64,false,true,false,false);
scene.environmentIntensity=.65;
new HemisphericLight('Fill',new Vector3(0,1,0),scene).intensity=.3;
const camera=new ArcRotateCamera('Review',0,Math.PI/2,1,Vector3.Zero(),scene);
camera.attachControl(canvas,true);camera.fov=.48;camera.lowerRadiusLimit=.2;camera.upperRadiusLimit=9;
camera.minZ=.005;camera.maxZ=25;
window.addEventListener('resize',()=>engine.resize());
const views={whole:{p:[2.9,1,3],t:[0,-.35,-.35]},left:{p:[4,-.35,-.35],t:[0,-.35,-.35]},right:{p:[-4,-.35,-.35],t:[0,-.35,-.35]},
  detailLeft:{p:[1.58,-.39,.22],t:[0,-.44,-.235]},detailRight:{p:[-1.58,-.39,.22],t:[0,-.44,-.235]},isolated:{p:[1.8,-.25,.5],t:[0,-.35,-.2]}};
try{
  // The candidate keeps original bytes but detaches four replaced studies.
  // Load those studies from the original file solely for the Before toggle.
  const plan=await fetch('/creative/research/under-tank-completion-v1/plan.json').then(r=>r.json());
  await SceneLoader.ImportMeshAsync('', '/assets-src/moto-components/under-tank-completion-v1/', 'motorcycle-completed-candidate.glb', scene);
  const current=scene.transformNodes.filter(n=>n.name.startsWith('PARENT ['));
  const added=scene.transformNodes.filter(n=>n.name.startsWith('COMPLETION ['));
  if(current.length!==173||added.length!==10)throw Error('Inventaire candidat incomplet');
  const original=await SceneLoader.LoadAssetContainerAsync('/assets-src/moto-components/handlebar-registration-v2/','motorcycle-registration-candidate.glb',scene);
  const oldGroups=original.transformNodes.filter(n=>plan.replace_groups.includes(n.name.slice(8,-1)));
  if(oldGroups.length!==4)throw Error('Inventaire avant incomplet');
  original.addAllToScene();
  for(const n of original.transformNodes.filter(n=>n.name.startsWith('PARENT [')))n.setEnabled(oldGroups.includes(n));
  await scene.whenReadyAsync();
  let completed=true,mode='whole';
  function state(){
    for(const n of current)n.setEnabled(mode!=='isolated');
    for(const n of oldGroups)n.setEnabled(!completed);
    for(const n of added)n.setEnabled(completed);
    document.querySelector('#before').setAttribute('aria-pressed',String(!completed));
    document.querySelector('#after').setAttribute('aria-pressed',String(completed));
    scene.render();
  }
  function version(value){completed=value;state()}
  function view(value){if(!views[value])throw Error('Vue inconnue');mode=value;camera.setTarget(Vector3.FromArray(views[value].t));camera.setPosition(Vector3.FromArray(views[value].p));state()}
  function report(){return {completed,mode,retained_groups:current.length,added_groups:added.length,old_groups:oldGroups.length,
    visible_meshes:scene.meshes.filter(m=>m.isEnabled()&&m.getTotalVertices()>0).length,
    visible_triangles:scene.meshes.filter(m=>m.isEnabled()).reduce((s,m)=>s+m.getTotalIndices()/3,0),
    textures_ready:scene.textures.every(t=>t.isReady()),
    camera:{position:camera.position.asArray(),target:camera.target.asArray(),fov:camera.fov},
    renderer:engine.getGlInfo(),art_accepted:false,physical_iphone_tested:false}}
  window.__UNDER_TANK__={scene,engine,camera,view,version,report};
  document.querySelector('#before').onclick=()=>version(false);document.querySelector('#after').onclick=()=>version(true);
  for(const button of document.querySelectorAll('[data-view]'))button.onclick=()=>view(button.dataset.view);
  view('whole');document.querySelector('#status').textContent='Moto complète · candidat à examiner';
  if(!new URLSearchParams(location.search).has('capture'))engine.runRenderLoop(()=>scene.render());
}catch(e){document.querySelector('#error').textContent=String(e);throw e}
