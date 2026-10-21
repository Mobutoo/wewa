"""Observed DF191020 continuous formed wire, author depth offsets; no mounting station or route."""
import bpy,math,json,runpy,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');K='front-completion-p03-wire-guide-front12-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));pixels=[(358,280),(480,218),(620,155),(641,143),(646,126),(641,112),(627,101),(611,96),(592,97),(463,156),(351,204),(337,215),(326,232),(326,251),(327,266),(318,281),(300,289),(215,320),(194,333),(184,347),(181,365),(170,373),(132,375),(108,382),(94,394),(95,401),(106,404),(125,403),(149,398),(170,388),(184,385),(197,402),(208,419)];depth=[0]*19+[.001,.002,.004,.004,.004,.003,.001,0,-.001,-.0015,-.002,-.002,-.002,-.002];controls=[Vector(((x-370)*.00024,(270-y)*.00024,z))for (x,y),z in zip(pixels,depth)];path=[]
for k in range(len(controls)-1):
 a,b,c,d=controls[max(0,k-1)],controls[k],controls[k+1],controls[min(len(controls)-1,k+2)]
 for j in range(24):
  t=j/24;q=.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t**3)
  if not path or (q-path[-1]).length>1e-8:path.append(q)
path.append(controls[-1]);radius=.0011
# Constant circular rod swept by parallel transported source frames; true planar free-end caps.
v=[];f=[];sides=32;prev=None;T=[]
for i,p in enumerate(path):
 tangent=(path[min(i+1,len(path)-1)]-path[max(0,i-1)]).normalized();T.append(tangent)
 normal=Vector((0,0,1))if prev is None else prev.copy();normal-=normal.dot(tangent)*tangent
 if normal.length<1e-8:normal=Vector((0,1,0));normal-=normal.dot(tangent)*tangent
 normal.normalize();binormal=tangent.cross(normal).normalized();prev=normal
 for j in range(sides):a=2*math.pi*j/sides;v.append(tuple(p+radius*(math.cos(a)*normal+math.sin(a)*binormal)))
for i in range(len(path)-1):
 for j in range(sides):a=i*sides+j;b=i*sides+(j+1)%sides;f.append((a,b,b+sides,a+sides))
for row,p,rev in [(0,path[0],True),(len(path)-1,path[-1],False)]:
 c=len(v);v.append(tuple(p))
 for j in range(sides):a=row*sides+j;b=row*sides+(j+1)%sides;f.append((c,b,a)if rev else(c,a,b))
ob=u['mesh_object']('DF191020_ONE_CONTINUOUS_FORMED_WIRE_TWO_FREE_ENDS',v,f);audit=u['clean_audit'](ob)
# Read centerline nonlocal spacing, excluding local rod neighbors by arc length.
P=np.array([tuple(p)for p in path]);arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(P,axis=0),axis=1))];minsep=float('inf')
for i in range(len(P)):
 mask=np.abs(arc-arc[i])>radius*math.pi*1.8
 if np.any(mask):minsep=min(minsep,float(np.min(np.linalg.norm(P[mask]-P[i],axis=1))))
(O/'centerline-check.json').write_text(json.dumps({'sampled_points':len(path),'arc_length_m':float(arc[-1]),'nonlocal_center_distance_m':minsep,'local_arc_exclusion_m':radius*math.pi*1.8,'rod_diameter_m':2*radius,'scope':'Sampled nonlocal source centerline only, not swept-surface BVH or mounted functional clearance'},indent=2));assert minsep>2*radius
(H/'parameters.json').write_text(json.dumps({'package':'P03','code':'DF191020','private_source':'front-completion-front12-candidates-v3/DF191020-0.jpg','trace_pixels':pixels,'trace_scale_estimate_m_per_pixel':.00024,'author_depth_offsets_m':depth,'wire_radius_m':radius,'radius_bounds_m':[.0008,.0016],'all_dimensions_estimated':True,'scope':'One continuous formed-wire guide with two visible free-end cuts, large elongated hairpin, offset S bend and small attachment loop. Source depth offsets author estimate; no mounted cable route/station, weld or material treatment claimed.','finish':'Uniform warm metal hypothesis only; not measured zinc/passivation or iridescence'},indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'continuous_source_bodies':1,'visible_free_ends':2,'mounted_fit':False},indent=2));u['gray_save'](H,'wire-guide',[ob]);print(audit,minsep)
