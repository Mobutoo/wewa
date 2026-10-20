// Texture export/format conversion only. Original artwork remains in the source blend.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { NodeIO } from '@gltf-transform/core';
import { EXTTextureWebP } from '@gltf-transform/extensions';
const require = createRequire(import.meta.url);
let sharp;
try { sharp = require('sharp'); }
catch { sharp = require(require.resolve('sharp', { paths: [process.env.WEWA_SHARP_ROOT ?? '/workspace/wewa-audit/node-tools'] })); }

const directory = process.argv[2] ?? '/workspace/wewa-assets/cargo-lot01';
const input = path.join(directory, 'cargo-lot01.glb');
const io = new NodeIO().registerExtensions([EXTTextureWebP]);
const document = await io.read(input);
const before = (await fs.stat(input)).size;
for (const mesh of document.getRoot().listMeshes()) {
  for (const primitive of mesh.listPrimitives()) {
    const material = primitive.getMaterial();
    if (!material?.getNormalTexture()) primitive.setAttribute('TANGENT', null);
    if (material && !material.getBaseColorTexture() && !material.getNormalTexture()
      && !material.getMetallicRoughnessTexture() && !material.getOcclusionTexture()
      && !material.getEmissiveTexture()) primitive.setAttribute('TEXCOORD_0', null);
  }
}
const images = [];
for (const texture of document.getRoot().listTextures()) {
  const name = texture.getName();
  const isColor = /basecolor/i.test(name);
  const existing = await sharp(texture.getImage()).metadata();
  if (texture.getMimeType() === 'image/webp' && existing.width <= 1024 && existing.height <= 1024) {
    images.push({ name, bytes: texture.getImage().length, width: existing.width, height: existing.height,
      encoding: 'Existing WebP retained byte-for-byte' });
    continue;
  }
  const data = await sharp(texture.getImage())
    .resize({ width: 1024, height: 1024, fit: 'inside', withoutEnlargement: true })
    .webp({ lossless: !isColor, quality: 92, effort: 6 })
    .toBuffer();
  texture.setImage(data).setMimeType('image/webp').setURI(name + '.webp');
  const metadata = await sharp(data).metadata();
  images.push({ name, bytes: data.length, width: metadata.width, height: metadata.height,
    encoding: isColor ? 'WebP color quality92' : 'WebP lossless data map' });
}
document.createExtension(EXTTextureWebP).setRequired(true);
const temporary = path.join(directory, 'cargo-lot01-webp.glb');
await io.write(temporary, document);
await fs.rename(temporary, input);
const result = { scope: 'Texture downscale/format conversion, not artistic approval',
  before_bytes: before, after_bytes: (await fs.stat(input)).size,
  required_extension: 'EXT_texture_webp', normal_and_roughness_encoding: 'lossless', images };
await fs.writeFile(path.join(directory, 'texture-compression.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ before: before, after: result.after_bytes, textures: images.length }));
