import fs from 'node:fs/promises';
import {NodeIO} from '@gltf-transform/core';
import {createHash} from 'node:crypto';
const H='assets-src/moto-components/cockpit-cables',O='creative/reviews/cockpit-cables-v3';
const io=new NodeIO(),old=(await io.read(H+'/cockpit-cables-v2-inspection.glb')).getRoot(),now=(await io.read(H+'/cockpit-cables-v3-inspection.glb')).getRoot();
const b=JSON.parse(await fs.readFile(H+'/build-report-v3.json','utf8'));
const raw=a=>Buffer.from(a.buffer,a.byteOffset,a.byteLength),rows=[];
for(const name of Object.keys(b.protected_lower_source_signatures)){
  const a=old.listNodes().find(n=>n.getName()===name),c=now.listNodes().find(n=>n.getName()===name);
  if(!a||!c||JSON.stringify(a.getWorldMatrix())!==JSON.stringify(c.getWorldMatrix()))throw Error('Lower node/matrix mismatch '+name);
  const x=a.getMesh().listPrimitives()[0],y=c.getMesh().listPrimitives()[0],attrs=[];
  for(const semantic of ['POSITION','NORMAL','TEXCOORD_0','indices']){
    const u=semantic==='indices'?x.getIndices():x.getAttribute(semantic),v=semantic==='indices'?y.getIndices():y.getAttribute(semantic);
    if(!u&&!v)continue;
    if(!u||!v||!raw(u.getArray()).equals(raw(v.getArray())))throw Error('Protected lower attribute changed '+name+' '+semantic);
    attrs.push({semantic,actual_native_bytes_identical:true,sha256:createHash('sha256').update(raw(v.getArray())).digest('hex')});
  }
  const ma=x.getMaterial(),mc=y.getMaterial();
  if(JSON.stringify([ma.getBaseColorFactor(),ma.getMetallicFactor(),ma.getRoughnessFactor()])!==JSON.stringify([mc.getBaseColorFactor(),mc.getMetallicFactor(),mc.getRoughnessFactor()]))throw Error('Lower material changed');
  rows.push({object:name,world_matrix_identical:true,material_constants_identical:true,attributes:attrs});
}
if(rows.length!==2||now.listTextures().length)throw Error('Unexpected protected scope/images');
const report={source_sha256:b.source_sha256,export_sha256:b.export_sha256,protected_lower_objects:rows,normalmap_used:false,actual_images:0,native_tangents_repaired:false,scope:'Only distal ignition pigtail changed; two lower sheath native attributes/material/matrices literally protected. No claim that unknown lower functions/fullroutes became resolved.',art_accepted:false};
await fs.writeFile(O+'/protected-export-invariants.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
