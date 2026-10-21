"""Original isolated PF113000-related metal support; bounded estimates, no installed datum."""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib
from mathutils import Vector
H=Path(__file__).resolve().parent; R=H.parents[2];O=R/'creative/reviews/front-footrest-left-v1';P=json.loads((H/'parameters.json').read_text());assert not(H/'preflight-manifest.json').exists()
sys.path.insert(0,str(H.parent/'throttle-control'))
from control_geometry import material,mesh_object,lathe,cylinder,csg,check_mesh,export,studio
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
parts=bpy.data.collections.new('WEWA_FRONT_FOOTREST_LEFT');con=bpy.data.collections.new('FOOTREST_LH_CONSTRUCTION_NOT_EXPORTED');stage=bpy.data.collections.new('FOOTREST_LH_STUDIO_NOT_EXPORTED')
for c in [parts,con,stage]:s.collection.children.link(c)
M=P['material_baseline'];mat=material('Representative black coated metal - chemistry unmeasured',M['linear_basecolor'],M['metallic'],M['roughness'])
# Rounded polygon corners: the domain is a qualitative uncalibrated outline, not a traced CAD drawing.
def roundpoly(q,cut=.18,n=12):
 out=[]
 for i,v in enumerate(q):
  a=Vector(q[i-1]);b=Vector(v);c=Vector(q[(i+1)%len(q)]);p=b+(a-b)*cut;t=b+(c-b)*cut
  for k in range(n):
   u=k/n;out.append(tuple((1-u)**2*p+2*u*(1-u)*b+u*u*t))
 return out
outline=roundpoly([(-.032,-.026),(-.025,-.038),(.013,-.039),(.029,-.029),(.032,-.018),(.022,-.012),(.021,.008),(.034,.017),(.031,.030),(.016,.040),(-.022,.037),(-.032,.026)])
# Closed sheet section with a raised central pad and rounded returned perimeter.
profiles=[(.80,.009),(.83,.009),(.86,.0086),(.89,.0075),(.92,.0056),(.95,.0038),(.97,.003),(.99,.003),(1,.0028),(1.008,.0022),(1.01,.0015),(1.008,.0008),(1,.0002),(.99,0),(.97,0),(.95,.0008),(.92,.0026),(.89,.0045),(.86,.0056),(.83,.006),(.80,.006)]
vs=[(x,y*k,z*k)for k,x in profiles for y,z in outline];n=len(outline);fs=[]
for j in range(len(profiles)-1):
 for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
fs.extend([tuple(range(n-1,-1,-1)),tuple((len(profiles)-1)*n+i for i in range(n))]);plate=mesh_object('Editable formed plate with continuous returned edge',vs,fs,con)
def closed_lathe(name, section, n=128):
 vs=[];rings=[];fs=[]
 for x,r in section:
  if r==0:rings.append([len(vs)]);vs.append((x,0,0))
  else:
   rings.append(list(range(len(vs),len(vs)+n)))
   vs.extend((x,r*math.cos(math.tau*i/n),r*math.sin(math.tau*i/n))for i in range(n))
 for j,a in enumerate(rings):
  b=rings[(j+1)%len(rings)]
  if len(a)==1 and len(b)==1:continue
  for i in range(n):
   if len(a)==1:fs.append((a[0],b[(i+1)%n],b[i]))
   elif len(b)==1:fs.append((a[i],a[(i+1)%n],b[0]))
   else:fs.append((a[i],a[(i+1)%n],b[(i+1)%n],b[i]))
 return mesh_object(name,vs,fs,con)
# Hollow tube built with true rounded annular far lip; base-side termination is explicitly unknown.
y0,z0=P['tube_YZ_m'];L=P['tube_length_m'];ro=P['tube_outer_radius_m'];ri=ro-P['tube_wall_m'];rr=.00045
section=[(.006,ro), (L-rr,ro)]
for i in range(1,13):
 a=math.pi/2*i/12;section.append((L-rr+rr*math.sin(a),ro-rr+rr*math.cos(a)))
section.append((L,ri+rr))
for i in range(1,13):
 a=math.pi/2*i/12;section.append((L-rr+rr*math.cos(a),ri+rr-rr*math.sin(a)))
