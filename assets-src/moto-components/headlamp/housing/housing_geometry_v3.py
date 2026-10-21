"""Revision2: subdivide profile edges BEFORE forming curved plates. No post-CSG bevel."""
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
 # Radius the finite FLAT outline first, before any cap triangulation or forming.
 ps=[Vector(q)for q in outline]
 # Remove redundant collinear curve samples before the finite flat extrusion.
 # Each accepted local edit moves the contour by <=1 micron in source metres.
 changed=True
 while changed and len(ps)>3:
  changed=False
  for j,b in enumerate(ps):
   a,c=ps[j-1],ps[(j+1)%len(ps)];ac=c-a
   if ac.length and 0<=(b-a).dot(ac)/ac.length_squared<=1 and abs(ac.x*(b.y-a.y)-ac.y*(b.x-a.x))/ac.length<1e-6:
    ps.pop(j);changed=True;break
 nv=len(ps);thick=back(ps[0].x,ps[0].y)-front(ps[0].x,ps[0].y)
 verts=[(p.x,y,p.y)for y in [0,thick]for p in ps]
 faces=[tuple(reversed(range(nv))),tuple(range(nv,nv*2))]+[(j,(j+1)%nv,(j+1)%nv+nv,j+nv)for j in range(nv)]
 o=object_mesh(name,verts,faces,collection)
 for poly in o.data.polygons:poly.use_smooth=True
 # Only explicit C1 ribbon inputs: interpolate the side field along the
 # sampled continuous outline. Designed sharp end corners stay split.
 side_incident={v.index:[]for v in o.data.vertices}
 for p in o.data.polygons:
  if abs(p.normal.y)<.1:
   for vi in p.vertices:side_incident[vi].append(p.normal.copy())
 field=[]
 for p in o.data.polygons:
  for li in p.loop_indices:
   n=p.normal.copy();candidates=side_incident[o.data.loops[li].vertex_index]
   if 'rib' in name and abs(n.y)<.1 and len(candidates)==2 and candidates[0].dot(candidates[1])>math.cos(math.radians(20)):
    n=(candidates[0]+candidates[1]).normalized()
   field.append(n)
 o.data.normals_split_custom_set(field);before_radius(o,r)
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 if r:bpy.ops.object.modifier_apply(modifier=o.modifiers[-1].name)
 mesh=o.data;mesh.calc_loop_triangles();vs=[v.co.copy()for v in mesh.vertices];triangles=[];ns=[];edge_samples={};target=min(step,.0015)
 # Shared edge subdivisions preserve one closed solid; planar caps receive new
 # constrained interior points instead of refining long, nearly collinear fans.
 for edge in mesh.edges:
  a,b=sorted(edge.vertices);count=max(1,math.ceil((vs[a]-vs[b]).length/target));ids=[a]
  for k in range(1,count):ids.append(len(vs));vs.append(vs[a]+(vs[b]-vs[a])*(k/count))
  ids.append(b);edge_samples[(a,b)]=ids
 from mathutils.geometry import barycentric_transform
 from mathutils.bvhtree import BVHTree
 for poly in mesh.polygons:
  normal=poly.normal.copy();axis=max(range(3),key=lambda k:abs(normal[k]));other=[k for k in range(3)if k!=axis];boundary=[];bn=[]
  for j,li in enumerate(poly.loop_indices):
   lj=poly.loop_indices[(j+1)%len(poly.loop_indices)];a=mesh.loops[li].vertex_index;b=mesh.loops[lj].vertex_index;ids=edge_samples[tuple(sorted((a,b)))];ids=ids if a<b else list(reversed(ids));n0=mesh.corner_normals[li].vector;n1=mesh.corner_normals[lj].vector
   for k,idx in enumerate(ids[:-1]):boundary.append(idx);bn.append((n0.lerp(n1,k/(len(ids)-1))).normalized())
  coords=[Vector((vs[i][other[0]],vs[i][other[1]]))for i in boundary];basecoords=[list(c)for c in coords]
  xs=[c.x for c in coords];zs=[c.y for c in coords]
  for i in range(math.ceil((max(xs)-min(xs))/target)+1):
   x=min(xs)+target*.371+i*target
   for j in range(math.ceil((max(zs)-min(zs))/target)+1):
    z=min(zs)+target*.613+j*target
    if inside(x,z,basecoords):
     q=Vector((x,z));distance=1
     for aa,bb in zip(basecoords,basecoords[1:]+basecoords[:1]):
      aa,bb=Vector(aa),Vector(bb);delta=bb-aa;t=max(0,min(1,(q-aa).dot(delta)/delta.length_squared));distance=min(distance,(q-aa-t*delta).length)
     if distance>target*.08:coords.append(q)
  points,_,caps,*_=delaunay_2d_cdt(coords,[],[list(range(len(boundary)))],1,1e-7,False)
  mapping={};fields={};source_tris=[t for t in mesh.loop_triangles if t.polygon_index==poly.index]
  tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[list(t.vertices)for t in source_tris],all_triangles=True)
  for idx,point in enumerate(points):
   close=min(range(len(boundary)),key=lambda k:(point-Vector(basecoords[k])).length_squared)
   if (point-Vector(basecoords[close])).length<2e-8:mapping[idx]=boundary[close];fields[idx]=bn[close];continue
   q=Vector((0,0,0));q[other[0]]=point.x;q[other[1]]=point.y;q[axis]=vs[boundary[0]][axis]-(normal[other[0]]*(q[other[0]]-vs[boundary[0]][other[0]])+normal[other[1]]*(q[other[1]]-vs[boundary[0]][other[1]]))/normal[axis]
   mapping[idx]=len(vs);vs.append(q);loc,_,ti,_=tree.find_nearest(q);tr=source_tris[ti];pa,pb,pc=[mesh.vertices[k].co for k in tr.vertices];na,nb,nc=[mesh.corner_normals[k].vector for k in tr.loops];fields[idx]=barycentric_transform(loc,pa,pb,pc,na,nb,nc).normalized()
  for cap in caps:
   if not inside(sum(points[k].x for k in cap)/len(cap),sum(points[k].y for k in cap)/len(cap),basecoords):continue
   assert len(cap)==3
   inds=[mapping[k]for k in cap];nn=[fields[k]for k in cap];geon=(vs[inds[1]]-vs[inds[0]]).cross(vs[inds[2]]-vs[inds[0]])
   if geon.dot(normal)<0:inds.reverse();nn.reverse()
   assert geon.length>0,(name,'zero flat CDT triangle')
   triangles.append(inds);ns.append(nn)
 flat_min=min((vs[t[1]]-vs[t[0]]).cross(vs[t[2]]-vs[t[0]]).normalized().dot(n)for t,nn in zip(triangles,ns)for n in nn)
 assert flat_min>.5,(name,'flat rounded source failed',flat_min)
 transport=[]
 for t,nn in zip(triangles,ns):
  for i,n in zip(t,nn):
   co=vs[i];e=1e-5;fx=(front(co.x+e,co.z)-front(co.x-e,co.z))/(2*e);fz=(front(co.x,co.z+e)-front(co.x,co.z-e))/(2*e);transport.append(Vector((n.x-n.y*fx,n.y,n.z-n.y*fz)).normalized())
 for v in vs:v.y+=front(v.x,v.z)
 fresh=bpy.data.meshes.new(name+' rounded flat then refined and formed');fresh.from_pydata(vs,[],triangles);fresh.update()
 for poly in fresh.polygons:poly.use_smooth=True
 fresh.normals_split_custom_set(transport);o.data=fresh;return o

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
