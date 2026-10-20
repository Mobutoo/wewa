// Inspect actual buffers, including axial drilled openings after all modifiers.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {getBounds} from '@gltf-transform/functions';
import validator from 'gltf-validator';
const revision=process.argv[2]||'v1',v2=revision==='v2';
const results=[];
for(const name of v2?['front-brake-plate-v2-inspection.glb','front-wheel-panel-v2-fit-inspection.glb']:['front-brake-plate-inspection.glb','front-wheel-panel-fit-inspection.glb']){
 const file='assets-src/moto-components/front-brake-plate/'+name,data=await fs.readFile(file),valid=await validator.validateBytes(new Uint8Array(data),{uri:file,maxIssues:30});
 const document=await new NodeIO().read(file),root=document.getRoot(),bounds=getBounds(root.getDefaultScene()),dimensions=bounds.max.map((x,i)=>x-bounds.min[i]);
 let vertices=0,triangles=0,volume=0;const hits={axle:[],cam:[],socket:[]};
 const probes={axle:[.29,0],cam:[.25,.030],socket:[.318,.043]};
 for(const mesh of root.listMeshes())for(const primitive of mesh.listPrimitives()){
  const positions=primitive.getAttribute('POSITION'),indices=primitive.getIndices();vertices+=positions.getCount();triangles+=indices.getCount()/3;const a=[],b=[],c=[];
  for(let i=0;i<indices.getCount();i+=3){
   positions.getElement(indices.getScalar(i),a);positions.getElement(indices.getScalar(i+1),b);positions.getElement(indices.getScalar(i+2),c);
   volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;
   if(!name.startsWith('front-brake-plate-'))continue;
   const denominator=(b[1]-c[1])*(a[2]-c[2])+(c[2]-b[2])*(a[1]-c[1]);
   if(Math.abs(denominator)<1e-16)continue;
   for(const [label,[y,z]] of Object.entries(probes)){
    const u=((b[1]-c[1])*(z-c[2])+(c[2]-b[2])*(y-c[1]))/denominator;
    const v=((c[1]-a[1])*(z-c[2])+(a[2]-c[2])*(y-c[1]))/denominator,w=1-u-v;
    if(u>=-1e-8&&v>=-1e-8&&w>=-1e-8)hits[label].push(u*a[0]+v*b[0]+w*c[0]);
   }
  }
 }
 const only=name.startsWith('front-brake-plate-'),diameter=only?.144:.58;
 const result={file,bytes:data.length,sha256:createHash('sha256').update(data).digest('hex'),glTF_errors:valid.issues.numErrors,glTF_warnings:valid.issues.numWarnings,glTF_messages:valid.issues.messages,meshes:root.listMeshes().length,vertices,triangles,bounds,dimensions_xyz_m:dimensions,signed_volume_m3:volume,axial_ray_hits:only?hits:null,materials:root.listMaterials().map(m=>({name:m.getName(),roughness:m.getRoughnessFactor(),metallic:m.getMetallicFactor(),normal_texture:m.getNormalTexture()?.getName()||null,roughness_texture:m.getMetallicRoughnessTexture()?.getName()||null}))};
 if(valid.issues.numErrors||Math.abs(dimensions[1]-diameter)>.005||Math.abs(dimensions[2]-diameter)>.005||volume<=0||!root.listMaterials().some(m=>m.getName()==='Panel machined bores and seat'))throw Error(JSON.stringify(result));
 if(only&&(hits.axle.length||hits.cam.length||!hits.socket.length||Math.abs(Math.max(...hits.socket)-.042)>.001))throw Error('Blocked bore or incorrect socket: '+JSON.stringify(result));
 results.push(result);
}
const report={scope:'Format, candidate scale, material presence and actual exported drilled openings; no exact RDC fitment, artistic or hardware qualification',exports:results,art_accepted:false};
await fs.writeFile('creative/reviews/front-brake-plate-'+revision+'/geometry-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
