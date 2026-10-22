"""Sample actual transformed plate triangles at historical annulus witness points; no fit claim."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');K='engine-protection-exterior-context-v2';D=R/'creative/research'/K;H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;bpy.ops.wm.open_mainfile(filepath=str(H/'integration-wrapper.blend'));bpy.context.view_layer.update();meta=json.loads((D/'native-links-and-transforms.json').read_text());prior=json.loads((D/'source-snapshots/guide-build-report.json').read_text());by={r['key']:r for r in meta['objects']};rows=[]
for role,key in [('terminalA','engine-protection-terminal-a'),('terminalB','engine-protection-terminal-b'),('centreplate','engine-protection-centre-plate')]:
 ob=next(o for o in bpy.context.scene.objects if o.name==by[key]['object']);mesh=ob.data;mesh.calc_loop_triangles();bvh=BVHTree.FromPolygons([ob.matrix_world@v.co for v in mesh.vertices],[tuple(t.vertices)for t in mesh.loop_triangles],all_triangles=True)
 pts=[Vector(q['nominal_tube_end_annulus_sample_m'])for w in prior['contact_witnesses']if w['plate']==role for q in w['samples']]if role!='centreplate'else[Vector((i*.005,0,-.01))for i in range(-8,9)]
 ds=[bvh.find_nearest(p)[3]for p in pts];assert min(ds)>.0029 and max(ds)<.0031,(role,min(ds),max(ds));rows.append({'part':key,'samples':len(ds),'minimum_sampled_distance_m':min(ds),'maximum_sampled_distance_m':max(ds),'scope':'Nearest actual native plate triangles at specified nominal tube points only; not complete collision/contact/fit proof.'})
(O/'open-joint-witness.json').write_text(json.dumps({'native_sha256':hashlib.sha256((H/'integration-wrapper.blend').read_bytes()).hexdigest(),'nominal_review_gap_m':.003,'actual_triangle_sample_checks':rows,'source_triangles_unchanged':True,'not_measured_OEM_clearance':True,'fit_qualified':False,'protocol_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
