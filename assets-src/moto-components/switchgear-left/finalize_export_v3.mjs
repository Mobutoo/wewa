/** Fill only undefined exported MikkTSpace tangent vectors from real geometry/UV.
 * Source geometry, UV, normals, indices, materials and images are not altered.
 */
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
const dir='assets-src/moto-components/switchgear-left',file=dir+'/switchgear-left-v3-inspection.glb',io=new NodeIO(),beforeBytes=await fs.readFile(file),doc=await io.read(file);
const hash=a=>createHash('sha256').update(Buffer.from(a.buffer,a.byteOffset,a.byteLength)).digest('hex');
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0),unit=a=>{const l=Math.hypot(...a);return a.map(x=>x/l)},sub=(a,b)=>a.map((x,i)=>x-b[i]);
const materialState=root=>root.listMaterials().map(m=>({name:m.getName(),base:m.getBaseColorFactor(),metallic:m.getMetallicFactor(),roughness:m.getRoughnessFactor(),emissive:m.getEmissiveFactor(),normalScale:m.getNormalScale(),occlusionStrength:m.getOcclusionStrength(),alphaMode:m.getAlphaMode(),alphaCutoff:m.getAlphaCutoff(),doubleSided:m.getDoubleSided(),textures:['BaseColor','MetallicRoughness','Normal','Occlusion','Emissive'].map(k=>{const t=m['get'+k+'Texture']();return t?{slot:k,name:t.getName(),mime:t.getMimeType(),imageSHA256:createHash('sha256').update(t.getImage()).digest('hex'),texCoord:m['get'+k+'TextureInfo']().getTexCoord()}:null})}));
const materialBefore=materialState(doc.getRoot()),materialHash=createHash('sha256').update(JSON.stringify(materialBefore)).digest('hex');
const proofs=[],removedUnused=[];
const inputDigest=createHash('sha256').update(beforeBytes).digest('hex');let priorStage=null;
try{const previous=JSON.parse(await fs.readFile('creative/reviews/switchgear-left-v3/export-tangent-finalization.json','utf8'));if(previous.output_sha256===inputDigest){const stage='creative/reviews/switchgear-left-v3/export-tangent-stage-'+inputDigest.slice(0,12)+'.json';await fs.writeFile(stage,JSON.stringify(previous,null,2)+'\n');priorStage={path:stage,sha256:createHash('sha256').update(await fs.readFile(stage)).digest('hex'),input_sha256:previous.input_sha256,output_sha256:previous.output_sha256};}}catch(e){if(e.code!=='ENOENT')throw e;}

