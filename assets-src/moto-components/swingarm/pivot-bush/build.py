"""Original native DP171006-related three-envelope candidate, no imported geometry.
All metrics/reverse sections are estimated; no certified bonded or press-fit model.
"""
import bpy,bmesh,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/swingarm-pivot-bush-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;col=bpy.data.collections.new(P['collection']);s.collection.children.link(col);studio=bpy.data.collections.new('LOCAL_NEUTRAL_STUDIO_NOT_EXPORT');s.collection.children.link(studio);rows=[]

def ring(name,L,ro,ri,c):
 assert 0<c<min(L/2,(ro-ri)/2);profile=[];normal=[]
 for x,r,a in [(L/2-c,ri+c,-math.pi/2),(L/2-c,ro-c,0),(-L/2+c,ro-c,math.pi/2),(-L/2+c,ri+c,math.pi)]:
  for k in range(P['corner_arc_samples']+1):
   t=a+k/P['corner_arc_samples']*math.pi/2;profile.append((x+c*math.cos(t),r+c*math.sin(t)));normal.append((math.cos(t),math.sin(t)))
 arc=[0.]
 for a,b in zip(profile,profile[1:]+profile[:1]):arc.append(arc[-1]+math.dist(a,b))
 N=P['radial_sectors'];U=max(1,round(math.tau*ro/.005));W=max(1,round(arc[-1]/.005));v=[];vn=[];faces=[];uv=[];corn=[]
 for (x,r),(nx,nr)in zip(profile,normal):
  for k in range(N):
   t=math.tau*k/N;v.append((x,r*math.cos(t),r*math.sin(t)));vn.append((nx,nr*math.cos(t),nr*math.sin(t)))
 for j in range(len(profile)):
  jn=(j+1)%len(profile);v0=arc[j]/arc[-1]*W;v1=arc[j+1]/arc[-1]*W
  for k in range(N):
   kn=(k+1)%N;a,b,c,d=j*N+k,jn*N+k,jn*N+kn,j*N+kn;q=[(k/N*U,v0),(k/N*U,v1),((k+1)/N*U,v1),((k+1)/N*U,v0)]
   for f,us in [((a,b,c),(q[0],q[1],q[2])),((a,c,d),(q[0],q[2],q[3]))]:faces.append(f);uv.extend(us);corn.extend(vn[i]for i in f)
 m=bpy.data.meshes.new(name+' original rounded annular section');m.from_pydata(v,[],faces);m.update();assert not m.validate(clean_customdata=False);m.polygons.foreach_set('use_smooth',np.ones(len(faces),bool));u=m.uv_layers.new(name='Periodic physical working tile');u.data.foreach_set('uv',np.array(uv,np.float32).ravel());m.normals_split_custom_set(corn);m.update();m.calc_loop_triangles();areas=[t.area for t in m.loop_triangles];bm=bmesh.new();bm.from_mesh(m);nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free();assert not nm and vol>0 and min(areas)>1e-18;o=bpy.data.objects.new(name,m);col.objects.link(o);o['component_id']=P['component_id'];o['all_metrics_estimated']=True;o['unseen_reverse_provisional']=True;mat=bpy.data.materials.new(name+' neutral gray geometry only');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.20,.21,.23,1);p.inputs['Roughness'].default_value=.30;m.materials.append(mat);rows.append({'object':name,'vertices':len(v),'triangles':len(faces),'connected_shells':1,'nonmanifold_edges':nm,'signed_volume_m3':vol,'minimum_triangle_area_m2':min(areas),'working_length_m':L,'working_outer_radius_m':ro,'working_inner_radius_m':ri,'rounded_corner_m':P['outer_corner_radius_m_estimated']if name=='Outer clear envelope'else P['inner_corner_radius_m_estimated']if name=='Inner pierced clear sleeve'else P['rubber_corner_radius_m_estimated'],'UV_integer_circumferential_repeats':U,'UV_integer_profile_repeats':W,'UV_outer_reference_tile_m':math.tau*ro/U,'UV_profile_tile_m':arc[-1]/W,'UV_radii_vary_so_circumferential_scale_varies_locally':True});return o
ro=P['working_outer_diameter_m_estimated']/2;ri=ro-P['outer_wall_m_estimated'];innerro=P['working_inner_sleeve_outer_diameter_m_estimated']/2;innerbore=P['working_inner_bore_m_estimated']/2
ring('Outer clear envelope',P['working_outer_length_m_estimated'],ro,ri,P['outer_corner_radius_m_estimated']);ring('Dark annulus',P['working_rubber_length_m_estimated'],ri,innerro,P['rubber_corner_radius_m_estimated']);ring('Inner pierced clear sleeve',P['working_inner_sleeve_length_m_estimated'],innerro,innerbore,P['inner_corner_radius_m_estimated'])
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.max_bounces=8;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1000;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.8;s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.20,.23,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
for name,loc,power,size in [('KEY',(.10,-.08,.12),.65,.10),('FILL',(-.08,-.05,.03),.25,.08),('EDGE',(.04,.10,.08),.45,.08),('LOWER',(.08,.07,-.07),.15,.07)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(name,l);studio.objects.link(o);o.location=loc;o.rotation_euler=(-Vector(loc)).to_track_quat('-Z','Y').to_euler()
c=bpy.data.cameras.new('Pivot bush isolated camera');cam=bpy.data.objects.new('CAMERA',c);studio.objects.link(cam);s.camera=cam;cam.location=(.075,-.075,.055);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=.055;c.clip_start=.001;c.clip_end=5
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
bpy.context.view_layer.objects.active=col.objects[0];bpy.ops.export_scene.gltf(filepath=str(H/'swingarm-pivot-bush-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True);bpy.ops.wm.save_as_mainfile(filepath=str(H/'swingarm-pivot-bush-v1.blend'),compress=True);report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(H/'swingarm-pivot-bush-v1.blend'),'export_sha256':sha(H/'swingarm-pivot-bush-inspection.glb'),'objects':rows,'triangles':sum(r['triangles']for r in rows),'closed_solids':3,'intentional_touching_cylindrical_boundaries':True,'bonding_materials_or_stiffness_measured':False,'current_RDC_identity_verified':False,'all_metric_parameters_estimated':True,'external_libraries':[l.filepath for l in bpy.data.libraries],'art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(H/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('PIVOT_BUSH_SOURCE',json.dumps(report))
