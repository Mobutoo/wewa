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

new=np.load(H/'evaluated-arrays.npz');oldpath=R/'assets-src/moto-components/cockpit-current-review-v1/cockpit-current-review-v1.blend';expected='323b3443f63868fbbc3bb8ca2567e4b7a31bf868126c3954ac101ff3007faa29';assert sha(oldpath)==expected
bpy.ops.wm.open_mainfile(filepath=str(oldpath))
for col in bpy.data.collections:col.hide_viewport=False
bpy.context.view_layer.update();objects=list(bpy.data.collections['MOTORCYCLE18_LINKED_REVIEW_COPIES'].all_objects);rows=[]
for key,source,collection,prefix,asset in entries:
 if key=='loop':continue
 ob=next(o for o in objects if o.type=='MESH'and o.name.startswith('M18 ['+asset+'] '+prefix));m=extract(ob,'historical_'+key);checks={}
 for field in ['local','world','triangles','matrix_world']:
  a=arrays['historical_'+key+'__'+field];b=new['assembly_'+key+'__'+field];checks[field]={'bit_identical':np.array_equal(a,b),'maximum_absolute_delta':float(np.max(np.abs(a.astype(np.float64)-b)))}
 rows.append({'key':key,'historical_evaluated':m,'historical_vs_new_assembly':checks})
np.savez_compressed(H/'historical-contact-target-arrays.npz',**arrays)
(H/'historical-contact-target-parity.json').write_text(json.dumps({'historical_assembly_sha256':sha(oldpath),'new_assembly_sha256':sha(assembly),'tool_sha256':sha(__file__),'historical_arrays_sha256':sha(H/'historical-contact-target-arrays.npz'),'new_arrays_sha256':sha(H/'evaluated-arrays.npz'),'entries':rows,'models_modified':False},indent=2)+'\n')
assert all(c['bit_identical']for r in rows for c in r['historical_vs_new_assembly'].values())
print('HISTORICAL_TARGETS_BIT_IDENTICAL',rows,flush=True)
