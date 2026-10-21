"""Original finite annular curved connector below inlet; function remains unassigned."""
import bpy,bmesh,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='carburettor-curved-connector-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
P=dict(schema=1,package='P19',component_id='MOTO-CARBURETTOR-CURVED-CONNECTOR-001',source='creative/research/powertrain-completion-p19-v1/curved-connector-plan-v7.json',tube_outer_diameter_m=.0055,tube_inner_diameter_m=.0032,bend_radius_m=.012,straight_lengths_m=[.006,.012],developed_length_m=.006+math.pi*.012/2+.012,collar_outer_diameter_m=.008,angular_samples=96,all_dimensions_estimated=True,scope='Separate bright curved small connector below inlet. Hollow finite annular wall, real open mouths and simple softened terminal collar. Function, hidden routing, pressed/threaded engagement and installed axes unqualified; retained top cable elbow untouched.',material=dict(name='Proposed bright plain connector metal',base_color_linear=[.32,.34,.36,1],metallic=.8,roughness=.27),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
# Cross sections with explicit tangents, smooth quarter-circle and terminal collar.
sections=[]
for i in range(13):sections.append((Vector((-.006*i/12,0,0)),Vector((-1,0,0)),.00275))
for i in range(1,81):
 a=math.pi*.5*i/80;sections.append((Vector((-.006-.012*math.sin(a),0,-.012+.012*math.cos(a))),Vector((-math.cos(a),0,-math.sin(a))),.00275))
for i in range(1,33):
 t=.012*i/32;z=-.012-t;u=max(0,min(1,(t-.008)/.0015));u=u*u*(3-2*u);rr=.00275+.00125*u
 if t>.0117:rr-=.00015*((t-.0117)/.0003)**2
 sections.append((Vector((-.018,0,z)),Vector((0,0,-1)),rr))
V=[];F=[];N=P['angular_samples'];L=len(sections)
for inner in [False,True]:
 for c,t,r in sections:
  n=t.cross(Vector((0,1,0))).normalized();r=.0016 if inner else r
  for j in range(N):
   a=math.tau*j/N;V.append(tuple(c+r*(math.cos(a)*Vector((0,1,0))+math.sin(a)*n)))
for side in range(2):
 for i in range(L-1):
  a=(side*L+i)*N;b=a+N
  for j in range(N):k=(j+1)%N;F.append((a+j,a+k,b+k,b+j))
for i in [0,L-1]:
 a=i*N;b=(L+i)*N
 for j in range(N):k=(j+1)%N;F.append((a+j,b+j,b+k,a+k))
ob=mesh_object('CURVED_LOWER_CONNECTOR_FINITE_ANNULAR_WALL_AND_COLLAR',V,F)
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob['scope']=P['scope'];finish_source(H,O,P)
