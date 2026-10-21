import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
const baseline='/workspace/wewa-assets/work-in-progress/rear-rim/g3/rear-rim-inspection.glb';
const current='assets-src/moto-components/rear-rim/rear-rim-inspection.glb';
const semantics=['POSITION','NORMAL','TEXCOORD_0','TANGENT'];
async function canonical(file){
 const bytes=await fs.readFile(file),root=(await new NodeIO().read(file)).getRoot(),triangles=[],matrices=[];
 for(const node of root.listNodes().filter(n=>n.getMesh())){
  matrices.push(node.getWorldMatrix());
  for(const p of node.getMesh().listPrimitives()){
   for(const k of semantics)if(!p.getAttribute(k))throw Error('Missing '+k);
   const keys=[];
   for(let i=0;i<p.getAttribute('POSITION').getCount();i++){
    const values=[];
    for(const k of semantics){const a=[];p.getAttribute(k).getElement(i,a);values.push(...a);}
    keys.push(createHash('sha256').update(Buffer.from(new Float32Array(values).buffer)).digest('hex'));
   }
   const ix=p.getIndices();
   for(let i=0;i<ix.getCount();i+=3){
    const k=[0,1,2].map(j=>keys[ix.getScalar(i+j)]);let first=0;
    if(k[1]<k[first])first=1;if(k[2]<k[first])first=2;
    triangles.push(createHash('sha256').update(k[first]).update(k[(first+1)%3]).update(k[(first+2)%3]).digest('hex'));
   }
  }
 }
 triangles.sort();return {sha256:createHash('sha256').update(bytes).digest('hex'),triangles,digest:createHash('sha256').update(triangles.join('')).digest('hex'),matrices};
}
const a=await canonical(baseline),b=await canonical(current);
if(a.digest!==b.digest||JSON.stringify(a.matrices)!==JSON.stringify(b.matrices))throw Error('Material stage altered oriented corner attributes or transform');
const r={baseline,baseline_sha256:a.sha256,current,current_sha256:b.sha256,method:'Canonical oriented triangle multiset, all Float32 corner POSITION/NORMAL/TEXCOORD_0/TANGENTxyz+w; cyclic rotations only, preserving winding and duplicates. Independent of material splitting/index reorder.',triangles:b.triangles.length,canonical_triangle_digest:b.digest,geometry_normals_UV_TangentW_and_transforms_identical:true};
await fs.writeFile('creative/reviews/rear-rim-v1/material-preservation-check.json',JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify(r));
