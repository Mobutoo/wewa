"""Small construction helpers for NEW front10 sources; immutable once referenced by a freeze."""
import bpy,bmesh,math
from math import sin,cos,pi

def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)

def mesh_object(name,vertices,faces):
 m=bpy.data.meshes.new(name);m.from_pydata(vertices,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);return o

def orient(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()

def boolean(ob,cutter,operation='DIFFERENCE'):
 orient(ob);orient(cutter);bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Explicit source CSG '+operation,'BOOLEAN');mod.operation=operation;mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)

def helical_x(name,x0,x1,r=.003,pitch=.001,depth=.00045,y0=0,z0=0,open_root=True):
 n=128;steps=math.ceil((x1-x0)/pitch*48);v=[];f=[]
 for i in range(steps+1):
  x=x0+(x1-x0)*i/steps;env=min(1,max(0,(x-x0)/(1.5*pitch)))
  for j in range(n):
   a=2*pi*j/n;d=abs(((x-x0)/pitch-a/(2*pi))%1-.5);rr=r-depth*smooth((d-.10)/.32)-.00035*(1-env);v.append((x,y0+rr*cos(a),z0+rr*sin(a)))
 for i in range(steps):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
 for row,x,rev in [(0,x0,True)]+([]if open_root else[(steps,x1,False)]):
  c=len(v);v.append((x,y0,z0))
  for j in range(n):a=row*n+j;b=row*n+(j+1)%n;f.append((c,b,a)if rev else(c,a,b))
 return mesh_object(name,v,f)

def clean_audit(ob,expected_boundary=0):
 m=ob.data;bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-9);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-10);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
 for p in m.polygons:p.use_smooth=True
 bm=bmesh.new();bm.from_mesh(m);bm.edges.ensure_lookup_table()
 for e in bm.edges:
  if e.is_manifold and e.calc_face_angle()>math.radians(40):m.edges[e.index].use_edge_sharp=True
 row={'object':ob.name,'vertices':len(m.vertices),'triangles':len(m.polygons),'boundary_edges':sum(e.is_boundary for e in bm.edges),'branch_edges':sum(len(e.link_faces)>2 for e in bm.edges),'minimum_triangle_area_m2':min(p.area for p in m.polygons),'signed_volume_closed_only_m3':bm.calc_volume(signed=True)if not expected_boundary else None};bm.free();assert row['boundary_edges']==expected_boundary and row['branch_edges']==0 and row['minimum_triangle_area_m2']>1e-18
 if not expected_boundary:assert row['signed_volume_closed_only_m3']>0
 return row

def gray_save(H,stem,objects):
 mat=bpy.data.materials.new('Gray form review');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.25,.25,.25,1);p.inputs['Roughness'].default_value=.3;bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.data.materials.append(mat);o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.context.scene.unit_settings.system='METRIC';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(H/(stem+'-gray.blend')),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/(stem+'-gray.glb')),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
