"""Original finite mounting profiles. Radii precede union; no global post-CSG bevel."""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

def object_mesh(name,vertices,faces,collection):
 m=bpy.data.meshes.new(name);m.from_pydata(vertices,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);collection.objects.link(o);return o

def smooth5(t):t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))

def before_radius(o,r):
 if not r:return
 b=o.modifiers.new('Intentional moulded profile radius BEFORE union','BEVEL');b.limit_method='ANGLE';b.angle_limit=.4;b.width=r;b.segments=8;b.harden_normals=True;b.use_clamp_overlap=True

def inside(x,z,ps):
 yes=False
 for a,b in zip(ps,ps[1:]+ps[:1]):
  if(a[1]>z)!=(b[1]>z)and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes

def formed_xz(name,outline,front,back,collection,r=.0007,step=.0035):
 ps=[list(x)for x in outline];area=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(ps,ps[1:]+ps[:1]))/2
 if area<0:ps.reverse()
 coords=[Vector(p)for p in ps];xs=[p[0]for p in ps];zs=[p[1]for p in ps]
 for i in range(math.ceil((max(xs)-min(xs))/step)+1):
  x=min(xs)+.00117+i*step
  for j in range(math.ceil((max(zs)-min(zs))/step)+1):
   z=min(zs)+.00191+j*step
   if inside(x,z,ps):coords.append(Vector((x,z)))
 pts,_,cap,*_=delaunay_2d_cdt(coords,[],[list(range(len(ps)))],1,1e-10,False);cap=[f for f in cap if inside(sum(pts[i].x for i in f)/len(f),sum(pts[i].y for i in f)/len(f),ps)];ids=sorted({i for f in cap for i in f});mp={old:i for i,old in enumerate(ids)};pts=[pts[i]for i in ids];cap=[tuple(mp[i]for i in f)for f in cap];nv=len(pts);v=[(p.x,fun(p.x,p.y),p.y)for fun in [front,back]for p in pts];faces=[tuple(reversed(f))for f in cap]+[tuple(i+nv for i in f)for f in cap];types=['front']*len(cap)+['back']*len(cap)
 from collections import Counter
 es=Counter(tuple(sorted((f[j],f[(j+1)%len(f)])))for f in cap for j in range(len(f)))
 for(a,b),n in es.items():
  if n==1:faces.append((a,b,b+nv,a+nv));types.append('edge')
 o=object_mesh(name,v,faces,collection);norms=[]
 for p,kind in zip(o.data.polygons,types):
  p.use_smooth=True
  for li in p.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co
   if kind=='edge':n=p.normal.copy()
   else:
    fun=front if kind=='front'else back;e=1e-5;dx=(fun(co.x+e,co.z)-fun(co.x-e,co.z))/(2*e);dz=(fun(co.x,co.z+e)-fun(co.x,co.z-e))/(2*e);n=Vector((dx,-1,dz)).normalized()*(1 if kind=='front'else-1)
   norms.append(n)
 o.data.normals_split_custom_set(norms);before_radius(o,r);return o

def prism_yz(name,outline,xcentre,width,collection,r=.0007):
 n=len(outline);v=[(xcentre(z)+sign*width/2,y,z)for sign in [-1,1]for y,z in outline];f=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(j,(j+1)%n,(j+1)%n+n,j+n)for j in range(n)];o=object_mesh(name,v,f,collection)
 for p in o.data.polygons:p.use_smooth=True
 o.data.set_sharp_from_angle(angle=.6);o.data.normals_split_custom_set([p.normal.copy()for p in o.data.polygons for _ in p.loop_indices]);before_radius(o,r);return o

def box(name,centre,dimensions,collection,r=.0006):
 bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o);o.dimensions=dimensions;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for p in o.data.polygons:p.use_smooth=True
 o.data.set_sharp_from_angle(angle=.6);o.data.normals_split_custom_set([p.normal.copy()for p in o.data.polygons for _ in p.loop_indices]);before_radius(o,r);return o

def hole_y(name,x,z,diameter,collection):
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=diameter/2,depth=.12,location=(x,.06,z),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o

def ribbon(points,width):
 # C1 Catmull interpolation of an explicitly estimated reinforcement path.
 ps=[Vector(p)for p in points];samples=[]
 for i in range(len(ps)-1):
  p0=ps[max(0,i-1)];p1=ps[i];p2=ps[i+1];p3=ps[min(len(ps)-1,i+2)]
  for k in range(10):
   t=k/10;samples.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
 samples.append(ps[-1]);left=[];right=[]
 for i,p in enumerate(samples):
  tangent=(samples[min(i+1,len(samples)-1)]-samples[max(0,i-1)]).normalized();normal=Vector((-tangent.y,tangent.x));left.append(list(p+normal*width/2));right.append(list(p-normal*width/2))
 return left+list(reversed(right))

def input_row(o):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);em=ev.to_mesh();em.calc_loop_triangles();normal_matrix=o.matrix_world.to_3x3().inverted().transposed();r={'name':o.name,'vertices':[list(o.matrix_world@v.co)for v in em.vertices],'triangles':[list(t.vertices)for t in em.loop_triangles],'corner_normals':[[list((normal_matrix@em.corner_normals[i].vector).normalized())for i in t.loops]for t in em.loop_triangles]};ev.to_mesh_clear();return r
