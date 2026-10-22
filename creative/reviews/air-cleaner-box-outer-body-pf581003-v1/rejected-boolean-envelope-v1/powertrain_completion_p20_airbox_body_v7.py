"""Original PF581003 photographed major exterior. No filter, partitions, hidden supports or structural interior claim."""
import bpy,sys,json,math,bmesh
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_loft_v4 import clean_smooth,recalc
R=Path(__file__).resolve().parents[1];name='air-cleaner-box-outer-body-pf581003-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
planpath='creative/research/powertrain-completion-p20-v1/airbox-outer-body-plan-v105.json';plan=json.loads((R/planpath).read_text());P=dict(schema=1,package='P20',component_id=plan['component_id'],source=planpath,identity=plan['identity'],scope=plan['scope'],all_dimensions_estimated=True,camera_calibrated=False,working_scale_m_px=.00042,technical_visual_skin_m=.0012,internal_status=plan['skin_status'],material=dict(name='Proposed clean black moulded air cleaner exterior',base_color_linear=[.014,.016,.019,1],metallic=0,roughness=.43),package_complete=False,art_accepted=False)
P['excluded']=['Existing carb boot, hoses and clamps','Filter and partitions/hidden supports/air-flow route','Metal screw hardware and hidden mounting stacks','Vendor pixels, label/logo and wear','Structural wall thickness, mass, airflow or installed pose certification']
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
C=[Vector(((x-365)*.00042,(500-y)*.00042))for x,y in plan['contour_pixels_61513']];curve=[]
for i in range(len(C)):
 p=[C[(i+j)%len(C)]for j in range(4)]
 for j in range(24):
  t=j/24;w=[(1-t)**3/6,(3*t*t*t-6*t*t+4)/6,(-3*t*t*t+3*t*t+3*t+1)/6,t*t*t/6];curve.append(sum((a*b for a,b in zip(p,w)),Vector((0,0))))
def cross(a,b):return a.x*b.y-a.y*b.x
N=256;M=48;radii=[]
for i in range(N):
 d=Vector((math.cos(math.tau*i/N),math.sin(math.tau*i/N)));hits=[]
 for a,b in zip(curve,curve[1:]+curve[:1]):
  e=b-a;den=cross(d,e)
  if abs(den)<1e-14:continue
  t=cross(a,e)/den;u=cross(a,d)/den
  if t>0 and -1e-8<=u<=1+1e-8:hits.append(t)
 hits=sorted(set(round(v,12)for v in hits));assert len(hits)==1,(i,hits);radii.append(hits[0])
def bump(t):return math.exp(-t**4) if abs(t)<3 else 0
A=math.radians(55);ca,sa=math.cos(A),math.sin(A)
def accessxy(u,v):return (.005+ca*u-sa*v, -.010+sa*u+ca*v)
def localaccess(x,y):return ca*(x-.005)+sa*(y+.010),-sa*(x-.005)+ca*(y+.010)
def segdistance(x,y,a,b):
 p=Vector((x,y));a=Vector(a);b=Vector(b);t=max(0,min(1,(p-a).dot(b-a)/(b-a).length_squared));return (p-a-t*(b-a)).length
frontcross=[[(.011,.134),(-.011,.015)],[(-.045,.086),(.041,.048)]]
backcross=[[(-.035,.106),(.034,.027)],[(-.034,.027),(.034,.106)]]
def frontz(x,y,t):
 z=.0045*(1-t*t)**2
 for a,b in frontcross:z-=.0008*math.exp(-(segdistance(x,y,a,b)/.0024)**4)
 return z

def backh(x,y,t):
 upper=bump(x/.050)*bump((y-.073)/.068);h=.062+.014*(1-t*t)**2+.028*upper
 u,v=localaccess(x,y);w=math.exp(-((u/.105)**8+(v/.040)**8));h=h*(1-w)+.100*w
 for a,b in backcross:h-=.0009*math.exp(-(segdistance(x,y,a,b)/.0023)**4)*upper
 fade=max(0,min(1,(1-t)/.10));fade=fade*fade*(3-2*fade)
 return .062+(h-.062)*fade

