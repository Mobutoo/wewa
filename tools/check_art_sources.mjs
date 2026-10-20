// Structural checks of downloaded candidates, separate from artistic acceptance.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import validator from 'gltf-validator';

const root = fileURLToPath(new URL('../', import.meta.url));
const source = process.argv[2];
if (!source) throw new Error('Usage: node tools/check_art_sources.mjs /path/to/library');
const manifest = JSON.parse(await fs.readFile(path.join(root, 'creative/library/manifest.json'), 'utf8'));
const rows = [];
for (const entry of manifest.assets.filter(e => e.kind === 'model')) {
  const gltfFile = entry.files.find(f => f.path.endsWith('.gltf'));
  const absolute = path.resolve(source, gltfFile.path);
  const json = JSON.parse(await fs.readFile(absolute, 'utf8'));
  let triangles = 0;
  for (const mesh of json.meshes ?? []) for (const primitive of mesh.primitives) {
    const count = json.accessors[primitive.indices ?? primitive.attributes.POSITION].count;
    if ((primitive.mode ?? 4) === 4) triangles += count / 3;
  }
  const totalBytes = entry.files.reduce((n, f) => n + f.bytes, 0);
  const row = { id: entry.id, triangles_in_all_mesh_definitions: triangles,
    meshes: json.meshes?.length ?? 0, materials: json.materials?.length ?? 0,
    total_source_bytes: totalBytes, artistic_acceptance: false,
    runtime_ready: false, lods_and_texture_optimization_required: true };
  // Avoid mistaking an enormous source tree library for a mobile-ready tree.
  if (totalBytes > 80_000_000) {
    row.structural_validation = 'deferred_heavy_source_not_for_direct_runtime_use';
  } else {
    const report = await validator.validateString(JSON.stringify(json), {
      uri: path.basename(absolute), maxIssues: 30,
      externalResourceFunction: async uri => {
        const relative = decodeURIComponent(uri);
        const candidate = path.resolve(path.dirname(absolute), relative);
        if (!candidate.startsWith(path.dirname(absolute) + path.sep)) throw new Error('Unsafe resource URI');
        return new Uint8Array(await fs.readFile(candidate));
      }
    });
    row.structural_validation = 'executed';
    row.errors = report.issues.numErrors;
    row.warnings = report.issues.numWarnings;
    row.issues = report.issues.messages;
  }
  rows.push(row);
  console.log(entry.id, triangles, row.structural_validation, row.errors ?? '-');
}
const output = { schema: 1, evaluated_utc: new Date().toISOString(),
  scope: 'Downloaded source glTF only; not runtime performance, artistic or geographic acceptance',
  models: rows };
await fs.writeFile(path.join(root, 'creative/library/source-checks.json'), JSON.stringify(output, null, 2) + '\n');
if (rows.some(row => row.errors > 0)) process.exitCode = 1;
