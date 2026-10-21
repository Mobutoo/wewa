// Additive experiment only: frozen v2 (and transitively v1) is imported verbatim.
import '../motorcycle-material-camera-lab-v2/review.js';
import {Engine,DirectionalLight,ShadowGenerator,Vector3,Color3,VertexBuffer} from '@babylonjs/core';
import {actualMeshes,snapshot} from './conservation.js';
const lab=window.__MATERIAL_CAMERA_REVIEW__,{scene,engine}=lab;
const response=await fetch(new URL('./configuration.json',import.meta.url));if(!response.ok)throw Error('Missing fixed configuration');
const config=await response.json();
if(Engine.Version!==config.babylon_version)throw Error('This experiment requires Babylon '+config.babylon_version);
const base=lab.report(),specPath=new URLSearchParams(location.search).get('spec');
if(!Object.values(config.camera_specs).some(s=>'/'+s.path===specPath))throw Error('Only the two pinned common cameras are allowed');
const pinned=path=>config.protected_inputs.find(p=>p.path===path)?.sha256;
for(const key of ['source','export','HDR'])if(base.spec[key+'_sha256']!==pinned(base.spec[key]))throw Error('Unpinned '+key);
if(base.actual_environment_rotation_y_radians!==config.rotation_y_radians)throw Error('HDR rotation is fixed');
if(scene.lights.length)throw Error('Unexpected existing light');
if(scene.postProcesses.length||scene.postProcessRenderPipelineManager.supportedPipelines.length)throw Error('No AO or post-effect pipeline allowed');
const meshes=actualMeshes(scene);
if(meshes.length!==config.expected_runtime_meshes||base.drawn_triangles!==config.expected_triangles)throw Error('Unexpected mesh inventory');
const receiveOwners=[...new Set(meshes.map(m=>m.sourceMesh??m))];
const originalReceive=new Map(receiveOwners.map(m=>[m,m.receiveShadows]));
const sourceDirection=Vector3.FromArray(config.direction_gltf),direction=sourceDirection.normalizeToNew();
// All extents below come from actual imported vertices transformed by actual world matrices.
function extrema(points){const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
  for(const p of points)for(let k=0;k<3;k++){min[k]=Math.min(min[k],p[k]);max[k]=Math.max(max[k],p[k]);}
  if(!min.every(Number.isFinite)||!max.every(Number.isFinite))throw Error('Non-finite actual bounds');return {min,max};}
const worldPoints=[];
for(const m of meshes){const positions=m.getVerticesData(VertexBuffer.PositionKind),world=m.computeWorldMatrix(true);
  for(let i=0;i<positions.length;i+=3)worldPoints.push(Vector3.TransformCoordinates(Vector3.FromArray(positions,i),world).asArray());}
const worldBounds=extrema(worldPoints),center=Vector3.FromArray(worldBounds.min).add(Vector3.FromArray(worldBounds.max)).scale(.5);
const diagonal=Vector3.Distance(Vector3.FromArray(worldBounds.min),Vector3.FromArray(worldBounds.max));
const sun=new DirectionalLight('W4 fixed experimental direct sun',sourceDirection.clone(),scene);
sun.position=center.subtract(direction.scale(diagonal+.01)); // deterministic shadow-view origin; no physical falloff claim
sun.diffuse=Color3.FromArray(config.color_linear_rgb);sun.specular=Color3.FromArray(config.color_linear_rgb);
sun.intensity=config.intensity_babylon_experimental;sun.setEnabled(false);sun.shadowEnabled=false;
const view=sun.getViewMatrix(),lightBounds=extrema(worldPoints.map(p=>Vector3.TransformCoordinates(Vector3.FromArray(p),view).asArray()));
const padding=lightBounds.min.map((v,k)=>Math.max(2*(lightBounds.max[k]-v)/config.shadow_map_px,4*config.normal_bias_m));
sun.shadowFrustumSize=0;sun.shadowOrthoScale=0;sun.autoUpdateExtends=false;sun.autoCalcShadowZBounds=false;
sun.orthoLeft=lightBounds.min[0]-padding[0];sun.orthoRight=lightBounds.max[0]+padding[0];
sun.orthoBottom=lightBounds.min[1]-padding[1];sun.orthoTop=lightBounds.max[1]+padding[1];
sun.shadowMinZ=lightBounds.min[2]-padding[2];sun.shadowMaxZ=lightBounds.max[2]+padding[2];
const projection=sun.getProjectionMatrix(view,meshes),biasFactor=engine.isNDCHalfZRange?.5:1;
const shadow=new ShadowGenerator(config.shadow_map_px,sun);
shadow.usePercentageCloserFiltering=true;shadow.filteringQuality=ShadowGenerator.QUALITY_MEDIUM;
if(!shadow.usePercentageCloserFiltering||shadow.filter!==ShadowGenerator.FILTER_PCF)throw Error('PCF unsupported; no fallback permitted');
// API bias offsets projected depth; it is NOT a world-space metre value.
shadow.bias=config.requested_depth_bias_m*Math.abs(projection.m[10])/biasFactor;
shadow.normalBias=config.normal_bias_m;
for(const m of meshes)shadow.addShadowCaster(m,false);
const identity=m=>({name:m.name,id:m.id,class:m.getClassName(),geometry_source:m.sourceMesh?.name??m.name,vertices:m.getTotalVertices(),triangles:m.getTotalIndices()/3,
  material:m.material?.id??null,world_matrix:Array.from(m.computeWorldMatrix(true).m)});
