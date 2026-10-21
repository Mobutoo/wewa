"""Constraint-aligned native crown patch; original estimated groove pattern, no copied mould."""
import bpy,bmesh,math,json,hashlib,bisect
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/rear-tyre-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;col=bpy.data.collections.new(P['collection']);s.collection.children.link(col);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
def pchip(xs,ys):
 d=[(ys[i+1]-ys[i])/(xs[i+1]-xs[i])for i in range(len(xs)-1)];m=[d[0]]
 for i in range(1,len(xs)-1):
  a,b=d[i-1:i+1];h0,h1=xs[i]-xs[i-1],xs[i+1]-xs[i];w0,w1=2*h1+h0,h1+2*h0;m.append(0 if a*b<=0 else(w0+w1)/(w0/a+w1/b))
 m.append(d[-1])
 def f(t):
  i=max(0,min(len(xs)-2,bisect.bisect_right(xs,t)-1));h=xs[i+1]-xs[i];u=(t-xs[i])/h;return(2*u**3-3*u*u+1)*ys[i]+(u**3-2*u*u+u)*h*m[i]+(-2*u**3+3*u*u)*ys[i+1]+(u**3-u*u)*h*m[i+1]
 return f
def section(raw,N):
 arc=[0.]
 for a,b in zip(raw,raw[1:]):arc.append(arc[-1]+math.dist(a,b))
 x=pchip(arc,[q[0]for q in raw]);r=pchip(arc,[q[1]for q in raw]);return[(x(arc[-1]*j/(N-1)),r(arc[-1]*j/(N-1)))for j in range(N)]
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def trench(d,width,depth):return depth*(1-smooth(max(0,width/2-P['groove_lip_transition_m_estimated']),width/2,d))
repeat=P['tread_repeats_estimated'];assert repeat%2==0;copies=repeat//2;R0=P['outside_radius_m_estimated'];circ=math.tau*R0;pitch=circ/repeat;T=2*pitch;X=.041;SN=128
raw=P['outer_profile_xr_m_estimated'][4:13];radius=pchip([q[0]for q in raw],[q[1]for q in raw])
def depth(x,r,arc):
 if r<.279 or abs(x)>.039:return 0.
 u=arc/pitch;side=1 if x>=0 else-1;ax=abs(x);lane=.010+.0024*math.sin(math.tau*u+.35*side)
 a=trench(abs(ax-lane),P['main_groove_width_m_estimated'],P['groove_depth_m_estimated']);target=.60*ax+.0018*math.sin(ax/.032*math.pi)+(0 if side>0 else pitch*.5);dist=abs((arc-target+pitch/2)%pitch-pitch/2)/math.sqrt(1+.60**2);b=trench(dist,.0030,.0032)*smooth(.0065,.012,ax)*(1-smooth(.034,.039,ax));dist=abs((arc+.003*math.sin(x/.012*math.pi)+pitch)%(2*pitch)-pitch);c=trench(dist,.0028,.0029)*(1-smooth(.008,.012,ax));return max(a,b,c)*smooth(.279,.289,r)
def crown_r(x,arc):return radius(x)-depth(x,radius(x),arc)
# Explicit geometric lip/bottom contours constrain triangulation; sparse background grid only fills smooth lands.
paths=[]
for side in [-1,1]:
 for off in [-.0013,-.00085,-.00045,0,.00045,.00085,.0013]:
  paths.append([(T*j/SN,side*(.010+.0024*math.sin(math.tau*(T*j/SN)/pitch+.35*side))+off)for j in range(SN+1)])
 for n in range(-2,4):
  for off in [-.0015,-.00105,-.00065,0,.00065,.00105,.0015]:
   paths.append([(.60*ax+.0018*math.sin(ax/.032*math.pi)+(0 if side>0 else pitch*.5)+n*pitch+off*math.sqrt(1+.60**2),side*ax)for ax in [.0065+(.039-.0065)*j/72 for j in range(73)]])
for n in [-1,0,1,2]:
 for off in [-.0014,-.000975,-.00055,0,.00055,.000975,.0014]:
  paths.append([(-.003*math.sin(x/.012*math.pi)+n*T+off,x)for x in [-.012+.024*j/64 for j in range(65)]])
