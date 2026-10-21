import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
const H='assets-src/moto-components/engine-intake-manifold/', O='creative/reviews/engine-intake-manifold-v1/';
const path=H+'engine-intake-manifold-inspection.glb', bytes=await fs.readFile(path);
const root=(await new NodeIO().readBinary(bytes)).getRoot(),hash=x=>createHash('sha256').update(x).digest('hex');
const material=root.listMaterials().find(x=>x.getName().startsWith('Original representative cast alloy'));
if(!material?.getNormalTexture()||!material.getMetallicRoughnessTexture())throw Error('Missing baked native PBR maps');
const results=[];
for(const mesh of root.listMeshes())for(const p of mesh.listPrimitives()){
 const m=p.getMaterial(),hasNormal=!!m.getNormalTexture(),uv=p.getAttribute('TEXCOORD_0'),t=p.getAttribute('TANGENT'),n=p.getAttribute('NORMAL'),ix=p.getIndices();
 let collapsed=0,badTangents=0,over1e4=0,minUVArea=Infinity,maxOrthogonality=0,maxLengthError=0;
 if(hasNormal){
  if(!uv||!t)throw Error('Normalmapped primitive without UV/tangents');
  for(let i=0;i<t.getCount();i++){
   const a=[],b=[];t.getElement(i,a);n.getElement(i,b);
   const dot=Math.abs(a.slice(0,3).reduce((s,x,k)=>s+x*b[k],0)),lengthError=Math.abs(Math.hypot(...a.slice(0,3))-1);
   maxOrthogonality=Math.max(dot,maxOrthogonality);maxLengthError=Math.max(lengthError,maxLengthError);
   if(lengthError>1e-4||dot>1e-4)over1e4++;
   if(a.some(x=>!Number.isFinite(x))||lengthError>.001||dot>.001||Math.abs(a[3])!==1)badTangents++;
  }
  for(let i=0;i<ix.getCount();i+=3){const a=[],b=[],c=[];uv.getElement(ix.getScalar(i),a);uv.getElement(ix.getScalar(i+1),b);uv.getElement(ix.getScalar(i+2),c);const area=Math.abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2;minUVArea=Math.min(area,minUVArea);if(area===0)collapsed++;}
  if(collapsed||badTangents)throw Error(JSON.stringify({mesh:mesh.getName(),collapsed,badTangents,maxOrthogonality,maxLengthError}));
 }
 results.push({mesh:mesh.getName(),normalmapped:hasNormal,triangles:ix.getCount()/3,UV_set:uv?'TEXCOORD_0':null,normalmapped_zero_area_UV_triangles:collapsed,native_invalid_tangents:badTangents,minUVArea:hasNormal?minUVArea:null,maxOrthogonality,maxLengthError,diagnostic_frames_over_1e_minus4:over1e4,shared_frame_tolerance:.001});
}
// Save copies of actual embedded image payloads for independent pixel decoding.
const extracted='/workspace/wewa-assets/work-in-progress/engine-intake-manifold/exported-v1-textures';await fs.mkdir(extracted,{recursive:true});
const body=root.listMeshes().find(m=>m.getName().startsWith('Cast intake manifold'));const pp=body.listPrimitives()[0],UV=pp.getAttribute('TEXCOORD_0'),indices=pp.getIndices(),samples=[];for(let i=0;i<UV.getCount();i++)samples.push(UV.getElement(i,[]));for(let i=0;i<indices.getCount();i+=3){const q=[0,0];for(let j=0;j<3;j++){const a=UV.getElement(indices.getScalar(i+j),[]);q[0]+=a[0]/3;q[1]+=a[1]/3;}samples.push(q);}await fs.writeFile(extracted+'/actual_UV_vertices_and_triangle_centres.json',JSON.stringify(samples));
const textures=[];
for(const [role,texture]of [['normal',material.getNormalTexture()],['metallic_roughness',material.getMetallicRoughnessTexture()]]){
 const data=texture.getImage(),file=extracted+'/'+role+'.png';await fs.writeFile(file,data);
 textures.push({role,name:texture.getName(),mime:texture.getMimeType(),bytes:data.length,sha256:hash(data),extracted_actual_embedded_bytes:file});
}
const report={export_sha256:hash(bytes),source_sha256:JSON.parse(await fs.readFile(H+'build-report.json','utf8')).source_sha256,
 native_exported_material:{name:material.getName(),baseColor:material.getBaseColorFactor(),metallic:material.getMetallicFactor(),roughness:material.getRoughnessFactor(),normalScale:material.getNormalScale(),normalUV:material.getNormalTextureInfo().getTexCoord(),roughnessUV:material.getMetallicRoughnessTextureInfo().getTexCoord()},
 primitives:results,textures,tangent_buffers_repaired:false,photo_texture_used:false,material_measured:false,art_accepted:false};
await fs.writeFile(O+'material-export-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
