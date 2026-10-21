// Read actual surface buffers and material-only transport; never certify fit/art.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import validator from 'gltf-validator';
const component=process.argv[2],grayOnly=process.argv.includes('--gray-only');
const configs={'right-stalk':['indicators-front/right-stalk','indicator-front-right-stalk-v1'],
 'seat-damper':['seat-damper','seat-damper-v1']};
if(!configs[component])throw Error('Unknown surface');
const [folder,revision]=configs[component],base='assets-src/moto-components/'+folder,review='creative/reviews/'+revision;
const hash=b=>createHash('sha256').update(b).digest('hex');
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS);
const reports=[];
const names=[revision.replace('-v1','-study-v1'),...(grayOnly?[]:[revision])];
for(const name of names){
 const path=base+'/'+name+'.glb',bytes=await fs.readFile(path);
 const validated=await validator.validateBytes(new Uint8Array(bytes),{uri:path,maxIssues:100});
 if(validated.issues.numErrors)throw Error(JSON.stringify(validated.issues));
 const root=(await io.readBinary(bytes)).getRoot();let triangles=0,minArea=Infinity,minDot=1,minUV=Infinity,maxNormalError=0;
 const signatures=[],edgeCounts=new Map(),positions=new Map();let nextPosition=0;
 const number=(a,b)=>a<b?a+','+b:b+','+a;
 for(const mesh of root.listMeshes())for(const primitive of mesh.listPrimitives()){
  const p=primitive.getAttribute('POSITION'),n=primitive.getAttribute('NORMAL'),uv=primitive.getAttribute('TEXCOORD_0'),idx=primitive.getIndices();
  if(!p||!n||!uv||!idx)throw Error('Missing actual surface buffer');
  const signature={};
  for(const [key,accessor]of[['P',p],['N',n],['UV',uv],['I',idx]]){
   const a=accessor.getArray();if([...a].some(x=>!Number.isFinite(x)))throw Error('Nonfinite actual accessor');
   signature[key]=hash(Buffer.from(a.buffer,a.byteOffset,a.byteLength));
  }
  signatures.push(signature);
  for(let i=0;i<n.getCount();i++)maxNormalError=Math.max(maxNormalError,Math.abs(Math.hypot(...n.getElement(i,[]))-1));
  for(let k=0;k<idx.getCount();k+=3){
   const ids=[0,1,2].map(i=>idx.getScalar(k+i)),v=ids.map(i=>p.getElement(i,[]));
   const [a,b,c]=v,u=b.map((x,i)=>x-a[i]),w=c.map((x,i)=>x-a[i]);
   const cross=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]],len=Math.hypot(...cross);
   if(!(len>0))throw Error('Collapsed exported triangle');minArea=Math.min(minArea,len/2);triangles++;
   for(const id of ids)minDot=Math.min(minDot,n.getElement(id,[]).reduce((sum,x,i)=>sum+x*cross[i]/len,0));
   const [A,B,C]=ids.map(i=>uv.getElement(i,[]));
   const uvArea=Math.abs((B[0]-A[0])*(C[1]-A[1])-(B[1]-A[1])*(C[0]-A[0]))/2;
   if(!(uvArea>0))throw Error('Collapsed actual UV triangle');minUV=Math.min(minUV,uvArea);
   const actual=v.map(q=>{const key=q.join(',');if(!positions.has(key))positions.set(key,nextPosition++);return positions.get(key);});
   for(let i=0;i<3;i++){const key=number(actual[i],actual[(i+1)%3]);edgeCounts.set(key,(edgeCounts.get(key)||0)+1);}
  }
 }
 if(minDot<.9||maxNormalError>.001)throw Error(JSON.stringify({minDot,maxNormalError}));
 const graph=new Map();
 for(const [key,count]of edgeCounts){
  if(count!==1&&count!==2)throw Error('Nonmanifold welded export edge');
  if(count===1){const [a,b]=key.split(',').map(Number);for(const[x,y]of[[a,b],[b,a]]){if(!graph.has(x))graph.set(x,new Set());graph.get(x).add(y);}}
 }
 if([...graph.values()].some(s=>s.size!==2))throw Error('Broken boundary ring');
 const unseen=new Set(graph.keys()),loops=[];
 while(unseen.size){const first=unseen.values().next().value;unseen.delete(first);const stack=[first];let count=0;
  while(stack.length){const n=stack.pop();count++;for(const k of graph.get(n)){if(unseen.delete(k))stack.push(k);}}
  loops.push(count);
 }
 const sourceGeometry=JSON.parse(await fs.readFile(review+'/geometry-build-report.json'));
 if(JSON.stringify(loops.sort((a,b)=>a-b))!==JSON.stringify([...sourceGeometry.boundary_loops].sort((a,b)=>a-b)))throw Error('Changed actual open cuts');
 reports.push({path,sha256:hash(bytes),triangles,minimum_actual_triangle_area_m2:minArea,
  minimum_actual_face_corner_normal_dot:minDot,minimum_actual_UV_area:minUV,max_normal_unit_error:maxNormalError,
  boundary_loops:loops,accessor_signatures:signatures,node_matrices:root.listNodes().map(n=>({name:n.getName(),matrix:n.getMatrix()})),
  glTF_errors:validated.issues.numErrors,glTF_warnings:validated.issues.numWarnings,
  materials:root.listMaterials().map(m=>({name:m.getName(),basecolor:m.getBaseColorFactor(),metallic:m.getMetallicFactor(),roughness:m.getRoughnessFactor()}))});
}
if(!grayOnly&&JSON.stringify([reports[0].accessor_signatures,reports[0].node_matrices])!==JSON.stringify([reports[1].accessor_signatures,reports[1].node_matrices]))throw Error('Material stage changed actual geometry/node buffers');
const report={schema:1,component,revision,reports,gray_to_material_geometry_and_nodes_identical:!grayOnly,
 scope:'Actual exported buffers, two intentional boundary rings and format; no global intersections, installed fit, optical parity or art acceptance.',art_accepted:false};
await fs.writeFile(review+'/'+(grayOnly?'gray-export-check.json':'material-transfer-check.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({component,grayOnly,triangles:reports.at(-1).triangles,boundary_loops:reports.at(-1).boundary_loops,glTF_errors:0,glTF_warnings:reports.at(-1).glTF_warnings}));
