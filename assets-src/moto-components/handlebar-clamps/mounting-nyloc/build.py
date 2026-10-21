"""Original conditional M10 low-profile locknut, independent metal and insert."""
import bpy,bmesh,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/handlebar-mount-nyloc-v1';P=json.loads((HERE/'parameters.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('WEWA_HANDLEBAR_MOUNT_NYLOC_ISOLATED');s.collection.children.link(col);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
N=P['radial_segments'];phi=np.arange(N)*math.tau/N
def bezier(points,steps):
 a,b,c,d=np.asarray(points,dtype=float);return [(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for t in np.linspace(0,1,steps+1)]
def rounded_hex_radius():
 # Minkowski offset of a smaller regular hexagon, with constant17mm AF.
 apothem=P['across_flats_working_m']/2;rho=P['corner_radius_working_m'];rr=(apothem-rho)/math.cos(math.pi/6)
 corners=np.array([[rr*math.cos(k*math.pi/3+math.pi/6),rr*math.sin(k*math.pi/3+math.pi/6)]for k in range(6)])
 unit=np.stack([np.cos(phi),np.sin(phi)],-1);lo=np.full(N,apothem-rho);hi=np.full(N,apothem/math.cos(math.pi/6))
 for _ in range(55):
  mid=(lo+hi)/2;q=unit*mid[:,None];distance=np.full(N,np.inf)
  for k in range(6):
   a=corners[k];b=corners[(k+1)%6];v=b-a;t=np.clip((q-a)@v/(v@v),0,1);distance=np.minimum(distance,np.linalg.norm(q-(a+t[:,None]*v),axis=1))
  normals=np.array([[math.cos(k*math.pi/3),math.sin(k*math.pi/3)]for k in range(6)])
  inside=np.max(q@normals.T,axis=1)<=apothem-rho
  distance=np.where(inside,-distance,distance)
  lo=np.where(distance<rho,mid,lo);hi=np.where(distance>=rho,mid,hi)
 return (lo+hi)/2
hex_r=rounded_hex_radius();profiles=[]
def add(r,z,role):
 row=(np.broadcast_to(r,(N,)).astype(float).copy(),float(z),role)
 if profiles and abs(profiles[-1][1]-z)<1e-12 and np.max(abs(profiles[-1][0]-row[0]))<1e-12:return
 profiles.append(row)
for z in np.linspace(0,P['hex_height_working_m'],145):
 limit=min(.0079+z*math.sqrt(3),.0079+(P['hex_height_working_m']-z)*math.sqrt(3));add(np.minimum(hex_r,limit),z,'outer_hex')
for z in np.linspace(.0067,.0087,12)[1:]:add(.0079,z,'outer_crown')
for r,z in bezier([(.0079,.0087),(.0079,.0096),(.0077,.0100),(.0072,.0100)],24)[1:]:add(r,z,'rolled_crown')
for r,z in bezier([(.0072,.0100),(.0069,.0100),(.0067,.0098),(.0067,.00945)],20)[1:]:add(r,z,'rolled_crown')
for z in np.linspace(.00945,.00705,15)[1:]:add(.0067,z,'insert_seat')
for r,z in bezier([(.0067,.00705),(.0067,.00695),(.0065,.00690),(.0052,.00690)],16)[1:]:add(r,z,'insert_seat_floor')
pitch=P['thread_pitch_working_m'];major=(P['thread_nominal_diameter_m']+P['thread_diametral_clearance_working_m'])/2;minor=major-5*math.sqrt(3)*pitch/16
def thread_r(z):
 phase=(z/pitch-phi/math.tau)%1
 # Original60degree nominal-style profile: flat crests, roots, twoflanks.
 f=np.where(phase<.125,0,np.where(phase<.4375,(phase-.125)/.3125,np.where(phase<.5625,1,np.where(phase<.875,(.875-phase)/.3125,0))))
 nominal=minor+(major-minor)*f
 # Estimated lead-in/runout, not a tolerance-class or physical thread gauge.
 ease=max(0,min(1,(z-.00035)/.00055,(.0069-z)/.00055));return nominal*ease+.0052*(1-ease)
for z in np.linspace(.00685,.00035,math.ceil(.0065/pitch*P['thread_steps_per_pitch'])+1):add(thread_r(z),z,'female_thread')
add(.0053,0,'lower_entry')
def mat(name,c):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.38;return m
gray=mat('Neutral metal geometry - coating pending',(.36,.38,.40));insertgray=mat('Neutral insert geometry - compound pending',(.16,.18,.20))
def mesh_from_profile(name,rings,material):
 verts=[];faces=[];metadata=[];arc=[0.]
 for i,(r,z,role)in enumerate(rings):
  verts.extend(np.stack([r*np.cos(phi),r*np.sin(phi),np.full(N,z)],-1).tolist())
  if i:arc.append(arc[-1]+math.hypot(float(np.mean(r-rings[i-1][0])),z-rings[i-1][1]))
 for i,(r,z,role)in enumerate(rings):
  k=(i+1)%len(rings);flat=abs(z-rings[k][1])<1e-12
  for j in range(N):
   a=i*N+j;b=i*N+(j+1)%N;c=k*N+(j+1)%N;d=k*N+j;faces.extend([(a,b,c),(a,c,d)]);metadata.extend([(i,k,j,flat,0),(i,k,j,flat,1)])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(material)
 uv=mesh.uv_layers.new(name='Estimated6mm profile reference and10circumferential repeats');mesh.set_sharp_from_angle(angle=.55)
 plane_normals=np.array([[math.cos(a*math.pi/3),math.sin(a*math.pi/3)]for a in range(6)])
 for face,(i,k,j,flat,tri)in zip(mesh.polygons,metadata):
  face.use_smooth=not flat
  if rings[i][2]=='outer_hex'and rings[k][2]=='outer_hex':
   q=np.array([mesh.vertices[v].co[:2]for v in face.vertices]);distance=abs(q@plane_normals.T-P['across_flats_working_m']/2)
   if np.any(np.max(distance,axis=0)<3e-8):face.use_smooth=False
  if flat:
   for li in face.loop_indices:
    v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v.x/.006,v.y/.006)
  else:
   u0=j/N*10;u1=(j+1)/N*10;v0=arc[i]/.006;v1=(arc[k]if k else arc[-1]+math.hypot(float(np.mean(rings[0][0]-rings[-1][0])),rings[0][1]-rings[-1][1]))/.006
   coords=[(u0,v0),(u1,v0),(u1,v1)]if tri==0 else[(u0,v0),(u1,v1),(u0,v1)]
   for li,co in zip(face.loop_indices,coords):uv.data[li].uv=co
 mesh.update();o=bpy.data.objects.new(name,mesh);col.objects.link(o)
 return o
