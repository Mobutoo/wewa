"""Conforming longest-edge refinement of underresolved corrected crown only.
Old source vertices remain exact, UV interpolated per corner, new normals analytic.
No voxel/general remesh or GLB repair. 50um is a sampled author criterion only.
"""
import bpy,bmesh,json,hashlib,math,sys,numpy as np
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/rear-tyre-v2';sys.path.insert(0,str(H));from junction_field import JunctionField
P=json.loads((H/'parameters.json').read_text());F=JunctionField(P);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not json.loads((O/'source-geometry-check.json').read_text()).get('junction_local_refinement',False),'Run build.py first; do not refine an already refined source';input_source_sha=sha(H/'rear-tyre-v2.blend');input_glb_sha=sha(H/'rear-tyre-v2-inspection.glb');bpy.ops.wm.open_mainfile(filepath=str(H/'rear-tyre-v2.blend'));o=bpy.data.collections[P['collection']].objects[0];oldm=o.data

def ar(c,k,n,dt):
 a=np.empty(len(c)*n,dt);c.foreach_get(k,a);return a.reshape(-1,n)if n>1 else a
V=ar(oldm.vertices,'co',3,np.float32);I=ar(oldm.polygons,'vertices',3,np.int32);UV=ar(oldm.uv_layers.active.data,'uv',2,np.float32).reshape(-1,3,2);NN=ar(oldm.corner_normals,'vector',3,np.float32).reshape(-1,3,3);initial_V=V.copy();initial_count=len(V);history=[]
def fields(v):
 x=v[:,0].astype(np.float64);r=np.hypot(v[:,1].astype(np.float64),v[:,2]);arc=np.mod(np.arctan2(v[:,2].astype(np.float64),v[:,1]),math.tau)*P['outside_radius_m_estimated'];return x,r,arc

def sample():
 x,r,a=fields(V);crown=np.zeros(len(V),bool);ids=np.flatnonzero(np.abs(x)<.04101);crown[ids]=np.abs(r[ids]-F.crown(x[ids],a[ids]))<5e-7;changed=np.zeros(len(V),bool);changed[ids]=np.abs(F.depth(x[ids],a[ids],True)-F.depth(x[ids],a[ids],False))>1e-8;faces=np.flatnonzero(crown[I].all(1)&changed[I].any(1));tri=V[I[faces]].astype(np.float64);errs=[]
 for w in [(1/3,1/3,1/3),(.5,.5,0),(0,.5,.5),(.5,0,.5)]:
  q=sum(tri[:,j]*v for j,v in enumerate(w));xx,rr,aa=fields(q);errs.append(np.abs(F.crown(xx,aa)-rr))
 E=np.array(errs);bad=faces[E.max(0)>.00005];return bad,{'triangles':len(I),'vertices':len(V),'sampled_triangles':len(faces),'sampled_max_radial_error_m':float(E.max()),'sampled_p99_radial_error_m':float(np.quantile(E,.99)),'bad_triangles':len(bad)}
def edgekeys(e):
 a=np.minimum(e[...,0],e[...,1]).astype(np.uint64);b=np.maximum(e[...,0],e[...,1]).astype(np.uint64);return(a<<np.uint64(32))|b

def analytic_normal(v):
 x,r,arc=fields(v);h=2e-6;rr=F.crown(x,arc);rx=(F.crown(x+h,arc)-F.crown(x-h,arc))/(2*h);rs=(F.crown(x,arc+h)-F.crown(x,arc-h))/(2*h);t=arc/P['outside_radius_m_estimated'];co=np.cos(t);si=np.sin(t);ps=np.stack([np.zeros_like(rs),rs*co-rr/P['outside_radius_m_estimated']*si,rs*si+rr/P['outside_radius_m_estimated']*co],-1);px=np.stack([np.ones_like(rx),rx*co,rx*si],-1);n=np.cross(ps,px);return(n/np.linalg.norm(n,axis=1)[:,None]).astype(np.float32)
