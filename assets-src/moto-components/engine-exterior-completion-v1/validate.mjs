import fs from 'node:fs';import validator from 'gltf-validator';
const base=new URL('./',import.meta.url);const r=await validator.validateBytes(new Uint8Array(fs.readFileSync(new URL('engine-exterior-completion-v1.glb',base))));fs.writeFileSync(new URL('gltf-validation.json',base),JSON.stringify(r,null,2));console.log(JSON.stringify(r.issues));if(r.issues.numErrors)process.exitCode=1;
