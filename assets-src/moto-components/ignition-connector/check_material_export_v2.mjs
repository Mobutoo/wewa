import fs from 'node:fs/promises';
import{createHash}from'node:crypto';
import{NodeIO}from'@gltf-transform/core';
const H='assets-src/moto-components/ignition-connector/',O='creative/reviews/ignition-connector-v2/';
const hash=x=>createHash('sha256').update(x).digest('hex');
const a=(await new NodeIO().read(H+'ignition-connector-v2-geometry.glb')).getRoot();
const b=(await new NodeIO().read(H+'ignition-connector-v2-inspection.glb')).getRoot();
const A=a.listMeshes()[0].listPrimitives()[0],B=b.listMeshes()[0].listPrimitives()[0];
const rows=[];
for(const semantic of [...new Set([...A.listSemantics(),...B.listSemantics()]),'indices']){
 const x=semantic==='indices'?A.getIndices():A.getAttribute(semantic),y=semantic==='indices'?B.getIndices():B.getAttribute(semantic);
 if(!x||!y)throw Error('Missing protected attribute '+semantic);
 const u=x.getArray(),v=y.getArray(),p=Buffer.from(u.buffer,u.byteOffset,u.byteLength),q=Buffer.from(v.buffer,v.byteOffset,v.byteLength);
 if(!p.equals(q))throw Error('Changed protected bytes '+semantic);rows.push({semantic,actual_native_bytes_identical:true,sha256:hash(p)});
}
const matrices=[];for(const node of a.listNodes()){
 const other=b.listNodes().find(q=>q.getName()===node.getName());if(!other||JSON.stringify(node.getWorldMatrix())!==JSON.stringify(other.getWorldMatrix()))throw Error('Changed matrix '+node.getName());matrices.push({node:node.getName(),actual_world_matrix_identical:true});
}
const report=JSON.parse(await fs.readFile(H+'build-report-v2.json','utf8'));
if(hash(await fs.readFile(H+'ignition-connector-v2-inspection.glb'))!==report.export_sha256)throw Error('SHA');
if(b.listTextures().length||B.getMaterial().getNormalTexture())throw Error('Unexpected texture');
await fs.writeFile(O+'protected-material-export-v2.json',JSON.stringify({source_sha256:report.source_sha256,export_sha256:report.export_sha256,geometry_source_sha256:report.geometry_source_sha256,attributes:rows,matrices,texture_images:0,normalmap_used:false,native_tangents_repaired:false,scope:'Material-only transition from geometryv2. Local mesh, all native attributes and world matrices protected. Constant dark polymer proposal, not measured grain or chemistry.',art_accepted:false},null,2)+'\n');
console.log('CONNECTOR_MATERIAL_NATIVE_PROTECTED',rows.length,matrices.length);
