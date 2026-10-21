"""Estimated section-varying OHC outer casting; no cap silhouette cutters.
Photos support connected shoulders, not metric taper or exact symmetry.
"""
from mathutils import Vector

def build(P,outline,collection,material,mesh_object):
 stations=P['joint_interface_rework_v3']['housing_outer_stations_x_scaleY_m'];x=[a for a,b in stations];y=[b for a,b in stations];d=[(y[i+1]-y[i])/(x[i+1]-x[i])for i in range(len(x)-1)];m=[d[0]]
 for i in range(1,len(x)-1):
  if d[i-1]*d[i]<=0:m.append(0)
  else:
   h0=x[i]-x[i-1];h1=x[i+1]-x[i];w0=2*h1+h0;w1=h1+2*h0;m.append((w0+w1)/(w0/d[i-1]+w1/d[i]))
 m.append(d[-1]);sections=[]
 for i in range(len(x)-1):
  h=x[i+1]-x[i]
  for j in range(12):
   t=j/12;xx=x[i]+h*t;scale=(2*t**3-3*t*t+1)*y[i]+(t**3-2*t*t+t)*h*m[i]+(-2*t**3+3*t*t)*y[i+1]+(t**3-t*t)*h*m[i+1];sections.append((xx,scale))
 sections.append(stations[-1]);outline=[Vector(v)for v in outline];N=len(outline);vv=[];ff=[]
 def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
 for xx,scale in sections:
  inset=.002*(1-smooth((xx-.008)/.002))+.0008*smooth((xx-.078)/.002)
  ring=[Vector((p.x*scale,p.y))for p in outline]
  for i,p in enumerate(ring):
   tangent=(ring[(i+1)%N]-ring[(i-1)%N]).normalized();q=p+Vector((-tangent.y,tangent.x))*inset;vv.append((xx,q.x,q.y))
 for j in range(len(sections)-1):
  for i in range(N):k=(i+1)%N;ff.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
 ff.extend([tuple(reversed(range(N))),tuple(range((len(sections)-1)*N,len(sections)*N))]);return mesh_object('Estimated section-varying OHC cast housing',vv,ff,collection,material)

def scale_at_x(P,xx):
 stations=P['joint_interface_rework_v3']['housing_outer_stations_x_scaleY_m'];x=[a for a,b in stations];y=[b for a,b in stations];d=[(y[i+1]-y[i])/(x[i+1]-x[i])for i in range(len(x)-1)];m=[d[0]]
 for i in range(1,len(x)-1):
  if d[i-1]*d[i]<=0:m.append(0)
  else:
   h0=x[i]-x[i-1];h1=x[i+1]-x[i];a=2*h1+h0;b=h1+2*h0;m.append((a+b)/(a/d[i-1]+b/d[i]))
 m.append(d[-1]);i=next((i for i in range(len(x)-1)if xx<=x[i+1]),len(x)-2);h=x[i+1]-x[i];t=max(0,min(1,(xx-x[i])/h));return (2*t**3-3*t*t+1)*y[i]+(t**3-2*t*t+t)*h*m[i]+(-2*t**3+3*t*t)*y[i+1]+(t**3-t*t)*h*m[i+1]

def add_visible_ribs(P,outline,collection,material,mesh_object):
 """Integral cast flanks only: section-derived rounded ridges, no cylinder glue."""
 contour=[Vector(v)for v in outline];result=[]
 def surface_y(x,z,sign):
  hits=[]
  for a,b in zip(contour,contour[1:]+contour[:1]):
   if (a.y<=z<=b.y or b.y<=z<=a.y)and abs(b.y-a.y)>1e-12:hits.append(a.x+(b.x-a.x)*(z-a.y)/(b.y-a.y))
  assert hits,z
  return (max(hits)if sign>0 else min(hits))*scale_at_x(P,x)
 for index,item in enumerate(P['joint_interface_rework_v3']['visible_flank_ribs_working']):
  sign=item['side_Y'];z0=item['centre_z_m'];start,end=item['extent_x_m'];half=item['width_z_m']/2;height=item['height_outward_m'];width=.003;vv=[];ff=[];rings=[]
  offsets=[-half+2*half*i/20 for i in range(21)];profile=[(z,True)for z in offsets]+[(z,False)for z in reversed(offsets)]
  for k in range(41):
   x=start+(end-start)*k/40;t=max(0,min(1,(x-start)/width))*max(0,min(1,(end-x)/width));t=t*t*(3-2*t);ring=[]
   for dz,top in profile:
    base=surface_y(x,z0+dz,sign);out=height*(1-(dz/half)**2)**2*t if top else-.001;ring.append(len(vv));vv.append((x,base+sign*out,z0+dz))
   rings.append(ring)
  N=len(profile)
  for k in range(len(rings)-1):
   for j in range(N):n=(j+1)%N;ff.append((rings[k][j],rings[k][n],rings[k+1][n],rings[k+1][j]))
  ff.extend([tuple(reversed(rings[0])),tuple(rings[-1])]);result.append(mesh_object('Estimated integral flank ridge '+str(index+1),vv,ff,collection,material))
 return result
