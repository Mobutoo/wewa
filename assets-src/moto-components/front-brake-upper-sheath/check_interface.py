"""Read-only conditional short sheath/immutable own guide checks. No installed fit."""
from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/front-brake-upper-sheath-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();final='--final'in sys.argv;B=json.loads((H/('build-report.json'if final else'geometry-report.json')).read_text());P=json.loads((H/'parameters.json').read_text());source=H/('front-brake-upper-sheath-v1.blend'if final else'front-brake-upper-sheath-v1-geometry.blend');assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import tree_world
G=bpy.data.collections['FRONT_BRAKE_UPPER_IMMUTABLE_WORLD_SNAPSHOTS_NOT_EXPORTED'];G.hide_viewport=False;o=bpy.data.objects[B['geometry'][0]['name']];N=P['length_samples'];K=P['radial_samples'];offset=(N+1)*K
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

# Mid-wall points, not lumen centre points: a surrounding solid is distinct from a valid hollow lumen.
points=[(o.data.vertices[i*K+j].co+o.data.vertices[offset+i*K+j].co)/2 for i in range(0,N+1,16)for j in range(0,K,12)]
pivot=Vector(json.loads((R/P['brake_report']).read_text())['preflight']['pivot_world_m']);poses=[]
for deg in P['inspection_brake_pull_degrees']:
 delta=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(deg)*P['lever_pull_world_Z_sign'],4,'Z')@Matrix.Translation(-pivot)
 for g in G.objects:g.matrix_world=delta if g['snapshot_group']=='levermoving'else Matrix.Identity(4)
 bpy.context.view_layer.update();wiretree=tree_world(o);rows=[]
 for g in G.objects:
  tree=tree_world(g);crossings=len(wiretree.overlap(tree));counts={k:0 for k in['inside','outside','boundary','ambiguous']}
  for p in points:counts[classify(tree,o.matrix_world@p)]+=1
  row={'guide':g['source_object'],'surface_crossing_pairs':crossings,'mid_wall_samples_vs_guide':counts};rows.append(row);assert crossings==0 and counts['inside']==counts['boundary']==counts['ambiguous']==0,row
 poses.append({'brake_pull_degrees_estimated':deg,'rows':rows})
r={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':B['export_sha256'],'input_brake_sha256':P['brake_source_sha256'],'input_instruments_sha256':P['instruments_source_sha256'],'known_closed_cube_witness':w,'boundary_threshold_m':eps,'ray_progress_step_rule':'max(100nm,8timesfloat32ULPofhitcoordinate); ray advancement only, not fit tolerance','mid_wall_samples_per_pose':len(points),'poses':poses,'scope':'Actual retained outer-jacket closed wall volume versus own immutable guide snapshots in five conditional related lever poses. Native surface BVH plus sampled wall-point parity; no reciprocal exhaustive containment or coplanar contact certification. Artificial distal review cut, 0.2mm working control gap; no ferrule/boot/innerwire/steering flex or real RDC installed fit.','art_accepted':False};(O/('conditional-interface-check-final.json'if final else'conditional-interface-check.json')).write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==B['source_sha256'];print(json.dumps({'source_sha256':sha(source),'poses':len(poses),'guides_per_pose':len(G.objects),'mid_wall_samples':len(points),'all_passed':True}))
