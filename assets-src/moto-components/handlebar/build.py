"""Original bare-handlebar candidate, all part dimensions explicitly estimated.
No vendor model or reference photograph used as a texture.
"""
import json,math,hashlib
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
P=json.loads((HERE/'parameters.json').read_text());OUT=ROOT/'creative/reviews/handlebar-v1';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_BARE_HANDLEBAR');scene.collection.children.link(source)
studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');scene.collection.children.link(studio)

def move(obj,collection):
 for old in list(obj.users_collection):old.objects.unlink(obj)
 collection.objects.link(obj);return obj

def material(name,color,metal,rough):
 mat=bpy.data.materials.new(name);mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(*color,1);shader.inputs['Metallic'].default_value=metal;shader.inputs['Roughness'].default_value=rough;mat.diffuse_color=(*color,1);return mat
chrome=material('Handlebar chrome appearance - estimated',(.56,.58,.60),1,.18)
inner=material('Handlebar inner steel appearance - estimated',(.23,.25,.27),.95,.34)
band=material('Handlebar observed clamp bands - estimated',(.43,.45,.46),1,.28)

# Circular 3D corner fillets give C1 continuity between straight tube segments.
# Each bend remains in the plane of its two adjacent directions.
raw=[Vector(v) for v in P['right_side_construction_polyline_m']]
pieces=[];cursor=raw[0];radius=P['bend_radius_working_m'];fillets=[]
for i in range(1,len(raw)-1):
 a,b,c=raw[i-1:i+2];u=(b-a).normalized();v=(c-b).normalized();theta=u.angle(v);distance=radius*math.tan(theta/2)
 assert distance<.45*min((b-a).length,(c-b).length),'Bend does not fit adjacent lengths'
 start=b-u*distance;end=b+v*distance;axis=u.cross(v).normalized();normal=axis.cross(u).normalized();centre=start+normal*radius
 pieces.append(('line',cursor,start));pieces.append(('arc',start,end,centre,axis,theta));fillets.append({'corner_index':i,'start':list(start),'end':list(end),'radius_m':radius,'turn_radians':theta});cursor=end
pieces.append(('line',cursor,raw[-1]))
right=[]
for piece in pieces:
 length=(piece[2]-piece[1]).length if piece[0]=='line' else radius*piece[5]
 steps=max(2,math.ceil(length/P['straight_sample_step_m']))
 if piece[0]=='line' and max(abs(piece[1].x),abs(piece[2].x))<.083:steps=max(steps,math.ceil(length/P['knurl_sample_step_m']))
 for i in range(steps):
  t=i/steps
  point=piece[1].lerp(piece[2],t) if piece[0]=='line' else piece[3]+Quaternion(piece[4],piece[5]*t)@(piece[1]-piece[3])
  if not right or (point-right[-1]).length>1e-8:right.append(point)
right.append(raw[-1]);path=[Vector((-v.x,v.y,v.z)) for v in reversed(right[1:])]+right
assert all((path[i+1]-path[i]).length>1e-8 for i in range(len(path)-1))
distance=[0.]
for a,b in zip(path,path[1:]):distance.append(distance[-1]+(b-a).length)
tangents=[]
for i in range(len(path)):
 tangent=path[min(i+1,len(path)-1)]-path[max(0,i-1)];tangents.append(tangent.normalized())
frames=[];normal=Vector((0,0,1));normal=(normal-tangents[0]*normal.dot(tangents[0])).normalized()
for i,t in enumerate(tangents):
 if i:normal=tangents[i-1].rotation_difference(t)@normal;normal=(normal-t*normal.dot(t)).normalized()
 frames.append((normal,t.cross(normal).normalized()))

N=P['radial_segments'];R=P['tube_outer_radius_working_m'];wall=P['tube_wall_working_m'];verts=[];faces=[];materials=[]
def knurl(x,phi):
 # Two clamp bands are visible on both related-part photographs. Tooth pitch,
 # amplitude and band position remain deliberately estimated.
 width=P['clamp_band_width_working_m'];depth=P['knurl_working_depth_m'];result=0.
 for centre in P['clamp_band_centres_x_working_m']:
  q=abs(x-centre)/(width/2)
  if q<1:
   fade=min(1,(1-q)*10);phase=(x-centre)/.0008*math.tau
   result+=depth*fade*(.5+.25*math.sin(48*phi+phase)+.25*math.sin(48*phi-phase))
 return result
for layer in range(2):
 for i,(point,(a,b)) in enumerate(zip(path,frames)):
  for j in range(N):
   phi=math.tau*j/N;base=R if layer==0 else R-wall
   outer=base+knurl(point.x,phi) if layer==0 else base
   # Tiny geometric chamfer at cut ends, no end plug or filled disc.
   end=min(distance[i],distance[-1]-distance[i]);chamfer=max(0,.00014-end)
   rr=outer-chamfer if layer==0 else outer+chamfer
   verts.append(tuple(point+(math.cos(phi)*a+math.sin(phi)*b)*rr))
