/** Verify fitted exported attributes and compare validator findings with the input. */
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {validateBytes} from 'gltf-validator';
const review='creative/reviews/under-tank-layout-v3/';
const path='assets-src/moto-components/under-tank-layout-v3/motorcycle-layout.glb';
const baseline=await validateBytes(await fs.readFile('assets-src/moto-components/visual-proportions-v2/motorcycle-proportions.glb'),{maxIssues:10000});
const bytes=await fs.readFile(path),result=await validateBytes(bytes,{maxIssues:10000});
assert.equal(result.issues.numErrors,0);
assert.deepEqual(result.issues.messages.filter(m=>m.severity===1),baseline.issues.messages.filter(m=>m.severity===1));
const composition=JSON.parse(await fs.readFile(review+'composition-check.json'));
const doc=await new NodeIO().registerExtensions(ALL_EXTENSIONS).read(path),parts=[];
for(const row of composition.fitted_connections){
 const node=doc.getRoot().listNodes().find(n=>n.getName()===row.name),mesh=node.getMesh(),matrix=node.getWorldMatrix();
 const lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
 let triangles=0,minArea=Infinity;
 for(const primitive of mesh.listPrimitives()){
  const p=primitive.getAttribute('POSITION'),n=primitive.getAttribute('NORMAL'),idx=primitive.getIndices();
  assert.equal(primitive.getMode(),4);assert(n&&idx);
  for(const value of p.getArray())assert(Number.isFinite(value));
  for(let i=0;i<p.getCount();i++){const v=p.getElement(i,[]),g=[0,1,2].map(k=>matrix[k]*v[0]+matrix[4+k]*v[1]+matrix[8+k]*v[2]+matrix[12+k]),b=[g[0],-g[2],g[1]];for(let k=0;k<3;k++){lo[k]=Math.min(lo[k],b[k]);hi[k]=Math.max(hi[k],b[k]);}}
  for(let i=0;i<n.getCount();i++)assert(Math.abs(Math.hypot(...n.getElement(i,[]))-1)<1e-5);
  for(let i=0;i<idx.getCount();i+=3){
   const [a,b,c]=[0,1,2].map(j=>p.getElement(idx.getScalar(i+j),[]));
   const u=b.map((v,k)=>v-a[k]),v=c.map((x,k)=>x-a[k]);
   const area=.5*Math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);
   assert(area>1e-15,`${row.name}: zero-area triangle ${i/3}`);minArea=Math.min(minArea,area);triangles++;
  }
 }
 parts.push({name:row.name,triangles,min_local_triangle_area:minArea,blender_world_bounds:{min:lo,max:hi}});
}
await fs.writeFile(review+'export-check.json',JSON.stringify({path,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),errors:result.issues.numErrors,warnings:result.issues.messages.filter(m=>m.severity===1),no_new_warnings:true,fitted_parts:parts},null,2)+'\n');
console.log('LAYOUT_EXPORT',parts.length,'fitted meshes; zero errors, no new warnings');
