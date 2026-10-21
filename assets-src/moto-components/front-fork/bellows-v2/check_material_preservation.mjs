import fs from 'node:fs/promises';import{createHash}from'node:crypto';import{NodeIO}from'@gltf-transform/core';
const baseline='/workspace/wewa-assets/work-in-progress/fork-bellows-v2/g3/fork-bellows-v2-inspection.glb',current='assets-src/moto-components/front-fork/bellows-v2/fork-bellows-v2-inspection.glb';
const [a,b]=await Promise.all([new NodeIO().read(baseline),new NodeIO().read(current)]),p=a.getRoot().listMeshes()[0].listPrimitives()[0],q=b.getRoot().listMeshes()[0].listPrimitives()[0],rows=[];
function same(label,x,y){if(!x||!y||x.length!==y.length)throw Error('Length '+label);let differences=0;for(let i=0;i<x.length;i++)if(x[i]!==y[i])differences++;if(differences)throw Error('Material altered '+label);rows.push({label,scalars:x.length,differences});}
same('indices',p.getIndices().getArray(),q.getIndices().getArray());
for(const s of p.listSemantics())same('base '+s,p.getAttribute(s).getArray(),q.getAttribute(s).getArray());
for(let i=0;i<2;i++)for(const s of p.listTargets()[i].listSemantics())same('morph'+i+' '+s,p.listTargets()[i].getAttribute(s).getArray(),q.listTargets()[i].getAttribute(s).getArray());
same('world matrix',a.getRoot().listNodes().find(n=>n.getMesh()).getWorldMatrix(),b.getRoot().listNodes().find(n=>n.getMesh()).getWorldMatrix());
const sha=async f=>createHash('sha256').update(await fs.readFile(f)).digest('hex');
const r={baseline,baseline_sha256:await sha(baseline),current,current_sha256:await sha(current),actual_buffer_comparisons:rows,geometry_normals_UV_baseTangentW_allMorphDeltas_and_transforms_identical:true};
await fs.writeFile('creative/reviews/fork-bellows-v2/material-preservation-check.json',JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify(r));
