"""One original hollowcradlerail; section/metricalbends are explicit estimates."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/frame-lower-cradle-rail-v1';P=json.loads((HERE/'parameters.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;col=bpy.data.collections.new('WEWA_FRAME_LOWER_CRADLE_RAIL_ISOLATED');s.collection.children.link(col);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
r=P['bend_radius_working_m'];span=P['span_working_m'];e=P['depth_working_m']-r;mid=span-2*r;L=2*e+math.pi*r+mid;breaks=[0,e,e+math.pi*r/2,e+math.pi*r/2+mid,e+math.pi*r+mid,L];assert e>0 and mid>0
samples=sorted(set([*breaks,*[L*i/math.ceil(L/P['path_segment_max_working_m'])for i in range(math.ceil(L/P['path_segment_max_working_m'])+1)]]))
def section(a):
 if a<=breaks[1]:C=Vector((0,0,-a));D=Vector((0,0,-1))
 elif a<=breaks[2]:t=math.pi+(a-breaks[1])/r;C=Vector((0,r+r*math.cos(t),-e+r*math.sin(t)));D=Vector((0,-math.sin(t),math.cos(t)))
 elif a<=breaks[3]:C=Vector((0,r+a-breaks[2],-e-r));D=Vector((0,1,0))
 elif a<=breaks[4]:t=3*math.pi/2+(a-breaks[3])/r;C=Vector((0,span-r+r*math.cos(t),-e+r*math.sin(t)));D=Vector((0,-math.sin(t),math.cos(t)))
 else:C=Vector((0,span,-e+a-breaks[4]));D=Vector((0,0,1))
 return C,D,Vector((0,-D.z,D.y))
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
  C,D,V=section(a);indices=[]
  for x,v,nx,nv in profiles[inner]:
   indices.append(len(verts));verts.append(tuple(C+Vector((x,0,0))+V*v));normals.append((Vector((nx,0,0))+V*nv)*(-1 if inner else 1))
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
  faces.append(f);uvs.append([(verts[v][0]/.02,Vector(verts[v]).dot(V)/.02)for v in f]);fn.append(normal);kinds.append('joining_annulus')
mesh=bpy.data.meshes.new('Continuous two bends original hollow roundedsection sweep');mesh.from_pydata(verts,[],faces);mesh.update();assert not mesh.validate(clean_customdata=False);bm=bmesh.new();bm.from_mesh(mesh);vol=bm.calc_volume(signed=True)
if vol<0:
 for f in bm.faces:f.normal_flip()
 bm.to_mesh(mesh)
bm.free();mesh.update();uv=mesh.uv_layers.new(name='Continuous estimated20mm longitudinal and integerperimeter charts');custom=[]
for f,values,n in zip(mesh.polygons,uvs,fn):
 # If winding was corrected, UVmust follow corneridentity instead of originalorder.
 original=faces[f.index];lookup={v:t for v,t in zip(original,values)};f.use_smooth=n is None
 for li in f.loop_indices:
  vid=mesh.loops[li].vertex_index;uv.data[li].uv=lookup[vid];custom.append(normals[vid]if n is None else n)
mesh.normals_split_custom_set(custom);mesh.update();o=bpy.data.objects.new('One observedface lowercradlerail - conditionalsection',mesh);col.objects.link(o);o['component_id']=P['component_id'];o['all_physical_dimensions_estimated']=True;o['opposite_rail_built']=False;o['analytical_normals_intentional']=True
m=bpy.data.materials.new('Neutral cradle G3');m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(.28,.30,.33,1);q.inputs['Roughness'].default_value=.3;mesh.materials.append(m);mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh);nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);euler=len(bm.verts)-len(bm.edges)+len(bm.faces);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;todo=[unseen.pop()]
 while todo:
  for ed in todo.pop().link_edges:
   for v in ed.verts:
    if v in unseen:unseen.remove(v);todo.append(v)
bm.free();areas=[(mesh.vertices[t.vertices[1]].co-mesh.vertices[t.vertices[0]].co).cross(mesh.vertices[t.vertices[2]].co-mesh.vertices[t.vertices[0]].co).length/2 for t in mesh.loop_triangles];error=max((mesh.corner_normals[k].vector-n).length for k,n in enumerate(custom));assert nm==0 and shells==1 and euler==0 and vol>0 and min(areas)>1e-18 and error<.001,(nm,shells,euler,vol,min(areas),error)
tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[list(t.vertices)for t in mesh.loop_triangles],all_triangles=True);probes=[]
for y in[0,span]:
 hit=tree.ray_cast(Vector((0,y,.010)),Vector((0,0,-1)),.030)[0];assert hit is None;probes.append({'label':'frontjoiningopening'if y==0 else'rearjoiningopening','origin_m':[0,y,.010],'direction':[0,0,-1],'distance_m':.030,'clear':True})
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;export=HERE/'frame-lower-cradle-rail-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
w=bpy.data.worlds.new('Cradle neutralstudio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,loc,power,size in[('KEY',(.25,.15,.15),2,.18),('FILL',(-.20,.15,.02),1,.20),('EDGE',(.12,-.15,-.02),1,.18)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;x=bpy.data.objects.new(name,d);studio.objects.link(x);x.location=loc;x.rotation_euler=(Vector((0,.12,-.045))-x.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('CRADLE_CAMERA',bpy.data.cameras.new('CRADLE_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.35,.05,.15);cam.rotation_euler=(Vector((0,.12,-.045))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.34;cam.data.clip_start=.001;cam.data.clip_end=5;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';source=HERE/'frame-lower-cradle-rail-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
r={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'connected_shells':shells,'nonmanifold_edges':nm,'Euler_characteristic':euler,'signed_volume_m3':vol,'minimum_triangle_area_m2':min(areas),'zero_area_triangles_at_1e18_m2':sum(v<=1e-18 for v in areas),'maximum_custom_normal_vector_error':error,'normal_error_note':'Digital compactnormalencoding, no OEMtolerance','sweep_arclength_m_estimated':L,'section_perimeter_m_estimated':[a[-1]for a in arcs],'section_UV_repeat_counts':periods,'path_sections':K,'profile_samples':N,'joining_opening_probes':probes,'analytical_normals_intentional':True,'opposite_rail_built':False,'all_physical_dimensions_estimated':True,'art_accepted':False};(OUT/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_CRADLE_G3',json.dumps(r))
