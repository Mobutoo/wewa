/** Inspect actual GLB embedded front texture and front/back assignment. No legal/material/fit receipt. */
import {NodeIO} from '@gltf-transform/core';
import fs from 'node:fs';
import crypto from 'node:crypto';
const base='assets-src/moto-components/license-plate-wewa/',out='creative/reviews/license-plate-wewa-v1/',p=base+'license-plate-wewa-v1.glb',doc=await new NodeIO().read(p),rows=[];
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');let textured=0;
for(const mesh of doc.getRoot().listMeshes())for(const prim of mesh.listPrimitives()){
 const mat=prim.getMaterial(),tex=mat.getBaseColorTexture(),n=prim.getAttribute('NORMAL').getArray(),ys=[];for(let i=1;i<n.length;i+=3)ys.push(n[i]);
 const row={material:mat.getName(),triangles:prim.getIndices().getCount()/3,normal_y_min:Math.min(...ys),normal_y_max:Math.max(...ys),has_color_texture:!!tex};
 if(tex){if(row.normal_y_min<.999)throw Error('Graphic incorrectly assigned to non-front faces');const data=tex.getImage();fs.writeFileSync(out+'embedded-front-color.png',data);row.texture_sha256=sha(data);row.texture_mime=tex.getMimeType();row.texture_size=tex.getSize();textured++;}
 else if(row.normal_y_max>.001)throw Error('Untextured front face');rows.push(row);
}
if(textured!==1)throw Error('Expected exactly one front texture primitive');
fs.writeFileSync(out+'graphic-export-check.json',JSON.stringify({source:p,source_sha256:sha(fs.readFileSync(p)),primitives:rows,scope:'Actual GLB normal/material and embedded image inspection; no legal plate, color calibration or fit/art receipt'},null,2)+'\n');console.log(JSON.stringify(rows));
