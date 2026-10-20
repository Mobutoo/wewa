// Actual exported buffers, not only source topology and exporter success.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {getBounds} from '@gltf-transform/functions';
import validator from 'gltf-validator';
const path='assets-src/moto-components/handlebar-grips/handlebar-grips-v3-inspection.glb';
const data=await fs.readFile(path),validation=await validator.validateBytes(new Uint8Array(data),{uri:path});
const root=(await new NodeIO().read(path)).getRoot(),bounds=getBounds(root.getDefaultScene()),meshes=[];
for(const mesh of root.listMeshes()){
 let volume=0,triangles=0,vertices=0,zeroAreaTriangles=0;
 for(const primitive of mesh.listPrimitives()){
  const p=primitive.getAttribute('POSITION'),ix=primitive.getIndices();vertices+=p.getCount();triangles+=ix.getCount()/3;const a=[],b=[],c=[];
  for(let i=0;i<ix.getCount();i+=3){p.getElement(ix.getScalar(i),a);p.getElement(ix.getScalar(i+1),b);p.getElement(ix.getScalar(i+2),c);const u=b.map((x,k)=>x-a[k]),v=c.map((x,k)=>x-a[k]);if(Math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])===0)zeroAreaTriangles++;volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;}
 }
 if(zeroAreaTriangles)throw Error('Degenerate grip triangles '+zeroAreaTriangles);if(volume<=0)throw Error('Non-positive exported volume: '+mesh.getName());
 meshes.push({name:mesh.getName(),vertices,triangles,zeroAreaTriangles,signed_volume_m3:volume});
}
const materials=root.listMaterials().map(m=>({name:m.getName(),basecolor:m.getBaseColorFactor(),metallic_roughness_texture:!!m.getMetallicRoughnessTexture()}));
const texture=root.listMaterials()[0].getMetallicRoughnessTexture();
const texture_source='assets-src/moto-components/handlebar-grips/textures-v3/rubber-metallic-roughness.png';
const texture_source_sha256=createHash('sha256').update(await fs.readFile(texture_source)).digest('hex');
const texture_export_sha256=createHash('sha256').update(texture.getImage()).digest('hex');
if(texture_source_sha256!==texture_export_sha256)throw Error('Exported roughness image differs from authored PNG');
const report={texture_source,texture_source_sha256,texture_export_sha256,texture_data_identical:true,path,sha256:createHash('sha256').update(data).digest('hex'),glTF_errors:validation.issues.numErrors,glTF_warnings:validation.issues.numWarnings,messages:validation.issues.messages,bounds,dimensions_glTF_xyz_m:bounds.max.map((x,i)=>x-bounds.min[i]),meshes,materials,scope:'Technical isolated candidate only; actual interface tolerances, throttle operation, art reception and physical Safari not verified',art_accepted:false};
if(report.glTF_errors||meshes.length!==2||!materials.every(m=>m.metallic_roughness_texture)||Math.abs(report.dimensions_glTF_xyz_m[0]-.700)>.030)throw Error(JSON.stringify(report));
await fs.writeFile('creative/reviews/handlebar-grips-v3/export-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
