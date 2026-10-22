"""Original visible rounded face/frame surface; open rear observation cut, not OEMCAD."""
import math

def make(P):
 w,h,d,r=P['width_m'],P['height_m'],P['depth_m'],P['corner_radius_m'];n=P['corner_segments'];inset=P['face_inset_m'];V=[(0,0,P['face_z_m'])];F=[];M=[]
 def outline(w,h,r,z):
  a=[]
  for x,y,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
   for j in range(n+1):
    t=math.radians(start+j*90/n);a.append((x+r*math.cos(t),y+r*math.sin(t),z))
  return a
 # Face boundary, shallow original lip, rounded outer shoulder and observed sidewall.
 specs=[(w-2*inset,h-2*inset,r-inset,P['face_z_m']), (w-.0022,h-.0022,r-.0011,.00555),(w-.0012,h-.0012,r-.0006,.0059),(w-.0004,h-.0004,r-.0002,d),(w,h,r,.0057),(w,h,r,.00055),(w-.00025,h-.00025,r-.000125,0)]
 N=4*(n+1);prev=None
 for k,(ww,hh,rr,z) in enumerate(specs):
  start=len(V);V+=outline(ww,hh,rr,z)
  if k==0:
   for j in range(N):F.append((0,start+j,start+(j+1)%N));M.append(0)
  else:
   for j in range(N):F.append((prev+j,start+j,start+(j+1)%N,prev+(j+1)%N));M.append(1)
  prev=start
 return V,F,M
