import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {getBounds} from '@gltf-transform/functions';
import validator from 'gltf-validator';
const folder='assets-src/moto-components/handlebar/',file=folder+'handlebar-inspection.glb';
const bytes=await fs.readFile(file),valid=await validator.validateBytes(new Uint8Array(bytes),{uri:file});
const root=(await new NodeIO().read(file)).getRoot(),bounds=getBounds(root.getDefaultScene());
const source=JSON.parse(await fs.readFile('creative/reviews/handlebar-v1/source-geometry-check.json','utf8'));
const sub=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
function ray(origin,dir,a,b,c){const e1=sub(b,a),e2=sub(c,a),p=cross(dir,e2),det=dot(e1,p);if(Math.abs(det)<1e-14)return false;const inv=1/det,t=sub(origin,a),u=dot(t,p)*inv;if(u<0||u>1)return false;const q=cross(t,e1),v=dot(dir,q)*inv;if(v<0||u+v>1)return false;const length=dot(e2,q)*inv;return length>=0&&length<=.015;}
const conv=v=>[v[0],v[2],-v[1]],probes={};
for(const [name,p] of Object.entries(source.end_probes)){
 const dir=conv(p.inward_axis),centre=conv(p.centre_m),origin=centre.map((v,i)=>v-dir[i]*.003);
 probes[name+'-lumen']={origin,dir,hits:0};probes[name+'-wall']={origin:origin.map((v,i)=>v+(i===1?.0101:0)),dir,hits:0};
}
let volume=0,triangles=0;
for(const node of root.listNodes().filter(n=>n.getMesh()))for(const primitive of node.getMesh().listPrimitives()){
 const world=node.getWorldMatrix(),pos=primitive.getAttribute('POSITION'),ix=primitive.getIndices();triangles+=ix.getCount()/3;
 const transform=v=>{const [x,y,z]=v;v[0]=world[0]*x+world[4]*y+world[8]*z+world[12];v[1]=world[1]*x+world[5]*y+world[9]*z+world[13];v[2]=world[2]*x+world[6]*y+world[10]*z+world[14];};
 const a=[],b=[],c=[];
 for(let i=0;i<ix.getCount();i+=3){pos.getElement(ix.getScalar(i),a);pos.getElement(ix.getScalar(i+1),b);pos.getElement(ix.getScalar(i+2),c);transform(a);transform(b);transform(c);volume+=dot(a,cross(b,c))/6;for(const p of Object.values(probes))if(ray(p.origin,p.dir,a,b,c))p.hits++;}
}
const report={file,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex'),glTF_errors:valid.issues.numErrors,glTF_warnings:valid.issues.numWarnings,messages:valid.issues.messages,bounds,triangles,signed_wall_volume_m3:volume,source_volume_relative_difference:Math.abs(volume/source.signed_wall_volume_m3-1),end_probes:probes,materials:root.listMaterials().map(m=>({name:m.getName(),metallic:m.getMetallicFactor(),roughness:m.getRoughnessFactor()})),physical_iphone_tested:false,art_accepted:false};
if(report.glTF_errors||volume<=0||report.source_volume_relative_difference>1e-5||Math.abs(bounds.max[0]-.3443795)>1e-5||Object.entries(probes).some(([k,v])=>k.endsWith('lumen')?v.hits!==0:v.hits===0))throw Error(JSON.stringify(report));
report.technical_passed=true;await fs.writeFile('creative/reviews/handlebar-v1/geometry-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
