"""Corrective original inboard ear/root revision from four NEW opposed/inside physical views."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_loft_v4 import recalc,clean_smooth
R=Path(__file__).resolve().parents[1];name='chaincase-front-ear-root-v2';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
controls=[[-.011,.032],[.011,.032],[.011,.025],[.008,.018],[.0075,.010],[.008,.004],[.0085,0],[.00785,-.00325],[.006,-.006],[.00325,-.00785],[0,-.0085],[-.00325,-.00785],[-.006,-.006],[-.00785,-.00325],[-.0085,0],[-.008,.004],[-.0075,.010],[-.008,.018],[-.011,.025]]
P=dict(schema=1,package='P26',component_id='MOTO-CHAINCASE-FRONT-EAR-ROOT-002',source='creative/research/powertrain-completion-p26-v1/front-ear-root-plan-v74.json',outline_control_m=controls,sheet_normal_thickness_m=.0012,bore_radius_m=.0035,root_out_of_plane_offset_m=.009,root_transition_y_m=[.007,.026],all_dimensions_estimated=True,camera_calibrated=False,axis_certified=False,supersedes_for_review='chaincase-front-ear-study-v1 ALTERNATIVE ONLY, not second physical ear',scope='Corrective compact inboard ear/lobe and continuous formed root from four new used-BM150 physical poses, plain real through-hole and finite normal thickness. Removes old wide-flare/raised-seat interpretation. Upper root edge is explicit parent-interface review cut: actual weld/contact/three-wall-axis registration/currentRDC fit unqualified. Historical shell/known3wall holes and frozen v1 remain untouched; do not mount both revisions.',material=dict(name='Proposed clean silver painted inboard ear root',base_color_linear=[.43,.45,.47,1],metallic=0,roughness=.32),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);cs=list(map(Vector,controls));curve=[]
for i in range(len(cs)):
 p=[cs[(i+j)%len(cs)]for j in range(4)]
 for k in range(24):
  t=k/24;w=[(1-t)**3/6,(3*t**3-6*t*t+4)/6,(-3*t**3+3*t*t+3*t+1)/6,t**3/6];curve.append(sum((a*b for a,b in zip(p,w)),Vector((0,0))))
def cross(a,b):return a.x*b.y-a.y*b.x
N=256;M=64;radii=[]
for i in range(N):
 d=Vector((math.cos(math.tau*i/N),math.sin(math.tau*i/N)));hits=[]
 for a,b in zip(curve,curve[1:]+curve[:1]):
  e=b-a;den=cross(d,e)
  if abs(den)<1e-14:continue
  t=cross(a,e)/den;u=cross(a,d)/den
  if t>0 and -1e-8<=u<=1+1e-8:hits.append(t)
 hits=sorted(set(round(x,12)for x in hits)) # Coincident hits on a shared polygon vertex are one crossing.
 assert len(hits)==1,(i,hits);radii.append(hits[0])
assert min(radii)>.006

def height(y):
 t=max(0,min(1,(y-.007)/.019));f=t*t*t*(10+t*(-15+6*t));dy=.009*30*t*t*(1-t)*(1-t)/.019 if 0<t<1 else 0
 return .009*f,Vector((0,-dy,1)).normalized()
V=[];F=[]
for side in [1,-1]:
 for k in range(M+1):
  t=k/M
  for i,outer in enumerate(radii):
   a=math.tau*i/N;r=.0035*(1-t)+outer*t;x,y=r*math.cos(a),r*math.sin(a);z,n=height(y);V.append(tuple(Vector((x,y,z))+n*(side*.0006)))
S=(M+1)*N
for k in range(M):
 a=k*N;b=a+N
 for i in range(N):
  j=(i+1)%N;F.extend([(a+i,b+i,b+j,a+j),(S+a+i,S+a+j,S+b+j,S+b+i)])
for i in range(N):
 j=(i+1)%N;a=M*N;F.extend([(a+i,S+a+i,S+a+j,a+j),(i,j,S+j,S+i)])
ob=mesh_object('COMPACT_INBOARD_EAR_PLAIN_BORE_CONTINUOUS_FORMED_ROOT',V,F);recalc(ob);clean_smooth(ob)
# Parallel normal offsets preserve the analytic normal of z=f(y), prior to triangles.
# Skin normals derive from f'(y), not arbitrary imported GLB normal repair.
source_map={}
for side_index,side in enumerate([1,-1]):
 for k in range(M+1):
  for i,outer in enumerate(radii):
   idx=side_index*S+k*N+i;angle=math.tau*i/N;r=.0035*(1-k/M)+outer*k/M;y=r*math.sin(angle);_,n=height(y)
   source_map[tuple(round(float(x),8)for x in Vector(V[idx]))]=(side_index,k,i,n)
corner_normals=[];skin_faces=wall_faces=0;minimum_dot=1.0
for f in ob.data.polygons:
 rows=[source_map[tuple(round(float(x),8)for x in ob.data.vertices[v].co)]for v in f.vertices]
 skin=len(set(row[0]for row in rows))==1
 if skin:skin_faces+=1
 else:wall_faces+=1
 for vi,row in zip(f.vertices,rows):
  si,k,i,n=row
  if skin:n=n*(1 if si==0 else -1)
  else:
   assert k in [0,M];prev=Vector(V[si*S+k*N+(i-1)%N]);nxt=Vector(V[si*S+k*N+(i+1)%N]);tangent=nxt-prev;n=tangent.cross(n).normalized()*(1 if k==M else -1)
  minimum_dot=min(minimum_dot,n.dot(f.normal));assert n.dot(f.normal)>0,'Derived surface normal must agree with actual triangle orientation'
  corner_normals.append(tuple(n))
ob.data.normals_split_custom_set(corner_normals);ob.data.update()
(O/'analytic-source-normal-check.json').write_text(json.dumps(dict(method='Analytic normals of original z=f(y) parallel-offset skins; ruled perimeter derivative crossed with skin normal, inward on bore and outward on perimeter',skin_faces=skin_faces,wall_faces=wall_faces,min_actual_face_corner_dot=minimum_dot,glb_normal_buffer_repair=False,geometry_modified_for_normals=False,scope='Source differential normals; actual independent GLB face/corner agreement remains required, no physical pressing/fit claim'),indent=2)+'\n')
ob['scope']=P['scope'];finish_source(H,O,P)
(O/'root-construction-check.json').write_text(json.dumps(dict(outline_method='Original periodic cubic B-spline; unique uniform-angle ray intersections prevent folded radial cells',angular_samples=N,radial_samples=M,minimum_outer_radius_m=min(radii),root_height_method='Analytic quintic C2 transition, zero first/second derivatives at both joins',normal_offset_each_side_m=.0006,scope='Constructed envelope continuity only, not real pressing/weld/metric fit',art_accepted=False),indent=2)+'\n')
