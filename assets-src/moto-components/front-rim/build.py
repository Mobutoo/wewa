"""One editable front cast wheel component, then an explicit tyre-fit inspection.
No complete motorcycle or rider. Reference photos are not used as textures.
"""
import argparse,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'creative/reviews/front-rim-v1'
OUT.mkdir(parents=True,exist_ok=True)
P=json.loads((HERE/'parameters.json').read_text())
parser=argparse.ArgumentParser()
parser.add_argument('--samples',type=int,default=48)
parser.add_argument('--resolution',type=int,default=1200)
parser.add_argument('--spokes',type=int,default=5)
parser.add_argument('--cast-remesh',type=float,default=.00065)
parser.add_argument('--inspection-ratio',type=float,default=.06)
parser.add_argument('--views',default='isolated-side,isolated-quarter,joint-close,tyre-fit-neutral,tyre-fit-cinematic')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=args.samples;scene.cycles.use_denoising=False;scene.cycles.max_bounces=6
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=args.resolution;scene.render.resolution_y=args.resolution;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.32,.35,.40,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.13
components=bpy.data.collections.new('WEWA_FRONT_RIM_EDITABLE');scene.collection.children.link(components)
cutters=bpy.data.collections.new('EDITABLE_CAST_SPOKE_CONSTRUCTION');scene.collection.children.link(cutters)
fit=bpy.data.collections.new('TYRE_FIT_INSPECTION_NOT_COMPLETE_MOTORCYCLE');scene.collection.children.link(fit)
parts=[]

def material(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;m.diffuse_color=(*color,1);return m
paint=material('Silver coating on cast alloy - working reference',(.35,.38,.42),.72,.30)
paint.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.08
machined=material('Machined drum and bearing seat',(.36,.39,.43),.88,.29)
rubber=material('Valve rubber',(.005,.006,.007),0,.68)
brass=material('Valve stem brass',(.36,.25,.10),.85,.32)

def mesh_object(name,verts,faces,mat,collection=components):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj);mesh.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
 for p in mesh.polygons:p.use_smooth=True
 obj['component_id']=P['component_id'];obj['status']='Editable candidate, estimated part dimensions, not art accepted'
 return obj

def lathe(name,section,mat,n=256,collection=components):
 verts=[];faces=[];count=len(section)
 for i in range(n):
  a=math.tau*i/n;s,c=math.sin(a),math.cos(a)
  for x,r in section:verts.append((x,r*s,.29+r*c))
 for i in range(n):
  for j in range(count):faces.append((i*count+j,((i+1)%n)*count+j,((i+1)%n)*count+(j+1)%count,i*count+(j+1)%count))
 obj=mesh_object(name,verts,faces,mat,collection)
 uv=obj.data.uv_layers.new(name='Circumference_section')
 for poly in obj.data.polygons:
  i,j=divmod(poly.index,count)
  for li,pair in zip(poly.loop_indices,[(i/n,j/count),((i+1)/n,j/count),((i+1)/n,(j+1)/count),(i/n,(j+1)/count)]):uv.data[li].uv=pair
 return obj

# Bead-seat17in is known; the other cross-section dimensions remain estimated.
rim_section=[(-.0210,.221),(-.0210,.2245),(-.0195,.2265),(-.0180,.2250),(-.01778,.216),(-.01778,.209),(-.014,.203),(-.008,.200),(.008,.200),(.014,.203),(.01778,.209),(.01778,.216),(.0180,.2250),(.0195,.2265),(.0210,.2245),(.0210,.221),(.0205,.215),(.0205,.207),(.0170,.199),(.0090,.195),(-.0090,.195),(-.0170,.199),(-.0205,.207),(-.0205,.215)]
rim_section=[(x*P['working_bead_seat_width_m']/.03556,r) for x,r in rim_section]
rim=lathe('Cast rim - closed bead and drop-centre section',rim_section,paint)
parts.append(rim)
# The wheel casting includes its drum housing, not the later removable brake plate.
hub_section=[(-.036,.0065),(-.036,.021),(-.028,.027),(-.027,.061),(-.024,.069),(-.018,.072),(.022,.072),(.027,.067),(.027,.065),(-.015,.065),(-.021,.060),(-.021,.026),(.035,.026),(.035,.0065)]
hub=lathe('Integral hollow drum and bearing boss',hub_section,paint)
hub.data.materials.append(machined)
for poly in hub.data.polygons:
 j=poly.index%len(hub_section)
 if j in [7,8,9,10,11,12,13]:poly.material_index=1
