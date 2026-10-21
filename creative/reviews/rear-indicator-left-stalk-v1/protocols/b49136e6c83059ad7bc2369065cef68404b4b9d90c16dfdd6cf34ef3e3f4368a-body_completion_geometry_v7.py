"""Original authored bodywork surfaces. Dimensions/variants specified per child, never OEM CAD."""
import math
from collections import Counter
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

def rounded_rect(cx,cy,w,h,r,n=16):
 p=[]
 for x,y,start in [(cx+w/2-r,cy+h/2-r,0),(cx-w/2+r,cy+h/2-r,90),(cx-w/2+r,cy-h/2+r,180),(cx+w/2-r,cy-h/2+r,270)]:
  for j in range(n+1):
   a=math.radians(start+90*j/n);p.append((x+r*math.cos(a),y+r*math.sin(a)))
 clean=[]
 for v in p:
  if not clean or math.dist(v,clean[-1])>1e-10:clean.append(v)
 if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-10:clean.pop()
 return clean

def plate(P):
 outer=P['outline'];holes=P.get('holes',[]);loops=[outer]+holes;verts=[];edges=[];faces=[]
 for loop in loops:
  first=len(verts);verts += [Vector(p) for p in loop];ids=list(range(first,len(verts)));edges += list(zip(ids,ids[1:]+ids[:1]));faces.append(ids)
 vv,ee,ff,*_=delaunay_2d_cdt(verts,edges,faces,0,1e-9,False)
 def inside(p,poly):
  x,y=p;hit=False
  for a,b in zip(poly,poly[1:]+poly[:1]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 T=[]
 for f in ff:
  if len(f)!=3:raise ValueError('Expected constrained triangles')
  c=sum((vv[i] for i in f),Vector((0,0)))/3
  if inside(c,outer) and not any(inside(c,h) for h in holes):
   a,b,c=[vv[i]for i in f];T.append(tuple(f) if (b-a).cross(c-a)>0 else tuple(reversed(f)))
 used=sorted({i for f in T for i in f});re={v:i for i,v in enumerate(used)};xy=[vv[i] for i in used];T=[tuple(re[i]for i in f)for f in T];N=len(xy);t=P['thickness_m'];z=P.get('z_m',0)
 V=[(p.x,p.y,z+t/2)for p in xy]+[(p.x,p.y,z-t/2)for p in xy];F=list(T)+[tuple(i+N for i in reversed(f))for f in T]
 counts=Counter(tuple(sorted((a,b)))for f in T for a,b in zip(f,f[1:]+f[:1]));boundary=[]
 for f in T:
  for a,b in zip(f,f[1:]+f[:1]):
   if counts[tuple(sorted((a,b)))]==1:boundary.append((a,b));F.append((a,b+N,a+N)) if False else None
 for a,b in boundary:F.append((a+N,b+N,b,a))
 return V,F,{'expected_boundary_loops':0,'documented_hole_count':len(holes),'construction':'Constrained cap tessellation with actual excluded holes and bridged side walls; no subtraction decal'}

def loft(P):
 # Closed radial face + rounded outer return; profile points authored, relief explicitly estimated.
 pts=[Vector(v)for v in P['outline']];curve=[]
 for i in range(len(pts)):
  a,b,c,d=[pts[k%len(pts)]for k in(i-1,i,i+1,i+2)]
  for j in range(16):
   t=j/16;curve.append(((1-t)**3*a+(3*t**3-6*t*t+4)*b+(-3*t**3+3*t*t+3*t+1)*c+t**3*d)/6)
 if sum(a.x*b.y-b.x*a.y for a,b in zip(curve,curve[1:]+curve[:1]))<0:curve.reverse()
 n=len(curve);rings=48;depth=P['depth_m'];bulge=P.get('bulge_m',.004);rx=max(abs(p.x)for p in curve);ry=max(abs(p.y)for p in curve)
 def face_z(x,y):return depth+bulge*(1-(x/rx)**2-(y/ry)**2)
 V=[(0,0,face_z(0,0))];F=[]
 for k in range(1,rings+1):
  r=.96*k/rings
  for p in curve:V.append((r*p.x,r*p.y,face_z(r*p.x,r*p.y)))
 for j in range(n):F.append((0,1+j,1+(j+1)%n))
 for k in range(rings-1):
  a=1+k*n;b=a+n
  for j in range(n):q=(j+1)%n;F.append((a+j,b+j,b+q,a+q))
 prev=1+(rings-1)*n
 radius=min(P.get('corner_return_radius_m',.0012),depth*.35)
 # Smooth sampled roll: outer face ends at .96 profile, corner reaches full silhouette.
 for k in range(1,17):
  t=(math.pi/2)*k/16;r=.96+.04*math.sin(t);a=len(V)
  for p in curve:V.append((p.x*r,p.y*r,face_z(.96*p.x,.96*p.y)-radius*(1-math.cos(t))))
  for j in range(n):q=(j+1)%n;F.append((prev+j,a+j,a+q,prev+q))
  prev=a
 for k in range(1,17):
  u=k/16;a=len(V)
  for p in curve:V.append((p.x*(1+(P.get('wall_scale_end',.98)-1)*u),p.y*(1+(P.get('wall_scale_end',.98)-1)*u),(face_z(.96*p.x,.96*p.y)-radius)*(1-u)+P.get('front_lip_rise_m',0)*u))
  for j in range(n):q=(j+1)%n;F.append((prev+j,a+j,a+q,prev+q))
  prev=a
 if P.get('front_lip_target_scale') is not None:
  rise=P['front_lip_rise_m'];fraction=P['front_lip_roll_fraction']
  for k in range(1,17):
   angle=math.pi*k/32;rr=.98-fraction*(1-math.cos(angle));zz=rise*(1-math.sin(angle));a=len(V)
   for p in curve:V.append((p.x*rr,p.y*rr,zz))
   for j in range(n):q=(j+1)%n;F.append((prev+j,a+j,a+q,prev+q))
   prev=a
  for k in range(1,5):
   rr=(.98-fraction)+(P['front_lip_target_scale']-(.98-fraction))*k/4;a=len(V)
   for p in curve:V.append((p.x*rr,p.y*rr,0.))
   for j in range(n):q=(j+1)%n;F.append((prev+j,a+j,a+q,prev+q))
   prev=a
 if P.get('closed_back',False):
  center=len(V);V.append((0,0,0))
  for j in range(n):F.append((center,prev+(j+1)%n,prev+j))
 return V,F,dict(expected_boundary_loops=0 if P.get('closed_back')else 1,construction='Original globally quadratic smooth face, periodic B-spline contour, continuous sampled return; no copied documentary pixels')

def ring(P):
 # Revolved closed section aroundZ, angle samples include exact plane faces.
 profile=P['section'];n=P.get('segments',128);V=[];F=[]
 for r,z in profile:
  for j in range(n):a=2*math.pi*j/n;V.append((r*math.cos(a),r*math.sin(a),z))
 for k in range(len(profile)):
  a=k*n;b=((k+1)%len(profile))*n
  for j in range(n):q=(j+1)%n;F.append((a+j,a+q,b+q,b+j))
 return V,F,dict(expected_boundary_loops=0,construction='Original revolved closed exterior section; no thread pitch or internal material measured')


def lathe_open(P):
 # Shape-preserving cubic radial profile along Z; exposed outer envelope only, no hidden bore/caps.
 pairs=P['profile_z_radius_m'];z=[v[0]for v in pairs];rr=[v[1]for v in pairs];h=[z[i+1]-z[i]for i in range(len(z)-1)];assert min(h)>0 and min(rr)>0
 delta=[(rr[i+1]-rr[i])/h[i]for i in range(len(h))];slope=[delta[0]]
 for i in range(1,len(z)-1):
  if delta[i-1]*delta[i]<=0:slope.append(0.)
  else:
   w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1];slope.append((w1+w2)/(w1/delta[i-1]+w2/delta[i]))
 slope.append(delta[-1]);profile=[];steps=P.get('profile_steps',8)
 for i in range(len(h)):
  for j in range(steps):
   t=j/steps;r=(2*t**3-3*t*t+1)*rr[i]+(t**3-2*t*t+t)*h[i]*slope[i]+(-2*t**3+3*t*t)*rr[i+1]+(t**3-t*t)*h[i]*slope[i+1]
   assert min(rr[i],rr[i+1])-1e-10<=r<=max(rr[i],rr[i+1])+1e-10
   profile.append((r,z[i]+t*h[i]))
 profile.append((rr[-1],z[-1]));arc=[0.]
 for a,b in zip(profile,profile[1:]):arc.append(arc[-1]+math.dist(a,b))
 n=P.get('segments',128);V=[];F=[]
 for r,z in profile:
  for j in range(n):a=2*math.pi*j/n;V.append((r*math.cos(a),r*math.sin(a),z))
 for k in range(len(profile)-1):
  a=k*n;b=a+n
  for j in range(n):q=(j+1)%n;F.append((a+j,a+q,b+q,b+j))
 return V,F,dict(expected_boundary_loops=2,construction='Original monotone cubic radius profile, open outer-envelope review cuts; no mechanical bore or hidden wall invented',uv_profile_arc_m=arc,uv_reference_radius_m=P.get('uv_reference_radius_m',sum(rr)/len(rr)),sampled_profile_radius_z_m=profile)
