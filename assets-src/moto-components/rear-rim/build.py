"""Original continuous rear-wheel surface; no global CSG bevel or buffer repair."""
import bpy,bmesh,math,json,hashlib,bisect
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/rear-rim-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;col=bpy.data.collections.new(P['collection']);s.collection.children.link(col);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
def area(q):return sum(q[i].x*q[(i+1)%len(q)].y-q[(i+1)%len(q)].x*q[i].y for i in range(len(q)))/2
def inside(q,loop):
 odd=False
 for i,a in enumerate(loop):
  b=loop[(i+1)%len(loop)]
  if(a.y>q.y)!=(b.y>q.y)and q.x<(b.x-a.x)*(q.y-a.y)/(b.y-a.y)+a.x:odd=not odd
 return odd
def segment_distance(q,a,b):
 d=b-a;t=max(0,min(1,(q-a).dot(d)/d.length_squared));return(q-a-d*t).length
rad=P['attach_radius_m_estimated'];N=P['radial_segments'];outer=[Vector((rad*math.cos(math.tau*k/N),rad*math.sin(math.tau*k/N)))for k in range(N)];holes=[]
def pchip(xs,ys):
 sec=[(ys[k+1]-ys[k])/(xs[k+1]-xs[k])for k in range(len(xs)-1)];sl=[0.]
 for k in range(1,len(xs)-1):
  a,b=sec[k-1],sec[k];h0,h1=xs[k]-xs[k-1],xs[k+1]-xs[k];w0,w1=2*h1+h0,h1+2*h0;sl.append(0. if a*b<=0 else(w0+w1)/(w0/a+w1/b))
 sl.append(0.)
 def value(r):
  if r<=xs[0]:return ys[0]
  if r>=xs[-1]:return ys[-1]
  k=bisect.bisect_right(xs,r)-1;h=xs[k+1]-xs[k];t=(r-xs[k])/h;return(2*t**3-3*t*t+1)*ys[k]+(t**3-2*t*t+t)*h*sl[k]+(-2*t**3+3*t*t)*ys[k+1]+(t**3-t*t)*h*sl[k+1]
 return value
width=pchip(P['spoke_width_radius_stations_m'],P['spoke_projected_width_stations_m_estimated']);r0=P['spoke_hole_inner_radius_m_estimated'];r1=P['spoke_hole_outer_radius_m_estimated']
for k in range(5):
 left=math.tau*k/5+P['spoke_phase_rad_estimated'];right=left+math.tau/5
 def pol(r,a):return Vector((r*math.cos(a),r*math.sin(a)))
 def al(r):return left+width(r)/(2*r)
 def ar(r):return right-width(r)/(2*r)
 curves=[lambda t:pol(r0,al(r0)+(ar(r0)-al(r0))*t),lambda t:pol(r0+(r1-r0)*t,ar(r0+(r1-r0)*t)),lambda t:pol(r1,ar(r1)+(al(r1)-ar(r1))*t),lambda t:pol(r1+(r0-r1)*t,al(r1+(r0-r1)*t))];trimmed=[]
 for fn in curves:
  pp=[fn(j/200)for j in range(201)];arc=[0.]
  for j in range(200):arc.append(arc[-1]+(pp[j+1]-pp[j]).length)
  def at(distance):
   j=max(0,min(199,bisect.bisect_right(arc,distance)-1));return(j+(distance-arc[j])/(arc[j+1]-arc[j]))/200
  d=P['spoke_hole_corner_trim_m_estimated'];trimmed.append((fn,at(d),at(arc[-1]-d)))
 loop=[]
 for j,(fn,start,end)in enumerate(trimmed):
  loop +=[fn(start+(end-start)*n/50)for n in range(51)];a=fn(end);b=fn(1);nxt,t0,_=trimmed[(j+1)%4];c=nxt(t0)
  for n in range(1,10):
   t=n/10;loop.append((1-t)**2*a+2*t*(1-t)*b+t*t*c)
 if area(loop)<0:loop.reverse()
 holes.append({'curve':loop,'edge_radius':P['spoke_aperture_edge_radius_m_estimated'],'kind':'spoke aperture'})
