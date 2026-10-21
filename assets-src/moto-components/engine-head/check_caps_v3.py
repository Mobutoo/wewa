"""Read-only current closed-solid interface checks, cap sources/matrices unchanged.
Points are sourcevertices, distances are sampled, never an OEM seal/contact tolerance.
"""
from pathlib import Path
import bpy,json,hashlib,sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-head-v3';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'engine-head-v3.blend';before=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));bpy.data.collections['HEAD_IMMUTABLE_INTERFACE_GUIDES'].hide_viewport=False;bpy.context.view_layer.update();body=next(o for c in bpy.data.collections if c.name=='WEWA_ENGINE_HEAD' and c.library is None for o in c.objects if o.type=='MESH');dg=bpy.context.evaluated_depsgraph_get()
exact_cache={}
def data(obj):
 evaluated=obj.evaluated_get(dg);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();verts=[obj.matrix_world@v.co for v in mesh.vertices];faces=[list(t.vertices)for t in mesh.loop_triangles];evaluated.to_mesh_clear();tree=BVHTree.FromPolygons(verts,faces,all_triangles=True);tri=np.asarray([[list(verts[i])for i in face]for face in faces],dtype=np.float64);exact_cache[id(tree)]=(tri[:,0],tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);return verts,tree
bodyverts,bodytree=data(body);directions=[Vector(a).normalized()for a in[(.8123,.3937,.4301),(-.4351,.7129,.5467),(.3281,-.5263,.7849),(.6173,-.7421,.2597),(-.6237,-.3141,.7159),(.1931,.9257,-.3259),(-.8917,.3811,-.2437),(.5129,.6731,-.5327),(-.2749,-.8653,-.4187)]]
def bounds(verts):return [min(v[i]for v in verts)for i in range(3)],[max(v[i]for v in verts)for i in range(3)]
def rayparity(point,direction,tree):
 origin=point.copy();hits=0;previous=-1.;previousface=None
 for attempt in range(100):
  hit,normal,face,distance=tree.ray_cast(origin,direction,2)
  if hit is None:return hits%2
  t=(hit-point).dot(direction);cosine=abs(normal.dot(direction))
  # Near-tangent or repeated hits are numerical diagnostics, never counted
  # as additional surfaces. Retry a different fixed direction for thispoint.
  if cosine<.001 or (previous>=0 and t-previous<1e-6):return None
  hits+=1;previous=t;previousface=face;step=max(1e-6,1e-7/cosine);origin=point+direction*(t+step)
 return None

def double_ray_parity(point,direction,tree):
 # Direct float64 Moller-Trumbore intersection against all actual triangles.
 # No BVH advancement, sourcepositions unchanged; shared hits deduplicated.
 a,e1,e2=exact_cache[id(tree)];d=np.asarray(direction,dtype=np.float64);p=np.asarray(point,dtype=np.float64);h=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,h);area2=np.linalg.norm(np.cross(e1,e2),axis=1);valid=np.abs(det)>1e-12*area2;inv=np.zeros_like(det);inv[valid]=1/det[valid];delta=p-a;u=inv*np.einsum('ij,ij->i',delta,h);q=np.cross(delta,e1);v=inv*(q@d);t=inv*np.einsum('ij,ij->i',e2,q);hit=valid&(u>=-1e-12)&(v>=-1e-12)&(u+v<=1+1e-12)&(t>1e-9)
 if np.any(hit&((np.minimum(np.minimum(u,v),1-u-v))<1e-10)):return None
 distances=np.sort(t[hit]);count=0;last=-1.
 for value in distances:
  if count==0 or value-last>1e-9:count+=1;last=value
 return count%2

def classify(points,tree,box):
 inside=[];ambiguous=[];boundary=[];skipped=0;retryrays=0;fallback=[]
 for index,p in enumerate(points):
  if any(p[i]<box[0][i]-1e-7 or p[i]>box[1][i]+1e-7 for i in range(3)):skipped+=1;continue
  near=tree.find_nearest(p)[3]
  if near<1e-7:boundary.append(index);continue
  answers=[]
  for direction in directions:
   answer=rayparity(p,direction,tree)
   if answer is None:retryrays+=1;continue
   answers.append(answer)
   if len(answers)==3:break
  if len(answers)!=3 or len(set(answers))!=1:
   previous=answers;answers=[]
   for direction in directions:
    answer=double_ray_parity(p,direction,tree)
    if answer is not None:answers.append(answer)
    if len(answers)==3:break
   fallback.append({'vertex':index,'point_world_m':list(p),'BVH_answers':previous,'direct_float64_answers':answers})
  if len(answers)!=3 or len(set(answers))!=1:ambiguous.append(index)
  elif answers[0]:inside.append(index)
 return {'vertices':len(points),'outside_bounding_box':skipped,'inside_count':len(inside),'ambiguous_count':len(ambiguous),'boundary_below100nm_count':len(boundary),'numerical_rays_retried':retryrays,'first_inside_indices':inside[:8],'direct_float64_fallbacks':fallback}
rows=[]
for name,collection in [('visit','WEWA_ENGINE_TAPPET_CAP'),('OHC','WEWA_ENGINE_OHC_COVER_BODY')]:
 coll=next(c for c in bpy.data.collections if c.name==collection)
 for obj in list(coll.all_objects):
  if obj.type!='MESH':continue
  verts,tree=data(obj);a=classify(verts,bodytree,bounds(bodyverts));b=classify(bodyverts,tree,bounds(verts));cross=len(bodytree.overlap(tree));row={'group':name,'object':obj.name,'surface_triangle_pairs':cross,'cap_vertices_against_head_solid':a,'head_vertices_against_cap_solid':b,'sampled_cap_vertex_to_head_surface_minimum_m':min(bodytree.find_nearest(v)[3]for v in verts),'cap_matrix_world':[list(x)for x in obj.matrix_world]};assert cross==0 and all(r[k]==0 for r in [a,b]for k in ['inside_count','ambiguous_count','boundary_below100nm_count']),row;rows.append(row)
assert sha(src)==before;report={'source_sha256':before,'immutable_caps':json.loads((H/'build-report-v3.json').read_text())['immutable_cap_sources'],'checks':rows,'scope':'Actual candidate closed-source surfaces and sourcevertices,Three valid directions selected from9 fixed directions; near-tangent/repeated rays retried,1micrometre minimum advancement and100nmnormaloffset/cosine adaptive step.; BVH disagreements resolved only by three unanimous direct float64 triangle intersections with explicit logs, not majority voting. Distances sampled, not exactclearance/seal/OEM/physicalqualification. No source/matrix modified.','source_modified':False,'art_accepted':False};(O/'caps-solid-check.json').write_text(json.dumps(report,indent=2)+'\n');print('HEAD3_CAP_SOLIDS',json.dumps(report))
