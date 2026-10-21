"""Original conditional M10 low-profile locknut, independent metal and insert."""
import bpy,bmesh,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/handlebar-mount-nyloc-v3';P=json.loads((HERE/'parameters.json').read_text())
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
 row=(np.broadcast_to(r,(N,)).astype(float).copy(),np.broadcast_to(z,(N,)).astype(float).copy(),role)
 if profiles and np.max(abs(profiles[-1][1]-row[1]))<1e-12 and np.max(abs(profiles[-1][0]-row[0]))<1e-12:return
 profiles.append(row)
# Follow the exact cone/rounded-hex intersection, rather than clipping a zgrid.
zbottom=(hex_r-.0079)/math.sqrt(3);ztop=P['hex_height_working_m']-zbottom
for t in np.linspace(0,1,13):add(.0079+t*(hex_r-.0079),t*zbottom,'outer_hex')
for t in np.linspace(0,1,25)[1:]:add(hex_r,(1-t)*zbottom+t*ztop,'outer_hex')
for t in np.linspace(0,1,13)[1:]:add((1-t)*hex_r+t*.0079,(1-t)*ztop+t*P['hex_height_working_m'],'outer_hex')
for z in np.linspace(.0067,.0087,12)[1:]:add(.0079,z,'outer_crown')
for r,z in bezier([(.0079,.0087),(.0079,.0096),(.0077,.0100),(.0072,.0100)],24)[1:]:add(r,z,'rolled_crown')
for r,z in bezier([(.0072,.0100),(.0069,.0100),(.0067,.0098),(.0067,.00945)],20)[1:]:add(r,z,'rolled_crown')
for z in np.linspace(.00945,.00705,15)[1:]:add(.0067,z,'insert_seat')
for r,z in bezier([(.0067,.00705),(.0067,.00695),(.0065,.00690),(.0052,.00690)],16)[1:]:add(r,z,'insert_seat_floor')
pitch=P['thread_pitch_working_m'];major=(P['thread_nominal_diameter_m']+P['thread_diametral_clearance_working_m'])/2;minor=major-5*math.sqrt(3)*pitch/16
def thread_r(z,angle=None):
 phase=(z/pitch-(phi if angle is None else angle)/math.tau)%1
 # Original60degree nominal-style profile: flat crests, roots, twoflanks.
 f=np.where(phase<.125,0,np.where(phase<.4375,(phase-.125)/.3125,np.where(phase<.5625,1,np.where(phase<.875,(.875-phase)/.3125,0))))
 nominal=minor+(major-minor)*f
 # Estimated lead-in/runout, not a tolerance-class or physical thread gauge.
 ease=np.clip(np.minimum((z-.00035)/.00055,(.0069-z)/.00055),0,1);return nominal*ease+.0052*(1-ease)