parts.append(hub)

# A swept closed I-section rather than cylindrical rods. All dimensions are editable.
def spoke(k):
 radial=[.060,.066,.077,.095,.120,.148,.174,.192,.204,.210]
 widths=[.017,.016,.013,.011,.010,.010,.0105,.012,.014,.015]
 depths=[.013,.013,.012,.011,.010,.010,.011,.012,.013,.014]
 verts=[];faces=[];n=12
 for i,r in enumerate(radial):
  u=(r-radial[0])/(radial[-1]-radial[0]);angle=math.tau*k/5+.08+P['spoke_sweep_radians']*u
  w,d=widths[i],depths[i];lip=.0023;web=.0040
  cross=[(-d,-w),(-d,w),(-d+lip,w),(-d+lip,web),(d-lip,web),(d-lip,w),(d,w),(d,-w),(d-lip,-w),(d-lip,-web),(-d+lip,-web),(-d+lip,-w)]
  for x,t in cross:verts.append((x,r*math.sin(angle)+t*math.cos(angle),.29+r*math.cos(angle)-t*math.sin(angle)))
 for i in range(len(radial)-1):
  for j in range(n):faces.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
 faces.extend([tuple(reversed(range(n))),tuple((len(radial)-1)*n+j for j in range(n))])
 obj=mesh_object('Cast spoke exemplar' if k==0 else f'Cast spoke {k+1:02}',verts,faces,paint,cutters)
 bevel=obj.modifiers.new('Rounded casting section edges','BEVEL');bevel.width=.0007;bevel.segments=3
 return obj
spokes=[spoke(k) for k in range(args.spokes)]
# Retain the construction objects and non-destructive union stack for later revisions.
for part in [hub]+spokes:
 modifier=rim.modifiers.new('Integral casting union '+part.name,'BOOLEAN');modifier.operation='UNION';modifier.solver='EXACT';modifier.object=part
 part.hide_render=True;part.hide_set(True)
if args.cast_remesh:
 remesh=rim.modifiers.new('Optional casting junction surface correction','REMESH');remesh.mode='VOXEL';remesh.voxel_size=args.cast_remesh;remesh.use_smooth_shade=True
 smooth=rim.modifiers.new('Gentle cast junction smoothing','SMOOTH');smooth.factor=.35;smooth.iterations=3
bevel=rim.modifiers.new('Small cast junction radii','BEVEL');bevel.width=.0012;bevel.segments=3;bevel.limit_method='ANGLE';bevel.angle_limit=.55
bevel.harden_normals=True
normals=rim.modifiers.new('Cast face normals','WEIGHTED_NORMAL');normals.keep_sharp=True;normals.weight=40

# Voxel remeshing discards Boolean material IDs. Restore the machined bore/cavity
# by a geometric region field, so source renders and evaluated GLB share it.
group=bpy.data.node_groups.new('Machined bore and drum surface assignment','GeometryNodeTree')
group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
nodes,links=group.nodes,group.links
gin=nodes.new('NodeGroupInput');gout=nodes.new('NodeGroupOutput')
position=nodes.new('GeometryNodeInputPosition');normal=nodes.new('GeometryNodeInputNormal')
separate=nodes.new('ShaderNodeSeparateXYZ');links.new(position.outputs['Position'],separate.inputs[0])
def vector_math(op,a,b=None):
 node=nodes.new('ShaderNodeVectorMath');node.operation=op;links.new(a,node.inputs[0])
 if b is not None:
  if isinstance(b,tuple):node.inputs[1].default_value=b
  else:links.new(b,node.inputs[1])
 return node.outputs['Value'] if op in ['DOT_PRODUCT','LENGTH','DISTANCE'] else node.outputs['Vector']
def scalar(op,a,b):
 node=nodes.new('ShaderNodeMath');node.operation=op;links.new(a,node.inputs[0]);node.inputs[1].default_value=b;return node.outputs[0]
