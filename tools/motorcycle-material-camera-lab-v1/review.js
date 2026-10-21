// Read-only same-camera comparison. Display/HDR responses are explicitly not calibrated.
import {Engine,Scene,FreeCamera,Vector3,Color4,Matrix,SceneLoader,HDRCubeTexture,ImageProcessingConfiguration} from '@babylonjs/core';
import '@babylonjs/loaders/glTF';
const path=new URLSearchParams(location.search).get('spec');
if(!path?.startsWith('/creative/reviews/')||path.includes('..'))throw Error('Expected a repository review camera specification');
const response=await fetch(path);if(!response.ok)throw Error('Camera spec missing');const spec=await response.json();
const engine=new Engine(document.querySelector('canvas'),true,{preserveDrawingBuffer:true,stencil:true}),scene=new Scene(engine);
scene.useRightHandedSystem=true;scene.clearColor=new Color4(.12,.12,.12,1);
const camera=new FreeCamera('Exact native preview camera',Vector3.FromArray(spec.camera_gltf.position_m),scene);
camera.upVector=Vector3.FromArray(spec.camera_gltf.up_vector);camera.setTarget(Vector3.FromArray(spec.camera_gltf.target_m));
camera.fov=spec.camera_gltf.vertical_fov_radians;camera.fovMode=0;camera.minZ=spec.camera_gltf.near_m;camera.maxZ=spec.camera_gltf.far_m;
scene.environmentTexture=new HDRCubeTexture('/'+spec.HDR,scene,256,false,true,false,true);scene.environmentIntensity=spec.environment_intensity;
const image=scene.imageProcessingConfiguration;image.toneMappingEnabled=true;image.toneMappingType=ImageProcessingConfiguration.TONEMAPPING_ACES;
image.exposure=2**spec.exposure_EV;image.contrast=1;
const slash=spec.export.lastIndexOf('/'),result=await SceneLoader.ImportMeshAsync('','/'+spec.export.slice(0,slash+1),spec.export.slice(slash+1),scene);
scene.stopAllAnimations();for(const group of scene.animationGroups){group.stop();group.reset();}
const meshes=result.meshes.filter(m=>m.getTotalVertices()>0);if(!meshes.length)throw Error('No actual meshes');
function report(){
  scene.render();const viewport=camera.viewport.toGlobal(engine.getRenderWidth(),engine.getRenderHeight());
  const witnesses=spec.software_projection_witnesses.map(w=>{const p=Vector3.Project(Vector3.FromArray(w.gltf_world_m),Matrix.Identity(),scene.getTransformMatrix(),viewport);return {...w,Babylon_pixel_xy:[p.x,p.y],pixel_difference:Math.hypot(p.x-w.native_pixel_xy[0],p.y-w.native_pixel_xy[1])};});
  return {spec,meshes:meshes.length,drawn_triangles:meshes.reduce((s,m)=>s+m.getTotalIndices()/3,0),textures_ready:scene.getWaitingItemsCount()===0,
    actual_camera:{position:camera.position.asArray(),target:camera.getTarget().asArray(),up:camera.upVector.asArray(),fov:camera.fov,near:camera.minZ,far:camera.maxZ},
    actual_environment_intensity:scene.environmentIntensity,actual_exposure:image.exposure,actual_tone_mapping:'ACES',projection_witnesses:witnesses,
    renderer:engine.getGlInfo(),scope:spec.scope,processing_difference:spec.processing_difference,art_accepted:false,physical_iphone_tested:false};
}
window.__MATERIAL_CAMERA_REVIEW__={scene,engine,camera,report};engine.runRenderLoop(()=>scene.render());
