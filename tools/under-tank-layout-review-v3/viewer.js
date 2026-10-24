import {Engine,Scene,ArcRotateCamera,Vector3,Color4,HDRCubeTexture,HemisphericLight,SceneLoader} from '@babylonjs/core';
import '@babylonjs/loaders/glTF';
const capture=new URLSearchParams(location.search).has('capture');
if(capture)document.body.classList.add('capture');
const engine=new Engine(document.querySelector('canvas'),true,{preserveDrawingBuffer:true});
engine.setHardwareScalingLevel(1);
const scene=new Scene(engine);scene.useRightHandedSystem=true;
scene.clearColor=new Color4(.18,.22,.27,1);
scene.environmentTexture=new HDRCubeTexture('/app/public/materials/kloppenheim_06_puresky_1k.hdr',scene,64,false,true,false,false);
scene.environmentIntensity=.65;new HemisphericLight('Fill',new Vector3(0,1,0),scene).intensity=.3;
const camera=new ArcRotateCamera('Review',0,Math.PI/2,1,Vector3.Zero(),scene);camera.attachControl(engine.getRenderingCanvas(),true);
camera.fov=.43;camera.minZ=.005;camera.maxZ=25;camera.lowerRadiusLimit=.15;
window.addEventListener('resize',()=>engine.resize());
const poses={front:{p:[2.75,.75,2.8],t:[0,-.39,-.35]},rear:{p:[2.7,.7,-3.45],t:[0,-.36,-.35]},
'centre-right':{p:[-1.8,-.31,-.1],t:[0,-.36,-.42]},centre:{p:[1.8,-.31,-.1],t:[0,-.36,-.42]},left:{p:[4,-.35,-.35],t:[0,-.35,-.35]},right:{p:[-4,-.35,-.35],t:[0,-.35,-.35]},head:{p:[0,-.35,3.65],t:[0,-.35,-.35]},tail:{p:[0,-.35,-4.35],t:[0,-.35,-.35]},lamp:{p:[1.25,.16,1.2],t:[0,-.10,.22]},transmission:{p:[2.25,-.62,-.68],t:[0,-.62,-.57]},plate:{p:[0,-.417,-1.8],t:[0,-.417,-1.21]}};
try{
  const before=new URLSearchParams(location.search).has('before');
  await SceneLoader.ImportMeshAsync('',before?'/assets-src/moto-components/visual-proportions-v2/':'/assets-src/moto-components/under-tank-layout-v3/',before?'motorcycle-proportions.glb':'motorcycle-layout.glb',scene);
  await scene.whenReadyAsync();
  let current='front';
  function view(name){const pose=poses[name];if(!pose)throw Error('Vue inconnue');current=name;camera.mode=['left','right'].includes(name)?1:0;camera.orthoTop=.85;camera.orthoBottom=-.85;camera.orthoLeft=-.85*engine.getRenderWidth()/engine.getRenderHeight();camera.orthoRight=-camera.orthoLeft;camera.setTarget(Vector3.FromArray(pose.t));camera.setPosition(Vector3.FromArray(pose.p));scene.render()}
  function report(){return {view:current,width:engine.getRenderWidth(),height:engine.getRenderHeight(),
    triangles:scene.meshes.reduce((s,m)=>s+m.getTotalIndices()/3,0),textures_ready:scene.textures.every(t=>t.isReady()),
    text_meshes:scene.meshes.filter(m=>m.name.startsWith('Plate text')).map(m=>m.name),
    camera:{position:camera.position.asArray(),target:camera.target.asArray(),fov:camera.fov},art_accepted:false}}
  window.__PROPORTIONS__={scene,engine,camera,view,report};view('front');
  for(const b of document.querySelectorAll('[data-view]'))b.onclick=()=>view(b.dataset.view);
  if(!capture)engine.runRenderLoop(()=>scene.render());
}catch(e){document.querySelector('#error').textContent=String(e);throw e}
