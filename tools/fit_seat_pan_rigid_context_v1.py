"""Read actual seat envelope and test bounded rigid/uniform-scale placement of an unreceived partial pan."""
import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'creative/research/seat-pan-context-correction-v1';O.mkdir(parents=True,exist_ok=True);dg=bpy.context.evaluated_depsgraph_get()
def evaluated(key):
 inst=bpy.data.objects['COVERAGE_PARENT ['+key+']'];ob=next(o for o in inst.instance_collection.all_objects if o.type=='MESH');ev=ob.evaluated_get(dg);me=ev.to_mesh();V=[inst.matrix_world@ob.matrix_world@v.co for v in me.vertices];F=[list(p.vertices)for p in me.polygons];ev.to_mesh_clear();return inst,ob,V,F
seat,ob,sv,sf=evaluated('seat-envelope');tree=BVHTree.FromPolygons(sv,sf,all_triangles=False);inst,ob,pv,pf=evaluated('WEWA_SEAT_BASE_OBSERVED_UNDERSIDE_V2');ev=ob.evaluated_get(dg);me=ev.to_mesh();verts=[ob.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();nx=240;ny=600;samples=[verts[j*(nx+1)+i]for j in range(0,ny+1,30)for i in [0,60,120,180,240]]
read=[]
for y in [.34,.36,.4,.5,.6,.7,.8,.9,1.,1.03,1.05]:
 points=[]
 for x in [0,.06,.10,.12,.135]:
  hit=tree.ray_cast(Vector((x,y,-1)),Vector((0,0,1)),2)[0];points.append(dict(x=x,lower_z=hit.z if hit else None))
 read.append(dict(y=y,probes=points))
trials=[]
for scale in [1,.98,.95,.92,.9,.88]:
 for cy in [.64,.65,.66,.67,.68,.69,.7]:
  for deg in [-5,0,3,6,9,12,15]:
   A=Matrix.Rotation(math.radians(deg),4,'X')@Matrix.Rotation(math.pi,4,'Y')@Matrix.Scale(scale,4);pts=[A@v for v in samples];diff=[];outside=0
   for v in pts:
    h=tree.ray_cast(Vector((v.x,v.y+cy,-1)),Vector((0,0,1)),2)[0]
    if h is None:outside+=1
    else:diff.append(h.z-v.z)
   if not diff:continue
   z=float(np.percentile(diff,10)-.002);errors=np.array(diff)-z;score=outside*.01+float(np.mean(np.minimum(errors,0)**2)*100)+float(np.mean(np.maximum(errors-.018,0)**2)*10)
   trials.append(dict(scale=scale,translation=[0,cy,z],rotation_x_degrees=deg,outside_samples=outside,tested_samples=len(samples),gap_min=float(min(errors)),gap_max=float(max(errors)),gap_mean=float(np.mean(errors)),score=score))
trials.sort(key=lambda v:v['score']);(O/'seat-envelope-probes-and-pan-trials.json').write_text(json.dumps(dict(scope='Actual source envelope rays and estimated partial pan fitting trials; no source deformation or artistic/physical receipt; negative gaps mean intersection, missing rays mean outside footprint',source_pan_shape_unchanged=True,source_pan_scale_bounds='Exploratory0.88..1.0 uniform estimated scale, not OEM measurements',native_lower_seat_probes=read,candidates=trials[:40]),indent=2)+'\n');print('PAN_TRIAL_BEST',json.dumps(trials[:3]))
