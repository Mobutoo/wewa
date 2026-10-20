// Independent actual-buffer inspection. Topology/art/fit checks remain separate.
import fs from 'node:fs/promises';import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';import {ALL_EXTENSIONS} from '@gltf-transform/extensions';import {getBounds} from '@gltf-transform/functions';import validator from 'gltf-validator';
const catalog=JSON.parse(await fs.readFile('tools/motorcycle-lab/catalog.json','utf8')),asset=process.argv[2],config=catalog.assets[asset];if(!config)throw Error('Unknown actual candidate');
const exports=[];
for(const relative of config.files){
 const path='assets-src/moto-components/'+relative,bytes=await fs.readFile(path),format=await validator.validateBytes(new Uint8Array(bytes),{uri:path,maxIssues:50});
 const root=(await new NodeIO().registerExtensions(ALL_EXTENSIONS).read(path)).getRoot(),bounds=getBounds(root.getDefaultScene());let vertices=0,triangles=0,zeroAreaTriangles=0,nearZeroAreaTriangles=0,minTriangleArea=Infinity,tangentVectors=0,maxTangentNormalDot=0,maxTangentUnitError=0;
 for(const mesh of root.listMeshes())for(const primitive of mesh.listPrimitives()){
  const p=primitive.getAttribute('POSITION'),n=primitive.getAttribute('NORMAL');if(!p||!n)throw Error('Missing real position/normal buffer');vertices+=p.getCount();triangles+=(primitive.getIndices()?.getCount()||p.getCount())/3;
  if([...p.getArray(),...n.getArray()].some(x=>!Number.isFinite(x)))throw Error('Nonfinite actual buffer');
  for(let i=0;i<n.getCount();i++){const len=Math.hypot(...n.getElement(i,[]));if(Math.abs(len-1)>.015)throw Error('Nonunit exported normal');}
  const indices=primitive.getIndices()?.getArray();const count=indices?.length||p.getCount();
  for(let j=0;j<count;j+=3){
   const [a,b,c]=[0,1,2].map(k=>p.getElement(indices?indices[j+k]:j+k,[]));
   const u=b.map((v,k)=>v-a[k]),v=c.map((x,k)=>x-a[k]);
   const area=.5*Math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);
   minTriangleArea=Math.min(minTriangleArea,area);if(area===0)zeroAreaTriangles++;if(area<1e-18)nearZeroAreaTriangles++;
  }
  const t=primitive.getAttribute('TANGENT');
  if(primitive.getMaterial()?.getNormalTexture()&&!t)throw Error('Normal-mapped primitive lacks exported tangent frame');
  if(t)for(let i=0;i<t.getCount();i++){
   const tv=t.getElement(i,[]),nv=n.getElement(i,[]);tangentVectors++;
   if(tv.some(x=>!Number.isFinite(x))||Math.abs(Math.abs(tv[3])-1)>.001)throw Error('Invalid tangent buffer');
   maxTangentUnitError=Math.max(maxTangentUnitError,Math.abs(Math.hypot(...tv.slice(0,3))-1));
   maxTangentNormalDot=Math.max(maxTangentNormalDot,Math.abs(tv.slice(0,3).reduce((s,x,k)=>s+x*nv[k],0)));
  }
 }
 if(zeroAreaTriangles||maxTangentUnitError>.001||maxTangentNormalDot>.001)throw Error(JSON.stringify({path,zeroAreaTriangles,maxTangentUnitError,maxTangentNormalDot}));
 if(!vertices||!triangles||bounds.min.some(x=>!Number.isFinite(x))||bounds.max.some(x=>!Number.isFinite(x)))throw Error('Empty/invalid export');
 const nodes=root.listNodes().map(n=>n.getName());
 exports.push({path,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length,glTF_errors:format.issues.numErrors,glTF_warnings:format.issues.numWarnings,messages:format.issues.messages,bounds,vertices,triangles,triangle_area_local_m2:{minimum:minTriangleArea,exactly_zero:zeroAreaTriangles,below_1e_minus18:nearZeroAreaTriangles,note:'Local exported coordinates; not a self-intersection or surface-fidelity proof'},tangent_frame:{vectors:tangentVectors,max_unit_error:maxTangentUnitError,max_normal_dot:maxTangentNormalDot,handedness_sign_is_unit:true,note:'Finite orthonormal frame only; not full MikkTSpace or renderer visual parity'},node_names:nodes,materials:root.listMaterials().map(m=>({name:m.getName(),basecolor:m.getBaseColorFactor(),metallic:m.getMetallicFactor(),roughness:m.getRoughnessFactor(),extensions:m.listExtensions().map(e=>e.extensionName)}))});
 if(format.issues.numErrors)throw Error('Invalid glTF '+JSON.stringify(exports.at(-1)));
}
for(const rig of config.rigs||[])if(!exports.some(e=>e.node_names.includes(rig.node)))throw Error('Missing actual rig '+rig.node);
const report={asset,revision:config.review,exports,scope:'Actual glTF buffers and format only; not shape reception, physical interface or mobile qualification',art_accepted:false,physical_iphone_tested:false};
await fs.writeFile('creative/reviews/'+config.review+'/export-buffer-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({asset,exports:exports.length,triangles:exports.reduce((n,e)=>n+e.triangles,0),glTF_errors:0}));