for iteration in range(9):
 bad,row=sample();row['iteration']=iteration;history.append(row);print('LOCAL_JUNCTION_REFINEMENT',json.dumps(row),flush=True)
 if not len(bad):break
 assert iteration<8,('Local refinement did not reach sampled criterion',row)
 be=I[bad][:,[[0,1],[1,2],[2,0]]];length=np.linalg.norm(V[be[:,:,0]].astype(np.float64)-V[be[:,:,1]],axis=2);chosen=be[np.arange(len(be)),length.argmax(1)];marked=np.unique(edgekeys(chosen));ends=np.stack([(marked>>np.uint64(32)).astype(np.int32),(marked&np.uint64(0xffffffff)).astype(np.int32)],-1);mid=(V[ends[:,0]].astype(np.float64)+V[ends[:,1]])/2;x,r,arc=fields(mid);rr=F.crown(x,arc);theta=arc/P['outside_radius_m_estimated'];mid[:,1]=rr*np.cos(theta);mid[:,2]=rr*np.sin(theta);mid=mid.astype(np.float32);assert not np.any(np.all(mid==V[ends[:,0]],1)|np.all(mid==V[ends[:,1]],1)),'Float32 midpoint collapsed';newnorm=analytic_normal(mid);offset=len(V);V=np.concatenate([V,mid]);allkeys=edgekeys(I[:,[[0,1],[1,2],[2,0]]]);split=np.isin(allkeys,marked);touched=split.any(1);where=np.flatnonzero(touched);NF=[];NU=[];NNN=[]
 for fi in where:
  ids=I[fi];local={int(ids[j]):(UV[fi,j],NN[fi,j])for j in range(3)};mm={}
  for j in np.flatnonzero(split[fi]):
   k=int(np.searchsorted(marked,allkeys[fi,j]));ni=offset+k;mm[int(j)]=ni;local[ni]=((UV[fi,j]+UV[fi,(j+1)%3])*.5,newnorm[k])
  n=len(mm)
  if n==1:
   e=next(iter(mm));a,b,c=map(int,[ids[e],ids[(e+1)%3],ids[(e+2)%3]]);q=mm[e];ff=[(a,q,c),(q,b,c)]
  elif n==2:
   missing=next(j for j in range(3)if j not in mm);c=(missing+2)%3;a=(c+2)%3;b=(c+1)%3;ma,mb=mm[a],mm[c];ff=[(int(ids[c]),mb,ma),(int(ids[a]),ma,int(ids[b])),(ma,mb,int(ids[b]))]
  else:
   a,b,c=map(int,ids);m0,m1,m2=mm[0],mm[1],mm[2];ff=[(a,m0,m2),(m0,b,m1),(m2,m1,c),(m0,m1,m2)]
  for f in ff:NF.append(f);NU.append([local[j][0]for j in f]);NNN.append([local[j][1]for j in f])
 I=np.concatenate([I[~touched],np.array(NF,np.int32)]);UV=np.concatenate([UV[~touched],np.array(NU,np.float32)]);NN=np.concatenate([NN[~touched],np.array(NNN,np.float32)])
assert np.array_equal(V[:initial_count],initial_V);assert np.array_equal(V.min(0),initial_V.min(0))and np.array_equal(V.max(0),initial_V.max(0));tri=V[I].astype(np.float64);area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2;volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);assert area.min()>1e-18,('Zero area from local refinement',float(area.min()));m=bpy.data.meshes.new('Locally refined corrected groove junctions');m.from_pydata(V,[],I);m.update();assert not m.validate(clean_customdata=False);u=m.uv_layers.new(name='Physical meridian and188 circumferential repeats');u.data.foreach_set('uv',UV.ravel());m.polygons.foreach_set('use_smooth',np.ones(len(I),bool));m.normals_split_custom_set(NN.reshape(-1,3));m.materials.append(oldm.materials[0]);o.data=m;bpy.data.meshes.remove(oldm);bm=bmesh.new();bm.from_mesh(m);nm=sum(not e.is_manifold for e in bm.edges);chi=len(bm.verts)-len(bm.edges)+len(bm.faces);bm.free();assert nm==0 and chi==0 and volume>0
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.gltf(filepath=str(H/'rear-tyre-v2-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True);bpy.ops.wm.save_as_mainfile(filepath=str(H/'rear-tyre-v2.blend'),compress=True);report={'input_source_sha256':input_source_sha,'input_export_sha256':input_glb_sha,'source_sha256':sha(H/'rear-tyre-v2.blend'),'export_sha256':sha(H/'rear-tyre-v2-inspection.glb'),'old_vertex_prefix_exact':True,'initial_vertices':initial_count,'added_vertices':len(V)-initial_count,'indices_changed_by_local_subdivision':True,'UV_interpolated_per_corner_without_seam_welding':True,'new_vertex_normals_analytic':True,'axis_aligned_bounds_exact':True,'iterations':history,'sampled_error_goal_m':.00005,'global_bound_proved':False,'no_buffer_repair':True,'art_accepted':False};(O/'junction-local-refinement.json').write_text(json.dumps(report,indent=2)+'\n');q=json.loads((O/'source-geometry-check.json').read_text());q.update(source_sha256=report['source_sha256'],export_sha256=report['export_sha256'],vertices=len(V),triangles=len(I),minimum_triangle_area_m2=float(area.min()),signed_volume_m3=volume,nonmanifold_edges=nm,euler_characteristic=chi,source_probes=[],junction_local_refinement=True);(O/'source-geometry-check.json').write_text(json.dumps(q,indent=2)+'\n');(H/'build-report.json').write_text(json.dumps(q,indent=2)+'\n');print('TYRE2_LOCAL_REFINED',json.dumps(report),flush=True)
