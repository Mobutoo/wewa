"""Original finite redshell candidate from officialviews; hiddenmount pattern absent."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/front-mudguard-shell-v1';P=json.loads((HERE/'parameters.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;col=bpy.data.collections.new('WEWA_FRONT_MUDGUARD_SHELL_ISOLATED');s.collection.children.link(col);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
A=P['longitudinal_sections'];B=P['transverse_sections'];E=P['edge_arc_sections'];th=P['sheet_thickness_working_m'];R=P['crown_radius_working_m'];drop=P['transverse_crown_drop_working_m']
def surface(t,v):
 phi=v*math.pi/2;start=math.radians(P['front_centre_angle_deg']+P['front_side_setback_angle_deg_estimated']*v*v);end=math.radians(P['rear_centre_angle_deg']-P['rear_side_setback_angle_deg_estimated']*v*v);theta=start+(end-start)*t;hw=P['maximum_width_working_m']/2*(.92+.08*math.sin(math.pi*t));radius=R-drop*(1-math.cos(phi));return Vector((hw*math.sin(phi),radius*math.sin(theta),radius*math.cos(theta)))
def frame(t,v):
 h=1e-5;u=(surface(t+h,v)-surface(t-h,v))/(2*h);q=(surface(t,v+h)-surface(t,v-h))/(2*h);return q.cross(u).normalized()
verts=[];surfaceN=[]
for i in range(A+1):
 for j in range(B+1):
  t=i/A;v=-1+2*j/B;verts.append(tuple(surface(t,v)));surfaceN.append(frame(t,v))
N=len(verts);verts.extend(tuple(Vector(q)-th*n)for q,n in zip(verts[:],surfaceN));faces=[];kinds=[];uvs=[];fn=[];estimatedL=R*math.radians(P['rear_centre_angle_deg']-P['front_centre_angle_deg']);crossL=math.pi*(P['maximum_width_working_m']/2+drop)/2
for inner in[0,1]:
 for i in range(A):
  for j in range(B):
   f=[i*(B+1)+j,i*(B+1)+j+1,(i+1)*(B+1)+j+1,(i+1)*(B+1)+j];uv=[(j/B*crossL/.02,i/A*estimatedL/.02),((j+1)/B*crossL/.02,i/A*estimatedL/.02),((j+1)/B*crossL/.02,(i+1)/A*estimatedL/.02),(j/B*crossL/.02,(i+1)/A*estimatedL/.02)];f=[k+inner*N for k in f]
   if inner:f.reverse();uv.reverse()
   faces.append(f);uvs.append(uv);fn.append(None);kinds.append('inner'if inner else'outer')
# Boundary follows orientedoutercap, preserving sharedvertices all the way around.
boundary=[j for j in range(B+1)]+[i*(B+1)+B for i in range(1,A+1)]+[A*(B+1)+j for j in range(B-1,-1,-1)]+[i*(B+1)for i in range(A-1,0,-1)];Q=len(boundary);assert len(set(boundary))==Q
arc=[0.]
for k in range(Q):arc.append(arc[-1]+(Vector(verts[boundary[(k+1)%Q]])-Vector(verts[boundary[k]])).length)
repeats=max(1,round(arc[-1]/.02));rings=[boundary];edgeNormals={};conormal=[]
for k,vid in enumerate(boundary):
 tangent=(Vector(verts[boundary[(k+1)%Q]])-Vector(verts[boundary[(k-1)%Q]])).normalized();n=surfaceN[vid];conormal.append(tangent.cross(n).normalized())
for j in range(1,E):
 a=math.pi*j/E;ring=[]
 for k,vid in enumerate(boundary):
  n=surfaceN[vid];b=conormal[k];c=Vector(verts[vid])-th/2*n;nn=(math.cos(a)*n+math.sin(a)*b).normalized();ring.append(len(verts));edgeNormals[len(verts)]=nn;verts.append(tuple(c+th/2*nn))
 rings.append(ring)
rings.append([v+N for v in boundary])
for j in range(E):
 for k in range(Q):
  n=(k+1)%Q;f=[rings[j][n],rings[j][k],rings[j+1][k],rings[j+1][n]];u0,u1=arc[k]/arc[-1]*repeats,arc[k+1]/arc[-1]*repeats;v0,v1=j/E*math.pi*th/2/.02,(j+1)/E*math.pi*th/2/.02;faces.append(f);uvs.append([(u1,v0),(u0,v0),(u0,v1),(u1,v1)]);fn.append('edge');kinds.append('rounded_boundary')
mesh=bpy.data.meshes.new('Original dense doublecurved sheet with finite roundedperimeter');mesh.from_pydata(verts,[],faces);mesh.update();assert not mesh.validate(clean_customdata=False);bm=bmesh.new();bm.from_mesh(mesh);vol=bm.calc_volume(signed=True)
if vol<0:
 for f in bm.faces:f.normal_flip()
 bm.to_mesh(mesh)
bm.free();mesh.update()
# Boundarycorner mitres are not a perfect circularsweep: derive ONLY interiorrim
# shading from fresh actualfacefans, retaining analyticbroadcap normals.
acc={vid:Vector((0,0,0))for vid in edgeNormals}
for f,kind in zip(mesh.polygons,kinds):
 if kind!='rounded_boundary':continue
 ids=list(f.vertices)
 for k,vid in enumerate(ids):
  if vid not in acc:continue
  a=(mesh.vertices[ids[k-1]].co-mesh.vertices[vid].co).normalized();b=(mesh.vertices[ids[(k+1)%len(ids)]].co-mesh.vertices[vid].co).normalized();angle=math.acos(max(-1,min(1,a.dot(b))));acc[vid]+=f.normal*angle
edgeNormals={vid:n.normalized()for vid,n in acc.items()}
uv=mesh.uv_layers.new(name='Estimated20mm longitudinal/crosssurface; continuous boundary charts');custom=[]
for f,values,kind in zip(mesh.polygons,uvs,kinds):
 original=faces[f.index];lookup={v:t for v,t in zip(original,values)};f.use_smooth=True
 for li in f.loop_indices:
  vid=mesh.loops[li].vertex_index;uv.data[li].uv=lookup[vid]
  if vid<N:n=surfaceN[vid]
  elif vid<2*N:n=-surfaceN[vid-N]
  else:n=edgeNormals[vid]
  custom.append(n)
mesh.normals_split_custom_set(custom);mesh.update();o=bpy.data.objects.new('Original redfrontmudguard shell - hiddenmounts unresolved',mesh);col.objects.link(o);o['component_id']=P['component_id'];o['all_physical_dimensions_estimated']=True;o['analytical_normals_intentional']=True;o['flap_and_mounts_built']=False
m=bpy.data.materials.new('Neutral fendershell G3');m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(.28,.30,.33,1);q.inputs['Roughness'].default_value=.30;mesh.materials.append(m);mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh);nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);euler=len(bm.verts)-len(bm.edges)+len(bm.faces);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;todo=[unseen.pop()]
 while todo:
  for ed in todo.pop().link_edges:
   for v in ed.verts:
    if v in unseen:unseen.remove(v);todo.append(v)
bm.free();areas=[(mesh.vertices[t.vertices[1]].co-mesh.vertices[t.vertices[0]].co).cross(mesh.vertices[t.vertices[2]].co-mesh.vertices[t.vertices[0]].co).length/2 for t in mesh.loop_triangles];err=max((mesh.corner_normals[k].vector-n).length for k,n in enumerate(custom));normal_face_dots=[mesh.corner_normals[li].vector.dot(f.normal)for f in mesh.polygons for li in f.loop_indices];audit={'normal_error_max':err,'lowest_face_corners':[{'face':f.index,'kind':kinds[f.index],'face_normal':list(f.normal),'positions':[list(mesh.vertices[v].co)for v in f.vertices],'dots':[mesh.corner_normals[li].vector.dot(f.normal)for li in f.loop_indices]}for f in sorted(mesh.polygons,key=lambda f:min(mesh.corner_normals[li].vector.dot(f.normal)for li in f.loop_indices))[:16]]};(OUT/'initial-boundary-normal-diagnostic.json').write_text(json.dumps(audit,indent=2)+'\n');assert nm==0 and shells==1 and euler==2 and vol>0 and min(areas)>1e-18 and err<.002 and min(normal_face_dots)>0,(nm,shells,euler,vol,min(areas),err,min(normal_face_dots))
tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[list(t.vertices)for t in mesh.loop_triangles],all_triangles=True);probes=[]
for name,origin,direction,distance,clear in[('axletransverse_open',(.2,0,0),(-1,0,0),.4,True),('topcrown_material',(0,0,.5),(0,0,-1),.3,False),('frontnose_material',(0,-.15,.5),(0,0,-1),.3,False)]:
 hit=tree.ray_cast(Vector(origin),Vector(direction),distance)[0];assert(hit is None)==clear;probes.append({'label':name,'origin_m':origin,'direction':direction,'distance_m':distance,'clear':clear})
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;export=HERE/'front-mudguard-shell-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
w=bpy.data.worlds.new('Fendershell neutralstudio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,loc,power,size in[('KEY',(.35,-.20,.65),5,.30),('FILL',(-.35,.25,.45),2,.30),('EDGE',(.10,.60,.25),3,.25)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;x=bpy.data.objects.new(name,d);studio.objects.link(x);x.location=loc;x.rotation_euler=(Vector((0,.08,.22))-x.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('FENDER_SHELL_CAMERA',bpy.data.cameras.new('FENDER_SHELL_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.55,-.50,.55);cam.rotation_euler=(Vector((0,.08,.22))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.70;cam.data.clip_start=.001;cam.data.clip_end=5;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';source=HERE/'front-mudguard-shell-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
r={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'connected_shells':shells,'nonmanifold_edges':nm,'Euler_characteristic':euler,'signed_volume_m3':vol,'minimum_triangle_area_m2':min(areas),'zero_area_triangles_at_1e18_m2':sum(v<=1e-18 for v in areas),'maximum_custom_normal_vector_error':err,'minimum_corner_normal_face_normal_dot':min(normal_face_dots),'normal_error_note':'Fresh authorednormals vs Blender compactcornerencoding; bound0.002 vector (~0.115deg) is digital only, smaller than samplingstep, not a universal shading/artistic criterion or OEMtolerance','longitudinal_sections':A,'transverse_sections':B,'finite_edge_arc_sections':E,'edge_UV_repeat_count':repeats,'edge_UV_period_m':arc[-1]/repeats,'surface_outer_vertex_count':N,'inner_face_index_range':[A*B,2*A*B],'probes':probes,'all_physical_dimensions_estimated':True,'hiddenmount_holes_and_brackets_built':False,'flap_built':False,'art_accepted':False};(OUT/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_FENDER_SHELL_G3',json.dumps(r))