def hull(label,inside=False):
 V=[];F=[];shrink=.978 if inside else 1;delta=.002 if inside else 0
 for back in [False,True]:
  offset=len(V);V.append((0,0,-backh(0,0,0)+delta if back else frontz(0,0,0)-delta))
  for k in range(1,M+1):
   t=k/M
   for i,r in enumerate(radii):
    a=math.tau*i/N;x=.985*t*r*math.cos(a);y=.985*t*r*math.sin(a);z=-backh(x,y,t)+delta if back else frontz(x,y,t)-delta;V.append((x*shrink,y*shrink,z))
  for i in range(N):j=(i+1)%N;F.append((offset,offset+1+i,offset+1+j))
  for k in range(M-1):
   for i in range(N):j=(i+1)%N;a=offset+1+k*N+i;b=offset+1+k*N+j;F.append((a,b,b+N,a+N))
 B=1+M*N;front_ring=[1+(M-1)*N+i for i in range(N)];back_ring=[B+1+(M-1)*N+i for i in range(N)]
 # Analytic rolled front/back corners and shallow photographed perimeter seam.
 profiles=[]
 for j in range(1,13):
  a=math.pi/2*j/12;profiles.append((.985+.018*math.sin(a),-.004*(1-math.cos(a))))
 for j in range(1,25):
  z=-.004-.054*j/24;r=1.003-.006*math.exp(-((z+.011)/.0018)**2);profiles.append((r,z))
 for j in range(1,12):
  a=math.pi/2*j/12;profiles.append((.985+.018*math.cos(a),-.058-.004*math.sin(a)))
 rows=[front_ring]
 for r,z in profiles:
  row=[]
  for i,Rr in enumerate(radii):
   a=math.tau*i/N;row.append(len(V));zz=z+(delta if z<-.031 else -delta);V.append((r*Rr*math.cos(a)*shrink,r*Rr*math.sin(a)*shrink,zz))
  rows.append(row)
 rows.append(back_ring)
 for a,b in zip(rows,rows[1:]):
  for i in range(N):j=(i+1)%N;F.append((a[i],b[i],b[j],a[j]))
 ob=mesh_object(label,V,F);clean_smooth(ob);return ob
body=hull('PF581003_MAJOR_ASYMMETRIC_EXTERIOR_SHELL')
inner=body.copy();inner.data=body.data.copy();inner.name='Technical normal-offset skin closure, no engineered interior';bpy.context.scene.collection.objects.link(inner)
bm=bmesh.new();bm.from_mesh(inner.data);bm.normal_update()
for v in bm.verts:v.co-=v.normal*.0012
bm.to_mesh(inner.data);bm.free();inner.data.update();recalc(inner)
def boolean(target,tool,op,label):
 recalc(target);recalc(tool);print('BOOLEAN_BEFORE',label,len(target.data.vertices),len(tool.data.vertices),flush=True);bpy.context.view_layer.objects.active=target;m=target.modifiers.new(label,'BOOLEAN');m.operation=op;m.solver='EXACT';m.object=tool;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(tool,do_unlink=True);print('BOOLEAN_AFTER',label,len(target.data.vertices), 'VOLUME',sum(target.data.vertices[t.vertices[0]].co.dot(target.data.vertices[t.vertices[1]].co.cross(target.data.vertices[t.vertices[2]].co))/6 for t in target.data.loop_triangles)if not target.data.calc_loop_triangles() else 0, flush=True)
def plate(label,poly,z0,z1):
 n=len(poly);ob=mesh_object(label,[(x,y,z)for z in [z0,z1]for x,y in poly],[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]);recalc(ob);return ob
