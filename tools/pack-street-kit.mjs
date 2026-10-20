import {NodeIO,Document} from '@gltf-transform/core';
import {mergeDocuments,dedup,prune,unpartition} from '@gltf-transform/functions';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import validator from 'gltf-validator';
const root=path.resolve('app/public/models/street-kit'),source=path.resolve('assets-src/street-kit/exports');
const manifest=JSON.parse(await fs.readFile(path.join(root,'manifest.json'),'utf8')),io=new NodeIO(),combined=new Document();
for(const asset of manifest.assets){const file=path.join(source,asset.id+'.glb');const document=await io.read(file);mergeDocuments(combined,document);if(asset.kind==='facade'){const lod=path.resolve('assets-src/street-kit/lod1',asset.id+'.glb');try{const low=await io.read(lod);mergeDocuments(combined,low);}catch(error){throw new Error('Required LOD1 missing for '+asset.id+': '+error.message);}}asset.source_export='assets-src/street-kit/exports/'+asset.id+'.glb';asset.file='street-kit.glb';}
const scenes=combined.getRoot().listScenes(),scene=scenes[0];
for(const s of scenes.slice(1)){for(const child of s.listChildren())scene.addChild(child);s.dispose();}combined.getRoot().setDefaultScene(scene);
await combined.transform(dedup(),prune(),unpartition());
const output=path.join(root,'street-kit.glb');await io.write(output,combined);const bytes=await fs.readFile(output),report=await validator.validateBytes(new Uint8Array(bytes),{uri:'street-kit.glb'});if(report.issues.numErrors||report.issues.numWarnings)throw new Error(JSON.stringify(report.issues));
manifest.runtime={file:'street-kit.glb',bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),materials:combined.getRoot().listMaterials().length,textures:combined.getRoot().listTextures().length,node_naming:'<asset_id>__<material>',source_exports:'assets-src/street-kit/exports',lod1:true,lod_policy:'LOD0 <45m and lowest two floors, LOD1 other facades <200m; props <160m',validation_errors:0,validation_warnings:0};
await fs.writeFile(path.join(root,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');await fs.writeFile(path.resolve('WEWA_Developpement_Web/validation/street-kit-runtime.json'),JSON.stringify(report,null,2)+'\n');console.log(manifest.runtime);