for(const mesh of doc.getRoot().listMeshes())for(const p of mesh.listPrimitives()) {
 const protectedData={};for(const semantic of p.listSemantics().filter(x=>x!=='TANGENT'))protectedData[semantic]=hash(p.getAttribute(semantic).getArray());protectedData.indices=hash(p.getIndices().getArray());
 const tang=p.getAttribute('TANGENT');if(!tang)continue;
 if(!p.getMaterial()?.getNormalTexture()){removedUnused.push({mesh:mesh.getName(),reason:'No normal texture: TANGENT is not consumed by this material',count:tang.getCount(),removed_attribute_sha256:hash(tang.getArray()),protected_buffer_sha256:protectedData});p.setAttribute('TANGENT',null);continue;}

 const pos=p.getAttribute('POSITION'),norm=p.getAttribute('NORMAL'),uv=p.getAttribute('TEXCOORD_0'),idx=p.getIndices(),values=new Float32Array(tang.getArray()),tacc=Array.from({length:pos.getCount()},()=>[0,0,0]),bacc=Array.from({length:pos.getCount()},()=>[0,0,0]),incidents=Array.from({length:pos.getCount()},()=>[]);
 const get=(a,i)=>{const v=[];a.getElement(i,v);return v};
 if(uv)for(let k=0;k<idx.getCount();k+=3){
  const ids=[idx.getScalar(k),idx.getScalar(k+1),idx.getScalar(k+2)],pp=ids.map(i=>get(pos,i)),vv=ids.map(i=>get(uv,i)),e1=sub(pp[1],pp[0]),e2=sub(pp[2],pp[0]),a=sub(vv[1],vv[0]),b=sub(vv[2],vv[0]),det=a[0]*b[1]-a[1]*b[0];
  const area=Math.hypot(...cross(e1,e2))/2;
  if(p.getMaterial()?.getNormalTexture()&&area<1e-20)throw Error('Geometrically zero normal-mapped triangle '+mesh.getName()+' triangle'+(k/3));
  for(const i of ids)incidents[i].push({triangle:k/3,indices:ids,geometric_area_m2:area,UV_determinant:det,tangent:null,bitangent:null});
  if(Math.abs(det)<1e-20)continue;
  const t=e1.map((x,j)=>(x*b[1]-e2[j]*a[1])/det),bit=e1.map((x,j)=>(e2[j]*a[0]-x*b[0])/det);
  for(const i of ids){incidents[i].at(-1).tangent=t;incidents[i].at(-1).bitangent=bit;for(let j=0;j<3;j++){tacc[i][j]+=t[j];bacc[i][j]+=bit[j];}}
 }
 const changed=[];
 for(let i=0;i<tang.getCount();i++) {
  const old=[values[i*4],values[i*4+1],values[i*4+2]],length=Math.hypot(...old);if(length>.999&&length<1.001)continue;
  const n=unit(get(norm,i)),projection=dot(n,tacc[i]);let t=tacc[i].map((x,j)=>x-n[j]*projection),method='actual incident position/UV gradients';
  if(Math.hypot(...t)<1e-20){
   const choices=incidents[i].filter(x=>x.tangent).sort((a,b)=>b.geometric_area_m2-a.geometric_area_m2);let chosen=null;
   for(const c of choices){const d=dot(n,c.tangent),candidate=c.tangent.map((x,j)=>x-n[j]*d);if(Math.hypot(...candidate)>1e-20){t=candidate;bacc[i]=c.bitangent;chosen=c;break;}}
   if(!chosen)throw Error('No UV-derived tangent can be defined, refusing arbitrary repair at '+mesh.getName()+' vertex'+i);
   method='largest-area valid incident UV derivative after cancelling/normal-parallel aggregate';
  }
  t=unit(t);const w=dot(cross(n,t),bacc[i])<0?-1:1;values.set([...t,w],i*4);changed.push({vertex:i,before_length:length,method,classification:'MikkTSpace zero/nonunit vector; incident geometric areas nonzero',normal_dot_tangent:dot(n,t),sign_w:w,incident_triangles:incidents[i]});
 }
 tang.setArray(values);
 for(const semantic of p.listSemantics().filter(x=>x!=='TANGENT'))if(hash(p.getAttribute(semantic).getArray())!==protectedData[semantic])throw Error('Protected buffer changed');
 if(hash(p.getIndices().getArray())!==protectedData.indices)throw Error('Indices changed');
 proofs.push({mesh:mesh.getName(),changed_count:changed.length,changes:changed,protected_buffer_sha256:protectedData});
}
await io.write(file,doc);
const after=await io.read(file);let primitiveIndex=0;
for(const mesh of after.getRoot().listMeshes())for(const p of mesh.listPrimitives()){const original=doc.getRoot().listMeshes().flatMap(m=>m.listPrimitives())[primitiveIndex++];for(const semantic of p.listSemantics().filter(x=>x!=='TANGENT'))if(hash(p.getAttribute(semantic).getArray())!==hash(original.getAttribute(semantic).getArray()))throw Error('Round-trip buffer changed');if(hash(p.getIndices().getArray())!==hash(original.getIndices().getArray()))throw Error('Round-trip indices changed');}
if(JSON.stringify(materialBefore)!==JSON.stringify(materialState(after.getRoot())))throw Error('Material state/image bytes changed');
const report={schema:1,prior_stage:priorStage,removed_unused_tangent_attributes:removedUnused,materials_and_images_bit_identical:true,material_state_sha256:materialHash,material_state:materialBefore,pipeline:'Original Blender4.3.2 evaluated GLB, finalise only nonunit/zero tangent vectors; actual incident positions/UVs define each tangent then Gram-Schmidt against actual normal. No arbitrary tangent fallback is allowed. Every affected triangle has a nonzero geometric area and a documented actual UV derivative. This is not a claim of exact MikkTSpace visual parity. Nothing is removed from geometry.',input_sha256:createHash('sha256').update(beforeBytes).digest('hex'),output_sha256:createHash('sha256').update(await fs.readFile(file)).digest('hex'),protected_geometry_and_UV_unchanged:true,changes:proofs,total_changed_tangents:proofs.reduce((n,p)=>n+p.changed_count,0),art_accepted:false};
await fs.writeFile('creative/reviews/switchgear-left-v3/export-tangent-finalization.json',JSON.stringify(report,null,2)+'\n');
console.log('Tangent finalization',report.total_changed_tangents,'actual geometry buffers unchanged');
