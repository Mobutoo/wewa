"""NEW DS151068 reverse exterior sub-study only. Existing front gray/material and G4 hold untouched."""
import bpy,math,json,runpy
from pathlib import Path
from math import sin,cos,pi,sqrt
R=Path('/workspace/wewa');K='front-completion-p21-reverse-front10-v4';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(parents=True,exist_ok=False);O.mkdir(parents=True,exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True)
U=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));globals().update({k:v for k,v in U.items()if not k.startswith('__')})
P=json.loads((R/'creative/research/front-completion-p21-opposite-v2/G0-G2-next-revision.json').read_text());P.update({'scope':'Independent photographed rear exterior, not a remake/replacement of front gray v3','frame':'Z up out of photographed rear; not installed or aligned to existing front frame','front_review_closure':'Artificial plain finite annular sheet atZ=-3mm; not a reconstructed front face, OEM wall or certified mounted section','bore':'Open central diameter37mm estimate; plain inner review continuation, not a bearing seat specification','witness_marks':'Rear round witnesses/lettering not interpreted as screws, caps or certified part stamps; excluded','finish':'Clean uniform silver hypothesis only; no cast grain or alloy measurement','all_metric_values_estimated':True});
for inherited in ['future_revision','status','geometry_method','material_rework_method']:P.pop(inherited,None)
P['inherited_bounds_source']='creative/research/front-completion-p21-opposite-v2/G0-G2-next-revision.json'
(H/'parameters.json').write_text(json.dumps(P,indent=2))
N=768;NR=241;v=[];f=[]
def height(r,a):
 # Rear stepped collar and outer circular bead independently constrained only as exterior.
 if r<=.0205:collar=.012
 elif r<.021:collar=.012+.003*smooth((r-.0205)/.0005)
 elif r<=.024:collar=.015
 else:collar=.015*(1-smooth((r-.024)/.0025))
 pad=0
 for t in [pi/4,3*pi/4,5*pi/4,7*pi/4]:
  x=r*cos(a-t);y=r*sin(a-t);dist=sqrt((x-min(.054,max(.036,x)))**2+y*y)-.0055;mask=1-smooth((dist+.0015)/.003);pad=max(pad,.020*mask)
 rim=.0025*smooth((r-.0615)/.0015)*(1-.25*smooth((r-.064)/.001))
 return max(collar,pad,rim)
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
points=[];constraints=[]
def add_loop(cx,cy,r,n):
 first=len(points)
 for j in range(n):
  a=2*pi*(j+.173)/n;points.append(Vector((cx+r*cos(a),cy+r*sin(a))))
 for j in range(n):constraints.append((first+j,first+(j+1)%n))
add_loop(0,0,.065,N);add_loop(0,0,.0185,N)
mouths=[(.047*cos(a),.047*sin(a))for a in [0,pi/2,pi,3*pi/2]]
for cx,cy in mouths:add_loop(cx,cy,.0035,128)
for i in range(1,NR-1):
 r=.0185+(.065-.0185)*i/(NR-1)
 for j in range(N):
  a=2*pi*(j+.173)/N;x=r*cos(a);y=r*sin(a)
  if all(math.hypot(x-cx,y-cy)>.00354 for cx,cy in mouths):points.append(Vector((x,y)))
verts2,edges2,faces2,*_ = delaunay_2d_cdt(points,constraints,[],0,1e-9)
used=[]
for face in faces2:
 cx=sum(verts2[j].x for j in face)/len(face);cy=sum(verts2[j].y for j in face)/len(face);r=math.hypot(cx,cy)
 if r>.0185 and r<.065 and all(math.hypot(cx-x,cy-y)>.0035 for x,y in mouths):used.append(tuple(face))
# Compact only vertices used by the constrained top domain. The identical topology on the
# artificial review back and explicit boundary walls avoids four fragile CSG cuts.
ids=sorted({i for face in used for i in face});remap={old:new for new,old in enumerate(ids)};xy=[verts2[i]for i in ids];top=[tuple(remap[i]for i in face)for face in used];L=len(xy)
v=[(p.x,p.y,height(math.hypot(p.x,p.y),math.atan2(p.y,p.x)))for p in xy]+[(p.x,p.y,-.003)for p in xy];f=list(top)+[tuple(i+L for i in face[::-1])for face in top]
counts={};oriented={}
for face in top:
 for a,b in zip(face,face[1:]+face[:1]):
  edge=tuple(sorted((a,b)));counts[edge]=counts.get(edge,0)+1;oriented[edge]=(a,b)
for edge,count in counts.items():
 assert count in (1,2)
 if count==1:
  a,b=oriented[edge];f.append((a,b,b+L,a+L))
ob=mesh_object('DS151068_REVERSE_ONLY_CONSTRAINED_HOLES_PADS_COLLAR',v,f)
(O/'construction-method.json').write_text(json.dumps({'method':'Original constrained2D Delaunay with exterior, central bore and4 mouth loops; form from sampled height field; identical finite review back and explicit boundary walls','input_points':len(points),'used_vertices_per_side':L,'top_triangles':len(top),'boundary_edges_before_walls':sum(c==1 for c in counts.values()),'no_CSG_hole_repair':True,'review_back_not_actual_front':True},indent=2))
report=clean_audit(ob)
# Normals derived from the ORIGINAL continuous height field, not geometric/buffer repair.
# The generic angle threshold incorrectly made a jagged sharp seam at sampled pad shoulders.
m=ob.data;normals=[]
for e in m.edges:e.use_edge_sharp=False
for face in m.polygons:
 coords=[m.vertices[i].co for i in face.vertices]
 is_top=all(v.z>=-1e-8 for v in coords);is_back=all(abs(v.z+.003)<1e-8 for v in coords)
 for li in face.loop_indices:
  v=m.vertices[m.loops[li].vertex_index].co;x,y=v.x,v.y
  if is_top:
   eps=1e-6
   def field(xx,yy):return height(math.hypot(xx,yy),math.atan2(yy,xx))
   gx=(field(x+eps,y)-field(x-eps,y))/(2*eps);gy=(field(x,y+eps)-field(x,y-eps))/(2*eps);n=Vector((-gx,-gy,1)).normalized()
  elif is_back:n=Vector((0,0,-1))
  else:
   r=math.hypot(x,y)
   if r>.0649:n=Vector((x/r,y/r,0))
   elif r<.0186:n=Vector((-x/r,-y/r,0))
   else:
    cx,cy=min(mouths,key=lambda c:math.hypot(x-c[0],y-c[1]));n=Vector((cx-x,cy-y,0)).normalized()
  normals.append(tuple(n))
 for p in [face]:p.use_smooth=True
m.normals_split_custom_set(normals);m.update()
(O/'source-normal-method.json').write_text(json.dumps({'method':'Original continuous height-field central derivative1um for top, analytic radial outward/inward wall normals and plain back -Z; source corner normals only, no GLB buffer edits','geometry_method_unchanged_from_v3':True,'reason':'Unwanted generic40deg sharp-edge assignment produced staircase highlights at pad top shoulder','corner_normals':len(normals)},indent=2))
gray_save(H,'carrier-reverse',[ob]);(O/'geometry-check.json').write_text(json.dumps({'objects':[report],'four_observed_rear_mouths':True,'four_observed_drive_pad_envelopes':True,'plain_front_review_closure_only':True,'current_RDC_identity':False,'mounted_fit':False,'all_metric_values_estimated':True},indent=2));print(report)
