// Drop only unused TANGENT attributes. Preserve every GLB binary byte and all
// other JSON values. Never recompute positions, UVs, normals or mapped tangents.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
const [input,output,reportPath]=process.argv.slice(2);
if(!reportPath||input===output)throw Error('Pass distinct INPUT OUTPUT and REPORT paths');
const sha=b=>createHash('sha256').update(b).digest('hex'),bytes=await fs.readFile(input);
if(bytes.readUInt32LE(0)!==0x46546c67||bytes.readUInt32LE(4)!==2||bytes.readUInt32LE(16)!==0x4e4f534a)throw Error('Expected binary glTF2 with JSON first');
const jsonLength=bytes.readUInt32LE(12),original=JSON.parse(bytes.subarray(20,20+jsonLength).toString()),doc=structuredClone(original),removed=[];
for(const [mi,mesh]of doc.meshes.entries())for(const [pi,p]of mesh.primitives.entries()){
 const m=doc.materials?.[p.material];
 const needsTangent=m?.normalTexture||m?.extensions?.KHR_materials_clearcoat?.clearcoatNormalTexture;
 if(!needsTangent&&p.attributes.TANGENT!==undefined){removed.push({mesh:mi,primitive:pi,accessor:p.attributes.TANGENT});delete p.attributes.TANGENT;}
}
const restored=structuredClone(doc);for(const r of removed)restored.meshes[r.mesh].primitives[r.primitive].attributes.TANGENT=r.accessor;
const sorted=v=>Array.isArray(v)?v.map(sorted):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,sorted(v[k])])):v;
if(JSON.stringify(sorted(original))!==JSON.stringify(sorted(restored)))throw Error('Unexpected JSON mutation');
const encoded=Buffer.from(JSON.stringify(doc)),padding=Buffer.alloc((4-encoded.length%4)%4,0x20),tail=bytes.subarray(20+jsonLength),head=Buffer.alloc(20);
head.writeUInt32LE(0x46546c67,0);head.writeUInt32LE(2,4);head.writeUInt32LE(20+encoded.length+padding.length+tail.length,8);head.writeUInt32LE(encoded.length+padding.length,12);head.writeUInt32LE(0x4e4f534a,16);
const result=Buffer.concat([head,encoded,padding,tail]);await fs.writeFile(output,result);
const report={input,source_sha256:sha(bytes),output,output_sha256:sha(result),removed_unused_tangent_attributes:removed,all_other_JSON_values_unchanged:true,binary_chunks_sha256:sha(tail),binary_chunks_byte_identical:true,normal_mapped_tangents_untouched:true,tool:'tools/remove_unused_review_tangents.mjs',tool_sha256:sha(await fs.readFile(new URL(import.meta.url))),scope:'Export attributes only; not a geometry, appearance, fit or artistic validation.'};
await fs.writeFile(reportPath,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({removed:removed.length,binary_chunks_unchanged:true,output}));