def boolean(op,a,b):
 node=nodes.new('FunctionNodeBooleanMath');node.operation=op;links.new(a,node.inputs[0]);links.new(b,node.inputs[1]);return node.outputs[0]
radial=vector_math('MULTIPLY',vector_math('SUBTRACT',position.outputs['Position'],(0,0,.29)),(0,1,1));radius=vector_math('LENGTH',radial)
inward=scalar('LESS_THAN',vector_math('DOT_PRODUCT',normal.outputs['Normal'],vector_math('NORMALIZE',radial)),-.5)
cavity=boolean('AND',boolean('AND',inward,scalar('LESS_THAN',radius,.0665)),scalar('GREATER_THAN',separate.outputs['X'],-.015))
bearing_end=boolean('AND',scalar('GREATER_THAN',separate.outputs['X'],.0335),scalar('LESS_THAN',radius,.027))
assign=nodes.new('GeometryNodeSetMaterial');assign.inputs['Material'].default_value=machined
links.new(gin.outputs['Geometry'],assign.inputs['Geometry']);links.new(boolean('OR',cavity,bearing_end),assign.inputs['Selection']);links.new(assign.outputs['Geometry'],gout.inputs['Geometry'])
modifier=rim.modifiers.new('Restore machined surface material after remeshing','NODES');modifier.node_group=group

# Original valve approximation, pointing inward into the accessible wheel opening.
def cylinder_between(name,a,b,r,mat,segments=32):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=r,depth=d.length,location=(a+b)/2);obj=bpy.context.object;obj.name=name;obj.rotation_euler=d.to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
 for collection in list(obj.users_collection):collection.objects.unlink(obj)
 components.objects.link(obj)
 bevel=obj.modifiers.new('Valve edge radius','BEVEL');bevel.width=.0004;bevel.segments=2
 for p in obj.data.polygons:p.use_smooth=True
 parts.append(obj);return obj
valve_angle=math.radians(42)
def vr(r):return (0,r*math.sin(valve_angle),.29+r*math.cos(valve_angle))
cylinder_between('Valve rubber base - estimated',vr(.201),vr(.194),.0050,rubber)
cylinder_between('Valve stem - estimated',vr(.195),vr(.181),.0032,brass)
cylinder_between('Valve dust cap - estimated',vr(.184),vr(.177),.0040,rubber)

# Link the existing tyre source. It remains editable in its own file, not duplicated.
tyre_path=HERE.parent/'front-tyre/front-tyre-v1.blend'
with bpy.data.libraries.load(str(tyre_path),link=True,relative=True) as (available,loaded):loaded.objects=['Front tyre - editable detailed surface']
for obj in loaded.objects:
 if obj:fit.objects.link(obj)
fit.hide_render=True

# Neutral studio and cinematic variant use the same component/materials.
floor_mat=material('Neutral studio floor',(.15,.16,.17),0,.83)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.0005));floor=bpy.context.object;floor.name='STUDIO_FLOOR_NOT_EXPORTED';floor.data.materials.append(floor_mat)
# A small rest keeps the bare rim off the floor; hidden during the tyre-fit check.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.032));rest=bpy.context.object;rest.name='INSPECTION_REST_NOT_EXPORTED';rest.dimensions=(.09,.15,.065);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);rest.data.materials.append(material('Inspection rest',(.015,.018,.022),0,.75));b=rest.modifiers.new('Rounded rest','BEVEL');b.width=.006;b.segments=3

