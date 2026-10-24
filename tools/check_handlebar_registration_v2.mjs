/** Read the actual exported plate buffers and test the whole stud cross-section. */
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {NodeIO} from '@gltf-transform/core';
import {validateBytes} from 'gltf-validator';
import {parentMatrix, multiply} from './compose_motorcycle_gltf_v1.mjs';

const planPath = 'creative/research/handlebar-registration-v2/plan.json';
const plan = JSON.parse(await fs.readFile(planPath));
const rows = JSON.parse(await fs.readFile('creative/research/motorcycle-exterior-v5/parents.json')).parents;
const routes = JSON.parse(await fs.readFile('creative/research/motorcycle-exterior-v5/routes.json')).rows;
const row = rows.find(r => r.key === 'steering-upper');
const route = routes.find(r => r.key === row.key);
const file = await fs.readFile(route.glb);
const doc = await new NodeIO().readBinary(file);
const world = parentMatrix(row), triangles = [];
const sub = (a,b) => a.map((v,i) => v-b[i]);
const dot = (a,b) => a.reduce((s,v,i) => s+v*b[i],0);
const cross = (a,b) => [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const point = (m,p) => [0,1,2].map(i => m[i]*p[0]+m[4+i]*p[1]+m[8+i]*p[2]+m[12+i]);
for (const node of doc.getRoot().listNodes().filter(n => n.getMesh())) {
  const matrix = multiply(world,node.getWorldMatrix());
  for (const primitive of node.getMesh().listPrimitives()) {
    const positions = primitive.getAttribute('POSITION'), indices = primitive.getIndices();
    assert.equal(primitive.getMode(),4); assert(indices);
    for (let i=0;i<indices.getCount();i+=3) {
      const [a,b,c] = [0,1,2].map(j => point(matrix,positions.getElement(indices.getScalar(i+j),[])));
      const ab=sub(b,a), ac=sub(c,a), h=cross([0,-1,0],ac), det=dot(ab,h);
      if (Math.abs(det)>1e-16) triangles.push({a,ab,ac,h,det});
    }
  }
}
function intersects(origin) {
  for (const {a,ab,ac,h,det} of triangles) {
    const s=sub(origin,a), u=dot(s,h)/det;
    if (u<0||u>1) continue;
    const q=cross(s,ab), v=-q[1]/det;
    if (v<0||u+v>1) continue;
    const t=dot(ac,q)/det;
    if (t>=0 && t<=.2) return true;
  }
  return false;
}
const probes=[];
for (const centre of [...plan.old_centres_x_m,...plan.candidate_centres_x_m]) {
  const samples=[[0,0]];
  for (const radius of [.0025,.005]) for (let i=0;i<64;i++) {
    const a=i*Math.PI*2/64; samples.push([radius*Math.cos(a),radius*Math.sin(a)]);
  }
  const hits=samples.filter(([x,z]) => intersects([centre+x,.1,.09749999642372131+z]));
  probes.push({centre_x_m:centre, samples:samples.length, radius_m:.005, blocked_samples:hits.length});
}
assert(probes.slice(0,2).every(p=>p.blocked_samples>0));
assert(probes.slice(2).every(p=>p.blocked_samples===0),JSON.stringify(probes));
const validations=[];
for (const name of ['clamps.glb','motorcycle-registration-candidate.glb']) {
  const path='assets-src/moto-components/handlebar-registration-v2/'+name, bytes=await fs.readFile(path);
  const report=await validateBytes(bytes,{uri:name,maxIssues:0});
  assert.equal(report.issues.numErrors,0,JSON.stringify(report.issues));
  validations.push({path,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),issues:report.issues});
}
const report={schema:1,probes,validations,plate_glb:route.glb,plate_sha256:crypto.createHash('sha256').update(file).digest('hex'),
  plan_sha256:crypto.createHash('sha256').update(await fs.readFile(planPath)).digest('hex'),
  scope:'129 rays over each 10 mm stud cross-section through the actual plate export. Sampling supplements native triangle intersection; neither certifies mounting preload or original dimensions.',art_accepted:false};
await fs.writeFile('creative/reviews/handlebar-registration-v2/export-check.json',JSON.stringify(report,null,2)+'\n');
console.log('REGISTRATION_EXPORT_CHECK',JSON.stringify(probes));