# Three exterior moulded mounting eyes, linked to source-constrained seam rather than an invented support frame.
eye_centres=[]
for px,py in plan['working_visible_layout_m']['mount_eyes_pixels']:
 c=Vector(((px-365)*.00042,(500-py)*.00042));near=min(curve,key=lambda q:(q-c).length);root=near+(-near).normalized()*.006;d=(c-root).normalized();ang=math.atan2(d.y,d.x);poly=[]
 for centre,base in [(c,ang-math.pi/2),(root,ang+math.pi/2)]:
  for j in range(48):a=base+math.pi*j/48;poly.append(tuple(centre+Vector((math.cos(a),math.sin(a)))*.008))
 boolean(body,plate('Visible moulded eye root',poly,-.006,.001),'UNION','Observed outer eye/root')
 eye_centres.append(list(c))
# Finite interior skin closure is cut LAST, after the observed exterior mouths, so nested disconnected normals cannot reverse the solid.
def cyl(r,depth,loc,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=r,depth=depth,location=loc,rotation=rot);return bpy.context.object
for c in eye_centres:boolean(body,cyl(.0035,.25,(c[0],c[1],-.04)),'DIFFERENCE','Observed open mounting eye')
# Circular exterior boot interface only; independent boot itself is not copied.
boolean(body,cyl(.018,.10,(0,.106,-.102)),'DIFFERENCE','Visible circular boot-root interface, estimated pose')
def rounded(w,h,r):
 p=[]
 for cx,cy,a in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for j in range(20):t=math.radians(a+90*j/20);p.append((cx+r*math.cos(t),cy+r*math.sin(t)))
 return p
boolean(body,plate('Actual long exterior access aperture cut',[accessxy(*q)for q in rounded(.136,.022,.002)],-.16,-.070),'DIFFERENCE','Observed long access opening')
# Rectangular mouth joins the main exterior shell. Ring connects actual interior/exterior skins at visible opening.
def rectring(label,outer,inner,a,b,axis='Z',mapxy=lambda x,y:(x,y)):
 N=len(outer);V=[]
 for z in [a,b]:
  for loop in [outer,inner]:
   for x,y in loop:
    x,y=mapxy(x,y);V.append((x,y,z)if axis=='Z'else(z,-.102+x,-.035+y))
 F=[]
 for i in range(N):j=(i+1)%N;F.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
 ob=mesh_object(label,V,F);clean_smooth(ob);return ob
neck=rectring('Observed rectangular three-vane mouth',rounded(.070,.045,.004),rounded(.062,.037,.002),.064,.105,'X')
neck.name='OBSERVED_RECTANGULAR_MOUTH_WITH_THREE_VANES' # Keep distinct exterior patch; root/fit remains qualified, no fragile coplanar shell union
bpy.ops.mesh.primitive_cube_add(size=1,location=(.087,-.102,-.035));tool=bpy.context.object;tool.dimensions=(.09,.062,.037);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);boolean(body,tool,'DIFFERENCE','Open actual rectangular mouth')
for y in [-.1195,-.102,-.0845]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=(.086,y,-.035));tool=bpy.context.object;tool.dimensions=(.037,.0018,.041);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);boolean(neck,tool,'UNION','Observed exterior intake vane')
boolean(body,inner,'DIFFERENCE','Finite normal-offset export closure through already open exterior mouths')
# Moulded outer access surround, connected locally; no hidden filter cartridge/supports.
surround=rectring('EXTERIOR_MOULDED_ACCESS_SURROUND',rounded(.166,.048,.005),rounded(.138,.024,.002),-.096,-.104,mapxy=accessxy)
clean_smooth(neck);clean_smooth(surround)
clean_smooth(body)
cover=rectring('REMOVABLE_TRIANGULATED_OUTER_ACCESS_COVER',rounded(.160,.041,.004),rounded(.138,.025,.002),-.103,-.110,mapxy=accessxy)
segments=[((-.063,-.015),(-.033,.015)),((-.033,.015),(.003,-.015)),((.003,-.015),(.039,.015)),((.039,.015),(.063,-.015))]
for a,b in segments:
 a,b=Vector(a),Vector(b);d=(b-a).normalized();n=Vector((-d.y,d.x))*.0015;poly=[accessxy(*(a-n)),accessxy(*(b-n)),accessxy(*(b+n)),accessxy(*(a+n))];boolean(cover,plate('Source-interpreted exterior diagonal web',poly,-.106,-.110),'UNION','Visible triangulated cover web')
