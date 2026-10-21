"""Read-only actual candidate optical stack and shell contacts."""
import bpy,json,hashlib,itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/mirror-left-v1';path=HERE/'mirror-left-head-study.blend';j=json.loads((OUT/'head-study-check.json').read_text());assert hashlib.sha256(path.read_bytes()).hexdigest()==j['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(path));names=[r['object'] for r in j['geometry']];trees={}
for name in names:
 o=bpy.data.objects[name];o.data.calc_loop_triangles();trees[name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
rows=[{'objects':[a,b],'actual_triangle_crossings':len(trees[a].overlap(trees[b]))} for a,b in itertools.combinations(names,2)];C=Vector(j['head_frame_world']['centre_m']);N=Vector(j['head_frame_world']['normal_toward_rider_N']);layers=[]
for name,t in trees.items():
 origin=C-N*.10;offset=-.10
 for k in range(8):
  hit=t.ray_cast(origin,N,.15)
  if hit[0] is None:break
  d=(hit[0]-C).dot(N);layers.append({'object':name,'centreline_depth_m':d});origin=hit[0]+N*.000001
layers.sort(key=lambda a:a['centreline_depth_m']);glass=[r['centreline_depth_m'] for r in layers if 'finite thickness' in r['object']];coat=[r['centreline_depth_m'] for r in layers if 'reflector' in r['object']];assert len(glass)==2 and len(coat)==2,(glass,coat);thickness=glass[1]-glass[0];gap=glass[0]-coat[1]
result={'source_sha256':j['source_sha256'],'scope':'Actual source BVH pairwise surface crossings plus measured centreline optical stack. Candidate dimensions only. Glass/source world geometry read directly, no source saved.','pairwise_contacts':rows,'centreline_optical_stack':layers,'measured_glass_thickness_m':thickness,'measured_glass_to_reflector_gap_m':gap,'actual_glass_thickness_matches_working_2_5mm':abs(thickness-.0025)<.000002,'reflector_separate_behind_glass':gap>0,'all_pairs_clear':all(r['actual_triangle_crossings']==0 for r in rows),'art_accepted':False};(OUT/'head-interface-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert result['all_pairs_clear'] and result['actual_glass_thickness_matches_working_2_5mm'] and result['reflector_separate_behind_glass'],result