add(.0052,.00035,'lower_thread_boundary')
add(.0053,0,'lower_entry')
def mat(name,c):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.38;return m
gray=mat('Neutral metal geometry - coating pending',(.36,.38,.40));insertgray=mat('Neutral insert geometry - compound pending',(.16,.18,.20))
def mesh_from_profile(name,rings,material):
 rings=[(np.broadcast_to(r,(N,)).astype(float),np.broadcast_to(z,(N,)).astype(float),role)for r,z,role in rings]
 verts=[];faces=[];face_uv=[];arc=[np.zeros(N)]
 for i,(r,z,role)in enumerate(rings):
  verts.extend(np.stack([r*np.cos(phi),r*np.sin(phi),z],-1).tolist())
  if i:arc.append(arc[-1]+np.sqrt((r-rings[i-1][0])**2+(z-rings[i-1][1])**2))
 def addface(indices,coords):faces.append(tuple(indices));face_uv.append(coords)
 has_helix=any(row[2]=='lower_thread_boundary'for row in rings)
 for i,(r,z,role)in enumerate(rings):
  k=(i+1)%len(rings)
  if role=='insert_seat_floor'and rings[k][2]=='lower_thread_boundary':continue
  flat=np.max(abs(z-rings[k][1]))<1e-12 and np.ptp(z)<1e-12
  for j in range(N):
   a=i*N+j;b=i*N+(j+1)%N;c=k*N+(j+1)%N;d=k*N+j
   if flat:
    uv4=[(verts[v][0]/.006,verts[v][1]/.006)for v in[a,b,c,d]]
   else:
    u0=j/N*10;u1=(j+1)/N*10;av=arc[i];bv=arc[k]if k else arc[-1]+np.sqrt((rings[0][0]-rings[-1][0])**2+(rings[0][1]-rings[-1][1])**2);uv4=[(u0,av[j]/.006),(u1,av[(j+1)%N]/.006),(u1,bv[(j+1)%N]/.006),(u0,bv[j]/.006)]
   addface([a,b,c],[uv4[0],uv4[1],uv4[2]]);addface([a,c,d],[uv4[0],uv4[2],uv4[3]])
 helix_report=None
 if has_helix:
  # Constant phase rows follow actual helices, with a shifted cyclic seam.
  # Clamping only the smooth lead-in cylinders permits matching open rings.
  K=P['thread_steps_per_pitch'];assert K%16==0
  zlo=.00035;zhi=.00690;kmin=math.floor(zlo/pitch*K)-K;kmax=math.ceil(zhi/pitch*K)+K
  indices={};zvalues={}
  for k in range(kmin,kmax+1):
   z=np.clip((k/K+np.arange(N)/N)*pitch,zlo,zhi);r=thread_r(z);indices[k]=list(range(len(verts),len(verts)+N));zvalues[k]=z
   verts.extend(np.stack([r*np.cos(phi),r*np.sin(phi),z],-1).tolist())
  helix_face_start=len(faces)
  for k in range(kmin,kmax):
   for j in range(N):
    if j<N-1:
     a=indices[k][j];b=indices[k][j+1];c=indices[k+1][j+1];d=indices[k+1][j];za=zvalues[k][j];zb=zvalues[k][j+1];zc=zvalues[k+1][j+1];zd=zvalues[k+1][j]
    else:
     if k+K+1>kmax:continue
     a=indices[k][j];b=indices[k+K][0];c=indices[k+K+1][0];d=indices[k+1][j];za=zvalues[k][j];zb=zvalues[k+K][0];zc=zvalues[k+K+1][0];zd=zvalues[k+1][j]
    u0=j/N*10;u1=(j+1)/N*10;uv4=[(u0,(zhi-za)/.006),(u1,(zhi-zb)/.006),(u1,(zhi-zc)/.006),(u0,(zhi-zd)/.006)]
    addface([a,d,c],[uv4[0],uv4[3],uv4[2]]);addface([a,c,b],[uv4[0],uv4[2],uv4[1]])
  # Clip the phase grid at the two axial derivative knots of the unchanged
  # author fade function. New points lie on that function; old points stay fixed.
  original_vertices=len(verts);original_positions=hashlib.sha256(np.asarray(verts,dtype=np.float64).tobytes()).hexdigest();cut_reports=[]
  for plane in[zlo+.00055,zhi-.00055]:
   cache={};newfaces=faces[:helix_face_start];newuv=face_uv[:helix_face_start];split_count=0
   def intersection(a,b):
    ia,ua=a;ib,ub=b;va=verts[ia];vb=verts[ib];t=(plane-va[2])/(vb[2]-va[2]);key=(min(ia,ib),max(ia,ib))
    if key not in cache:
     x=va[0]+t*(vb[0]-va[0]);y=va[1]+t*(vb[1]-va[1]);angle=math.atan2(y,x);radius=float(thread_r(plane,angle));cache[key]=len(verts);verts.append([radius*math.cos(angle),radius*math.sin(angle),plane])
    return(cache[key],tuple(ua[q]+t*(ub[q]-ua[q])for q in range(2)))
   def clipped(poly,upper):
    output=[];previous=poly[-1];previous_in=(verts[previous[0]][2]>=plane)if upper else(verts[previous[0]][2]<=plane)
    for current in poly:
     current_in=(verts[current[0]][2]>=plane)if upper else(verts[current[0]][2]<=plane)
     if current_in!=previous_in:output.append(intersection(previous,current))
     if current_in:output.append(current)
     previous,previous_in=current,current_in
    return output
   for face,coords in zip(faces[helix_face_start:],face_uv[helix_face_start:]):
    zs=[verts[v][2]for v in face]
    if min(zs)<plane-1e-12 and max(zs)>plane+1e-12:
     split_count+=1;poly=list(zip(face,coords))
     for upper in[False,True]:
      part=clipped(poly,upper)
      for q in range(1,len(part)-1):
       tri=[part[0],part[q],part[q+1]];newfaces.append(tuple(v[0]for v in tri));newuv.append([v[1]for v in tri])
    else:newfaces.append(face);newuv.append(coords)
   faces,face_uv=newfaces,newuv;cut_reports.append({'exact_axial_plane_m':plane,'split_original_triangles':split_count,'new_shared_intersection_vertices':len(cache),'existing_points_moved':False})
  assert hashlib.sha256(np.asarray(verts[:original_vertices],dtype=np.float64).tobytes()).hexdigest()==original_positions
  helix_report={'phase_steps_per_pitch':K,'angular_segments':N,'shifted_seam_profile_rows':K,'clamped_runout_limits_m':[zlo,zhi],'no_uniform_axial_crest_staircase':True,'axial_runout_boundary_cuts':cut_reports,'original_vertex_positions_preserved':True,'author_radial_function_changed':False}
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(material);uv=mesh.uv_layers.new(name='Estimated6mm reference; helixphase aligned,10circumferential repeats')
 for face,coords in zip(mesh.polygons,face_uv):
  for li,co in zip(face.loop_indices,coords):uv.data[li].uv=co
 # Remove coincident runout rows in the source; no displaced vertices or buffer edits.
 bm=bmesh.new();bm.from_mesh(mesh);before=len(bm.verts);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-9);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-11);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
 if helix_report:helix_report.update({'vertices_before_clamped_row_merge':before,'vertices_after_clamped_row_merge':len(bm.verts),'coincident_merge_distance_m':1e-9})
 bm.to_mesh(mesh);bm.free();mesh.update();mesh.set_sharp_from_angle(angle=.55)
 plane_normals=np.array([[math.cos(a*math.pi/3),math.sin(a*math.pi/3)]for a in range(6)])
 for face in mesh.polygons:
  q=np.array([mesh.vertices[v].co[:]for v in face.vertices]);flat=np.ptp(q[:,2])<1e-10
  face.use_smooth=not flat
  if has_helix:
   distances=abs(q[:,:2]@plane_normals.T-P['across_flats_working_m']/2)
   if np.any(np.max(distances,axis=0)<3e-8):face.use_smooth=False
 mesh.update()
 if not has_helix:
  # Fresh analytical normals for this original rounded annulus only. They keep
  # long straight cylinder sections radial at their tangent fillet junctions.
  vertex_normals=[];eps=2e-8
  for v in mesh.vertices:
   x,y,z=v.co;r=math.hypot(x,y)
   if r>=.0065-eps and z<=.00725+eps:rc,zc=.0065,.00725;nr,nz=r-rc,z-zc
   elif r>=.0065-eps and z>=.0093-eps:rc,zc=.0065,.0093;nr,nz=r-rc,z-zc
   elif r<=.00485+eps and z>=.0093-eps:rc,zc=.00485,.0093;nr,nz=r-rc,z-zc
   elif r<=.00485+eps and z<=.00725+eps:rc,zc=.00485,.00725;nr,nz=r-rc,z-zc
   elif abs(r-.00665)<eps:nr,nz=1.,0.
   elif abs(r-.0047)<eps:nr,nz=-1.,0.
   elif abs(z-.00945)<eps:nr,nz=0.,1.
   elif abs(z-.0071)<eps:nr,nz=0.,-1.
   else:raise AssertionError(('Unclassifiedoriginalinsertsection',r,z))
   scale=math.hypot(nr,nz);nr/=scale;nz/=scale;vertex_normals.append((nr*x/r,nr*y/r,nz))
  for f in mesh.polygons:f.use_smooth=True
  mesh.normals_split_custom_set([vertex_normals[loop.vertex_index]for loop in mesh.loops]);mesh.update()
 o=bpy.data.objects.new(name,mesh);col.objects.link(o)
 if helix_report:o['helical_topology_report']=json.dumps(helix_report)
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
assert max(float(np.max(z))for _,z,_ in profiles)==P['height_working_m']
assert .01673<=float(hex_r.min()*2)<=.01700001 and float(hex_r.max()*2)>=.0189
# Conservative separation: insert is radially inside the seat and above its floor.
assert P['polymer_outer_radius_working_m']<.0067 and min(z for _,z,_ in ins)>.00705
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
bpy.context.view_layer.objects.active=metal
bpy.ops.export_scene.gltf(filepath=str(HERE/'handlebar-mount-nyloc-v3-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
w=bpy.data.worlds.new('Locknut neutral studio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.40
for name,loc,power,size in [('KEY',(.035,.030,.050),.11,.050),('FILL',(-.040,.020,.025),.045,.040),('EDGE',(.020,-.045,.035),.08,.045),('LOWER',(-.025,.030,-.025),.02,.025)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.005))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('NYLOC_CAMERA',bpy.data.cameras.new('NYLOC_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.032,.038,.031);cam.rotation_euler=(Vector((0,0,.005))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.029;cam.data.clip_start=.001;cam.data.clip_end=5
s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'handlebar-mount-nyloc-v3.blend'),compress=True)
r={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'source_sha256':hashlib.sha256((HERE/'handlebar-mount-nyloc-v3.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'handlebar-mount-nyloc-v3-inspection.glb').read_bytes()).hexdigest(),'objects':checks,'analytic_insert_normals_freshly_computed':True,'helical_topology':json.loads(metal['helical_topology_report']),'conditional_family':'DIN985M10,notidentifiedOEMnorm','nominal_targets_m':{'height':P['height_working_m'],'across_flats':P['across_flats_working_m'],'pitch':pitch},'working_thread_major_minor_diameter_m':[major*2,minor*2],'insert_steel_radial_separation_m':.0067-P['polymer_outer_radius_working_m'],'nylon_function_strain_and_preload_verified':False,'current_RDC_identity_verified':False,'art_accepted':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_NYLOC_SOURCE',json.dumps(r))
