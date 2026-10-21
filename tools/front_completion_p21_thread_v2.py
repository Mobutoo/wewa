"""New revision adds only photographed upper-mouth thread relief; no hidden thread standard."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');old='front-completion-p21-carrier-v1';key='front-completion-p21-carrier-v2';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'assets-src/moto-components'/old/'carrier-gray.blend'));bpy.context.preferences.filepaths.save_version=0;ob=next(o for o in bpy.data.objects if o.type=='MESH');P=json.loads((R/'assets-src/moto-components'/old/'parameters.json').read_text());P.update(mouths='Upper visible-mouth helical relief only; deeper bore remains plain review continuation',thread_pitch_working_m=.0012,thread_pitch_bounds_m=[.0008,.0016],thread_groove_depth_m=.00035,thread_depth_bounds_m=[.0002,.0006],thread_form='rounded estimated groove, not certified thread angle/size/hand; right-hand author hypothesis',thread_turns=3);(H/'parameters.json').write_text(json.dumps(P,indent=2))
for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
 cx=.047*math.cos(angle);cy=.047*math.sin(angle);v=[];f=[];steps=288;sides=12
 for i in range(steps+1):
  a=2*math.pi*3*i/steps+.17;z=.0232+.0036*i/steps
  # Solid swept round tool intersects existing bore wall; rounded open-ended relief bounded to visible depth.
  radial=Vector((math.cos(a),math.sin(a),0));tangent=Vector((-.0035*math.sin(a),.0035*math.cos(a),.0012/(2*math.pi))).normalized();up=tangent.cross(radial).normalized();c=Vector((cx+.0035*math.cos(a),cy+.0035*math.sin(a),z))
  for j in range(sides):p=c+.00035*(math.cos(2*math.pi*j/sides)*radial+math.sin(2*math.pi*j/sides)*up);v.append(tuple(p))
 for i in range(steps):
  for j in range(sides):a=i*sides+j;b=i*sides+(j+1)%sides;f.append((a,b,b+sides,a+sides))
 f.append(tuple(reversed(range(sides))));f.append(tuple(steps*sides+j for j in range(sides)));m=bpy.data.meshes.new('Upper mouth helical relief tool');m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();c=bpy.data.objects.new('TEMP_THREAD_CUT',m);bpy.context.collection.objects.link(c);bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Observed upper mouth relief','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(c,do_unlink=True)
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();m=ob.data;m.update();m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m);report={'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles),'visible_thread_relief_only':True};bm.free();print(report,flush=True);assert report['nonmanifold_edges']==0 and report['minimum_triangle_area_m2']>1e-18
for p in m.polygons:
 p.use_smooth=not any(min(math.hypot(m.vertices[i].co.x-.047*math.cos(a),m.vertices[i].co.y-.047*math.sin(a)) for a in [0,math.pi/2,math.pi,3*math.pi/2])<.0041 for i in p.vertices)
bm=bmesh.new();bm.from_mesh(m)
for e in bm.edges:
 if e.is_manifold and e.calc_face_angle()>math.radians(35):m.edges[e.index].use_edge_sharp=True
bm.free();bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.wm.save_as_mainfile(filepath=str(H/'carrier-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'carrier-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2))
