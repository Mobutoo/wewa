#!/usr/bin/env node
/** Static glTF compositor. Original GLBs are immutable external RAW buffers. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';

const clone = x => structuredClone(x);
const fail = message => { throw new Error(message); };
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const alias = new Map([['Front brake panel - editable casting', 'Front brake panel - inspection export']]);
const scalarMaterialExtensions = new Set(['KHR_materials_unlit', 'KHR_materials_clearcoat', 'KHR_materials_ior', 'KHR_materials_transmission', 'KHR_materials_volume', 'KHR_materials_specular', 'KHR_materials_sheen', 'KHR_materials_iridescence', 'KHR_materials_anisotropy', 'KHR_materials_emissive_strength', 'KHR_materials_pbrSpecularGlossiness', 'KHR_materials_dispersion']);
const tables = ['accessors', 'bufferViews', 'images', 'textures', 'samplers', 'materials', 'meshes'];
const uriFor = (from, to) => path.relative(from, to).split(path.sep).map(encodeURIComponent).join('/');
const localURI = uri => !/^[a-z][a-z\d+.-]*:/i.test(uri) && !uri.startsWith('/') && !uri.includes('\\');
const resolveURI = (folder, uri) => localURI(uri) ? path.resolve(folder, decodeURIComponent(uri)) : fail(`Unsupported nonlocal URI: ${uri}`);

// Column-major matrices; Blender XYZ Euler = Rz * Ry * Rx.
export const multiply = (a,b) => Array.from({length:16},(_,i) => {
  const row=i%4,col=Math.floor(i/4); return [0,1,2,3].reduce((s,k)=>s+a[k*4+row]*b[col*4+k],0);
});
const G=[1,0,0,0, 0,0,-1,0, 0,1,0,0, 0,0,0,1];
const GI=[1,0,0,0, 0,0,1,0, 0,-1,0,0, 0,0,0,1];
export function parentMatrix(row) {
  const vector = (v,n,label) => { if(!Array.isArray(v)||v.length!==n||!v.every(Number.isFinite)) fail(`${row.key}: invalid ${label}`);return v; };
  const scale=vector(row.scale??[1,1,1],3,'scale');
  if(scale.some(x=>x<=0))fail(`${row.key}: strictly positive scale required; no mirror or collapse`);
  const matrixFields=['matrix_blender','matrix_world','matrix'].filter(k=>row[k]!==undefined);
  let blender;
  if(matrixFields.length) {
    if(matrixFields.length!==1)fail(`${row.key}: ambiguous matrix fields`);
    const raw=row[matrixFields[0]];
    if(Array.isArray(raw)&&raw.length===4&&raw.every(r=>Array.isArray(r)&&r.length===4)) {
      raw.forEach(r=>vector(r,4,'matrix row'));
      blender=Array.from({length:16},(_,i)=>raw[i%4][Math.floor(i/4)]);
    } else {
      vector(raw,16,'flat matrix');
      if(!['row-major','column-major'].includes(row.matrix_layout))fail(`${row.key}: flat matrix requires matrix_layout`);
      blender=row.matrix_layout==='column-major'?[...raw]:Array.from({length:16},(_,i)=>raw[(i%4)*4+Math.floor(i/4)]);
    }
    if(blender[3]!==0||blender[7]!==0||blender[11]!==0||blender[15]!==1)fail(`${row.key}: matrix must be affine`);
    const columns=[0,1,2].map(c=>blender.slice(c*4,c*4+3));
    const dot=(a,b)=>a.reduce((n,x,i)=>n+x*b[i],0);
    const lengths=columns.map(c=>Math.hypot(...c));
    const [a,b,c]=columns;
    const det=a[0]*(b[1]*c[2]-b[2]*c[1])-b[0]*(a[1]*c[2]-a[2]*c[1])+c[0]*(a[1]*b[2]-a[2]*b[1]);
    if(!Number.isFinite(det)||det<=0||lengths.some(x=>!Number.isFinite(x)||x===0))fail(`${row.key}: reflected or singular matrix`);
    for(const [i,j] of [[0,1],[0,2],[1,2]])if(Math.abs(dot(columns[i],columns[j]))>1e-10*lengths[i]*lengths[j])fail(`${row.key}: shear cannot be represented by a glTF TRS node`);
    // Explicit Blender world matrix is authoritative; do not apply row TRS twice.
  } else {
    const [x,y,z]=vector(row.rotation_degrees,3,'rotation').map(v=>v*Math.PI/180);
    const [cx,sx,cy,sy,cz,sz]=[Math.cos(x),Math.sin(x),Math.cos(y),Math.sin(y),Math.cos(z),Math.sin(z)];
    const rx=[1,0,0,0, 0,cx,sx,0, 0,-sx,cx,0, 0,0,0,1];
    const ry=[cy,0,-sy,0, 0,1,0,0, sy,0,cy,0, 0,0,0,1];
    const rz=[cz,sz,0,0, -sz,cz,0,0, 0,0,1,0, 0,0,0,1];
    const sm=[scale[0],0,0,0, 0,scale[1],0,0, 0,0,scale[2],0, 0,0,0,1];
    blender=multiply(multiply(rz,multiply(ry,rx)),sm);
    const t=vector(row.translation_m,3,'translation');blender[12]=t[0];blender[13]=t[1];blender[14]=t[2];
  }
  const result=multiply(multiply(G,blender),GI);
  if(!result.every(Number.isFinite))fail(`${row.key}: nonfinite composed matrix`);
  return result;
}

async function readGLB(file) {
  const bytes=await fs.readFile(file);
  if(bytes.length<20||bytes.readUInt32LE(0)!==0x46546c67||bytes.readUInt32LE(4)!==2||bytes.readUInt32LE(8)!==bytes.length) fail(`Invalid GLB2: ${file}`);
  let json, binOffset, binLength;
  for(let at=12;at<bytes.length;) {
    if(at+8>bytes.length) fail(`Truncated chunk: ${file}`);
    const len=bytes.readUInt32LE(at),type=bytes.readUInt32LE(at+4),payload=at+8;
    if(len%4||payload+len>bytes.length) fail(`Invalid chunk bounds: ${file}`);
    if(type===0x4e4f534a) {if(json||at!==12) fail(`Invalid JSON chunk: ${file}`);json=JSON.parse(bytes.subarray(payload,payload+len).toString('utf8').trim());}
    else if(type===0x004e4942) {if(binOffset!==undefined) fail(`Multiple BIN chunks: ${file}`);binOffset=payload;binLength=len;}
    else fail(`Unsupported GLB chunk: ${type}`);
    at=payload+len;
  }
  if(!json||json.asset?.version!=='2.0') fail(`Not glTF2: ${file}`);
  if(json.buffers?.length!==1||json.buffers[0].uri!==undefined||binOffset===undefined||json.buffers[0].byteLength>binLength) fail(`Expected single embedded BIN: ${file}`);
  return {json,binOffset,binLength,byteLength:bytes.length,sha256:sha(bytes)};
}

// Reject extensions unless their reference semantics are explicitly implemented.
function auditExtensions(value, context='root', used=new Set()) {
  if(!value||typeof value!=='object') return used;
  for(const [key,v] of Object.entries(value)) {
    if(key==='extras') continue;
    if(key==='extensions') {
      for(const [name,data] of Object.entries(v)) {
        if(name==='KHR_lights_punctual'&&(context==='root'||context==='nodes')) continue;
        const ok=(context==='materials'&&scalarMaterialExtensions.has(name)) ||
          (context==='textureInfo'&&name==='KHR_texture_transform') ||
          (context==='textures'&&['KHR_texture_basisu','EXT_texture_webp'].includes(name));
        if(!ok) fail(`Unsupported extension ${name} at ${context}; no index guessing`);
        used.add(name);auditExtensions(data,context,used);
      }
    } else if(Array.isArray(v)) for(const child of v) auditExtensions(child, ['materials','textures','nodes'].includes(key)?key:context,used);
    else auditExtensions(v,/Texture$/.test(key)?'textureInfo':context,used);
  }
  return used;
}
function mapMaterial(m, texture) {
  const visit=v=> {if(!v||typeof v!=='object')return;for(const [k,c] of Object.entries(v)) {
    if(k==='extras')continue;
    if(/Texture$/.test(k)&&c&&typeof c==='object'&&c.index!==undefined)c.index=texture(c.index);
    visit(c);
  }};visit(m);return m;
}

export async function compose({parentsFile,routesFile,outFile,root=process.cwd()}) {
  const parentsBytes=await fs.readFile(parentsFile),routesBytes=await fs.readFile(routesFile);
  const parents=JSON.parse(parentsBytes).parents,routes=JSON.parse(routesBytes).rows;
  if(!Array.isArray(parents)||!parents.length||!Array.isArray(routes))fail('Expected parents[] and routes.rows[]');
  const routeMap=new Map();for(const r of routes){if(routeMap.has(r.key))fail(`Duplicate route ${r.key}`);routeMap.set(r.key,r);}
  const outDir=path.dirname(path.resolve(outFile));
  const gltf={asset:{version:'2.0',generator:'WEWA compose_motorcycle_gltf_v1 — immutable GLB RAW buffers'},scene:0,scenes:[{name:'Motorcycle static provisional assembly',nodes:[]}],nodes:[],skins:[],buffers:[]};
  for(const t of tables)gltf[t]=[];
  const proof={parents_input:{path:parentsFile,sha256:sha(parentsBytes)},routes_input:{path:routesFile,sha256:sha(routesBytes)},sources:[],parents:[],aliases:Object.fromEntries(alias),binary_files_written:0,animation_camera_lights_exported:false};
  const sources=new Map(),used=new Set(),required=new Set();
  if(new Set(parents.map(p=>p.key)).size!==parents.length)fail('Duplicate parent keys');
  async function load(file) {
    if(sources.has(file))return sources.get(file);
    const data=await readGLB(file),s=data.json;const active=s.scenes?.[s.scene??0];if(!active)fail(`No active/default scene: ${file}`);
    for(const e of auditExtensions(s))used.add(e);
    for(const e of [...(s.extensionsUsed??[]),...(s.extensionsRequired??[])]) {
      if(e==='KHR_lights_punctual')continue;
      if(!scalarMaterialExtensions.has(e)&&!['KHR_texture_transform','KHR_texture_basisu','EXT_texture_webp'].includes(e))fail(`Unsupported declared extension ${e}`);used.add(e);
    }
    for(const e of s.extensionsRequired??[])if(e!=='KHR_lights_punctual')required.add(e);
    const offsets=Object.fromEntries(tables.map(t=>[t,gltf[t].length]));
    const map=(table,i)=>{if(!Number.isInteger(i)||i<0||i>=(s[table]?.length??0))fail(`Invalid ${table} index ${i} in ${file}`);return offsets[table]+i;};
    const buffer=gltf.buffers.length;gltf.buffers.push({uri:uriFor(outDir,file),byteLength:data.byteLength});
    for(const item of s.bufferViews??[]) {const v=clone(item);if(v.buffer!==0)fail('Only embedded buffer0 supported');if((v.byteOffset??0)+v.byteLength>s.buffers[0].byteLength)fail(`bufferView beyond original BIN: ${file}`);v.buffer=buffer;v.byteOffset=(v.byteOffset??0)+data.binOffset;gltf.bufferViews.push(v);}
    for(const item of s.accessors??[]) {const a=clone(item);if(a.bufferView!==undefined)a.bufferView=map('bufferViews',a.bufferView);if(a.sparse){a.sparse.indices.bufferView=map('bufferViews',a.sparse.indices.bufferView);a.sparse.values.bufferView=map('bufferViews',a.sparse.values.bufferView);}gltf.accessors.push(a);}
    for(const item of s.images??[]) {const im=clone(item);if(im.bufferView!==undefined)im.bufferView=map('bufferViews',im.bufferView);if(im.uri&&!im.uri.startsWith('data:'))im.uri=uriFor(outDir,resolveURI(path.dirname(file),im.uri));gltf.images.push(im);}
    gltf.samplers.push(...clone(s.samplers??[]));
    for(const item of s.textures??[]) {const t=clone(item);if(t.source!==undefined)t.source=map('images',t.source);if(t.sampler!==undefined)t.sampler=map('samplers',t.sampler);for(const v of Object.values(t.extensions??{}))if(v.source!==undefined)v.source=map('images',v.source);gltf.textures.push(t);}
    for(const item of s.materials??[])gltf.materials.push(mapMaterial(clone(item),i=>map('textures',i)));
    for(const item of s.meshes??[]) {const m=clone(item);for(const p of m.primitives){for(const k of Object.keys(p.attributes))p.attributes[k]=map('accessors',p.attributes[k]);if(p.indices!==undefined)p.indices=map('accessors',p.indices);if(p.material!==undefined)p.material=map('materials',p.material);for(const target of p.targets??[])for(const k of Object.keys(target))target[k]=map('accessors',target[k]);}gltf.meshes.push(m);}
    const reachable=new Set(),ancestors=new Map();
    function walk(i,parent,stack=new Set()){if(!Number.isInteger(i)||!s.nodes?.[i])fail('Invalid source node');if(stack.has(i)||reachable.has(i))fail(`Cyclic/multiple-parent source hierarchy: ${file}`);reachable.add(i);if(parent!==undefined)ancestors.set(i,parent);for(const c of s.nodes[i].children??[])walk(c,i,new Set([...stack,i]));}
    for(const i of active.nodes??[])walk(i);
    const row={source_glb:path.relative(root,file),sha256:data.sha256,byteLength:data.byteLength,bin_payload_offset:data.binOffset,bin_chunk_length:data.binLength,buffer_index:buffer,exemplar_count:0,active_scene:s.scene??0};proof.sources.push(row);
    const source={s,map,reachable,ancestors,roots:active.nodes??[],row};sources.set(file,source);return source;
  }
  for(const p of parents) {
    const r=routeMap.get(p.key);if(!r)fail(`Missing route ${p.key}`);
    if(r.source_blend!==p.source)fail(`${p.key}: route/native source mismatch`);
    const selected=p.selected_objects??r.selected_objects??[];
    if(p.selected_objects&&r.selected_objects&&JSON.stringify(p.selected_objects)!==JSON.stringify(r.selected_objects))fail(`${p.key}: conflicting selected_objects`);
    const src=await load(path.resolve(root,r.glb));const {s,map,reachable,ancestors}=src;
    const meshNodes=new Set(),matched=[];
    function descendants(i){if(!reachable.has(i))fail('Inactive selected descendant');if(s.nodes[i].mesh!==undefined)meshNodes.add(i);for(const c of s.nodes[i].children??[])descendants(c);}
    if(selected.length)for(const label of selected){const name=alias.get(label)??label;const matches=[...reachable].filter(i=>s.nodes[i].name===name);if(matches.length!==1)fail(`${p.key}: selected label ${label} matched ${matches.length} active nodes`);const i=matches[0];matched.push({requested:label,matched:name,node:i});if(s.nodes[i].mesh!==undefined)meshNodes.add(i);else descendants(i);}
    else for(const i of reachable)if(s.nodes[i].mesh!==undefined)meshNodes.add(i);
    if(!meshNodes.size)fail(`${p.key}: no selected meshes`);
    const keep=new Set();function keepPath(i){if(!reachable.has(i))fail(`${p.key}: skin joint outside active scene`);while(i!==undefined&&!keep.has(i)){keep.add(i);i=ancestors.get(i);}}
    const skins=new Set();for(const i of meshNodes){keepPath(i);if(s.nodes[i].skin!==undefined)skins.add(s.nodes[i].skin);}
    for(const i of skins){const sk=s.skins?.[i];if(!sk)fail('Invalid skin');for(const j of sk.joints)keepPath(j);if(sk.skeleton!==undefined)keepPath(sk.skeleton);}
    const nodeMap=new Map([...keep].map((i,k)=>[i,gltf.nodes.length+k]));const skinMap=new Map([...skins].map((i,k)=>[i,gltf.skins.length+k]));
    for(const i of keep){const n=clone(s.nodes[i]);delete n.camera;if(n.extensions){delete n.extensions.KHR_lights_punctual;if(!Object.keys(n.extensions).length)delete n.extensions;}
      if(meshNodes.has(i)){n.mesh=map('meshes',n.mesh);if(n.skin!==undefined)n.skin=skinMap.get(n.skin);}else {delete n.mesh;delete n.skin;delete n.weights;}
      if(n.children){n.children=n.children.filter(c=>keep.has(c)).map(c=>nodeMap.get(c));if(!n.children.length)delete n.children;}gltf.nodes.push(n);
    }
    for(const i of skins){const sk=clone(s.skins[i]);sk.joints=sk.joints.map(j=>nodeMap.get(j));if(sk.skeleton!==undefined)sk.skeleton=nodeMap.get(sk.skeleton);if(sk.inverseBindMatrices!==undefined)sk.inverseBindMatrices=map('accessors',sk.inverseBindMatrices);gltf.skins.push(sk);}
    const index=gltf.nodes.length;gltf.nodes.push({name:`PARENT [${p.key}]`,matrix:parentMatrix(p),children:src.roots.filter(i=>keep.has(i)).map(i=>nodeMap.get(i)),extras:{parent_key:p.key,source_glb:src.row.source_glb,placement_status:p.placement_status??'unverified',transform_input:['matrix_blender','matrix_world','matrix'].find(k=>p[k]!==undefined)??'TRS_Blender_XYZ'}});gltf.scenes[0].nodes.push(index);src.row.exemplar_count++;
    proof.parents.push({key:p.key,source_blend:p.source,source_blend_manifest_sha256:p.sha256,parent_node:index,source_glb:src.row.source_glb,selected_matches:matched,mesh_node_count:meshNodes.size,cloned_node_count:keep.size,shared_mesh_ids:[...new Set([...meshNodes].map(i=>map('meshes',s.nodes[i].mesh)))],matrix:gltf.nodes[index].matrix});
  }
  if(used.size)gltf.extensionsUsed=[...used].sort();if(required.size)gltf.extensionsRequired=[...required].sort();
  for(const t of [...tables,'skins'])if(!gltf[t].length)delete gltf[t];
  proof.parent_count=parents.length;proof.unique_glb_count=sources.size;proof.original_glb_total_bytes=proof.sources.reduce((n,r)=>n+r.byteLength,0);
  return {gltf,proof};
}

export async function validateAndBounds(gltf,outFile,proof) {
  const folder=path.dirname(path.resolve(outFile));const validator=await import('gltf-validator');
  const result=await validator.validateString(JSON.stringify(gltf),{uri:path.basename(outFile),maxIssues:0,externalResourceFunction:async uri=>new Uint8Array(await fs.readFile(resolveURI(folder,uri)))});
  proof.validator={numErrors:result.issues.numErrors,numWarnings:result.issues.numWarnings,numInfos:result.issues.numInfos,numHints:result.issues.numHints,messages:result.issues.messages};
  if(result.issues.truncated)fail('Validator issue list unexpectedly truncated');
  if(result.issues.numErrors)fail(`glTF validator: ${result.issues.numErrors} errors: ${JSON.stringify(result.issues.messages.filter(m=>m.severity===0).slice(0,8))}`);
  const {NodeIO}=await import('@gltf-transform/core');const {getBounds}=await import('@gltf-transform/functions');
  const resources={};for(const b of gltf.buffers)resources[b.uri]=new Uint8Array(await fs.readFile(resolveURI(folder,b.uri)));
  for(const im of gltf.images??[])if(im.uri&&!im.uri.startsWith('data:'))resources[im.uri]=new Uint8Array(await fs.readFile(resolveURI(folder,im.uri)));
  const {ALL_EXTENSIONS}=await import('@gltf-transform/extensions');
  const doc=await new NodeIO().registerExtensions(ALL_EXTENSIONS).readJSON({json:gltf,resources});
  proof.bounds_method='NodeIO readJSON + getBounds on each actual parent subtree; glTF metres. No native comparison asserted.';
  const nodes=doc.getRoot().listNodes();for(const p of proof.parents){
    if(nodes[p.parent_node]?.getName()!==`PARENT [${p.key}]`)fail(`NodeIO parent index mismatch: ${p.key}`);
    p.export_bounds_gltf=getBounds(nodes[p.parent_node]);
    if(![...p.export_bounds_gltf.min,...p.export_bounds_gltf.max].every(Number.isFinite))fail(`Nonfinite bounds: ${p.key}`);
  }
  for(const source of proof.sources){const b=await fs.readFile(path.resolve(folder,gltf.buffers[source.buffer_index].uri.split('/').map(decodeURIComponent).join('/')));if(sha(b)!==source.sha256)fail(`Source changed during probe: ${source.source_glb}`);}
  proof.original_glb_hashes_rechecked=true;
}
async function main(){
  const args=process.argv.slice(2),opts={};for(let i=0;i<args.length;i++){const k=args[i];if(k==='--probe'){opts.probe=true;continue;}if(!['--parents','--routes','--out'].includes(k)||!args[i+1])fail(`Usage: --parents file --routes file --out file.gltf [--probe]`);opts[k.slice(2)]=args[++i];}
  if(!opts.parents||!opts.routes||!opts.out||path.extname(opts.out)!=='.gltf')fail('Required --parents --routes --out *.gltf');
  const {gltf,proof}=await compose({parentsFile:opts.parents,routesFile:opts.routes,outFile:opts.out});
  await validateAndBounds(gltf,opts.out,proof);const text=JSON.stringify(gltf)+'\n';proof.gltf_bytes=Buffer.byteLength(text);proof.gltf_sha256=sha(text);
  if(!opts.probe){
    for(const file of [opts.out,opts.out+'.proof.json']){try{await fs.access(file);fail(`Refusing existing output ${file}`);}catch(e){if(e.code!=='ENOENT')throw e;}}
    await fs.mkdir(path.dirname(opts.out),{recursive:true});await fs.writeFile(opts.out,text,{flag:'wx'});await fs.writeFile(opts.out+'.proof.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});}
  process.stdout.write(JSON.stringify({probe:!!opts.probe,...proof},null,2)+'\n');
}
if(process.argv[1]&&import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href)main().catch(e=>{console.error(e.stack);process.exitCode=1;});