def clip(a,b):
 da=b[0]-a[0];db=b[1]-a[1];lo,hi=0.,1.
 for p,q in [(-da,a[0]),(da,T-a[0]),(-db,a[1]+X),(db,X-a[1])]:
  if abs(p)<1e-15:
   if q<0:return None
  else:
   t=q/p
   if p<0:lo=max(lo,t)
   else:hi=min(hi,t)
  if lo>hi:return None
 return[(max(0,min(T,a[0]+t*da)),max(-X,min(X,a[1]+t*db)))for t in [lo,hi]]
segments=[];xb=[-X,X];sb=[T*k/SN for k in range(SN+1)]
for path in paths:
 for a,b in zip(path,path[1:]):
  seg=clip(a,b)
  if not seg or math.dist(*seg)<1e-8:continue
  segments.append(seg)
  for q in seg:
   if abs(q[0])<1e-9 or abs(q[0]-T)<1e-9:xb.append(q[1])
# Both periodic sides receive the same boundary vertices before CDT.
xb+= [-X+2*X*k/96 for k in range(97)];xb=sorted(set(round(x,10)for x in xb));points=[];edges=[];key={}
def pid(q):
 k=(round(q[0],10),round(q[1],10))
 if k not in key:key[k]=len(points);points.append(Vector(k))
 return key[k]
def addseg(a,b):
 ia,ib=pid(a),pid(b)
 if ia!=ib:edges.append((ia,ib))
border=[(v,-X)for v in sb]+[(T,x)for x in xb[1:]]+[(v,X)for v in reversed(sb[:-1])]+[(0,x)for x in reversed(xb[1:-1])];borderids=[pid(q)for q in border]
for a,b in zip(border,border[1:]+border[:1]):addseg(a,b)
for a,b in segments:addseg(a,b)
# Avoid points almost coincident with constrained lines; CDT itself computes crossings.
for j in range(1,69):
 for k in range(1,69):pid((T*j/69,-X+2*X*k/69))
refinement=[]
for iteration in range(10):
 coords,ee,ff,origv,orige,origf=delaunay_2d_cdt(points,edges,[borderids],1,1e-7,True);assert all(len(f)==3 for f in ff);edgeorig={tuple(sorted(e)):orige[i]for i,e in enumerate(ee)};added=[];errors=[];periodic_added=[]
 for f in ff:
  qs=[coords[i]for i in f];hs=[crown_r(q.y,q.x)for q in qs]
  probes=[((qs[0]+qs[1]+qs[2])/3,sum(hs)/3,None)]
  probes +=[((qs[i]+qs[(i+1)%3])/2,(hs[i]+hs[(i+1)%3])/2,tuple(sorted((f[i],f[(i+1)%3]))))for i in range(3)]
  candidates=[]
  for q,h0,edge in probes:
   error=abs(crown_r(q.y,q.x)-h0);errors.append(error)
   if error>.000050 and (q.x<2e-7 or T-q.x<2e-7) and abs(q.y)<X-1e-7:periodic_added.extend([Vector((0,q.y)),Vector((T,q.y))])
   if error>.000050 and min((q-v).length for v in qs)>.000002 and q.x>1e-7 and q.x<T-1e-7 and abs(q.y)<X-1e-7:candidates.append((error,q,edgeorig.get(edge,[])))
  if candidates:added.append(max(candidates,key=lambda z:z[0])[1:])
 errors.sort();refinement.append({'iteration':iteration,'tile_vertices':len(coords),'tile_triangles':len(ff),'max_radial_error_sampled_m':errors[-1],'p99_radial_error_sampled_m':errors[int(len(errors)*.99)],'new_probe_candidates':len(added),'periodic_probe_candidates':len(periodic_added)})
 if (not added and not periodic_added)or iteration==9:break
 old=len(points);splits={}
 for q,original_edges in added:
  if original_edges:
   for ei in original_edges:
    va,vb=edges[ei];a,b=points[va],points[vb];d=b-a;t=max(0,min(1,(q-a).dot(d)/d.length_squared));point=pid(a+d*t)
    if point not in[va,vb]:splits.setdefault(ei,[]).append((t,point))
  else:pid(q)
 for q in periodic_added:pid(q)
 newedges=[]
 for ei,(va,vb)in enumerate(edges):
  chain=[va]+[pid for _,pid in sorted(set(splits.get(ei,[])))]+[vb]
  newedges.extend((x,y)for x,y in zip(chain,chain[1:])if x!=y)
 edges=newedges
 if len(points)==old:break
 assert len(points)<45000,('Adaptive point budget',len(points),refinement[-1])
 print('ADAPTIVE_GROOVE',refinement[-1],flush=True)
