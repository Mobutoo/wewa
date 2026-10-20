"""Build only the cast brake-panel body; export before any beauty rendering."""
import json,math,shutil,subprocess,tempfile
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
P=json.loads((HERE/'parameters.json').read_text());Z=P['centre_height_m']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['scope']='Single brake-panel casting candidate. Related JA131605, not exact RDC fitment or an operational brake.'
source=bpy.data.collections.new('WEWA_FRONT_BRAKE_PANEL_BODY');scene.collection.children.link(source)
construction=bpy.data.collections.new('EDITABLE_CAST_FEATURES_AND_DRILLING');scene.collection.children.link(construction)
fit=bpy.data.collections.new('FIT_INSPECTION_LINKED_CANDIDATES');scene.collection.children.link(fit)
studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');scene.collection.children.link(studio)
def material(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;m.diffuse_color=(*color,1);return m
paint=material('Panel silver cast coating - candidate',(.39,.42,.46),.55,.38)
machined=material('Panel machined bores and seat',(.40,.43,.47),.90,.25)
def move(obj,collection):
 for c in list(obj.users_collection):c.objects.unlink(obj)
 collection.objects.link(obj);return obj
def mesh_obj(name,verts,faces,mat=paint,collection=construction):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
 for f in mesh.polygons:f.use_smooth=True
 obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj);mesh.materials.append(mat);return obj
def lathe(name,section,n=192,collection=construction):
 verts=[];faces=[];count=len(section)
 for i in range(n):
  a=math.tau*i/n
  for x,r in section:verts.append((x,r*math.sin(a),Z+r*math.cos(a)))
 for i in range(n):
  for j in range(count):faces.append((i*count+j,((i+1)%n)*count+j,((i+1)%n)*count+(j+1)%count,i*count+(j+1)%count))
 return mesh_obj(name,verts,faces,collection=collection)
def bevel(obj,width=.0007):
 b=obj.modifiers.new('Cast edge radii - working estimate','BEVEL');b.width=width;b.segments=3
 return obj
def box(name,centre,dimensions,rotation=0,width=.0007):
 bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=move(bpy.context.object,construction);o.name=name;o.dimensions=dimensions;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.rotation_euler.x=rotation;o.data.materials.append(paint);bevel(o,width);return o
def cylinder(name,centre,radius,depth,axis='X',vertices=64):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre);o=move(bpy.context.object,construction);o.name=name
 o.rotation_euler=(Vector((1,0,0)) if axis=='X' else Vector((0,1,0)) if axis=='Y' else Vector((0,0,1))).to_track_quat('Z','Y').to_euler();o.data.materials.append(paint)
 for p in o.data.polygons:p.use_smooth=True
 return o
section=[(.048,.0063),(.048,.014),(.0465,.016),(.043,.018),(.0405,.026),(.037,.032),(.034,.050),(.034,.060),(.037,.063),(.037,.070),(.035,.072),(.028,.072),(.028,.070),(.028,.0642),(.024,.0642),(.024,.0612),(.028,.0612),(.030,.0545),(.027,.0538),(.024,.0535),(.0238,.0528),(.0238,.0512),(.024,.0505),(.030,.0500),(.030,.0358),(.028,.0353),(.024,.0350),(.0238,.0343),(.0238,.0327),(.024,.0320),(.0325,.0315),(.0363,.0268),(.0363,.0063)]
def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
for i in range(len(section)):
 for j in range(i+1,len(section)):
  if j==i+1 or (i==0 and j==len(section)-1):continue
  a,b,c,d=section[i],section[(i+1)%len(section)],section[j],section[(j+1)%len(section)]
  assert not (orient(a,b,c)*orient(a,b,d)<-1e-18 and orient(c,d,a)*orient(c,d,b)<-1e-18),'Self-crossing closed section'
