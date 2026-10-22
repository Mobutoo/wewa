import fs from 'node:fs/promises';import crypto from 'node:crypto';import {NodeIO}from'@gltf-transform/core';import{ALL_EXTENSIONS}from'@gltf-transform/extensions';import validator from'gltf-validator';
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS),rows=[],sha=b=>crypto.createHash('sha256').update(b).digest('hex');
for(const side of ['left','right']){
 const before=`assets-src/moto-components/rear-indicator-${side}-stalk-v1/rear-indicator-${side}-stalk-v1.glb`,after=`assets-src/moto-components/rear-indicator-dark-polymer-v2/${side}-stalk.glb`,a=(await io.read(before)).getRoot(),b=(await io.read(after)).getRoot();const ap=a.listMeshes().flatMap(m=>m.listPrimitives()),bp=b.listMeshes().flatMap(m=>m.listPrimitives());if(ap.length!==bp.length)throw Error('Primitive count');const attributes=[];
 for(let i=0;i<ap.length;i++){
  for(const s of ['POSITION','NORMAL','TEXCOORD_0','TANGENT']){
   const u=ap[i].getAttribute(s),v=bp[i].getAttribute(s);if(!u&&!v)continue;if(!u||!v||u.getArray().length!==v.getArray().length)throw Error('Attribute presence/count '+s);const ub=Buffer.from(u.getArray().buffer,u.getArray().byteOffset,u.getArray().byteLength),vb=Buffer.from(v.getArray().buffer,v.getArray().byteOffset,v.getArray().byteLength);if(!ub.equals(vb))throw Error('Geometry attribute changed '+s);attributes.push({semantic:s,sha256:sha(ub),unchanged:true});
  }
  const u=ap[i].getIndices()?.getArray(),v=bp[i].getIndices()?.getArray();if(JSON.stringify([...u])!==JSON.stringify([...v]))throw Error('Triangle indices changed');
 }
 const bytes=await fs.readFile(after),val=await validator.validateBytes(bytes,{maxIssues:50});if(val.issues.numErrors)throw Error('glTF errors');rows.push({side,before,after,geometry_attributes:attributes,triangles_unchanged:true,glTF_errors:val.issues.numErrors,materials:b.listMaterials().map(m=>({name:m.getName(),basecolor:m.getBaseColorFactor(),roughness:m.getRoughnessFactor(),metallic:m.getMetallicFactor()}))});
}
await fs.writeFile('creative/reviews/rear-indicator-dark-polymer-v2/export-check.json',JSON.stringify({rows,scope:'Exact geometry/normals/UV/tangents/index invariance; only uncalibrated material changes; no fit or artistic reception'},null,2)+'\n');console.log('MATERIAL_ONLY_GEOMETRY_EXACT',rows.length);
