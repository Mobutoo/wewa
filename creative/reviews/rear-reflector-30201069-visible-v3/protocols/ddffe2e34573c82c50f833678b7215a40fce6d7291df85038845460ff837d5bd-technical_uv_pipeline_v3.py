"""Boyle SAME reflector, face material correction. Never modify/rebuild mesh or frozenV1."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion
from bpy_extras.object_utils import world_to_camera_view
H=Path(__file__).resolve().parent;R=H.parents[2];P=json.loads((H/'parameters-v3.json').read_text());rev=P['revision'];O=R/'creative/reviews'/rev;Q=R/'creative/research'/rev;stage=sys.argv[sys.argv.index('--')+1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
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
src=R/P['source_v2']if stage=='chart'else H/(rev+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);s=setup();ob=bpy.data.objects['EXTERIOR_CHILD'];m=ob.data;before=fingerprint(ob);frame_before=material_signature(m.materials[1]);face_before=material_signature(m.materials[0])
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

def native_snapshot():
 m.calc_loop_triangles()
 rows=[]
 for t in m.loop_triangles:
  rows.append(dict(material=t.material_index,vertices=list(t.vertices),corners=[[*m.vertices[m.loops[li].vertex_index].co,*m.corner_normals[li].vector]for li in t.loops]))
 return dict(rows=rows,world=[list(r)for r in ob.matrix_world],faceUV=[[p.index,[list(m.uv_layers.active.data[li].uv)for li in p.loop_indices]]for p in m.polygons if p.material_index==0],materials=[material_signature(mat)for mat in m.materials])
if stage=='chart':
 baseline=native_snapshot();oldUV=[list(u.uv)for u in m.uv_layers.active.data];charts={};changed=0
 for poly in m.polygons:
  if poly.material_index!=1:continue
  axis=max(range(3),key=lambda a:abs(poly.normal[a]));a,b=[(1,2),(2,0),(0,1)][axis];sign=1 if poly.normal[axis]>=0 else -1
  charts[str(axis)+('+'if sign>0 else '-')]=charts.get(str(axis)+('+'if sign>0 else '-'),0)+1
  for li in poly.loop_indices:
   co=m.vertices[m.loops[li].vertex_index].co
   # Native loop UV only: separated dominant-face charts, shared metric scale .08m.
   m.uv_layers.active.data[li].uv=(sign*co[a]/.08+axis*2+.5,co[b]/.08+(0 if sign>0 else 2)+.5)
   changed+=list(m.uv_layers.active.data[li].uv)!=oldUV[li]
 assert native_snapshot()==baseline,'Geometry, normal, faceUV, matrix or material changed'
 newUV=[list(u.uv)for u in m.uv_layers.active.data];assert changed>0
 write('native-unchanged-baseline.json',baseline)
 write('native-UV-rechart.json',dict(frame_loop_UVs_changed=changed,charts=charts,method='dominant polygon normal; X:Y/Z, Y:Z/X, Z:X/Y; stable sign/tile; native mesh loop UV only',before_UV=oldUV,after_UV=newUV,faceUV_materials_normals_geometry_exact=True))
 # Relink authored image paths to own immutable package without changing packed image bytes/nodes.
 for im in bpy.data.images:
  if im.source=='FILE' and Path(im.filepath).name in ['original-staggered-cell-normal.png','original-ruby-appearance-color.png']:im.filepath='//'+Path(im.filepath).name
 assert native_snapshot()==baseline
 bpy.ops.wm.save_as_mainfile(filepath=str(H/(rev+'.blend')),compress=True)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.gltf(filepath=str(H/(rev+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True,export_animations=False)
 write('native-export-report.json',dict(source_sha256=sha(H/(rev+'.blend')),GLB_sha256=sha(H/(rev+'.glb')),native_snapshot_exact=True,official_export=True,postexport_changes=False,protocol_sha256=sha(Path(__file__))))
elif stage=='reopen':
 assert native_snapshot()==json.loads((O/'native-unchanged-baseline.json').read_text())
 assert [list(u.uv)for u in m.uv_layers.active.data]==json.loads((O/'native-UV-rechart.json').read_text())['after_UV']
 write('source-reopen-check.json',dict(source_sha256=sha(src),geometry_normals_faceUV_materials_exact_V2=True,frameUV_matches_chart=True,source_reopened=True))
elif stage in ['preview','final']:
 assert native_snapshot()==json.loads((O/'native-unchanged-baseline.json').read_text())
 if stage=='final':assert json.loads((O/'preview-review.json').read_text())['actually_read']
 if stage=='preview':views=[render('preview-source-broad','broad'),render('preview-source-compact','compact')]
 else:views=[render('whole-source-broad','broad',samples=96),render('whole-source-compact','compact',samples=96),render('neutral-outdoor','neutral',samples=96)]
 write('render-report.json'if stage=='final'else'preview-render-report.json',dict(component_id=P['component_id'],package=P['package'],source_sha256=sha(src),export_sha256=sha(H/(rev+'.glb')),views=views,geometry_before=before,geometry_after=fingerprint(ob),frame_material_unchanged=material_signature(m.materials[1])==frame_before,exposure=0,gamma=1,calibrated=False,protocol_sha256=sha(Path(__file__))))
else:raise ValueError(stage)
