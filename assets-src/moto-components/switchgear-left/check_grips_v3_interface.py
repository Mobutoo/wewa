"""Read-only source-hashed comparison with changed grip flanges; no source saved."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];base=HERE.parent
grip=base/'handlebar-grips/handlebar-grips-v3.blend';paths={'left':HERE/'switchgear-left-v2.blend','right':base/'switchgear-right/switchgear-right-v1.blend'}
assert hashlib.sha256(grip.read_bytes()).hexdigest()=='8ba577ea4078850569394d7d17e6e6d868e590bb287b329da3c0600706351381'
rows=[]
def tree(o,matrix=None):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();M=matrix if matrix is not None else o.matrix_world;t=BVHTree.FromPolygons([M@v.co for v in m.vertices],[tuple(p.vertices) for p in m.loop_triangles],all_triangles=True);ev.to_mesh_clear();return t
for side,path in paths.items():
 bpy.ops.wm.open_mainfile(filepath=str(path));coll=bpy.data.collections['WEWA_SWITCHGEAR_'+side.upper()];bodies=[o for o in coll.all_objects if o.type=='MESH' and ('shell - editable' in o.name or 'button' in o.name or 'rocker' in o.name or 'tongue' in o.name)]
 if not bodies:raise Exception('No switch bodies')
 bpy.context.view_layer.update();shells={o.name:tree(o) for o in bodies};name=side.title()+' rubber grip - editable candidate'
 with bpy.data.libraries.load(str(grip),link=False) as (a,b):assert name in a.objects;b.objects=[name]
 obj=b.objects[0];bpy.context.scene.collection.objects.link(obj);bpy.context.view_layer.update();E=Vector((.340 if side=='left' else -.340,.085,.105));I=Vector((-.9166959524 if side=='left' else .9166959524,-.3995854259,0));poses=[]
 for angle in ([0] if side=='left' else [0,-10,-20,-30,-40,-50]):
  matrix=Matrix.Translation(E)@Matrix.Rotation(math.radians(angle),4,I)@Matrix.Translation(-E);t=tree(obj,matrix);counts={n:len(t.overlap(s)) for n,s in shells.items()};poses.append({'rotation_about_inward_axis_degrees':angle,'actual_triangle_crossings':counts})
 rows.append({'side':side,'switch_source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'switch_bodies_tested':list(shells),'poses':poses})
report={'grip_source_sha256':hashlib.sha256(grip.read_bytes()).hexdigest(),'scope':'Read-only BVH actual source triangle surface crossings. New estimated 46mm grip flanges vs current switch shells and buttons; RH opening follows corrected negative inward-axis rotation. No clearance volume or exact fit certification. No source saved.','sides':rows,'all_clear':all(not any(p['actual_triangle_crossings'].values()) for r in rows for p in r['poses']),'art_accepted':False}
(ROOT/'creative/reviews/switchgear-left-v2/grips-v3-interface-check.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_clear'],report;print('GRIPS_V3_SWITCH_INTERFACE_CLEAR')
