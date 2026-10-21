// Additive inspector variant. The frozen camera/material implementation stays unchanged.
import '../motorcycle-material-camera-lab-v1/review.js';
const value=new URLSearchParams(location.search).get('rotation_y');
if(value===null||!Number.isFinite(Number(value)))throw Error('Explicit HDR sampling rotation required');
const lab=window.__MATERIAL_CAMERA_REVIEW__,rotation=Number(value);
lab.scene.environmentTexture.rotationY=rotation;
const originalReport=lab.report;
lab.report=()=>({...originalReport(),actual_environment_rotation_y_radians:lab.scene.environmentTexture.rotationY,
  orientation_scope:'Explicit HDR sampling rotation applied in Babylon. Convention-derived directional alignment is separately documented; no GPU irradiance calibration, display/prefilter/BRDF equality or art reception.',
  processing_difference:'Native AgX Medium High Contrast versus Babylon ACES. HDR sampling rotation is explicit; HDR prefilter, BRDF, geometric occlusion and display responses are not calibrated equal.'});
lab.orientation_variant_ready=true;
