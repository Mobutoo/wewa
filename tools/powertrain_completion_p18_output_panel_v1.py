"""Original LH output-region exterior casting panel; not the retained output cover."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='crankcase-lh-output-panel-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
outline=[[609,186],[639,177],[667,191],[711,181],[741,181],[773,197],[804,207],[813,245],[835,292],[841,351],[875,404],[884,446],[894,490],[905,541],[901,593],[890,636],[903,665],[889,690],[854,712],[706,706],[620,706],[604,666],[593,612],[611,579],[616,534],[607,483],[592,455],[600,399],[609,350],[603,294],[597,249]]
scale=.00045
P={'schema':1,'package':'P18','component_id':'MOTO-CRANKCASE-LH-OUTPUT-PANEL-001','source':'creative/research/powertrain-completion-p18-v1/lh-output-exterior-plan-v3.json','outline_pixels':outline,'scale_m_px':scale,'scale_range_m_px':[.00035,.00055],'projection_origin_px':[747,380],'all_dimensions_estimated':True,'camera_calibrated':False,'base_thickness_m':.009,'base_thickness_range_m':[.005,.016],'seat_outer_radius_m':.031,'seat_bore_radius_m':.0195,'seat_height_m':.021,'scope':'LH rear/output exterior casting panel beside magneto cavity. Projected contour, raised circular seat, radial webs and visible mounting bores only. Left cut follows cavity boundary; back/plain thickness is a finite review closure. Actual bearings/seals, underside, other case half, installed fit and historic output cover excluded.','material':{'name':'Proposed clean cast aluminium exterior','base_color_linear':[.33,.35,.37,1],'metallic':.7,'roughness':.44},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
def xy(p):return ((p[0]-747)*scale,(380-p[1])*scale)
def plate(name,poly,zlo,zhi):
 area=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(poly,poly[1:]+poly[:1]));poly=poly if area>0 else list(reversed(poly));n=len(poly)
 return mesh_object(name,[(x,y,z)for z in [zlo,zhi]for x,y in poly],[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)])
# Bounded quadratic fillets soften the photographed cast perimeter, without spline overshoot.
pts=[Vector(xy(p))for p in outline];poly=[]
for i,b in enumerate(pts):
 a,c=pts[i-1],pts[(i+1)%len(pts)];q=min(.003,(b-a).length*.25,(c-b).length*.25);u=b-(b-a).normalized()*q;v=b+(c-b).normalized()*q
 for j in range(8):t=j/8;poly.append(tuple((1-t)**2*u+2*(1-t)*t*b+t*t*v))
ob=plate('LH_OUTPUT_REGION_CASTING_FACE_WITH_SEAT_AND_RIBS',poly,-.009,0)
def boolean(cut,op,label):
 bm=bmesh.new();bm.from_mesh(cut.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cut.data);bm.free()
 bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new(label,'BOOLEAN');m.operation=op;m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
def cylinder(radius,depth,loc):
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=radius,depth=depth,location=loc);return bpy.context.object
# A continuous height-field replaces the rejected flat core. Relief amplitudes
# are bounded estimates, not depth recovered from an uncalibrated photograph.
P['core_relief_method']='Continuous sampled convex output shoulder and lower transverse cast ridge, silhouette-clipped to traced perimeter'
P['core_relief_height_range_m']=[.002,.010]
def height(x,y):return .002+.005*math.exp(-((x/.065)**2+(y/.080)**2))+.003*math.exp(-((y+.088)/.013)**2)
nx,ny=60,112;xlo,xhi=-.075,.077;ylo,yhi=-.153,.097;V=[];F=[]
for j in range(ny+1):
 for i in range(nx+1):
  x=xlo+(xhi-xlo)*i/nx;y=ylo+(yhi-ylo)*j/ny;V.append((x,y,height(x,y)))
for j in range(ny):
 for i in range(nx):a=j*(nx+1)+i;F.append((a,a+1,a+nx+2,a+nx+1))
border=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1)for j in range(ny-1,0,-1)]
lower=[]
for idx in border:x,y,z=V[idx];lower.append(len(V));V.append((x,y,-.009))
for k in range(len(border)):
 q=(k+1)%len(border);F.append((border[k],lower[k],lower[q],border[q]))
F.append(tuple(reversed(lower)))
core=mesh_object('Nonplanar exterior core construction',V,F)
# The prism is used only as a silhouette cutter, not left as overlapping slabs.
mask=plate('Projected contour silhouette mask',poly,-.010,.030)
bpy.data.objects.remove(ob,do_unlink=True);ob=core;ob.name='LH_OUTPUT_REGION_CASTING_FACE_WITH_SEAT_AND_RIBS'
boolean(mask,'INTERSECT','Trace-clipped continuous exterior relief')
# Rounded frustum seat, integrated into face; actual bearing/seal is not built.
profile=[(.034,-.001),(.034,.002),(.032,.005),(.031,.009),(.031,.017),(.0305,.020),(.0295,.021)]
N=160;V=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z)for r,z in profile for i in range(N)];F=[tuple(reversed(range(N))),tuple((len(profile)-1)*N+i for i in range(N))]
for k in range(len(profile)-1):
 for i in range(N):F.append((k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i))
boolean(mesh_object('Seat union construction',V,F),'UNION','Raised output circular seat')
# Cast radial webs, narrow domed sections, each genuinely joined to seat and base.
ends=[[650,299],[780,268],[837,362],[855,478],[716,511],[649,446]]
P['rib_endpoints_pixels']=ends
for index,end in enumerate(ends):
 e=Vector(xy(end));d=e.normalized();n=Vector((-d.y,d.x));V=[];F=[];steps=18
 for k in range(steps+1):
  t=k/steps;c=d*.026+(e-d*.026)*t;w=.0035*(1-.35*t);base=height(c.x,c.y);rib_height=base+.010*(1-t)+.004*t
  for offset,z in [(-w,-.0015),(-w,base+.001),(0,rib_height),(w,base+.001),(w,-.0015)]:
   p=c+n*offset;V.append((p.x,p.y,z))
 for k in range(steps):
  for j in range(5):F.append((k*5+j,k*5+(j+1)%5,(k+1)*5+(j+1)%5,(k+1)*5+j))
 F += [tuple(reversed(range(5))),tuple(steps*5+j for j in range(5))]
 boolean(mesh_object('Radial web union '+str(index),V,F),'UNION','External cast web '+str(index))
# Visible mounting bosses are integrated rings, distinct from the absent bolts.
bosses=[([637,238],.010,.0065),([747,200],.009,.0045),([786,237],.011,.006),([831,567],.009,.004),([882,659],.014,.008),([660,608],.016,.010)]
for i,(p,r,bore) in enumerate(bosses):
 x,y=xy(p);boolean(cylinder(r,.017,(x,y,.004)),'UNION','Visible mount boss '+str(i))
boolean(cylinder(.0195,.080,(0,0,0)),'DIFFERENCE','Output seat open bore')
for i,(p,r,bore) in enumerate(bosses):
 x,y=xy(p);boolean(cylinder(bore,.080,(x,y,0)),'DIFFERENCE','Visible mount bore '+str(i))
P['bosses_pixels_radius_bore_m']=bosses
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n')
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:f.smooth=abs(f.normal.z)<.97 or all(abs(v.co.z-height(v.co.x,v.co.y))<.00005 for v in f.verts)
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(35))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];finish_source(H,O,P)
