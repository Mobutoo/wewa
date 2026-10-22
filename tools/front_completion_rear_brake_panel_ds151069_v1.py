"""Original DS151069 visible casting from actual front/reverse photos; not DS151076 or DJ151092."""
import bpy,runpy,math,json
from pathlib import Path
R=Path('/workspace/wewa');K='rear-brake-panel-ds151069-visible-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));N=256;RR=.075
def lathe(name,profile,xy=(0,0),n=N):
 v=[(xy[0]+r*math.cos(2*math.pi*j/n),xy[1]+r*math.sin(2*math.pi*j/n),z) for r,z in profile for j in range(n)];f=[]
 for i in range(len(profile)):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;c=((i+1)%len(profile))*n;f.append((a,b,c+(j+1)%n,c+j))
 ob=u['mesh_object'](name,v,f);u['orient'](ob);return ob
def cyl(name,r,depth,xy,z,n=128):
 bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=depth,location=(xy[0],xy[1],z));ob=bpy.context.object;ob.name=name;return ob
def union(ob):u['boolean'](body,ob,'UNION')
def cut(ob):u['boolean'](body,ob,'DIFFERENCE')
def rounded_outline(points,rad=.0018,steps=5):
 out=[]
 for i,p in enumerate(points):
  a=points[i-1];b=points[(i+1)%len(points)];da=math.hypot(a[0]-p[0],a[1]-p[1]);db=math.hypot(b[0]-p[0],b[1]-p[1]);d=min(rad,da*.25,db*.25);aa=(p[0]+(a[0]-p[0])*d/da,p[1]+(a[1]-p[1])*d/da);bb=(p[0]+(b[0]-p[0])*d/db,p[1]+(b[1]-p[1])*d/db)
  for j in range(steps+1):t=j/steps;out.append(((1-t)**2*aa[0]+2*t*(1-t)*p[0]+t*t*bb[0],(1-t)**2*aa[1]+2*t*(1-t)*p[1]+t*t*bb[1]))
 return out
def prism(name,outline,z0,z1):
 n=len(outline);v=[(x,y,z)for z in [z0,z1]for x,y in outline];f=[tuple(reversed(range(n))),tuple(n+j for j in range(n))]
 for j in range(n):a=j;b=(j+1)%n;f.append((a,b,b+n,a+n))
 ob=u['mesh_object'](name,v,f);u['orient'](ob);return ob
def rib(name,p0,p1,width,height,zcentre,steps=36):
 # Rounded tapered elliptical rib volume, embedded in visible casting floor; no arbitrary weld beads.
 dx=p1[0]-p0[0];dy=p1[1]-p0[1];L=math.hypot(dx,dy);nx=-dy/L;ny=dx/L;nc=16;v=[(p0[0],p0[1],zcentre)];f=[]
 for i in range(1,steps):
  t=i/steps;env=math.sin(math.pi*t)**.38
  for j in range(nc):a=2*math.pi*j/nc;w=width*env*math.cos(a);v.append((p0[0]+dx*t+nx*w,p0[1]+dy*t+ny*w,zcentre+height*env*math.sin(a)))
 end=len(v);v.append((p1[0],p1[1],zcentre))
 for j in range(nc):f.append((0,1+(j+1)%nc,1+j))
 for i in range(steps-2):
  for j in range(nc):a=1+i*nc+j;b=1+i*nc+(j+1)%nc;f.append((a,b,b+nc,a+nc))
 last=1+(steps-2)*nc
 for j in range(nc):f.append((last+j,last+(j+1)%nc,end))
 ob=u['mesh_object'](name,v,f);u['orient'](ob);return ob
def arcband(name,r0,r1,z0,z1,a0,a1,xy=(0,0),steps=160):
 v=[];f=[]
 for r,z in [(r0,z0),(r1,z0),(r1,z1),(r0,z1)]:
  for i in range(steps+1):a=math.radians(a0+(a1-a0)*i/steps);v.append((xy[0]+r*math.cos(a),xy[1]+r*math.sin(a),z))
 m=steps+1
 for k in range(4):
  for i in range(steps):a=k*m+i;b=((k+1)%4)*m+i;f.append((a,a+1,b+1,b))
 f.append((0,m,2*m,3*m));f.append((steps,3*m+steps,2*m+steps,m+steps));ob=u['mesh_object'](name,v,f);u['orient'](ob);return ob
