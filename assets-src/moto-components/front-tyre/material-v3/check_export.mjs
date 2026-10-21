// Compare actual old/new geometry attributes and the new exported material.
// A new tangent can split vertices; triangle-corner POSITION/N/UV0 equality is
// tested as well as raw buffers. No buffer is modified by this checker.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import validator from 'gltf-validator';
const H='assets-src/moto-components/front-tyre/material-v3/',O='creative/reviews/front-tyre-v3/';
const params=JSON.parse(await fs.readFile(H+'parameters.json'));const oldfile=params.baseline_export.path,file=H+'front-tyre-v3-inspection.glb';
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS),a=(await io.read(oldfile)).getRoot(),b=(await io.read(file)).getRoot();
const sha=x=>createHash('sha256').update(x).digest('hex');
const digest=x=>sha(Buffer.from(x.buffer,x.byteOffset,x.byteLength));
const na=a.listNodes().filter(n=>n.getMesh()),nb=b.listNodes().filter(n=>n.getMesh());
if(na.length!==1||nb.length!==1)throw Error('Expected one inspection node in each export');
const pa=na[0].getMesh().listPrimitives(),pb=nb[0].getMesh().listPrimitives();
if(pa.length!==1||pb.length!==1)throw Error('Expected one primitive');
const p=pa[0],q=pb[0],ia=p.getIndices().getArray(),ib=q.getIndices().getArray();
if(ia.length!==ib.length)throw Error('Triangle count changed');
function expanded(primitive,semantic){
 const attr=primitive.getAttribute(semantic),ix=primitive.getIndices().getArray(),array=attr.getArray(),width=attr.getElementSize();
 const out=new array.constructor(ix.length*width);
 for(let i=0;i<ix.length;i++)for(let j=0;j<width;j++)out[i*width+j]=array[ix[i]*width+j];
 return out;
}
const attrs={};
for(const k of ['POSITION','NORMAL','TEXCOORD_0']){
 const x=p.getAttribute(k).getArray(),y=q.getAttribute(k).getArray(),xx=expanded(p,k),yy=expanded(q,k);
 let max=0;for(let i=0;i<xx.length;i++)max=Math.max(max,Math.abs(xx[i]-yy[i]));
 attrs[k]={old_raw_values:x.length,new_raw_values:y.length,raw_exact:x.constructor.name===y.constructor.name&&x.length===y.length&&digest(x)===digest(y),
 old_corner_sha256:digest(xx),new_corner_sha256:digest(yy),triangle_corner_exact:xx.constructor.name===yy.constructor.name&&xx.length===yy.length&&digest(xx)===digest(yy),max_corner_abs_delta:max};
}
const matricesExact=JSON.stringify(na[0].getWorldMatrix())===JSON.stringify(nb[0].getWorldMatrix());
const preserve={old_export_sha256:sha(await fs.readFile(oldfile)),export_sha256:sha(await fs.readFile(file)),
 actual_world_matrix_exact:matricesExact,raw_indices_exact:ia.constructor.name===ib.constructor.name&&digest(ia)===digest(ib),attributes:attrs,
 all_oriented_triangle_corners_POSITION_N_UV0_and_world_matrix_exact:matricesExact&&Object.values(attrs).every(x=>x.triangle_corner_exact),
 old_tangent_present:!!p.getAttribute('TANGENT'),new_tangent_present:!!q.getAttribute('TANGENT'),
 tangent_status:'New actual tangent attribute for the baked normal map; no false claim of preserving a missing old tangent.',
 buffer_repair_performed:false,art_accepted:false};
