"""Original round-wire sweep and source centerline clearance checks, no supplied geometry."""
import math,bpy,bmesh
from mathutils import Vector,kdtree
from powertrain_completion_common import mesh_object
def bezier(a,b,c,d,n=36):
 a,b,c,d=map(Vector,[a,b,c,d]);return [a*(1-t)**3+3*b*t*(1-t)**2+3*c*t*t*(1-t)+d*t**3 for t in [i/n for i in range(n+1)]]
def line(a,b,step=.00035):
 a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/step));return [a.lerp(b,i/n)for i in range(n+1)]
def segdistance(p,q,a,b):
 u=q-p;v=b-a;w=p-a;aa=u.dot(u);bb=u.dot(v);cc=v.dot(v);dd=u.dot(w);ee=v.dot(w);cl=lambda x:max(0,min(1,x));out=[(p-(a+cl(ee/cc)*v)).length,(q-(a+cl((ee+bb)/cc)*v)).length,(a-(p+cl(-dd/aa)*u)).length,(b-(p+cl((bb-dd)/aa)*u)).length];D=aa*cc-bb*bb
 if D>1e-12*aa*cc:
  s=(bb*ee-cc*dd)/D;t=(aa*ee-bb*dd)/D
  if 0<=s<=1 and 0<=t<=1:out.append((p+s*u-a-t*v).length)
 return min(out)
def check_path(points,radius):
 arc=[0];lengths=[];curvature=[]
 for a,b in zip(points,points[1:]):lengths.append((b-a).length);arc.append(arc[-1]+lengths[-1])
 for i,(a,b,c) in enumerate(zip(points,points[1:],points[2:])):
  u=b-a;v=c-b;cross=u.cross(v).length
  if cross>1e-13:curvature.append((u.length*v.length*(c-a).length/(2*cross),i+1))
 minimum_curvature,minimum_index=min(curvature);assert minimum_curvature>radius*1.1,('Local wire fold',minimum_curvature,radius,minimum_index,[tuple(v)for v in points[minimum_index-1:minimum_index+2]])
 tree=kdtree.KDTree(len(points));[tree.insert(p,i)for i,p in enumerate(points)];tree.balance();maxstep=max(lengths);minimum=math.inf;pair=None;checked=0
 for i,p in enumerate(points[:-1]):
  for _,j,_ in tree.find_range(p,2*radius+2*maxstep+.0004):
   if j<=i+1 or j>=len(points)-1 or arc[j]-arc[i]<4*radius:continue
   distance=segdistance(points[i],points[i+1],points[j],points[j+1]);checked+=1
   if distance<minimum:minimum=distance;pair=[i,j]
 assert minimum>2*radius+.00002,('Nonlocal wire collision',minimum,pair,radius)
 return dict(centerline_points=len(points),developed_length_m=arc[-1],maximum_segment_m=maxstep,minimum_local_curvature_radius_m=minimum_curvature,wire_radius_m=radius,nonlocal_segment_pairs_checked=checked,minimum_nonlocal_segment_distance_m=minimum if math.isfinite(minimum)else None,minimum_nonlocal_pair=pair,minimum_checked_wire_surface_clearance_m=minimum-2*radius if math.isfinite(minimum)else None,scope='Selected centerline segment-distance and local-curvature checks; not spring force, exact winding or installed clearance')
def round_wire(name,raw,radius,n=32):
 points=[]
 for p in raw:
  p=Vector(p)
  if not points or(p-points[-1]).length>1e-9:points.append(p)
 report=check_path(points,radius);tangents=[(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()for i in range(len(points))];V=[];F=[];normal=None;previous=None
 for p,t in zip(points,tangents):
  if normal is None:
   ref=min([Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))],key=lambda v:abs(v.dot(t)));normal=t.cross(ref).normalized()
  else:normal=previous.rotation_difference(t)@normal;normal=(normal-t*normal.dot(t)).normalized()
  binormal=t.cross(normal).normalized()
  for j in range(n):a=j*math.tau/n;V.append(tuple(p+radius*(normal*math.cos(a)+binormal*math.sin(a))))
  previous=t
 for k in range(len(points)-1):
  for j in range(n):F.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
 F += [tuple(reversed(range(n))),tuple((len(points)-1)*n+j for j in range(n))]
 ob=mesh_object(name,V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(40))
 bm.to_mesh(ob.data);bm.free();ob.data.update();return ob,report