holes.append({'curve':[Vector((.076*math.cos(math.tau*k/N),.076*math.sin(math.tau*k/N)))for k in range(N)],'edge_radius':0.,'kind':'open visible hub envelope'})
for h in holes:
 c=h['curve'];h['outward']=[Vector(((c[(k+1)%len(c)]-c[k-1]).y,-(c[(k+1)%len(c)]-c[k-1]).x)).normalized()for k in range(len(c))];h['cap']=[q+h['edge_radius']*n for q,n in zip(c,h['outward'])]
 assert area(h['cap'])>0
points=outer[:];edges=[(k,(k+1)%N)for k in range(N)]
for h in holes:
 h['input_ids']=list(range(len(points),len(points)+len(h['cap'])));points+=h['cap'];ids=h['input_ids'];edges +=[(ids[k],ids[(k+1)%len(ids)])for k in range(len(ids))]
kd=KDTree(sum(len(h['cap'])for h in holes));kd_records=[]
for j,h in enumerate(holes):
 for k,q in enumerate(h['cap']):kd.insert((q.x,q.y,0),len(kd_records));kd_records.append((j,k))
kd.balance()
def inhole(q):
 rr=q.length
 if rr<.078:return inside(q,holes[-1]['cap'])
 if rr<.073 or rr>.194:return False
 ac=math.atan2(q.y,q.x);k=round((ac-P['spoke_phase_rad_estimated']-math.pi/5)/(math.tau/5))%5;return inside(q,holes[k]['cap'])
spacing=P['surface_grid_spacing_m'];margin=spacing*.45
for iy in range(math.ceil(2*rad/spacing)+1):
 for iz in range(math.ceil(2*rad/spacing)+1):
  q=Vector((-rad+(iy+.173)*spacing,-rad+(iz+.319)*spacing))
  if q.length>rad-margin or inhole(q):continue
  _,idx,_=kd.find((q.x,q.y,0));j,k=kd_records[idx];loop=holes[j]['cap']
  if min(segment_distance(q,loop[k-1],loop[k]),segment_distance(q,loop[k],loop[(k+1)%len(loop)]))<margin:continue
  points.append(q)
coords,cdte,cap,*_=delaunay_2d_cdt(points,edges,[list(range(N))],1,1e-8,False);cap=[f for f in cap if not inhole(sum((coords[k]for k in f),Vector((0,0)))/len(f))]
for k,f in enumerate(cap):
 if area([coords[i]for i in f])<0:cap[k]=tuple(reversed(f))
expected=abs(area(outer))-sum(abs(area(h['cap']))for h in holes);actual=sum(area([coords[k]for k in f])for f in cap);assert abs(actual-expected)<1e-8,(actual,expected)
used=sorted({i for f in cap for i in f});mapping={old:new for new,old in enumerate(used)};coords=[coords[k]for k in used];cap=[tuple(mapping[k]for k in f)for f in cap];C=len(coords);look={tuple(round(float(v),7)for v in q):i for i,q in enumerate(coords)}
def coord_id(q):
 key=tuple(round(float(v),7)for v in q);assert key in look,tuple(q);i=look[key];assert(coords[i]-q).length<5e-8;return i
outerids=[coord_id(q)for q in outer]
for h in holes:h['capids']=[coord_id(q)for q in h['cap']]
# Monotone cubic Hermite radial depth, with analytic derivatives for all cap normals.
xr=P['heightfield_radius_stations_m'];yh=P['heightfield_halfdepth_stations_m_estimated'];sec=[(yh[k+1]-yh[k])/(xr[k+1]-xr[k])for k in range(len(xr)-1)];slopes=[0.]
for k in range(1,len(xr)-1):
 a,b=sec[k-1],sec[k]
 if a*b<=0:slopes.append(0.)
 else:
  h0,h1=xr[k]-xr[k-1],xr[k+1]-xr[k];w0,w1=2*h1+h0,h1+2*h0;slopes.append((w0+w1)/(w0/a+w1/b))