body=lathe('Front brake panel - editable casting',section,collection=source);body['component_id']=P['component_id'];body['dimension_status']=P['dimensions_status'];body['art_accepted']=False
features=[];drills=[]
# Concentric rear rings are integral to the closed turned section above.
# Their former Boolean unions created coincident ring intersections.
for i in range(8):
 a=math.tau*i/8+.12;r=.047
 features.append(box('Back radial web '+str(i+1),(.0265,r*math.sin(a),Z+r*math.cos(a)),(.008,.0028,.030),rotation=-a,width=.00045))
 features.append(cylinder('Cast rib junction '+str(i+1),(.0245,.052*math.sin(a),Z+.052*math.cos(a)),.0033,.0045))
# The raised fork-stop pad grows from the central boss into the dish.
direction=Vector((0,-.84,.54));direction.normalize();a=math.atan2(-direction.y,direction.z)
pad_verts=[];pad_faces=[]
for u,width,front in [(-.004,.013,.049),(.025,.014,.052),(.064,.010,.050)]:
 for x,t in [(.031,-width),(front,-width),(front,width),(.031,width)]:pad_verts.append((x,u*direction.y+t*direction.z,Z+u*direction.z-t*direction.y))
for i in range(2):
 for j in range(4):pad_faces.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
pad_faces.extend([tuple(reversed(range(4))),tuple(8+j for j in range(4))]);features.append(bevel(mesh_obj('Tapered oblique fork-stop cast pad',pad_verts,pad_faces),.0012))
drills.append(box('Fork-stop rectangular recessed socket',(.051,-.043,Z+.028),(.018,.015,.021),rotation=a,width=.0008))
# Raised spine and two small pierced bosses; functions/installation remain unconfirmed.
spine_verts=[];spine_faces=[]
spine_sections=[(-.027,.024,.0015,.036),(-.023,.024,.0045,.040),(-.010,.024,.0055,.043),(.005,.025,.0065,.045),(.023,.025,.0050,.043),(.036,.024,.0030,.039),(.040,.024,.0015,.036)]
for z,y,width,front in spine_sections:
 for x,t in [(.0315,-width),(front,-width),(front,width),(.0315,width)]:spine_verts.append((x,y+t,Z+z))
for i in range(len(spine_sections)-1):
 for j in range(4):spine_faces.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
spine_faces.extend([tuple(reversed(range(4))),tuple((len(spine_sections)-1)*4+j for j in range(4))]);features.append(bevel(mesh_obj('Tapered rounded front casting spine',spine_verts,spine_faces),.0010))
for label,y,z,sx,sy,sz,hole in [('upper',.009,.029,.014,.014,.011,.0030),('outer',.052,.009,.019,.016,.014,.0040)]:
 centre=(.034+sx/2-.001,y,Z+z)
 features.append(box('Front '+label+' cast boss',centre,(sx,sy,sz),width=.0022))
 drills.append(cylinder('Cross opening '+label,(centre[0]+.001,y,Z+z),hole,sy+.02,axis='Y'))
cy,cz=P['working_cam_yz_m']
features.append(cylinder('Cast camshaft surround',(.0365,cy,Z+cz),.010,.013))
features.append(cylinder('Back anchor mounting boss',(.025,.030,Z+.040),.008,.012))
# A short indicator relief is visible in the product photo; no invented OEM lettering.
arc=[];arcfaces=[];samples=48
for i in range(samples+1):
 theta=4.06+(4.66-4.06)*i/samples
 for x,r in [(.034,.045),(.034,.049),(.036,.049),(.036,.045)]:arc.append((x,r*math.sin(theta),Z+r*math.cos(theta)))
for i in range(samples):
 for j in range(4):arcfaces.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
arcfaces.extend([tuple(reversed(range(4))),tuple(samples*4+j for j in range(4))]);features.append(mesh_obj('Indicator arc relief - no unverified text',arc,arcfaces))
for y,z in [(.024,.025),(.031,.045)]:
 features.append(cylinder('Small fixing surround',(.0375,y,Z+z),.0043,.008))
 drills.append(cylinder('Blind fixing recess',(.041,y,Z+z),.0018,.005))
