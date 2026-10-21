"""Original small artwork helpers and exact zero-area FONT repair for v2 only."""
import bpy,hashlib,json,struct
from mathutils import Vector

def area(mesh,ids):
 a,b,c=[mesh.vertices[i].co for i in ids];return (b-a).cross(c-a).length/2

def face_digest(mesh,faces):
 rows=[]
 for face in faces:
  rows.append(b''.join(struct.pack('<fff',*mesh.vertices[i].co)for i in face))
 return hashlib.sha256(b''.join(sorted(rows))).hexdigest()

def repair_zero_font(name,parts,guides):
 """Retain every source vertex and every positive-area triangle, remove only0.
 The editable FONT is kept hidden; the visible evaluated mesh retains UV loops.
 """
 old=bpy.data.objects[name];assert old.type=='FONT',name;deps=bpy.context.evaluated_depsgraph_get();m=bpy.data.meshes.new_from_object(old.evaluated_get(deps),depsgraph=deps);assert all(len(p.vertices)==3 for p in m.polygons);keep=[];remove=[]
 for p in m.polygons:(remove if area(m,p.vertices)==0 else keep).append(p)
 assert len(remove)==2,(name,len(remove));before=face_digest(m,[tuple(p.vertices)for p in keep]);mesh=bpy.data.meshes.new(name+' - exact zero-area faces removed v2');mesh.from_pydata([tuple(v.co)for v in m.vertices],[],[tuple(p.vertices)for p in keep]);mesh.update()
 for material in m.materials:mesh.materials.append(material)
 for layer in m.uv_layers:
  uv=mesh.uv_layers.new(name=layer.name)
  for newface,oldface in zip(mesh.polygons,keep):
   for newloop,oldloop in zip(newface.loop_indices,oldface.loop_indices):uv.data[newloop].uv=layer.data[oldloop].uv
 after=face_digest(mesh,[tuple(p.vertices)for p in mesh.polygons]);assert before==after
 assert all(tuple(a.co)==tuple(b.co)for a,b in zip(m.vertices,mesh.vertices));assert all(area(mesh,p.vertices)>0 for p in mesh.polygons)
 original=name;old.name='EDITABLE original FONT '+name+' v2'
 for c in list(old.users_collection):c.objects.unlink(old)
 guides.objects.link(old);old.hide_render=True;old.hide_set(True)
 new=bpy.data.objects.new(original,mesh);parts.objects.link(new);new.parent=old.parent;new.matrix_parent_inverse=old.matrix_parent_inverse.copy();new.matrix_basis=old.matrix_basis.copy()
 for k,v in old.items():new[k]=v
 new['only_exact_zero_faces_removed']=True;new['editable_font_source']=old.name
 report={'object':name,'editable_font_object':old.name,'source_vertices_retained':len(m.vertices),'source_vertex_coordinate_drift_m':0,'positive_area_triangles_retained':len(keep),'exact_zero_area_faces_removed':[{'index':p.index,'vertex_indices':list(p.vertices),'coordinates_m':[list(m.vertices[i].co)for i in p.vertices]}for p in remove],'retained_positive_triangles_before_sha256':before,'retained_positive_triangles_after_sha256':after,'positive_triangle_geometry_bit_identical':before==after,'dropped_positive_area_m2':0,'UV_layers_retained':[l.name for l in m.uv_layers]};bpy.data.meshes.remove(m);return report

def flat_polygon(name,points,material,parts,parent,z):
 """Planar original ink with supplied contour, no photographed raster."""
 data=bpy.data.meshes.new(name);data.from_pydata([(p[0],p[1],z)for p in points],[],[tuple(range(len(points)))]);data.update();o=bpy.data.objects.new(name,data);parts.objects.link(o);o.parent=parent;data.materials.append(material);o['structural_closed_volume']=False;o['surface_role']='Original planar printed ink, not solid hardware';return o

def filled_curve(name,loops,material,parts,parent,location=(0,0,0)):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='2D';data.resolution_u=12;data.fill_mode='BOTH';data.extrude=0
 for points in loops:
  path=data.splines.new('POLY');path.points.add(len(points)-1);path.use_cyclic_u=True
  for p,co in zip(path.points,points):p.co=(co[0],co[1],0,1)
 o=bpy.data.objects.new(name,data);parts.objects.link(o);o.parent=parent;o.location=location;data.materials.append(material);o['structural_closed_volume']=False;o['surface_role']='Original planar printed ink, not solid hardware';return o

def flat_line(name,points,width,material,parts,parent,z):
 """A planar ribbon: original ink, finite width and round cap discs separately."""
 verts=[];faces=[]
 for a,b in zip(points,points[1:]):
  a,b=Vector(a),Vector(b);d=(b-a).normalized();n=Vector((-d.y,d.x))*width/2;k=len(verts);verts.extend([(a.x+n.x,a.y+n.y,z),(a.x-n.x,a.y-n.y,z),(b.x-n.x,b.y-n.y,z),(b.x+n.x,b.y+n.y,z)]);faces.append((k,k+1,k+2,k+3))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);parts.objects.link(o);o.parent=parent;mesh.materials.append(material);o['structural_closed_volume']=False;return o
