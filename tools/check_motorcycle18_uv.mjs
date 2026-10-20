// Inspect the actual UV triangles used by normal maps, independently of names.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
const catalog=JSON.parse(await fs.readFile('tools/motorcycle-lab/catalog.json','utf8'));
const key=process.argv[2],config=catalog.assets[key];
if(!config)throw Error('Unknown candidate '+key);
const output=process.argv[3]||`creative/reviews/${config.review}/uv-buffer-check.json`;
const checks=[];let errors=0;
for(const file of config.files){
 const path='assets-src/moto-components/'+file,bytes=await fs.readFile(path);
 const document=await new NodeIO().registerExtensions(ALL_EXTENSIONS).read(path);
 for(const mesh of document.getRoot().listMeshes())for(const primitive of mesh.listPrimitives()){
  const material=primitive.getMaterial();if(!material?.getNormalTexture())continue;
  const set=material.getNormalTextureInfo().getTexCoord(),uv=primitive.getAttribute('TEXCOORD_'+set);
  if(!uv)throw Error('Missing normal-map UV set');
  const indices=primitive.getIndices()?.getArray(),count=indices?.length||uv.getCount();
  let zero=0,near=0,min=Infinity,positive=0,negative=0;
  for(let j=0;j<count;j+=3){
   const [a,b,c]=[0,1,2].map(k=>uv.getElement(indices?indices[j+k]:j+k,[]));
   if([...a,...b,...c].some(v=>!Number.isFinite(v)))throw Error('Nonfinite actual UV');
   const determinant=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
   min=Math.min(min,Math.abs(determinant)*.5);
   if(determinant===0)zero++;if(Math.abs(determinant)*.5<1e-14)near++;
   if(determinant>0)positive++;if(determinant<0)negative++;
  }
  errors+=zero;
  checks.push({path,export_sha256:createHash('sha256').update(bytes).digest('hex'),mesh:mesh.getName(),material:material.getName(),uv_set:set,triangles:count/3,exactly_collapsed:zero,below_1e_minus14:near,min_uv_area:min,positive_orientation:positive,negative_orientation:negative});
 }
}
await fs.writeFile(output,JSON.stringify({asset:key,revision:config.review,checks,exactly_collapsed_triangles:errors,scope:'Actual UV area of normal-mapped primitives; no texture-density, camera, geometry or artistic certification',art_accepted:false},null,2)+'\n');
console.log(JSON.stringify({asset:key,normal_mapped_primitives:checks.length,collapsed_uv_triangles:errors,report:output}));
if(errors)process.exitCode=2;