domainarea=sum(abs((coords[f[1]]-coords[f[0]]).cross(coords[f[2]]-coords[f[0]]))/2 for f in ff);assert abs(domainarea-2*X*T)<1e-8,(domainarea,2*X*T)
(O/'constraint-refinement-diagnostic.json').write_text(json.dumps({'domain_test_preceded_mesh_export':True,'radial_sample_target_m':.000050,'why':'Half pixel radial distance for120mm macro/1200px; numerical approximation only, not a measurement or universal quality threshold.','samples':'Every triangle centroid and three edge midpoints in authorUVdomain, not a mathematical global bound.','iterations':refinement},indent=2)+'\n')
# Lock the output periodic boundary to one common canonical X list; no buffer welding.
periodic=sorted(set(round(q.y,7)for q in coords if abs(q.x)<2e-7 or abs(q.x-T)<2e-7))
verts=[];normals=[];faces=[];uvs=[];vertexkeys={}
def addvertex(x,r,theta,n):
 theta=theta%math.tau
 if theta<1e-10 or math.tau-theta<1e-10:theta=0.
 k=(round(x,7),round(r,7),round(theta,10))
 if k in vertexkeys:return vertexkeys[k]
 i=len(verts);vertexkeys[k]=i;verts.append((x,r*math.cos(theta),r*math.sin(theta)));normals.append(tuple(Vector(n).normalized()));return i
def face(ids,uv):
 faces.append(tuple(ids));uvs.append(uv)
# Arc density used only for physical UV; it does not deform the authored profile.
xs=[-X+2*X*j/2048 for j in range(2049)];aa=[0.]
for a,b in zip(xs,xs[1:]):aa.append(aa[-1]+math.hypot(b-a,radius(b)-radius(a)))
arcfn=pchip(xs,aa);left=section(P['outer_profile_xr_m_estimated'][:5],55);right=[(-x,r)for x,r in reversed(left)];inside=section(P['inner_profile_xr_m_estimated'],85);leftarc=sum(math.dist(a,b)for a,b in zip(left,left[1:]));crownarc=aa[-1];N=SN*copies
for block in range(copies):
 ids=[];vuv=[]
 for q in coords:
  ar=max(0,min(T,q.x));x=max(-X,min(X,q.y))
  if ar<2e-7 or T-ar<2e-7:
   ar=0 if ar<2e-7 else T;x=min(periodic,key=lambda z:abs(z-x))
  if abs(x+X)<2e-7:x=-X;ar=min(sb,key=lambda z:abs(z-ar))
  if abs(x-X)<2e-7:x=X;ar=min(sb,key=lambda z:abs(z-ar))
  globalarc=ar+block*T;theta=(globalarc/circ*math.tau)%math.tau;r=crown_r(x,ar);h=2e-6;rx=(crown_r(x+h,ar)-crown_r(x-h,ar))/(2*h);rs=(crown_r(x,ar+h)-crown_r(x,ar-h))/(2*h);co,si=math.cos(theta),math.sin(theta);ps=Vector((0,rs*co-r/R0*si,rs*si+r/R0*co));px=Vector((1,rx*co,rx*si));ids.append(addvertex(x,r,theta,ps.cross(px)));vuv.append((globalarc/circ*188,(leftarc+arcfn(x))/.010))
 for f in ff:face([ids[i]for i in f],[vuv[i]for i in f])
# Remaining closed section uses smooth meridian strips; crown-edge rings share actual native vertices.
profile=right+inside[1:]+left[1:];patharc=[leftarc+crownarc]
for a,b in zip(profile,profile[1:]):patharc.append(patharc[-1]+math.dist(a,b))
rings=[]
for j,(x,r)in enumerate(profile):
 d=Vector(profile[min(j+1,len(profile)-1)])-Vector(profile[max(j-1,0)]);ring=[]
 for k in range(N):
  t=math.tau*k/N;co,si=math.cos(t),math.sin(t);ring.append(addvertex(x,r,t,(-d.y,d.x*co,d.x*si)))
 rings.append(ring)
for j in range(len(rings)-1):
 for k in range(N):
  kn=(k+1)%N;a,b,c,d=rings[j][k],rings[j+1][k],rings[j+1][kn],rings[j][kn];u0,u1=k/N*188,(k+1)/N*188;v0,v1=patharc[j]/.010,patharc[j+1]/.010;face([a,c,b],[(u0,v0),(u1,v1),(u0,v1)]);face([a,d,c],[(u0,v0),(u1,v0),(u1,v1)])
