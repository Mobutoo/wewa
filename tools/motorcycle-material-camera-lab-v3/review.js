// Experimental screen-space visibility only; not a replacement for calibrated lighting.
import '../motorcycle-material-camera-lab-v2/review.js';
import {SSAO2RenderingPipeline} from '@babylonjs/core';
const lab=window.__MATERIAL_CAMERA_REVIEW__,name='Read-only screen-space visibility diagnostic';
if(!SSAO2RenderingPipeline.IsSupported)throw Error('SSAO2 unsupported in this runtime');
let seed=331601;const originalRandom=Math.random;let pipeline;
try{
  Math.random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  pipeline=new SSAO2RenderingPipeline(name,lab.scene,{ssaoRatio:1,blurRatio:1},[lab.camera]);
  pipeline.samples=16;pipeline.radius=.015;pipeline.epsilon=.0002;pipeline.totalStrength=1;pipeline.base=0;
  pipeline.maxZ=2;pipeline.textureSamples=1;pipeline.bilateralSamples=16;
}finally{Math.random=originalRandom;}
let enabled=true;
lab.setOcclusion=(value)=>{
  if(Boolean(value)===enabled)return;
  if(value)lab.scene.postProcessRenderPipelineManager.attachCamerasToRenderPipeline(name,[lab.camera]);
  else lab.scene.postProcessRenderPipelineManager.detachCamerasFromRenderPipeline(name,[lab.camera]);
  enabled=Boolean(value);
};
const originalReport=lab.report;
lab.report=()=>({...originalReport(),occlusion_diagnostic:{enabled,pipeline_ready:pipeline.isReady(),supported:SSAO2RenderingPipeline.IsSupported,
  samples:pipeline.samples,radius_m:pipeline.radius,epsilon_depth_m:pipeline.epsilon,totalStrength:pipeline.totalStrength,
  base:pipeline.base,maxZ_m:pipeline.maxZ,textureSamples:pipeline.textureSamples,bilateralSamples:pipeline.bilateralSamples,
  ssaoRatio:1,blurRatio:1,random_seed:331601,
  scope:'Screen-space final-image occlusion approximation from actual depth and normals. Parameters are diagnostic choices, not measured material or a radiometric match. Hidden/off-screen visibility, physical indirect lighting and iPhone cost are not qualified.'}});
lab.occlusion_variant_ready=true;
