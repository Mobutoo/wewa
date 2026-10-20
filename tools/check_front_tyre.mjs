// Inspect real exported buffers, independently from the Blender build counters.
import fs from 'node:fs/promises';
import {NodeIO} from '@gltf-transform/core';
import {getBounds} from '@gltf-transform/functions';
import validator from 'gltf-validator';
const file='assets-src/moto-components/front-tyre/front-tyre-inspection.glb';
const data=await fs.readFile(file);
const valid=await validator.validateBytes(new Uint8Array(data),{uri:file,maxIssues:20});
const document=await new NodeIO().read(file);const root=document.getRoot();const bounds=getBounds(root.getDefaultScene());
const dimensions=bounds.max.map((x,i)=>x-bounds.min[i]);let vertices=0,triangles=0,signedVolume=0,crownNormalChecks=0,crownOutward=0;
for(const mesh of root.listMeshes())for(const primitive of mesh.listPrimitives()){
 const pos=primitive.getAttribute('POSITION'),normal=primitive.getAttribute('NORMAL'),idx=primitive.getIndices();
 vertices+=pos.getCount();triangles+=idx.getCount()/3;
 const p=[0,0,0],n=[0,0,0];
 for(let i=0;i<pos.getCount();i++){
  pos.getElement(i,p);normal.getElement(i,n);
  const dy=p[1]-.29,dz=p[2];const r=Math.hypot(dy,dz);
  if(Math.abs(p[0])<.012&&r>.285){crownNormalChecks++;if(n[1]*dy+n[2]*dz>0)crownOutward++;}
 }
 const a=[0,0,0],b=[0,0,0],c=[0,0,0];
 for(let i=0;i<idx.getCount();i+=3){pos.getElement(idx.getScalar(i),a);pos.getElement(idx.getScalar(i+1),b);pos.getElement(idx.getScalar(i+2),c);signedVolume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;}
}
const result={scope:'Exported geometry and format integrity only; no OEM identity, user art or mobile performance acceptance',file,bytes:data.length,glTF_errors:valid.issues.numErrors,glTF_warnings:valid.issues.numWarnings,glTF_messages:valid.issues.messages,meshes:root.listMeshes().length,vertices,triangles,bounds,dimensions_xyz_m:dimensions,signed_volume_m3:signedVolume,crown_outward_fraction:crownOutward/crownNormalChecks,materials:root.listMaterials().map(m=>({name:m.getName(),base_color:m.getBaseColorFactor(),roughness:m.getRoughnessFactor(),normal_texture_present:!!m.getNormalTexture()})),art_accepted:false};
await fs.writeFile('creative/reviews/front-tyre-v1/geometry-check.json',JSON.stringify(result,null,2)+'\n');
if(valid.issues.numErrors||dimensions[0]<.068||dimensions[0]>.080||Math.abs(dimensions[1]-.58)>.004||Math.abs(dimensions[2]-.58)>.004||signedVolume<=0||result.crown_outward_fraction<.99||result.materials.some(m=>Math.abs(m.roughness-.60)>.001))throw Error('Geometry integrity check failed: '+JSON.stringify(result));
console.log(JSON.stringify(result,null,2));
