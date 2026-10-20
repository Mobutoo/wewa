"""Original reusable construction helpers for isolated cable-operated controls.
Shared read-only by the two later control builders; no existing assets modified.
"""
import json,math,subprocess,shutil,tempfile
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
def material(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
def mesh_object(name,verts,faces,collection,mat=None):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free()
 for p in m.polygons:p.use_smooth=True
 if mat:m.materials.append(mat)
 o=bpy.data.objects.new(name,m);collection.objects.link(o);return o
def lathe(name,section,collection,mat=None,n=128):
 verts=[];faces=[];count=len(section)
 for i in range(n):
  a=math.tau*i/n
  for x,r in section:verts.append((x,r*math.cos(a),r*math.sin(a)))
 for i in range(n):
  for j in range(count):faces.append((i*count+j,((i+1)%n)*count+j,((i+1)%n)*count+(j+1)%count,i*count+(j+1)%count))
 return mesh_object(name,verts,faces,collection,mat)
def cylinder(name,centre,radius,depth,collection,mat=None,axis=(1,0,0),n=64):
 bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=radius,depth=depth,location=centre);o=bpy.context.object;o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o);o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
 if mat:o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o
def box(name,centre,dimensions,collection,mat=None,bevel=.0005):
 bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o);o.dimensions=dimensions;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if mat:o.data.materials.append(mat)
 if bevel:
  mod=o.modifiers.new('Estimated edge radius','BEVEL');mod.width=bevel;mod.segments=3
 return o
def evaluate(o):
 deps=bpy.context.evaluated_depsgraph_get();return bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps)
def csg(base,features,drills,collection,mat,root,name):
 def row(o):
  deps=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();r={'name':o.name,'vertices':[list(o.matrix_world@v.co) for v in m.vertices],'triangles':[list(t.vertices) for t in m.loop_triangles]};ev.to_mesh_clear();return r
 with tempfile.TemporaryDirectory(prefix='wewa-control-csg-') as tmp:
  inp=Path(tmp)/'in.json';out=Path(tmp)/'out.json';inp.write_text(json.dumps({'base':row(base),'features':[row(o) for o in features],'drills':[row(o) for o in drills]}));subprocess.run([shutil.which('python'),str(root/'assets-src/moto-components/front-brake-plate/csg.py'),str(inp),str(out)],check=True);data=json.loads(out.read_text())
 result=mesh_object(name,data['vertices'],data['triangles'],collection,mat)
 for o in [base]+features+drills:o.hide_render=True;o.hide_set(True)
 return result,data
def check_mesh(o):
 m=evaluate(o);bm=bmesh.new();bm.from_mesh(m);unseen=set(bm.verts);shells=0
 while unseen:
  shells+=1;queue=[unseen.pop()]
  while queue:
   for e in queue.pop().link_edges:
    for v in e.verts:
     if v in unseen:unseen.remove(v);queue.append(v)
 row={'name':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'connected_shells':shells,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True)};bm.free();bpy.data.meshes.remove(m)
 assert shells==1 and not row['non_manifold_edges'] and row['signed_volume_m3']>0,row
 return row
def tree_world(o):
 m=evaluate(o);verts=[o.matrix_world@v.co for v in m.vertices];faces=[tuple(p.vertices) for p in m.polygons];tree=BVHTree.FromPolygons(verts,faces);bpy.data.meshes.remove(m);return tree
def export(filepath,objects,animations=False):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=next(o for o in objects if o.type=='MESH')
 bpy.ops.export_scene.gltf(filepath=str(filepath),export_format='GLB',use_selection=True,export_apply=True,export_animations=animations,export_tangents=False)
def frame_matrix(endpoint,inward):
 a=Vector(inward).normalized();u=Vector((0,0,1));v=a.cross(u).normalized();return Matrix(((a.x,u.x,v.x,endpoint[0]),(a.y,u.y,v.y,endpoint[1]),(a.z,u.z,v.z,endpoint[2]),(0,0,0,1)))
def studio(scene,collection,target,scale=.3):
 world=bpy.data.worlds.new('Control neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.29,.34,1);world.node_tree.nodes['Background'].inputs[1].default_value=.25;scene.world=world
 floor_mat=material('Control studio slate',(.10,.12,.14),0,.8)
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.073));floor=bpy.context.object
 for c in list(floor.users_collection):c.objects.unlink(floor)
 collection.objects.link(floor);floor.data.materials.append(floor_mat)
 for name,offset,power,size in [('CONTROL_KEY',(.1,-.2,.35),22,.35),('CONTROL_FILL',(-.2,.15,.20),12,.30),('CONTROL_EDGE',(.2,.1,.18),15,.25)]:
  data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);collection.objects.link(o);o.location=Vector(target)+Vector(offset);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 cam=bpy.data.objects.new('CONTROL_CAMERA',bpy.data.cameras.new('CONTROL_CAMERA'));collection.objects.link(cam);scene.camera=cam;cam.location=Vector(target)+Vector((.18,.25,.18));cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=65
 scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE';scene.render.resolution_x=1100;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
