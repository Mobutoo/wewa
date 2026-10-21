"""Original underside casting land and observed mouths; explicit estimated depths.
Coordinates are a provisional plane gauge from four unmeasured candidate stud points,
not camera calibration or a reconstruction of heights in noncoplanar photo regions.
"""
import math
from mathutils import Vector

def build(P,geo,profile_solid,cylinder,box,lathe,construction,black):
 p=P['underside_v2'];features=[];drills=[]
 cast=geo.curve(p['casting_outline_xy_working_m'],n=8);land=geo.curve(p['machined_land_xy_working_m'],n=8)
 # Foot wings and land are separate construction volumes joined into one true casting.
 features.append(profile_solid('Asymmetric underside cast foot',cast,[(.004,.0006),(.0047,0),(.0063,0),(.007,.0006)],axis=(0,0,1),u=(1,0,0),v=(0,1,0)))
 features.append(profile_solid('Asymmetric machined gasket land',land,[(0,.0004),(.0005,0),(.0055,0),(.006,.0005)],axis=(0,0,1),u=(1,0,0),v=(0,1,0)))
 # Finite chain-side casting wall joins the bottom foot to lower OHC housing.
 # Rounded cross-section, internal opening handled separately, no generic open fins.
 duct=[]
 for cx,cy,start in[(.035,-.0525,math.pi),(.073,-.0525,math.pi*1.5),(.073,.0525,0),(.035,.0525,math.pi*.5)]:
  for k in range(25):
   angle=start+math.pi*.5*k/24;duct.append((cx+.006*math.cos(angle),cy+.006*math.sin(angle)))
 features.append(profile_solid('Finite rounded chain-side cast duct',duct,[(.002,.0007),(.003,0),(.054,0),(.056,.0007)],axis=(0,0,1),u=(1,0,0),v=(0,1,0)))
 # Raised cross ribs live on recessed cast wings, not drilled passages or copied text.
 from control_geometry import mesh_object
 # Observed irregular branches, not a perfect repeated manufactured grid.
 for branch_index,coords in enumerate(p['lattice_branch_traces_xy_working_m']):
  a,b=map(Vector,coords);tangent=(b-a).normalized();normal=Vector((-tangent.y,tangent.x));vertices=[];polys=[];N=24;rad=p['lattice_branch_radius_working_m']
  for k in range(13):
   point=a+(b-a)*(k/12)
   for side in range(N):
    angle=math.tau*side/N;q=point+normal*(rad*math.cos(angle));vertices.append((q.x,q.y,.004+rad*math.sin(angle)))
  for k in range(12):
   for side in range(N):other=(side+1)%N;polys.append((k*N+side,k*N+other,(k+1)*N+other,(k+1)*N+side))
  polys.extend([tuple(reversed(range(N))),tuple(range(12*N,13*N))]);features.append(mesh_object('Irregular observed cast branch '+str(branch_index),vertices,polys,construction,black))
 for feature in p['relief_features']:
  x,y=feature['centre_xy_working_m'];radius=feature['diameter_working_m']/2
  # Ring ridge is a solid rounded section, centre stays cast material, never a bore.
  verts=[];faces=[];N=128;M=20
  from control_geometry import mesh_object
  for i in range(N):
   a=math.tau*i/N
   for j in range(M):
    b=math.tau*j/M;r=radius+.0010*math.cos(b);verts.append((x+r*math.cos(a),y+r*math.sin(a),.0040+.0010*math.sin(b)))
  for i in range(N):
   for j in range(M):faces.append((i*M+j,((i+1)%N)*M+j,((i+1)%N)*M+(j+1)%M,i*M+(j+1)%M))
  features.append(mesh_object(feature['label']+' rounded ridge',verts,faces,construction,black))
  if 'rosette'in feature['label']:
   for k in range(12):
    a=math.tau*k/12;features.append(cylinder('Small rosette casting spoke '+str(k),(x+radius*.85*math.cos(a),y+radius*.85*math.sin(a),.004),.0008,.004,construction,black,axis=(math.cos(a),math.sin(a),0),n=24))
 # Additional shallow rounded cast ribs on the lower wing, observed outline only.
 for path_index,points in enumerate(p['lower_wing_cast_ribs_xy_working_m']):
  controls=[Vector(v)for v in points];path=[]
  for k in range(len(controls)-1):
   for sample in range(12):path.append(geo.cat(controls[max(0,k-1)],controls[k],controls[k+1],controls[min(len(controls)-1,k+2)],sample/12))
  path.append(controls[-1]);vertices=[];polys=[];rad=p['lower_wing_cast_rib_radius_working_m'];N=24
  for k,point in enumerate(path):
   tangent=(path[min(k+1,len(path)-1)]-path[max(0,k-1)]).normalized();normal=Vector((-tangent.y,tangent.x))
   for side in range(N):
    a=math.tau*side/N;q=point+normal*(rad*math.cos(a));vertices.append((q.x,q.y,.004+rad*math.sin(a)))
  for k in range(len(path)-1):
   for side in range(N):other=(side+1)%N;polys.append((k*N+side,k*N+other,(k+1)*N+other,(k+1)*N+side))
  polys.extend([tuple(reversed(range(N))),tuple(range((len(path)-1)*N,len(path)*N))]);features.append(mesh_object('Observed lower wing rounded rib '+str(path_index),vertices,polys,construction,black))
 for aperture in p['new_apertures']:
  x,y=aperture['centre_xy_working_m'];sx,sy=aperture['size_xy_working_m'];depth=aperture['mouth_depth_working_m'];z=depth/2-.001
  if aperture['kind']=='round':drills.append(cylinder('Visible underside mouth '+aperture['id'],(x,y,z),sx/2,depth+.002,construction,axis=(0,0,1),n=96))
  else:
   controls={'A':[[-.45,-.35],[-.1,-.5],[.4,-.4],[.48,0],[.35,.45],[-.35,.48],[-.5,.2],[-.48,-.2]],'C':[[-.42,-.5],[.28,-.47],[.5,-.27],[.45,.34],[.26,.5],[-.35,.44],[-.5,.2],[-.48,-.18]],'D':[[-.35,-.46],[.16,-.5],[.45,-.3],[.42,.38],[.25,.5],[-.35,.4],[-.5,.1],[-.48,-.2]]}[aperture['id']]
   contour=geo.curve([[a*sx,b*sy]for a,b in controls],n=12);drills.append(profile_solid('Individual visible mouth '+aperture['id'],contour,[(-.002,0),(depth,0)],axis=(0,0,1),u=(1,0,0),v=(0,1,0),centre=(x,y,0)))
 mouth=[Vector(v)for v in p['timing_mouth_outline_xy_working_m']]
 # Smooth unmeasured internal enlargement stops below the intact arch roof.
 vertices=[];faces=[];N=len(mouth);xmin=min(q.x for q in mouth);xmax=max(q.x for q in mouth);levels=[(-.002,0),(.012,0)]
 for k in range(1,25):
  t=k/24;levels.append((.012+.032*t,t*t*(3-2*t)))
 levels.append((.060,1))
 for z,factor in levels:
  outboard=xmax+(.075-xmax)*factor
  for point in mouth:vertices.append((xmin+(point.x-xmin)*(outboard-xmin)/(xmax-xmin),point.y,z))
 for k in range(len(levels)-1):
  for i in range(N):other=(i+1)%N;faces.append((k*N+i,k*N+other,(k+1)*N+other,(k+1)*N+i))
 faces.extend([tuple(reversed(range(N))),tuple(range((len(levels)-1)*N,len(levels)*N))]);drills.append(mesh_object('Continuous long mouth with finite-wall OHC entry',vertices,faces,construction))
 return features,drills
