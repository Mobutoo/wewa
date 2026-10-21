// Read-only actual exported world geometry, documentary camera exploration only.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
const file='assets-src/moto-components/headlamp/cowl/headlamp-cowl-shell-study-v13.glb';
const bytes=await fs.readFile(file);
const root=(await new NodeIO().registerExtensions(ALL_EXTENSIONS).readBinary(bytes)).getRoot();
const points=[];
for(const node of root.listNodes()) {
 if(!node.getMesh()) continue;
 const m=node.getWorldMatrix();
 for(const primitive of node.getMesh().listPrimitives()) {
  const p=primitive.getAttribute('POSITION');
  for(let i=0;i<p.getCount();i++) {
   const [x,y,z]=p.getElement(i,[]);
   const world=[m[0]*x+m[4]*y+m[8]*z+m[12],m[1]*x+m[5]*y+m[9]*z+m[13],m[2]*x+m[6]*y+m[10]*z+m[14]];
   points.push([world[0],-world[2],world[1]]);
  }
 }
}
await fs.writeFile(process.argv[2],JSON.stringify({file,sha256:createHash('sha256').update(bytes).digest('hex'),frame:'Blender+XriderLEFT,+Yrear,+Zup; actualglTFworld inverted(x,-z,y)',points}));
console.log(points.length,'actual points');
