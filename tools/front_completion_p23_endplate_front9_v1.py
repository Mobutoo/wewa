"""New DJ151047 bounded pressing study. Historical protocols unchanged."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from math import sin,cos,pi,sqrt
R=Path('/workspace/wewa');K='front-completion-p23-endplate-front9-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
H.mkdir(parents=True,exist_ok=False);O.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
P=json.loads((R/'creative/research/front-completion-p23-v1/endplate-G0-G2.json').read_text());P.update({'frame':'XY sheet, Z raised photographed face; underside is estimated sheet continuation','reverse_photo_available':False,'finish':'Clean uniform plated-metal hypothesis only; no yellow passivation map, wear or measured alloy claim','construction':'Nested rounded rectangles smoothly interpolated; finite vertical sheet thickness; three actual holes; peripheral return','source_private':'/workspace/wewa-assets/references/front-completion-rear/DJ151047-opposite-0.jpg','source_sha256':hashlib.sha256(Path('/workspace/wewa-assets/references/front-completion-rear/DJ151047-opposite-0.jpg').read_bytes()).hexdigest()});(H/'parameters.json').write_text(json.dumps(P,indent=2))
def rr(a,hx,hy,r):
 # Intersection ray and rounded rectangle, solved using exact signed distance.
 lo=0;hi=math.hypot(hx,hy)
 for _ in range(45):
  m=(lo+hi)/2;q=(abs(m*cos(a))-hx+r,abs(m*sin(a))-hy+r);d=math.hypot(max(q[0],0),max(q[1],0))+min(max(q),0)-r
  if d>0:hi=m
  else:lo=m
 return (lo+hi)/2
N=256
# Hole ring, top crown, formed shoulder, flange and small turned perimeter.
shapes=[('circle',.0042,.0042,0,.007),('rect',.0105,.0068,.003,.007),('rect',.015,.011,.004,.00065),('rect',.0218,.0153,.0025,.00065),('rect',.023,.0165,.0025,0)]
rings=[]
for i in range(len(shapes)-1):
 s,t=shapes[i:i+2]
 for k in range(16):
  u=k/16;v=u*u*(3-2*u);row=[]
  for j in range(N):
   a=2*pi*j/N;r0=s[1] if s[0]=='circle' else rr(a,*s[1:4]);r1=t[1] if t[0]=='circle' else rr(a,*t[1:4]);r=r0+(r1-r0)*u;z=s[4]+(t[4]-s[4])*v;row.append((r*cos(a),r*sin(a),z))
  rings.append(row)
s=shapes[-1];rings.append([(rr(2*pi*j/N,*s[1:4])*cos(2*pi*j/N),rr(2*pi*j/N,*s[1:4])*sin(2*pi*j/N),s[4])for j in range(N)])
V=[p for row in rings for p in row];L=len(V);V += [(x,y,z-.0015)for x,y,z in V[:]];F=[]
for off,reverse in [(0,False),(L,True)]:
 for i in range(len(rings)-1):
  for j in range(N):
   a=off+i*N+j;b=off+i*N+(j+1)%N;f=(a,a+N,b+N,b);F.append(f[::-1]if reverse else f)
for row,rev in [(0,True),(len(rings)-1,False)]:
 for j in range(N):
  a=row*N+j;b=row*N+(j+1)%N;f=(a,b,b+L,a+L);F.append(f[::-1]if rev else f)
m=bpy.data.meshes.new('Continuous formed three-aperture sheet');m.from_pydata(V,[],F);m.update();ob=bpy.data.objects.new('DJ151047_RELATED_PRESSING_ESTIMATED_REVERSE',m);bpy.context.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob
for x in [-.018,.018]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.0018,depth=.05,location=(x,0,0));c=bpy.context.object;bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Observed flange aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(c,do_unlink=True)
m=ob.data;bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-9);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-10);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
for p in m.polygons:p.use_smooth=True
bm=bmesh.new();bm.from_mesh(m);bm.edges.ensure_lookup_table()
for e in bm.edges:
 if e.is_manifold and e.calc_face_angle()>math.radians(40):m.edges[e.index].use_edge_sharp=True
report={'vertices':len(m.vertices),'triangles':len(m.polygons),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True),'minimum_triangle_area_m2':min(p.area for p in m.polygons),'three_real_apertures':True,'all_metric_values_estimated':True,'reverse_sheet_estimated':True};bm.free();assert report['nonmanifold_edges']==0 and report['signed_volume_m3']>0 and report['minimum_triangle_area_m2']>1e-18
mat=bpy.data.materials.new('Gray form review');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.25,.25,.25,1);p.inputs['Roughness'].default_value=.3;m.materials.append(mat);bpy.context.scene.unit_settings.system='METRIC';bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.wm.save_as_mainfile(filepath=str(H/'endplate-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'endplate-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2));print(report)
