"""Analytic cone/rounded-hex loops instead of a stair boundary on axial rings."""
import math
def body_geometry(contour,p):
 contour=sorted(contour,key=lambda q:math.atan2(q[1],q[0]));angles=[math.atan2(q[1],q[0])for q in contour];radii=[math.hypot(*q)for q in contour];N=len(contour);verts=[];rings=[];roles=[]
 def loop(points,role):
  ids=list(range(len(verts),len(verts)+N));verts.extend(points);rings.append(ids);roles.append(role);return ids
 def circle(x,r,role):return loop([(x,r*math.cos(a),r*math.sin(a))for a in angles],role)
 prefix=[(-.0125,.00485),(-.01235,.005),(.0009,.005),(.00105,.005),(.00125,.0078),(.00145,.008),(.0047,.008),(.0049,.00775),(.0051,.0076),(.0054,.0076),(.0056,.00785),(.0063,.00785),(.0066,.0078),(.0070,.0078)]
 for x,r in prefix:circle(x,r,'body profile')
 lower=[p['lower_cone_start_x_m']+(r-p['lower_cone_start_radius_m'])*p['lower_cone_dx_dr']for r in radii];upper=[p['upper_cone_end_x_m']+(r-p['upper_cone_end_radius_m'])*p['upper_cone_dx_dr']for r in radii];K=p['conical_strip_intervals'];boundary={}
 for i in range(1,K+1):
  t=i/K;points=[]
  for a,r,x in zip(angles,radii,lower):
   radius=(1-t)*p['lower_cone_start_radius_m']+t*r;points.append(((1-t)*p['lower_cone_start_x_m']+t*x,radius*math.cos(a),radius*math.sin(a)))
  ids=loop(points,'lower cone')
 boundary['lower intersection']=ids
 boundary['upper intersection']=loop([(x,u,v)for x,(u,v)in zip(upper,contour)],'hex side')
 for i in range(1,K+1):
  t=i/K;points=[]
  for a,r,x in zip(angles,radii,upper):
   radius=(1-t)*r+t*p['upper_cone_end_radius_m'];points.append(((1-t)*x+t*p['upper_cone_end_x_m'],radius*math.cos(a),radius*math.sin(a)))
  ids=loop(points,'upper cone')
 boundary['upper annulus']=ids
 suffix=[(.0138,.0062),(.0140,.0061),(.0144,.00585),(.0144,.00505),(.0017,.00505),(.0014,.003),(-.0125,.003)]
 for x,r in suffix:circle(x,r,'body profile')
 faces=[];flat_faces=[];sharp=[]
 for k in range(len(rings)):
  q=(k+1)%len(rings)
  for j in range(N):
   m=(j+1)%N;face=(rings[k][j],rings[k][m],rings[q][m],rings[q][j]);faces.append(face)
   if roles[q]=='hex side':
    pts=[contour[j],contour[m]]
    if any(all(abs(u*math.cos(h*math.pi/3)+v*math.sin(h*math.pi/3)-.008)<1e-8 for u,v in pts)for h in range(6)):flat_faces.append(len(faces)-1)
 for ids in boundary.values():sharp.extend((ids[j],ids[(j+1)%N])for j in range(N))
 assert min(r-p['upper_cone_end_radius_m']for r in radii)>1e-8
 return verts,faces,flat_faces,sharp,{'contour_points':N,'contour_yz_m':contour,'boundary_vertex_indices':boundary,'lower_boundary_x_range_m':[min(lower),max(lower)],'upper_boundary_x_range_m':[min(upper),max(upper)],'minimum_positive_conical_strip_radial_width_m':min(r-p['upper_cone_end_radius_m']for r in radii),'method':'Exact analytic X per existing rounded-hex contour point, native automatic normals at explicit geometric boundaries, no stair on axial grid.'}
