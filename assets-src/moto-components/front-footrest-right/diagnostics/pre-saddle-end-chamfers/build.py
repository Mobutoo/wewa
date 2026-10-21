"""Original PF113001-related RH support, independently observed, isolated and unmeasured."""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/front-footrest-right-v1';P=json.loads((H/'parameters.json').read_text());assert not(H/'preflight-manifest.json').exists()
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,mesh_object,cylinder,csg,check_mesh,export,studio
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
parts=bpy.data.collections.new('WEWA_FRONT_FOOTREST_RIGHT');con=bpy.data.collections.new('FOOTREST_RH_CONSTRUCTION_NOT_EXPORTED');stage=bpy.data.collections.new('FOOTREST_RH_STUDIO_NOT_EXPORTED')
for c in [parts,con,stage]:s.collection.children.link(c)
M=P['material_baseline'];mat=material('Representative black coated metal - chemistry unmeasured',M['linear_basecolor'],M['metallic'],M['roughness'])
def roundpoly(q,cut=.18,n=12):
 out=[]
 for i,v in enumerate(q):
  a=Vector(q[i-1]);b=Vector(v);c=Vector(q[(i+1)%len(q)]);p=b+(a-b)*cut;t=b+(c-b)*cut
  for k in range(n):
   u=k/n;out.append(tuple((1-u)**2*p+2*u*(1-u)*b+u*u*t))
 return out
def extrude(name, outline, axis, lo, hi):
 other=[k for k in range(3)if k!=axis];vs=[]
 for depth in [lo,hi]:
  for a,b in outline:
   v=[0,0,0];v[axis]=depth;v[other[0]]=a;v[other[1]]=b;vs.append(v)
 N=len(outline);fs=[tuple(range(N-1,-1,-1)),tuple(N+i for i in range(N))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)]
 return mesh_object(name,vs,fs,con)
def closed_lathe(name,section,n=128):
 vs=[];rings=[];fs=[]
 for x,r in section:
  if r==0:rings.append([len(vs)]);vs.append((x,0,0))
  else:rings.append(list(range(len(vs),len(vs)+n)));vs.extend((x,r*math.cos(math.tau*i/n),r*math.sin(math.tau*i/n))for i in range(n))
 for j,a in enumerate(rings):
  b=rings[(j+1)%len(rings)]
  if len(a)==len(b)==1:continue
  for i in range(n):
   if len(a)==1:fs.append((a[0],b[(i+1)%n],b[i]))
   elif len(b)==1:fs.append((a[i],a[(i+1)%n],b[0]))
   else:fs.append((a[i],a[(i+1)%n],b[(i+1)%n],b[i]))
 return mesh_object(name,vs,fs,con)
# Base independent of LH, broader rounded slab with shallow central concave shoulders.
outline=roundpoly([(-.048,-.015),(-.046,-.022),(-.025,-.021),(0,-.017),(.024,-.021),(.046,-.021),(.049,-.015),(.048,.014),(.043,.020),(.019,.019),(0,.016),(-.021,.020),(-.046,.019)],cut=.18,n=12)
profiles=[(.87,.0065),(.91,.0065),(.95,.0062),(.98,.0057),(1,.005),(1.006,.0043),(1.008,.0035),(1.006,.0027),(1,.002),(.98,.0014),(.95,.0011),(.91,.001),(.87,.001)]
vs=[(x,y*k,z*k)for k,x in profiles for y,z in outline];N=len(outline);fs=[]
for j in range(len(profiles)-1):
 for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
fs.extend([tuple(range(N-1,-1,-1)),tuple((len(profiles)-1)*N+i for i in range(N))]);base=mesh_object('Editable independent RH base with rounded edge',vs,fs,con)
L=P['tube_length_m'];ro=P['tube_outer_radius_m'];ri=ro-P['tube_wall_m'];rr=.00045;section=[(.004,ro),(L-rr,ro)]
for i in range(1,13):
 a=math.pi/2*i/12;section.append((L-rr+rr*math.sin(a),ro-rr+rr*math.cos(a)))
