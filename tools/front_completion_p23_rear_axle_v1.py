"""PF131208 related exterior axle: observed side mouth with OPEN inner review continuation, genuine external helix."""
import bpy,bmesh,math,json
from pathlib import Path
from math import sin,cos,pi
R=Path('/workspace/wewa');key='front-completion-p23-rear-axle-v1';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);P=json.loads((R/'creative/research/front-completion-p23-v1/rear-axle-G0-G2.json').read_text());P['mouth_center_z_fraction']={'working':.5,'bounds':[.4,.6],'status':'estimated placement within observed round head'};(H/'parameters.json').write_text(json.dumps(P,indent=2));bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
rings=[(0,.0110),(.0003,.0116),(.0007,.0118),(.0073,.0118),(.0077,.0115),(.008,.0109),(.008,.0084),(.0083,.0078),(.009,.0075),(.08,.0075),(.17,.0075),(.250,.0075),(.253,.0075),(.254,.0068),(.255,.0065),(.259,.0065)]
for i in range(1,841):rings.append((.259+.021*i/840,None))
n=192;v=[];f=[]
for z,r in rings:
 for j in range(n):
  a=2*pi*(j+.173)/n
  if r is None:
   d=abs(((z-.259)/.0015-a/(2*pi))%1-.5);q=min(1,max(0,(d-.13)/.30));q=q*q*(3-2*q);env=max(0,min(1,(z-.259)/.0015,(.280-z)/.001));rr=.0065-.0007*q*env
   if z>.2795:rr-=.0005*(z-.2795)/.0005
  else:rr=r
  v.append((rr*cos(a),rr*sin(a),z))
for i in range(len(rings)-1):
 for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
for row,z,rev in [(0,0,True),(len(rings)-1,.280,False)]:
 c=len(v);v.append((0,0,z))
 for j in range(n):a=row*n+j;b=row*n+(j+1)%n;f.append((c,b,a)if rev else(c,a,b))
m=bpy.data.meshes.new('Continuous round head shaft steps and external helical end');m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();ob=bpy.data.objects.new('RELATED_PF131208_AXLE_OBSERVED_MOUTH_OPEN_REVIEW_CUT',m);bpy.context.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob
# Positive-X side only. The artificial terminal disk at X=0 is removed; no opposite mouth is invented.
bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=.0025,depth=.040,location=(.020,0,.004),rotation=(0,pi/2,0));c=bpy.context.object;bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Observed side-mouth exterior review opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(c,do_unlink=True);m=ob.data
bm=bmesh.new();bm.from_mesh(m);caps=[face for face in bm.faces if all(abs(v.co.x)<1e-7 for v in face.verts)and abs(face.normal.x)>.99];assert caps,'Missing deliberate review cap';bmesh.ops.delete(bm,geom=caps,context='FACES');bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-9);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-10);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
for p in m.polygons:p.use_smooth=abs(p.normal.z)<.95
bm=bmesh.new();bm.from_mesh(m);bm.edges.ensure_lookup_table()
for e in bm.edges:
 if e.is_manifold and e.calc_face_angle()>math.radians(35):m.edges[e.index].use_edge_sharp=True
m.update();m.calc_loop_triangles();report={'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'boundary_edges':sum(e.is_boundary for e in bm.edges),'expected_boundary_edges':128,'branch_edges':sum(len(e.link_faces)>2 for e in bm.edges),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles),'review_cut':'Single open circular inner side-mouth loop at X=0; no opposite exit or hidden complete cross-bore claimed','thread_form':'Explicit estimated pitch/root/crest and right-hand hypothesis; no certified standard or load claim','all_metric_values_estimated':True};bm.free();print(report,flush=True);assert report['boundary_edges']==128 and report['branch_edges']==0 and report['minimum_triangle_area_m2']>1e-18
mat=bpy.data.materials.new('Gray form review');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.25,.25,.25,1);p.inputs['Roughness'].default_value=.3;m.materials.append(mat);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'rear-axle-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'rear-axle-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2))
