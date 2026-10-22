#!/usr/bin/env node
/** Derive a review LOD from the exact exterior v5 resource tree; originals stay immutable. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {NodeIO, PropertyType} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {prune, weld, simplifyPrimitive, getBounds, textureCompress, unpartition, dedup, quantize} from '@gltf-transform/functions';
import {MeshoptSimplifier} from 'meshoptimizer';
import sharp from 'sharp';
import {validateBytes} from 'gltf-validator';

const root = path.resolve(import.meta.dirname, '..');
const args = process.argv.slice(2);
const options = {};
for (let i = 0; i < args.length; i += 2) {
  if (!['--out', '--ratio', '--error', '--texture-size', '--manifest', '--expected-parents'].includes(args[i]) || !args[i + 1]) {
    throw Error('Usage: node tools/build_motorcycle_lod_v2.mjs --out folder --manifest path --expected-parents 177 [--ratio .005 --error .002 --texture-size 1024]');
  }
  options[args[i].slice(2)] = args[i + 1];
}
if (!options.out) throw Error('--out required');
const out = path.resolve(root, options.out);
if (!out.startsWith(root + path.sep)) throw Error('Output must be inside the repository');
const ratio = Number(options.ratio ?? .005), error = Number(options.error ?? .002);
const size = Number(options['texture-size'] ?? 1024);
if (!(ratio > 0 && ratio <= 1 && error > 0 && error <= .02 && Number.isInteger(size) && size >= 128)) {
  throw Error('Invalid simplification parameters');
}
await fs.mkdir(out, {recursive: true});
const output = path.join(out, 'motorcycle-lod.glb');
try { await fs.access(output); throw Error('Refusing to overwrite an existing LOD'); }
catch (e) { if (e.code !== 'ENOENT') throw e; }
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const manifestPath = options.manifest;
const expectedParents=Number(options['expected-parents']);
if(!manifestPath || !Number.isInteger(expectedParents) || expectedParents<1)throw Error('--manifest and --expected-parents required');
const manifestBytes = await fs.readFile(path.join(root, manifestPath));
const manifest = JSON.parse(manifestBytes);
const sourceFiles = manifest.files.filter(f => f.usage.includes('runtime'));
for (const f of sourceFiles) {
  const bytes = await fs.readFile(path.join(root, f.path));
  if (bytes.length !== f.bytes || sha(bytes) !== f.sha256) throw Error(`Changed input: ${f.path}`);
}
console.log(`Verified ${sourceFiles.length} frozen runtime resources`);
const input = path.join(root, manifest.runtime_model);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const document = await io.read(input);
// Discard source objects absent from the selected assembly, before counting or simplifying.
await document.transform(prune({keepLeaves: true}));
const r = document.getRoot();
const parents = r.listNodes().filter(n => n.getName().startsWith('PARENT ['));
const snapshot = () => parents.map(n => ({name:n.getName(), matrix:n.getWorldMatrix(), bounds:getBounds(n)}));
const beforeParents = snapshot();
const stats = () => ({
  parents: parents.length,
  mesh_instances: r.listNodes().filter(n => n.getMesh()).length,
  unique_meshes: r.listMeshes().length,
  primitives: r.listMeshes().reduce((s,m) => s+m.listPrimitives().length, 0),
  primitive_instances: r.listNodes().reduce((s,n) => s+(n.getMesh()?.listPrimitives().length ?? 0),0),
  triangles: r.listNodes().reduce((s,n) => s+(n.getMesh()?.listPrimitives().reduce((a,p) => a+(p.getIndices()?.getCount() ?? p.getAttribute('POSITION').getCount())/3,0) ?? 0),0),
  textures: r.listTextures().length,
  bounds: getBounds(r.listScenes()[0]),
});
const before = stats();
console.log(JSON.stringify({before}));
// Glossy silhouette panels need a tighter approximation than small mechanical relief.
// These overrides were selected after comparing the actual first-pass source/LOD canvases.
const profiles = {
  'instrument-visor': {ratio:1,error:.00005},
  'fuel-tank-shell': {ratio:.1,error:.00005},
  'seat-envelope': {ratio:.15,error:.0001},
  'headlamp-cowl': {ratio:.04,error:.0001},
  'handlebar': {ratio:.015,error:.0002},
  'fuel-tap-visible-body': {ratio:.2,error:.0001},
  'fuel-tap-visible-lever': {ratio:.25,error:.0001},
  'side-stand-return-spring': {ratio:.05,error:.0002},
  'steering-cap-visible': {ratio:1,error:.00005},
};
const meshProfiles = new Map();
for (const [key, profile] of Object.entries(profiles)) {
  const parent = parents.find(n=>n.getName()===`PARENT [${key}]`);
  if (!parent) throw Error(`Missing protected surface: ${key}`);
  parent.traverse(n=>{if(n.getMesh())meshProfiles.set(n.getMesh(),{...profile,parent:key});});
}
await document.transform(weld());
await MeshoptSimplifier.ready;
const rows = [];
for (const mesh of r.listMeshes()) {
  for (const [index, prim] of mesh.listPrimitives().entries()) {
    if (prim.getMode() !== 4 || !prim.getIndices()) throw Error(`Unsupported primitive: ${mesh.getName()}`);
    const count = prim.getIndices().getCount()/3;
    const profile = meshProfiles.get(mesh) ?? {ratio,error,parent:null};
    const row = {mesh:mesh.getName(), primitive:index, triangles_before:count, profile};
    // Keep small controls/fasteners and ensure no primitive can be erased by a zero target.
    if (count > 24 && profile.ratio<1) simplifyPrimitive(prim, {simplifier:MeshoptSimplifier, ratio:Math.max(profile.ratio,12/count), error:profile.error, lockBorder:false});
    row.triangles_after = prim.getIndices().getCount()/3;
    if (!row.triangles_after) throw Error(`Primitive erased: ${mesh.getName()}`);
    rows.push(row);
  }
}
console.log('Simplified all primitives; resizing embedded textures');
await document.transform(
  prune({keepLeaves:true}),
  textureCompress({encoder:sharp, resize:[size,size]}),
  dedup({propertyTypes:[PropertyType.TEXTURE,PropertyType.MATERIAL]}),
  quantize({quantizePosition:16,quantizeNormal:16,quantizeTexcoord:16,cleanup:false}),
  prune({keepLeaves:true}),
  unpartition(),
);
const after = stats(), afterParents = snapshot();
const checks = beforeParents.map((p,i) => {
  const next = afterParents[i];
  if (p.name !== next.name || JSON.stringify(p.matrix) !== JSON.stringify(next.matrix)) throw Error(`Changed placement: ${p.name}`);
  const boundDelta = Math.max(...['min','max'].flatMap(k => p.bounds[k].map((v,j) => Math.abs(v-next.bounds[k][j]))));
  if (!Number.isFinite(boundDelta) || boundDelta > .005) throw Error(`Bounds moved >5mm: ${p.name}: ${boundDelta}`);
  return {name:p.name, matrix_unchanged:true, max_bounds_delta_m:boundDelta, bounds_before:p.bounds, bounds_after:next.bounds};
});
if (before.parents !== expectedParents || before.mesh_instances !== after.mesh_instances || before.primitives !== after.primitives) {
  throw Error('Assembly coverage changed');
}
const bytes = await io.writeBinary(document);
const validation = await validateBytes(bytes, {maxIssues:1000});
if (validation.issues.numErrors) throw Error(JSON.stringify(validation.issues));
// Reopen the exact binary to catch serialization losses, rather than checking only the in-memory document.
const reopened = await io.readBinary(bytes);
const reopenedParents = reopened.getRoot().listNodes().filter(n => n.getName().startsWith('PARENT ['));
if (reopenedParents.length !== expectedParents) throw Error('Serialized parent coverage changed');
for (const p of reopenedParents) {
  const original = afterParents.find(n => n.name === p.getName());
  if (!original || p.getWorldMatrix().some((v,i) => Math.abs(v-original.matrix[i])>2e-6)) throw Error(`Serialized transform changed: ${p.getName()}`);
}
// Verify frozen inputs again after processing.
for (const f of sourceFiles) if (sha(await fs.readFile(path.join(root,f.path))) !== f.sha256) throw Error(`Source changed: ${f.path}`);
const report = {
  schema:1, date:'2026-10-22', source_manifest:manifestPath, source_manifest_sha256:sha(manifestBytes),
  input:manifest.runtime_model, input_resources:sourceFiles.length, input_resource_bytes:sourceFiles.reduce((s,f)=>s+f.bytes,0),
  tool:'tools/build_motorcycle_lod_v2.mjs', tool_sha256:sha(await fs.readFile(new URL(import.meta.url))),
  settings:{ratio,error_relative_to_each_primitive_radius:error,texture_max_size:size,minimum_target_triangles:12,protected_surface_profiles:profiles,quantize_position_bits:16,quantize_normal_bits:16,quantize_uv_bits:16,identical_textures_and_materials_deduplicated:true},
  before, after, primitive_checks:rows, parent_checks:checks,
  output:path.relative(root,output), output_bytes:bytes.length, output_sha256:sha(bytes),
  gltf_validator:validation.issues, serialized_parents:reopenedParents.length,
  original_resources_unchanged:true, art_accepted:false, physical_iphone_tested:false,
  scope:'Static review LOD; no new mechanical shapes, no rig or mobile frame-rate claim. Bounds deltas measure export consistency, not surface error or OEM dimensions.',
};
await fs.writeFile(output,bytes,{flag:'wx'});
await fs.writeFile(path.join(out,'build-report.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({output:report.output,bytes:bytes.length,before,after,validator:validation.issues.numErrors}));
