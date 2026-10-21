"""Original reusable right-handed u/v/w hollow casting surface builder.
The caller owns documentary silhouette, depths and uncertainty; no inferred dimensions here.
No finishing Bevel is applied to this dense shell. The cup has a genuine open back/rim.
"""
import math
from mathutils import Vector

def closed_loft(outline_uv,face_height,wall=.003,rim_width=.0035,angular=384,radial=144):
 points=[Vector(p) for p in outline_uv];outline=[]
 for j in range(angular):
  t=j/angular*len(points);i=int(t);f=t-i;a,b,c,d=[points[(i+k)%len(points)] for k in [-1,0,1,2]]
  outline.append((2*b+(-a+c)*f+(2*a-5*b+4*c-d)*f*f+(-a+3*b-3*c+d)*f*f*f)*.5)
 verts=[];faces=[]
 def layer(inner):
  start=len(verts);verts.append((0,0,face_height(Vector((0,0)),0)-(wall if inner else 0)))
  for k in range(1,radial+1):
   t=k/radial
   for q in outline:
    factor=1-rim_width/q.length if inner else 1;p=q*t*factor;h=face_height(p,t*factor)-(wall if inner else 0);verts.append((p.x,p.y,h))
  for j in range(angular):
   tri=(start,start+1+j,start+1+(j+1)%angular);faces.append(tri[::-1] if inner else tri)
  for k in range(1,radial):
   a=start+1+(k-1)*angular;b=a+angular
   for j in range(angular):
    quad=(a+j,b+j,b+(j+1)%angular,a+(j+1)%angular);faces.append(quad[::-1] if inner else quad)
  return [start+1+(radial-1)*angular+j for j in range(angular)]
 outer=layer(False);inner=layer(True);ob=[];ib=[]
 for q in outline:
  ob.append(len(verts));verts.append((q.x,q.y,0));p=q*(1-rim_width/q.length);ib.append(len(verts));verts.append((p.x,p.y,0))
 for j in range(angular):
  k=(j+1)%angular;faces.extend([(outer[j],ob[j],ob[k],outer[k]),(ob[j],ib[j],ib[k],ob[k]),(ib[j],inner[j],inner[k],ib[k])])
 return verts,faces,outline