mesh=bpy.data.meshes.new('Constraint-aligned crown, native closed tyre section');mesh.from_pydata(verts,[],faces);mesh.update();assert not mesh.validate(clean_customdata=False);uv=mesh.uv_layers.new(name='Physical meridian and188 circumferential repeats');ln=[]
for f,values in zip(mesh.polygons,uvs):
 f.use_smooth=True
 for li,q in zip(f.loop_indices,values):uv.data[li].uv=q;ln.append(normals[mesh.loops[li].vertex_index])
bm=bmesh.new();bm.from_mesh(mesh);vol=bm.calc_volume(signed=True);nm=sum(not e.is_manifold for e in bm.edges);chi=len(bm.verts)-len(bm.edges)+len(bm.faces);bm.free();assert vol>0 and nm==0 and chi==0,(vol,nm,chi);mesh.normals_split_custom_set(ln);mesh.update();mesh.calc_loop_triangles();minarea=min(t.area for t in mesh.loop_triangles);assert minarea>1e-18,minarea;o=bpy.data.objects.new('Rear tyre native aligned grooves - estimated mould candidate',mesh);col.objects.link(o);o['component_id']=P['component_id'];o['all_physical_dimensions_estimated_except_nominal_size']=True;o['tyre_brand_or_model_identified']=False;o['analytic_author_normals_intentional']=True
m=bpy.data.materials.new('Neutral gray geometry only - rubber material pending');m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(.20,.21,.23,1);q.inputs['Roughness'].default_value=.3;mesh.materials.append(m)
bpy.context.view_layer.update();tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());probes=[]
def ray(label,origin,direction,distance,clear):
 hit=tree.ray_cast(Vector(origin),Vector(direction),distance);actual=hit[0]is None;assert actual==clear,(label,hit);probes.append({'label':label,'origin_m':list(origin),'direction_m':list(direction),'direction':list(direction),'distance_m':distance,'clear':actual,'hit_distance_m':hit[3]})
ray('open axle axis',(-.15,0,0),(1,0,0),.3,True)
for theta in [0,.13,.31]:ray('rubber crown at angle '+str(theta),(0,.34*math.cos(theta),.34*math.sin(theta)),(0,-math.cos(theta),-math.sin(theta)),.09,False)
ray('bead opening clearance',(-.10,.20,0),(1,0,0),.20,True)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.max_bounces=8;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.20,.23,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
for name,loc,power,size in [('KEY',(.6,.35,.75),23,.65),('FILL',(-.6,.35,.2),15,.6),('EDGE',(.1,-.5,.55),18,.5),('LOWER',(.4,.4,-.45),8,.45)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;x=bpy.data.objects.new(name,l);studio.objects.link(x);x.location=loc;x.rotation_euler=(-Vector(loc)).to_track_quat('-Z','Y').to_euler()
c=bpy.data.cameras.new('Isolated rear tyre camera');cam=bpy.data.objects.new('CAMERA',c);studio.objects.link(cam);s.camera=cam;cam.location=(.65,.65,.3);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=.70;c.clip_start=.001;c.clip_end=10
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.gltf(filepath=str(H/'rear-tyre-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True);bpy.ops.wm.save_as_mainfile(filepath=str(H/'rear-tyre-v1.blend'),compress=True)
r={'component_id':P['component_id'],'revision':P['revision'],'collection':P['collection'],'source_frame':P['frame'],'source_sha256':sha(H/'rear-tyre-v1.blend'),'export_sha256':sha(H/'rear-tyre-inspection.glb'),'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'connected_shells':1,'nonmanifold_edges':nm,'euler_characteristic':chi,'signed_volume_m3':vol,'minimum_triangle_area_m2':minarea,'source_probes':probes,'nominal_designation':'3.00-17 TL','all_physical_dimensions_estimated_except_nominal_size':True,'brand_or_exact_mould_identified':False,'grooves_are_native_geometry':True,'no_buffer_repair':True,'constraint_domain_area_m2':domainarea,'expected_domain_area_m2':2*X*T,'crown_tile_copies':copies,'crown_tile_vertices':len(coords),'crown_tile_triangles':len(ff),'constraint_epsilon_m':1e-7,'native_constraint_aligned_groove_lips':True,'adaptive_refinement':refinement,'analytic_author_normals':True,'art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(H/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('REAR_TYRE_SOURCE',json.dumps(r))
