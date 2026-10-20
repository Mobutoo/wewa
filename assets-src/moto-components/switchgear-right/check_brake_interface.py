"""Read-only actual-source brake/switch interface sample; no acceptance claim."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/switchgear-right-v1';own=HERE/'switchgear-right-v1.blend';other=HERE.parent/'front-brake-control/front-brake-control-v1.blend'
check=json.loads((OUT/'source-geometry-check.json').read_text());assert hashlib.sha256(own.read_bytes()).hexdigest()==check['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(own));shells=[o for o in bpy.data.collections['WEWA_SWITCHGEAR_RIGHT'].objects if o.type=='MESH']
with bpy.data.libraries.load(str(other),link=False) as (a,b):b.collections=['WEWA_FRONT_BRAKE_CONTROL']
coll=b.collections[0];bpy.context.scene.collection.children.link(coll);objects=[o for o in coll.all_objects if o.type=='MESH'];lever=next(o for o in objects if o.name=='Front cable brake lever - moving candidate');lever.animation_data_clear()
def tree(o):
 dep=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dep);m=ev.to_mesh();m.calc_loop_triangles();t=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True);ev.to_mesh_clear();return t
bpy.context.view_layer.update();shelltrees={o.name:tree(o) for o in shells};rows=[]
for angle in [0,3,6,9,12]:
 lever.rotation_euler.z=-math.radians(angle);bpy.context.view_layer.update();crossings={o.name:{name:len(tree(o).overlap(t)) for name,t in shelltrees.items()} for o in objects};rows.append({'brake_pull_degrees_estimated':angle,'triangle_crossings_with_switch_bodies':crossings})
report={'switch_source_sha256':check['source_sha256'],'brake_source_sha256':hashlib.sha256(other.read_bytes()).hexdigest(),'scope':'Read-only BVH triangle-surface crossings, source geometry in shared cockpit datum. Candidate fits only, not measured assembly clearance; includes all six rigid brake objects and switch seven rigid bodies. Neither source saved.','poses':rows,'all_clear':all(not any(v for o in r['triangle_crossings_with_switch_bodies'].values() for v in o.values()) for r in rows),'art_accepted':False}
(OUT/'brake-interface-check.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_clear'],report