drills.extend([cylinder('Axle through bore',(.04,0,Z),P['working_axle_bore_radius_m'],.12),cylinder('Camshaft through bore',(.04,cy,Z+cz),P['working_cam_bore_radius_m'],.12),cylinder('Reassert rear central clearance',(.0065,0,Z),P['working_counterbore_radius_m'],.060)])
def operand(obj):
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();e=obj.evaluated_get(deps);mesh=e.to_mesh();mesh.calc_loop_triangles()
 row={'name':obj.name,'vertices':[list(obj.matrix_world@v.co) for v in mesh.vertices],'triangles':[list(t.vertices) for t in mesh.loop_triangles]};e.to_mesh_clear();return row
inputs={'base':operand(body),'features':[operand(o) for o in features],'drills':[operand(o) for o in drills]}
with tempfile.TemporaryDirectory(prefix='wewa-panel-csg-') as directory:
 input_file=Path(directory)/'input.json';output_file=Path(directory)/'output.json';input_file.write_text(json.dumps(inputs))
 subprocess.run([shutil.which('python'),str(HERE/'csg.py'),str(input_file),str(output_file)],check=True);csg=json.loads(output_file.read_text())
body.name='Editable turned section - construction';move(body,construction)
for part in [body]+features+drills:part.hide_render=True;part.hide_set(True)
body=mesh_obj('Front brake panel - editable casting',csg['vertices'],csg['triangles'],collection=source);body['component_id']=P['component_id'];body['dimension_status']=P['dimensions_status'];body['art_accepted']=False
remesh=body.modifiers.new('Cast junction surface - explicit300um working grid','REMESH');remesh.mode='VOXEL';remesh.voxel_size=P['voxel_surface_m'];remesh.use_smooth_shade=True
smooth=body.modifiers.new('Gentle casting junction smoothing','SMOOTH');smooth.factor=.28;smooth.iterations=2
# Restore visible machined bores after remeshing; material IDs cannot be assumed.
group=bpy.data.node_groups.new('Panel machined bores after remesh','GeometryNodeTree');group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n,l=group.nodes,group.links
gin=n.new('NodeGroupInput');gout=n.new('NodeGroupOutput');position=n.new('GeometryNodeInputPosition');normal=n.new('GeometryNodeInputNormal')
def vmath(op,a,b=None):
 node=n.new('ShaderNodeVectorMath');node.operation=op;l.new(a,node.inputs[0])
 if b is not None:
  if isinstance(b,tuple):node.inputs[1].default_value=b
  else:l.new(b,node.inputs[1])
 return node.outputs['Value'] if op in ['LENGTH','DOT_PRODUCT'] else node.outputs['Vector']
def scalar(op,a,b):
 node=n.new('ShaderNodeMath');node.operation=op;l.new(a,node.inputs[0]);node.inputs[1].default_value=b;return node.outputs[0]
def boolean(op,a,b):
 node=n.new('FunctionNodeBooleanMath');node.operation=op;l.new(a,node.inputs[0]);l.new(b,node.inputs[1]);return node.outputs[0]
regions=[]
for y,z,r in [(0,Z,P['working_axle_bore_radius_m']),(cy,Z+cz,P['working_cam_bore_radius_m'])]:
 radial=vmath('MULTIPLY',vmath('SUBTRACT',position.outputs[0],(0,y,z)),(0,1,1));radius=vmath('LENGTH',radial)
 inward=scalar('LESS_THAN',vmath('DOT_PRODUCT',normal.outputs[0],vmath('NORMALIZE',radial)),-.4)
 regions.append(boolean('AND',scalar('LESS_THAN',radius,r+.0006),inward))