section.append((L,ri+rr))
for i in range(1,13):
 a=math.pi/2*i/12;section.append((L-rr+rr*math.cos(a),ri+rr-rr*math.sin(a)))
section.extend([(.012,ri),(.012,0),(.004,0)]);tube=closed_lathe('Editable RH annular tube with rounded open rim',section)
# Bent U strap: face and two attachment feet are a continuous3mm estimated sheet.
earline=roundpoly([(.044,.008),(.043,.026),(.046,.032),(.051,.034),(.099,.034),(.104,.031),(.106,.026),(.106,.008),(.103,.008),(.103,.025),(.100,.029),(.097,.031),(.052,.031),(.049,.029),(.047,.025),(.047,.008)],cut=.16,n=12)
ear=extrude('Editable continuous bent middle ear with two feet',earline,2,-.014,.014)
# Drill only the bracket, not tube. Cylinder constructor axisX transformed toY.
hole=cylinder('Editable middle ear through aperture',(.075,.033,0),P['ear_hole_radius_m'],.025,con,axis=(0,1,0),n=96);bpy.context.view_layer.update();ear,ear_report=csg(ear,[],[hole],con,None,R,'Editable pierced middle bent ear')
# Wrapped terminal saddle: curved central face, formed longitudinal side flanges.
# At inner R10.4mm it enters the tube wall, not the lumen. Piercings cut BEFORE union.
A=72;outer=[];inner=[];half=math.radians(P['saddle_half_angle_degrees']);r0,r1=P['saddle_radii_m']
for i in range(A+1):
 a=-half+2*half*i/A;outer.append((-r1*math.cos(a),r1*math.sin(a)));inner.append((-r0*math.cos(a),r0*math.sin(a)))
# Add short flared side returns, observed in Store front/reverse; exact radii estimated.
outer=[(-.0045,-.017),(-.0038,-.015),*outer,(-.0038,.015),(-.0045,.017)]
inner=[(-.0032,-.017),(-.0025,-.015),*inner,(-.0025,.015),(-.0032,.017)]
cross=outer+list(reversed(inner));saddle=extrude('Editable terminal formed saddle with side returns',cross,0,*P['saddle_X_extent_m'])
# Round the longitudinal ends by subtracting corner caps from saddle only. Two circles plus slot.
cutters=[]
for x in P['saddle_circle_X_m']:
 q=cylinder('Editable saddle circular opening '+str(x),(x,-.014,0),P['saddle_circle_radius_m'],.045,con,axis=(0,1,0),n=96);cutters.append(q)
a,b=P['saddle_slot_X_extent_m'];w=P['saddle_slot_Z_width_m']*.5
slot=roundpoly([(a,-w),(b,-w),(b,w),(a,w)],cut=.20,n=14);cutters.append(extrude('Editable terminal saddle longitudinal slot',slot,1,-.035,.015));bpy.context.view_layer.update();saddle,saddle_report=csg(saddle,[],cutters,con,None,R,'Editable pierced terminal saddle - tube untouched')
# Original bounded welds. These are shape estimates, not measured bead/process.
def weld_ring():
 A=160;B=20;vs=[];fs=[]
 for i in range(A):
  a=math.tau*i/A;wave=1+.10*math.sin(17*a)+.045*math.sin(29*a+.6)
  for j in range(B):
   b=math.tau*j/B;r=.0115+.0017*wave*math.cos(b);vs.append((.007+.0017*wave*math.sin(b),r*math.cos(a),r*math.sin(a)))
 for i in range(A):
  for j in range(B):fs.append((i*B+j,((i+1)%A)*B+j,((i+1)%A)*B+(j+1)%B,i*B+(j+1)%B))
 return mesh_object('Editable original tube-to-base weld',vs,fs,con)
