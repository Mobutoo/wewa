// Validate actual evaluated GLB geometry and its animation channels.
import fs from 'node:fs/promises';import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';import {getBounds} from '@gltf-transform/functions';import validator from 'gltf-validator';
const folder=process.argv[2]||'throttle-control',revision=folder+'-v2';
const path='assets-src/moto-components/'+folder+'/'+folder+'-v2-inspection.glb';
const data=await fs.readFile(path),valid=await validator.validateBytes(new Uint8Array(data),{uri:path,maxIssues:30});const root=(await new NodeIO().read(path)).getRoot(),meshes=[];
for(const node of root.listNodes().filter(n=>n.getMesh())){
 const matrix=node.getWorldMatrix();let volume=0,triangles=0,vertices=0,zeroAreaTriangles=0;
 const transform=v=>{const [x,y,z]=v;v[0]=matrix[0]*x+matrix[4]*y+matrix[8]*z+matrix[12];v[1]=matrix[1]*x+matrix[5]*y+matrix[9]*z+matrix[13];v[2]=matrix[2]*x+matrix[6]*y+matrix[10]*z+matrix[14];};
 for(const primitive of node.getMesh().listPrimitives()){
  const pos=primitive.getAttribute('POSITION'),ix=primitive.getIndices();vertices+=pos.getCount();triangles+=ix.getCount()/3;const a=[],b=[],c=[];
  for(let i=0;i<ix.getCount();i+=3){pos.getElement(ix.getScalar(i),a);pos.getElement(ix.getScalar(i+1),b);pos.getElement(ix.getScalar(i+2),c);const u=b.map((x,k)=>x-a[k]),v=c.map((x,k)=>x-a[k]);if(Math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])===0)zeroAreaTriangles++;transform(a);transform(b);transform(c);volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;}
 }
 if(zeroAreaTriangles)throw Error(node.getName()+' zero-area triangles '+zeroAreaTriangles);if(volume<=0)throw Error('Non-positive exported world volume '+node.getName());meshes.push({name:node.getName(),vertices,triangles,zeroAreaTriangles,world_volume_m3:volume});
}
const animations=root.listAnimations().map(a=>({name:a.getName(),channels:a.listChannels().map(c=>({node:c.getTargetNode()?.getName(),path:c.getTargetPath()}))}));
const report={path,sha256:createHash('sha256').update(data).digest('hex'),glTF_errors:valid.issues.numErrors,glTF_warnings:valid.issues.numWarnings,messages:valid.issues.messages,bounds:getBounds(root.getDefaultScene()),meshes,animations,materials:root.listMaterials().map(m=>({name:m.getName(),basecolor:m.getBaseColorFactor(),metallic:m.getMetallicFactor(),roughness:m.getRoughnessFactor()})),scope:'Actual buffers and animation presence; no exact variant, installed mechanical function, art or device qualification',art_accepted:false};
if(report.glTF_errors||!animations.length||!animations.some(a=>a.channels.some(c=>c.path==='rotation')))throw Error(JSON.stringify(report));
await fs.writeFile('creative/reviews/'+revision+'/export-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