let state='neutral';
function setState(next){
  if(!['neutral','W0','W1'].includes(next))throw Error('Only neutral/W0/W1 are defined');
  state=next;sun.setEnabled(next!=='neutral');sun.shadowEnabled=next==='W1';
  for(const m of receiveOwners)m.receiveShadows=next==='neutral'?originalReceive.get(m):true;
}
async function prepareState(next){
  setState(next);engine.resize();scene.render();await scene.whenReadyAsync();
  if(next==='W1'){await shadow.forceCompilationAsync({useInstances:false});
    if(meshes.some(m=>m.sourceMesh))await shadow.forceCompilationAsync({useInstances:true});}
  for(let i=0;i<config.settle_frames;i++){await new Promise(requestAnimationFrame);scene.render();}
}
const originalReport=lab.report;
lab.report=()=>({...originalReport(),experiment:'sun-shadow-v4',state,babylon_version:Engine.Version,
  fixed_configuration:config,world_vertex_bounds_m:worldBounds,actual_vertex_count:worldPoints.length,
  lights:scene.lights.map(l=>({name:l.name,type:l.getClassName(),enabled:l.isEnabled(),shadow_enabled:l.shadowEnabled,
    direction:l.direction?.asArray(),position:l.position?.asArray(),diffuse_linear_rgb:l.diffuse.asArray(),
    specular_linear_rgb:l.specular.asArray(),intensity:l.intensity,intensity_mode:l.intensityMode,radius:l.radius})),
  sunlight_scope:'Babylon intensity 1.5 is experimental; not a photometric equivalence to Blender SUN energy 1.5. Color supplied as linear RGB.',
  shadow:{map_size:shadow.getShadowMap().getSize(),filter:shadow.filter,use_PCF:shadow.usePercentageCloserFiltering,
    filtering_quality:shadow.filteringQuality,quality_name:'MEDIUM',requested_depth_bias_m:config.requested_depth_bias_m,
    actual_API_bias_projected_depth:shadow.bias,normal_bias_world_m:shadow.normalBias,
    bias_conversion:'API_bias = requested_m * abs(lightProjection[10]) / shader_BIASFACTOR',
    shader_BIASFACTOR:biasFactor,NDC_half_z:engine.isNDCHalfZRange,reverse_depth:engine.useReverseDepthBuffer,
    light_view_matrix:Array.from(view.m),light_projection_matrix:Array.from(projection.m),
    generator_view_projection_matrix:Array.from(shadow.getTransformMatrix().m),
    generator_view_matrix:Array.from(shadow.viewMatrix.m),generator_projection_matrix:Array.from(shadow.projectionMatrix.m),
    actual_lightspace_vertex_bounds_m:lightBounds,padding_m:padding,padding_formula:config.frustum_padding_formula,
    frustum:{left:sun.orthoLeft,right:sun.orthoRight,bottom:sun.orthoBottom,top:sun.orthoTop,near:sun.shadowMinZ,far:sun.shadowMaxZ},
    casters:shadow.getShadowMap().renderList.map(identity),receivers:meshes.filter(m=>m.receiveShadows).map(identity)},
  pipelines:scene.postProcessRenderPipelineManager.supportedPipelines.map(p=>p.name),
  scene_shadows_enabled:scene.shadowsEnabled,art_accepted:false,physical_iphone_tested:false,
  limits:'Only direct sun is shadowed; no new AO, fill, floor or material change. PCF does not reproduce Blender 2-degree penumbra. AgX/ACES and BRDF/prefilter differences remain.'});
lab.prepareState=prepareState;lab.snapshot=()=>snapshot(lab);lab.sun_shadow_variant_ready=true;
setState('neutral');
