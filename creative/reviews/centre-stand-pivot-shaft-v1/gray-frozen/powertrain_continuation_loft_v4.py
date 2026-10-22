"""Original periodic C2 finite-wall meridian; no polygon caps or singular section powers."""
import bpy,bmesh,math
from mathutils import Vector
from powertrain_completion_common import mesh_object

def bspline(c,i,t):
 p=[Vector(c[(i+j)%len(c)])for j in range(4)]
 w=[(1-t)**3/6,(3*t**3-6*t*t+4)/6,(-3*t**3+3*t*t+3*t+1)/6,t**3/6]
 dw=[-(1-t)**2/2,(9*t*t-12*t)/6,(-9*t*t+6*t+3)/6,t*t/2]
 ddw=[1-t,3*t-2,1-3*t,t]
 return tuple(sum((v*a for v,a in zip(p,weights)),Vector((0,0,0,0)))for weights in [w,dw,ddw])

def wall(name,controls,cy=0,cz=-.014,n=192,steps=12):
 # Control vectors are X, lateral radius, vertical radius, lateral centre offset.
 # Weighted B-spline is C2, positive radii remain positive by convex combination.
 errors=[]
 for i in range(len(controls)):
  left=bspline(controls,i,1);right=bspline(controls,(i+1)%len(controls),0)
  errors.append([(a-b).length for a,b in zip(left,right)])
 assert max(max(x)for x in errors)<1e-12
 curves=[bspline(controls,i,j/steps)[0]for i in range(len(controls))for j in range(steps)]
 assert min(min(p[1],p[2])for p in curves)>.005
 V=[];F=[]
 for x,ry,rz,off in curves:
  for j in range(n):
   a=math.tau*j/n;c,s=math.cos(a),math.sin(a);q=1-.045*math.cos(4*a)
   V.append((x,cy+off+ry*c*q*(1+.045*c+.015*math.sin(2*a)),cz+rz*s*q))
 for k in range(len(curves)):
  for j in range(n):F.append((k*n+j,k*n+(j+1)%n,((k+1)%len(curves))*n+(j+1)%n,((k+1)%len(curves))*n+j))
 ob=mesh_object(name,V,F);recalc(ob)
 return ob,dict(method='Analytic periodic uniform cubic B-spline meridian, C2 at every knot including wrap; no cap polygons',knot_position_first_second_derivative_errors=errors,section_method='Analytic positive-radius rounded quadrangular Fourier deformation',meridian_samples=len(curves),angular_samples=n,controls=controls,scope='Continuity of pre-boss constructed envelope, not source calibration or hidden gallery topology')

def recalc(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()

def clean_smooth(ob,tol=1e-7):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=tol);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=tol);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 for f in bm.faces:f.smooth=True
 for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(45))
 bm.to_mesh(ob.data);bm.free();ob.data.update()

def soft_cyl(cyl,a,b,r,rounding=.00035):
 ob=cyl(a,b,r);bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new('Finite softened visible seat rim','BEVEL');m.width=rounding;m.segments=4;m.affect='EDGES';bpy.ops.object.modifier_apply(modifier=m.name);recalc(ob);return ob
