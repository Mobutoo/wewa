/** Validate delivered exports and actual triangle buffers, including the new shells. */
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {validateBytes} from 'gltf-validator';

const folder='assets-src/moto-components/under-tank-completion-v1/';
const baseline=await validateBytes(await fs.readFile('assets-src/moto-components/handlebar-registration-v2/motorcycle-registration-candidate.glb'),{maxIssues:200});
const inheritedWarnings=baseline.issues.messages.filter(m=>m.severity===1);
const reports=[];
for(const name of ['additions.glb','motorcycle-completed-candidate.glb']){
  const raw=await fs.readFile(folder+name);
  const result=await validateBytes(raw,{uri:name,maxIssues:100});
  assert.equal(result.issues.numErrors,0);
  assert.deepEqual(result.issues.messages.filter(m=>m.severity===1),name==='additions.glb'?[]:inheritedWarnings);
  reports.push({path:folder+name,sha256:crypto.createHash('sha256').update(raw).digest('hex'),issues:result.issues});
}
const doc=await new NodeIO().read(folder+'additions.glb');
const parts=[];
for(const mesh of doc.getRoot().listMeshes()){
  let triangles=0,minArea=Infinity;
  for(const primitive of mesh.listPrimitives()){
    const p=primitive.getAttribute('POSITION'),n=primitive.getAttribute('NORMAL'),idx=primitive.getIndices();
    assert.equal(primitive.getMode(),4);assert(idx);assert(n);assert(primitive.getMaterial());
    for(const v of p.getArray())assert(Number.isFinite(v));
    for(let i=0;i<n.getCount();i++)assert(Math.abs(Math.hypot(...n.getElement(i,[]))-1)<1e-4);
    for(let i=0;i<idx.getCount();i+=3){
      const [a,b,c]=[0,1,2].map(j=>p.getElement(idx.getScalar(i+j),[]));
      const u=b.map((v,k)=>v-a[k]),v=c.map((x,k)=>x-a[k]);
      const area=.5*Math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);
      assert(area>1e-15,`${mesh.getName()} degenerate triangle ${i/3}: ${area}`);
      minArea=Math.min(minArea,area);triangles++;
    }
  }
  parts.push({name:mesh.getName(),triangles,min_triangle_area_m2:minArea});
}
assert.equal(parts.length,75);
const native=JSON.parse(await fs.readFile('creative/reviews/under-tank-completion-v1/native-check.json'));
assert(native.mesh_checks.every(c=>c.non_manifold_edges===0&&c.volume_m3>0));
await fs.writeFile('creative/reviews/under-tank-completion-v1/export-check.json',JSON.stringify({
  validations:reports,parts,triangles:parts.reduce((s,p)=>s+p.triangles,0),inherited_warnings:inheritedWarnings,
  scope:'All new exported triangles finite and nondegenerate; normals unit length; native surfaces closed. Does not certify exact dimensions, mechanical assembly or moving cable clearance.',
  art_accepted:false},null,2)+'\n');
console.log('UNDER_TANK_EXPORT',parts.length,'meshes',parts.reduce((s,p)=>s+p.triangles,0),'triangles; glTF errors 0, no new warnings');
