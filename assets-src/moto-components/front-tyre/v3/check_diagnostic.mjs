// Diagnostic export preflight only, not fidelity or sampled-target acceptance.
import fs from 'node:fs/promises';import{createHash}from'node:crypto';import{NodeIO}from'@gltf-transform/core';import validator from'gltf-validator';
const O='creative/reviews/front-tyre-v3/',src=JSON.parse(await fs.readFile(O+'diagnostic-source-geometry-check.json')),file=src.export_path;
const bytes=await fs.readFile(file),sha=x=>createHash('sha256').update(x).digest('hex');if(sha(bytes)!==src.export_sha256)throw Error('Changed diagnostic export');
const root=(await new NodeIO().read(file)).getRoot(),nodes=root.listNodes().filter(n=>n.getMesh());if(nodes.length!==1)throw Error('One diagnostic component only');
const dot=(a,b)=>a.reduce((s,v,j)=>s+v*b[j],0),sub=(a,b)=>a.map((v,j)=>v-b[j]),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const node=nodes[0],matrix=node.getWorldMatrix(),xf=([x,y,z])=>[matrix[0]*x+matrix[4]*y+matrix[8]*z+matrix[12],-(matrix[2]*x+matrix[6]*y+matrix[10]*z+matrix[14]),matrix[1]*x+matrix[5]*y+matrix[9]*z+matrix[13]];
const unique=new Map(),edges=new Map(),adj=[],id=v=>{const k=v.join(',');if(!unique.has(k)){unique.set(k,unique.size);adj.push([]);}return unique.get(k);};
let count=0,zero=0,uvzero=0,minarea=Infinity,volume=0,badnormals=0;
for(const p of node.getMesh().listPrimitives()){
 const pos=p.getAttribute('POSITION'),nor=p.getAttribute('NORMAL'),uv=p.getAttribute('TEXCOORD_0'),indices=p.getIndices().getArray(),V=[];
 for(let i=0;i<pos.getCount();i++){
  const a=pos.getElement(i,[]),n=nor.getElement(i,[]);if(![...a,...n].every(Number.isFinite)||Math.abs(Math.hypot(...n)-1)>.002)badnormals++;V.push(xf(a));
 }
 for(let k=0;k<indices.length;k+=3){
  const ids=[indices[k],indices[k+1],indices[k+2]],a=V[ids[0]],b=V[ids[1]],c=V[ids[2]],area=Math.hypot(...cross(sub(b,a),sub(c,a)))/2;
  count++;minarea=Math.min(minarea,area);if(area<=1e-18)zero++;volume+=dot(a,cross(b,c))/6;
  const ww=ids.map(i=>id(V[i]));for(let j=0;j<3;j++){const x=ww[j],y=ww[(j+1)%3],key=x<y?x+','+y:y+','+x;edges.set(key,(edges.get(key)||0)+1);adj[x].push(y);adj[y].push(x);}
  const [u,v,w]=ids.map(i=>uv.getElement(i,[]));if((v[0]-u[0])*(w[1]-u[1])-(v[1]-u[1])*(w[0]-u[0])===0)uvzero++;
 }
}
let components=0;const seen=new Set();for(let i=0;i<adj.length;i++){if(seen.has(i))continue;components++;const stack=[i];seen.add(i);while(stack.length){const a=stack.pop();for(const b of adj[a])if(!seen.has(b)){seen.add(b);stack.push(b);}}}
const nm=[...edges.values()].filter(x=>x!==2).length,chi=unique.size-edges.size+count,valid=await validator.validateBytes(new Uint8Array(bytes),{uri:file});
const r={source_sha256:src.source_sha256,export_sha256:sha(bytes),actual_triangles:count,actual_welded_vertices:unique.size,connected_shells:components,nonmanifold_edges:nm,euler_characteristic:chi,
 minimum_triangle_area_m2:minarea,zero_area_triangles:zero,zero_UV_triangles:uvzero,bad_normals:badnormals,signed_volume_m3:volume,source_volume_relative_delta:Math.abs(volume/src.signed_volume_m3-1),
 glTF_errors:valid.issues.numErrors,glTF_warnings:valid.issues.numWarnings,messages:valid.issues.messages,
 technical_preflight_passed:count===src.triangles&&!zero&&!uvzero&&!badnormals&&!nm&&chi===0&&components===1&&volume>0&&!valid.issues.numErrors,
 sampled20um_goal_met:src.sampled_goal_met,diagnostic_only_no_production_freeze:true,art_accepted:false};
await fs.writeFile(O+'diagnostic-export-preflight.json',JSON.stringify(r,null,2)+'\n');if(!r.technical_preflight_passed)throw Error('Diagnostic not ready to render');console.log('FRONT_TYRE_G3_DIAGNOSTIC_EXPORT',JSON.stringify(r));
