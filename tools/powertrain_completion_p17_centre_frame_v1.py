"""Original centre-stand main welded frame from attributed physical front view."""
import bpy,bmesh,math,json,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='centre-stand-main-frame-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P17','component_id':'MOTO-CENTRE-STAND-MAIN-FRAME-001','source':'creative/research/powertrain-completion-p17-v1/centre-frame-plan-v3.json','height_m':.29,'height_range_m':[.25,.34],'foot_span_m':.30,'leg_OD_m':.022,'pivot_width_m':.085,'pivot_OD_m':.024,'pivot_ID_m':.014,'web_thickness_m':.003,'web_hole_diameter_m':.012,'crossbar_OD_m':.018,'all_dimensions_estimated':True,'camera_calibrated':False,'axes':'X projected lateral, Y up in reference view, Z depth; not installed coordinates','scope':'Centre-stand structural frame only: distinct splayed legs, open transverse pivot tube, pierced upper web, lower crossbar and unequal terminal foot plates, integrated welded-envelope representation. Out-of-plane profile, hidden tube interiors/weld beads, left operating arm/gusset, spring/stops/pivot shaft and installed deployment/ground contact excluded.','material':{'name':'Proposed clean black stand coating','base_color_linear':[.012,.014,.017,1],'metallic':.15,'roughness':.32},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
def cyl_between(a,b,r):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);return o
ob=cyl_between((-.0425,.29,0),(.0425,.29,0),.012);ob.name='CENTRE_STAND_MAIN_FRAME_OPEN_PIVOT_PIERCED_WEB'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);ob.data.name=ob.name
def boolean(cut,op,label):
 bm=bmesh.new();bm.from_mesh(cut.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cut.data);bm.free();bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new(label,'BOOLEAN');m.operation=op;m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
legs=[((-.014,.286,0),(-.135,.007,0)),((.014,.286,0),(.165,.007,0))]
P['leg_endpoints_m']=legs
for i,(a,b) in enumerate(legs):boolean(cyl_between(a,b,.011),'UNION','Independent splayed leg '+str(i))
# Crossbar endpoints lie inside the two leg envelopes at the working height.
bar_y=.179
def at_y(a,b,y):t=(y-a[1])/(b[1]-a[1]);return a[0]+t*(b[0]-a[0])
bar_x=[at_y(a,b,bar_y)for a,b in legs]
boolean(cyl_between((bar_x[0]-.002,bar_y,0),(bar_x[1]+.002,bar_y,0),.009),'UNION','Lower transverse crossbar')
# Upper trapezoidal web, independently visible above the rectangular opening.
poly=[(-.043,.223),(.049,.223),(.009,.280),(-.010,.280)];n=len(poly)
V=[(x,y,z)for z in [-.0015,.0015]for x,y in poly];F=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
boolean(mesh_object('Upper web union construction',V,F),'UNION','Pierced upper welded web envelope')
# Separate asymmetrical projected terminal feet with rounded ends and finite thickness.
for side,cx,width in [('left',-.135,.046),('right',.171,.061)]:
 poly=[]
 for x,z,start in [(cx+width/2-.008,.008,0),(cx-width/2+.008,.008,90),(cx-width/2+.008,-.008,180),(cx+width/2-.008,-.008,270)]:
  for j in range(17):a=math.radians(start+j*90/16);poly.append((x+.008*math.cos(a),z+.008*math.sin(a)))
 n=len(poly);V=[(x,y,z)for y in [-.004,.004]for x,z in poly];F=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
 boolean(mesh_object('Foot union '+side,V,F),'UNION','Unequal terminal plate '+side)
boolean(cyl_between((-.08,.29,0),(.08,.29,0),.007),'DIFFERENCE','Open axial pivot bore')
boolean(cyl_between((.002,.246,-.030),(.002,.246,.030),.006),'DIFFERENCE','Visible round upper web opening')
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:f.smooth=not(abs(f.normal.z)>.99 or abs(f.normal.x)>.999 or abs(f.normal.y)>.999)
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(35))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');finish_source(H,O,P)
