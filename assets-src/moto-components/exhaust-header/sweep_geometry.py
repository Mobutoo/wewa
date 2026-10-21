"""C1 authored route, adaptive Bezier bounds and transported hollow-wall sweep."""
import math,bisect
from mathutils import Vector,Quaternion

def cubic(p0,p1,m0,m1,t):
 c=(2*t**3-3*t*t+1)*p0+(t**3-2*t*t+t)*m0+(-2*t**3+3*t*t)*p1+(t**3-t*t)*m1
 d=(6*t*t-6*t)*p0+(3*t*t-4*t+1)*m0+(-6*t*t+6*t)*p1+(3*t*t-2*t)*m1
 dd=(12*t-6)*p0+(6*t-4)*m0+(-12*t+6)*p1+(6*t-2)*m1
 return c,d,dd

def path(P):
 points=[Vector(p)for p in P['centreline_world_controls_m']];tangents=[]
 for i,p in enumerate(points):
  if i==0:m=Vector(P['fixed_tangent_directions_at_knots']['0'])*(points[1]-p).length
  elif i==len(points)-1:m=Vector(P['fixed_tangent_directions_at_knots'][str(i)])*(p-points[i-1]).length
  else:
   a=(p-points[i-1]);b=(points[i+1]-p);direction=Vector(P['fixed_tangent_directions_at_knots'][str(i)])if str(i)in P['fixed_tangent_directions_at_knots']else(a.normalized()+b.normalized()).normalized();m=direction*min(a.length,b.length)*.8
  tangents.append(m.normalized())
 rows=[];bounds=[]
 def distance_to_chord(p,a,b):
  d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared))if d.length_squared else 0;return(p-a-t*d).length
 def subdiv(segment,t0,t1,bezier,depth):
  a,b,c,d=bezier;err=max(distance_to_chord(p,a,d)for p in [b,c]);angle=math.acos(max(-1,min(1,(b-a).normalized().dot((d-c).normalized()))))
  if err>P['curve_max_midpoint_deviation_m']or(d-a).length>P['curve_max_chord_m']or angle>math.radians(P['curve_max_tangent_angle_deg']):
   assert depth<24,'Adaptive cubic did not converge';ab=(a+b)/2;bc=(b+c)/2;cd=(c+d)/2;abc=(ab+bc)/2;bcd=(bc+cd)/2;mid=(abc+bcd)/2;tm=(t0+t1)/2;subdiv(segment,t0,tm,[a,ab,abc,mid],depth+1);subdiv(segment,tm,t1,[mid,bcd,cd,d],depth+1)
  else:
   bounds.append(err);rows.append((segment,t0))
 for i in range(len(points)-1):
  chord=(points[i+1]-points[i]).length;subdiv(i,0,1,[points[i],points[i]+tangents[i]*chord/3,points[i+1]-tangents[i+1]*chord/3,points[i+1]],0)
 rows.append((len(points)-2,1));data=[];length=0;previous=None;frame=None
 for segment,t in rows:
  c,d,dd=cubic(points[segment],points[segment+1],tangents[segment]*(points[segment+1]-points[segment]).length,tangents[segment+1]*(points[segment+1]-points[segment]).length,t);assert d.length>1e-8;T=d.normalized();curvature=(dd-T*dd.dot(T))/d.length_squared
  if previous is None:N=Vector((1,0,0));N=(N-T*N.dot(T)).normalized()
  else:
   length+=(c-previous['point']).length;axis=previous['T'].cross(T)
   N=previous['N'].copy()
   if axis.length>1e-12:N=Quaternion(axis.normalized(),math.atan2(axis.length,previous['T'].dot(T)))@N
   N=(N-T*N.dot(T)).normalized()
  B=T.cross(N).normalized();item={'s':length,'point':c,'T':T,'N':N,'B':B,'curvature':curvature};data.append(item);previous=item
 return data,{'path_samples':len(data),'working_polyline_developed_length_m':length,'maximum_Bezier_control_hull_to_chord_bound_m':max(bounds),'sampled_minimum_curvature_radius_m':1/max(x['curvature'].length for x in data),'curvature_bound_is_sampled':True,'metric_path_measured':False,'C1_parameter':'Cumulative knot chord length; common unit derivative direction at every knot'}

