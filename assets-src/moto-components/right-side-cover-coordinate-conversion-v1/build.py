"""Authorized RH convention derivative only. Callable functions; no actions on import."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/workspace/wewa');K='right-side-cover-coordinate-conversion-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;D=R/'creative/research'/K
A=Matrix(((0,0,-1),(1,0,0),(0,1,0)))
NAMES=['RIGHT_COVER_OUTER_SKIN','RIGHT_COVER_LOWER_ROUND_VISIBLE_HEAD_NO_DRIVE_CLAIM']
COLLECTION='WEWA_RIGHT_SIDE_COVER_WORLD_FRAME_V1'
SOURCE=R/'assets-src/moto-components/side-cover-right-v2/child-candidate.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def geometry_digest(m):return hashlib.sha256(repr(([tuple(v.co)for v in m.vertices],[tuple(f.vertices)for f in m.polygons],[[tuple(x.uv)for x in uv.data]for uv in m.uv_layers])).encode()).hexdigest()
def material_proof(ob):
 rows=[]
 for mat in ob.data.materials:
  nodes=[]
  for n in mat.node_tree.nodes:
   inputs={x.identifier:list(x.default_value)if hasattr(x.default_value,'__len__')and not isinstance(x.default_value,str)else x.default_value for x in n.inputs if hasattr(x,'default_value') and isinstance(x.default_value,(float,int,str,bool,list,tuple,Vector))}
   node=dict(name=n.name,type=n.bl_idname,inputs=inputs)
   if n.type=='TEX_IMAGE':
    assert n.image.packed_file;node.update(image=n.image.name,image_sha256=hashlib.sha256(n.image.packed_file.data).hexdigest(),colorspace=n.image.colorspace_settings.name)
   nodes.append(node)
  rows.append(dict(name=mat.name,nodes=nodes,links=[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier)for l in mat.node_tree.links]))
 return rows

def normalize_object(ob):
 assert ob.matrix_world==Matrix.Identity(4);m=ob.data;assert not ob.modifiers
 verts=[v.co.copy()for v in m.vertices];faces=[tuple(p.vertices)for p in m.polygons];m.calc_loop_triangles();tri_before={tuple(sorted(t.vertices))for t in m.loop_triangles}
 normals={(p.index,m.loops[i].vertex_index):m.corner_normals[i].vector.copy()for p in m.polygons for i in p.loop_indices}
 uv_before=[{(p.index,m.loops[i].vertex_index):tuple(uv.data[i].uv)for p in m.polygons for i in p.loop_indices}for uv in m.uv_layers]
 tangent_before={}
 if m.uv_layers:
  m.calc_tangents(uvmap=m.uv_layers.active.name)
  tangent_before={(p.index,m.loops[i].vertex_index):(m.loops[i].tangent.copy(),m.loops[i].bitangent_sign)for p in m.polygons for i in p.loop_indices}
 mats=material_proof(ob)
 for v,old in zip(m.vertices,verts):v.co=A@old
 m.flip_normals();m.update()
 for uv,values in zip(m.uv_layers,uv_before):
  for p in m.polygons:
   for i in p.loop_indices:uv.data[i].uv=values[(p.index,m.loops[i].vertex_index)]
 custom=[None]*len(m.loops)
 for p in m.polygons:
  for i in p.loop_indices:custom[i]=A@normals[(p.index,m.loops[i].vertex_index)]
 m.normals_split_custom_set(custom);m.update();m.calc_loop_triangles()
 max_pos=max((v.co-A@old).length for v,old in zip(m.vertices,verts));max_n=max((m.corner_normals[i].vector-custom[i]).length for i in range(len(custom)))
 assert max_pos<1e-7 and max_n<.0003,(max_pos,max_n)
 assert tri_before=={tuple(sorted(t.vertices))for t in m.loop_triangles},'Original triangle diagonal/connectivity changed'
 for p,f in zip(m.polygons,faces):
  new=list(p.vertices);expected=list(reversed(f));assert any(new==expected[i:]+expected[:i]for i in range(len(f)))
 for uv,values in zip(m.uv_layers,uv_before):
  assert all(tuple(uv.data[i].uv)==values[(p.index,m.loops[i].vertex_index)]for p in m.polygons for i in p.loop_indices)
 max_t=None;max_sign=None
 if tangent_before:
  m.calc_tangents(uvmap=m.uv_layers.active.name)
  max_t=max((m.loops[i].tangent-A@tangent_before[(p.index,m.loops[i].vertex_index)][0]).length for p in m.polygons for i in p.loop_indices)
  max_sign=max(abs(m.loops[i].bitangent_sign+tangent_before[(p.index,m.loops[i].vertex_index)][1])for p in m.polygons for i in p.loop_indices)
  assert max_t<.001 and max_sign<.0001,(max_t,max_sign)
 assert material_proof(ob)==mats
 return dict(object=ob.name,vertices=len(verts),polygons=len(faces),triangles=len(m.loop_triangles),maximum_position_A_error_m=max_pos,maximum_corner_normal_A_error=max_n,original_triangle_vertex_connectivity_preserved=True,winding_reversed_once=True,uv_by_face_vertex_identical=True,maximum_tangent_A_error=max_t,maximum_bitangent_sign_reversal_error=max_sign,tangent_scope='UV skin only; head has no UV and no source normal map, no artificial tangent/UV generated'if not tangent_before else'UV skin: T_new=A*T_old, handedness_new=-handedness_old',materials_before=mats,materials_unchanged=True,geometry_digest=geometry_digest(m))

def studio():
 s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.cycles.max_bounces=5;s.cycles.samples=16;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1000;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_layers[0].cycles.denoising_store_passes=True;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
 w=bpy.data.worlds.new('Neutral derivative review');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.15,.15,.15,1);w.node_tree.nodes['Background'].inputs[1].default_value=.6;s.world=w
 for name,eye,power in [('Key',(-.5,-.25,.4),18),('Fill',(-.4,.35,-.1),9),('Reverse',(.3,.1,.4),9)]:
  l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=.35;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=eye;look(o,(0,0,0))
 cam=bpy.data.objects.new('Review camera',bpy.data.cameras.new('Review camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.45;cam.data.clip_start=.001;cam.data.clip_end=10;cam.location=(-.6,-.12,.18);look(cam,(0,0,0));return s

def look(ob,t):ob.rotation_euler=(Vector(t)-ob.location).to_track_quat('-Z','Y').to_euler()
def export():
 bpy.ops.object.select_all(action='DESELECT')
 for name in NAMES:bpy.data.objects[name].select_set(True)
 bpy.context.view_layer.objects.active=bpy.data.objects[NAMES[0]]
 bpy.ops.export_scene.gltf(filepath=str(H/'child-candidate.glb'),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True,export_animations=False)

def build():
 before=sha(SOURCE);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 col=bpy.data.collections.new(COLLECTION);bpy.context.scene.collection.children.link(col)
 with bpy.data.libraries.load(str(SOURCE),link=False)as(src,dst):dst.objects=list(NAMES)
 rows=[]
 for ob in dst.objects:
  assert ob and not ob.library;col.objects.link(ob);rows.append(normalize_object(ob))
 for im in bpy.data.images:
  if im.source=='FILE':assert im.packed_file,'Derivative must be self-contained'
 studio()
 for lib in list(bpy.data.libraries):
  linked=[x.name for group in [bpy.data.objects,bpy.data.meshes,bpy.data.materials,bpy.data.images,bpy.data.node_groups]for x in group if x.library==lib]
  assert not linked,linked
  bpy.data.libraries.remove(lib)
 assert not bpy.data.libraries
 bpy.context.scene['scope']='Independent normalized RH derivative, zero new physical IDs; old G4/G8 unchanged; no physical fit';bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-candidate.blend'),compress=True);export();assert sha(SOURCE)==before
 write(O/'conversion-check.json',dict(source=str(SOURCE.relative_to(R)),source_sha256=before,A_rows=[list(r)for r in A],determinant=A.determinant(),objects=rows,source_unchanged=True,source_independent=True,object_origins_and_matrices_identity=True,collection=COLLECTION,physical_count_increment=0,art_accepted=False))

def render(mode):
 if mode=='preview':assert json.loads((O/'gray-read.json').read_text())['actually_read']
 if mode=='final':assert json.loads((O/'preview-read.json').read_text())['actually_read']
 bpy.ops.wm.open_mainfile(filepath=str(H/'child-candidate.blend'));s=bpy.context.scene
 before={name:geometry_digest(bpy.data.objects[name].data)for name in NAMES}
 if mode=='gray':
  gray=bpy.data.materials.new('Render-only gray override');gray.use_nodes=True;b=gray.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.18,.18,.18,1);b.inputs['Roughness'].default_value=.32;s.view_layers[0].material_override=gray
 views=[('profile',(-.65,0,0)),('quarter',(-.60,-.18,.18)),('neutral',(-.55,.20,.12))]
 if mode=='preview':views=views[:2]
 rows=[];(O/'raw').mkdir(exist_ok=True)
 for label,eye in views:
  s.camera.location=eye;look(s.camera,(0,0,0));s.cycles.samples=96 if mode=='final' else 16
  if label=='neutral':s.view_settings.look='None'
  name=mode+'-'+label;s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s)
  rows.append(dict(name=name,view=name,png=name+'.png',exr='raw/'+name+'.exr',PNG_sha256=sha(O/(name+'.png')),EXR_sha256=sha(O/'raw'/(name+'.exr')),samples=s.cycles.samples,actually_saved=True,camera=list(eye),look=s.view_settings.look,resolution_px=[1000,700]))
 assert before=={name:geometry_digest(bpy.data.objects[name].data)for name in NAMES}
 write(O/(mode+'-render-report.json'),dict(source_sha256=sha(H/'child-candidate.blend'),export_sha256=sha(H/'child-candidate.glb'),views=rows,protocol_sha256=sha(Path(__file__)),geometry_unchanged=True,original_materials_retained=True,art_accepted=False))

if __name__=='__main__':
 mode=sys.argv[-1]
 if mode=='build':build()
 elif mode in ['gray','preview','final']:render(mode)
 else:raise ValueError(mode)
