import {Engine, Scene, ArcRotateCamera, Vector3, Color4, HDRCubeTexture, HemisphericLight, SceneLoader} from '@babylonjs/core';
import '@babylonjs/loaders/glTF';

const canvas=document.querySelector('canvas');
const engine=new Engine(canvas,false,{preserveDrawingBuffer:true});
engine.setHardwareScalingLevel(1.5);
const scene=new Scene(engine);
scene.useRightHandedSystem=true;
scene.clearColor=new Color4(.18,.22,.27,1);
scene.environmentTexture=new HDRCubeTexture('/app/public/materials/kloppenheim_06_puresky_1k.hdr',scene,64,false,true,false,false);
scene.environmentIntensity=.65;
new HemisphericLight('Fill',new Vector3(0,1,0),scene).intensity=.3;
const camera=new ArcRotateCamera('Review',0,Math.PI/2,1,Vector3.Zero(),scene);
camera.attachControl(canvas,true);camera.fov=.48;camera.lowerRadiusLimit=.03;camera.upperRadiusLimit=8;
window.addEventListener('resize',()=>engine.resize());
try {
  await SceneLoader.ImportMeshAsync('', '/assets-src/moto-components/handlebar-registration-v2/', 'motorcycle-registration-candidate.glb', scene);
  await scene.whenReadyAsync();
  const groups=scene.transformNodes.filter(n=>n.name.startsWith('PARENT ['));
  if(groups.length!==177)throw Error('Inventaire incomplet');
  const corrections=await fetch('/creative/reviews/handlebar-registration-v2/derivation-check.json').then(r=>{if(!r.ok)throw Error('Rapport indisponible');return r.json()});
  const changes=corrections.files.find(f=>f.output.endsWith('motorcycle-registration-candidate.glb')).changes;
  const parts=changes.map(change=>{
    const node=scene.getNodeByName(change.name);if(!node)throw Error('Pièce manquante : '+change.name);
    if(Vector3.Distance(node.position,Vector3.FromArray(change.after))>1e-7)throw Error('Pose inattendue');
    return {node,change};
  });
  let corrected=true,mode='underside';
  function version(value){
    corrected=value;
    for(const {node,change} of parts)node.position.copyFromFloats(...(value?change.after:change.before));
    document.querySelector('#before').setAttribute('aria-pressed',String(!value));
    document.querySelector('#after').setAttribute('aria-pressed',String(value));
    document.querySelector('#description').textContent=value?'Chaque pontet et ses boulons sont rapprochés de 6,5 mm du centre. Les autres éléments conservent leur position.':'Position v5 : les goujons traversent la matière de la plaque supérieure.';
    scene.render();
  }
  function view(value){
    if(!['whole','underside','top'].includes(value))throw Error('Vue inconnue');
    mode=value;
    for(const group of groups)group.setEnabled(value==='whole'||['PARENT [clamps]','PARENT [handlebar]','PARENT [steering-upper]'].includes(group.name));
    const close=value!=='whole';
    camera.minZ=close?.001:.05;camera.maxZ=close?3:20;
    camera.setTarget(Vector3.FromArray(close?[0,-.035,.0975]:[0,-.35,-.35]));
    camera.setPosition(Vector3.FromArray(value==='whole'?[2.9,1,3]:value==='top'?[.11,.44,.34]:[.16,-.39,-.10]));
    scene.render();
  }
  document.querySelector('#before').onclick=()=>version(false);
  document.querySelector('#after').onclick=()=>version(true);
  for(const key of ['whole','underside','top'])document.querySelector('#'+key).onclick=()=>view(key);
  function report(){return {corrected,mode,groups:groups.length,
    triangles:scene.meshes.reduce((s,m)=>s+m.getTotalIndices()/3,0),
    textures_ready:scene.textures.every(t=>t.isReady()),
    parts:parts.map(({node,change})=>({name:change.name,position:node.position.asArray()})),
    enabled_groups:groups.filter(n=>n.isEnabled()).map(n=>n.name),
    parent_matrices:groups.map(n=>({name:n.name,matrix:n.computeWorldMatrix(true).asArray()})),
    renderer:engine.getGlInfo(),art_accepted:false,physical_iphone_tested:false};}
  window.__REGISTRATION__={scene,engine,camera,view,version,report};
  view('underside');
  document.querySelector('#status').textContent='177 groupes conservés · comparaison avant / candidat';
  if(!new URLSearchParams(location.search).has('capture'))engine.runRenderLoop(()=>scene.render());
}catch(error){document.querySelector('#error').textContent=String(error);throw error;}