# One continuous rounded central boss, casting floor, visible turned peripheral rim, central through-bore.
profile=[(.0078,-.021),(.0148,-.021),(.0156,-.0204),(.0160,-.0193),(.0160,-.0065),(.0168,-.0050),(.0635,-.0045),(.0660,-.0060),(.0668,-.0175),(.0674,-.0190),(.0690,-.0190),(.0690,-.0170),(.0700,-.0170),(.0700,-.0153),(.0691,-.0153),(.0691,-.0137),(.0706,-.0137),(.0710,-.0115),(.0738,-.0115),(.0750,-.0095),(.0750,-.0005),(.0744,.0003),(.0734,.0007),(.0220,.0000),(.0200,.0006),(.0178,.0032),(.0157,.0062),(.0130,.0078),(.0115,.0082),(.0078,.0082)]
body=lathe('DS151069_VISIBLE_CAST_PANEL_FRONT_AND_BARE_REVERSE',profile)
# Rounded source-observed tapered ear; actual round passage and reverse hex pocket cut below.
ear=(1.39*RR,-.26*RR);cam=(-.60*RR,-.34*RR)
outline=rounded_outline([(.045,.035),(.073,.027),(.109,-.008),(.115,-.016),(.115,-.024),(.107,-.031),(.077,-.036),(.043,-.053)])
union(prism('Visible cast lateral reaction ear envelope',outline,-.009,.001))
union(lathe('Ear rounded circular bearing face',[(.00435,-.009),(.0100,-.009),(.0116,-.008),(.0121,-.0065),(.0121,.0033),(.0115,.0050),(.0105,.0055),(.00435,.0055)],ear,128))
# Actual offset machined bore and rear ring, not an invented insert/bushing specification.
union(lathe('Offset bore raised casting envelope',[(.0068,-.018),(.0092,-.018),(.0100,-.0174),(.0105,-.0155),(.0105,.0008),(.0100,.0028),(.0090,.0038),(.0068,.0038)],cam,128))
# Three individually traced front ribs converge on the ear. Dimensions are working estimates.
front_ribs=[((.47*RR,.30*RR),(1.32*RR,-.18*RR),.0017,.0033),((.43*RR,-.04*RR),(1.32*RR,-.27*RR),.0019,.0035),((.42*RR,-.39*RR),(1.32*RR,-.35*RR),.0018,.0030)]
for i,(a,b,w,h)in enumerate(front_ribs):union(rib('Observed exterior rib '+str(i+1),a,b,w,h,.0004))
union(arcband('Observed interrupted circumferential front track',.0660,.0676,-.0010,.0016,28,310))
# Curved label cartouche: observed outline only, no invented calibrated lettering or graduation.
union(arcband('USABLERANGE cartouche visible frame envelope',.0278,.0368,-.0005,.0013,60,120,cam,64))
dimple=(.59*RR,.34*RR);union(cyl('Small visible round pad with shallow dimple',.0030,.0020,dimple,.0005,64));bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=.00125,location=(*dimple,.0018));cut(bpy.context.object)
# Reverse pose registration: reflection + in-plane rotation fitted to common ear/cam projections, not mirror-copy of front details.
phi=math.radians(31.3)
def backxy(x,y):return (RR*(math.cos(phi)*x+math.sin(phi)*y),RR*(math.sin(phi)*x-math.cos(phi)*y))
union(lathe('Visible reverse central annular web wall',[(.0270,-.004),(.0288,-.004),(.0293,-.005),(.0293,-.0165),(.0288,-.018),(.0275,-.018),(.0270,-.017)],n=192))
union(lathe('Visible reverse intermediate concentric wall',[(.0457,-.004),(.0475,-.004),(.0480,-.005),(.0480,-.0115),(.0474,-.013),(.0462,-.013),(.0457,-.012)],n=192))
inner_angles=[2,44,88,134,180,226,270,316]
for i,a in enumerate(inner_angles):
 c=math.cos(math.radians(a));s=math.sin(math.radians(a));union(rib('Individually observed short reverse spoke '+str(i+1),backxy(.20*c,.20*s),backxy(.385*c,.385*s),.00115,.0055,-.0098,24))
