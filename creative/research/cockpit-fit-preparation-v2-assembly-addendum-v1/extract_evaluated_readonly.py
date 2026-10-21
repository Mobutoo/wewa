"""Fresh source/assembly evaluated arrays. No transforms, saves, renders or export."""
import bpy,json,hashlib
import numpy as np
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assembly=R/'assets-src/moto-components/cockpit-current-review-v2/cockpit-current-review-v2.blend'
assert sha(assembly)=='849f4121146889c2976b3378c3177846a0025532ee8531ea13c70d9951b00f98'
entries=[('loop','assets-src/moto-components/cockpit-cables/cockpit-cables-v2.blend','WEWA_COCKPIT_CABLES_PARTIAL','Visible ignition pigtail','cockpit-cables-v2'),('cover','assets-src/moto-components/instruments/instruments-v3.blend','WEWA_INSTRUMENTS_SEPARATE_PARTS','Shaped central cluster cover','instruments-v3'),('visor','assets-src/moto-components/instrument-visor/instrument-visor-v1.blend','WEWA_INSTRUMENT_VISOR','Visor finite smoked curved shell','instrument-visor')]
arrays={};metadata=[]
def extract(ob,key):
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(deps);me=ev.to_mesh()
 try:
  me.calc_loop_triangles();local=np.asarray([list(v.co)for v in me.vertices],dtype=np.float32);world=np.asarray([list(ev.matrix_world@v.co)for v in me.vertices],dtype=np.float32);tris=np.asarray([list(t.vertices)for t in me.loop_triangles],dtype=np.int32)
  for n,a in [('local',local),('world',world),('triangles',tris),('matrix_world',np.asarray([list(row)for row in ev.matrix_world],dtype=np.float32))]:arrays[key+'__'+n]=a
  return {'object':ob.name,'vertices':len(local),'triangles':len(tris),'world_matrix':[list(row)for row in ev.matrix_world],'array_sha256':{n:hashlib.sha256(arrays[key+'__'+n].tobytes()).hexdigest()for n in ['local','world','triangles','matrix_world']}}
 finally:ev.to_mesh_clear()
for key,source,collection,prefix,asset in entries:
 path=R/source;before=sha(path);bpy.ops.wm.open_mainfile(filepath=str(path))
 activated=[]
 for col in bpy.data.collections:
  if col.hide_viewport:activated.append(col.name);col.hide_viewport=False
 bpy.context.view_layer.update()
 matches=[o for o in bpy.data.collections[collection].all_objects if o.type=='MESH'and o.name.startswith(prefix)];assert len(matches)==1,(key,[o.name for o in matches])
 row={'key':key,'source':source,'source_sha256':before,'source_guides_activated_in_memory':activated,'source_evaluated':extract(matches[0],'source_'+key)}
 assert sha(path)==before;metadata.append(row)
bpy.ops.wm.open_mainfile(filepath=str(assembly))
activated=[]
for col in bpy.data.collections:
 if col.hide_viewport:activated.append(col.name);col.hide_viewport=False
bpy.context.view_layer.update();objects=list(bpy.data.collections['MOTORCYCLE18_LINKED_REVIEW_COPIES'].all_objects)
for key,source,collection,prefix,asset in entries:
 matches=[o for o in objects if o.type=='MESH'and o.name.startswith('M18 ['+asset+'] '+prefix)];assert len(matches)==1,(key,[o.name for o in matches]);row=next(x for x in metadata if x['key']==key);row['assembly_evaluated']=extract(matches[0],'assembly_'+key)
 comparisons={}
 for field in ['local','world','triangles','matrix_world']:
  a=arrays['source_'+key+'__'+field];b=arrays['assembly_'+key+'__'+field];comparisons[field]={'same_shape':a.shape==b.shape,'bit_identical':np.array_equal(a,b),'max_absolute_delta':float(np.max(np.abs(a.astype(np.float64)-b)))if a.shape==b.shape else None}
 row['source_vs_assembly']=comparisons
np.savez_compressed(H/'evaluated-arrays.npz',**arrays)
assert sha(assembly)=='849f4121146889c2976b3378c3177846a0025532ee8531ea13c70d9951b00f98'
(H/'evaluated-source-assembly.json').write_text(json.dumps({'assembly_path':str(assembly.relative_to(R)),'assembly_sha256':sha(assembly),'tool_sha256':sha(__file__),'array_archive_sha256':sha(H/'evaluated-arrays.npz'),'assembly_hidden_collections_activated_in_memory':activated,'entries':metadata,'source_saved_or_rendered':False},indent=2)+'\n')
print('EVALUATED_PARITY',[(x['key'],x['source_vs_assembly'])for x in metadata],flush=True)