assign=n.new('GeometryNodeSetMaterial');assign.inputs['Material'].default_value=machined;l.new(gin.outputs[0],assign.inputs['Geometry']);l.new(boolean('OR',*regions),assign.inputs['Selection']);l.new(assign.outputs['Geometry'],gout.inputs[0]);gn=body.modifiers.new('Actual machined bore assignment','NODES');gn.node_group=group
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();evaluated=body.evaluated_get(deps);mesh=evaluated.to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
metrics={'vertices':len(bm.verts),'faces':len(bm.faces),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True),'material_faces':{m.name:sum(p.material_index==i for p in mesh.polygons) for i,m in enumerate(mesh.materials)}}
assert metrics['non_manifold_edges']==0 and metrics['signed_volume_m3']>0,metrics
assert .95<metrics['signed_volume_m3']/csg['volume_m3']<1.05,('Unexpected surface-correction volume change',metrics,csg['volume_m3'])
assert metrics['material_faces'].get(machined.name,0)>0,metrics
bm.free();evaluated.to_mesh_clear()
export_mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps);inspection=bpy.data.objects.new('Front brake panel - inspection export',export_mesh);source.objects.link(inspection)
dec=inspection.modifiers.new('Inspection reduction - not mobile LOD','DECIMATE');dec.ratio=P['inspection_ratio'];dec.use_collapse_triangulate=True;bpy.context.view_layer.objects.active=inspection;bpy.ops.object.modifier_apply(modifier=dec.name)
inspection.hide_render=True;bpy.ops.object.select_all(action='DESELECT');inspection.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(HERE/'front-brake-plate-inspection.glb'),use_selection=True,export_apply=True,export_format='GLB',export_yup=True,export_extras=True)
linked=[]
for file,name in [(HERE.parent/'front-rim/front-rim-v1.blend','Front cast rim - inspection export'),(HERE.parent/'front-tyre/front-tyre-v1.blend','Front tyre - inspection export')]:
 with bpy.data.libraries.load(str(file),link=True,relative=True) as (available,loaded):loaded.objects=[name]
 for original in loaded.objects:
  obj=original.copy();obj.name='FIT '+name;fit.objects.link(obj);obj.hide_render=False;obj.hide_set(False);obj.select_set(True);linked.append(obj)
bpy.ops.export_scene.gltf(filepath=str(HERE/'front-wheel-panel-fit-inspection.glb'),use_selection=True,export_apply=True,export_format='GLB',export_yup=True,export_extras=True)
inspection.hide_set(True);fit.hide_render=True
# Studio is separate from exports and does not alter asset coordinates.
floor_mat=material('Panel neutral studio floor',(.13,.14,.15),0,.82)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.2177));floor=move(bpy.context.object,studio);floor.name='PANEL_STUDIO_FLOOR';floor.data.materials.append(floor_mat)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.30,.33,.37,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.13
for name,loc,power,size in [('PANEL_KEY',(.7,-.6,1.1),27,.9),('PANEL_FILL',(-.65,-.05,.8),15,.8),('PANEL_EDGE',(.25,.6,.8),22,.65)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;obj=bpy.data.objects.new(name,data);studio.objects.link(obj);obj.location=loc;obj.rotation_euler=(Vector((.035,0,Z))-obj.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Panel review camera');camera=bpy.data.objects.new('Panel review camera',data);studio.objects.link(camera);camera.location=(.45,-.25,.49);camera.rotation_euler=(Vector((.032,0,Z))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=80;camera.data.clip_start=.002;camera.data.clip_end=300;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'front-brake-plate-v1.blend'),compress=True)
report={'component':P['component_id'],'parameters':P,'section_m':section,'solid_processing':{k:v for k,v in csg.items() if k not in ['vertices','triangles']},'evaluated_casting':metrics,'inspection_vertices':len(inspection.data.vertices),'inspection_faces':len(inspection.data.polygons),'render_views':0,'linked_fit_geometry':'Reduced inspection wheel candidates, not a complete motorcycle','photo_cameras_calibrated':False,'installation_clocking_confirmed':False,'functional_brake_created':False,'art_accepted':False}
(HERE/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_PANEL_BUILD',json.dumps(metrics))
