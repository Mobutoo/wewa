// Additive v5: import the frozen v4 scene, change exactly one shadow property.
import '../motorcycle-material-camera-lab-v4/review.js';
const lab=window.__MATERIAL_CAMERA_REVIEW__;
const response=await fetch(new URL('./configuration.json',import.meta.url));
if(!response.ok)throw Error('Missing fixed v5 configuration');
const config=await response.json(),before=lab.report();
if(before.experiment!=='sun-shadow-v4'||lab.scene.lights.length!==1)throw Error('Expected the unmodified v4 scene');
const sun=lab.scene.lights[0],shadow=sun.getShadowGenerator();
if(!shadow||shadow.normalBias!==config.normal_bias_m)throw Error('Unexpected v4 shadow generator');
const actualSize=shadow.getShadowMap().getSize();
if(actualSize.width!==2048||actualSize.height!==2048)throw Error('Shadow map resolution changed');
// Derive from actual runtime orthographic extents, not rounded values in the diagnosis.
const spanX=sun.orthoRight-sun.orthoLeft,spanY=sun.orthoTop-sun.orthoBottom;
const requestedM=Math.max(spanX,spanY)/actualSize.width;
if(!Number.isFinite(requestedM)||requestedM<=0)throw Error('Invalid runtime frustum');
const projection=sun.getProjectionMatrix(sun.getViewMatrix(),shadow.getShadowMap().renderList);
const factor=lab.engine.isNDCHalfZRange?.5:1;
const previousAPI=shadow.bias;
shadow.bias=requestedM*Math.abs(projection.m[10])/factor; // the sole scene-setting mutation
const originalReport=lab.report;
lab.report=()=>{const report=originalReport();return {...report,experiment:'sun-shadow-v5',
  fixed_configuration:{...report.fixed_configuration,requested_depth_bias_m:requestedM,
    requested_depth_bias_rule:config.requested_depth_bias_rule},
  shadow:{...report.shadow,requested_depth_bias_m:requestedM},
  bias_revision:{configuration:config,only_scene_property_changed:'ShadowGenerator.bias',
    inherited_scene:'Frozen sun-shadow-v4; same light identity, caster/receiver logic and conservation helper.',
    previous_API_bias:previousAPI,actual_API_bias:shadow.bias,
    runtime_span_xy_m:[spanX,spanY],runtime_map_px:actualSize.width,
    requested_depth_bias_m:requestedM,selection_rule:config.requested_depth_bias_rule,
    projection10:projection.m[10],shader_BIASFACTOR:factor,
    status:'Single predeclared hypothesis test; no automatic retuning or art acceptance.'},
  art_accepted:false,physical_iphone_tested:false};};
lab.sun_shadow_v5_ready=true;
