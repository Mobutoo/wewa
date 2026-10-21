"""Original constrained skin sampling: local pad rings, whole silhouette constraint.
No remesh closes a rejected volume; the two surface disks and rim form a closed cup.
"""
import math
import numpy as np
from collections import Counter,defaultdict
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.geometry import delaunay_2d_cdt

def patch_cup(outline,pads,height,wall=.003,rim=.0035,spacing=.0012,post_radius=.0051,root_radius=.0006,lip_radius=.0005,face_radius=.0066,foot_radius=.0095):
 def disk(poly,back):
  # CCW outer face defines the inclusion domain. Each pad ring is an edge constraint.
  if sum(poly[i].x*poly[(i+1)%len(poly)].y-poly[(i+1)%len(poly)].x*poly[i].y for i in range(len(poly)))<0:poly=list(reversed(poly))
  n=len(poly);vv=[p.copy()for p in poly];edges=[];face=[list(range(n))]
  kd=KDTree(n)
  for i,p in enumerate(poly):kd.insert(Vector((p.x,p.y,0)),i)
  kd.balance()
  px=np.array([q.x for q in poly]);py=np.array([q.y for q in poly]);qx=np.roll(px,-1);qy=np.roll(py,-1);dy=qy-py;den=np.where(np.abs(dy)>1e-20,dy,1.)
  def inside(p):return int(np.count_nonzero(((py>p.y)!=(qy>p.y))&(p.x<(qx-px)*(p.y-py)/den+px)))%2==1
  for pad in pads:
   c=pad['centre']
   if not back:vv.append(c.copy())
   radii=sorted(set([.002,.0031,.0033,.0035,.0045,.0055,post_radius+root_radius,face_radius]+[face_radius+(foot_radius-face_radius)*k/32 for k in range(1,33)]+[foot_radius+x for x in [.0003,.0007,.0013,.002,.0028,.0037,.0047]]))
   if back:radii=[r for r in radii if r>=post_radius+root_radius]
   for radius in radii:
    ring=[]
    for k in range(128):
     a=math.tau*k/128;p=c+Vector((math.cos(a),math.sin(a)))*radius
     if inside(p)and kd.find(Vector((p.x,p.y,0)))[2]>2e-6:ring.append(len(vv));vv.append(p)
     else:ring.append(None)
    for k,i in enumerate(ring):
     j=ring[(k+1)%128]
     if i is not None and j is not None and inside((vv[i]+vv[j])*.5):edges.append((i,j))
  xmin=min(p.x for p in poly);xmax=max(p.x for p in poly);ymin=min(p.y for p in poly);ymax=max(p.y for p in poly);row=0;y=ymin
  while y<=ymax:
   x=xmin+(spacing*.5 if row%2 else 0)
   while x<=xmax:
    p=Vector((x,y))
    if inside(p)and min((p-q['centre']).length for q in pads)>foot_radius+.0052 and kd.find(Vector((x,y,0)))[2]>spacing*.45:vv.append(p)
    x+=spacing
   row+=1;y+=spacing*math.sqrt(3)/2
  cv,ce,cf,*_=delaunay_2d_cdt([p*1000 for p in vv],edges,face,1,1e-6,False)
  cv=[p*.001 for p in cv]
  # CDT may retain triangles outside a concave face; filter the real 2D domain explicitly.
  raw_triangle_count=len(cf)
  cf=[f for f in cf if inside(sum((cv[i]for i in f),Vector((0,0)))/len(f))]
  outside_triangles_removed=raw_triangle_count-len(cf)
  if back:cf=[f for f in cf if all((sum((cv[i]for i in f),Vector((0,0)))/len(f)-pad['centre']).length>(post_radius+root_radius)*.99999 for pad in pads)]
  used=sorted({i for f in cf for i in f});lookup={old:new for new,old in enumerate(used)};coords=[cv[i]for i in used];triangles=[tuple(lookup[i]for i in f)for f in cf];counts=Counter(tuple(sorted((f[j],f[(j+1)%3])))for f in triangles for j in range(3));adj=defaultdict(list)
  for (a,b),count in counts.items():
   if count==1:adj[a].append(b);adj[b].append(a)
  assert all(len(v)==2 for v in adj.values()),'Non-simple skin boundary';remaining=set(adj);loops=[]
  while remaining:
   start=next(iter(remaining));loop=[start];prev=None;cur=start
   while True:
    nxt=next(i for i in adj[cur]if i!=prev)
    if nxt==start:break
    loop.append(nxt);prev,cur=cur,nxt;assert len(loop)<=len(adj),'Boundary traversal loop'
   remaining.difference_update(loop);loops.append(loop)
  def area(loop):return sum(coords[loop[i]].x*coords[loop[(i+1)%len(loop)]].y-coords[loop[(i+1)%len(loop)]].x*coords[loop[i]].y for i in range(len(loop)))
  loop=max(loops,key=lambda l:abs(area(l)));holes=[l for l in loops if l is not loop];assert len(holes)==(3 if back else 0),('Unexpected holes',len(holes))
  if area(loop)<0:loop.reverse()
  oa=np.array([list(coords[i])for i in loop]);ob=np.roll(oa,-1,axis=0);od=ob-oa;od2=np.sum(od*od,axis=1);contour_error=0.;worst=None
  for point in poly:
   pp=np.array(point);tt=np.clip(np.sum((pp-oa)*od,axis=1)/od2,0,1);distance=float(np.min(np.linalg.norm(pp-(oa+od*tt[:,None]),axis=1)))
   if distance>contour_error:contour_error=distance;worst=list(point)
  assert contour_error<2e-7,('Contour changed after triangulation',back,contour_error,worst)
  ia=np.array([list(p)for p in poly]);ib=np.roll(ia,-1,axis=0);di=ib-ia;di2=np.sum(di*di,axis=1);reverse_error=0.
  for point in oa:
   tt=np.clip(np.sum((point-ia)*di,axis=1)/di2,0,1);reverse_error=max(reverse_error,float(np.min(np.linalg.norm(point-(ia+di*tt[:,None]),axis=1))))
  assert reverse_error<2e-7,('Output contour leaves working input contour',back,reverse_error)
  from planar_domain_checks_v2 import check_planar_domain
  whole_domain=check_planar_domain(coords,triangles,poly,holes)
  input_area=abs(sum(poly[i].x*poly[(i+1)%len(poly)].y-poly[(i+1)%len(poly)].x*poly[i].y for i in range(len(poly))))*.5
  outer_area=abs(area(loop))*.5;hole_area=sum(abs(area(ids))*.5 for ids in holes)
  triangle_area=sum(abs((cv[f[1]].x-cv[f[0]].x)*(cv[f[2]].y-cv[f[0]].y)-(cv[f[1]].y-cv[f[0]].y)*(cv[f[2]].x-cv[f[0]].x))*.5 for f in cf)
  area_error=abs(triangle_area-(input_area-hole_area));assert area_error<1e-8,('Planar domain area changed',area_error)
  vertices=[(p.x,p.y,height(p)-(wall if back else 0))for p in coords]
  for pad in pads if back else []:
   c=pad['centre'];hole=min(holes,key=lambda ids:(sum((coords[i]for i in ids),Vector((0,0)))/len(ids)-c).length);assert len(hole)==128,('Support boundary split',len(hole));hole=sorted(hole,key=lambda i:math.atan2(coords[i].y-c.y,coords[i].x-c.x));angles=[math.atan2(coords[i].y-c.y,coords[i].x-c.x)for i in hole];inside=pad['inner_plane'];previous=hole;section=[]
   for k in range(1,25):
    a=math.pi*.5*(1-k/24);section.append((inside-root_radius+root_radius*math.sin(a),post_radius+root_radius*(1-math.cos(a))))
   section.append((lip_radius,post_radius))
   for k in range(1,17):
    a=math.pi*.5*(1-k/16);section.append((lip_radius*(1-math.cos(a)),post_radius-lip_radius+lip_radius*math.sin(a)))
   for w,r in section:
    ring=[]
    for angle in angles:ring.append(len(vertices));vertices.append((c.x+r*math.cos(angle),c.y+r*math.sin(angle),w))
    for k,i in enumerate(previous):j=(k+1)%len(previous);triangles.extend([(i,ring[k],ring[j]),(i,ring[j],previous[j])])
    previous=ring
   centre=len(vertices);vertices.append((c.x,c.y,0))
   for k,i in enumerate(previous):triangles.append((i,centre,previous[(k+1)%len(previous)]))
  return vertices,triangles,loop,{'vertices':len(vertices),'triangles':len(triangles),'boundary_vertices':len(loop),'constraints_rings_per_pad':len(radii),'ring_segments':128,'support_roots_topologically_connected':back,'CDT_coordinates_scaled_from_m_to_mm':True,'CDT_epsilon_in_coordinate_mm':1e-6,'CDT_merge_epsilon_m':1e-9,'input_outline_to_triangulated_boundary_max_m':contour_error,'triangulated_boundary_to_input_outline_max_m':reverse_error,'whole_triangle_verification':whole_domain,'outside_convex_hull_triangles_removed':outside_triangles_removed,'planar_input_area_m2':input_area,'planar_outer_boundary_area_m2':outer_area,'planar_internal_support_holes_area_m2':hole_area,'planar_kept_triangles_area_m2':triangle_area,'planar_area_error_m2':area_error,'worst_input_outline_point_uv_m':worst}
 a,af,al,ar=disk(outline,False);inner=[q*(1-rim/q.length)for q in outline];b,bf,bl,br=disk(inner,True);verts=list(a)+list(b);faces=list(af)+[tuple(len(a)+i for i in f[::-1])for f in bf];offset=len(a);ab=[];bb=[]
 for i in al:ab.append(len(verts));verts.append((a[i][0],a[i][1],0))
 for i in bl:bb.append(len(verts));verts.append((b[i][0],b[i][1],0))
 for k,i in enumerate(al):j=(k+1)%len(al);faces.append((i,ab[k],ab[j],al[j]))
 for k,i in enumerate(bl):j=(k+1)%len(bl);faces.append((offset+i,offset+bl[j],bb[j],bb[k]))
 def ordered(ids):return sorted(ids,key=lambda i:math.atan2(verts[i][1],verts[i][0]))
 A=ordered(ab);B=ordered(bb);aa=[math.atan2(verts[i][1],verts[i][0])for i in A];ba=[math.atan2(verts[i][1],verts[i][0])for i in B];i=j=0
 # Start each loop at the -pi seam, then zipper the two full cyclic rings.
 while i<len(A)or j<len(B):
  an=aa[(i+1)%len(A)]+(math.tau if i+1>=len(A)else 0);bn=ba[(j+1)%len(B)]+(math.tau if j+1>=len(B)else 0)
  if i>=len(A):an=float('inf')
  if j>=len(B):bn=float('inf')
  if an<bn:faces.append((A[i%len(A)],B[j%len(B)],A[(i+1)%len(A)]));i+=1
  else:faces.append((A[i%len(A)],B[j%len(B)],B[(j+1)%len(B)]));j+=1
 return verts,faces,{'front':ar,'back':br,'method':'Constrained Delaunay with explicit plateau/transition ring edges, separate hollow inner skin, zipper annular back rim; no voxel remesh'}
