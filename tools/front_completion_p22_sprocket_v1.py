"""D04 standard44T diagram branch only; original bounded roller-seat plate and arced windows."""
import bpy,bmesh,math,json
from pathlib import Path
from math import sin,cos,pi,sqrt
R=Path('/workspace/wewa');key='front-completion-p22-sprocket-v1';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);P=json.loads((R/'creative/research/front-completion-p22-v1/G0-G2.json').read_text());(H/'parameters.json').write_text(json.dumps(P,indent=2));bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
N=44;pitch=.0127;rp=pitch/(2*sin(pi/N));roller=.00425;half=pi/N;seat_end=.85*math.asin(roller/rp);crest_start=.94*half;crest=rp+.0035

def seat(a):return rp*cos(a)-sqrt(max(0,roller*roller-rp*rp*sin(a)**2))
def radius(a):
 d=abs((a+half)%(2*half)-half)
 if d<seat_end:return seat(d)
 if d>=crest_start:return crest
 t=(d-seat_end)/(crest_start-seat_end);r0=seat(seat_end);h=1e-6;der=(seat(seat_end+h)-seat(seat_end-h))/(2*h);return (2*t**3-3*t*t+1)*r0+(t**3-2*t*t+t)*(crest_start-seat_end)*der+(-2*t**3+3*t*t)*crest

def solid(name,outline,z0,z1):
 n=len(outline);v=[(x,y,z)for z in [z0,z1]for x,y in outline];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n)for j in range(n)];m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();ob=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(ob);return ob
outline=[]
for i in range(N*64):a=2*pi*(i+.173)/(N*64);r=radius(a);outline.append((r*cos(a),r*sin(a)))
ob=solid('RELATED_D04_STANDARD_44T_SPROCKET_EXTERIOR',outline,0,.005)
def cut(c,label):
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(c,do_unlink=True)
# Three annular arc capsule windows: actual curved slots, never generic rectangular cuts.
for rot in [0,2*pi/3,4*pi/3]:
 a0=rot-pi/6;a1=rot+pi/6;ri=.045;ro=.068;mid=(ri+ro)/2;rr=(ro-ri)/2;points=[]
 for i in range(65):a=a0+(a1-a0)*i/64;points.append((ro*cos(a),ro*sin(a)))
 cx=mid*cos(a1);cy=mid*sin(a1)
 for i in range(1,49):a=a1+pi*i/48;points.append((cx+rr*cos(a),cy+rr*sin(a)))
 for i in range(1,65):a=a1-(a1-a0)*i/64;points.append((ri*cos(a),ri*sin(a)))
 cx=mid*cos(a0);cy=mid*sin(a0)
 for i in range(1,48):a=a0+pi+pi*i/48;points.append((cx+rr*cos(a),cy+rr*sin(a)))
 cut(solid('TEMP_ARCED_WINDOW',points,-.010,.020),'Three documented curved windows')
for i in range(6):
 a=2*pi*i/6+.0137;bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=.0035,depth=.040,location=(.0315*cos(a),.0315*sin(a),.0025));cut(bpy.context.object,'Six-hole D04 branch; not four-hole carrier fit')
bpy.ops.mesh.primitive_cylinder_add(vertices=256,radius=.020,depth=.040,location=(0,0,.0025));cut(bpy.context.object,'Open center aperture')
m=ob.data;bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-9);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-10);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
for p in m.polygons:p.use_smooth=abs(p.normal.z)<.01
bm=bmesh.new();bm.from_mesh(m);bm.edges.ensure_lookup_table()
for e in bm.edges:
 if e.is_manifold and e.calc_face_angle()>math.radians(35):m.edges[e.index].use_edge_sharp=True
m.update();m.calc_loop_triangles();report={'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles),'teeth':44,'arced_windows':3,'mounting_holes':6,'pitch_radius_working_m':rp,'current_RDC_identity':False,'mounted_fit':False};bm.free();print(report,flush=True);assert report['nonmanifold_edges']==0 and report['volume_m3']>0 and report['minimum_triangle_area_m2']>1e-18
mat=bpy.data.materials.new('Gray form review only');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.25,.25,.25,1);p.inputs['Roughness'].default_value=.3;m.materials.append(mat);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'sprocket-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'sprocket-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2))