slopes.append(0.)
def height(r):
 if r<=xr[0]:return yh[0],0.
 if r>=xr[-1]:return yh[-1],0.
 k=bisect.bisect_right(xr,r)-1;d=xr[k+1]-xr[k];t=(r-xr[k])/d;a,b=yh[k:k+2];m,n=slopes[k:k+2];v=(2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*d*m+(-2*t**3+3*t*t)*b+(t**3-t*t)*d*n;der=(6*t*t-6*t)*a/d+(3*t*t-4*t+1)*m+(-6*t*t+6*t)*b/d+(3*t*t-2*t)*n;return v,der
def capnormal(q,sign=1):
 _,der=height(q.length);return Vector((sign,-sign*der*q.x/max(q.length,1e-20),-sign*der*q.y/max(q.length,1e-20))).normalized()
verts=[];normals=[]
for sign in[1,-1]:
 for q in coords:verts.append((sign*height(q.length)[0],q.x,q.y));normals.append(capnormal(q,sign))
faces=[];uvs=[];kinds=[]
def face(ids,values,kind):
 for j in range(1,len(ids)-1):faces.append((ids[0],ids[j],ids[j+1]));uvs.append((values[0],values[j],values[j+1]));kinds.append(kind)
for f in cap:
 face(f,[(coords[i].x/.010,coords[i].y/.010)for i in f],'front cap');b=tuple(i+C for i in reversed(f));face(b,[(-verts[i][1]/.010,verts[i][2]/.010)for i in b],'reverse cap')
def addvertex(xyz,n):i=len(verts);verts.append(tuple(xyz));normals.append(Vector(n).normalized());return i
# Every aperture has its own continuous rounded entry, wall and reverse entry.
for h in holes[:5]:
 c=h['curve'];out=h['outward'];K=len(c);rho=h['edge_radius'];steps=10;wallsteps=12;curves=[]
 for j in range(steps+1):
  alpha=math.pi/2*j/steps;curves.append(('front',alpha))
 for j in range(1,wallsteps+1):curves.append(('wall',j/wallsteps))
 for j in range(1,steps+1):curves.append(('back',math.pi/2*(1-j/steps)))
 grid=[];gridpos=[]
 for j,(kind,t)in enumerate(curves):
  ring=[];pos=[]
  for k,(q,n)in enumerate(zip(c,out)):
   if kind=='wall':p=q;x=(height(q.length)[0]-rho)*(1-2*t)
   else:
    p=q+rho*n*(1-math.sin(t));hh=height(p.length)[0];x=hh-rho*(1-math.cos(t))if kind=='front'else-hh+rho*(1-math.cos(t))
   xyz=Vector((x,p.x,p.y));pos.append(xyz)
   if j==0:i=h['capids'][k]
   elif j==len(curves)-1:i=h['capids'][k]+C
   else:i=addvertex(xyz,(0,-n.x,-n.y))
   ring.append(i)
  grid.append(ring);gridpos.append(pos)
 # Analytic meridian derivative; circumferential derivative includes depth and offset curvature.
 for j,(kind,t)in enumerate(curves):
  if j in[0,len(curves)-1]:continue
  for k,(q,n)in enumerate(zip(c,out)):
   ts=gridpos[j][(k+1)%K]-gridpos[j][k-1]
   if kind=='wall':tp=Vector((-1,0,0))
   else:
    sign=1 if kind=='front'else-1;p=q+rho*n*(1-math.sin(t));dp=-rho*math.cos(t)*n if kind=='front'else rho*math.cos(t)*n;dh=height(p.length)[1]*p.dot(dp)/max(p.length,1e-20);dx=dh-rho*math.sin(t)if kind=='front'else-dh-rho*math.sin(t);tp=Vector((dx,dp.x,dp.y))
   normals[grid[j][k]]=ts.cross(tp).normalized()
 arcs=[0.]
 for k in range(K):arcs.append(arcs[-1]+(c[(k+1)%K]-c[k]).length)
 repeats=max(1,round(arcs[-1]/.010));vv=[]
 for k in range(K):
  a=[0.]
  for j in range(1,len(grid)):a.append(a[-1]+(gridpos[j][k]-gridpos[j-1][k]).length/.010)
  vv.append(a)
 for j in range(len(grid)-1):
  for k in range(K):
   kn=(k+1)%K;u0,u1=arcs[k]/arcs[-1]*repeats,arcs[k+1]/arcs[-1]*repeats;face((grid[j][k],grid[j][kn],grid[j+1][kn],grid[j+1][k]),[(u0,vv[k][j]),(u1,vv[kn][j]),(u1,vv[kn][j+1]),(u0,vv[k][j+1])],h['kind'])
# Open original crosssection connects front and reverse caps into a real drop-centre rim.
raw=P['rim_open_profile_xr_m_estimated'];prof=[Vector(raw[0])]
for j in range(1,len(raw)-1):
 a,b,c=[Vector(q)for q in raw[j-1:j+2]];d=min(.0003,(a-b).length*.24,(c-b).length*.24);start=b+(a-b).normalized()*d;end=b+(c-b).normalized()*d
 for k in range(6):
  t=k/5;prof.append((1-t)**2*start+2*t*(1-t)*b+t*t*end)
prof.append(Vector(raw[-1]));grid=[];arcs=[0.]
for j in range(1,len(prof)):arcs.append(arcs[-1]+(prof[j]-prof[j-1]).length)
for j,q in enumerate(prof):
 ring=[];dp=prof[min(j+1,len(prof)-1)]-prof[max(j-1,0)]
 for k in range(N):
  theta=math.tau*k/N;co,si=math.cos(theta),math.sin(theta)
  if j==0:i=outerids[k]
  elif j==len(prof)-1:i=outerids[k]+C
  else:i=addvertex((q.x,q.y*co,q.y*si),(dp.y,-dp.x*co,-dp.x*si))
  ring.append(i)
 grid.append(ring)
for j in range(len(grid)-1):
 for k in range(N):
  kn=(k+1)%N;u0,u1=k/N*128,(k+1)/N*128;v0,v1=arcs[j]/.010,arcs[j+1]/.010;face((grid[j][k],grid[j+1][k],grid[j+1][kn],grid[j][kn]),[(u0,v0),(u0,v1),(u1,v1),(u1,v0)],'rounded rimsection')
# Native annular outer hub envelope. Unknown central bearing/coupling web is excluded.
raw=P['hub_open_profile_xr_m_estimated'];prof=[Vector(raw[0])]
for j in range(1,len(raw)-1):
 a,b,c=[Vector(q)for q in raw[j-1:j+2]];d=min(.0003,(a-b).length*.24,(c-b).length*.24);start=b+(a-b).normalized()*d;end=b+(c-b).normalized()*d
 for k in range(6):
  t=k/5;prof.append((1-t)**2*start+2*t*(1-t)*b+t*t*end)
prof.append(Vector(raw[-1]));grid=[];arcs=[0.]
for j in range(1,len(prof)):arcs.append(arcs[-1]+(prof[j]-prof[j-1]).length)
for j,q in enumerate(prof):
 ring=[];dp=prof[min(j+1,len(prof)-1)]-prof[max(j-1,0)]
 for k in range(N):
  theta=math.tau*k/N;co,si=math.cos(theta),math.sin(theta)
  if j==0:i=holes[-1]['capids'][k]
  elif j==len(prof)-1:i=holes[-1]['capids'][k]+C
  else:i=addvertex((q.x,q.y*co,q.y*si),(-dp.y,dp.x*co,dp.x*si))
  ring.append(i)
 grid.append(ring)
for j in range(len(grid)-1):
 for k in range(N):
  kn=(k+1)%N;u0,u1=k/N*48,(k+1)/N*48;v0,v1=arcs[j]/.010,arcs[j+1]/.010;face((grid[j][k],grid[j][kn],grid[j+1][kn],grid[j+1][k]),[(u0,v0),(u1,v0),(u1,v1),(u0,v1)],'hub outer envelope')
mesh=bpy.data.meshes.new('Original continuous rear casting, native sections and six apertures');mesh.from_pydata(verts,[],faces);mesh.update();assert not mesh.validate(clean_customdata=False);uv=mesh.uv_layers.new(name='Physical10mm caps and meridian charts, integer circumferential repeats');loopnorm=[]
for f,values in zip(mesh.polygons,uvs):
 f.use_smooth=True
 for li,q in zip(f.loop_indices,values):uv.data[li].uv=q;loopnorm.append(normals[mesh.loops[li].vertex_index])
mesh.normals_split_custom_set(loopnorm);mesh.update();o=bpy.data.objects.new('Rear casting native continuous surface - conditional candidate',mesh);col.objects.link(o);o['component_id']=P['component_id'];o['all_physical_dimensions_estimated_except_nominal_size']=True;o['analytic_source_normals_intentional']=True
m=bpy.data.materials.new('Neutral rear casting shape - silver finish pending');m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(.24,.26,.28,1);q.inputs['Roughness'].default_value=.30;mesh.materials.append(m);mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh);nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);chi=len(bm.verts)-len(bm.edges)+len(bm.faces);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;stack=[unseen.pop()]
 while stack:
  for e in stack.pop().link_edges:
   for v in e.verts:
    if v in unseen:unseen.remove(v);stack.append(v)