metal=mesh_from_profile('Locknut metal body - conditionalDIN985M10 with original female helix',profiles,gray)
ins=[]
def ip(r,z):ins.append((np.full(N,r),z,'polymer_insert'))
# Rounded rectangular annular meridian, no pretended unloaded female thread.
for center,angles in [((.0065,.00725),(-math.pi/2,0)),((.0065,.0093),(0,math.pi/2)),((.00485,.0093),(math.pi/2,math.pi)),((.00485,.00725),(math.pi,3*math.pi/2))]:
 for a in np.linspace(*angles,13):ip(center[0]+.00015*math.cos(a),center[1]+.00015*math.sin(a))
insert=mesh_from_profile('Nonmetal locking insert - unloaded visualestimate',ins,insertgray)
checks=[]
for o in [metal,insert]:
 bm=bmesh.new();bm.from_mesh(o.data);nm=sum(not e.is_manifold for e in bm.edges);unseen=set(bm.verts);shells=0
 while unseen:
  shells+=1;todo=[unseen.pop()]
  while todo:
   for ed in todo.pop().link_edges:
    for v in ed.verts:
     if v in unseen:unseen.remove(v);todo.append(v)
 vol=bm.calc_volume(signed=True);bm.free();area=[p.area for p in o.data.polygons];assert not nm and shells==1 and vol>0 and min(area)>1e-18
 tree=BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons],all_triangles=True);axisfree=tree.ray_cast(Vector((0,0,-.005)),Vector((0,0,1)),.020)[0]is None;assert axisfree
 o['component_id']=P['component_id'];o['current_RDC_identity_verified']=False;o['installed_fit_verified']=False
 checks.append({'object':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.polygons),'connected_shells':shells,'non_manifold_edges':nm,'signed_volume_m3':vol,'min_triangle_area_m2':min(area),'axis_open':axisfree})
assert max(z for _,z,_ in profiles)==P['height_working_m']
assert .01673<=float(hex_r.min()*2)<=.01700001 and float(hex_r.max()*2)>=.0189
# Conservative separation: insert is radially inside the seat and above its floor.
assert P['polymer_outer_radius_working_m']<.0067 and min(z for _,z,_ in ins)>.00705
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
bpy.context.view_layer.objects.active=metal
bpy.ops.export_scene.gltf(filepath=str(HERE/'handlebar-mount-nyloc-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
w=bpy.data.worlds.new('Locknut neutral studio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.40
for name,loc,power,size in [('KEY',(.035,.030,.050),.11,.050),('FILL',(-.040,.020,.025),.045,.040),('EDGE',(.020,-.045,.035),.08,.045),('LOWER',(-.025,.030,-.025),.02,.025)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.005))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('NYLOC_CAMERA',bpy.data.cameras.new('NYLOC_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.032,.038,.031);cam.rotation_euler=(Vector((0,0,.005))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.029;cam.data.clip_start=.001;cam.data.clip_end=5
s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'handlebar-mount-nyloc-v1.blend'),compress=True)
r={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'source_sha256':hashlib.sha256((HERE/'handlebar-mount-nyloc-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'handlebar-mount-nyloc-inspection.glb').read_bytes()).hexdigest(),'objects':checks,'conditional_family':'DIN985M10,notidentifiedOEMnorm','nominal_targets_m':{'height':P['height_working_m'],'across_flats':P['across_flats_working_m'],'pitch':pitch},'working_thread_major_minor_diameter_m':[major*2,minor*2],'insert_steel_radial_separation_m':.0067-P['polymer_outer_radius_working_m'],'nylon_function_strain_and_preload_verified':False,'current_RDC_identity_verified':False,'art_accepted':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_NYLOC_SOURCE',json.dumps(r))