section.extend([(.012,ri),(.012,0),(.006,0)])
tube=closed_lathe('Editable open tube and rounded far rim',section,n=128);tube.location=(0,y0,z0)
# Curved triangular gusset: curve follows the actual arched web, all offsets still estimates.
web=roundpoly([(.009,-.015),(.050,-.015),(.045,-.010),(.034,-.006),(.025,.001),(.019,.009),(.016,.020),(.009,.024)],cut=.20,n=10)
vs=[(x,y,z)for z in [-.0015,.0015]for x,y in web];nn=len(web);fs=[tuple(range(nn-1,-1,-1)),tuple(nn+i for i in range(nn))]+[(i,(i+1)%nn,(i+1)%nn+nn,i+nn)for i in range(nn)];gusset=mesh_object('Editable curved triangular welded web',vs,fs,con)
# Two separate formed longitudinal tabs. Their angular placement and section are bounded estimates.
def tab(angle):
 N=48;vs=[];rings=[]
 for i in range(N):
  t=i/(N-1);x=.083+.052*t;end=math.sin(math.pi*t)**.35;half=math.radians(20)*(.25+.75*end)
  cross=[]
  for j in range(13):
   a=angle-half+2*half*j/12;cross.append((x,y0+.0127*math.cos(a),z0+.0127*math.sin(a)))
  for j in range(12,-1,-1):
   a=angle-half+2*half*j/12;cross.append((x,y0+.0104*math.cos(a),z0+.0104*math.sin(a)))
  vs.extend(cross)
 count=26;fs=[tuple(range(count-1,-1,-1)),tuple((N-1)*count+j for j in range(count))]
 for i in range(N-1):
  for j in range(count):fs.append((i*count+j,(i+1)*count+j,(i+1)*count+(j+1)%count,i*count+(j+1)%count))
 return mesh_object('Editable longitudinal tab '+str(round(math.degrees(angle))),vs,fs,con)
tabs=[tab(math.radians(60)),tab(math.radians(-60))]
# Continuous original weld bead, not photographic height texture or a certified welding process.
def weld_ring():
 A=160;B=20;vs=[];fs=[]
 for i in range(A):
  a=math.tau*i/A;wave=1+.13*math.sin(17*a)+.06*math.sin(29*a+.6)
  for j in range(B):
   b=math.tau*j/B;r=.0115+.0017*wave*math.cos(b);vs.append((.010+.0017*wave*math.sin(b),y0+r*math.cos(a),z0+r*math.sin(a)))
 for i in range(A):
  for j in range(B):fs.append((i*B+j,((i+1)%A)*B+j,((i+1)%A)*B+(j+1)%B,i*B+(j+1)%B))
 return mesh_object('Editable original bounded tube-to-plate weld bead',vs,fs,con)
weld=weld_ring()
def linear_weld(name,start,end,radius,phase):
 A=72;B=16;start=Vector(start);delta=Vector(end)-start;tangent=delta.normalized();u=tangent.cross(Vector((0,0,1))).normalized();v=tangent.cross(u).normalized();vs=[];fs=[]
 for i in range(A):
  t=i/(A-1);centre=start+delta*t;rad=radius*(1+.12*math.sin(math.tau*11*t+phase)+.04*math.sin(math.tau*19*t));
  for j in range(B):
   a=math.tau*j/B;vs.append(tuple(centre+rad*(u*math.cos(a)+v*math.sin(a))))
 for i in range(A-1):
  for j in range(B):fs.append((i*B+j,(i+1)*B+j,(i+1)*B+(j+1)%B,i*B+(j+1)%B))
 fs.extend([tuple(range(B-1,-1,-1)),tuple((A-1)*B+j for j in range(B))]);return mesh_object(name,vs,fs,con)
web_welds=[]
for sign in [-1,1]:
 web_welds.append(linear_weld('Editable original web-to-plate weld '+str(sign),(.0105,-.011,sign*.0018),(.0105,.021,sign*.0018),.00125,.3))
 web_welds.append(linear_weld('Editable original web-to-tube weld '+str(sign),(.016,-.0089,sign*.0018),(.044,-.0089,sign*.0018),.0011,.8))
