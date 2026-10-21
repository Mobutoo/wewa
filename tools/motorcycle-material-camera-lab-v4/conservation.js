// Read-only content fingerprints, also imported into the live frozen-v2 control page.
// GPU effects/compiled defines and receiveShadows are deliberately outside material serialization.
export function canonical(value, omitUniqueIds=false) {
  if(ArrayBuffer.isView(value))return Array.from(value);
  if(Array.isArray(value))return value.map(v=>canonical(v,omitUniqueIds));
  if(value&&typeof value==='object')return Object.fromEntries(Object.keys(value).sort()
    .filter(k=>!omitUniqueIds||k!=='uniqueId').map(k=>[k,canonical(value[k],omitUniqueIds)]));
  return value;
}
export async function digest(value) {
  const bytes=typeof value==='string'?new TextEncoder().encode(value):
    ArrayBuffer.isView(value)?new Uint8Array(value.buffer,value.byteOffset,value.byteLength):new Uint8Array(value);
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
}
export function actualMeshes(scene) {
  return scene.meshes.filter(m=>m.getTotalVertices()>0).sort((a,b)=>a.name.localeCompare(b.name)||a.id.localeCompare(b.id));
}
async function bufferRecord(data) {
  if(data===null||data===undefined)return null;
  const array=ArrayBuffer.isView(data)?data:Float64Array.from(data);
  return {type:array.constructor.name,items:array.length,bytes:array.byteLength,sha256:await digest(array)};
}
export async function snapshot(lab) {
  const meshes=actualMeshes(lab.scene), rows=[];
  for(const m of meshes){
    const buffers={};
    for(const kind of (m.sourceMesh??m).getVerticesDataKinds().sort())buffers[kind]=await bufferRecord(m.getVerticesData(kind));
    rows.push({name:m.name,id:m.id,class:m.getClassName(),geometry_source:m.sourceMesh?.name??m.name,parent:m.parent?.name??null,vertices:m.getTotalVertices(),
      triangles:m.getTotalIndices()/3,buffers,indices:await bufferRecord(m.getIndices()),
      world_matrix:Array.from(m.computeWorldMatrix(true).m),
      pivot_matrix:Array.from(m.getPivotMatrix().m),position:m.position.asArray(),scaling:m.scaling.asArray(),
      rotation:m.rotation.asArray(),rotation_quaternion:m.rotationQuaternion?.asArray()??null,
      material:m.material?.id??null,submeshes:m.subMeshes.map(s=>({material_index:s.materialIndex,
        vertices_start:s.verticesStart,vertices_count:s.verticesCount,index_start:s.indexStart,index_count:s.indexCount}))});
  }
  const materials=[...new Set(meshes.map(m=>m.material).filter(Boolean))].sort((a,b)=>a.id.localeCompare(b.id));
  const serialized=materials.map(m=>({id:m.id,name:m.name,class:m.getClassName(),value:m.serialize()}));
  const materialRecords=await Promise.all(serialized.map(async m=>({id:m.id,name:m.name,class:m.class,
    serialized_sha256:await digest(JSON.stringify(canonical(m.value))),
    semantic_sha256:await digest(JSON.stringify(canonical(m.value,true)))})));
  const camera=lab.camera, scene=lab.scene;
  const environment={camera:{position:camera.position.asArray(),target:camera.getTarget().asArray(),up:camera.upVector.asArray(),
    fov:camera.fov,minZ:camera.minZ,maxZ:camera.maxZ,viewport:[camera.viewport.x,camera.viewport.y,camera.viewport.width,camera.viewport.height]},
    hdr_url:scene.environmentTexture?.url,rotation_y:scene.environmentTexture?.rotationY,intensity:scene.environmentIntensity,
    image_processing:scene.imageProcessingConfiguration.serialize(),clear_color:scene.clearColor.asArray(),right_handed:scene.useRightHandedSystem};
  return {schema:'wewa.runtime-content-conservation.v1',mesh_count:rows.length,triangles:rows.reduce((s,r)=>s+r.triangles,0),
    meshes:rows,materials:materialRecords,environment,
    geometry_normals_allUV_tangents_indices_matrices_assignments_sha256:await digest(JSON.stringify(canonical(rows))),
    materials_serialized_sha256:await digest(JSON.stringify(canonical(serialized))),
    materials_semantic_sha256:await digest(JSON.stringify(canonical(serialized,true))),
    camera_HDR_processing_sha256:await digest(JSON.stringify(canonical(environment,true))),
    semantic_omission:'Only recursively named uniqueId keys, for fresh-page neutral comparison. W0/W1 use the full serialized hash.',
    excluded_expected_shader_state:'Compiled effects/defines and receiveShadows are not PBR settings; shadow roles are reported separately.'};
}
