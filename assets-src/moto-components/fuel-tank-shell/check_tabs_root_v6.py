"""Read-only actual intersection localization; estimated weldguide, never fitapproval."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/fuel-tank-shell-study-v6';j=json.loads((O/'build-report.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'fuel-tank-shell-study-v6.blend';assert sha(source)==j['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));sets=[]
for name in j['objects']:
 o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles();vs=[tuple(o.matrix_world@v.co)for v in m.vertices];tri=[tuple(t.vertices)for t in m.loop_triangles];sets.append((vs,tri,BVHTree.FromPolygons(vs,tri,all_triangles=True,epsilon=0)))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def hit(a,b,t):
 d=sub(b,a);e1=sub(t[1],t[0]);e2=sub(t[2],t[0]);h=cross(d,e2);det=dot(e1,h);scale=math.sqrt(dot(d,d)*dot(e1,e1)*dot(e2,e2))
 if abs(det)<=scale*1e-12:return None
 s=sub(a,t[0]);u=dot(s,h)/det;q=cross(s,e1);v=dot(d,q)/det;f=dot(e2,q)/det;eps=1e-9
 if u>=-eps and v>=-eps and u+v<=1+eps and -eps<=f<=1+eps:return tuple(a[i]+f*d[i]for i in range(3))
 return None
rows=[]
for ai,bi in [(0,1),(0,2),(1,2)]:
 av,at,ab=sets[ai];bv,bt,bb=sets[bi];pairs=ab.overlap(bb);points=[];confirmed=0
 for ia,ib in pairs:
  a=[av[k]for k in at[ia]];b=[bv[k]for k in bt[ib]];pp=[]
  for tri,other in [(a,b),(b,a)]:
   for p,q in zip(tri,tri[1:]+tri[:1]):
    h=hit(p,q,other)
    if h is not None:pp.append(h)
  if pp:confirmed+=1;points+=pp
 rows.append({'a':j['objects'][ai],'b':j['objects'][bi],'BVH_candidatepairs':len(pairs),'confirmed_pairs_with_segmenttriangle_points':confirmed,'points_bbox_m':[[min(p[i]for p in points)for i in range(3)],[max(p[i]for p in points)for i in range(3)]]if points else None,'points_first50_m':points[:50]})
report={'source_sha256':j['source_sha256'],'pairs':rows,'method':'ActualFloat32source worldpositions, BVHepsilon0 then doubleprecision edge/triangle localization. Relativeparallel threshold1e-12, barycentric1e-9; coplanar containment notcertified.','disposition':'Guideposes only. Any rootintersection is declared, not ignored or passed as physicalfit. No exactweld/mount or lowerpan established.','art_accepted':False};(O/'tab-root-interface-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert sha(source)==j['source_sha256']
