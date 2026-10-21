"""Original finite cosmetic helix, preserving the old estimated radial profile.
No OEM dimensions/fit are inferred. Crease helices are actual cell boundaries.
"""
import math

def profile(phase):
 p=phase%1
 return 1 if p<.15 or p>=.95 else 1-(p-.15)/.30 if p<.45 else 0 if p<.65 else (p-.65)/.30

def make_stud(mount,pitch=.00125,z0=-.004,z1=.024,sectors=144):
 length=(z1-z0)/pitch;verts=[];faces=[];keys={};boundary={0:set(),1:set()}
 def clip(poly,bottom):
  out=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   da=a[0]+a[1]-(0 if bottom else length);db=b[0]+b[1]-(0 if bottom else length)
   ia=da>=-1e-12 if bottom else da<=1e-12;ib=db>=-1e-12 if bottom else db<=1e-12
   if ia:out.append(a)
   if ia!=ib:
    t=da/(da-db);out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
  clean=[]
  for p in out:
   if not clean or abs(p[0]-clean[-1][0])+abs(p[1]-clean[-1][1])>1e-12:clean.append(p)
  if len(clean)>1 and abs(clean[0][0]-clean[-1][0])+abs(clean[0][1]-clean[-1][1])<1e-12:clean.pop()
  return clean
 def index(u,v):
  q=u+v
  if abs(q)<1e-11:q=0.
  if abs(q-length)<1e-11:q=length
  canonical_u=0. if abs(u-1)<1e-12 else u
  key=(round(canonical_u,12),round(q,12))
  if key not in keys:
   angle=canonical_u*math.tau;r=.00335+.00065*profile(v);keys[key]=len(verts);verts.append((mount[0]+r*math.cos(angle),mount[1]+r*math.sin(angle),mount[2]+z0+pitch*q))
  i=keys[key]
  if q==0:boundary[0].add(i)
  if q==length:boundary[1].add(i)
  return i
 levels=sorted(k+p for k in range(-2,math.ceil(length)+2)for p in [0,.15,.45,.65,.95])
 for j in range(sectors):
  lo=j/sectors;hi=(j+1)/sectors
  for va,vb in zip(levels,levels[1:]):
   if vb+hi<0 or va+lo>length:continue
   poly=clip(clip([(lo,va),(hi,va),(hi,vb),(lo,vb)],True),False)
   if len(poly)<3:continue
   ids=[index(*p)for p in poly]
   if len(set(ids))>=3:faces.append(tuple(ids))
 for end in [0,1]:
  ids=sorted(boundary[end],key=lambda i:math.atan2(verts[i][1]-mount[1],verts[i][0]-mount[0])%math.tau);centre=len(verts);verts.append((mount[0],mount[1],mount[2]+(z0 if not end else z1)))
  for i,a in enumerate(ids):
   b=ids[(i+1)%len(ids)];faces.append((centre,b,a)if not end else(centre,a,b))
 return verts,faces,{'sectors':sectors,'helical_phase_boundaries':[0,.15,.45,.65,.95],'axial_range_q_m':[z0,z1],'pitch_estimated_m':pitch,'major_diameter_estimated_m':.008,'root_diameter_estimated_m':.0067,'cap_boundary_vertices':[len(boundary[0]),len(boundary[1])],'profile':'Exact old piecewise radial equation, mesh crease curves aligned in parameter domain; angular facets reduced, no added bevel or crease radius.'}
