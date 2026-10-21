"""Related DS151068 observed front envelope; no hidden cush dogs or fitted bearing."""
import bpy,bmesh,math,json
from pathlib import Path
from math import sin,cos,pi,sqrt
R=Path('/workspace/wewa');key='front-completion-p21-carrier-v1';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
P={'package':'P21','photo_url':'https://bajajmatriz.com/wp-content/uploads/2022/07/DS151068..jpg','photo_sha256':'2b0056f79c2b19c0b72d0a76580ac6188936865ffb672d29f0068d62c9cd42bc','all_dimensions_estimated':True,'outer_radius_m':.065,'outer_radius_bounds_m':[.055,.080],'collar_radius_m':.029,'collar_radius_bounds_m':[.024,.036],'height_m':.038,'height_bounds_m':[.028,.050],'mount_circle_radius_m':.047,'mount_circle_bounds_m':[.038,.058],'mouth_radius_m':.0035,'mouth_radius_bounds_m':[.0025,.0045],'observed':'Flared dish, four raised lands, stepped open collar, three directly readable pockets; top pocket occluded','unknown':'Backside and cush dogs excluded; collar depths and plain back continuation estimated, not reconstructed bearing seats; no fit to current rim or six-bolt diagram branch','mouths':'Plain finite exterior bores; photographed internal thread relief remains unfinished'}
(H/'parameters.json').write_text(json.dumps(P,indent=2));D=R/'creative/research/front-completion-p21-v1';D.mkdir(parents=True,exist_ok=True);(D/'G0-G2.json').write_text(json.dumps(P,indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
N=512;v=[];f=[]
def ring(r,z,front=False):
 for j in range(N):
  a=2*pi*(j+.371)/N;zz=z
  if front:
   base=.025*max(0,(.065-r)/.036)**1.4;w=0
   for t in (0,pi/2,pi,3*pi/2):
    s=r*cos(a-t);q=r*sin(a-t);dist=sqrt((s-min(.049,max(.032,s)))**2+q*q)-.0085
    u=max(0,min(1,(.004-dist)/.008));w=max(w,u*u*(3-2*u))
   zz=base+max(0,.027-base)*w
  v.append((r*cos(a),r*sin(a),zz))
# Continuous annular skin, thin plain back continuation openly marked estimated.
for i in range(121):ring(.065-(.065-.029)*i/120,0,True)
for r,z in [(.029,.026),(.029,.028),(.0282,.0288),(.0282,.0300),(.0288,.0308),(.0288,.0365),(.0282,.038),(.0215,.038),(.0208,.0373),(.0208,.018),(.0190,.0165),(.0190,.007),(.0185,.006),(.0185,-.003),(.064,-.003),(.065,-.002)]:ring(r,z)
rows=len(v)//N
for i in range(rows):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;c=((i+1)%rows)*N+(j+1)%N;d=((i+1)%rows)*N+j;f.append((a,b,c,d))
m=bpy.data.meshes.new('Continuous flared dish lands stepped open collar');m.from_pydata(v,[],f);m.update();ob=bpy.data.objects.new('RELATED_FOUR_HOLE_CARRIER_FRONT_ENVELOPE',m);bpy.context.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob;ob.select_set(True)
def orient():
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
orient()
def subtract(cutter,label):
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 bm=bmesh.new();bm.from_mesh(ob.data);print(label,'nonmanifold',sum(not e.is_manifold for e in bm.edges),flush=True);bm.free()
for t in (0,pi/2,pi,3*pi/2):
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.0035,depth=.080,location=(.047*cos(t),.047*sin(t),.018));bpy.context.object.rotation_euler[2]=.0137;subtract(bpy.context.object,'Observed mounting mouth plain relief pending')
# Three readable pockets only: rounded rectangles, radial narrow dimension, tangential width.
for t in (0,pi,3*pi/2):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(.0368*cos(t),.0368*sin(t),.034));c=bpy.context.object;c.dimensions=(.007,.011,.024);c.rotation_euler[2]=t;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);be=c.modifiers.new('Rounded observed pocket corners','BEVEL');be.width=.0015;be.segments=5;bpy.context.view_layer.objects.active=c;bpy.ops.object.modifier_apply(modifier=be.name);subtract(c,'Readable shallow cast pocket')
bpy.context.view_layer.objects.active=ob;orient();bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-10);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-10);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();m=ob.data;m.update()
for p in m.polygons:p.use_smooth=True
bm=bmesh.new();bm.from_mesh(m);bm.edges.ensure_lookup_table()
for e in bm.edges:
 if e.is_manifold and e.calc_face_angle()>math.radians(35):m.edges[e.index].use_edge_sharp=True
m.update();m.calc_loop_triangles();report={'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles),'three_visible_pockets_only':True,'hidden_cush_dogs':False};bm.free();print(report,flush=True);assert report['nonmanifold_edges']==0 and report['volume_m3']>0 and report['minimum_triangle_area_m2']>1e-18
mat=bpy.data.materials.new('Gray form review');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.25,.25,.25,1);bs.inputs['Roughness'].default_value=.3;m.materials.append(mat)
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'carrier-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'carrier-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2));print(report)
