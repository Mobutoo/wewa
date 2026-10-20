import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {getBounds} from '@gltf-transform/functions';
import validator from 'gltf-validator';
const file='assets-src/moto-components/switchgear-left/switchgear-left-v2-inspection.glb',bytes=await fs.readFile(file);
const validation=await validator.validateBytes(new Uint8Array(bytes),{uri:file,maxIssues:50});
const root=(await new NodeIO().read(file)).getRoot(),bounds=getBounds(root.getDefaultScene());
const source=JSON.parse(await fs.readFile('creative/reviews/switchgear-left-v2/source-geometry-check.json','utf8'));
const meshes=[];let totalTriangles=0;
function world(v,m){const [x,y,z]=v;return [m[0]*x+m[4]*y+m[8]*z+m[12],m[1]*x+m[5]*y+m[9]*z+m[13],m[2]*x+m[6]*y+m[10]*z+m[14]];}
const I=source.datum.inward_axis,E=source.datum.endpoint_m;
const start=[E[0]+I[0]*.10,E[2],-E[1]-I[1]*.10],axis=[I[0],0,-I[1]];
function ray(a,b,c){
 const sub=(x,y)=>x.map((z,i)=>z-y[i]),dot=(x,y)=>x.reduce((s,z,i)=>s+z*y[i],0),cross=(x,y)=>[x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]];
 const e1=sub(b,a),e2=sub(c,a),h=cross(axis,e2),den=dot(e1,h);if(Math.abs(den)<1e-14)return false;
 const t=sub(start,a),u=dot(t,h)/den;if(u<0||u>1)return false;
 const q=cross(t,e1),v=dot(axis,q)/den;if(v<0||u+v>1)return false;
 const distance=dot(e2,q)/den;return distance>0&&distance<.09;
}
for(const node of root.listNodes().filter(n=>n.getMesh())){
 let triangles=0,volume=0,boreHits=0;
 for(const p of node.getMesh().listPrimitives()){
  const pos=p.getAttribute('POSITION'),idx=p.getIndices();triangles+=idx.getCount()/3;const wm=node.getWorldMatrix();
  for(let i=0;i<idx.getCount();i+=3){
   const points=[];for(let j=0;j<3;j++){const v=[];pos.getElement(idx.getScalar(i+j),v);points.push(world(v,wm));}
   const [a,b,c]=points;volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;
   if(node.getName().includes('shell - editable')&&ray(a,b,c))boreHits++;
  }
 }
 totalTriangles+=triangles;const entry={name:node.getName(),triangles,signed_volume_m3:volume,bar_axis_ray_hits:node.getName().includes('shell - editable')?boreHits:null};meshes.push(entry);
 if(source.checks.some(c=>c.object===entry.name)&&volume<=0)throw Error('Nonpositive exported rigid volume '+JSON.stringify(entry));
 if(boreHits)throw Error('Exported tube passage obstructed '+JSON.stringify(entry));
}
const material=root.listMaterials().find(m=>m.getName()==='LH moulded black polymer - candidate');
if(!material?.getMetallicRoughnessTexture())throw Error('Missing authored PBR map');
const map=material.getMetallicRoughnessTexture(),original=await fs.readFile('assets-src/moto-components/switchgear-left/textures/plastic-metallic-roughness.png');
const embeddedHash=createHash('sha256').update(map.getImage()).digest('hex'),sourceHash=createHash('sha256').update(original).digest('hex');if(embeddedHash!==sourceHash)throw Error('PBR bytes changed');
const normalMap=material.getNormalTexture();if(!normalMap)throw Error('Original polymer normal missing');
const normalBytes=await fs.readFile('assets-src/moto-components/switchgear-left/textures/plastic-normal.png');
const normalHash=createHash('sha256').update(normalMap.getImage()).digest('hex');if(normalHash!==createHash('sha256').update(normalBytes).digest('hex'))throw Error('Normal texture changed');
for(const node of root.listNodes().filter(n=>n.getMesh()))for(const primitive of node.getMesh().listPrimitives())if(primitive.getMaterial()===material&&!primitive.getAttribute('TANGENT'))throw Error('Tangent missing on polymer');
const report={file,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length,glTF_errors:validation.issues.numErrors,glTF_warnings:validation.issues.numWarnings,messages:validation.issues.messages,bounds,total_triangles:totalTriangles,meshes,material_map_bytes_identical:true,normal_map_bytes_identical:true,normal_map_sha256:normalHash,polymer_tangent_buffers_present:true,material_map_sha256:sourceHash,scope:'Actual exported buffers/world node transforms; related switch candidate, no current RDC identity or functional electrical qualification',physical_iphone_tested:false,art_accepted:false};
if(validation.issues.numErrors||bounds.min[0]<.15||bounds.max[0]>.27||bounds.max[1]>.15||bounds.min[1]<.04)throw Error(JSON.stringify(report));
await fs.writeFile('creative/reviews/switchgear-left-v2/geometry-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
