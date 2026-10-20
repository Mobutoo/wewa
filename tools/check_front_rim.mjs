// Verify the real exported casting, including spokes after modifier evaluation.
import fs from 'node:fs/promises';
import {NodeIO} from '@gltf-transform/core';
import {getBounds} from '@gltf-transform/functions';
import validator from 'gltf-validator';
const base='assets-src/moto-components/front-rim/';
const results=[];
for(const name of ['front-rim-inspection.glb','front-wheel-fit-inspection.glb']){
 const file=base+name,data=await fs.readFile(file);
 const valid=await validator.validateBytes(new Uint8Array(data),{uri:file,maxIssues:30});
 const document=await new NodeIO().read(file),root=document.getRoot();
 const bounds=getBounds(root.getDefaultScene()),dimensions=bounds.max.map((v,i)=>v-bounds.min[i]);
 let vertices=0,triangles=0,volume=0;const crossings=[];
 for(const mesh of root.listMeshes())for(const primitive of mesh.listPrimitives()){
  const pos=primitive.getAttribute('POSITION'),indices=primitive.getIndices();
  vertices+=pos.getCount();triangles+=indices.getCount()/3;
  const a=[],b=[],c=[];
  for(let i=0;i<indices.getCount();i+=3){
   pos.getElement(indices.getScalar(i),a);pos.getElement(indices.getScalar(i+1),b);pos.getElement(indices.getScalar(i+2),c);
   volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;
   // Circle at axle plane, radius140mm: two boundaries for each of five spokes.
   if(name!=='front-rim-inspection.glb')continue;
   const section=[];
   for(const [p,q] of [[a,b],[b,c],[c,a]]){
    if(p[0]*q[0]>=0)continue;
    const t=-p[0]/(q[0]-p[0]);section.push([p[1]+t*(q[1]-p[1])-.29,p[2]+t*(q[2]-p[2])]);
   }
   if(section.length!==2)continue;
   const [p,q]=section,dx=q[0]-p[0],dy=q[1]-p[1],A=dx*dx+dy*dy,B=2*(p[0]*dx+p[1]*dy),C=p[0]*p[0]+p[1]*p[1]-.14**2,D=B*B-4*A*C;
   if(D<0||A<1e-16)continue;
   for(const t of [(-B-Math.sqrt(D))/(2*A),(-B+Math.sqrt(D))/(2*A)])if(t>=0&&t<=1)crossings.push(Math.atan2(p[1]+t*dy,p[0]+t*dx));
  }
 }
 crossings.sort((a,b)=>a-b);const unique=crossings.filter((a,i)=>!i||a-crossings[i-1]>1e-4);
 const result={file,bytes:data.length,glTF_errors:valid.issues.numErrors,glTF_warnings:valid.issues.numWarnings,glTF_messages:valid.issues.messages,meshes:root.listMeshes().length,vertices,triangles,bounds,dimensions_xyz_m:dimensions,signed_volume_m3:volume,casting_spoke_circle_boundaries:name==='front-rim-inspection.glb'?unique.length:null,materials:root.listMaterials().map(m=>({name:m.getName(),roughness:m.getRoughnessFactor(),metallic:m.getMetallicFactor()}))};
 if(!root.listMaterials().some(m=>m.getName()==='Machined drum and bearing seat'))throw Error('Machined surface assignment missing from actual export');
 const diameter=name==='front-rim-inspection.glb'?.453:.58;
 if(valid.issues.numErrors||Math.abs(dimensions[1]-diameter)>.005||Math.abs(dimensions[2]-diameter)>.005||dimensions[0]<.068||dimensions[0]>.080||volume<=0||(name==='front-rim-inspection.glb'&&unique.length!==10))throw Error(JSON.stringify(result));
 results.push(result);
}
const report={scope:'Real exported buffers: format, scale, positive volume and five casting spokes. Not an OEM section, physical seal, artistic acceptance or iPhone performance qualification.',exports:results,art_accepted:false};
await fs.writeFile('creative/reviews/front-rim-v1/geometry-check.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
