"""Original formed panel, constrained two-hole skin and explicit rolled perimeter.
No photographed texture, global bevel, voxel repair or hidden mounting hardware.
"""
import math,sys
from collections import Counter,defaultdict
import numpy as np
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from planar_domain_checks import check_planar_domain

def rounded_outline(P):
 vertices=[Vector(p)for p in P['working_outline_vertices_uv_m']];radii=P['working_corner_radii_m'];points=[];normals=[]
 for i,(b,r)in enumerate(zip(vertices,radii)):
  a=vertices[i-1];c=vertices[(i+1)%len(vertices)];incoming=(b-a).normalized();outgoing=(c-b).normalized();turn=math.acos(max(-1,min(1,incoming.dot(outgoing))));distance=r*math.tan(turn/2);start=b-incoming*distance;centre=start+Vector((-incoming.y,incoming.x))*r;starta=math.atan2(start.y-centre.y,start.x-centre.x)
  for j in range(max(8,math.ceil(turn/.04))):
   angle=starta+turn*j/max(8,math.ceil(turn/.04));normal=Vector((math.cos(angle),math.sin(angle)));points.append(centre+r*normal);normals.append(normal)
  end=centre+r*Vector((math.cos(starta+turn),math.sin(starta+turn)));nextb=c;nextout=(vertices[(i+2)%len(vertices)]-c).normalized();nextturn=math.acos(max(-1,min(1,outgoing.dot(nextout))));nextstart=c-outgoing*(radii[(i+1)%len(vertices)]*math.tan(nextturn/2));length=(nextstart-end).length
  assert (nextstart-end).dot(outgoing)>-1e-8,('Overlapping rounded corners',i,length)
  for j in range(max(1,math.ceil(length/.002))):
   points.append(end+(nextstart-end)*j/max(1,math.ceil(length/.002)));normals.append(Vector((outgoing.y,-outgoing.x)))
 # Exact coincident front semicircle junction may occur when both radii touch.
 keep=[i for i in range(len(points))if (points[i]-points[i-1]).length>1e-9]
 return [points[i]for i in keep],[normals[i]for i in keep]

def skin_domain(outline,P):
 vv=list(outline);n=len(vv);edges=[(i,(i+1)%n)for i in range(n)];input_holes=[];holes=P['working_hole_centres_uv_m'];N=P['ring_segments'];hr=P['working_hole_radius_m']+P['working_hole_edge_round_m']
 def inside(p):
  return sum(((a.y>p.y)!=(b.y>p.y))and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x for a,b in zip(outline,outline[1:]+outline[:1]))%2==1
 for centre in holes:
  c=Vector(centre)
  for k,r in enumerate(sorted(set([hr,P['working_cup_flat_radius_m']]+[P['working_cup_flat_radius_m']+(P['working_cup_outer_radius_m']-P['working_cup_flat_radius_m'])*j/20 for j in range(1,21)]+[P['working_cup_outer_radius_m']+.0015,P['working_cup_outer_radius_m']+.003]))):
   ids=[]
   for j in range(N):
    a=math.tau*j/N;point=c+Vector((math.cos(a),math.sin(a)))*r;assert inside(point);ids.append(len(vv));vv.append(point)
   edges.extend((ids[j],ids[(j+1)%N])for j in range(N))
   if k==0:input_holes.append([vv[i]for i in ids])
 step=P['grid_step_m'];u=min(p.x for p in outline)+step;row=0
 while u<max(p.x for p in outline):
  v=min(p.y for p in outline)+step*(.5 if row%2 else 1)
  while v<max(p.y for p in outline):
   p=Vector((u,v))
   if inside(p)and all((p-Vector(c)).length>P['working_cup_outer_radius_m']+.004 for c in holes)and min((p-q).length for q in outline)>step*.4:vv.append(p)
   v+=step
  u+=step;row+=1
 cv,_,cf,*_=delaunay_2d_cdt([p*1000 for p in vv],edges,[list(range(n))],1,1e-6,False);cv=[p*.001 for p in cv]
 def allowed(p):return inside(p)and all((p-Vector(c)).length>hr*.99999 for c in holes)
 raw=len(cf);cf=[tuple(f)for f in cf if allowed(sum((cv[i]for i in f),Vector((0,0)))/3)];used=sorted({i for f in cf for i in f});lookup={i:j for j,i in enumerate(used)};coords=[cv[i]for i in used];faces=[tuple(lookup[i]for i in f)for f in cf];counts=Counter(tuple(sorted((f[j],f[(j+1)%3])))for f in faces for j in range(3));adj=defaultdict(list)
 for (a,b),count in counts.items():
  if count==1:adj[a].append(b);adj[b].append(a)
 assert all(len(q)==2 for q in adj.values());remaining=set(adj);loops=[]
 while remaining:
  start=next(iter(remaining));loop=[start];cur=start;prev=None
  while True:
   nxt=next(q for q in adj[cur]if q!=prev)
   if nxt==start:break
   loop.append(nxt);prev,cur=cur,nxt;assert len(loop)<=len(adj)
  remaining.difference_update(loop);loops.append(loop)
 def area(poly):
  a=np.array([list(p)for p in poly],dtype=np.float64);b=np.roll(a,-1,axis=0);return abs(float(np.sum(a[:,0]*b[:,1]-b[:,0]*a[:,1])))*.5
 outer=max(loops,key=lambda q:area([coords[i]for i in q]));actualholes=[q for q in loops if q is not outer];assert len(actualholes)==2
 def boundary_distance(a,b):
  aa=np.array(b);bb=np.roll(aa,-1,axis=0);d=bb-aa;dd=(d*d).sum(axis=1);assert np.all(dd>0);maximum=0
  for p in a:
   t=np.clip(((np.array(p)-aa)*d).sum(axis=1)/dd,0,1);maximum=max(maximum,float(np.linalg.norm(np.array(p)-(aa+t[:,None]*d),axis=1).min()))
  return maximum
 errors=[]
 for expected in [outline]+input_holes:
  actual=min(loops,key=lambda ids:(sum((coords[i]for i in ids),Vector((0,0)))/len(ids)-sum(expected,Vector((0,0)))/len(expected)).length)
  polygon=[coords[i]for i in actual];errors.append([boundary_distance(expected,polygon),boundary_distance(polygon,expected)])
 assert max(max(q)for q in errors)<2e-7,errors
 expectedarea=area(outline)-sum(area(h)for h in input_holes);actualarea=sum(area([coords[i]for i in f])for f in faces);assert abs(expectedarea-actualarea)<1e-8,('Area mismatch',expectedarea,actualarea,abs(expectedarea-actualarea))
 check=check_planar_domain(coords,faces,outline,actualholes)
 return coords,faces,outer,actualholes,{'domain':check,'boundary_both_directions_m':errors,'expected_area_m2':expectedarea,'retained_area_m2':actualarea,'area_error_m2':abs(expectedarea-actualarea),'discarded_triangles_outside_domain':raw-len(cf)}

