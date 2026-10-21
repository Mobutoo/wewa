"""Original isolated related DS181007 annulus; every physical dimension estimated."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/handlebar-mount-upper-washer-v1';P=json.loads((HERE/'parameters.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('WEWA_HANDLEBAR_MOUNT_UPPER_WASHER_ISOLATED');s.collection.children.link(col);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio);R=P['outer_diameter_working_m']/2;r=P['bore_diameter_working_m']/2;h=P['thickness_working_m'];a=P['outer_edge_radius_working_m'];b=P['bore_entry_radius_working_m'];N=P['radial_segments'];profile=[]
for rc,zc,radius,start in[(R-a,a,a,-math.pi/2),(R-a,h-a,a,0),(r+b,h-b,b,math.pi/2),(r+b,b,b,math.pi)]:
 for k in range(P['quarter_round_steps']+1):
  angle=start+math.pi/2*k/P['quarter_round_steps'];profile.append((rc+radius*math.cos(angle),zc+radius*math.sin(angle),math.cos(angle),math.sin(angle)))
vertices=[];normals=[];faces=[];uvs=[];arc=[0.]
for i,(radius,z,nr,nz)in enumerate(profile):
 if i:arc.append(arc[-1]+math.hypot(radius-profile[i-1][0],z-profile[i-1][1]))
 for j in range(N):
  angle=math.tau*j/N;vertices.append((radius*math.cos(angle),radius*math.sin(angle),z));normals.append((nr*math.cos(angle),nr*math.sin(angle),nz))
for i,row in enumerate(profile):
 k=(i+1)%len(profile);flat=abs(row[1]-profile[k][1])<1e-12;repeats=16 if(row[0]+profile[k][0])/2>.010 else 6
 for j in range(N):
  ids=(i*N+j,i*N+(j+1)%N,k*N+(j+1)%N,k*N+j);faces.append(ids)
  if flat:coords=[(vertices[v][0]/.006,vertices[v][1]/.006)for v in ids]
  else:
   av=arc[i];bv=arc[k]if k else arc[-1]+math.hypot(profile[0][0]-row[0],profile[0][1]-row[1]);coords=[(j/N*repeats,av/.006),((j+1)/N*repeats,av/.006),((j+1)/N*repeats,bv/.006),(j/N*repeats,bv/.006)]
  uvs.append(coords)
mesh=bpy.data.meshes.new('Original continuous rounded annular section');mesh.from_pydata(vertices,[],faces);mesh.update();uv=mesh.uv_layers.new(name='Planar6mm faces; integer16/6 circumference edge charts')
for f,coords in zip(mesh.polygons,uvs):
 f.use_smooth=True
 for li,q in zip(f.loop_indices,coords):uv.data[li].uv=q
mesh.normals_split_custom_set([normals[loop.vertex_index]for loop in mesh.loops]);mesh.update();o=bpy.data.objects.new('Upper handlebar washer - relatedDS181007 conditional candidate',mesh);col.objects.link(o);o['component_id']=P['component_id'];o['all_physical_dimensions_estimated']=True;o['installed_orientation_verified']=False
m=bpy.data.materials.new('Neutral washer geometry - material pending');m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(.32,.34,.37,1);q.inputs['Roughness'].default_value=.32;mesh.materials.append(m);mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;todo=[unseen.pop()]
 while todo:
  for ed in todo.pop().link_edges:
   for v in ed.verts:
    if v in unseen:unseen.remove(v);todo.append(v)
bm.free();areas=[(mesh.vertices[t.vertices[1]].co-mesh.vertices[t.vertices[0]].co).cross(mesh.vertices[t.vertices[2]].co-mesh.vertices[t.vertices[0]].co).length/2 for t in mesh.loop_triangles];tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[list(t.vertices)for t in mesh.loop_triangles],all_triangles=True);probes=[]
for label,x,expected in[('axis',0,True),('inside_working_bore',r-.0003,True),('estimated_bearing_face',r+.0006,False),('outside_ring',R+.0005,True)]:
 clear=tree.ray_cast(Vector((x,0,-.010)),Vector((0,0,1)),.030)[0]is None;assert clear==expected;probes.append({'name':label,'origin_x_m':x,'Z_ray_clear':clear,'expected_clear':expected})
assert nonmanifold==0 and shells==1 and volume>0 and min(areas)>1e-18
normal_errors=[]
for loop in mesh.loops:normal_errors.append((mesh.corner_normals[loop.index].vector-Vector(normals[loop.vertex_index])).length)
# Blender stores custom normals in a compact loop-space encoding; record its
# numerical deviation rather than claiming exact floating-point reconstruction.
assert max(normal_errors)<.001

bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;export=HERE/'handlebar-mount-upper-washer-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
w=bpy.data.worlds.new('Upperwasher neutral studio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.40
for name,loc,power,size in[('KEY',(.060,.050,.075),.25,.070),('FILL',(-.065,.040,.030),.12,.060),('EDGE',(.030,-.070,.045),.18,.065),('LOWER',(-.035,.040,-.045),.05,.050)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;x=bpy.data.objects.new(name,d);studio.objects.link(x);x.location=loc;x.rotation_euler=(Vector((0,0,h/2))-x.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('UPPER_WASHER_CAMERA',bpy.data.cameras.new('UPPER_WASHER_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.045,.055,.060);cam.rotation_euler=(Vector((0,0,h/2))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.044;cam.data.clip_start=.001;cam.data.clip_end=5;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';source=HERE/'handlebar-mount-upper-washer-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
report={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'connected_shells':shells,'nonmanifold_edges':nonmanifold,'signed_volume_m3':volume,'minimum_triangle_area_m2':min(areas),'zero_area_triangles_at_1e18_m2':sum(v<=1e-18 for v in areas),'probes':probes,'fresh_analytical_profile_normals':True,'maximum_source_corner_normal_vector_error':max(normal_errors),'normal_encoding_note':'Fresh analytical normals encoded by Blender source API; numerical max vector error bounded by0.001, not a physical tolerance','measured_manufacturer_dimensions':False,'all_physical_dimensions_estimated':True,'lower_face_observed':False,'current_RDC_identity_verified':False,'art_accepted':False};(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_UPPER_WASHER',json.dumps(report))
