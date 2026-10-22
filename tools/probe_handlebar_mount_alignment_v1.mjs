/** Ray probe of the actual upper-plate buffers at the current handlebar stud axes. */
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {parentMatrix,multiply} from './compose_motorcycle_gltf_v1.mjs';
const planPath='creative/research/motorcycle-exterior-v5/parents.json',routePath='creative/research/motorcycle-exterior-v5/routes.json';
const plan=JSON.parse(await fs.readFile(planPath)),routes=JSON.parse(await fs.readFile(routePath)),row=plan.parents.find(r=>r.key==='steering-upper'),route=routes.rows.find(r=>r.key===row.key);
const io=new NodeIO(),doc=await io.read(route.glb),world=parentMatrix(row),triangles=[];
const sub=(a,b)=>a.map((x,i)=>x-b[i]),dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const point=(m,p)=>[0,1,2].map(i=>m[i]*p[0]+m[4+i]*p[1]+m[8+i]*p[2]+m[12+i]);
for(const node of doc.getRoot().listNodes().filter(n=>n.getMesh())){
 const m=multiply(world,node.getWorldMatrix());
 for(const prim of node.getMesh().listPrimitives()){
  const p=prim.getAttribute('POSITION'),ix=prim.getIndices();if(!ix||prim.getMode()!==4)throw Error('Expected triangle indices');
  for(let i=0;i<ix.getCount();i+=3)triangles.push([0,1,2].map(j=>point(m,p.getElement(ix.getScalar(i+j),[]))));
 }
}
function ray(origin,direction){let nearest=Infinity;for(const [a,b,c]of triangles){const ab=sub(b,a),ac=sub(c,a),h=cross(direction,ac),det=dot(ab,h);if(Math.abs(det)<1e-16)continue;const s=sub(origin,a),u=dot(s,h)/det;if(u<0||u>1)continue;const q=cross(s,ab),v=dot(direction,q)/det;if(v<0||u+v>1)continue;const t=dot(ac,q)/det;if(t>=0&&t<nearest)nearest=t;}return Number.isFinite(nearest)?origin.map((v,i)=>v+direction[i]*nearest):null;}
const rays=[-.052,-.045,-.038,.038,.045,.052].map(x=>{const origin=[x,.1,.0975],hit=ray(origin,[0,-1,0]);return{origin_native_m:[x,-.0975,.1],direction_native:[0,0,-1],hit_native_m:hit?[hit[0],-hit[2],hit[1]]:null,is_current_stud_axis:Math.abs(x)===.045};});
if(!rays.filter(r=>r.is_current_stud_axis).every(r=>r.hit_native_m)||rays.filter(r=>Math.abs(r.origin_native_m[0])===.038).some(r=>r.hit_native_m))throw Error('Native blocker observation not reproduced');
const hashes={};for(const p of [planPath,routePath,route.glb,'tools/probe_handlebar_mount_alignment_v1.mjs'])hashes[p]=crypto.createHash('sha256').update(await fs.readFile(p)).digest('hex');
const report={input_sha256:hashes,source:route.glb,triangles_tested:triangles.length,rays,conclusion:'Current stud axes encounter plate material; nearby hole axes pass through. Lower fitted fastener stack remains blocked.',scope:'Actual exported triangle intersection, not original engineering dimensions, thread contact or a certified fitted tolerance.'};
await fs.writeFile('creative/reviews/motorcycle-exterior-v5/handlebar-mount-alignment.json',JSON.stringify(report,null,2)+'\n');console.log('MOUNT_MISMATCH_REPRODUCED');
