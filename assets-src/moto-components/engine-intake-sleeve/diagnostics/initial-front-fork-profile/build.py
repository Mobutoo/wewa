"""Original isolated PF581402-related sleeve; single physical annular candidate, no installed side certified."""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib,numpy as np
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-sleeve-v1';P=json.loads((H/'parameters.json').read_text());assert not(H/'preflight-manifest.json').exists();sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,mesh_object,cylinder,csg,check_mesh,export,studio
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;parts=bpy.data.collections.new('WEWA_ENGINE_INTAKE_SLEEVE');con=bpy.data.collections.new('INTAKE_SLEEVE_CONSTRUCTION_NOT_EXPORTED');stage=bpy.data.collections.new('INTAKE_SLEEVE_STUDIO_NOT_EXPORTED')
for c in [parts,con,stage]:s.collection.children.link(c)
M=P['material_baseline'];mat=material('Representative black moulded sleeve - chemistry unknown',M['linear_basecolor'],M['metallic'],M['roughness'])
def rounded(q,cut=.22,n=12):
 out=[]
 for i,point in enumerate(q):
  a=Vector(q[i-1]);b=Vector(point);c=Vector(q[(i+1)%len(q)]);v=b+cut*(a-b);w=b+cut*(c-b)
  for j in range(n):
   t=j/n;out.append(tuple((1-t)**2*v+2*t*(1-t)*b+t*t*w))
 return out
def annular_mesh(name,profile,angles=192,start=0,span=math.tau):
 # Closed cross-section, finite positive radius throughout. Open sector has true end caps.
 full=abs(span-math.tau)<1e-10;A=angles if full else angles+1;N=len(profile);vs=[];fs=[]
 for i in range(A):
  a=start+span*i/angles
  for r,z in profile:vs.append((r*math.cos(a),r*math.sin(a),z))
 for i in range(angles):
  k=(i+1)%A
  for j in range(N):fs.append((i*N+j,k*N+j,k*N+(j+1)%N,i*N+(j+1)%N))
 if not full:fs.extend([tuple(range(N-1,-1,-1)),tuple((A-1)*N+j for j in range(N))])
 return mesh_object(name,vs,fs,con)
# Profile coordinates(r,z) all working estimates, rear shoulder conditional Garage face.
outer=[(.0229,-.0175),(.0235,-.0171),(.0235,-.0164),(.0228,-.0157),(.0228,-.0036),(.0231,-.0028),(.0238,-.0022),(.0238,-.0014),(.0229,-.0008),(.0229,-.0002),(.0238,.0005),(.0238,.0013),(.0231,.0021),(.0228,.0027),(.0228,.0155),(.0235,.0161),(.0235,.0172),(.0232,.0175)]
profile=rounded([(.0114,-.0175),*outer,(.018,.0175),(.0176,.0172),(.0173,.0163),(.0169,.0154),(.0169,.0145),(.0176,.0132),(.0178,.0112),(.0178,.0088),(.0165,.0078),(.0165,.0067),(.0176,.0056),(.0176,-.010),(.0170,-.012),(.0120,-.014),(.0114,-.015)],cut=.20,n=12)
body=annular_mesh('Editable continuous sleeve outer bands inner lips and conditional rear shoulder',profile)
# The front fork has two original rounded tongues, real roots overlap collar wall.
def tongue(name,angle,width,z0,z1):
 sign=1 if z1>z0 else -1;top=z1;root=z0
 profile=rounded([(.0218,root),(.0250,root),(.0250,top-sign*.0008),(.0244,top),(.0226,top),(.0218,top-sign*.0008)],cut=.20,n=10)
 return annular_mesh(name,profile,angles=32,start=math.radians(angle-width/2),span=math.radians(width))
