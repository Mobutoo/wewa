// Preserve geometry and skinning while making Blender's review colour factor explicit in glTF.
// Use after glTF Transform resize/webp; no app asset is overwritten.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import validator from 'gltf-validator';
const [input,output]=process.argv.slice(2);
if(!input||!output)throw new Error('Usage: node tools/prepare_hero_review.mjs input.glb output.glb');
const bytes=await fs.readFile(input);
if(bytes.readUInt32LE(0)!==0x46546c67||bytes.readUInt32LE(4)!==2)throw new Error('Expected glTF2 binary');
const jsonLength=bytes.readUInt32LE(12),document=JSON.parse(bytes.subarray(20,20+jsonLength).toString());
// Blender can emit a zero tangent at a UV-degenerate cap vertex. Give that vertex
// an orthonormal fallback; its UV has no defined tangent direction. Do not suppress
// the validator or discard the normal map for all the other, well-defined vertices.
const binaryStart=28+jsonLength;let repairedTangents=0;
function address(accessorIndex,index){const accessor=document.accessors[accessorIndex],view=document.bufferViews[accessor.bufferView];if(accessor.componentType!==5126)throw Error('Expected float vertex attribute');return binaryStart+(view.byteOffset??0)+(accessor.byteOffset??0)+index*(view.byteStride??(accessor.type==='VEC4'?16:12));}
for(const mesh of document.meshes??[])for(const primitive of mesh.primitives){
 const ti=primitive.attributes?.TANGENT,ni=primitive.attributes?.NORMAL;if(ti===undefined||ni===undefined)continue;
 const accessor=document.accessors[ti];
 for(let i=0;i<accessor.count;i++){
  const offset=address(ti,i);let vector=[0,1,2].map(k=>bytes.readFloatLE(offset+k*4));const length=Math.hypot(...vector);if(length>1e-8)continue;
  const no=address(ni,i),n=[0,1,2].map(k=>bytes.readFloatLE(no+k*4));
  const axis=Math.abs(n[0])<.9?[1,0,0]:[0,1,0];vector=[n[1]*axis[2]-n[2]*axis[1],n[2]*axis[0]-n[0]*axis[2],n[0]*axis[1]-n[1]*axis[0]];
  const size=Math.hypot(...vector);if(size<1e-8)throw Error('Invalid normal at degenerate tangent');
  vector.forEach((value,k)=>bytes.writeFloatLE(value/size,offset+k*4));repairedTangents++;
 }
}
for(const material of document.materials??[]){
 if(material.name==='male_casualsuit05')material.pbrMetallicRoughness.baseColorFactor=[.15,.21,.29,1];
}
const encoded=Buffer.from(JSON.stringify(document)),padded=Buffer.alloc(Math.ceil(encoded.length/4)*4,0x20);encoded.copy(padded);
const rest=bytes.subarray(20+jsonLength),header=Buffer.alloc(20);header.writeUInt32LE(0x46546c67);header.writeUInt32LE(2,4);header.writeUInt32LE(20+padded.length+rest.length,8);header.writeUInt32LE(padded.length,12);header.writeUInt32LE(0x4e4f534a,16);
const result=Buffer.concat([header,padded,rest]);await fs.writeFile(output,result);
const report=await validator.validateBytes(new Uint8Array(result),{uri:output,maxIssues:100});
const summary={file:output,bytes:result.length,sha256:crypto.createHash('sha256').update(result).digest('hex'),repaired_degenerate_tangents:repairedTangents,errors:report.issues.numErrors,warnings:report.issues.numWarnings,issues:report.issues.messages,skins:document.skins?.map(s=>({joints:s.joints.length})),animations:document.animations?.map(a=>a.name),art_accepted:false,physical_iphone_tested:false};
await fs.writeFile(output.replace(/\.glb$/,'.validation.json'),JSON.stringify(summary,null,2)+'\n');console.log(JSON.stringify(summary));
if(report.issues.numErrors)process.exitCode=1;