def light(name,loc,energy,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=loc;obj.rotation_euler=(Vector((0,0,.29))-obj.location).to_track_quat('-Z','Y').to_euler();return obj
key=light('KEY',(.8,-.8,1.4),30,1.0);fill=light('FILL',(-.9,-.1,.8),18,1.0);edge=light('EDGE',(.3,.8,1.0),25,.7)
camera_data=bpy.data.cameras.new('Component review camera');camera=bpy.data.objects.new('Component review camera',camera_data);scene.collection.objects.link(camera);scene.camera=camera;camera.data.clip_start=.005;camera.data.clip_end=300
views={'isolated-side':((1.52,0,.35),(0,0,.29),70,False),'isolated-quarter':((.82,-1.10,.74),(0,0,.29),70,False),'joint-close':((.34,-.45,.55),(0,-.075,.43),85,False),'tyre-fit-neutral':((.95,-1.38,.84),(0,0,.29),70,True),'tyre-fit-cinematic':((.95,-1.38,.84),(0,0,.29),70,True)}
report={'component':P['component_id'],'parameters':P,'rim_section_m':rim_section,'hub_section_m':hub_section,'spokes':len(spokes),'renders':[],'photo_cameras_calibrated':False,'brake_plate_modelled':False,'rider_created':False,'whole_motorcycle_complete':False,'art_accepted':False,'cast_remesh_m':args.cast_remesh}
# Evaluate actual geometry, rather than counting source primitives as quality proof.
bpy.context.view_layer.update();evaluated=rim.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
report['evaluated_casting']={'vertices':len(bm.verts),'faces':len(bm.faces),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True)}
assert report['evaluated_casting']['non_manifold_edges']==0 and report['evaluated_casting']['signed_volume_m3']>0,report['evaluated_casting']
bm.free();evaluated.to_mesh_clear()
# Inspection export evaluates all casting modifiers, with an explicit reduced copy.
# Blender glTF export_apply is necessary: otherwise the Boolean spokes are omitted.
evaluated=rim.evaluated_get(bpy.context.evaluated_depsgraph_get())
export_mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get())
export_rim=bpy.data.objects.new('Front cast rim - inspection export',export_mesh);components.objects.link(export_rim)
decimate=export_rim.modifiers.new('Inspection reduction - not a mobile LOD','DECIMATE');decimate.ratio=args.inspection_ratio;decimate.use_collapse_triangulate=True
bpy.context.view_layer.objects.active=export_rim;bpy.ops.object.modifier_apply(modifier=decimate.name)
report['inspection_casting']={'vertices':len(export_rim.data.vertices),'faces':len(export_rim.data.polygons),'reduction_ratio_requested':args.inspection_ratio,'mobile_lod':False}
export_rim.hide_render=True
bpy.ops.object.select_all(action='DESELECT');export_rim.select_set(True);bpy.context.view_layer.objects.active=export_rim
for obj in parts[2:]:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(HERE/'front-rim-inspection.glb'),use_selection=True,export_apply=True,export_format='GLB',export_extras=True,export_yup=True,export_materials='EXPORT')
# A separate assembly inspection includes tyre inspection geometry, not the1M source.
with bpy.data.libraries.load(str(tyre_path),link=True,relative=True) as (available,loaded):loaded.objects=['Front tyre - inspection export']
inspection=bpy.data.collections.new('GLTF_TYRE_INSPECTION_ONLY');scene.collection.children.link(inspection)
for obj in loaded.objects:
 if obj:
  inspection.objects.link(obj);obj.hide_set(False);obj.select_set(True)
inspection.hide_render=True
bpy.ops.export_scene.gltf(filepath=str(HERE/'front-wheel-fit-inspection.glb'),use_selection=True,export_apply=True,export_format='GLB',export_extras=True,export_yup=True,export_materials='EXPORT')
export_rim.hide_set(True)
for name in ([] if args.views=='none' else args.views.split(',')):
 loc,target,lens,show_tyre=views[name];fit.hide_render=not show_tyre;rest.hide_render=show_tyre
 camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=lens
 cinematic=name.endswith('cinematic');key.data.color=(1,.70,.43) if cinematic else (1,1,1);key.data.energy=43 if cinematic else 30;fill.data.color=(.68,.79,1) if cinematic else (1,1,1);fill.data.energy=11 if cinematic else 18;edge.data.color=(1,.82,.63) if cinematic else (1,1,1)
 scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);report['renders'].append({'name':name,'camera_location_m':loc,'camera_target_m':target,'lens_mm':lens,'includes_linked_tyre':show_tyre})
# Preserve source, editable profiles, booleans and linked tyre reference.
fit.hide_render=False;rest.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'front-rim-v1.blend'),compress=True)
report.update(samples=args.samples,resolution_px=[args.resolution,args.resolution],linked_tyre_source=str(tyre_path.relative_to(ROOT)))
(HERE/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('WEWA_RIM_COMPLETE',json.dumps(report['evaluated_casting']))
