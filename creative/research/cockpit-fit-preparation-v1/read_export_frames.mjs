// Read existing export node transforms/positions; no scene mutation or GLB writes.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {NodeIO} from '@gltf-transform/core';
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../../..');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const snapshot=JSON.parse(fs.readFileSync(path.join(here,'input-snapshot.json'),'utf8'));
const rows=[];
for(const entry of snapshot.entries.filter(e=>e.scope==='catalog_shared_cockpit')) {
  const exported=entry.exports[0],input=path.join(root,exported.path);
  if(sha(input)!==exported.sha256)throw Error('Changed export '+input);
  const doc=await new NodeIO().read(input),low=[Infinity,Infinity,Infinity],high=[-Infinity,-Infinity,-Infinity],nodes=[];
  for(const node of doc.getRoot().listNodes()){
    const mesh=node.getMesh();if(!mesh)continue;
    const m=node.getWorldMatrix(),nlow=[Infinity,Infinity,Infinity],nhigh=[-Infinity,-Infinity,-Infinity];let vertices=0;
    for(const primitive of mesh.listPrimitives()) {
      const p=primitive.getAttribute('POSITION');if(!p)continue;vertices+=p.getCount();
      const xyz=[];
      for(let i=0;i<p.getCount();i++){
        p.getElement(i,xyz);const [x,y,z]=xyz;
        const q=[x*m[0]+y*m[4]+z*m[8]+m[12],x*m[1]+y*m[5]+z*m[9]+m[13],x*m[2]+y*m[6]+z*m[10]+m[14]];
        for(let k=0;k<3;k++){nlow[k]=Math.min(nlow[k],q[k]);nhigh[k]=Math.max(nhigh[k],q[k]);low[k]=Math.min(low[k],q[k]);high[k]=Math.max(high[k],q[k]);}
      }
    }
    nodes.push({node:node.getName(),parent:node.getParentNode()?.getName()??null,world_matrix_column_major:Array.from(m),vertices,bounds_glTF_m:{min:nlow,max:nhigh}});
  }
  rows.push({key:entry.key,path:exported.path,sha256:sha(input),world_bounds_glTF_m:{min:low,max:high},nodes});
}
const out=path.join(here,'export-frames.json');if(fs.existsSync(out))throw Error('Refuse overwrite');
fs.writeFileSync(out,JSON.stringify({schema:'wewa.cockpit-readonly-export-frames.v1',tool_sha256:sha(fileURLToPath(import.meta.url)),input_snapshot_sha256:sha(path.join(here,'input-snapshot.json')),exports_modified:false,entries:rows},null,2)+'\n');
console.log(JSON.stringify({exports:rows.length,GLBs_written:0}));
