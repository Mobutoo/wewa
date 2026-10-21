"""Original section construction helpers for new continuation children, no registry writes."""
import bpy,bmesh,math
from mathutils import Vector
from powertrain_completion_common import mesh_object
def recalc(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
def shell(name,rings,n=160,exponent=2.8):
 # Rings follow a closed wall section: outer back -> rim -> inner floor.
 V=[];F=[]
 for x,cy,cz,ry,rz in rings:
  for i in range(n):
   a=i*math.tau/n;c,s=math.cos(a),math.sin(a);u=math.copysign(abs(c)**(2/exponent),c);v=math.copysign(abs(s)**(2/exponent),s);asym=1+.075*c+.025*math.sin(2*a)
   V.append((x,cy+ry*u*asym,cz+rz*v))
 for k in range(len(rings)-1):
  for i in range(n):F.append((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i))
 F += [tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))]
 ob=mesh_object(name,V,F);recalc(ob);return ob
def cyl(a,b,r,n=128):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=d.length,location=(a+b)/2);ob=bpy.context.object
 for v in ob.data.vertices:
  x,y=v.co.x,v.co.y;v.co.x=x*math.cos(.0137)-y*math.sin(.0137);v.co.y=x*math.sin(.0137)+y*math.cos(.0137)
 ob.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);return ob
def boolean(ob,cut,operation,label):
 recalc(cut);bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new(label,'BOOLEAN');m.operation=operation;m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
 bm=bmesh.new();bm.from_mesh(ob.data);print('BOOLEAN_TOPOLOGY',label,'boundary',sum(e.is_boundary for e in bm.edges),'nonmanifold',sum(not e.is_manifold for e in bm.edges));bm.free()
def clean(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 for f in bm.faces:f.smooth=abs(f.normal.x)<.99
 for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(35))
 bm.to_mesh(ob.data);bm.free();ob.data.update()
