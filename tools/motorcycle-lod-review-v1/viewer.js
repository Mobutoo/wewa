import {Engine,Scene,ArcRotateCamera,Vector3,Color4,SceneLoader,HDRCubeTexture,HemisphericLight,StandardMaterial,Color3} from '@babylonjs/core';
import '@babylonjs/loaders/glTF';

const models={lod:'/assets-src/moto-components/motorcycle-lod-review-v1/motorcycle-lod.glb',source:'/assets-src/moto-components/motorcycle-assembled-v4.gltf'};
const selected=new URLSearchParams(location.search).get('model')||'lod';
if(!Object.hasOwn(models,selected))throw Error('Unknown review model');
document.querySelector('#model').value=selected;
document.querySelector('#model').onchange=e=>location.search='?model='+e.target.value;
const engine=new Engine(document.querySelector('canvas'),false,{preserveDrawingBuffer:true,stencil:true});
engine.setHardwareScalingLevel(2);
const scene=new Scene(engine);scene.useRightHandedSystem=true;scene.clearColor=new Color4(.18,.22,.27,1);
scene.environmentTexture=new HDRCubeTexture('/app/public/materials/kloppenheim_06_puresky_1k.hdr',scene,64,false,true,false,false);scene.environmentIntensity=.65;
const fill=new HemisphericLight('Review fill',new Vector3(0,1,0),scene);fill.intensity=.2;
const target=new Vector3(0,-.35,-.35),camera=new ArcRotateCamera('Same camera for both models',0,Math.PI/2,4,target,scene);
camera.attachControl(document.querySelector('canvas'),true);camera.fov=.48;camera.minZ=.01;camera.maxZ=50;camera.lowerRadiusLimit=.1;camera.upperRadiusLimit=10;scene.activeCamera=camera;
const views={quarter:{eye:[2.9,1,3]},left:{eye:[3.5,-.15,-.35]},right:{eye:[-3.5,-.15,-.35]},front:{eye:[0,-.3,4.3]},rear:{eye:[0,-.3,-4.8]},cockpit:{eye:[.55,.60,-.55],target:[0,.02,.02]}};
function view(name){const v=views[name];if(!v)throw Error('Unknown view');camera.setTarget(Vector3.FromArray(v.target||target.asArray()));camera.setPosition(Vector3.FromArray(v.eye));}
document.querySelectorAll('[data-view]').forEach(button=>button.onclick=()=>view(button.dataset.view));
window.addEventListener('resize',()=>engine.resize());
try{
 const url=models[selected],split=url.lastIndexOf('/');
 const result=await SceneLoader.ImportMeshAsync('',url.slice(0,split+1),url.slice(split+1),scene);
 document.querySelector('#status').textContent='Préparation de la vue…';
 scene.stopAllAnimations();const meshes=result.meshes.filter(m=>m.getTotalVertices()>0);
 if(!meshes.length)throw Error('Empty imported model');
 await scene.whenReadyAsync();for(const mesh of meshes)mesh.computeWorldMatrix(true);
 const originals=meshes.map(m=>m.material),white=new StandardMaterial('Silhouette measurement',scene);white.disableLighting=true;white.emissiveColor=Color3.White();white.backFaceCulling=false;
 const originalBackground=scene.clearColor.clone();
 function silhouette(enabled){meshes.forEach((m,i)=>m.material=enabled?white:originals[i]);scene.clearColor=enabled?new Color4(0,0,0,1):originalBackground;}
 function report(){return{model:selected,uri:url,meshes:meshes.length,triangles:meshes.reduce((s,m)=>s+m.getTotalIndices()/3,0),parents:scene.transformNodes.filter(n=>n.name.startsWith('PARENT [')).map(n=>({name:n.name,matrix:n.computeWorldMatrix(true).asArray()})),camera:{eye:camera.position.asArray(),target:camera.target.asArray()},textures_ready:scene.textures.every(t=>t.isReady()),renderer:engine.getGlInfo(),art_accepted:false,physical_iphone_tested:false};}
 view('quarter');window.__MOTO_LOD__={engine,scene,camera,view,report,silhouette};
 const info=report();document.querySelector('#status').textContent=`${selected==='lod'?'Candidat allégé':'Source détaillée'} · ${info.triangles.toLocaleString('fr')} triangles · ${info.parents.length} parents`;
 if(!new URLSearchParams(location.search).has('capture'))engine.runRenderLoop(()=>scene.render());
}catch(error){document.querySelector('#error').textContent=String(error);throw error;}
