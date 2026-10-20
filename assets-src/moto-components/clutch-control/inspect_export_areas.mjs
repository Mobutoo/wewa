import fs from'node:fs/promises';import{NodeIO}from'@gltf-transform/core';import{createHash}from'node:crypto';
for(const folder of process.argv.slice(2)){
 const path=`assets-src/moto-components/${folder}/${folder}-inspection.glb`,root=(await new NodeIO().read(path)).getRoot(),rows=[];
 for(const mesh of root.listMeshes()){
  let triangles=0,zero=0,repeated=0,collinear=0,minimumPositive=Infinity;const examples=[];
  for(const primitive of mesh.listPrimitives()){
   const p=primitive.getAttribute('POSITION'),ix=primitive.getIndices();
   for(let j=0;j<ix.getCount();j+=3){triangles++;const[a,b,c]=[0,1,2].map(k=>p.getElement(ix.getScalar(j+k),[]));const u=b.map((v,k)=>v-a[k]),v=c.map((x,k)=>x-a[k]);const area=.5*Math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);
    if(area===0){zero++;const same=(x,y)=>x.every((v,k)=>v===y[k]);if(same(a,b)||same(b,c)||same(a,c))repeated++;else collinear++;if(examples.length<2)examples.push({indices:[0,1,2].map(k=>ix.getScalar(j+k)),positions:[a,b,c]});}else minimumPositive=Math.min(minimumPositive,area);
   }
  }
  rows.push({mesh:mesh.getName(),triangles,zero,repeated,collinear,minimumPositive,examples});
 }
 const report={path,sha256:createHash('sha256').update(await fs.readFile(path)).digest('hex'),rows,zeroAreaTriangles:rows.reduce((n,r)=>n+r.zero,0)};await fs.mkdir('/workspace/wewa-assets/work-in-progress/area-audits',{recursive:true});await fs.writeFile(`/workspace/wewa-assets/work-in-progress/area-audits/${folder}.json`,JSON.stringify(report,null,2)+'\n');
 if(['ignition-lock','cockpit-cables'].includes(folder))await fs.writeFile(`creative/reviews/${folder}-v1/export-area-check.json`,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}
