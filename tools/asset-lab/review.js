// Local QA only. Does not replace a public game model or make performance claims.
import {Engine,Scene,ArcRotateCamera,Vector3,Color3,Color4,HemisphericLight,DirectionalLight,MeshBuilder,StandardMaterial,SceneLoader,HDRCubeTexture} from '@babylonjs/core';
import '@babylonjs/loaders/glTF';
const canvas=document.querySelector('#view'),status=document.querySelector('#status');
const engine=new Engine(canvas,true,{preserveDrawingBuffer:true,stencil:true});
const scene=new Scene(engine);scene.useRightHandedSystem=true;scene.clearColor=new Color4(.10,.12,.14,1);
const camera=new ArcRotateCamera('review',-1.1,1.14,1.25,new Vector3(0,.29,0),scene);camera.minZ=.005;camera.lowerRadiusLimit=.3;camera.upperRadiusLimit=3;camera.wheelPrecision=90;camera.attachControl(canvas,true);
const fill=new HemisphericLight('fill',new Vector3(0,1,0),scene);fill.intensity=.7;fill.groundColor=new Color3(.12,.14,.17);
const key=new DirectionalLight('key',new Vector3(-1,-1,.5),scene);key.intensity=2;key.diffuse=new Color3(1,1,1);
const floor=MeshBuilder.CreateGround('inspection floor',{width:6,height:6},scene);floor.position.y=-.002;const mat=new StandardMaterial('floor',scene);mat.diffuseColor=new Color3(.22,.24,.26);mat.specularColor=new Color3(.02,.02,.02);floor.material=mat;
scene.environmentTexture=new HDRCubeTexture('/app/public/materials/kloppenheim_06_puresky_1k.hdr',scene,128,false,true,false,true);
scene.environmentIntensity=.45;
const imported=await SceneLoader.ImportMeshAsync('','/assets-src/moto-components/front-tyre/','front-tyre-inspection.glb',scene);
const meshes=imported.meshes.filter(m=>m.getTotalVertices()>0);let cinematic=false;
const views={quarter:[-1.1,1.14,1.25],side:[0,Math.PI/2,1.2],tread:[-Math.PI/2,1.5,.9]};
function view(name){[camera.alpha,camera.beta,camera.radius]=views[name];camera.setTarget(new Vector3(0,.29,0));}
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));
document.querySelector('#light').onclick=()=>{cinematic=!cinematic;key.diffuse=cinematic?new Color3(1,.72,.45):new Color3(1,1,1);fill.diffuse=cinematic?new Color3(.7,.8,1):new Color3(1,1,1);document.querySelector('#light').textContent=cinematic?'Lumière neutre':'Lumière cinématographique';};
status.textContent='Pièce chargée · inspection locale, hors jeu public';
window.__ASSET_LAB__={scene,engine,camera,view,report:()=>({meshes:meshes.length,vertices:meshes.reduce((s,m)=>s+m.getTotalVertices(),0),indices:meshes.reduce((s,m)=>s+m.getTotalIndices(),0),textures_ready:scene.getWaitingItemsCount()===0,renderer:engine.getGlInfo(),art_accepted:false,physical_iphone_tested:false,procedural_micrograin_baked:false})};
engine.runRenderLoop(()=>scene.render());window.addEventListener('resize',()=>engine.resize());
