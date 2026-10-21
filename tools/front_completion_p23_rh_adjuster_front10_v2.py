"""DJ151037 related exterior, formed sheet and separately cut thread exterior; no invented hidden root."""
import bpy,bmesh,math,json
from pathlib import Path
from math import sin,cos,pi,sqrt
R=Path('/workspace/wewa');K='front-completion-p23-rh-adjuster-front10-v2';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(parents=True,exist_ok=False);O.mkdir(parents=True,exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
P=json.loads((R/'creative/research/front-completion-p23-v1/rh-adjuster-G0-G2.json').read_text());P.update({'frame':'X long axis; Z formed top; rod review root2mm outside plate, not mounted','reverse':'Finite sheet continuation estimated; no underside reinforcement','stamp':'Photographed short ticks and long index with terminal dots; working layout/depth photo inferred, not calibration','root':'OPEN proximal rod ring at X=-39mm; gap2mm to sheet avoids guessing hidden root/weld','all_metric_values_estimated':True,'corrected_eye_radius_m':.010,'corrected_eye_outer_width_m':.032});(H/'parameters.json').write_text(json.dumps(P,indent=2))
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
V=[];F=[];NX=321;NY=161
for i in range(NX):
 x=-.037+.074*i/(NX-1);w=.012+.004*math.exp(-(x/.012)**6)
 for j in range(NY):
  t=-1+2*j/(NY-1);y=w*t;r=math.hypot(x,y);z=.004*smooth((.020-r)/.009);fold=smooth((abs(x)-.010)/.007);z-=.005*fold*smooth((abs(y)-.0095)/.0025)
  # Original sampled shallow stamping at observed face, no generic text or calibrated scale.
  ds=[]
  for sign in [-1,1]:
   for xx in [.0145,.025,.030,.0335]:ds.append(math.hypot(x-sign*xx,max(0,abs(y)-.0015)))
   ds.append(math.hypot(x-sign*.020,max(0,abs(y)-.004)))
   for yy in [-.004,.004]:ds.append(math.hypot(x-sign*.020,y-yy)*.65)
  z-=.00022*(1-smooth((min(ds)-.00030)/.00045))
  xx=x
  if abs(x)>.035:xx-=math.copysign(.0008*abs(t)**8*smooth((abs(x)-.035)/.002),x)
  V.append((xx,y,z))
L=len(V);V += [(x,y,z-.0015)for x,y,z in V[:]]
for off,rev in [(0,False),(L,True)]:
 for i in range(NX-1):
  for j in range(NY-1):a=off+i*NY+j;f=(a,a+NY,a+NY+1,a+1);F.append(f[::-1]if rev else f)
loop=list(range(NY))+[i*NY+NY-1 for i in range(1,NX)]+list(range((NX-1)*NY+NY-2,(NX-1)*NY-1,-1))+[i*NY for i in range(NX-2,0,-1)]
for a,b in zip(loop,loop[1:]+loop[:1]):F.append((a,b,b+L,a+L))
m=bpy.data.meshes.new('Continuous raised-eye folded stamped sheet');m.from_pydata(V,[],F);m.update();ob=bpy.data.objects.new('DJ151037_RELATED_FORMED_RH_SHEET',m);bpy.context.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob
bpy.ops.mesh.primitive_cylinder_add(vertices=192,radius=.010,depth=.06);c=bpy.context.object;bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Observed central eye','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(c,do_unlink=True)
# Helical exterior with open root review cut; NOT an assembled rod/plate joint.
n=128;steps=1856;v=[];f=[]
for i in range(steps+1):
 x=-.097+.058*i/steps;env=min(1,max(0,(x+.097)/.0015))
 for j in range(n):
  a=2*pi*j/n;d=abs(((x+.097)/.001-a/(2*pi))%1-.5);q=smooth((d-.10)/.32);r=.003-.00045*q
  if i<48:r-=.00035*(1-env)
  v.append((x,r*cos(a),-.002+r*sin(a)))
for i in range(steps):
 for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
c=len(v);v.append((-.097,0,-.002))
for j in range(n):f.append((c,(j+1)%n,j))
mm=bpy.data.meshes.new('Explicit helical exterior open root');mm.from_pydata(v,[],f);mm.update();rod=bpy.data.objects.new('DJ151037_THREAD_OPEN_REVIEW_ROOT_NOT_JOINED',mm);bpy.context.collection.objects.link(rod)
reports=[]
for obj,expected in [(ob,0),(rod,128)]:
 m=obj.data;bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-9);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-10);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
 for p in m.polygons:p.use_smooth=True
 bm=bmesh.new();bm.from_mesh(m);bm.edges.ensure_lookup_table()
 for e in bm.edges:
  if e.is_manifold and e.calc_face_angle()>math.radians(40):m.edges[e.index].use_edge_sharp=True
 row={'object':obj.name,'triangles':len(m.polygons),'boundary_edges':sum(e.is_boundary for e in bm.edges),'branch_edges':sum(len(e.link_faces)>2 for e in bm.edges),'minimum_triangle_area_m2':min(p.area for p in m.polygons),'volume_closed_only_m3':bm.calc_volume(signed=True)if not expected else None};bm.free();assert row['boundary_edges']==expected and row['branch_edges']==0 and row['minimum_triangle_area_m2']>1e-18
 if not expected:assert row['volume_closed_only_m3']>0
 reports.append(row)
mat=bpy.data.materials.new('Gray form review');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.25,.25,.25,1);p.inputs['Roughness'].default_value=.3
bpy.ops.object.select_all(action='DESELECT')
for obj in [ob,rod]:obj.data.materials.append(mat);obj.select_set(True)
bpy.context.view_layer.objects.active=ob;bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'rh-adjuster-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'rh-adjuster-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps({'objects':reports,'root_review_gap_m':.002,'mounted_fit':False,'all_dimensions_estimated':True},indent=2));print(reports)
