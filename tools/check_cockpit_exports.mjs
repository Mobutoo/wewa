// Read actual glTF buffers, extension-aware materials, node hierarchy and pivots.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {getBounds} from '@gltf-transform/functions';
import validator from 'gltf-validator';
const asset=process.argv[2]||'instruments';
const config={instruments:['instruments','instruments-inspection.glb','instruments-v1'],handlebar:['handlebar','handlebar-inspection.glb','handlebar-v1'],grips:['handlebar-grips','handlebar-grips-inspection.glb','handlebar-grips-v1']}[asset];
if(!config)throw Error('Unknown cockpit component');
const [folder,name,revision]=config,file='assets-src/moto-components/'+folder+'/'+name;
const bytes=await fs.readFile(file),format=await validator.validateBytes(new Uint8Array(bytes),{uri:file,maxIssues:40});
const root=(await new NodeIO().registerExtensions(ALL_EXTENSIONS).read(file)).getRoot();
const bounds=getBounds(root.getDefaultScene());let vertices=0,triangles=0;
for(const mesh of root.listMeshes())for(const p of mesh.listPrimitives()){vertices+=p.getAttribute('POSITION').getCount();triangles+=(p.getIndices()?.getCount()||p.getAttribute('POSITION').getCount())/3;}
const nodes=root.listNodes().map(n=>n.getName());
const materials=root.listMaterials().map(m=>({name:m.getName(),basecolor:m.getBaseColorFactor(),roughness:m.getRoughnessFactor(),metallic:m.getMetallicFactor(),extensions:m.listExtensions().map(e=>e.extensionName)}));
const report={asset,file,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length,glTF_errors:format.issues.numErrors,glTF_warnings:format.issues.numWarnings,messages:format.issues.messages,bounds,vertices,triangles,node_names:nodes,materials,art_accepted:false,physical_iphone_tested:false};
if(asset==='instruments'){
 if(!['INSTRUMENT_CLUSTER_MOUNT','SPEED_NEEDLE_PIVOT','FUEL_NEEDLE_PIVOT','GEAR_DIGIT_1','GEAR_DIGIT_5'].every(name=>nodes.includes(name)))throw Error('Missing movable pointer or printed gear nodes');
 if(!materials.some(m=>m.extensions.includes('KHR_materials_transmission')))throw Error('Lens transmission lost in export');
 const dimensions=bounds.max.map((v,i)=>v-bounds.min[i]);if(dimensions[0]<.22||dimensions[0]>.26)throw Error('Unexpected cluster width');
}
if(report.glTF_errors)throw Error(JSON.stringify(report));
await fs.writeFile('creative/reviews/'+revision+'/geometry-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
