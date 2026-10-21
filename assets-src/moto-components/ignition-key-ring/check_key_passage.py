"""Read-only conditional surface/containment checks against immutable own snapshots."""
from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/ignition-key-ring-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/('build-report.json'if'--final'in sys.argv else'geometry-report.json')).read_text());P=json.loads((H/'parameters.json').read_text());source=H/('ignition-key-ring-v1.blend'if'--final'in sys.argv else'ignition-key-ring-v1-geometry.blend');assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import tree_world
G=bpy.data.collections['KEYRING_IMMUTABLE_WORLD_GEOMETRY_SNAPSHOTS_NOT_EXPORTED'];G.hide_viewport=False;o=bpy.data.objects[B['geometry'][0]['name']];root=o.parent;M=Matrix(B['rest_keypivot_world_matrix']);Mi=M.inverted();K=B['authored_section_samples'];N=B['authored_centreline_samples']-1;directions=[Vector(d).normalized()for d in[(.83,.47,.29),(.24,.91,.34),(.31,.42,.85)]];eps=1e-7
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
centres=[sum((o.data.vertices[i*K+j].co for j in range(K)),Vector())/K for i in range(0,N+1,16)];poses=[]
for deg in P['inspection_rotor_angles_degrees']:
 delta=M@Matrix.Rotation(math.radians(deg),4,'Z')@Mi;root.matrix_world=M@Matrix.Rotation(math.radians(deg),4,'Z')
 for g in G.objects:g.matrix_world=delta if g['snapshot_group']=='keymoving'else Matrix.Identity(4)
 bpy.context.view_layer.update();wiretree=tree_world(o);rows=[]
 for g in G.objects:
  tree=tree_world(g);crossings=len(wiretree.overlap(tree));counts={k:0 for k in['inside','outside','boundary','ambiguous']}
  for p in centres:counts[classify(tree,o.matrix_world@p)]+=1
  row={'guide':g['source_object'],'surface_crossing_pairs':crossings,'wire_centreline_samples_vs_closed_guide':counts};rows.append(row);assert crossings==0 and counts['inside']==counts['boundary']==counts['ambiguous']==0,row
 poses.append({'rotor_angle_degrees_estimated':deg,'rows':rows})
r={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':B['export_sha256'],'input_ignition_sha256':P['ignition_source_sha256'],'input_instruments_sha256':P['instruments_source_sha256'],'known_closed_cube_witness':w,'boundary_threshold_m':eps,'ray_progress_step_rule':'max(100nm,8timesfloat32ULPofhitcoordinate), solely to advance past the same float32 triangle; no geometry/contact tolerance' ,'wire_centreline_samples_per_pose':len(centres),'poses':poses,'scope':'Actual retained wire closed1shell and immutable closedguide snapshots. Surfacecrossings plus sampledcentreline point parity detect wholecontainment as well as crossings; nativeBVH coplanarcontact remains unqualified. Rigid relatedpresentationstates only, no gauge/elastic/gravity or realRDC certification.','art_accepted':False};(O/('conditional-key-passage-check-final.json'if'--final'in sys.argv else'conditional-key-passage-check.json')).write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==B['source_sha256'];print(json.dumps({'source_sha256':sha(source),'poses':len(poses),'guides_per_pose':len(G.objects),'wire_centreline_samples':len(centres),'all_passed':True}))