# Small post with a short cosmetic threaded region, not a nominated standard.
N=96; vs=[]; fs=[]
xs=[.007,.009,.010,.011,.0255]+[.026+.005*i/120 for i in range(121)]+[.0311,.0312,.0314,.0317,.0322,.0325,.0327]
for j,x in enumerate(xs):
 for i in range(N):
  a=math.tau*i/N
  if x<=.010:r=.0038
  elif x<.026:r=.003
  elif x<=.031:
   t=(x-.026)/.005;window=min(1,t/.06,(1-t)/.06);r=.0027+.0003*window*(.5+.5*math.cos(math.tau*(x-.026)/.001-a))
  else:
   # Distinct flat small terminal head over a reduced short neck; actual code/function unknown.
   r=next(r for xx,r in [( .0311,.0027),(.0312,.0033),(.0314,.0037),(.0317,.0038),(.0322,.0038),(.0325,.0037),(.0327,.0035)]if abs(x-xx)<1e-8)
  vs.append((x,P['post_YZ_m'][0]+r*math.cos(a),P['post_YZ_m'][1]+r*math.sin(a)))
for j in range(len(xs)-1):
 for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
# Truly planar closed end caps, no arbitrary tiny axial holes.
fs.extend([tuple(range(N-1,-1,-1)),tuple((len(xs)-1)*N+i for i in range(N))])
post=mesh_object('Editable small post - short cosmetic helical thread unknown standard',vs,fs,con)
# Hole cutters open true mount apertures. Their sizes do not derive from catalogue bolt codes.
drills=[cylinder('Editable plate hole '+str(i),(0,y,z),P['hole_radius_m'],.05,con,n=96)for i,(y,z)in enumerate(P['hole_YZ_m'])]
# Bore the nominal hidden tube base only above its technical estimated root closure.
# This cutter guarantees no weld or tab accidentally fills the visible lumen.
drills.append(cylinder('Editable clear tube lumen',(.1,y0,z0),ri,.176,con,n=128))
bpy.context.view_layer.update();result,data=csg(plate,[tube,gusset,*tabs,weld,*web_welds,post],drills,parts,mat,R,'PF113000 related metal support - isolated candidate')
# CSG results are final topology: no global bevel/remesh, no tangent repair.
bm=bmesh.new();bm.from_mesh(result.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(result.data);bm.free();result.data.update()
# Hard edges follow actual source dihedral sectors, curved patches retain smooth reflections.
bm=bmesh.new();bm.from_mesh(result.data)
for e in bm.edges:e.smooth=len(e.link_faces)==2 and e.calc_face_angle(0)<.55
bm.to_mesh(result.data);bm.free();result.data.update()
for f in result.data.polygons:f.use_smooth=True
result.data.calc_loop_triangles();zero=sum(t.area<=0 for t in result.data.loop_triangles);assert zero==0,zero
# Original physical-scale planar sectors. No phototexture and no normal-map assumption.
uv=result.data.uv_layers.new(name='Original physical 150mm planar sectors')
for f in result.data.polygons:
 axes=sorted(range(3),key=lambda k:abs(f.normal[k]));a,b=axes[:2]
 for li in f.loop_indices:
  v=result.data.vertices[result.data.loops[li].vertex_index].co;uv.data[li].uv=(float(v[a])/.150+.5,float(v[b])/.150+.5)
checks=[check_mesh(result)];datum=bpy.data.objects.new('Front footrest LH isolated inspection datum - not installed',None);parts.objects.link(datum);result.parent=datum
# Keep editable construction hidden locally, never altering another source/library.
con.hide_render=True;con.hide_viewport=True
studio(s,stage,Vector((.075,0,0)));s.camera.data.clip_start=.0001
for q in stage.objects:
 if q.type=='MESH':q.hide_render=True
 if q.type=='LIGHT':q.data.energy*=.08
source=H/'front-footrest-left-v1-geometry.blend';glb=H/'front-footrest-left-v1-geometry.glb';export(glb,[datum,result]);bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':sha(glb),'geometry':checks,'triangles':len(result.data.loop_triangles),'zero_area_triangles':zero,'collection':parts.name,'root':datum.name,'all_dimensions_estimated':True,'automatic_attachment_allowed':False,'no_post_csg_bevel_or_remesh':True,'CSG_report':{k:v for k,v in data.items()if k not in ['vertices','triangles']},'art_accepted':False};(H/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'geometry-source-check.json').write_text(json.dumps(report,indent=2)+'\n');print('FOOTREST_LH_GEOMETRY',json.dumps(report),flush=True)
