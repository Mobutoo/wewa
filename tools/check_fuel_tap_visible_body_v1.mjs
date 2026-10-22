/** Independent inspection of the exact GLB buffers; no manufacturer-fit assertion. */
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {getBounds} from '@gltf-transform/functions';
import {validateBytes} from 'gltf-validator';
const file='assets-src/moto-components/fuel-tap-visible-body-v1/child-candidate.glb',bytes=await fs.readFile(file);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const validation=await validateBytes(bytes,{maxIssues:1000});if(validation.issues.numErrors)throw Error(JSON.stringify(validation.issues));
const doc=await new NodeIO().readBinary(bytes),rows=[];
for(const node of doc.getRoot().listNodes().filter(n=>n.getMesh())){
 let minimumArea=Infinity,triangles=0,normalError=0;
 for(const primitive of node.getMesh().listPrimitives()){
  const p=primitive.getAttribute('POSITION'),n=primitive.getAttribute('NORMAL'),ix=primitive.getIndices();if(primitive.getMode()!==4||!ix||!n)throw Error('Missing triangle/normal data');
  for(let i=0;i<n.getCount();i++){const v=n.getElement(i,[]);normalError=Math.max(normalError,Math.abs(Math.hypot(...v)-1));}
  for(let i=0;i<ix.getCount();i+=3){const [a,b,c]=[0,1,2].map(j=>p.getElement(ix.getScalar(i+j),[])),u=b.map((v,j)=>v-a[j]),v=c.map((x,j)=>x-a[j]),area=Math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])/2;if(!Number.isFinite(area)||area<=1e-15)throw Error(`Degenerate triangle: ${node.getName()}: ${area}`);minimumArea=Math.min(area,minimumArea);triangles++;}
 }
 if(normalError>.002)throw Error('Non-unit normals');rows.push({object:node.getName(),triangles,minimum_triangle_area_m2:minimumArea,maximum_normal_length_error:normalError,bounds:getBounds(node)});
}
if(rows.length!==3)throw Error('Three separate exterior parts required');
const native=JSON.parse(await fs.readFile('creative/reviews/fuel-tap-visible-body-v1/source-geometry-check.json'));
for(const row of rows){const part=native.parts.find(p=>p.object===row.object);if(!part||part.triangles!==row.triangles||!part.closed)throw Error('Source/export triangle mismatch');}
await fs.writeFile('creative/reviews/fuel-tap-visible-body-v1/export-buffer-check.json',JSON.stringify({source:file,sha256:sha(bytes),parts:rows,gltf_validator:validation.issues,native_triangle_counts_agree:true,scope:'Actual buffers, topology checked separately in native; not photographic calibration, flow geometry or mechanical fit',art_accepted:false},null,2)+'\n');
console.log('FUEL_TAP_EXPORT_OK',rows.reduce((s,r)=>s+r.triangles,0));