def line_weld(name,start,end,radius,phase):
 A=64;B=16;start=Vector(start);delta=Vector(end)-start;t=delta.normalized();u=t.cross(Vector((0,0,1))).normalized()
 if u.length==0:u=Vector((1,0,0))
 v=t.cross(u).normalized();vs=[];fs=[]
 for i in range(A):
  f=i/(A-1);centre=start+delta*f;rad=radius*(1+.10*math.sin(math.tau*11*f+phase)+.035*math.sin(math.tau*19*f))
  for j in range(B):
   a=math.tau*j/B;vs.append(tuple(centre+rad*(u*math.cos(a)+v*math.sin(a))))
 for i in range(A-1):
  for j in range(B):fs.append((i*B+j,(i+1)*B+j,(i+1)*B+(j+1)%B,i*B+(j+1)%B))
 fs.extend([tuple(range(B-1,-1,-1)),tuple((A-1)*B+j for j in range(B))]);return mesh_object(name,vs,fs,con)
welds=[weld_ring()]
for x in [.045,.104]:welds.append(line_weld('Editable bent ear foot weld '+str(x),(x,.0111,-.007),(x,.0111,.007),.0013,.4))
for x in [.140,.202]:
 for sign in [-1,1]:welds.append(line_weld('Editable terminal saddle spot weld '+str((x,sign)),(x-.004,-.0054,sign*.0098),(x+.004,-.0054,sign*.0098),.0012,.7))
drills=[cylinder('Editable true base mounting opening '+str(i),(0,y,z),P['base_hole_radius_m'],.05,con,n=96)for i,(y,z)in enumerate(P['base_hole_YZ_m'])]
bpy.context.view_layer.update();result,data=csg(base,[tube,ear,saddle,*welds],drills,parts,mat,R,'PF113001 related RH welded support - isolated candidate')
# Clean only numerical degeneracies after actual CSG, never add a global bevel/remesh.
bm=bmesh.new();bm.from_mesh(result.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for e in bm.edges:e.smooth=len(e.link_faces)==2 and e.calc_face_angle(0)<.55
bm.to_mesh(result.data);bm.free();result.data.update()
for f in result.data.polygons:f.use_smooth=True
result.data.calc_loop_triangles();zero=sum(t.area<=0 for t in result.data.loop_triangles);assert zero==0,zero
uv=result.data.uv_layers.new(name='Original physical150mm planar sectors')
for f in result.data.polygons:
 dominant=max(range(3),key=lambda k:abs(f.normal[k]));a,b=[k for k in range(3)if k!=dominant]
 for li in f.loop_indices:
  p=result.data.vertices[result.data.loops[li].vertex_index].co;uv.data[li].uv=(float(p[a])/.15+.5,float(p[b])/.15+.5)
checks=[check_mesh(result)];datum=bpy.data.objects.new('Front footrest RH isolated inspection datum - not installed',None);parts.objects.link(datum);result.parent=datum;con.hide_render=True;con.hide_viewport=True
studio(s,stage,Vector((.115,0,0)));s.camera.data.clip_start=.0001
for q in stage.objects:
 if q.type=='MESH':q.hide_render=True
 if q.type=='LIGHT':q.data.energy*=.08
source=H/'front-footrest-right-v1-geometry.blend';glb=H/'front-footrest-right-v1-geometry.glb';export(glb,[datum,result]);bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':sha(glb),'geometry':checks,'triangles':len(result.data.loop_triangles),'zero_area_triangles':zero,'collection':parts.name,'root':datum.name,'all_dimensions_estimated':True,'automatic_attachment_allowed':False,'middle_ear_drilled_before_union':True,'saddle_pierced_before_union':True,'no_coincident_full_lumen_cut':True,'no_post_csg_bevel_or_remesh':True,'CSG_report':{k:v for k,v in data.items()if k not in ['vertices','triangles']},'art_accepted':False};(H/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'geometry-source-check.json').write_text(json.dumps(report,indent=2)+'\n');print('FOOTREST_RH_GEOMETRY',json.dumps(report),flush=True)
