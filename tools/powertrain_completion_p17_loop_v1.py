"""P17 open deployment rod following observed unequal bends; foot supplies fourth side."""
import bpy,sys,json,math,bmesh
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='side-stand-deployment-rod-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True)
controls=[[.200,.010,0],[.230,.085,0],[.245,.090,0],[.287,.061,0]]
P={'schema':1,'package':'P17','component_id':'MOTO-SIDE-STAND-DEPLOYMENT-ROD-001','source':'creative/research/powertrain-completion-p17-v1/deployment-loop-plan-v2.json','centerline_controls_m':controls,'position_range_each_axis_m':.015,'rod_radius_m':.0035,'radius_range_m':[.0025,.0045],'corner_setback_m':.010,'setback_range_m':[.006,.016],'corner_samples':24,'section_samples':64,'all_dimensions_estimated':True,'scope':'Open unequal-segment bent deployment rod from visible physical side stand. Foot supplies fourth side, not a standalone closed rectangle. Planar pose and capped interface ends estimated; welds/out-of-plane bend/foot contacts/installed clearance unqualified. Prior fork/stem unchanged.','material':{'name':'Proposed black stand coating','base_color_linear':[.012,.014,.017,1],'metallic':.15,'roughness':.32},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);pts=[Vector(p)for p in controls];path=[pts[0]]
for i in range(1,len(pts)-1):
 a,b,c=pts[i-1:i+2];q=min(.010,(b-a).length*.3,(c-b).length*.3);u=b+(a-b).normalized()*q;v=b+(c-b).normalized()*q
 path.append(u)
 for j in range(1,25):t=j/24;path.append((1-t)**2*u+2*(1-t)*t*b+t*t*v)
path.append(pts[-1]);V=[];F=[];N=64
for k,p in enumerate(path):
 tangent=(path[min(k+1,len(path)-1)]-path[max(k-1,0)]).normalized();normal=Vector((-tangent.y,tangent.x,0)).normalized();binormal=Vector((0,0,1))
 for i in range(N):a=i*math.tau/N;V.append(tuple(p+.0035*(math.cos(a)*normal+math.sin(a)*binormal)))
for k in range(len(path)-1):
 a=k*N;b=a+N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
F.append(tuple(reversed(range(N))));F.append(tuple((len(path)-1)*N+i for i in range(N)))
ob=mesh_object('SIDE_STAND_OPEN_UNEQUAL_BENT_DEPLOYMENT_ROD',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:
 if len(f.verts)>4:f.smooth=False
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(40))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];finish_source(H,O,P)
