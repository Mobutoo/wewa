"""Two-way old/new retained-surface distance and bounding/volume evidence; no mesh mutation."""
from pathlib import Path
import bpy,json,hashlib,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/front-footrest-left-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=H/'diagnostics/native-normalmap-refusal/front-footrest-left-v1-geometry.blend';new=H/'front-footrest-left-v1-geometry.blend';name='PF113000 related metal support - isolated candidate'
def read(p):
 bpy.ops.wm.open_mainfile(filepath=str(p));o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles();verts=[o.matrix_world@v.co for v in m.vertices];faces=[tuple(t.vertices)for t in m.loop_triangles];triangles=[[verts[i]for i in t]for t in faces];area=sum((b-a).cross(c-a).length*.5 for a,b,c in triangles);volume=sum(a.dot(b.cross(c))/6 for a,b,c in triangles);bbox=[[min(v[k]for v in verts),max(v[k]for v in verts)]for k in range(3)];return {'vertices':verts,'faces':faces,'area':area,'volume':volume,'bbox':bbox,'triangle_centres':[tuple((float(a[k])+float(b[k])+float(c[k]))/3 for k in range(3))for a,b,c in triangles]}
a=read(old);b=read(new)
def tree(q):return BVHTree.FromPolygons(q['vertices'],q['faces'],all_triangles=True)
ta=tree(a);tb=tree(b)
native_new_old=max(ta.find_nearest(v)[3]for v in b['vertices']+b['triangle_centres']);native_old_new=max(tb.find_nearest(v)[3]for v in a['vertices']+a['triangle_centres'])
def double_upper_bound(target,query):
 verts=np.asarray(target['vertices'],dtype=np.float64);tris=np.asarray(target['faces']);kd=KDTree(len(verts));incident=[[]for _ in verts]
 for i,v in enumerate(verts):kd.insert(Vector(v),i)
 kd.balance();centres=verts[tris].mean(axis=1);ckd=KDTree(len(centres))
 for j,v in enumerate(centres):ckd.insert(Vector(v),j)
 ckd.balance();bvh=tree(target)
 for j,t in enumerate(tris):
  for i in t:incident[int(i)].append(j)
 maxvertex=0;maxcentre=0;max_nearestvertex=0
 for kind,points in [('vertex',query['vertices']),('centre',query['triangle_centres'])]:
  for point in points:
   Q=np.asarray(point,dtype=np.float64);co,vi,d=kd.find(Vector(point));vd=float(np.linalg.norm(Q-verts[vi]))
   if kind=='vertex':max_nearestvertex=max(max_nearestvertex,vd)
   co,ci,d=ckd.find(Vector(point));cd=float(np.linalg.norm(Q-centres[ci]));upper=min(vd,cd)
   if upper>1.1e-7:
    inds={ci};nearest=bvh.find_nearest(Vector(point))
    if nearest[2]is not None:inds.add(nearest[2])
    for co,i,d in kd.find_n(Vector(point),3):inds.update(incident[i])
    t=verts[tris[list(inds)]];A=t[:,0];B=t[:,1];C=t[:,2];N=np.cross(B-A,C-A);N2=np.einsum('ij,ij->i',N,N);valid=N2>0;proj=Q-np.einsum('ij,ij->i',Q-A,N)[:,None]*N/np.where(valid,N2,1)[:,None];inside=valid.copy();best=np.full(len(t),np.inf)
    for E,F in [(A,B),(B,C),(C,A)]:
     delta=F-E;dd=np.einsum('ij,ij->i',delta,delta);u=np.clip(np.einsum('ij,ij->i',Q-E,delta)/np.where(dd>0,dd,1),0,1);near=E+u[:,None]*delta;best=np.minimum(best,np.linalg.norm(Q-near,axis=1));inside&=np.einsum('ij,ij->i',np.cross(delta,proj-E),N)>=0
    best=np.minimum(best,np.where(inside,np.linalg.norm(Q-proj,axis=1),np.inf));upper=min(upper,float(best.min()))
   if kind=='vertex':maxvertex=max(maxvertex,upper)
   else:maxcentre=max(maxcentre,upper)
 return maxvertex,maxcentre,max_nearestvertex
newvertex, newcentre,new_vertex_to_vertex=double_upper_bound(a,b);oldvertex,oldcentre,old_vertex_to_vertex=double_upper_bound(b,a);max_new_old=max(newvertex,newcentre);max_old_new=max(oldvertex,oldcentre);max_newvertex_oldvertex=new_vertex_to_vertex;vol=abs(b['volume']/a['volume']-1);area=abs(b['area']/a['area']-1);bbox=max(abs(a['bbox'][i][j]-b['bbox'][i][j])for i in range(3)for j in range(2));print('CLEANUP_FLOAT64',max_new_old,max_old_new,vol,area,bbox,flush=True);assert max(max_new_old,max_old_new)<=1.1e-7 and vol<1e-5 and area<1e-5 and bbox<=1.1e-7
x={'component_id':'MOTO-FRONT-FOOTREST-LEFT-001','source_sha256':sha(new),'old_geometry_source_sha256':sha(old),'old_vertices':len(a['vertices']),'new_vertices':len(b['vertices']),'old_triangles':len(a['faces']),'new_triangles':len(b['faces']),'max_new_vertex_to_old_vertex_m':max_newvertex_oldvertex,'max_new_vertex_or_triangle_centre_to_old_surface_m':max_new_old,'max_old_vertex_or_triangle_centre_to_new_surface_m':max_old_new,'bbox_max_abs_difference_m':bbox,'volume_relative_difference':vol,'area_relative_difference':area,'native_BVH_nearest_diagnostic_m':{'new_to_old':native_new_old,'old_to_new':native_old_new,'refused_as_surface_proof':True},'float64_method':'Upper bound from actual float64 target triangle centres; unmatched centres checked against candidate triangles from centroid KD/BVH index and three nearest vertices. Found target points supply upper bounds, never global minimum claims. Vertex distances recomputed float64. Native BVH distance values explicitly refused.','scope_of_revision':'Seam cleanup plus redundant coincident bore removed, web hidden overlap trimmed0.2mm into tube wall before union, stable dominant-plane UV orientations. No visible design dimensions changed.','source_cleanup':{'remove_doubles_m':1e-7,'dissolve_degenerate_m':1e-9},'scope':'Source seam weld only, retained positions checked two ways at vertices and actual triangle centroids. Distance bound is sampled, not a Hausdorff supremum. Hard/soft sectors recomputed from source dihedrals; actual reflection review separately required. No exported tangent repair.','art_accepted':False};(O/'cleanup-surface-check.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x))
