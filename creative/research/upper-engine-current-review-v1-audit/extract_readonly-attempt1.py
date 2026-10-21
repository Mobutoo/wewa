"""Evaluate all actual seven source libraries and linked-review copies. No save/render/export.
Exact local mesh/UV/normals/attributes; world matrix tolerance is builder v2's existing1e-6 coefficient guard, not a distance or fit tolerance.
"""
from pathlib import Path
import bpy,json,hashlib,numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
snapshot=json.loads((H/'input-snapshot.json').read_text());proof=json.loads((R/snapshot['builder_proof']['path']).read_text());arrays={};rows=[]
def activate():
 names=[]
 for c in bpy.data.collections:
  if c.hide_viewport:c.hide_viewport=False;names.append(c.name)
 bpy.context.view_layer.update();return names
def savearr(key,name,a):
 a=np.asarray(a);arrays[key+'__'+name]=a
 return {'shape':list(a.shape),'dtype':str(a.dtype),'sha256':hashlib.sha256(a.tobytes()).hexdigest()}
def extract(o,key):
 deps=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(deps);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
 try:
  me.calc_loop_triangles();attrs={}
  local=np.array([tuple(v.co)for v in me.vertices],dtype=np.float32)
  matrix=np.array([list(v)for v in ev.matrix_world],dtype=np.float64)
  world=np.array([tuple(ev.matrix_world@v.co)for v in me.vertices],dtype=np.float32)
  for n,v in [('local',local),('world',world),('triangles',np.array([tuple(t.vertices)for t in me.loop_triangles],dtype=np.int32)),('matrix_world',matrix),('corner_normals',np.array([tuple(n.vector)for n in me.corner_normals],dtype=np.float32)),('loop_vertex_indices',np.array([l.vertex_index for l in me.loops],dtype=np.int32)),('polygon_material_indices',np.array([p.material_index for p in me.polygons],dtype=np.int32))]:attrs[n]=savearr(key,n,v)
  for uv in me.uv_layers:attrs['UV:'+uv.name]=savearr(key,'UV:'+uv.name,np.array([tuple(v.uv)for v in uv.data],dtype=np.float32))
  attribute_inventory=[]
  for att in me.attributes:
   prop=next((p for p in ['value','vector','color','uv']if len(att.data)and hasattr(att.data[0],p)),None)
   data=[getattr(v,prop)for v in att.data]if prop else[]
   try:arr=np.array(data);digest=savearr(key,'ATTR:'+att.name,arr)
   except Exception as ex:digest={'unread_reason':str(ex)}
   attribute_inventory.append({'name':att.name,'domain':att.domain,'data_type':att.data_type,'property':prop,'data':digest})
  lib=lambda d:str(Path(bpy.path.abspath(d.library.filepath)).resolve().relative_to(R))if d.library else None
  return {'object':o.name,'mesh':o.data.name,'object_library':lib(o),'data_library':lib(o.data),'parent':o.parent.name if o.parent else None,'hidden_render':o.hide_render,'vertices':len(local),'triangles':len(me.loop_triangles),'arrays':attrs,'attributes':attribute_inventory,'material_slots':[{'name':m.name if m else None,'library':lib(m)if m else None}for m in o.data.materials]}
 finally:ev.to_mesh_clear()
for s in proof['linked_sources']:
 path=R/s['source'];assert sha(path)==s['sha256'];bpy.ops.wm.open_mainfile(filepath=str(path));activated=activate();col=bpy.data.collections[s['source_collection']]
 for i,o in enumerate(sorted(col.all_objects,key=lambda x:x.name)):
  if o.type!='MESH':continue
  key=s['asset']+'__'+str(i);row={'key':key,'asset':s['asset'],'source':s['source'],'source_sha256':sha(path),'collection':s['source_collection'],'source_name':o.name,'guides_activated_in_memory':activated,'source_evaluated':extract(o,'source_'+key)};rows.append(row)
 assert sha(path)==s['sha256']
assembly=R/snapshot['assembly']['path'];assert sha(assembly)==snapshot['assembly']['sha256'];bpy.ops.wm.open_mainfile(filepath=str(assembly));activated=activate();copies=list(bpy.data.collections['MOTORCYCLE18_LINKED_REVIEW_COPIES'].all_objects);libraries=[{'path':str(Path(bpy.path.abspath(l.filepath)).resolve().relative_to(R)),'sha256':sha(bpy.path.abspath(l.filepath))}for l in bpy.data.libraries]
for row in rows:
 key=row['key'];name='M18 ['+row['asset']+'] '+row['source_name'];found=[o for o in copies if o.type=='MESH'and o.name==name];assert len(found)==1,(name,[o.name for o in found]);row['assembly_evaluated']=extract(found[0],'assembly_'+key);checks={}
 for field in row['source_evaluated']['arrays']:
  a=arrays['source_'+key+'__'+field];b=arrays['assembly_'+key+'__'+field];checks[field]={'same_shape':a.shape==b.shape,'bit_identical':np.array_equal(a,b),'max_absolute_delta':float(np.abs(a.astype(np.float64)-b).max())if a.size and a.shape==b.shape else None}
 row['comparisons']=checks
 row['attributes_exact']=row['source_evaluated']['attributes']==row['assembly_evaluated']['attributes']
 row['material_names_and_libraries_exact']=row['source_evaluated']['material_slots']==row['assembly_evaluated']['material_slots']
 assert row['assembly_evaluated']['data_library']==row['source']
 for field,v in checks.items():
  if field not in ['world','matrix_world']:assert v['bit_identical'],(key,field,v)
 assert row['attributes_exact']and row['material_names_and_libraries_exact'],key
 assert checks['matrix_world']['max_absolute_delta']<1e-6,(key,'existing builder coefficient guard',checks['matrix_world'])
 row['world_delta_explained_by_actual_matrix_roundoff_m']=float(np.max(np.linalg.norm((arrays['source_'+key+'__local'].astype(np.float64)@ (arrays['assembly_'+key+'__matrix_world'][:3,:3]-arrays['source_'+key+'__matrix_world'][:3,:3]).T)+(arrays['assembly_'+key+'__matrix_world'][:3,3]-arrays['source_'+key+'__matrix_world'][:3,3]),axis=1)))
expected={s['source']:s['sha256']for s in proof['linked_sources']};assert {e['path']:e['sha256']for e in libraries}==expected
np.savez_compressed(H/'evaluated-arrays.npz',**arrays)
report={'assembly':snapshot['assembly'],'builder_proof':snapshot['builder_proof'],'actual_libraries':libraries,'hidden_collections_activated_in_memory':activated,'entries':rows,'array_archive_sha256':sha(H/'evaluated-arrays.npz'),'tool_sha256':sha(__file__),'source_saved_or_exported_or_rendered':False,'matrix_policy':'No serialized matrix bit-identity assertion. Exact local geometry/attributes; actual evaluated matrix deltas reported under builder v2 existing1e-6 coefficient guard, not a mechanical fit tolerance.'}
(H/'evaluated-source-assembly.json').write_text(json.dumps(report,indent=2)+'\n')
for e in snapshot['inputs']:assert sha(R/e['path'])==e['sha256'],e['path']
print('ACTUAL_FRESH_SOURCE_COPIES',len(rows),'LIBRARIES',len(libraries),'MAX_WORLD_COMPONENT_DELTA',max(r['comparisons']['world']['max_absolute_delta']for r in rows),flush=True)