def build(P,bodyP,root):
 sys.path.insert(0,str(root/'assets-src/moto-components/exhaust-silencer-body'));from loft_geometry import pchip
 Y=[q['y_m']for q in bodyP['working_sections_world']];functions=[pchip(Y,[q[k]for q in bodyP['working_sections_world']])for k in ['rx_m','rz_m','centre_z_m']];R=P['working_outer_bend_radius_m'];wall=P['working_wall_m'];raw,outs=rounded_outline(P);outline=[q-R*n for q,n in zip(raw,outs)];coords,triangles,outer,holes,report=skin_domain(outline,P);origin=Vector((-.18,P['working_centre_y_m'],functions[2](P['working_centre_y_m'])[0]));vertices=[];normals=[];faces=[];UV=[]
 def surface(uv,depth=0):
  u,v=uv;y=P['working_centre_y_m']+u;(rx,dx),(rz,dz),(cz,dc)=[f(y)for f in functions];a=math.sqrt(1-(v/rz)**2);cup=du=dv=0
  for centre in P['working_hole_centres_uv_m']:
   diff=Vector((u-centre[0],v-centre[1]));r=diff.length;lo=P['working_cup_flat_radius_m'];hi=P['working_cup_outer_radius_m'];d=P['working_cup_depth_m']
   if r<=lo:cup+=d
   elif r<hi:
    t=(r-lo)/(hi-lo);cup+=d*(1-10*t**3+15*t**4-6*t**5);der=d*(-30*t*t+60*t**3-30*t**4)/(hi-lo);du+=der*diff.x/r;dv+=der*diff.y/r
  fu=-dx*a-rx*v*v*dz/(a*rz**3)+du;fv=rx*v/(rz*rz*a)+dv;normal=-Vector((fu,1,dc)).cross(Vector((fv,0,1))).normalized();return Vector((-.18-rx*a-P['working_panel_to_body_airgap_m']+cup+depth,y,cz+v))-origin,normal
 def add(uv,d=0,normal=None):
  point,n=surface(uv,d);i=len(vertices);vertices.append(tuple(point));normals.append(tuple(normal if normal is not None else n));return i
 for p in coords:add(p)
 for p in coords:
  _,n=surface(p);add(p,wall,-n)
 count=len(coords);faces.extend(triangles);faces.extend(tuple(i+count for i in f[::-1])for f in triangles)
 def planar(p,back):return ((.52 if back else .02)+.46*(p.x+.16)/.32,.02+.46*(p.y+.05)/.10)
 UV.extend([[planar(coords[i],False)for i in f]for f in triangles]);UV.extend([[planar(coords[i],True)for i in f[::-1]]for f in triangles])
 def connect(A,B,aa,bb):
  assert len(A)==len(B)
  for i in range(len(A)):
   j=(i+1)%len(A);faces.extend([(A[i],B[i],B[j]),(A[i],B[j],A[j])]);UV.extend([[(.01+.98*i/len(A),aa),(.01+.98*i/len(A),bb),(.01+.98*(i+1)/len(A),bb)],[(.01+.98*i/len(A),aa),(.01+.98*(i+1)/len(A),bb),(.01+.98*(i+1)/len(A),aa)]])
 # Order outer perimeter by exact nearest working outline point. Verify no split/omission.
 assert len(outer)==len(outline),(len(outer),len(outline));ids=sorted(outer,key=lambda i:min(range(len(outline)),key=lambda j:(coords[i]-outline[j]).length));assert max((coords[i]-outline[j]).length for j,i in enumerate(ids))<2e-7
 profile=[(R*math.sin(math.pi*j/48),R*(1-math.cos(math.pi*j/48)))for j in range(1,25)];profile.append((R,R+P['working_edge_return_m']))
 for j in range(1,25):
  a=math.pi*j/24;profile.append((R-wall/2+wall/2*math.cos(a),R+P['working_edge_return_m']+wall/2*math.sin(a)))
 profile.append((R-wall,R))
 for j in range(1,24):
  a=math.pi/2*(1-j/24);profile.append(((R-wall)*math.sin(a),R-(R-wall)*math.cos(a)))
 previous=ids;fullprofile=[(0,0)]+profile+[(0,wall)];lengths=[0.]
 for a,b in zip(fullprofile,fullprofile[1:]):lengths.append(lengths[-1]+math.dist(a,b))
 for k,(distance,depth)in enumerate(profile):
  ring=[add(p+out*distance,depth)for p,out in zip(outline,outs)];connect(previous,ring,.52+.20*lengths[k]/lengths[-1],.52+.20*lengths[k+1]/lengths[-1]);previous=ring
 connect(previous,[i+count for i in ids],.52+.20*lengths[-2]/lengths[-1],.72)
 # True small bores with source-constructed half-round lips across wall depth.
 radius=P['working_hole_radius_m'];rr=P['working_hole_edge_round_m']
 for holeindex,centre in enumerate(P['working_hole_centres_uv_m']):
  c=Vector(centre);loop=min(holes,key=lambda h:(sum((coords[i]for i in h),Vector((0,0)))/len(h)-c).length);loop=sorted(loop,key=lambda i:math.atan2(coords[i].y-c.y,coords[i].x-c.x));angles=[math.atan2(coords[i].y-c.y,coords[i].x-c.x)for i in loop];previous=loop
  hp=[(radius+rr-rr*math.sin(math.pi*j/48),rr*(1-math.cos(math.pi*j/48)))for j in range(1,25)];hp.append((radius,wall-rr))
  hp +=[(radius+rr-rr*math.cos(math.pi*j/48),wall-rr+rr*math.sin(math.pi*j/48))for j in range(1,24)]
  fullhp=[(radius+rr,0)]+hp+[(radius+rr,wall)];hl=[0.]
  for a,b in zip(fullhp,fullhp[1:]):hl.append(hl[-1]+math.dist(a,b))
  vstart=.76+.12*holeindex
  for k,(r,d)in enumerate(hp):
   ring=[add(c+Vector((math.cos(a),math.sin(a)))*r,d)for a in angles];connect(previous,ring,vstart+.08*hl[k]/hl[-1],vstart+.08*hl[k+1]/hl[-1]);previous=ring
  connect(previous,[i+count for i in loop],vstart+.08*hl[-2]/hl[-1],vstart+.08)
 # Separate skin/rolled-edge/bore strips avoid collapsed vertical-side UVs.
 report.update(skin_vertices_per_face=count,method='Constrained skin with two exact hole loops, cubic-section body-conformal working camber, quintic pressed seats, explicitly rolled perimeter and bore lips',all_dimensions_estimated=True,hidden_mounts_fabricated=False)
 return vertices,faces,normals,UV,origin,report
