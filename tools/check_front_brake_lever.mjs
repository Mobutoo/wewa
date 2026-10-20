// Verify actual exported geometry, not construction objects or export success alone.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {getBounds} from '@gltf-transform/functions';
import validator from 'gltf-validator';
const file='assets-src/moto-components/front-brake-lever/front-brake-lever-inspection.glb';
const bytes=await fs.readFile(file),valid=await validator.validateBytes(new Uint8Array(bytes),{uri:file});
const root=(await new NodeIO().read(file)).getRoot(),bounds=getBounds(root.getDefaultScene());
let triangles=0,volume=0;const hits={shaft:0,eye:0,open_slot:0,blade:0};
const probes={shaft:[.105,0],eye:[.017,.0015],open_slot:[.113,0],blade:[.065,-.004]};
for(const node of root.listNodes().filter(n=>n.getMesh()))for(const primitive of node.getMesh().listPrimitives()){
 const world=node.getWorldMatrix();
 const transform=v=>{const [x,y,z]=v;v[0]=world[0]*x+world[4]*y+world[8]*z+world[12];v[1]=world[1]*x+world[5]*y+world[9]*z+world[13];v[2]=world[2]*x+world[6]*y+world[10]*z+world[14];};
 const p=primitive.getAttribute('POSITION'),ix=primitive.getIndices();triangles+=ix.getCount()/3;
 const a=[],b=[],c=[];
 for(let i=0;i<ix.getCount();i+=3){
  p.getElement(ix.getScalar(i),a);p.getElement(ix.getScalar(i+1),b);p.getElement(ix.getScalar(i+2),c);transform(a);transform(b);transform(c);
  volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;
  const den=(b[1]-c[1])*(a[2]-c[2])+(c[2]-b[2])*(a[1]-c[1]);if(Math.abs(den)<1e-18)continue;
  for(const [name,[y,z]] of Object.entries(probes)){
   const u=((b[1]-c[1])*(z-c[2])+(c[2]-b[2])*(y-c[1]))/den;
   const v=((c[1]-a[1])*(z-c[2])+(a[2]-c[2])*(y-c[1]))/den;
   if(u>=-1e-8&&v>=-1e-8&&1-u-v>=-1e-8)hits[name]++;
  }
 }
}
const material=root.listMaterials()[0];
const report={file,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length,glTF_errors:valid.issues.numErrors,glTF_warnings:valid.issues.numWarnings,messages:valid.issues.messages,bounds,triangles,signed_volume_m3:volume,axial_ray_hits:hits,material:{name:material.getName(),basecolor_texture:!!material.getBaseColorTexture(),metallic_roughness_texture:!!material.getMetallicRoughnessTexture()},scope:'Estimated isolated lever; not a dimensioned OEM reproduction or installed/functionally tested brake',art_accepted:false};

if(report.glTF_errors||volume<=0||hits.shaft||hits.eye||hits.open_slot||!hits.blade||!report.material.basecolor_texture||!report.material.metallic_roughness_texture)throw Error(JSON.stringify(report));
if(Math.abs((bounds.max[1]-bounds.min[1])-.109)>.006)throw Error('Unexpected lever scale');
report.technical_passed=true;
await fs.writeFile('creative/reviews/front-brake-lever-v1/geometry-check.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
