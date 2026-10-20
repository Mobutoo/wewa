import fs from 'node:fs/promises';import{createHash}from'node:crypto';
import{NodeIO}from'@gltf-transform/core';import{getBounds}from'@gltf-transform/functions';import validator from'gltf-validator';
const path='assets-src/moto-components/ignition-lock/ignition-lock-inspection.glb',data=await fs.readFile(path),valid=await validator.validateBytes(new Uint8Array(data),{uri:path,maxIssues:30}),root=(await new NodeIO().read(path)).getRoot(),meshes=[];
for(const node of root.listNodes().filter(n=>n.getMesh())){
 const matrix=node.getWorldMatrix();let volume=0,triangles=0,vertices=0;
 const transform=v=>{const[x,y,z]=v;v[0]=matrix[0]*x+matrix[4]*y+matrix[8]*z+matrix[12];v[1]=matrix[1]*x+matrix[5]*y+matrix[9]*z+matrix[13];v[2]=matrix[2]*x+matrix[6]*y+matrix[10]*z+matrix[14];};
 for(const p of node.getMesh().listPrimitives()){
  const pos=p.getAttribute('POSITION'),ix=p.getIndices();vertices+=pos.getCount();triangles+=ix.getCount()/3;const a=[],b=[],c=[];
  for(let i=0;i<ix.getCount();i+=3){pos.getElement(ix.getScalar(i),a);pos.getElement(ix.getScalar(i+1),b);pos.getElement(ix.getScalar(i+2),c);transform(a);transform(b);transform(c);volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;}
 }
 const ink=node.getName().includes(' label - original geometry');if(!ink&&volume<=0)throw Error('Nonpositive structural volume '+node.getName());meshes.push({name:node.getName(),vertices,triangles,world_volume_m3:volume,structural_closed_body:!ink});
}
const animations=root.listAnimations().map(a=>({name:a.getName(),channels:a.listChannels().map(c=>({node:c.getTargetNode()?.getName(),path:c.getTargetPath()}))}));
const report={path,sha256:createHash('sha256').update(data).digest('hex'),glTF_errors:valid.issues.numErrors,glTF_warnings:valid.issues.numWarnings,messages:valid.issues.messages,bounds:getBounds(root.getDefaultScene()),meshes,animations,scope:'Four positive hardware bodies; original printed marks may be planar; animation states not measured locking detents',art_accepted:false};
if(report.glTF_errors||meshes.filter(m=>m.structural_closed_body).length!==4||!animations.some(a=>a.channels.some(c=>c.path==='rotation')))throw Error(JSON.stringify(report));
await fs.writeFile('creative/reviews/ignition-lock-v1/export-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
