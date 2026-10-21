"""Fresh source/assembly evaluated arrays. No transforms, saves, renders or export."""
import bpy,json,hashlib
import numpy as np
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
snapshot=json.loads((H/'input-snapshot.json').read_text());assembly=R/snapshot['assembly']['path'];assert sha(assembly)==snapshot['assembly']['sha256'];entries=json.loads((H/'geometry-targets.json').read_text())
arrays={};metadata=[]
def extract(ob,key):
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(deps);me=ev.to_mesh()
 try:
  me.calc_loop_triangles();local=np.asarray([list(v.co)for v in me.vertices],dtype=np.float32);world=np.asarray([list(ev.matrix_world@v.co)for v in me.vertices],dtype=np.float32);tris=np.asarray([list(t.vertices)for t in me.loop_triangles],dtype=np.int32)
  for n,a in [('local',local),('world',world),('triangles',tris),('matrix_world',np.asarray([list(row)for row in ev.matrix_world],dtype=np.float32))]:arrays[key+'__'+n]=a
  return {'data_library':str(Path(bpy.path.abspath(ob.data.library.filepath)).resolve().relative_to(R))if ob.data.library else None,'object_library':str(Path(bpy.path.abspath(ob.library.filepath)).resolve().relative_to(R))if ob.library else None,'local_corner_normals_sha256':hashlib.sha256(np.asarray([list(n.vector)for n in me.corner_normals],dtype=np.float32).tobytes()).hexdigest(),'object':ob.name,'vertices':len(local),'triangles':len(tris),'world_matrix':[list(row)for row in ev.matrix_world],'array_sha256':{n:hashlib.sha256(arrays[key+'__'+n].tobytes()).hexdigest()for n in ['local','world','triangles','matrix_world']}}
 finally:ev.to_mesh_clear()

def activate():
 activated=[]
 for col in bpy.data.collections:
  if col.hide_viewport:activated.append(col.name);col.hide_viewport=False
 bpy.context.view_layer.update();return activated
for source in dict.fromkeys(e['source']for e in entries):
 path=R/source;before=sha(path);bpy.ops.wm.open_mainfile(filepath=str(path));activated=activate()
 for e in [x for x in entries if x['source']==source]:
  key=e['key'];matches=[o for o in bpy.data.collections[e['collection']].all_objects if o.type=='MESH'and o.name.startswith(e['prefix'])];assert len(matches)==1,(key,[o.name for o in matches]);metadata.append({'key':key,'source':source,'source_sha256':before,'source_guides_activated_in_memory':activated,'source_evaluated':extract(matches[0],'source_'+key)})
 assert sha(path)==before
bpy.ops.wm.open_mainfile(filepath=str(assembly));activated=activate();objects=list(bpy.data.collections['MOTORCYCLE18_LINKED_REVIEW_COPIES'].all_objects)
libraries=[{'path':str(Path(bpy.path.abspath(lib.filepath)).resolve().relative_to(R)),'sha256':sha(Path(bpy.path.abspath(lib.filepath)).resolve())}for lib in bpy.data.libraries]
for e in entries:
 key=e['key'];matches=[o for o in objects if o.type=='MESH'and o.name.startswith('M18 ['+e['asset']+'] '+e['prefix'])];assert len(matches)==1,(key,[o.name for o in matches]);row=next(x for x in metadata if x['key']==key);row['assembly_evaluated']=extract(matches[0],'assembly_'+key);comparisons={}
 for field in ['local','world','triangles','matrix_world']:
  a=arrays['source_'+key+'__'+field];b=arrays['assembly_'+key+'__'+field];comparisons[field]={'same_shape':a.shape==b.shape,'bit_identical':np.array_equal(a,b),'max_absolute_delta':float(np.max(np.abs(a.astype(np.float64)-b)))if a.shape==b.shape else None}
 row['source_vs_assembly']=comparisons;row['source_vs_assembly_local_corner_normals_bit_identical']=row['source_evaluated']['local_corner_normals_sha256']==row['assembly_evaluated']['local_corner_normals_sha256'];assert row['assembly_evaluated']['data_library']==e['source']
# Independent3→5 physical-body comparison from freshly opened v3source.
oldsource=R/'assets-src/moto-components/instruments/instruments-v3.blend';oldsha=sha(oldsource);bpy.ops.wm.open_mainfile(filepath=str(oldsource));activate();oldrows=[]
for e in entries:
 if e['asset']!='instruments-v5':continue
 key=e['key'];ob=next(o for o in bpy.data.collections[e['collection']].all_objects if o.type=='MESH'and o.name.startswith(e['prefix']));oldmeta=extract(ob,'prior_source_'+key);checks={f:np.array_equal(arrays['prior_source_'+key+'__'+f],arrays['source_'+key+'__'+f])for f in ['local','world','triangles','matrix_world']};newmeta=next(x for x in metadata if x['key']==key)['source_evaluated'];oldrows.append({'key':key,'object':ob.name,'geometry_array_bit_identity_3_to_5':checks,'local_corner_normals_bit_identical':oldmeta['local_corner_normals_sha256']==newmeta['local_corner_normals_sha256'],'old':oldmeta})
# Compare exact physical copies in previous/current real assembly, no placements.
oldassembly=R/'assets-src/moto-components/cockpit-current-review-v2/cockpit-current-review-v2.blend';oldassemblysha=sha(oldassembly);bpy.ops.wm.open_mainfile(filepath=str(oldassembly));activate();objects=list(bpy.data.collections['MOTORCYCLE18_LINKED_REVIEW_COPIES'].all_objects);oldcopies=[]
for e in entries:
 key=e['key'];asset=e['asset'].replace('instruments-v5','instruments-v3');ob=next(o for o in objects if o.type=='MESH'and o.name.startswith('M18 ['+asset+'] '+e['prefix']));oldmeta=extract(ob,'prior_assembly_'+key);oldcopies.append({'key':key,'object':ob.name,'geometry_array_bit_identity_previous_to_current':{f:np.array_equal(arrays['prior_assembly_'+key+'__'+f],arrays['assembly_'+key+'__'+f])for f in ['local','world','triangles','matrix_world']},'old':oldmeta})
np.savez_compressed(H/'evaluated-arrays.npz',**arrays)
report={'assembly_path':str(assembly.relative_to(R)),'assembly_sha256':sha(assembly),'tool_sha256':sha(__file__),'array_archive_sha256':sha(H/'evaluated-arrays.npz'),'assembly_hidden_collections_activated_in_memory':activated,'actual_libraries_in_new_assembly':libraries,'entries':metadata,'prior_instruments_source':{'path':str(oldsource.relative_to(R)),'sha256':oldsha},'prior_instruments_geometry_comparisons':oldrows,'prior_assembly':{'path':str(oldassembly.relative_to(R)),'sha256':oldassemblysha},'prior_assembly_geometry_comparisons':oldcopies,'source_saved_or_rendered':False}
(H/'evaluated-source-assembly.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(assembly)==snapshot['assembly']['sha256'];assert all(all(r['geometry_array_bit_identity_3_to_5'].values())for r in oldrows);assert all(all(r['geometry_array_bit_identity_previous_to_current'].values())for r in oldcopies);assert all(r['source_vs_assembly_local_corner_normals_bit_identical']for r in metadata)
print('EVALUATED_PARITY_TARGETS',len(metadata),'OLD_GEOMETRY_UNCHANGED',len(oldrows),'ACTUAL_C5_NORMAL_TARGET_CHANGES',[r['object']for r in oldrows if not r['local_corner_normals_bit_identical']],flush=True)