count=len(path);layer_size=count*N
for layer in range(2):
 offset=layer*layer_size
 for i in range(count-1):
  for j in range(N):
   face=(offset+i*N+j,offset+i*N+(j+1)%N,offset+(i+1)*N+(j+1)%N,offset+(i+1)*N+j)
   faces.append(face if layer==0 else tuple(reversed(face)))
   is_band=layer==0 and any(abs((path[i].x+path[i+1].x)/2-c)<P['clamp_band_width_working_m']/2 for c in P['clamp_band_centres_x_working_m'])
   materials.append(2 if is_band else layer)
for i in [0,count-1]:
 for j in range(N):
  face=(i*N+j,i*N+(j+1)%N,layer_size+i*N+(j+1)%N,layer_size+i*N+j);faces.append(face);materials.append(1)
mesh=bpy.data.meshes.new('Continuous bent tube wall');mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
obj=bpy.data.objects.new('Handlebar bare continuous tube - editable candidate',mesh);source.objects.link(obj)
for mat in [chrome,inner,band]:mesh.materials.append(mat)
for i,p in enumerate(mesh.polygons):p.material_index=materials[i];p.use_smooth=i<2*(count-1)*N
# Continuous length/circumference UV for future controlled appearance, no photo texture.
uv=mesh.uv_layers.new(name='Tube length circumference metres')
for poly in mesh.polygons:
 for li in poly.loop_indices:
  index=mesh.loops[li].vertex_index%layer_size;row,j=divmod(index,N);uv.data[li].uv=(distance[row],j/N*math.tau*R)
obj['component_id']=P['component_id'];obj['all_dimensions_estimated']=True;obj['grips_or_controls_created']=False;obj['art_accepted']=False

# Independent source preflight: the tube WALL is closed while its lumen stays open.
bm=bmesh.new();bm.from_mesh(mesh);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;pending=[unseen.pop()]
 while pending:
  for edge in pending.pop().link_edges:
   for v in edge.verts:
    if v in unseen:unseen.remove(v);pending.append(v)
tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons]);probes={}
for name,i,t in [('left',0,tangents[0]),('right',count-1,-tangents[-1])]:
 p=path[i];out=p-t*.003;hit=tree.ray_cast(out,t,.015);a,b=frames[i];metal_probe=tree.ray_cast(out+a*(R-wall/2),t,.015)
 probes[name]={'short_axial_lumen_clear':hit[0] is None,'short_axial_wall_hit':metal_probe[0] is not None,'centre_m':list(p),'inward_axis':list(t),'straight_control_section_length_available_m':.18}
volume=bm.calc_volume(signed=True);nm=sum(not e.is_manifold for e in bm.edges)
expected=math.pi*(R*R-(R-wall)**2)*distance[-1]
assert shells==1 and nm==0 and volume>0,(shells,nm,volume)
assert .98<volume/expected<1.03,(volume,expected)
assert all(p['short_axial_lumen_clear'] and p['short_axial_wall_hit'] for p in probes.values()),probes
bm.free()
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.gltf(filepath=str(HERE/'handlebar-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False)

floor_mat=material('Handlebar studio matte neutral',(.045,.05,.06),0,.70)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.0113));floor=move(bpy.context.object,studio);floor.name='HANDLEBAR_STUDIO_FLOOR';floor.data.materials.append(floor_mat)
world=bpy.data.worlds.new('Handlebar neutral studio');world.use_nodes=True;scene.world=world;bg=world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.28,.30,.34,1);bg.inputs[1].default_value=.28
# Strip lights reveal continuous bends and metal reflections rather than relying on colour.
for name,location,target,energy,size,size_y in [('HB_KEY',(0,.3,.95),(0,0,.05),70,1.1,.16),('HB_FILL',(-.65,-.25,.6),(0,0,.05),38,.65,.45),('HB_EDGE',(.6,-.35,.45),(0,0,.05),48,.9,.12)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='RECTANGLE';data.size=size;data.size_y=size_y;light=bpy.data.objects.new(name,data);studio.objects.link(light);light.location=location;light.rotation_euler=(Vector(target)-light.location).to_track_quat('-Z','Y').to_euler()
camera=bpy.data.objects.new('HANDLEBAR_CAMERA',bpy.data.cameras.new('HANDLEBAR_CAMERA'));studio.objects.link(camera);scene.camera=camera;camera.location=(.82,.92,.68);camera.rotation_euler=(Vector((0,.02,.05))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=60
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=False;scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'handlebar-v1.blend'),compress=True)
bounds={'min':[min(v.co[i] for v in mesh.vertices) for i in range(3)],'max':[max(v.co[i] for v in mesh.vertices) for i in range(3)]}
report={'component_id':P['component_id'],'scope':'Bare bent tube only; not complete rider controls or accepted exact RDC part','source_sha256':hashlib.sha256((HERE/'handlebar-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'handlebar-inspection.glb').read_bytes()).hexdigest(),'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'non_manifold_edges':nm,'connected_wall_shells':shells,'signed_wall_volume_m3':volume,'analytic_untextured_wall_volume_m3':expected,'centreline_length_m':distance[-1],'bounds_blender_xyz_m':bounds,'fillets':fillets,'end_probes':probes,'all_dimensions_estimated':True,'exact_RDC_part_confirmed':False,'physical_iphone_tested':False,'art_accepted':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_HANDLEBAR_SOURCE',json.dumps(report))
