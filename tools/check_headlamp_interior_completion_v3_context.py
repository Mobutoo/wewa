"""Actual v19 placed housing/protector versus v3, without guessing bulb poses."""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Matrix,Vector,Euler
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');K='headlamp-interior-completion-v3';O=R/'creative/reviews'/K
baseline=json.loads((R/'creative/reviews/whole-exterior-coverage-v19/linked-parents-check.json').read_text())
candidate=json.loads((O/'integration-fragment.json').read_text())['replacements'][0]
bpy.ops.wm.read_factory_settings(use_empty=True)
def load(row):
 p=R/row['source'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 with bpy.data.libraries.load(str(p),link=True) as (a,b):
  # Old selection wrappers exist in assembly only; these two rows use native collections.
  assert row['collection'] in a.collections,row['collection'];b.collections=[row['collection']]
 col=b.collections[0];bpy.context.scene.collection.children.link(col)
 rot=Euler(tuple(math.radians(x) for x in row['rotation_degrees']),'XYZ').to_matrix().to_4x4()
 pose=Matrix.Translation(Vector(row['translation_m']))@rot@Matrix.Diagonal(Vector((*row['scale'],1)))
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();result=[]
 for o in col.all_objects:
  if o.type!='MESH' or o.hide_render:continue
  ev=o.evaluated_get(deps);m=ev.to_mesh();v=[pose@o.matrix_world@p.co for p in m.vertices];pol=[list(p.vertices) for p in m.polygons]
  result.append({'name':o.name,'bvh':BVHTree.FromPolygons(v,pol),'min':[min(p[i] for p in v) for i in range(3)],'max':[max(p[i] for p in v) for i in range(3)]});ev.to_mesh_clear()
 return result
parts=load(candidate);results=[]
for key in ['headlamp-housing-v2','headlamp-front-protector-v2']:
 row=next(p for p in baseline['parents'] if p['key']==key);other=load(row)
 for a in parts:
  for b in other:
   pairs=a['bvh'].overlap(b['bvh'])
   results.append({'candidate_mesh':a['name'],'existing_parent':key,'existing_mesh':b['name'],'actual_surface_triangle_intersections':len(pairs),'candidate_bounds':[a['min'],a['max']],'existing_bounds':[b['min'],b['max']]})
standalone=json.loads((R/'creative/reviews/headlamp-interior-context-v1/build-report.json').read_text())
report={'source_sha256':candidate['sha256'],'baseline':'whole-exterior-coverage-v19','actual_placed_parent_keys_checked':['headlamp-housing-v2','headlamp-front-protector-v2'],'checks':results,'no_surface_intersections_with_checked_placed_parts':all(r['actual_surface_triangle_intersections']==0 for r in results),'separate_bulb_cap_cage_in_baseline':False,'separate_bulb_cap_cage_mounted_nonobstruction':'not established: no mounted matrices in baseline140 or earlier standalone context; no invented poses','previous_context_limit':standalone.get('placement_notes',standalone.get('limitations',[])),'positive_aperture_and_silver_surface_probes':'native-export-parity.json; actual main/pilot rays pass while left/upper field rays hit','scope':'Only actual source geometry with v19 recorded transforms; not universal compatibility, hidden interfaces, art or optical qualification.'}
(O/'placed-context-nonobstruction.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'pairs_checked':len(results),'intersections':sum(p['actual_surface_triangle_intersections'] for p in results),'separate_bulb_cap_cage_pose':'absent from v19'}))
