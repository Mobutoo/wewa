// Local QA only. Does not replace a public game model or make performance claims.
import {Engine,Scene,ArcRotateCamera,Vector3,Color3,Color4,HemisphericLight,DirectionalLight,MeshBuilder,StandardMaterial,SceneLoader,HDRCubeTexture,Quaternion} from '@babylonjs/core';
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
const assets={instruments:['instruments','instruments-inspection.glb','compteurs seuls','Disposition publiée sur pageRDC : vitesse, carburant, rapports et USB. Dimensions estimées ; variante matérielle non certifiée.'],handlebar:['handlebar','handlebar-inspection.glb','guidon nu','Tube creux et zones moletées. Dimensions estimées, aucun montage mécanique reçu.'],grips:['handlebar-grips','handlebar-grips-inspection.glb','poignées seules','Deux enveloppes caoutchouc candidates ; commandes et manchon accélérateur non fabriqués.'],cockpit:['instruments','instruments-inspection.glb','poste de conduite candidat','Assemblage de revue des pièces isolées. Sans conducteur, contact ni commandes complètes ; ne constitue pas une scène du jeu.'],lever:['front-brake-lever','front-brake-lever-inspection.glb','levier de came avant seul','Référence voisine JA131607. Cotes, cannelures et finition estimées ; aucun montage reçu.'],tyre:['front-tyre','front-tyre-inspection.glb','pneu avant seul','Sculpture et dimensions gonflées estimées ; fournisseur inconnu. Le micrograin procédural Blender n’est pas encore cuit pour cet export.'],rim:['front-rim','front-rim-inspection.glb','jante avant seule','Cinq branches moulées. Diamètre nominal 17 pouces ; section, moyeu et valve estimés. Export réduit pour inspection, sans réception artistique.'],wheel:['front-rim','front-wheel-fit-inspection.glb','raccord pneu et jante avant','Contrôle visuel du raccord entre deux pièces candidates. Le flasque de frein et l’axe ne sont pas inclus dans cette révision ; étanchéité et montage mécanique non validés.'],plate:['front-brake-plate','front-brake-plate-inspection.glb','flasque avant seul','Corps moulé candidat d’après vues recto/verso JA131605. Variante RDC, dimensions et orientation de montage non confirmées. Aucun axe, levier ou frein fonctionnel.'],wheelpanel:['front-brake-plate','front-wheel-panel-fit-inspection.glb','raccord provisoire du flasque au moyeu','Pièces candidates, cotes estimées. Contrôle de dégagement uniquement ; orientation sur la fourche, étanchéité et fonctionnement non validés.']};
if(!assets[asset])throw new Error('Unknown inspection asset');
const [folder,file,label,details]=assets[asset];
document.querySelector('h1').textContent='Viva Wewa · '+label;
canvas.setAttribute('aria-label','Vue 3D : '+label);
document.querySelector('#details').textContent='Glisser pour tourner · molette ou pincement pour zoomer. '+details;
document.querySelector('[data-view="tread"]').textContent=asset==='plate'?'Verso':asset==='tyre'?'Bande de roulement':'Vue de tranche';
if(asset==='plate')document.querySelector('[data-view="side"]').textContent='Recto';
if(['instruments','handlebar','grips','cockpit'].includes(asset)){document.querySelector('[data-view="side"]').textContent='Vue conducteur';document.querySelector('[data-view="tread"]').textContent='Verso';}
const revision=new URLSearchParams(location.search).get('revision')||'v1';
if(revision==='v2'&&asset==='plate')assets.plate[1]='front-brake-plate-v2-inspection.glb';
if(revision==='v2'&&asset==='wheelpanel')assets.wheelpanel[1]='front-wheel-panel-v2-fit-inspection.glb';
const selectedFile=assets[asset][1];
const imported=await SceneLoader.ImportMeshAsync('','/assets-src/moto-components/'+folder+'/',selectedFile,scene);
if(asset==='cockpit')for(const [extraFolder,extraFile] of [['handlebar','handlebar-inspection.glb'],['handlebar-grips','handlebar-grips-inspection.glb']]){const extra=await SceneLoader.ImportMeshAsync('','/assets-src/moto-components/'+extraFolder+'/',extraFile,scene);imported.meshes.push(...extra.meshes);}
const meshes=imported.meshes.filter(m=>m.getTotalVertices()>0);let cinematic=false;
const views=asset==='plate'?{quarter:[-1.1,1.14,.35],side:[0,Math.PI/2,.36],tread:[Math.PI,Math.PI/2,.36]}:{quarter:[-1.1,1.14,1.25],side:[0,Math.PI/2,1.2],tread:[-Math.PI/2,1.5,.9]};
if(asset==='plate')camera.lowerRadiusLimit=.12;
if(asset==='lever'){camera.lowerRadiusLimit=.08;camera.fov=2*Math.atan(36/(2*80));views.quarter=[Math.atan2(.12,.32),Math.acos(.08/Math.hypot(.32,.12,.08)),Math.hypot(.32,.12,.08)];views.side=[0,Math.PI/2,.33];views.tread=[Math.PI,Math.PI/2,.33];}
let cockpitTarget=null;
if(['instruments','handlebar','grips','cockpit'].includes(asset)){
 scene.environmentIntensity=.28;camera.lowerRadiusLimit=.08;camera.fovMode=1;camera.fov=asset==='instruments'?.55:1.05;
 const small=asset==='instruments';cockpitTarget=small?new Vector3(0,.085,.12):new Vector3(0,.055,0);
 views.quarter=small?[-1.08,.90,.65]:[-1.15,1.05,.90];views.side=small?[-Math.PI/2,1.01,.65]:[-Math.PI/2,.96,.83];views.tread=small?[Math.PI/2,1.9,.62]:[Math.PI/2,1.35,.90];
}
function view(name){[camera.alpha,camera.beta,camera.radius]=views[name];camera.setTarget(cockpitTarget|| (asset==='lever'?new Vector3(0,.060,-.002):new Vector3(asset==='plate'?(revision==='v2'?.032:.035):0,.29,0)));}
if(revision==='v2'&&asset==='plate'){views.quarter=[Math.atan2(.25,.418),Math.acos(.20/Math.hypot(.418,.20,.25)),Math.hypot(.418,.20,.25)];camera.fov=2*Math.atan(36/(2*80));}
view('quarter');
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));
document.querySelector('#light').onclick=()=>{cinematic=!cinematic;key.diffuse=cinematic?new Color3(1,.72,.45):new Color3(1,1,1);fill.diffuse=cinematic?new Color3(.7,.8,1):new Color3(1,1,1);document.querySelector('#light').textContent=cinematic?'Lumière neutre':'Lumière cinématographique';};
const instrumentPose={speed_kmh:0,fuel_fraction:.65,gear:0};const instrumentInputs={};
function setInstrumentPose(next={}){
 if(!['instruments','cockpit'].includes(asset))return null;
 const finite=(value,old)=>Number.isFinite(Number(value))?Number(value):old;
 instrumentPose.speed_kmh=Math.min(140,Math.max(0,finite(next.speed_kmh??instrumentPose.speed_kmh,instrumentPose.speed_kmh)));
 instrumentPose.fuel_fraction=Math.min(1,Math.max(0,finite(next.fuel_fraction??instrumentPose.fuel_fraction,instrumentPose.fuel_fraction)));
 instrumentPose.gear=Math.round(Math.min(5,Math.max(0,finite(next.gear??instrumentPose.gear,instrumentPose.gear))));
 for(const [name,degrees] of [['SPEED_NEEDLE_PIVOT',225-instrumentPose.speed_kmh*270/140],['FUEL_NEEDLE_PIVOT',225-instrumentPose.fuel_fraction*80]]){
  const node=scene.getTransformNodeByName(name);if(!node)throw Error('Missing actual pointer pivot '+name);node.rotationQuaternion=Quaternion.RotationAxis(new Vector3(0,1,0),degrees*Math.PI/180);
 }
 for(let gear=1;gear<=5;gear++){const material=scene.getMaterialByName('Gear '+gear+' white indicator');if(material){const active=gear===instrumentPose.gear;material.albedoColor=active?new Color3(.08,.8,.25):new Color3(.82,.84,.8);material.emissiveColor=active?new Color3(.03,.35,.08):Color3.Black();}}
 for(const [key,input] of Object.entries(instrumentInputs))input.value=instrumentPose[key];
 return {...instrumentPose};
}
if(['instruments','cockpit'].includes(asset)){
 const controls=document.createElement('div');controls.style.cssText='position:fixed;right:24px;bottom:24px;padding:12px;background:#171c20dd;border-radius:8px;max-width:270px';
 for(const [key,label,min,max,step] of [['speed_kmh','Vitesse (km/h)',0,140,1],['fuel_fraction','Carburant',0,1,.01],['gear','Rapport (0=point mort)',0,5,1]]){
  const row=document.createElement('label');row.style.cssText='display:block;font-size:12px;margin:6px 0';row.textContent=label+' ';const input=document.createElement('input');input.type='range';Object.assign(input,{min,max,step,value:instrumentPose[key]});instrumentInputs[key]=input;input.setAttribute('aria-label',label);input.oninput=()=>setInstrumentPose({[key]:input.valueAsNumber});row.append(input);controls.append(row);
 }
 document.body.append(controls);setInstrumentPose({});
}
function pointerTip(prefix){const mesh=scene.meshes.find(m=>m.name===prefix+' red needle');if(!mesh)return null;mesh.computeWorldMatrix(true);const positions=mesh.getVerticesData('position');let index=0;for(let i=3;i<positions.length;i+=3)if(positions[i]>positions[index])index=i;return Vector3.TransformCoordinates(new Vector3(positions[index],positions[index+1],positions[index+2]),mesh.getWorldMatrix()).asArray();}
status.textContent='Pièce chargée · inspection locale, hors jeu public';
window.__ASSET_LAB__={scene,engine,camera,view,setInstrumentPose,report:()=>({asset,file:selectedFile,revision,environment_intensity:scene.environmentIntensity,instrument_pose:{...instrumentPose},pointer_tips_world_m:{speed:pointerTip('SPEED'),fuel:pointerTip('FUEL')},meshes:meshes.length,vertices:meshes.reduce((s,m)=>s+m.getTotalVertices(),0),indices:meshes.reduce((s,m)=>s+m.getTotalIndices(),0),textures_ready:scene.getWaitingItemsCount()===0,renderer:engine.getGlInfo(),art_accepted:false,physical_iphone_tested:false,procedural_micrograin_baked:revision==='v2'&&['plate','wheelpanel'].includes(asset),materials:meshes.map(m=>({name:m.material?.name,normal_texture:!!m.material?.bumpTexture,metallic_roughness_texture:!!m.material?.metallicTexture}))})};
engine.runRenderLoop(()=>scene.render());window.addEventListener('resize',()=>engine.resize());