bm.free();minarea=min(t.area for t in mesh.loop_triangles);assert nm==0 and shells==1 and chi==-10 and vol>0 and minarea>1e-18,(nm,shells,chi,vol,minarea)
bpy.context.view_layer.update();tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());probes=[]
def ray(label,origin,direction,distance,clear):
 hit=tree.ray_cast(Vector(origin),Vector(direction),distance);actual=hit[0]is None;assert actual==clear,(label,hit);probes.append({'label':label,'origin_m':list(origin),'direction':list(direction),'distance_m':distance,'clear':actual,'hit_distance_m':hit[3]})
ray('open hub axis clearance',(-.1,0,0),(1,0,0),.2,True)
for k in range(5):
 a=math.tau*(k+.5)/5+P['spoke_phase_rad_estimated'];ray('spoke opening '+str(k+1),(-.1,.14*math.cos(a),.14*math.sin(a)),(1,0,0),.2,True)
 a=math.tau*k/5+P['spoke_phase_rad_estimated'];ray('shaped spoke solid '+str(k+1),(-.1,.14*math.cos(a),.14*math.sin(a)),(1,0,0),.2,False)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.max_bounces=8;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.20,.23,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
for name,loc,power,size in [('KEY',(.45,.25,.65),16,.50),('FILL',(-.40,.35,.18),10,.45),('EDGE',(.10,-.35,.45),12,.35),('LOWER',(.25,.35,-.35),5,.3)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;x=bpy.data.objects.new(name,l);studio.objects.link(x);x.location=loc;x.rotation_euler=(-Vector(loc)).to_track_quat('-Z','Y').to_euler()
c=bpy.data.cameras.new('Isolated rear casting camera');cam=bpy.data.objects.new('CAMERA',c);studio.objects.link(cam);s.camera=cam;cam.location=(.65,.4,.3);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=.57;c.clip_start=.001;c.clip_end=10
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.gltf(filepath=str(H/'rear-rim-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True);bpy.ops.wm.save_as_mainfile(filepath=str(H/'rear-rim-v1.blend'),compress=True)
r={'component_id':P['component_id'],'revision':P['revision'],'collection':P['collection'],'source_frame':P['frame'],'source_sha256':sha(H/'rear-rim-v1.blend'),'export_sha256':sha(H/'rear-rim-inspection.glb'),'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'connected_shells':shells,'nonmanifold_edges':nm,'euler_characteristic':chi,'signed_volume_m3':vol,'minimum_triangle_area_m2':minarea,'source_probes':probes,'CDT_cap_area_m2':actual,'expected_cap_area_m2':expected,'cap_area_error_m2':abs(actual-expected),'cap_grid_spacing_m_estimated':spacing,'rounded_aperture_count':6,'no_CSG_bevel_remesh_or_buffer_repair':True,'analytic_source_normals':True,'hub_scope':'Visible annular outer wall only. Central bearing/coupling web, bearingseats, carrier and certified friction surface NOT fabricated. Unverified I-section excluded.','all_physical_dimensions_estimated_except_nominal_size':True,'art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(H/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('REAR_NATIVE_SOURCE',json.dumps({k:r[k]for k in ['source_sha256','export_sha256','vertices','triangles','connected_shells','nonmanifold_edges','euler_characteristic','minimum_triangle_area_m2']}))
