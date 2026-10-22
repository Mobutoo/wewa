import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
O=Path(__file__).resolve().parent;R=Path('/workspace/wewa');B=O/'lh-donor-lower-apron-v2.blend';bpy.ops.wm.open_mainfile(filepath=str(B));ob=next(o for o in bpy.context.scene.objects if o.type=='MESH');ob.data.calc_loop_triangles();tree=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(t.vertices)for t in ob.data.loop_triangles],all_triangles=True)
probes=[]
for name,p,expected in [('magneto cavity centre',(-.05,0),False),('magneto cavity upper',(-.03,.02),False),('rear region not arbitrarily closed',(.07,0),False),('lower apron exterior',(0,-.09),True),('lower apron aft',(.08,-.09),True),('service mouth exact source station',(-.07436,-.0924),False)]:
 hit=tree.ray_cast(Vector((p[0],p[1],.15)),Vector((0,0,-1)),.30)[0];probes.append(dict(name=name,xy_m=p,expected_hit=expected,actual_hit=hit is not None));assert (hit is not None)==expected,(name,hit)
source=R/'assets-src/moto-components/crankcase-lh-major-outer-envelope-donor-v1/child-candidate.blend'
with bpy.data.libraries.load(str(source),link=False) as(a,b):b.objects=['MAJOR_LH_DONOR_EXTERIOR_PERIPHERAL_CAST_WALLS_OPEN_ENGINE_VOID']
old=b.objects[0];newtree=KDTree(len(ob.data.vertices))
for i,v in enumerate(ob.data.vertices):newtree.insert(v.co,i)
newtree.balance();region=[v.co for v in old.data.vertices if v.co.y>-.06];maxdelta=max(newtree.find(v)[2]for v in region);assert maxdelta<1e-7,maxdelta
(O/'apron-openings-and-preservation.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(B.read_bytes()).hexdigest(),probes=probes,untouched_upper_region_vertices=len(region),untouched_upper_region_max_vertex_delta_m=maxdelta,scope='Actual changed child BVH rays; only the photograph-bounded lower exterior band is filled, not magneto cavity or output area. No physical mating fit certified.'),indent=2))
print('openings and source preservation passed',maxdelta)
