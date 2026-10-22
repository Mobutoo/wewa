import bpy,json,hashlib,collections,sys
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;B=O/'lh-donor-lower-apron-v2.blend';G=O/'lh-donor-lower-apron-v2.glb'
from mathutils.kdtree import KDTree
bpy.ops.wm.open_mainfile(filepath=str(B))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];ref=[];source_triangles=[]
for ob in meshes:
 me=ob.data;me.calc_loop_triangles();coords=[tuple(ob.matrix_world@v.co) for v in me.vertices];ref.extend(coords);source_triangles.extend(tuple(coords[i] for i in t.vertices) for t in me.loop_triangles)
unique=list(set(ref));tree=KDTree(len(unique))
for i,p in enumerate(unique):tree.insert(p,i)
tree.balance()
parents=list(range(len(unique)))
def root(i):
 while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
 return i
for i,p in enumerate(unique):
 for co,j,delta in tree.find_range(p,2e-7):
  a0,b0=root(i),root(j)
  if a0!=b0:parents[max(a0,b0)]=min(a0,b0)

# All exported corners are matched to actual source positions within 1 micrometre.
def key(points):return tuple(sorted(root(tree.find(p)[1]) for p in points))
a=collections.Counter(key(t) for t in source_triangles);na=len(source_triangles);source_mesh_count=len(meshes)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(G));b=collections.Counter();nb=0;maxdelta=0
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 me=ob.data;me.calc_loop_triangles();mapped=[]
 for v in me.vertices:
  co,index,delta=tree.find(ob.matrix_world@v.co);maxdelta=max(maxdelta,delta);mapped.append(root(index))
 for t in me.loop_triangles:b[tuple(sorted(mapped[i] for i in t.vertices))]+=1;nb+=1
report=dict(source_triangles=na,export_triangles=nb,triangle_position_multiset_equal=a==b,maximum_vertex_delta_m=maxdelta,source_meshes=source_mesh_count,export_meshes=sum(o.type=='MESH' for o in bpy.context.scene.objects),source_sha256=hashlib.sha256(B.read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(G.read_bytes()).hexdigest(),missing_triangles=sum((a-b).values()),added_triangles=sum((b-a).values()),coincident_vertex_comparison_tolerance_m=2e-7,scope='Actual GLB reimport triangle parity with nearest native vertex, tolerance 1 micrometre; no art or OEM fit acceptance')
(O/'child-parity.json').write_text(json.dumps(report,indent=2));assert na==nb and a==b and maxdelta<1e-6,report
