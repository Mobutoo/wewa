import fs from 'node:fs/promises';import crypto from 'node:crypto';import {NodeIO} from '@gltf-transform/core';import validator from 'gltf-validator';
const O=new URL('./',import.meta.url);const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const rows=[],sign=[];
for(const name of ['context-native.glb','kit-gray.glb','kit-material.glb']){
 const bytes=await fs.readFile(new URL(name,O));const validation=await validator.validateBytes(bytes);await fs.writeFile(new URL(name+'.validator.json',O),JSON.stringify(validation,null,2));
 const root=(await new NodeIO().read(new URL(name,O).pathname)).getRoot();let triangles=0,degenerate=0,nonfinite=0;const records=[];
 for(const mesh of root.listMeshes())for(const p of mesh.listPrimitives()){
  const attrs={};for(const semantic of p.listSemantics()){const a=p.getAttribute(semantic).getArray();attrs[semantic]=sha(Buffer.from(a.buffer,a.byteOffset,a.byteLength));for(const v of a)if(!Number.isFinite(v))nonfinite++;}
  const ind=p.getIndices()?.getArray(),pos=p.getAttribute('POSITION').getArray();const n=ind?ind.length:pos.length/3;triangles+=n/3;
  for(let i=0;i<n;i+=3){const ids=[0,1,2].map(j=>(ind?ind[i+j]:i+j)*3);const a=[0,1,2].map(j=>pos[ids[1]+j]-pos[ids[0]+j]),b=[0,1,2].map(j=>pos[ids[2]+j]-pos[ids[0]+j]);if(Math.hypot(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])===0)degenerate++;}
  records.push({name:mesh.getName(),attrs,indices:ind?sha(Buffer.from(ind.buffer,ind.byteOffset,ind.byteLength)):null,material:p.getMaterial()?.getName()});
 }
 const nodes=root.listNodes().map(n=>({name:n.getName(),matrix:n.getMatrix(),mesh:n.getMesh()?.getName()}));const geometry=records.map(({material,...r})=>r);sign.push(JSON.stringify({geometry,nodes}));rows.push({file:name,sha256:sha(bytes),errors:validation.issues.numErrors,warnings:validation.issues.numWarnings,meshes:root.listMeshes().length,triangles,degenerate_triangles:degenerate,nonfinite,records,nodes});
}
const report={exports:rows,gray_material_geometry_normals_uv_indices_nodes_equal:sign[1]===sign[2],strict_pass:rows.every(r=>r.errors===0&&r.nonfinite===0),scope:'Actual exported accessors and node matrices; degenerates counted, historical sources not repaired; no fit or art acceptance'};
await fs.writeFile(new URL('export-parity.json',O),JSON.stringify(report,null,2));console.log(JSON.stringify({strict_pass:report.strict_pass,parity:sign[1]===sign[2],exports:rows.map(({records,nodes,...r})=>r)}));if(!report.strict_pass||sign[1]!==sign[2])process.exitCode=1;
