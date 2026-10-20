import fs from 'node:fs/promises';
import path from 'node:path';
import validator from 'gltf-validator';

const directory = process.argv[2] ?? '/workspace/wewa-assets/cargo-lot01';
const file = path.join(directory, 'cargo-lot01.glb');
const bytes = new Uint8Array(await fs.readFile(file));
const report = await validator.validateBytes(bytes, { uri: 'cargo-lot01.glb', maxIssues: 50 });
const result = {
  scope: 'Binary glTF structural inspection, not artistic acceptance or hardware qualification',
  file: 'cargo-lot01.glb',
  bytes: bytes.length,
  errors: report.issues.numErrors,
  warnings: report.issues.numWarnings,
  infos: report.issues.numInfos,
  messages: report.issues.messages,
  gltf_info: report.info,
  artistic_acceptance: false
};
await fs.writeFile(path.join(directory, 'glb-validation.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ bytes: bytes.length, errors: result.errors, warnings: result.warnings }));
if (result.errors) process.exitCode = 1;
