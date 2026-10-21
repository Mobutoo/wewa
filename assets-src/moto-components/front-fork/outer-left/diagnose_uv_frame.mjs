// Read-only diagnostic for rejected preflight, never edits source or GLB.
import fs from'node:fs/promises';import{createHash}from'node:crypto';import{NodeIO}from'@gltf-transform/core';
const file='assets-src/moto-components/front-fork/outer-left/fork-outer-left-inspection.glb',bytes=await fs.readFile(file),root=(await new NodeIO().read(file)).getRoot(),rows=[];
for(const mesh of root.listMeshes())for(const p of mesh.listPrimitives()){
 const pos=p.getAttribute('POSITION'),normal=p.getAttribute('NORMAL'),t=p.getAttribute('TANGENT'),uv=p.getAttribute('TEXCOORD_0'),ix=p.getIndices(),bad=new Set();let minUV=Infinity;const collapsed=[];
 for(let i=0;i<t.getCount();i++){const a=[];t.getElement(i,a);if(Math.hypot(...a.slice(0,3))<.9)bad.add(i);}
 const get=(a,i)=>{const x=[];a.getElement(i,x);return x;},samples=[];
 for(let k=0;k<ix.getCount();k+=3){const ids=[0,1,2].map(j=>ix.getScalar(k+j)),u=ids.map(i=>get(uv,i)),area=Math.abs((u[1][0]-u[0][0])*(u[2][1]-u[0][1])-(u[1][1]-u[0][1])*(u[2][0]-u[0][0]))/2;minUV=Math.min(minUV,area);if(area<=1e-14&&collapsed.length<12)collapsed.push({triangle:k/3,ids,UV:u,position:ids.map(i=>get(pos,i))});if(ids.some(i=>bad.has(i))&&samples.length<16)samples.push({triangle:k/3,ids,UV:u,UVarea:area,position:ids.map(i=>get(pos,i)),normal:ids.map(i=>get(normal,i)),T:ids.map(i=>get(t,i))});}
 rows.push({mesh:mesh.getName(),invalid_tangent_vertices:bad.size,minimum_actual_UV_area:minUV,collapsed_UV_samples:collapsed,invalid_frame_adjacent_triangles:samples});
}
const r={file,sha256:createHash('sha256').update(bytes).digest('hex'),status:'rejected_preflight_diagnostic_only',rows};await fs.writeFile('creative/reviews/fork-outer-left-v1/rejected-frame-diagnostic.json',JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify(r));
