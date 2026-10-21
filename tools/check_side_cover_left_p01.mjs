import fs from 'node:fs/promises';import crypto from 'node:crypto';import {NodeIO} from '@gltf-transform/core';import validator from 'gltf-validator';
const base='assets-src/moto-components/side-cover-left/',names=['side-cover-left-study-v1.glb','side-cover-left-candidate-v1.glb'],results=[],buffers=[];
for(const name of names){let bytes;try{bytes=await fs.readFile(base+name)}catch(e){if(name.includes('candidate'))continue;throw e}
 const v=await validator.validateBytes(bytes);if(v.issues.numErrors)throw Error(JSON.stringify(v.issues));const root=(await new NodeIO().read(base+name)).getRoot(),tris=[],verts=[],normals=[];let minDot=1,minimumArea=Infinity;
 for(const mesh of root.listMeshes())for(const p of mesh.listPrimitives()){
 const pos=p.getAttribute('POSITION'),nor=p.getAttribute('NORMAL'),idx=p.getIndices().getArray();
 for(let j=0;j<idx.length;j+=3){const pts=[0,1,2].map(k=>pos.getElement(idx[j+k],[]));const keys=pts.map(v=>v.map(x=>x.toFixed(8)).join(','));tris.push(keys);const u=pts[1].map((x,i)=>x-pts[0][i]),w=pts[2].map((x,i)=>x-pts[0][i]);let n=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]];const len=Math.hypot(...n);minimumArea=Math.min(minimumArea,len/2);if(!(len>0))throw Error('Degenerate triangle');n=n.map(x=>x/len);for(let k=0;k<3;k++){const nn=nor.getElement(idx[j+k],[]);const dot=n.reduce((s,x,i)=>s+x*nn[i],0);minDot=Math.min(minDot,dot);if(nn.some(x=>!Number.isFinite(x))||Math.abs(Math.hypot(...nn)-1)>.015)throw Error('Normal invalid');normals.push([...pts[k],...nn]);}}
 }
 const edges=new Map();for(const t of tris)for(let j=0;j<3;j++){const key=[t[j],t[(j+1)%3]].sort().join('|');edges.set(key,(edges.get(key)||0)+1)}
 if([...edges.values()].some(n=>n>2)||minDot<=0)throw Error('Invalid exterior topology/normals');
 const boundary=[...edges].filter(([k,v])=>v===1);if(boundary.length!==240)throw Error('Unexpected open boundary count '+boundary.length);
 const graph=new Map();for(const [edge]of boundary){const [a,b]=edge.split('|');for(const [x,y] of [[a,b],[b,a]]){if(!graph.has(x))graph.set(x,new Set());graph.get(x).add(y)}}if([...graph.values()].some(v=>v.size!==2))throw Error('Branched boundary');const seen=new Set(),todo=[graph.keys().next().value];while(todo.length){const k=todo.pop();if(seen.has(k))continue;seen.add(k);todo.push(...graph.get(k))}if(seen.size!==graph.size)throw Error('More than one boundary');
 // Canonical triangles compare actual source-export geometry, independent of material primitive split/order.
 buffers.push(normals.map(v=>v.map(x=>x.toFixed(7)).join(',')).sort());
 results.push({path:base+name,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),triangles:tris.length,min_face_corner_normal_dot:minDot,minimum_triangle_area:minimumArea,glTF_errors:v.issues.numErrors,glTF_warnings:v.issues.numWarnings,open_boundary_loops:1,open_boundary_edges:boundary.length});
}
const identical=buffers.length===2?JSON.stringify(buffers[0])===JSON.stringify(buffers[1]):null;if(identical===false)throw Error('Material export changed actual geometry/normals');
await fs.writeFile('creative/reviews/side-cover-left-study-v1/independent-export-check.json',JSON.stringify({exports:results,gray_material_actual_geometry_normals_equal:identical,scope:'Actual triangle/normal and topology checks; not calibrated surface fidelity, fit, UV parity or art acceptance'},null,2)+'\n');console.log(JSON.stringify(results));
