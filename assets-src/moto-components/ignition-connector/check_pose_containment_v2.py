from pathlib import Path
import bpy,json,hashlib,math,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/ignition-connector-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'geometry-report-v2.json').read_text());source=H/'ignition-connector-v2-geometry.blend';assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import tree_world
G=bpy.data.collections['CONNECTOR_OWN_WORLD_SNAPSHOTS_NOT_EXPORTED'];G.hide_viewport=False;o=bpy.data.objects[B['geometry'][0]['name']]
directions=[Vector(d).normalized()for d in[(.83,.47,.29),(.24,.91,.34),(.31,.42,.85)]];eps=1e-7
# The point test is distinct from native overlap, which can omit coplanar contact.
def classify(tree,p):
 near=tree.find_nearest(p)
 if near[0]is not None and near[3]<eps:return'boundary'
 parity=[]
 for d in directions:
  at=p.copy();hits=0
  for _ in range(256):
   hit,normal,index,distance=tree.ray_cast(at,d,10)
   if hit is None:break
   hits+=1;mag=max(abs(float(v))for v in hit);ulp=2**(math.floor(math.log2(mag))-23)if mag else 2**-149;at=hit+d*max(eps,8*ulp)
  else:raise AssertionError('Raycast did not terminate')
  parity.append(hits%2)
 return'inside'if parity==[1,1,1]else'outside'if parity==[0,0,0]else'ambiguous'
cube=BVHTree.FromPolygons([(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],all_triangles=False);w={'known_inside':classify(cube,Vector((0,0,0))),'known_outside':classify(cube,Vector((2,2,2)))};print('WITNESS_RESULT',w,flush=True);assert w=={'known_inside':'inside','known_outside':'outside'}


points=[o.matrix_world@v.co for v in list(o.data.vertices)[::128]];o.data.calc_loop_triangles()
points += [o.matrix_world@sum((o.data.vertices[i].co for i in t.vertices),Vector())/3 for t in list(o.data.loop_triangles)[::256]]
rows=[];bodytree=tree_world(o)
for g in G.objects:
 tree=tree_world(g);crossings=len(bodytree.overlap(tree));counts={k:0 for k in['inside','outside','boundary','ambiguous']}
 for p in points:counts[classify(tree,p)]+=1
 row={'guide':g['source_object'],'surface_crossing_pairs':crossings,'body_surface_sample_vs_guide':counts};rows.append(row);assert crossings==0 and counts['inside']==counts['boundary']==counts['ambiguous']==0,row
r={'source_sha256':sha(source),'export_sha256':B['export_sha256'],'closed_cube_witness':w,'sampled_body_points':len(points),'guide_checks':rows,'scope':'Surface crossings and sampled body vertices/trianglecentroids versus immutable own guide solids. Not reciprocal exhaustive containment or coplanar contact certification; pose/route artistic estimates and no installedhardware fit.','ray_progress_rule':'max100nm/8float32ULP, no geometry/contact tolerance','art_accepted':False};(O/'conditional-point-containment.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==B['source_sha256'];print('CONDITIONAL_POINT_CHECK',len(points),len(rows))
