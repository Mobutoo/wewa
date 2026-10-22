"""Boyle SAME reflector, face material correction. Never modify/rebuild mesh or frozenV1."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion
from bpy_extras.object_utils import world_to_camera_view
H=Path(__file__).resolve().parent;R=H.parents[2];P=json.loads((H/'parameters-v2.json').read_text());rev=P['revision'];O=R/'creative/reviews'/rev;Q=R/'creative/research'/rev;stage=sys.argv[sys.argv.index('--')+1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(O/n).write_text(json.dumps(v,indent=2)+'\n')
def material_signature(mat):
 nodes=[]
 for n in mat.node_tree.nodes:
  inputs=[]
  for sock in n.inputs:
   if not hasattr(sock,'default_value'):continue
   v=sock.default_value
   if hasattr(v,'__len__')and not isinstance(v,str):v=list(v)
   if not isinstance(v,(str,list,int,float,bool,type(None))):v=str(v)
   inputs.append([sock.identifier,v])
  nodes.append([n.name,n.bl_idname,inputs,getattr(getattr(n,'image',None),'name',None)])
 links=sorted([l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier]for l in mat.node_tree.links)
 return hashlib.sha256(json.dumps(dict(name=mat.name,use_backface_culling=mat.use_backface_culling,nodes=nodes,links=links),sort_keys=True).encode()).hexdigest()
def fingerprint(ob):
 m=ob.data;m.calc_loop_triangles();tri=[];parts={0:[],1:[]}
 for t in m.loop_triangles:
  row=[t.material_index,list(t.vertices),[[*m.vertices[m.loops[li].vertex_index].co,*m.corner_normals[li].vector,*m.uv_layers.active.data[li].uv]for li in t.loops]];tri.append(row);parts[t.material_index].append(row)
 enc=lambda a:hashlib.sha256(json.dumps(a,separators=(',',':')).encode()).hexdigest()
 return dict(all=enc(tri),face=enc(parts[0]),frame=enc(parts[1]),world=enc([list(r)for r in ob.matrix_world]),vertices=len(m.vertices),triangles=len(tri))
def setup():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.max_bounces=6;s.render.threads_mode='FIXED';s.render.threads=2;s.view_layers[0].cycles.denoising_store_passes=True;s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1;bpy.context.preferences.filepaths.save_version=0;return s
src=R/P['source_v1']if stage in ['diagnostic','material']else H/(rev+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);s=setup();ob=bpy.data.objects['EXTERIOR_CHILD'];m=ob.data;before=fingerprint(ob);frame_before=material_signature(m.materials[1]);face_before=material_signature(m.materials[0])
def lighting(kind):
 for l in bpy.data.lights:l.energy=0
 world=bpy.data.worlds.new('Boyle V2 '+kind);world.use_nodes=True;nt=world.node_tree;nt.nodes['Background'].inputs[0].default_value=(.10,.10,.10,1);nt.nodes['Background'].inputs[1].default_value=.35;s.world=world
 if kind=='neutral':
  env=nt.nodes.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(str(R/'app/public/materials/kloppenheim_06_puresky_1k.hdr'));nt.links.new(env.outputs['Color'],nt.nodes['Background'].inputs[0]);nt.nodes['Background'].inputs[1].default_value=.65;return
 for label,pos,power,size in [('Key',(-.065,-.08,.13),1.28,.088),('Fill',(.08,.024,.067),.32,.072),('Rim',(-.048,.08,-.037),.45,.056)]:
  if kind=='compact'and label!='Key':continue
  l=bpy.data.lights.new('V2 '+kind+' '+label,'POINT'if kind=='compact'else'AREA');l.energy=power
  if kind=='compact':l.shadow_soft_size=.001
  else:l.shape='RECTANGLE';l.size=size;l.size_y=size*.6
  o=bpy.data.objects.new(l.name,l);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.003))-o.location).to_track_quat('-Z','Y').to_euler()
def camera(source=True,front=False):
 c=s.camera;cfg=P['source_camera'];c.data.type='ORTHO';c.data.ortho_scale=.123;c.data.clip_start=.0001;c.data.clip_end=10;c.location=Vector([0,0,.26]if front else cfg['eye_m']if source else [.08,-.1,.227]);q=(Vector((0,0,.003))-c.location).to_track_quat('-Z','Y');roll=cfg['roll_deg']if source and not front else 0;c.rotation_euler=(q@Quaternion((0,0,1),math.radians(roll))).to_euler();bpy.context.view_layer.update();return dict(eye=list(c.location),target=[0,0,.003],roll_deg=roll,projection='ORTHO',ortho_scale_m=c.data.ortho_scale)
def render(name,light,source=True,samples=16,front=False):
 lighting(light);pose=camera(source,front);s.cycles.samples=samples;pts=[world_to_camera_view(s,s.camera,ob.matrix_world@Vector(v))for v in ob.bound_box];fr=dict(min=[min(v[i]for v in pts)for i in range(3)],max=[max(v[i]for v in pts)for i in range(3)]);assert min(fr['min'][:2])>.02 and max(fr['max'][:2])<.98
 raw=O/'raw';raw.mkdir(exist_ok=True);s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(raw/(name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s)
 assert fingerprint(ob)==before
 return dict(name=name,samples=samples,resolution_px=[900,700],camera=pose,light=light,framing=fr,PNG_sha256=sha(O/(name+'.png')),raw_sha256=sha(raw/(name+'.exr')))
if stage=='diagnostic':
 views=[render('G2-v1-old-angle-broad','broad',False),render('G2-v1-source-angle-broad','broad'),render('G2-v1-source-angle-compact','compact')]
 assert material_signature(m.materials[0])==face_before and material_signature(m.materials[1])==frame_before
 write('G2-diagnostic-report.json',dict(component_id=P['component_id'],package=P['package'],source_sha256=sha(src),geometry_before=before,geometry_after=fingerprint(ob),frame_material_before=frame_before,frame_material_after=material_signature(m.materials[1]),v1_face_material_unchanged=True,views=views,calibrated=False,protocol_sha256=sha(Path(__file__))))
elif stage=='material':
 assert json.loads((O/'G2-diagnostic-review.json').read_text())['actually_read']
 face=m.materials[0];face.name='Original V2 staggered apparent ruby cells';nt=face.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled');nt.links.new(bs.outputs[0],out.inputs[0]);bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=P['material_candidate']['roughness'];bs.inputs['Coat Weight'].default_value=.55;bs.inputs['Coat Roughness'].default_value=.12
 N=P['material_candidate']['normal_resolution'];npix=[];cpix=[];cols=36;rows=22.5
 for y in range(N):
  q=(y+.5)/N*rows;row=math.floor(q);dy=q-row-.5
  for x in range(N):
   p=(x+.5)/N*cols-.5*(row%2);dx=p-math.floor(p)-.5
   # Offset lattice of rounded apparent optical cells, material normals only, no optical-prism mesh.
   xx=dx/.48;yy=dy/.48;rr=math.sqrt(xx*xx+yy*yy);edge=max(0,min(1,(1.08-rr)/.14));a=.42*edge
   nx=a*math.sin(math.pi*xx*.8);ny=a*math.sin(math.pi*yy*.8);nz=math.sqrt(max(.01,1-nx*nx-ny*ny));npix.extend((nx*.5+.5,ny*.5+.5,nz*.5+.5,1))
   # Authored colour response, not a sampled/albedo measurement of the JPEG.
   gutter=.48+.52*min(1,max(0,(1.02-rr)/.20));seed=(math.sin((math.floor(p)+1)*12.9898+(row+1)*78.233)*43758.5453)%1;variation=.92+.16*seed;col=P['material_candidate']['color_linear'];cpix.extend((col[0]*gutter*variation,col[1]*gutter,col[2]*gutter,1))
 def image(name,pixels,path,colorspace):
  im=bpy.data.images.new(name,width=N,height=N,alpha=True);im.colorspace_settings.name=colorspace;im.pixels=pixels;im.file_format='PNG';im.filepath_raw=str(H/path);im.save();im.pack();return im
 norm=image('V2 authored staggered cell NORMAL',npix,'original-staggered-cell-normal.png','Non-Color');color=image('V2 authored ruby appearance COLOR',cpix,'original-ruby-appearance-color.png','Non-Color')
 tex=nt.nodes.new('ShaderNodeTexImage');tex.image=norm;nm=nt.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.75;nt.links.new(tex.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs[0],bs.inputs['Normal']);nt.links.new(nm.outputs[0],bs.inputs['Coat Normal']);ct=nt.nodes.new('ShaderNodeTexImage');ct.image=color;nt.links.new(ct.outputs['Color'],bs.inputs['Base Color'])
 assert fingerprint(ob)==before and material_signature(m.materials[1])==frame_before
 ob['component_id']=P['component_id'];ob['package']=P['package'];ob['same_physical_specimen_material_revision']=True;camera();lighting('broad');s.cycles.samples=96;bpy.ops.wm.save_as_mainfile(filepath=str(H/(rev+'.blend')),compress=True)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.gltf(filepath=str(H/(rev+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True,export_animations=False)
 # Native export parity rows and explicit UV/tangent data for USED normal chart.
 m.calc_loop_triangles();native=[];minUV=1.;faceTris=0
 for t in m.loop_triangles:
  corners=[];uv=[]
  for li in t.loops:
   v=m.vertices[m.loops[li].vertex_index].co;n=m.corner_normals[li].vector;u=m.uv_layers.active.data[li].uv;corners.append([v.x,v.z,-v.y,n.x,n.z,-n.y,u.x,1-u.y]);uv.append(tuple(u))
  native.append(corners)
  if t.material_index==0:
   area=abs((uv[1][0]-uv[0][0])*(uv[2][1]-uv[0][1])-(uv[1][1]-uv[0][1])*(uv[2][0]-uv[0][0]))/2;minUV=min(minUV,area);faceTris+=1
 assert minUV>1e-12
 write('native-corners.json',dict(triangles=native,world_matrix=[list(r)for r in ob.matrix_world],axis_map='x,z,-y;UVvflip',component_id=P['component_id']))
 write('geometry-material-parity.json',dict(component_id=P['component_id'],package=P['package'],source_v1_sha256=P['source_v1_sha256'],source_v2_sha256=sha(H/(rev+'.blend')),export_v2_sha256=sha(H/(rev+'.glb')),before=before,after=fingerprint(ob),frame_material_before=frame_before,frame_material_after=material_signature(m.materials[1]),face_and_frame_positions_triangles_normals_UV_world_exact=True,frame_material_exact=True,used_face_UV_triangles=faceTris,used_face_min_UVarea=minUV,hidden_geometry_added=False,normalmap_role='Original apparent cells only, no mesh corrections/prisms',protocol_sha256=sha(Path(__file__))))
elif stage in ['preview','final']:
 if stage=='final':assert json.loads((O/'preview-review.json').read_text())['actually_read']
 if stage=='preview':views=[render('preview-source-broad','broad'),render('preview-source-compact','compact')]
 else:views=[render('whole-source-broad','broad',samples=96),render('whole-source-compact','compact',samples=96),render('neutral-outdoor','neutral',samples=96)]
 write('render-report.json'if stage=='final'else'preview-render-report.json',dict(component_id=P['component_id'],package=P['package'],source_sha256=sha(src),export_sha256=sha(H/(rev+'.glb')),views=views,geometry_before=before,geometry_after=fingerprint(ob),frame_material_unchanged=material_signature(m.materials[1])==frame_before,exposure=0,gamma=1,calibrated=False,protocol_sha256=sha(Path(__file__))))
else:raise ValueError(stage)
