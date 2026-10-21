"""Read actual triangle/plane sections of unstructured native tyre, without altering source."""
import bpy,json,hashlib,math,numpy as np
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/rear-tyre-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(H/'rear-tyre-v2.blend'));o=bpy.data.collections['WEWA_REAR_TYRE_ISOLATED'].objects[0];m=o.data;m.calc_loop_triangles();v=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',v);v=v.reshape(-1,3);ix=np.empty(len(m.loop_triangles)*3,np.int32);m.loop_triangles.foreach_get('vertices',ix);tris=v[ix.reshape(-1,3)].astype(np.float64);rows=[]
for theta in [.013,.081,.143,.227,.313,.441,.637,.813]:
 n=np.array([0,-math.sin(theta),math.cos(theta)]);d=tris@n;rr=tris[:,:,1]*math.cos(theta)+tris[:,:,2]*math.sin(theta);take=(d.min(1)<=1e-10)&(d.max(1)>=-1e-10)&(rr.min(1)>0);segments={}
 for tri,dist in zip(tris[take],d[take]):
  pts=[]
  for j in range(3):
   a,b=tri[j],tri[(j+1)%3];da,db=dist[j],dist[(j+1)%3]
   if abs(da)<1e-10:pts.append(a)
   if da*db<-1e-22:pts.append(a+(b-a)*(da/(da-db)))
  if len(pts)<2:continue
  points=[]
  for p in pts:
   q=(round(float(p[0]),7),round(float(p[1]*math.cos(theta)+p[2]*math.sin(theta)),7))
   if q not in points:points.append(q)
  if len(points)==2 and points[0]!=points[1]:segments[tuple(sorted(points))]=True
 # Numerical stitch for a contour graph is diagnostic only, never a mesh/buffer repair.
 graph={}
 for a,b in segments:
  graph.setdefault(a,set()).add(b);graph.setdefault(b,set()).add(a)
 bad=[p for p,e in graph.items()if len(e)!=2];assert not bad,(theta,len(bad),bad[:5]);unseen=set(graph);loops=[]
 while unseen:
  start=min(unseen);chain=[start];prev=None;cur=start
  while True:
   opts=graph[cur]-({prev}if prev else set());nxt=min(opts)
   if nxt==start:break
   assert nxt not in chain,(theta,'loop repeats');chain.append(nxt);prev,cur=cur,nxt
  unseen-=set(chain);loops.append(chain)
 assert len(loops)==1,(theta,len(loops));chain=loops[0]
 def orient(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 crossings=[]
 for i,a in enumerate(chain):
  b=chain[(i+1)%len(chain)]
  for j in range(i+2,len(chain)):
   if i==0 and j==len(chain)-1:continue
   c,e=chain[j],chain[(j+1)%len(chain)]
   if orient(a,b,c)*orient(a,b,e)<-1e-22 and orient(c,e,a)*orient(c,e,b)<-1e-22:crossings.append([i,j])
 assert not crossings,(theta,crossings[:5]);rows.append({'angle_rad':theta,'actual_triangle_plane_segments':len(segments),'section_xr_m':chain,'strict_segment_crossings':crossings,'closed_loops':1})
r={'source_sha256':sha(H/'rear-tyre-v2.blend'),'export_sha256':sha(H/'rear-tyre-v2-inspection.glb'),'actual_sections_checked':len(rows),'method':'Actual triangle/plane intersections at8 offset angles, positive radial half only. Diagnostic contour stitch precision0.1micrometre, no source or export change.','all_sampled_sections_closed_nonintersecting':True,'rows':rows,'limits':'8 sections only, not exhaustive self-intersection certification. Interior remains estimated and unloaded.'};(O/'native-section-check.json').write_text(json.dumps(r,indent=2)+'\n');print('TYRE_ACTUAL_SECTIONS',len(rows))
