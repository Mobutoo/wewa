import bpy,pathlib,json,hashlib
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews'/H.name;P=json.loads((H/'parameters-v2.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 bpy.ops.wm.open_mainfile(filepath=str(p),use_scripts=False);ob=bpy.data.objects['EXTERIOR_CHILD'];m=ob.data;m.calc_loop_triangles();parts={0:[],1:[]}
 for t in m.loop_triangles:parts[t.material_index].append([t.material_index,list(t.vertices),[[*m.vertices[m.loops[li].vertex_index].co,*m.corner_normals[li].vector,*m.uv_layers.active.data[li].uv]for li in t.loops]])
 enc=lambda x:hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest();f=m.materials[1];bs=f.node_tree.nodes['Principled BSDF'];props={k:list(bs.inputs[k].default_value)if hasattr(bs.inputs[k].default_value,'__len__')else bs.inputs[k].default_value for k in ['Base Color','Roughness','Metallic','Coat Weight']}
 return dict(source_sha256=sha(p),face_hash=enc(parts[0]),frame_hash=enc(parts[1]),world_hash=enc([list(r)for r in ob.matrix_world]),frame_material=dict(name=f.name,properties=props,node_count=len(f.node_tree.nodes),link_count=len(f.node_tree.links),backface_culling=f.use_backface_culling),mesh_count=sum(o.type=='MESH'for o in bpy.context.scene.objects),camera_position=list(bpy.context.scene.camera.location),camera_samples=bpy.context.scene.cycles.samples)
a=read(R/P['source_v1']);b=read(H/(H.name+'.blend'))
for k in ['face_hash','frame_hash','world_hash','frame_material','mesh_count']:assert a[k]==b[k],k
assert b['mesh_count']==1
(O/'source-reopen-check.json').write_text(json.dumps(dict(component_id=P['component_id'],package=P['package'],source_v1=a,source_v2=b,face_and_frame_geometry_normals_UV_world_exact=True,frame_material_exact=True,same_single_specimen=True,source_v1_untouched=True),indent=2)+'\n')
