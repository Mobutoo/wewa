"""Original dense formed gusset candidate; documentary dimensions remain estimated."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/frame-head-gusset-v1';P=json.loads((HERE/'parameters.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;col=bpy.data.collections.new('WEWA_FRAME_HEAD_GUSSET_ISOLATED');s.collection.children.link(col);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
land=[Vector(q)for q in P['outline_yz_m']];outline=[]
for i in range(len(land)):
 a,b,c,d=[land[k%len(land)]for k in[i-1,i,i+1,i+2]]
 for j in range(12):
  t=j/12;outline.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
def area(loop):return sum(loop[i].x*loop[(i+1)%len(loop)].y-loop[(i+1)%len(loop)].x*loop[i].y for i in range(len(loop)))/2
def inside(q):
 odd=False
 for i,a in enumerate(outline):
  b=outline[(i+1)%len(outline)]
  if(a.y>q.y)!=(b.y>q.y)and q.x<(b.x-a.x)*(q.y-a.y)/(b.y-a.y)+a.x:odd=not odd
 return odd
points=outline[:];constraints=list(range(len(points)));edges=[]
if area(outline)<0:constraints.reverse()
for i in range(len(constraints)):edges.append((constraints[i],constraints[(i+1)%len(constraints)]))
holeloops=[];bevel=P['bevel_working_m'];th=P['thickness_working_m']
for h in P['holes']:
 cy,cz=h['centre_yz_m'];rr=h['radius_working_m']+bevel;ids=[];loop=[]
 for k in range(P['hole_segments']):
  a=math.tau*k/P['hole_segments'];q=Vector((cy+rr*math.cos(a),cz+rr*math.sin(a)));ids.append(len(points));points.append(q);loop.append(q)
 edges.extend((ids[k],ids[(k+1)%len(ids)])for k in range(len(ids)));holeloops.append(loop)
spacing=P['surface_grid_spacing_working_m'];lo=[min(q[i]for q in outline)for i in[0,1]];hi=[max(q[i]for q in outline)for i in[0,1]]
for iy in range(math.ceil((hi[0]-lo[0])/spacing)+1):
 for iz in range(math.ceil((hi[1]-lo[1])/spacing)+1):
  q=Vector((lo[0]+iy*spacing,lo[1]+iz*spacing))
  if inside(q)and all((q-Vector(h['centre_yz_m'])).length>h['radius_working_m']+bevel+.00002 for h in P['holes']):points.append(q)
coords,cdtedges,cap,*_=delaunay_2d_cdt(points,edges,[constraints],1,1e-8,False)
cap=[f for f in cap if inside(sum((coords[i]for i in f),Vector((0,0)))/len(f))and all((sum((coords[i]for i in f),Vector((0,0)))/len(f)-Vector(h['centre_yz_m'])).length>h['radius_working_m']+bevel-1e-8 for h in P['holes'])]
for i,f in enumerate(cap):
 if area([coords[k]for k in f])<0:cap[i]=tuple(reversed(f))
expected=abs(area(outline))-sum(abs(area(q))for q in holeloops);actual=sum(area([coords[k]for k in f])for f in cap);assert abs(actual-expected)<1e-9,(actual,expected)
used=sorted({i for f in cap for i in f});mapping={old:new for new,old in enumerate(used)};coords=[coords[k]for k in used];cap=[tuple(mapping[k]for k in f)for f in cap];N=len(coords)
cy,cz=P['holes'][0]['centre_yz_m'];peak=P['holes'][0]['radius_working_m']+.003;sigma=.0035;H=P['large_hole_annular_form_height_m_estimated']
def field(y,z):
 dy,dz=y-cy,z-cz;r=math.hypot(dy,dz);h=H*math.exp(-((r-peak)/sigma)**2);dh=-2*(r-peak)/sigma**2*h
 return h,dh*dy/max(r,1e-20),dh*dz/max(r,1e-20)
verts=[]
for sign in[1,-1]:
 for q in coords:verts.append((field(q.x,q.y)[0]+sign*th/2,q.x,q.y))
arcs=[0.]
for k in range(len(outline)):arcs.append(arcs[-1]+(outline[(k+1)%len(outline)]-outline[k]).length)
outer_periods=max(1,round(arcs[-1]/.020))
def outer_U(q):
 best=(1e30,0.)
 for k,a in enumerate(outline):
  b=outline[(k+1)%len(outline)];d=b-a;t=max(0.,min(1.,(q-a).dot(d)/d.length_squared));error=(q-a-d*t).length_squared
  if error<best[0]:best=(error,(arcs[k]+t*d.length)/arcs[-1]*outer_periods)
 assert best[0]<1e-12
 return best[1]
faces=[];kinds=[];uvs=[]
def addface(ids,kind,uv):faces.append(tuple(ids));kinds.append(kind);uvs.append(uv)
for f in cap:
 addface(f,('cap',1),[(coords[i].x/.020,coords[i].y/.020)for i in f]);b=tuple(i+N for i in reversed(f));addface(b,('cap',-1),[(-verts[i][1]/.020,verts[i][2]/.020)for i in b])
counts=Counter(tuple(sorted((f[i],f[(i+1)%len(f)])))for f in cap for i in range(len(f)));boundary=[(f[i],f[(i+1)%len(f)])for f in cap for i in range(len(f))if counts[tuple(sorted((f[i],f[(i+1)%len(f)])))]==1];outerN=defaultdict(lambda:Vector());holemap={};innerF={};innerB={}
for a,b in boundary:
 labels=[]
 for i in[a,b]:
  match=None
  for j,h in enumerate(P['holes']):
   if abs((coords[i]-Vector(h['centre_yz_m'])).length-h['radius_working_m']-bevel)<2e-7:match=j;break
  labels.append(match)
 if labels[0]is not None and labels[0]==labels[1]:
  j=labels[0];h=P['holes'][j];c=Vector(h['centre_yz_m']);holemap[a]=holemap[b]=j
  for i in[a,b]:
   if i not in innerF:
    q=c+(coords[i]-c).normalized()*h['radius_working_m'];base=field(coords[i].x,coords[i].y)[0];innerF[i]=len(verts);verts.append((base+th/2-bevel,q.x,q.y));innerB[i]=len(verts);verts.append((base-th/2+bevel,q.x,q.y))
  rep=4 if j==0 else 1;angles=[math.atan2(coords[i].y-c.y,coords[i].x-c.x)/math.tau%1 for i in[a,b]]
  if abs(angles[0]-angles[1])>.5:angles=[q+1 if q<.5 else q for q in angles]
  ua,ub=[q*rep for q in angles];v0=0;v1=math.sqrt(2)*bevel/.020;v2=v1+(th-2*bevel)/.020;v3=v2+math.sqrt(2)*bevel/.020
  addface((b,a,innerF[a],innerF[b]),('bevel',j,1),[(ub,v0),(ua,v0),(ua,v1),(ub,v1)]);addface((innerF[b],innerF[a],innerB[a],innerB[b]),('bore',j),[(ub,v1),(ua,v1),(ua,v2),(ub,v2)]);addface((innerB[b],innerB[a],a+N,b+N),('bevel',j,-1),[(ub,v2),(ua,v2),(ua,v3),(ub,v3)])
 else:
  assert labels==[None,None],labels;q=coords[b]-coords[a];normal=Vector((0,q.y,-q.x)).normalized();outerN[a]+=normal;outerN[b]+=normal
  # Edgechart uses a physical20mm projection along perimeteredge, no collapse.
  ua,ub=outer_U(coords[a]),outer_U(coords[b])
  if abs(ua-ub)>outer_periods/2:
   if ua<ub:ua+=outer_periods
   else:ub+=outer_periods
  addface((b,a,a+N,b+N),('outer',),[(ub,0),(ua,0),(ua,th/.020),(ub,th/.020)])
mesh=bpy.data.meshes.new('Original constrained dense formedplate and three entryprofiles');mesh.from_pydata(verts,[],faces);mesh.update();assert not mesh.validate(clean_customdata=False);uv=mesh.uv_layers.new(name='Estimated20mm caps; circumferential4/1 repeats on entrywalls');normals=[]
for f,kind,values in zip(mesh.polygons,kinds,uvs):
 f.use_smooth=True
 for li,t in zip(f.loop_indices,values):
  uv.data[li].uv=t;i=mesh.loops[li].vertex_index;q=mesh.vertices[i].co
  if kind[0]=='cap':
   _,dy,dz=field(q.y,q.z);normal=Vector((1,-dy,-dz)).normalized()*kind[1]
  elif kind[0]in['bore','bevel']:
   h=P['holes'][kind[1]];y,z=h['centre_yz_m'];rad=Vector((0,q.y-y,q.z-z)).normalized();normal=-rad if kind[0]=='bore'else Vector((kind[2],-rad.y,-rad.z)).normalized()
  else:normal=outerN[i%N].normalized()
  normals.append(normal)
mesh.normals_split_custom_set(normals);mesh.update();o=bpy.data.objects.new('Frame headgusset - documentedface only conditionalcandidate',mesh);col.objects.link(o);o['component_id']=P['component_id'];o['all_physical_dimensions_estimated']=True;o['analytical_normals_intentional']=True;o['opposite_gusset_modelled']=False
m=bpy.data.materials.new('Neutral formedgusset geometry');m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(.28,.30,.33,1);q.inputs['Roughness'].default_value=.3;mesh.materials.append(m);mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh);nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;todo=[unseen.pop()]
 while todo:
  for ed in todo.pop().link_edges:
   for v in ed.verts:
    if v in unseen:unseen.remove(v);todo.append(v)
euler=len(bm.verts)-len(bm.edges)+len(bm.faces);bm.free();areas=[(mesh.vertices[t.vertices[1]].co-mesh.vertices[t.vertices[0]].co).cross(mesh.vertices[t.vertices[2]].co-mesh.vertices[t.vertices[0]].co).length/2 for t in mesh.loop_triangles];tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[list(t.vertices)for t in mesh.loop_triangles],all_triangles=True);probes=[]
for h in P['holes']:
 y,z=h['centre_yz_m'];clear=tree.ray_cast(Vector((.03,y,z)),Vector((-1,0,0)),.06)[0]is None;assert clear;probes.append({'label':h['label'],'centre_yz_m':[y,z],'axis_X_clear':clear})
assert tree.ray_cast(Vector((.03,.060,-.065)),Vector((-1,0,0)),.06)[0]is not None
errors=[(mesh.corner_normals[k].vector-n).length for k,n in enumerate(normals)];assert nm==0 and shells==1 and vol>0 and euler==-4 and min(areas)>1e-18 and max(errors)<.001,(nm,shells,vol,euler,min(areas),max(errors))
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;export=HERE/'frame-head-gusset-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
w=bpy.data.worlds.new('Gusset neutralstudio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,loc,power,size in[('KEY',(.18,.01,-.14),.6,.08),('FILL',(-.18,.12,.02),.5,.16),('EDGE',(.12,.18,-.08),.3,.12)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;x=bpy.data.objects.new(name,d);studio.objects.link(x);x.location=loc;x.rotation_euler=(Vector((0,.06,-.07))-x.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('HEAD_GUSSET_CAMERA',bpy.data.cameras.new('HEAD_GUSSET_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.22,.16,.08);cam.rotation_euler=(Vector((0,.06,-.07))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.24;cam.data.clip_start=.001;cam.data.clip_end=5;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';source=HERE/'frame-head-gusset-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
r={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'connected_shells':shells,'nonmanifold_edges':nm,'Euler_characteristic':euler,'signed_volume_m3':vol,'minimum_triangle_area_m2':min(areas),'zero_area_triangles_at_1e18_m2':sum(v<=1e-18 for v in areas),'planar_cap_area_expected_m2':expected,'planar_cap_area_actual_m2':actual,'outer_wall_UV_periods':outer_periods,'outer_wall_UV_period_m':arcs[-1]/outer_periods,'max_custom_normal_vector_error':max(errors),'normal_error_note':'Blender compactnormalencoding versus authoranalyticalfield, not OEMtolerance','through_hole_probes':probes,'holes':P['holes'],'analytical_normals_intentional':True,'hidden_backface_and_forming_direction_estimated':True,'all_physical_dimensions_estimated':True,'manufacturing_process_verified':False,'physicalside_verified':False,'opposite_gusset_built':False,'complete_frame_built':False,'art_accepted':False};(OUT/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_HEAD_GUSSET',json.dumps(r))