outer_angles=[0,43,89,134,181,225,270,316]
for i,a in enumerate(outer_angles):
 c=math.cos(math.radians(a));s=math.sin(math.radians(a));union(rib('Individually observed outer reverse web '+str(i+1),backxy(.37*c,.37*s),backxy(.90*c,.90*s),.00155,.0048,-.0085,40))
# Seven round pads individually located in actual bare reverse image, not a generated repeated part pattern.
pads=[(.50,-.03),(.00,.50),(.00,-.53),(-.30,.73),(.62,.49),(.75,-.27),(.27,-.75)]
for i,(x,y) in enumerate(pads):union(cyl('Observed reverse round pad '+str(i+1),.0031,.008,backxy(x,y),-.010,64))
post=backxy(.76,-.065);union(cyl('Observed reverse post rounded base',.0080,.008,post,-.008,96));union(cyl('Observed reverse cylindrical post no hidden retention',.0058,.024,post,-.016,96))
# The actual three openings remain through the casting; hidden hardware is excluded.
cut(cyl('Actual offset through-bore',.0068,.12,cam,0,128));cut(cyl('Actual ear through-bore',.00435,.12,ear,0,128));cut(cyl('Actual central through-bore',.0078,.12,(0,0),0,128))
bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.0075,depth=.010,location=(ear[0],ear[1],-.0085));pocket=bpy.context.object;pocket.rotation_euler.z=math.radians(30);cut(pocket)
audit=u['clean_audit'](body)
# Keep machined flat annuli planar; evaluated clean mesh retains source-derived smooth casting elsewhere.
for p in body.data.polygons:
 if abs(p.normal.z)>.999999:p.use_smooth=False
body.data.update()
params={'package':'LEGACY15-REAR-BRAKE','component_id':'MOTO-REAR-BRAKE-PANEL-DS151069-VISIBLE-STUDY-001','scope':'Broad DS151069 casting exterior and actually exposed bare reverse. Three true through-openings, lateral pierced ear/reverse hex pocket, three front ribs, visible rear annular/radial webs, seven individually located pads and one post. No hidden shoes, fasteners, threads, bearings or arbitrary inside mechanism.','source':'Boyle rear-brake-panel-evidence-v1 physical Parton front/oblique/reverse, Matriz front and D04 rear hub DS151069','all_dimensions_estimated':True,'working_radius_m':RR,'bounds_m':{'plate_radius':[.065,.085],'base_wall':[.003,.007],'total_hub_thickness':[.020,.038],'central_bore_radius':[.0065,.010],'cam_bore_radius':[.0055,.0085],'front_rib_height':[.002,.0055],'reverse_web_height':[.004,.016]},'working_profile_r_z_m':profile,'working_ear_xy_m':ear,'working_cam_xy_m':cam,'front_ribs':front_ribs,'back_to_front_registration_deg':31.3,'back_registration_status':'Approximate reflection/rotation from common cam/ear projected positions, perspective/depth parallax uncalibrated','rear_short_web_angles_traced':inner_angles,'rear_outer_web_angles_traced':outer_angles,'rear_round_pads_source_normalized':pads,'omissions':['Exact cast text/logo/letter forms; cartouche envelope only','Unseen fine rim cross-section tolerances','Shoe/contact hardware and hidden fastening','No transferred DS151076 or DJ151092 details'],'material':'Clean silver metal hypothesis, no measured alloy/finish/grain or regional machining certification','current_RDC_fit':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(params,indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'three_through_bores':True,'reverse_pocket_is_recess_not_fourth_through_hole':True},indent=2));(O/'child-plan.json').write_text(json.dumps({'package':'LEGACY15-REAR-BRAKE','component_id':params['component_id'],'child':'DS151069 rear brake panel visible casting extension LEGACY15','scope':params['scope']+' Working dimensions and current RDC variant remain estimated; not OEM certified or installed brake function.','protocols':['front_completion_rear_brake_panel_ds151069_v1.py','front_completion_front10_mesh_helpers_v1.py','front_completion_rear_panel_render_front19_v1.py','front_completion_front10_material_v1.py'],'remaining':params['omissions']+['Current hub fit, axle/cam/shoe interfaces and assembled function']},indent=2));u['gray_save'](H,'rear-brake-panel',[body])