for u,v in [(-.067,-.018),(-.067,.018),(.067,-.018),(.067,.018)]:
 x,y=accessxy(u,v);boolean(cover,cyl(.0055,.004,(x,y,-.108)),'UNION','Observed moulded corner fastener pad, hardware omitted')
clean_smooth(cover)

# Exact boolean roots can create submicron-altitude slivers with an unstable float32 normal.
# Collapse only their <50um shortest source edge, before export; no GLB normal edits.
repairs=[]
for target in [body,cover]:
 for attempt in range(300):
  bm=bmesh.new();bm.from_mesh(target.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.normal_update();candidates=[]
  for f in bm.faces:
   lengths=[e.calc_length()for e in f.edges];alt=2*f.calc_area()/max(lengths)
   if (alt<1e-7 or f.calc_area()<1e-14) and min(lengths)<.00005:candidates.append((alt,min(f.edges,key=lambda e:e.calc_length())))
  if not candidates:
   bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
   for f in bm.faces:f.smooth=True
   for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(45))
   bm.to_mesh(target.data);bm.free();target.data.update();break
  alt,e=min(candidates,key=lambda q:q[0]);repairs.append(dict(object=target.name,altitude_m=alt,collapsed_edge_length_m=e.calc_length()));bmesh.ops.collapse(bm,edges=[e]);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(target.data);bm.free();target.data.update()
 else:raise AssertionError('Sliver source cleanup did not converge')
 for ob in [target]:
  ob.data.calc_loop_triangles();print('CLEANED',ob.name,len(repairs),min(t.area for t in ob.data.loop_triangles),flush=True)
(O/'source-sliver-cleanup.json').write_text(json.dumps(dict(method='Local source edge collapse only for submicron-altitude exact-boolean slivers with shortest edge under50um',repairs=repairs,glb_buffer_repair=False,scope='Numerical source topology cleanup below documentary dimensional uncertainty; exterior form still requires manual review'),indent=2)+'\n')

P.update(source_contour_pixels=plan['contour_pixels_61513'],source_outline_method='Original periodic cubic contour with unique uniform-angle radial intersections',eye_centres_source_m=eye_centres,actual_intake_vanes=3,cover_web_segments_uv_m=[[list(a),list(b)]for a,b in segments],technical_skin_closure='1.2mm source-normal export closure only; NOT source-certified internal wall/filterbox geometry or mass/collision model',boot_rebuilt=False,whole_motorcycle_pose_certified=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n')
for ob in [body,cover,neck,surround]:ob['scope']=P['scope'];ob['internal_geometry_status']=P['technical_skin_closure']
assert max(v.co.y for v in body.data.vertices)>.13 and min(v.co.y for v in body.data.vertices)<-.12, 'Major silhouette lost during boolean'
finish_source(H,O,P)
(O/'outer-body-construction-check.json').write_text(json.dumps(dict(method='Original noncircular C2 source contour, smooth radial broad faces, analytic rolled side edges/perimeter groove, asymmetric rear roof/shoulder; real observed mouth/eye openings',angular_samples=N,radial_samples=M,body_has_filter_or_partitions=False,source_identity=plan['identity'],technical_closure_only=True,observed_intake_vanes=3,removable_cover_state='Installed triangulated cover from first physical sample; missing-cover second sample only constrains opening, never a second simultaneous cover',remaining=['Metal fasteners, hoses/boot/clips separate','Internal construction and structural thickness unqualified','Whole-motorcycle pose/mounting stack/fit unknown']),indent=2)+'\n')
