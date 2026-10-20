"""Original hollow PF121017-related tube; visible section details, estimated dimensions."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];P=json.loads((HERE/'parameters.json').read_text());OUT=ROOT/'creative/reviews/front-fork-inner-tube-v1';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('WEWA_FORK_INNER_TUBE_ISOLATED');s.collection.children.link(col);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
N=P['radial_segments'];L=P['length_working_m'];R=P['outer_diameter_working_m']/2;IR=R-P['wall_working_m'];v=[];f=[];regions=[];surface_uv=[]
# Original ordered meridian: smooth rounded shoulder and two narrow machined grooves.
outer=[(0,.01455),(.00030,.01485),(.00060,.0149),(.003,.0149)]
for z in P['groove_centres_working_m']:
 w=P['groove_width_working_m'];d=P['groove_depth_working_m'];outer += [(z-w,.0149),(z-w*.55,.0149-d*.3),(z-w*.20,.0149-d),(z+w*.20,.0149-d),(z+w*.55,.0149-d*.3),(z+w,.0149)]
outer += [(.048,.0149),(.050,.0149),(.051,.01496),(.052,.01513),(.053,.01533),(.054,.01546),(.055,.0155),(.075,R),(.20,R),(.40,R),(L-.001,R),(L-.00025,R-.00005),(L,R-.00025)]
assert all(a[0]<b[0] for a,b in zip(outer,outer[1:]))
# Female thread is a bounded visual estimate of the observed internal helix.
thread=P['female_thread'];start=L-thread['working_length_m'];inner=[(0,IR+.0005),(.00035,IR+.00018),(.001,IR),(.025,IR),(.08,IR),(.25,IR),(.45,IR),(start-.001,IR)]
steps=round(thread['working_length_m']/thread['working_pitch_m']*P['thread_samples_per_pitch'])
inner += [(start+i/steps*(L-start),IR) for i in range(steps+1)]
loops=[]
for side,profile in [('outer',outer),('inner',list(reversed(inner)))]:
 for z,r in profile:
  ring=[]
  for j in range(N):
   phi=math.tau*j/N;rr=r
   if side=='inner' and z>=start:
    phase=((z-start)/thread['working_pitch_m']-j/N)%1;ridge=(1+math.cos(math.tau*phase))/2;fade=min(1,max(0,(z-start)/.001),max(0,(L-z)/.0005));rr+=thread['working_radial_depth_m']*ridge*fade
   ring.append(len(v));v.append((rr*math.cos(phi),rr*math.sin(phi),z))
  loops.append((ring,z,side))
# Join through both annular lips, retaining the open axial passage and real wall.
for k in range(len(loops)):
 ring,z,side=loops[k];other,z2,side2=loops[(k+1)%len(loops)]
 for j in range(N):
  f.append((ring[j],ring[(j+1)%N],other[(j+1)%N],other[j]));regions.append('lip' if side!=side2 else side)
mesh=bpy.data.meshes.new('Original meridian wall plus continuous female helix');mesh.from_pydata(v,[],f);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free();body=bpy.data.objects.new('Single inner fork tube - related PF121017 estimate',mesh);col.objects.link(body)
def mat(name,color,rough,metal):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
for m in [mat('Polished tube steel - visual estimate',(.55,.57,.60),.15,1),mat('Machined lower end and lips - visual estimate',(.48,.50,.53),.23,1),mat('Internal steel and female thread - estimated',(.28,.30,.33),.27,1)]:mesh.materials.append(m)
uv=mesh.uv_layers.new(name='Physical cylindrical 8mm mapping');circum=math.tau*R;tile=.008
for k,p in enumerate(mesh.polygons):
 z=sum(mesh.vertices[i].co.z for i in p.vertices)/4;region=regions[k];p.material_index=2 if region=='inner' else 1 if region=='lip' or z<.055 else 0;p.use_smooth=region!='lip'
 # Faces retain ordered circumferential sectors; seam corners get distinct UV.
 j=k%N;u0=j/N*circum/tile;u1=(j+1)/N*circum/tile
 for li,u in zip(p.loop_indices,[u0,u1,u1,u0]):
  q=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(q.x/tile,q.y/tile) if region=='lip' else (u,q.z/tile)
mesh.set_sharp_from_angle(angle=.55);tri=body.modifiers.new('Evaluated export triangulation','TRIANGULATE');tri.keep_custom_normals=True
body['component_id']=P['component_id'];body['dimensions_current_RDC_verified']=False;body['installed_pose_applied']=False
# Preflight evaluated wall, connectivity, zero-area faces and axial clear passage.
e=body.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;stack=[unseen.pop()]
 while stack:
  for edge in stack.pop().link_edges:
   for x in edge.verts:
    if x in unseen:unseen.remove(x);stack.append(x)
areas=[(m.vertices[t.vertices[1]].co-m.vertices[t.vertices[0]].co).cross(m.vertices[t.vertices[2]].co-m.vertices[t.vertices[0]].co).length/2 for t in m.loop_triangles];tree=BVHTree.FromPolygons([x.co for x in m.vertices],[tuple(p.vertices) for p in m.polygons]);axis_clear=tree.ray_cast(Vector((0,0,-.01)),Vector((0,0,1)),L+.02)[0] is None
rim_r=(IR+R)/2;rim_hit=tree.ray_cast(Vector((rim_r,0,-.01)),Vector((0,0,1)),L+.02)[0] is not None
report={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'non_manifold_edges':sum(not x.is_manifold for x in bm.edges),'connected_shells':shells,'signed_volume_m3':bm.calc_volume(signed=True),'min_triangle_area_m2':min(areas),'zero_area_triangles_at_1e18_m2':sum(a<=1e-18 for a in areas),'axis_clear':axis_clear,'rim_present':rim_hit,'minimum_wall_lower_bound_m':min(r for z,r in outer)-max(max(r for z,r in inner),IR+thread['working_radial_depth_m']),'related_diameter_not_exact_RDC':True,'all_other_dimensions_estimated':True,'art_accepted':False};assert shells==1 and report['non_manifold_edges']==0 and report['signed_volume_m3']>0 and axis_clear and rim_hit and not report['zero_area_triangles_at_1e18_m2'];bm.free();e.to_mesh_clear()
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.export_scene.gltf(filepath=str(HERE/'front-fork-inner-tube-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_normals=True,export_texcoords=True,export_tangents=True)
w=bpy.data.worlds.new('Neutral tube studio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.26,.29,.34,1);w.node_tree.nodes['Background'].inputs[1].default_value=.45
for name,location,power,size,sy in [('KEY',(.18,.12,.29),12,.06,.7),('FILL',(-.20,.05,.30),6,.10,.6),('EDGE',(.03,-.18,.35),10,.035,.7)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='RECTANGLE';d.size=size;d.size_y=sy;o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=location;o.rotation_euler=(Vector((0,0,L/2))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('TUBE_CAMERA',bpy.data.cameras.new('TUBE_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.55,.85,.39);cam.rotation_euler=(Vector((0,0,L/2))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.63
s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1000;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG';s.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'front-fork-inner-tube-v1.blend'),compress=True);report['source_sha256']=hashlib.sha256((HERE/'front-fork-inner-tube-v1.blend').read_bytes()).hexdigest();report['export_sha256']=hashlib.sha256((HERE/'front-fork-inner-tube-inspection.glb').read_bytes()).hexdigest();(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_TUBE_SOURCE',json.dumps(report))