features=[tongue('Editable Matriz front fork tongue '+str(i),a,P['fork_width_degrees'],P['fork_root_Z_m'],P['fork_top_Z_m'])for i,a in enumerate(P['fork_working_angles_degrees'])]
features.append(tongue('Editable opposite axial appendage - count unknown',P['rear_appendage_angle_degrees'],P['rear_appendage_width_degrees'],-.010,P['rear_appendage_top_Z_m']))
# Original bounded parting-line ridge follows exterior lands and beads; no photo-derived height.
N=180;B=14;vs=[];fs=[];zmin,zmax=-.0164,.0164;zs=np.array([z for r,z in outer]);rs=np.array([r for r,z in outer])
for i in range(N):
 t=i/(N-1);z=zmin+(zmax-zmin)*t;a=math.radians(P['seam_working_angle_degrees']+.35*math.sin(2*math.pi*t));r=float(np.interp(z,zs,rs))-.00007;centre=Vector((r*math.cos(a),r*math.sin(a),z));u=Vector((math.cos(a),math.sin(a),0));v=Vector((-math.sin(a),math.cos(a),0));radius=P['seam_relief_m']*(.65+.35*math.sin(math.pi*t)**.3)
 for j in range(B):
  b=math.tau*j/B;vs.append(tuple(centre+radius*(u*math.cos(b)+v*math.sin(b))))
for i in range(N-1):
 for j in range(B):fs.append((i*B+j,(i+1)*B+j,(i+1)*B+(j+1)%B,i*B+(j+1)%B))
fs.extend([tuple(range(B-1,-1,-1)),tuple((N-1)*B+j for j in range(B))]);features.append(mesh_object('Editable original bounded longitudinal mould seam',vs,fs,con))
# Five closed shallow face marks, not through holes; depth/sign/function not certified.
drills=[]
for i,degrees in enumerate(P['closed_front_mark_angles_degrees']):
 a=math.radians(degrees);r=.0208;drills.append(cylinder('Editable closed shallow front mould mark '+str(i),(r*math.cos(a),r*math.sin(a),.0175),P['closed_front_mark_radius_m'],P['closed_front_mark_working_depth_m']*2,con,axis=(0,0,1),n=64))
bpy.context.view_layer.update();result,data=csg(body,features,drills,parts,mat,R,'PF581402 sleeve - isolated conditional')
bm=bmesh.new();bm.from_mesh(result.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for e in bm.edges:e.smooth=len(e.link_faces)==2 and e.calc_face_angle(0)<.55
bm.to_mesh(result.data);bm.free();result.data.update()
for p in result.data.polygons:p.use_smooth=True
result.data.calc_loop_triangles();zero=sum(t.area<=0 for t in result.data.loop_triangles);assert zero==0
uv=result.data.uv_layers.new(name='Original physical100mm planar sectors')
for f in result.data.polygons:
 dominant=max(range(3),key=lambda k:abs(f.normal[k]));a,b=[k for k in range(3)if k!=dominant]
 for li in f.loop_indices:
  p=result.data.vertices[result.data.loops[li].vertex_index].co;uv.data[li].uv=(float(p[a])/.1+.5,float(p[b])/.1+.5)
checks=[check_mesh(result)];root=bpy.data.objects.new('Intake sleeve isolated - end correspondence unknown',None);parts.objects.link(root);result.parent=root;con.hide_render=True;con.hide_viewport=True;studio(s,stage,Vector((0,0,0)));s.camera.data.clip_start=.0001
for q in stage.objects:
 if q.type=='MESH':q.hide_render=True
 if q.type=='LIGHT':q.data.energy*=.08
source=H/'engine-intake-sleeve-v1-geometry.blend';glb=H/'engine-intake-sleeve-v1-geometry.glb';export(glb,[root,result]);bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':sha(glb),'geometry':checks,'triangles':len(result.data.loop_triangles),'zero_area_triangles':zero,'collection':parts.name,'root':root.name,'all_dimensions_estimated':True,'automatic_attachment_allowed':False,'same_Matriz_Garage_mould_confirmed':False,'rear_appendage_full_count_unresolved':True,'rear_mould_lettering_fabricated':False,'no_post_csg_bevel_or_remesh':True,'CSG_report':{k:v for k,v in data.items()if k not in ['vertices','triangles']},'art_accepted':False};(H/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'geometry-source-check.json').write_text(json.dumps(report,indent=2)+'\n');print('INTAKE_SLEEVE_GEOMETRY',json.dumps(report),flush=True)
