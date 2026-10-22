// Inspect actual exported primitive assignments and PBR factors, not just material declarations.
import fs from 'node:fs/promises';import crypto from 'node:crypto';import{NodeIO}from'@gltf-transform/core';
const n=process.argv[2],H='assets-src/moto-components/'+n,O='creative/reviews/'+n,P=JSON.parse(await fs.readFile(H+'/parameters.json','utf8')),path=H+'/child-candidate.glb',bytes=await fs.readFile(path),root=(await new NodeIO().read(path)).getRoot(),rows=[];
for(const mesh of root.listMeshes()){
 const region=P.material_regions[mesh.getName()];if(!region)throw Error('Unassigned region '+mesh.getName());
 for(const prim of mesh.listPrimitives()){
  const m=prim.getMaterial();if(!m)throw Error('No actual primitive material');const actual={name:m.getName(),base_color_linear:m.getBaseColorFactor(),metallic:m.getMetallicFactor(),roughness:m.getRoughnessFactor()};
  if(actual.name!==region.name||actual.base_color_linear.some((x,i)=>Math.abs(x-region.base_color_linear[i])>1e-6)||Math.abs(actual.metallic-region.metallic)>1e-6||Math.abs(actual.roughness-region.roughness)>1e-6)throw Error(JSON.stringify({actual,expected:region}));
  rows.push({mesh:mesh.getName(),triangles:prim.getIndices().getCount()/3,actual,expected:region});
 }
}
if(rows.length!==Object.keys(P.material_regions).length)throw Error('Region count');const report={path,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),actual_export_material_regions:rows,scope:'Actual PBR assignment only, not measured physical material fidelity',art_accepted:false};await fs.writeFile(O+'/actual-material-regions-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
