"""Original related PF111000 headtube outer envelope; every physical dimension estimated."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/frame-head-tube-v1';P=json.loads((HERE/'parameters.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('WEWA_FRAME_HEADTUBE_ISOLATED');s.collection.children.link(col);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio);R=P['end_lip_outer_radius_working_m'];r=P['bore_radius_working_m'];h=P['overall_length_working_m'];N=P['radial_segments'];profile=[]
def add(radius,z,dr,dz):
 mag=math.hypot(dr,dz);row=(radius,z,dz/mag,-dr/mag)
 if profile and math.hypot(radius-profile[-1][0],z-profile[-1][1])<1e-12:return
 profile.append(row)
def line(a,b,steps=1):
 for k in range(steps+1):
  t=k/steps;add(a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t,b[0]-a[0],b[1]-a[1])
def arc(rc,zc,rad,start,steps=12):
 for k in range(steps+1):
  angle=start+math.pi/2*k/steps;add(rc+rad*math.cos(angle),zc+rad*math.sin(angle),-math.sin(angle),math.cos(angle))
def bez(a,b,c,d,steps=18):
 for k in range(steps+1):
  t=k/steps;u=1-t;rr=u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*d[0];zz=u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*d[1];dr=3*u*u*(b[0]-a[0])+6*u*t*(c[0]-b[0])+3*t*t*(d[0]-c[0]);dz=3*u*u*(b[1]-a[1])+6*u*t*(c[1]-b[1])+3*t*t*(d[1]-c[1]);add(rr,zz,dr,dz)
e=.0004;mid=P['main_outer_radius_working_m']
line((r+e,0),(R-e,0));arc(R-e,e,e,-math.pi/2);line((R,e),(R,.002));bez((R,.002),(R,.0035),(mid,.0035),(mid,.005));line((mid,.005),(mid,h-.005),36);bez((mid,h-.005),(mid,h-.0035),(R,h-.0035),(R,h-.002));line((R,h-.002),(R,h-e));arc(R-e,h-e,e,0);line((R-e,h),(r+e,h));arc(r+e,h-e,e,math.pi/2);line((r,h-e),(r,e),36);arc(r+e,e,e,math.pi)
if math.hypot(profile[-1][0]-profile[0][0],profile[-1][1]-profile[0][1])<1e-12:profile.pop()
vertices=[];normals=[];faces=[];uvs=[];arc=[0.]
for i,(radius,z,nr,nz)in enumerate(profile):
 if i:arc.append(arc[-1]+math.hypot(radius-profile[i-1][0],z-profile[i-1][1]))
 for j in range(N):
  angle=math.tau*j/N;vertices.append((radius*math.cos(angle),radius*math.sin(angle),z));normals.append((nr*math.cos(angle),nr*math.sin(angle),nz))
for i,row in enumerate(profile):
 k=(i+1)%len(profile);flat=abs(row[1]-profile[k][1])<1e-12;repeats=14
 for j in range(N):
  ids=(i*N+j,i*N+(j+1)%N,k*N+(j+1)%N,k*N+j);faces.append(ids)
  if flat:coords=[(vertices[v][0]/.010,vertices[v][1]/.010)for v in ids]
  else:
   av=arc[i];bv=arc[k]if k else arc[-1]+math.hypot(profile[0][0]-row[0],profile[0][1]-row[1]);coords=[(j/N*repeats,av/.010),((j+1)/N*repeats,av/.010),((j+1)/N*repeats,bv/.010),(j/N*repeats,bv/.010)]
  uvs.append(coords)
mesh=bpy.data.meshes.new('Original continuous hollow steeringheadtube envelope');mesh.from_pydata(vertices,[],faces);mesh.update();uv=mesh.uv_layers.new(name='Planar10mm end lips; integer14 circumference charts')
for f,coords in zip(mesh.polygons,uvs):
 f.use_smooth=True
 for li,q in zip(f.loop_indices,coords):uv.data[li].uv=q
mesh.normals_split_custom_set([normals[loop.vertex_index]for loop in mesh.loops]);mesh.update();o=bpy.data.objects.new('Frame headtube - relatedPF111000 conditional envelope',mesh);col.objects.link(o);o['component_id']=P['component_id'];o['all_physical_dimensions_estimated']=True;o['installed_orientation_verified']=False;o['bearing_seats_modelled']=False
m=bpy.data.materials.new('Neutral headtube geometry - material pending');m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(.32,.34,.37,1);q.inputs['Roughness'].default_value=.32;mesh.materials.append(m);mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;todo=[unseen.pop()]
 while todo:
  for ed in todo.pop().link_edges:
   for v in ed.verts:
    if v in unseen:unseen.remove(v);todo.append(v)
bm.free();areas=[(mesh.vertices[t.vertices[1]].co-mesh.vertices[t.vertices[0]].co).cross(mesh.vertices[t.vertices[2]].co-mesh.vertices[t.vertices[0]].co).length/2 for t in mesh.loop_triangles];tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[list(t.vertices)for t in mesh.loop_triangles],all_triangles=True);probes=[]
for label,x,expected in[('axis',0,True),('inside_working_bore',r-.0003,True),('estimated_annular_end_face',r+.0006,False),('outside_ring',R+.0005,True)]:
 clear=tree.ray_cast(Vector((x,0,-.010)),Vector((0,0,1)),.030)[0]is None;assert clear==expected;probes.append({'name':label,'origin_x_m':x,'Z_ray_clear':clear,'expected_clear':expected})
assert nonmanifold==0 and shells==1 and volume>0 and min(areas)>1e-18
normal_errors=[]
for loop in mesh.loops:normal_errors.append((mesh.corner_normals[loop.index].vector-Vector(normals[loop.vertex_index])).length)
# Blender stores custom normals in a compact loop-space encoding; record its
# numerical deviation rather than claiming exact floating-point reconstruction.
assert max(normal_errors)<.001

bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;export=HERE/'frame-head-tube-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
w=bpy.data.worlds.new('Headtube neutral studio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.40
for name,loc,power,size in[('KEY',(.30,.24,.27),3,.24),('FILL',(-.26,.22,.12),1.5,.22),('EDGE',(.18,-.28,.18),2,.24),('LOWER',(-.15,.18,-.18),.7,.2)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;x=bpy.data.objects.new(name,d);studio.objects.link(x);x.location=loc;x.rotation_euler=(Vector((0,0,h/2))-x.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('FRAME_HEADTUBE_CAMERA',bpy.data.cameras.new('FRAME_HEADTUBE_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.26,.30,.22);cam.rotation_euler=(Vector((0,0,h/2))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.215;cam.data.clip_start=.001;cam.data.clip_end=5;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';source=HERE/'frame-head-tube-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
report={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'connected_shells':shells,'nonmanifold_edges':nonmanifold,'signed_volume_m3':volume,'minimum_triangle_area_m2':min(areas),'zero_area_triangles_at_1e18_m2':sum(v<=1e-18 for v in areas),'probes':probes,'fresh_analytical_profile_normals':True,'maximum_source_corner_normal_vector_error':max(normal_errors),'normal_encoding_note':'Fresh analytical normals encoded by Blender source API; numerical max vector error bounded by0.001, not a physical tolerance','measured_manufacturer_dimensions':False,'all_physical_dimensions_estimated':True,'bearing_seats_modelled':False,'complete_frame_modelled':False,'current_RDC_identity_verified':False,'art_accepted':False};(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_FRAME_HEADTUBE',json.dumps(report))