await fs.writeFile(O+'material-geometry-preservation-check.json',JSON.stringify(preserve,null,2)+'\n');
if(!preserve.all_oriented_triangle_corners_POSITION_N_UV0_and_world_matrix_exact)throw Error('Geometry/normal/UV/matrix changed; inspect report');
const pos=q.getAttribute('POSITION').getArray(),nor=q.getAttribute('NORMAL').getArray(),tan=q.getAttribute('TANGENT')?.getArray(),uv=q.getAttribute('TEXCOORD_0').getArray();
if(!tan)throw Error('Missing actual tangent');
let areaZero=0,uvZero=0,minArea=Infinity,maxDot=0,badFrames=0;
for(let i=0;i<pos.length/3;i++){
 const n=[nor[i*3],nor[i*3+1],nor[i*3+2]],t=[tan[i*4],tan[i*4+1],tan[i*4+2]],nl=Math.hypot(...n),tl=Math.hypot(...t);
 maxDot=Math.max(maxDot,Math.abs(n[0]*t[0]+n[1]*t[1]+n[2]*t[2])/(nl*tl));
 if(!Number.isFinite(nl+tl)||Math.abs(nl-1)>.002||Math.abs(tl-1)>.002||Math.abs(tan[i*4+3])!==1)badFrames++;
}
for(let k=0;k<ib.length;k+=3){
 const [ai,bi,ci]=[ib[k],ib[k+1],ib[k+2]];
 const u=[0,1,2].map(j=>pos[bi*3+j]-pos[ai*3+j]),v=[0,1,2].map(j=>pos[ci*3+j]-pos[ai*3+j]);
 const area=.5*Math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);
 minArea=Math.min(minArea,area);if(area<=1e-18)areaZero++;
 const ua=uv[ai*2],va=uv[ai*2+1],ub=uv[bi*2],vb=uv[bi*2+1],uc=uv[ci*2],vc=uv[ci*2+1];
 if((ub-ua)*(vc-va)-(vb-va)*(uc-ua)===0)uvZero++;
}
const material=q.getMaterial(),nt=material.getNormalTexture(),orm=material.getMetallicRoughnessTexture();
if(!nt||!orm)throw Error('Missing normal or metallic-roughness PNG');
const textureRows=[];
for(const [semantic,texture,path]of [['NORMAL',nt,H+'textures/original-rubber-baked-tangent-normal.png'],['ORM',orm,H+'textures/original-rubber-baked-metallic-roughness.png']]){
 const embedded=texture.getImage(),original=await fs.readFile(path);
 textureRows.push({semantic,embedded_bytes:embedded.length,embedded_sha256:sha(embedded),source_sha256:sha(original),source_exact:sha(embedded)===sha(original)});
 if(!textureRows.at(-1).source_exact)throw Error('Embedded texture differs');
}
const bytes=await fs.readFile(file),valid=await validator.validateBytes(new Uint8Array(bytes),{uri:file});
const report={component_id:'MOTO-TYRE-FRONT-001',revision:'front-tyre-v3',export_sha256:sha(bytes),export_bytes:bytes.length,
 actual_triangles:ib.length/3,actual_vertices:pos.length/3,zero_area_triangles:areaZero,zero_normalmap_UV_triangles:uvZero,min_triangle_area_m2:minArea,
 max_abs_N_dot_T:maxDot,invalid_tangent_frames:badFrames,normalmap_scale:material.getNormalScale(),normalmap_UV_set:material.getNormalTextureInfo().getTexCoord(),
 baseColor_linear:material.getBaseColorFactor(),textures:textureRows,glTF_errors:valid.issues.numErrors,glTF_warnings:valid.issues.numWarnings,messages:valid.issues.messages,
 geometry_and_UV_preserved:preserve.all_oriented_triangle_corners_POSITION_N_UV0_and_world_matrix_exact,
 technical_passed:!areaZero&&!uvZero&&!badFrames&&maxDot<.002&&!valid.issues.numErrors&&textureRows.every(x=>x.source_exact),
 material_reflectance_or_tyre_mould_measured:false,installed_fit_received:false,mobile_qualified:false,art_accepted:false};
await fs.writeFile(O+'geometry-material-buffer-check.json',JSON.stringify(report,null,2)+'\n');
if(!report.technical_passed)throw Error('Actual export check failed');
console.log('FRONT_TYRE_V3_ACTUAL_BUFFERS',JSON.stringify(report));
