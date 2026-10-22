import fs from 'node:fs/promises';import crypto from 'node:crypto';import {NodeIO}from '@gltf-transform/core';
const O=new URL('./',import.meta.url);const sha=a=>crypto.createHash('sha256').update(Buffer.from(a.buffer,a.byteOffset,a.byteLength)).digest('hex');const sets=[];
for(const file of ['kit-gray.glb','kit-material.glb']){
 const root=(await new NodeIO().read(new URL(file,O).pathname)).getRoot();const rows=[];for(const node of root.listNodes()){
  const mesh=node.getMesh();if(!mesh)continue;const primitives=[];for(const p of mesh.listPrimitives()){
   const ind=p.getIndices().getArray();const attrs={};for(const semantic of p.listSemantics()){
    const attr=p.getAttribute(semantic),a=attr.getArray(),width=attr.getElementSize(),expanded=new a.constructor(ind.length*width);for(let i=0;i<ind.length;i++)for(let j=0;j<width;j++)expanded[i*width+j]=a[ind[i]*width+j];attrs[semantic]=sha(expanded);
   }primitives.push({corners:ind.length,attrs});
  }rows.push({name:node.getName(),matrix:node.getWorldMatrix(),primitives});
 }rows.sort((a,b)=>a.name.localeCompare(b.name));sets.push(rows);
}
const differences=[];const A=new Map(sets[0].map(r=>[r.name,r]));for(const b of sets[1]){const a=A.get(b.name);if(JSON.stringify(a)!==JSON.stringify(b))differences.push({name:b.name,gray:a,material:b});A.delete(b.name);}for(const a of A.values())differences.push({name:a.name,gray:a});
const report={actual_node_parity:!differences.length,gray_rendered_triangles:sets[0].reduce((s,n)=>s+n.primitives.reduce((t,p)=>t+p.corners/3,0),0),material_rendered_triangles:sets[1].reduce((s,n)=>s+n.primitives.reduce((t,p)=>t+p.corners/3,0),0),node_counts:sets.map(r=>r.length),differences,scope:'Expanded indexed triangle-corner buffers for every actual mesh node plus world matrices. Handles genuine shared-mesh instances. Earlier definition-level mismatch retained in export-parity.json.'};await fs.writeFile(new URL('node-geometry-parity.json',O),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(differences.length)process.exitCode=1;
