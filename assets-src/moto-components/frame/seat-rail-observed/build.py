"""One original 3Dseatmember; section/spine and pose remain boundedestimates."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/frame-seat-rail-observed-v1';P=json.loads((HERE/'parameters.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;col=bpy.data.collections.new('WEWA_FRAME_SEAT_RAIL_ISOLATED');s.collection.children.link(col);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
controls=[Vector(q)for q in P['centreline_bezier_controls_m']]
def curve(t):
 u=1-t;return u**3*controls[0]+3*u*u*t*controls[1]+3*u*t*t*controls[2]+t**3*controls[3]
def derivative(t):
 u=1-t;return 3*u*u*(controls[1]-controls[0])+6*u*t*(controls[2]-controls[1])+3*t*t*(controls[3]-controls[2])
approx=sum((curve((i+1)/1000)-curve(i/1000)).length for i in range(1000));steps=math.ceil(approx/P['path_segment_max_working_m']);samples=[0.];frames={};previousD=None;U=None
for i in range(steps+1):
 t=i/steps;C=curve(t);D=derivative(t).normalized()
 if i:samples.append(samples[-1]+(C-previousC).length)
 if previousD is None:
  U=Vector((1,0,0));U=(U-D*U.dot(D)).normalized()
 else:
  U.rotate(previousD.rotation_difference(D));U=(U-D*U.dot(D)).normalized()
 V=U.cross(D).normalized();frames[samples[-1]]=(C,D,V,U.copy());previousC=C;previousD=D
L=samples[-1]
def section(a):return frames[a][:3]
def boundary(inner):
 wall=P['wall_working_m']if inner else 0;hw=P['outer_width_working_m']/2-wall;hh=P['outer_height_working_m']/2-wall;rad=P['corner_radius_working_m']-wall;out=[]
 for cx,cv,start in[(hw-rad,-hh+rad,-math.pi/2),(hw-rad,hh-rad,0),(-hw+rad,hh-rad,math.pi/2),(-hw+rad,-hh+rad,math.pi)]:
  for k in range(P['angular_corner_steps']+1):
   t=start+math.pi/2*k/P['angular_corner_steps'];out.append((cx+rad*math.cos(t),cv+rad*math.sin(t),math.cos(t),math.sin(t)))
 return out
profiles=[boundary(False),boundary(True)];N=len(profiles[0]);K=len(samples);verts=[];normals=[];ring=[]
for inner in[0,1]:
 side=[]
 for a in samples:
  C,D,V=section(a);U=frames[a][3];indices=[]
  for x,v,nx,nv in profiles[inner]:
   indices.append(len(verts));verts.append(tuple(C+U*x+V*v));normals.append((U*nx+V*nv)*(-1 if inner else 1))
  side.append(indices)
 ring.append(side)
faces=[];uvs=[];fn=[];kinds=[];arcs=[];periods=[]
for inner,profile in enumerate(profiles):
 arc=[0.]
 for j in range(N):arc.append(arc[-1]+math.hypot(profile[(j+1)%N][0]-profile[j][0],profile[(j+1)%N][1]-profile[j][1]))
 repeat=max(1,round(arc[-1]/.02));arcs.append(arc);periods.append(repeat)
 for i in range(K-1):
  for j in range(N):
   f=[ring[inner][i][j],ring[inner][i][(j+1)%N],ring[inner][i+1][(j+1)%N],ring[inner][i+1][j]];uv=[(arc[j]/arc[-1]*repeat,samples[i]/.02),(arc[j+1]/arc[-1]*repeat,samples[i]/.02),(arc[j+1]/arc[-1]*repeat,samples[i+1]/.02),(arc[j]/arc[-1]*repeat,samples[i+1]/.02)]
   if inner:f.reverse();uv.reverse()
   faces.append(f);uvs.append(uv);fn.append(None);kinds.append('inner'if inner else'outer')
for i in[0,K-1]:
 C,D,V=section(samples[i]);normal=D*(-1 if i==0 else 1)
 for j in range(N):
  f=[ring[0][i][j],ring[1][i][j],ring[1][i][(j+1)%N],ring[0][i][(j+1)%N]]
  if i==0:f.reverse()
  faces.append(f);uvs.append([((Vector(verts[v])-C).dot(frames[samples[i]][3])/.02,(Vector(verts[v])-C).dot(V)/.02)for v in f]);fn.append(normal);kinds.append('joining_annulus')
mesh=bpy.data.meshes.new('Original3D cubicseatspine with transported hollowroundedsection');mesh.from_pydata(verts,[],faces);mesh.update();assert not mesh.validate(clean_customdata=False);bm=bmesh.new();bm.from_mesh(mesh);vol=bm.calc_volume(signed=True)
if vol<0:
 for f in bm.faces:f.normal_flip()
 bm.to_mesh(mesh)
bm.free();mesh.update();uv=mesh.uv_layers.new(name='Continuous estimated20mm longitudinal and integerperimeter charts');custom=[]
for f,values,n in zip(mesh.polygons,uvs,fn):
 # If winding was corrected, UVmust follow corneridentity instead of originalorder.
 original=faces[f.index];lookup={v:t for v,t in zip(original,values)};f.use_smooth=n is None
 for li in f.loop_indices:
  vid=mesh.loops[li].vertex_index;uv.data[li].uv=lookup[vid];custom.append(normals[vid]if n is None else n)
mesh.normals_split_custom_set(custom);mesh.update();o=bpy.data.objects.new('One observedface seatmember - conditionalsection andside',mesh);col.objects.link(o);o['component_id']=P['component_id'];o['all_physical_dimensions_estimated']=True;o['opposite_rail_built']=False;o['analytical_normals_intentional']=True
m=bpy.data.materials.new('Neutral seatmember G3');m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(.28,.30,.33,1);q.inputs['Roughness'].default_value=.3;mesh.materials.append(m);mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh);nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);euler=len(bm.verts)-len(bm.edges)+len(bm.faces);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;todo=[unseen.pop()]
 while todo:
  for ed in todo.pop().link_edges:
   for v in ed.verts:
    if v in unseen:unseen.remove(v);todo.append(v)
bm.free();areas=[(mesh.vertices[t.vertices[1]].co-mesh.vertices[t.vertices[0]].co).cross(mesh.vertices[t.vertices[2]].co-mesh.vertices[t.vertices[0]].co).length/2 for t in mesh.loop_triangles];error=max((mesh.corner_normals[k].vector-n).length for k,n in enumerate(custom));assert nm==0 and shells==1 and euler==0 and vol>0 and min(areas)>1e-18 and error<.002,(nm,shells,euler,vol,min(areas),error)
tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[list(t.vertices)for t in mesh.loop_triangles],all_triangles=True);probes=[]
for label,a,outward in [('frontjoiningopening',samples[0],-1),('rearjoiningopening',samples[-1],1)]:
 C,D,V=section(a);origin=C+D*outward*.010;direction=-D*outward;distance=.025;hit=tree.ray_cast(origin,direction,distance)[0];assert hit is None;probes.append({'label':label,'origin_m':list(origin),'direction':list(direction),'distance_m':distance,'clear':True})
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;export=HERE/'frame-seat-rail-observed-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
w=bpy.data.worlds.new('Seatmember neutralstudio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,loc,power,size in[('KEY',(.45,.35,.35),8,.35),('FILL',(-.35,.30,.20),4,.30),('EDGE',(.12,-.25,.20),5,.30)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;x=bpy.data.objects.new(name,d);studio.objects.link(x);x.location=loc;x.rotation_euler=(Vector((.018,.34,.025))-x.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('SEAT_RAIL_CAMERA',bpy.data.cameras.new('SEAT_RAIL_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.70,.10,.30);cam.rotation_euler=(Vector((.018,.34,.025))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.85;cam.data.clip_start=.001;cam.data.clip_end=5;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';source=HERE/'frame-seat-rail-observed-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
r={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'connected_shells':shells,'nonmanifold_edges':nm,'Euler_characteristic':euler,'signed_volume_m3':vol,'minimum_triangle_area_m2':min(areas),'zero_area_triangles_at_1e18_m2':sum(v<=1e-18 for v in areas),'maximum_custom_normal_vector_error':error,'normal_error_note':'Fresh authorsectionnormals vs digitalcompactencoding, no OEMtolerance','sweep_arclength_m_estimated':L,'section_perimeter_m_estimated':[a[-1]for a in arcs],'section_UV_repeat_counts':periods,'path_sections':K,'profile_samples':N,'joining_opening_probes':probes,'normal_frame_method':'Discrete rotation-minimizing transport via successive tangentquaternions, sectionfield freshlyassigned','analytical_normals_intentional':True,'opposite_rail_built':False,'all_physical_dimensions_estimated':True,'art_accepted':False};(OUT/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_SEAT_RAIL_G3',json.dumps(r))
