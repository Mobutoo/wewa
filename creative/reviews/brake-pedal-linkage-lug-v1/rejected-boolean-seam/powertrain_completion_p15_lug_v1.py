"""Photo-informed mid-arm pierced lug; no root weld or pin fit invention."""
import bpy,sys,json,math,bmesh
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='brake-pedal-linkage-lug-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True)
outline=[[-.011,.013],[.011,.013],[.009,-.014],[-.009,-.014]]
P={'schema':1,'package':'P15','component_id':'MOTO-BRAKE-PEDAL-LINKAGE-LUG-001','source':'creative/research/powertrain-completion-p15-v1/linkage-lug-child-plan-v3.json','outline_xy_m':outline,'outline_corner_radius_m':.001,'width_range_m':[.017,.027],'height_range_m':[.020,.034],'sheet_thickness_m':.003,'thickness_range_m':[.002,.0045],'hole_center_xy_m':[0,-.005],'hole_diameter_m':.009,'hole_range_m':[.007,.011],'edge_bevel_m':.00025,'bevel_range_m':[.0001,.0005],'all_dimensions_estimated':True,'scope':'Photo-observed tapered flat mid-arm lug, real single through-hole, bounded rounded corners/edges. Root weld, opposite face details, actual offset and pin/rod fit unqualified. Separate unplaced child; prior arm and sleeve immutable.','material':{'name':'Proposed coated linkage lug','base_color_linear':[.013,.015,.018,1],'metallic':.15,'roughness':.30},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);pts=[Vector(p)for p in outline];curve=[]
for i,b in enumerate(pts):
 a,c=pts[(i-1)%len(pts)],pts[(i+1)%len(pts)];q=.001;u=b+(a-b).normalized()*q;v=b+(c-b).normalized()*q
 for j in range(12):t=j/12;curve.append((1-t)**2*u+2*(1-t)*t*b+t*t*v)
N=len(curve);V=[(p.x,p.y,z)for z in [-.0015,.0015]for p in curve];F=[tuple(reversed(range(N))),tuple(N+i for i in range(N))]
for i in range(N):j=(i+1)%N;F.append((i,j,N+j,N+i))
ob=mesh_object('BRAKE_PEDAL_TAPERED_SINGLE_HOLE_LINKAGE_LUG',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=.0045,depth=.020,location=(0,-.005,0));tool=bpy.context.object;bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Actual single through-hole','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
mod=ob.modifiers.new('Bounded edge roll','BEVEL');mod.width=.00025;mod.segments=4;mod.limit_method='ANGLE';mod.angle_limit=math.radians(35);bpy.ops.object.modifier_apply(modifier=mod.name)
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:f.smooth=abs(f.normal.z)<.999
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(35))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];finish_source(H,O,P)
