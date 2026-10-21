import fs from 'node:fs/promises';import{createHash}from'node:crypto';import{NodeIO}from'@gltf-transform/core';import{getBounds}from'@gltf-transform/functions';import validator from'gltf-validator';
const folder='engine-output-cover-left',here='assets-src/moto-components/'+folder,proof='creative/reviews/'+folder+'-v1',path=here+'/'+folder+'-inspection.glb';
const sha=b=>createHash('sha256').update(b).digest('hex');
// Blender4.3 glTF export rounds both unit source directions to4decimal, then
// renormalizes only NORMAL. For delta=sqrt(3)*0.5*10^-4, the resulting
// |N dot T| <=(2delta+delta²)/(1-delta), plus Float32 storage error.
// This checks the unmodified buffers against their documented precision.
const exportRoundDigits=4,vectorRoundBound=Math.sqrt(3)*.5*10**(-exportRoundDigits),orthogonalityBound=(2*vectorRoundBound+vectorRoundBound**2)/(1-vectorRoundBound)+1e-6;
function geometry(root){
 const keys=[];for(const m of root.listMeshes())for(const p of m.listPrimitives()){const x=p.getAttribute('POSITION'),ix=p.getIndices();for(let i=0;i<ix.getCount();i+=3){const v=[];for(let k=0;k<3;k++){const a=[];x.getElement(ix.getScalar(i+k),a);v.push(a.map(x=>Object.is(x,-0)?0:x).join(','));}keys.push([v.join('/'),[v[1],v[2],v[0]].join('/'),[v[2],v[0],v[1]].join('/')].sort()[0]);}}
 return {triangles:keys.length,canonical_triangle_sha256:sha(keys.sort().join('\n'))};
}
// --baseline is an explicit one-off archival operation, never an automatic overwrite.
if(process.argv[2]==='--baseline'){
 const file=here+'/gray-geometry-baseline.json';try{await fs.stat(file);throw Error('Refusing to replace an existing baseline');}catch(e){if(e.code!=='ENOENT')throw e;}
 const old='/workspace/wewa-assets/work-in-progress/'+folder+'/gray-shape-ba6421ea/'+folder+'-inspection.glb',b=await fs.readFile(old),r=(await new NodeIO().read(old)).getRoot();
 await fs.writeFile(file,JSON.stringify({source_sha256:'ba6421ea04f4b5d378a5ecaa35bd4fddf70cf6d4cf9f94e084f174dc4f0ab4cc',gray_export_sha256:sha(b),...geometry(r),encoding:'Sorted Float32 local triangle coordinate strings, cyclic rotations canonicalized; winding preserved. Materials/UV/tangents excluded.',scope:'Gray geometry baseline before original coating grain, not artistic reception'},null,2)+'\n');process.exit(0);
}
const bytes=await fs.readFile(path),root=(await new NodeIO().read(path)).getRoot(),v=await validator.validateBytes(new Uint8Array(bytes),{uri:path}),meshes=[];const normalMapped=root.listMaterials().some(m=>m.getNormalTexture());
for(const mesh of root.listMeshes()){
 let vertices=0,triangles=0,zeroAreaTriangles=0,nonFinitePositions=0,nonUnitNormals=0,zeroAreaUVTriangles=0,nonFiniteUVs=0,nonFiniteTangents=0,nonUnitTangents=0,nonOrthogonalTangents=0,invalidHandedness=0,maxAbsDotNormalTangent=0,volume=0;
 for(const p of mesh.listPrimitives()){
  const pos=p.getAttribute('POSITION'),norm=p.getAttribute('NORMAL'),ix=p.getIndices(),uv=p.getAttribute('TEXCOORD_0'),tan=p.getAttribute('TANGENT');vertices+=pos.getCount();triangles+=ix.getCount()/3;if(normalMapped&&(!tan||!uv))throw Error('Normal map requires actual UV/tangent buffers');
  for(let i=0;i<pos.getCount();i++){
   const a=[],n=[];pos.getElement(i,a);norm.getElement(i,n);if(a.some(x=>!Number.isFinite(x)))nonFinitePositions++;if(Math.abs(Math.hypot(...n)-1)>1e-4)nonUnitNormals++;
   if(tan){const t=[];tan.getElement(i,t);if(t.some(x=>!Number.isFinite(x)))nonFiniteTangents++;if(Math.abs(Math.hypot(...t.slice(0,3))-1)>1e-4)nonUnitTangents++;const dot=Math.abs(n[0]*t[0]+n[1]*t[1]+n[2]*t[2]);maxAbsDotNormalTangent=Math.max(maxAbsDotNormalTangent,dot);if(dot>orthogonalityBound)nonOrthogonalTangents++;if(Math.abs(Math.abs(t[3])-1)>1e-6)invalidHandedness++;}
  }
  for(let i=0;i<ix.getCount();i+=3){
   if(uv){const a=[],b=[],c=[];uv.getElement(ix.getScalar(i),a);uv.getElement(ix.getScalar(i+1),b);uv.getElement(ix.getScalar(i+2),c);if([...a,...b,...c].some(x=>!Number.isFinite(x)))nonFiniteUVs++;if((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])===0)zeroAreaUVTriangles++;}
   const a=[],b=[],c=[];pos.getElement(ix.getScalar(i),a);pos.getElement(ix.getScalar(i+1),b);pos.getElement(ix.getScalar(i+2),c);const u=b.map((x,k)=>x-a[k]),w=c.map((x,k)=>x-a[k]);if(Math.hypot(u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0])===0)zeroAreaTriangles++;volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;
  }
 }
 const row={name:mesh.getName(),vertices,triangles,zeroAreaTriangles,nonFinitePositions,nonUnitNormals,zeroAreaUVTriangles,nonFiniteUVs,nonFiniteTangents,nonUnitTangents,nonOrthogonalTangents,invalidHandedness,maxAbsDotNormalTangent,signed_volume_m3:volume};if(Object.entries(row).some(([k,n])=>/^(zeroArea|nonFinite|nonUnit|nonOrthogonal|invalid)/.test(k)&&n!==0)||volume<=0)throw Error(JSON.stringify(row));meshes.push(row);
}
const source=JSON.parse(await fs.readFile(proof+'/source-geometry-check.json','utf8'));if(Math.abs(meshes[0].signed_volume_m3/source.geometry[0].signed_volume_m3-1)>1e-5)throw Error('Export volume changed');
const currentGeometry=geometry(root),baseline=JSON.parse(await fs.readFile(here+'/gray-geometry-baseline.json','utf8'));if(currentGeometry.canonical_triangle_sha256!==baseline.canonical_triangle_sha256||currentGeometry.triangles!==baseline.triangles)throw Error('Geometry changed from gray baseline');
const textureChecks=[];for(const mat of root.listMaterials())for(const [label,tex,file]of [['normal',mat.getNormalTexture(),'silver-coating-normal.png'],['metallic-roughness',mat.getMetallicRoughnessTexture(),'silver-coating-metallic-roughness.png']]){
 if(source.original_grain_maps_created){if(!tex)throw Error('Missing exported '+label);const expected=sha(await fs.readFile(here+'/textures/'+file)),actual=sha(tex.getImage());if(expected!==actual)throw Error('Export image differs from authored PNG '+label);textureChecks.push({channel:label,source_png:file,source_sha256:expected,export_sha256:actual,byte_identical:true,mime:tex.getMimeType()});}
}
const report={path,sha256:sha(bytes),glTF_errors:v.issues.numErrors,glTF_warnings:v.issues.numWarnings,messages:v.issues.messages,meshes,bounds:getBounds(root.getDefaultScene()),materials:root.listMaterials().map(m=>({name:m.getName(),basecolor:m.getBaseColorFactor(),metallic_factor:m.getMetallicFactor(),roughness_factor:m.getRoughnessFactor(),normal_map:!!m.getNormalTexture(),normal_scale:m.getNormalScale(),normal_texcoord:m.getNormalTextureInfo()?.getTexCoord()})),textureChecks,geometry_unchanged_from_gray:true,actual_geometry_signature:currentGeometry,source_sha256:source.source_sha256,tangents_repaired:false,tangent_precision_policy:{exporter:'Official Blender4.3.2 bundled io_scene_gltf2',rounding_digits:exportRoundDigits,source_file:'io/com/constants.py:159 and blender/exp/primitive_extract.py:1425,1492',rounded_vector_error_bound:vectorRoundBound,abs_dot_bound_with_float32_margin:orthogonalityBound,source_max_abs_dot_normal:source.source_tangents?.max_abs_dot_normal,reason:'Bound from two independent direction roundings and NORMAL renormalization; buffers unchanged'},all_dimensions_estimated:true,art_accepted:false};
if(report.glTF_errors||meshes.length!==1)throw Error(JSON.stringify(report));await fs.writeFile(proof+'/export-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
