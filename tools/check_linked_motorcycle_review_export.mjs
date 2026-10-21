// Actual buffers of a linked review export, independently of source counters.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {getBounds} from '@gltf-transform/functions';
import validator from 'gltf-validator';

const proof=process.argv[2];if(!proof)throw Error('Pass the linked source-geometry-check.json');
const sha=b=>createHash('sha256').update(b).digest('hex');
const proofBytes=await fs.readFile(proof),source=JSON.parse(proofBytes);
if(source.kind!=='linked_review_assembly_not_gameplay_or_installed_certification')throw Error('Not a linked review');
if(source.editable_source&&sha(await fs.readFile(source.editable_source))!==source.source_sha256)throw Error('Changed editable assembly');
for(const row of source.linked_sources)if(sha(await fs.readFile(row.source))!==row.sha256)throw Error('Changed library '+row.asset);
const file=source.inspection_export.path,bytes=await fs.readFile(file);
if(sha(bytes)!==source.inspection_export.sha256)throw Error('Changed review GLB');
const format=await validator.validateBytes(new Uint8Array(bytes),{uri:file,maxIssues:50});
const root=(await new NodeIO().registerExtensions(ALL_EXTENSIONS).read(file)).getRoot();
let vertices=0,triangles=0,zeroArea=0,collapsedUV=0,normalMapped=0,maxNormalError=0,maxTangentDot=0,maxTangentError=0;
for(const mesh of root.listMeshes())for(const primitive of mesh.listPrimitives()){
 const p=primitive.getAttribute('POSITION'),n=primitive.getAttribute('NORMAL'),t=primitive.getAttribute('TANGENT');
 if(!p||!n)throw Error('Missing position/normal');
 vertices+=p.getCount();const ids=primitive.getIndices()?.getArray(),count=ids?.length||p.getCount();triangles+=count/3;
 for(const a of [p,n,t].filter(Boolean))if([...a.getArray()].some(v=>!Number.isFinite(v)))throw Error('Nonfinite buffer');
 for(let i=0;i<n.getCount();i++)maxNormalError=Math.max(maxNormalError,Math.abs(Math.hypot(...n.getElement(i,[]))-1));
 if(t)for(let i=0;i<t.getCount();i++){
  const tv=t.getElement(i,[]),nv=n.getElement(i,[]);
  if(Math.abs(Math.abs(tv[3])-1)>.001)throw Error('Invalid tangent sign');
  maxTangentError=Math.max(maxTangentError,Math.abs(Math.hypot(...tv.slice(0,3))-1));
  maxTangentDot=Math.max(maxTangentDot,Math.abs(tv.slice(0,3).reduce((s,v,k)=>s+v*nv[k],0)));
 }
 const material=primitive.getMaterial(),normalTexture=material?.getNormalTexture();
 const uv=normalTexture?primitive.getAttribute('TEXCOORD_'+(material.getNormalTextureInfo().getTexCoord()||0)):null;
 if(normalTexture){normalMapped++;if(!uv||!t)throw Error('Missing normal map UV/tangent');}
 for(let i=0;i<count;i+=3){
  const ids3=[0,1,2].map(k=>ids?ids[i+k]:i+k),[a,b,c]=ids3.map(k=>p.getElement(k,[]));
  const u=b.map((v,k)=>v-a[k]),v=c.map((x,k)=>x-a[k]);
  if(Math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])===0)zeroArea++;
  if(uv){const [a,b,c]=ids3.map(k=>uv.getElement(k,[]));if((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])===0)collapsedUV++;}
 }
}
const report={source_geometry_report:proof,source_geometry_report_sha256:sha(proofBytes),file,sha256:sha(bytes),linked_sources:source.linked_sources.length,bytes:bytes.length,glTF_errors:format.issues.numErrors,glTF_warnings:format.issues.numWarnings,messages:format.issues.messages,vertices,triangles,zero_area_triangles:zeroArea,normal_mapped_primitives:normalMapped,collapsed_uv_triangles:collapsedUV,max_normal_unit_error:maxNormalError,max_tangent_normal_dot:maxTangentDot,max_tangent_unit_error:maxTangentError,bounds:getBounds(root.getDefaultScene()),checker:'tools/check_linked_motorcycle_review_export.mjs',checker_sha256:sha(await fs.readFile(new URL(import.meta.url))),scope:'Actual linked-export buffers and library hashes; no appearance parity, mechanical fit, mobile budget or art reception.',art_accepted:false,physical_iphone_tested:false};
await fs.writeFile(path.join(path.dirname(proof),'export-buffer-check.json'),JSON.stringify(report,null,2)+'\n');
if(format.issues.numErrors||zeroArea||collapsedUV||maxNormalError>.015||maxTangentDot>.001||maxTangentError>.001)throw Error(JSON.stringify(report));
console.log(JSON.stringify({linked_sources:report.linked_sources,triangles,glTF_errors:0,zeroArea,collapsedUV}));