def build(P):
 data,report=path(P);L=data[-1]['s'];rr=P['working_open_mouth_edge_round_m'];outer=P['working_outer_diameter_m']/2;inner=outer-P['working_wall_thickness_m'];assert inner>rr and rr<P['working_wall_thickness_m']/2;assert report['sampled_minimum_curvature_radius_m']>outer*1.5,report
 stations=[r['s']for r in data]
 def at(s):
  k=min(len(data)-2,max(0,bisect.bisect_right(stations,s)-1));a,b=data[k:k+2];t=(s-a['s'])/(b['s']-a['s']);v=lambda key:a[key].lerp(b[key],t);T=v('T').normalized();N=v('N');N=(N-T*N.dot(T)).normalized();return v('point'),T,N,T.cross(N).normalized(),v('curvature')
 profile=[]
 for j in range(13):
  a=math.pi/2*j/12;profile.append((rr*(1-math.cos(a)),outer-rr+rr*math.sin(a),math.sin(a),math.cos(a)))
 profile +=[(r['s'],outer,1,0)for r in data if rr<r['s']<L-rr]
 profile.append((L-rr,outer,1,0))
 for j in range(1,13):
  a=math.pi/2*j/12;profile.append((L-rr+rr*math.sin(a),outer-rr+rr*math.cos(a),math.cos(a),-math.sin(a)))
 profile.append((L,inner+rr,0,-1))
 for j in range(1,13):
  a=math.pi/2*j/12;profile.append((L-rr+rr*math.cos(a),inner+rr-rr*math.sin(a),-math.sin(a),-math.cos(a)))
 profile +=[(r['s'],inner,-1,0)for r in reversed(data)if rr<r['s']<L-rr]
 profile.append((rr,inner,-1,0))
 for j in range(1,13):
  a=math.pi/2*j/12;profile.append((rr-rr*math.sin(a),inner+rr-rr*math.cos(a),-math.cos(a),math.sin(a)))
 N=P['cross_section_vertices'];vertices=[];normals=[];faces=[];faceUV=[];origin=data[0]['point'];vcoords=[0.]
 for i,(s,r,ds,dr)in enumerate(profile):
  if i:vcoords.append(vcoords[-1]+math.hypot(s-profile[i-1][0],r-profile[i-1][1]))
  c,T,A,B,k=at(s)
  for j in range(N):
   a=math.tau*j/N;radial=A*math.cos(a)+B*math.sin(a);vertices.append(tuple(c+radial*r-origin));factor=1-r*k.dot(radial);normal=(radial*(factor*ds)-T*dr).normalized();normals.append(tuple(normal))
 total=vcoords[-1]+abs(profile[-1][1]-profile[0][1]);vcoords=[v/total for v in vcoords]
 for i in range(len(profile)):
  ni=(i+1)%len(profile);v0=vcoords[i];v1=vcoords[ni]if ni else 1.
  for j in range(N):
   nj=(j+1)%N;a=i*N+j;b=i*N+nj;c=ni*N+nj;d=ni*N+j;u0=j/N;u1=(j+1)/N
   faces.extend([(a,b,c),(a,c,d)]);faceUV.extend([[(u0,v0),(u1,v0),(u1,v1)],[(u0,v0),(u1,v1),(u0,v1)]])
 report.update(outer_radius_working_m=outer,inner_radius_working_m=inner,wall_is_estimated_technical_envelope=True,profile_stations=len(profile),parallel_transport_frames=True,analytically_authored_surface_normals=True,two_open_lumens=True)
 return vertices,faces,normals,faceUV,origin,report
