"""P16 distinct passenger metal peg: shaped pierced root, distal flange and long stop tab."""
import bpy,sys,json,math,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='passenger-footpeg-metal-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True)
sections=[[.004,.0095,.0035],[.012,.0095,.004],[.018,.0095,.006],[.022,.0095,.0085],[.026,.0095,.0095],[.099,.0095,.0095],[.100,.0095,.0095],[.100,.0138,.0138],[.1005,.0145,.0145],[.1035,.0145,.0145],[.104,.0138,.0138]]
P={'schema':1,'package':'P16','component_id':'MOTO-PASSENGER-FOOTPEG-METAL-001','source':'creative/research/powertrain-completion-p16-v1/passenger-metal-supplement-v3.json','sections_x_ry_rz_m':sections,'length_range_m':[.085,.125],'body_diameter_range_m':[.016,.024],'flange_diameter_range_m':[.024,.035],'root_end_x_tilt_m':.004,'root_thickness_range_m':[.0045,.009],'hole_x_m':.012,'hole_radius_m':.004,'hole_diameter_range_m':[.006,.010],'stop_tab_x_range_m':[.071,.100],'stop_tab_height_z_m':.012,'stop_tab_width_m':.003,'tab_height_above_body_range_m':[.0015,.005],'tab_width_range_m':[.002,.0045],'angular_samples':192,'all_dimensions_estimated':True,'scope':'Physical DP161170 exterior interpretation: flattened oblique pierced root, round body, distal flange and elongated upper stop tab. Core is a solid exterior envelope, not a measured hidden tube/channel section. Backside, weld/casting process, hinge axis/stop engagement, rubber retention and installed fold fit unqualified. Existing rider supports unchanged.','material':{'name':'Proposed coated passenger peg metal','base_color_linear':[.016,.018,.021,1],'metallic':.3,'roughness':.34},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);N=192;V=[];F=[]
for k,(x,ry,rz)in enumerate(sections):
 for i in range(N):a=i*math.tau/N;y=ry*math.cos(a);z=rz*math.sin(a);xx=x-.004*y/.0095 if k==0 else x;V.append((xx,y,z))
for k in range(len(sections)-1):
 a=k*N;b=a+N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
F.append(tuple(reversed(range(N))));F.append(tuple((len(sections)-1)*N+i for i in range(N)));ob=mesh_object('PASSENGER_PEG_SHAPED_ROOT_FLANGE_AND_STOP_TAB',V,F)
def apply(tool,op):
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Visible peg feature '+op,'BOOLEAN');mod.operation=op;mod.solver='EXACT';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
outline=[(.071,.007),(.074,.012),(.101,.012),(.101,.007)];verts=[(x,y,z)for y in [-.0015,.0015]for x,z in outline];faces=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4)for i in range(4)];tab=mesh_object('Stop tab construction',verts,faces);bm=bmesh.new();bm.from_mesh(tab.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(tab.data);bm.free();apply(tab,'UNION')
bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=.004,depth=.040,location=(.012,0,0),rotation=(0,0,.007));apply(bpy.context.object,'DIFFERENCE')
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:f.smooth=abs(f.normal.x)<.85 and not(abs(f.normal.y)>.999 or abs(f.normal.z)>.999)
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(35))
bm.to_mesh(ob.data);bm.free();ob.data.update();
from collections import Counter
cnt=Counter(tuple(sorted((a,b)))for f in ob.data.polygons for a,b in zip(list(f.vertices),list(f.vertices[1:])+[f.vertices[0]]));print('ACTUAL_EDGE_COUNTS',dict(Counter(cnt.values())))
ob['scope']=P['scope'];finish_source(H,O,P)
