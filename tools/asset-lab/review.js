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
const asset=new URLSearchParams(location.search).get('asset')||'tyre';
const assets={lever:['front-brake-lever','front-brake-lever-inspection.glb','levier de came avant seul','Référence voisine JA131607. Cotes, cannelures et finition estimées ; aucun montage reçu.'],tyre:['front-tyre','front-tyre-inspection.glb','pneu avant seul','Sculpture et dimensions gonflées estimées ; fournisseur inconnu. Le micrograin procédural Blender n’est pas encore cuit pour cet export.'],rim:['front-rim','front-rim-inspection.glb','jante avant seule','Cinq branches moulées. Diamètre nominal 17 pouces ; section, moyeu et valve estimés. Export réduit pour inspection, sans réception artistique.'],wheel:['front-rim','front-wheel-fit-inspection.glb','raccord pneu et jante avant','Contrôle visuel du raccord entre deux pièces candidates. Le flasque de frein et l’axe ne sont pas inclus dans cette révision ; étanchéité et montage mécanique non validés.'],plate:['front-brake-plate','front-brake-plate-inspection.glb','flasque avant seul','Corps moulé candidat d’après vues recto/verso JA131605. Variante RDC, dimensions et orientation de montage non confirmées. Aucun axe, levier ou frein fonctionnel.'],wheelpanel:['front-brake-plate','front-wheel-panel-fit-inspection.glb','raccord provisoire du flasque au moyeu','Pièces candidates, cotes estimées. Contrôle de dégagement uniquement ; orientation sur la fourche, étanchéité et fonctionnement non validés.']};
if(!assets[asset])throw new Error('Unknown inspection asset');
const [folder,file,label,details]=assets[asset];
document.querySelector('h1').textContent='Viva Wewa · '+label;
canvas.setAttribute('aria-label','Vue 3D : '+label);
document.querySelector('#details').textContent='Glisser pour tourner · molette ou pincement pour zoomer. '+details;
document.querySelector('[data-view="tread"]').textContent=asset==='plate'?'Verso':asset==='tyre'?'Bande de roulement':'Vue de tranche';
if(asset==='plate')document.querySelector('[data-view="side"]').textContent='Recto';
const revision=new URLSearchParams(location.search).get('revision')||'v1';
if(revision==='v2'&&asset==='plate')assets.plate[1]='front-brake-plate-v2-inspection.glb';
if(revision==='v2'&&asset==='wheelpanel')assets.wheelpanel[1]='front-wheel-panel-v2-fit-inspection.glb';
const selectedFile=assets[asset][1];
const imported=await SceneLoader.ImportMeshAsync('','/assets-src/moto-components/'+folder+'/',selectedFile,scene);
const meshes=imported.meshes.filter(m=>m.getTotalVertices()>0);let cinematic=false;
const views=asset==='plate'?{quarter:[-1.1,1.14,.35],side:[0,Math.PI/2,.36],tread:[Math.PI,Math.PI/2,.36]}:{quarter:[-1.1,1.14,1.25],side:[0,Math.PI/2,1.2],tread:[-Math.PI/2,1.5,.9]};
if(asset==='plate')camera.lowerRadiusLimit=.12;
if(asset==='lever'){camera.lowerRadiusLimit=.08;camera.fov=2*Math.atan(36/(2*80));views.quarter=[Math.atan2(.12,.32),Math.acos(.08/Math.hypot(.32,.12,.08)),Math.hypot(.32,.12,.08)];views.side=[0,Math.PI/2,.33];views.tread=[Math.PI,Math.PI/2,.33];}
function view(name){[camera.alpha,camera.beta,camera.radius]=views[name];camera.setTarget(asset==='lever'?new Vector3(0,.060,-.002):new Vector3(asset==='plate'?(revision==='v2'?.032:.035):0,.29,0));}
if(revision==='v2'&&asset==='plate'){views.quarter=[Math.atan2(.25,.418),Math.acos(.20/Math.hypot(.418,.20,.25)),Math.hypot(.418,.20,.25)];camera.fov=2*Math.atan(36/(2*80));}
view('quarter');
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));
document.querySelector('#light').onclick=()=>{cinematic=!cinematic;key.diffuse=cinematic?new Color3(1,.72,.45):new Color3(1,1,1);fill.diffuse=cinematic?new Color3(.7,.8,1):new Color3(1,1,1);document.querySelector('#light').textContent=cinematic?'Lumière neutre':'Lumière cinématographique';};
status.textContent='Pièce chargée · inspection locale, hors jeu public';
window.__ASSET_LAB__={scene,engine,camera,view,report:()=>({asset,file:selectedFile,revision,meshes:meshes.length,vertices:meshes.reduce((s,m)=>s+m.getTotalVertices(),0),indices:meshes.reduce((s,m)=>s+m.getTotalIndices(),0),textures_ready:scene.getWaitingItemsCount()===0,renderer:engine.getGlInfo(),art_accepted:false,physical_iphone_tested:false,procedural_micrograin_baked:revision==='v2'&&['plate','wheelpanel'].includes(asset),materials:meshes.map(m=>({name:m.material?.name,normal_texture:!!m.material?.bumpTexture,metallic_roughness_texture:!!m.material?.metallicTexture}))})};
engine.runRenderLoop(()=>scene.render());window.addEventListener('resize',()=>engine.resize());
