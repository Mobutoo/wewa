// Actual buffers before/after the temporary exporter correction; no buffer edits.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
const oldFile='/workspace/wewa-assets/work-in-progress/fork-bellows/native-morph-tangent-rejected/fork-bellows-inspection.glb';
const newFile='assets-src/moto-components/front-fork/bellows/fork-bellows-inspection.glb';
const [a,b]=await Promise.all([new NodeIO().read(oldFile),new NodeIO().read(newFile)]);
const rows=[];
function identical(label,x,y){if(!x||!y||x.length!==y.length)throw Error('Different length '+label);let changed=0;for(let i=0;i<x.length;i++)if(x[i]!==y[i])changed++;if(changed)throw Error(label+' changed '+changed);rows.push({attribute:label,scalars:x.length,changed_scalars:changed});}
const aa=a.getRoot().listMeshes(),bb=b.getRoot().listMeshes();if(aa.length!==bb.length)throw Error('Meshes differ');
let tangentChanges=[];
for(let m=0;m<aa.length;m++)for(let k=0;k<aa[m].listPrimitives().length;k++){
 const p=aa[m].listPrimitives()[k],q=bb[m].listPrimitives()[k];
 identical('indices',p.getIndices().getArray(),q.getIndices().getArray());
 for(const semantic of p.listSemantics())identical('base '+semantic,p.getAttribute(semantic).getArray(),q.getAttribute(semantic).getArray());
 for(let i=0;i<p.listTargets().length;i++)for(const semantic of p.listTargets()[i].listSemantics()){
  const x=p.listTargets()[i].getAttribute(semantic).getArray(),y=q.listTargets()[i].getAttribute(semantic).getArray();
  if(semantic!=='TANGENT')identical('morph'+i+' '+semantic,x,y);
  else {let changed=0,maxDifference=0;for(let j=0;j<x.length;j++){if(x[j]!==y[j])changed++;maxDifference=Math.max(maxDifference,Math.abs(x[j]-y[j]));}if(!changed)throw Error('No tangent correction');tangentChanges.push({target:i,changed_scalars:changed,max_abs_delta_difference:maxDifference});}
 }
}
const sha=async p=>createHash('sha256').update(await fs.readFile(p)).digest('hex');
const report={before_file:oldFile,before_sha256:await sha(oldFile),after_file:newFile,after_sha256:await sha(newFile),identical_buffers:rows,changed_morph_tangent_buffers:tangentChanges,geometry_baseNormals_UV_baseTangentsIncludingW_morphPosition_morphNormal_identical:true,post_export_buffer_editing:false};
await fs.writeFile('creative/reviews/fork-bellows-v1/converter-preservation-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
