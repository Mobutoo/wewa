"""Profiled related-variant clamp candidates, documentary estimates explicit.
Original geometry; reference photographs are never textures.
"""
import bpy,bmesh,json,math,hashlib,tempfile,subprocess,shutil
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
cleanup_rows=[]
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/handlebar-clamps-v1';P=json.loads((HERE/'parameters.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_HANDLEBAR_CLAMPS_SEPARATE_PARTS');scene.collection.children.link(source)
construction=bpy.data.collections.new('CLAMP_ORIGINAL_PROFILES_AND_CUTTERS');scene.collection.children.link(construction)
studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');scene.collection.children.link(studio)
def move(o,c):
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o);return o
def mat(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;m.diffuse_color=(*color,1);return m
cast=mat('Clamp silver cast coating - estimated',(.18,.20,.22),.72,.32);steel=mat('Clamp zinc-like steel - estimated',(.38,.40,.43),.92,.25)
def mesh_obj(name,vs,fs,collection=construction,material=cast):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);collection.objects.link(o);m.materials.append(material);return o
def profile(name,points,half):
 n=len(points);vs=[(x,y,z) for x in [-half,half] for y,z in points];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return mesh_obj(name,vs,fs)
def cyl(name,centre,r,depth,axis='Z',n=128,material=cast):
 bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=depth,location=centre);o=move(bpy.context.object,construction);o.name=name
 if axis=='X':o.rotation_euler.y=math.pi/2
 o.data.materials.append(material);return o
def bevel(o,width=.0006):
 b=o.modifiers.new('Cast edge radii - estimated','BEVEL');b.width=width;b.segments=4;b.limit_method='ANGLE';b.angle_limit=.35
def volume(o):
 dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();r={'name':o.name,'vertices':[list(o.matrix_world@v.co) for v in m.vertices],'triangles':[list(t.vertices) for t in m.loop_triangles]};e.to_mesh_clear();return r
def fuse(name,base,features,drills,material):
 with tempfile.TemporaryDirectory(prefix='wewa-clamp-') as temp:
  inp=Path(temp)/'in.json';out=Path(temp)/'out.json';inp.write_text(json.dumps({'base':volume(base),'features':[volume(x) for x in features],'drills':[volume(x) for x in drills]}));subprocess.run([shutil.which('python'),str(HERE.parent/'front-brake-plate/csg.py'),str(inp),str(out)],check=True);d=json.loads(out.read_text())
 o=mesh_obj(name,d['vertices'],d['triangles'],source,material);bevel(o,.00045)
 # Evaluate edge treatment before technical checks/export; retain the original
 # fused source + bevel object hidden for later edits, without pretending live CSG.
 dg=bpy.context.evaluated_depsgraph_get();mesh=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);backup=o.copy();backup.data=o.data.copy();backup.name=name+' - bevel construction';construction.objects.link(backup);backup.hide_render=True;backup.hide_set(True);o.modifiers.clear();o.data=mesh
 # Bake the original weighted CORNER normals before welding vertices. Face-loop
 # data carries each normal through cleanup, so old hard/smooth boundaries are
 # preserved instead of re-smoothing across newly welded seams.
 for face in mesh.polygons:face.use_smooth=True
 wn=o.modifiers.new('Original weighted casting normals before weld','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=50;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();normal_mesh=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);o.modifiers.clear();o.data=normal_mesh;mesh=normal_mesh;mesh.update();old_corner_normals=[n.vector.copy().normalized() for n in mesh.corner_normals];old_face_corners=[[(mesh.vertices[mesh.loops[li].vertex_index].co.copy(),old_corner_normals[li]) for li in face.loop_indices] for face in mesh.polygons]
 # Evaluating bevel on CSG seams can produce coincident zero-area skin faces.
 # Weld only within0.1micrometre, preserve original profiles and boolean solids.
 bm=bmesh.new();bm.from_mesh(mesh);bm.faces.ensure_lookup_table();layer=bm.loops.layers.float_vector.new('WeightedCornerNormalBeforeWeld');faceid=bm.faces.layers.int.new('WeightedNormalSourceFace')
 for face in bm.faces:
  face[faceid]=face.index
  for loop,li in zip(face.loops,mesh.polygons[face.index].loop_indices):loop[layer]=old_corner_normals[li]
 oldv=[v.co.copy() for v in bm.verts];oldf=len(bm.faces);oldvol=bm.calc_volume(signed=True);oldarea=sum(f.calc_area() for f in bm.faces);kd=KDTree(len(oldv))
 for i,v in enumerate(oldv):kd.insert(v,i)
 kd.balance();bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);maxshift=max(kd.find(v.co)[2] for v in bm.verts);newvol=bm.calc_volume(signed=True);newarea=sum(f.calc_area() for f in bm.faces);nm=sum(not e.is_manifold for e in bm.edges)
 row={'name':name,'old_vertices':len(oldv),'old_faces':oldf,'new_vertices':len(bm.verts),'new_faces':len(bm.faces),'max_retained_vertex_shift_m':maxshift,'relative_volume_change':abs(newvol/oldvol-1),'relative_surface_area_change':abs(newarea/oldarea-1),'non_manifold_edges_after':nm};assert nm==0 and maxshift<1.1e-7 and row['relative_volume_change']<1e-5 and row['relative_surface_area_change']<1e-5,row;max_corner_position_match=0
 for face in bm.faces:
  for loop in face.loops:
   co,normal=min(old_face_corners[face[faceid]],key=lambda item:(item[0]-loop.vert.co).length_squared);distance=(co-loop.vert.co).length;max_corner_position_match=max(max_corner_position_match,distance);assert distance<1.1e-7;loop[layer]=normal
 normal_boundaries=0
 for edge in bm.edges:
  if len(edge.link_faces)==2:
   split=False
   for v in edge.verts:
    normals=[next(loop[layer] for loop in face.loops if loop.vert==v) for face in edge.link_faces]
    if (normals[0]-normals[1]).length>1e-4:split=True
   if split:edge.smooth=False;normal_boundaries+=1
 row['preserved_normal_discontinuity_edges']=normal_boundaries;row['maximum_source_face_corner_position_match_m']=max_corner_position_match
 bm.to_mesh(mesh);bm.free();mesh.update()
 for face in mesh.polygons:face.use_smooth=True
 # Preserve the original smooth/sharp sectors; recompute with the same weighting
 # on the cleaned surface. No interpolated packed-normal transfer or export fix.
 mesh.normals_split_custom_set([(0,0,0)]*len(mesh.loops));w=o.modifiers.new('Weighted normals in preserved original sectors','WEIGHTED_NORMAL');w.keep_sharp=True;w.weight=50
 row['normal_method']='Original face-corner discontinuities restored; same WeightedNormal50 recomputed in preserved sectors';cleanup_rows.append(row)
 return o
# Smooth the observed outer outline in its own YZ plane before extrusion.
# Straight split face is kept exactly flat; no non-planar cap trickery.
land=[Vector(p) for p in P['casting_outer_profile_yz_m']];profile_points=[]
for i in range(len(land)-1):
 a,b,c,d=land[max(0,i-1)],land[i],land[i+1],land[min(len(land)-1,i+2)]
 for k in range(8):
  t=k/8;q=.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t);profile_points.append((q.x,max(.0003,q.y)))
profile_points.append(tuple(land[-1]));upper_base=profile('Upper saddle outlined casting',profile_points,P['clamp_half_width_x_m']);bevel(upper_base,.0012)
lower_base=profile('Lower saddle outlined casting',[(y,-z) for y,z in profile_points],P['clamp_half_width_x_m']);bevel(lower_base,.0012)
bar=cyl('Candidate tube contact bore',(0,0,0),P['tube_bore_radius_m'],.045,'X')
holes=[cyl('M6 passage '+str(i),(0,y,0),P['bolt_clearance_radius_m'],.080) for i,y in enumerate(P['bolt_centres_y_m'])]
# Small flat seats visible at the bolt ears; depth and spot-face diameter estimated.
seats=[cyl('Upper bolt seat '+str(i),(0,y,.0275),.0066,.035) for i,y in enumerate(P['bolt_centres_y_m'])]
upper=fuse('Clamp upper saddle candidate',upper_base,[],[bar]+holes+seats,cast)
# The stud is a continuous closed volume. Only its exposed part has original
# helical radial relief; pitch/profile are visual estimates, not an M10 gauge.
n=96;layers=160;vs=[]
for k in range(layers+1):
 z=-.018-k/layers*.040
 for j in range(n):
  phi=math.tau*j/n;phase=((z+.057)/P['stem_thread_pitch_working_m']-phi/math.tau)%1
  ridge=max(0,1-abs(phase-.5)/.40);r=.0043+.0007*ridge if z<-.028 else .005
  if z<-.057:r*=1-(abs(z+.057)/.001)*.08
  vs.append((r*math.cos(phi),r*math.sin(phi),z))
fs=[tuple(reversed(range(n))),tuple(range(layers*n,(layers+1)*n))]+[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for k in range(layers) for j in range(n)]
stud=mesh_obj('Lower stud - estimated helical exterior',vs,fs,material=steel)
# Related Matriz photo shows a small recess in the lower bore seat; its
# function, diameter and depth remain unknown. Original shallow spherical cut.
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=.0025,location=(0,0,-.0102));recess=move(bpy.context.object,construction);recess.name='Observed lower bore shallow recess - dimensions estimated'
lower=fuse('Clamp lower saddle with stud candidate',lower_base,[stud],[bar,recess]+holes,cast)
lower.data.materials.append(steel)
for p in lower.data.polygons:
 if p.center.z<-.024:p.material_index=1
# Bolts: separate shaft, flange and chamfered hex body. Hidden screw threads and
# exact OEM head marks are deliberately not fabricated as unverified details.
shaft=cyl('M6 working bolt shaft',(0,0,-.002),.003,.026,material=steel);flange=cyl('M6 working flange',(0,0,.011),.0063,.002,material=steel);hexhead=cyl('M6 working hex head',(0,0,.0148),.0057735,.006,n=6,material=steel);bevel(hexhead,.00045)
bolt=fuse('Clamp flange bolt candidate',shaft,[flange,hexhead],[],steel)
objects=[]
for side,x in [('L',.045),('R',-.045)]:
 for proto,kind in [(upper,'upper'),(lower,'lower')]:
  o=proto.copy();o.data=proto.data.copy();o.name='Handlebar clamp '+side+' '+kind;source.objects.link(o);o.location.x=x;o['component_id']=P['component_id'];o['part_dimensions_estimated']=True;objects.append(o)
 for i,y in enumerate(P['bolt_centres_y_m']):
  o=bolt.copy();o.data=bolt.data.copy();o.name='Handlebar clamp '+side+' bolt '+str(i+1);source.objects.link(o);o.location=(x,y,0);objects.append(o)
for o in [upper,lower,bolt]:source.objects.unlink(o);construction.objects.link(o)
for o in construction.objects:o.hide_render=True;o.hide_set(True)

dg=bpy.context.evaluated_depsgraph_get();checks=[]
for o in objects:
 e=o.evaluated_get(dg);m=e.to_mesh();bm=bmesh.new();bm.from_mesh(m);unseen=set(bm.verts);shells=0
 while unseen:
  shells+=1;pending=[unseen.pop()]
  while pending:
   for edge in pending.pop().link_edges:
    for v in edge.verts:
     if v in unseen:unseen.remove(v);pending.append(v)
 row={'name':o.name,'vertices':len(m.vertices),'faces':len(m.polygons),'non_manifold_edges':sum(not ed.is_manifold for ed in bm.edges),'shells':shells,'signed_volume_m3':bm.calc_volume(signed=True),'world_location':list(o.location)}
 assert row['non_manifold_edges']==0 and shells==1 and row['signed_volume_m3']>0,row
 if 'bolt' not in o.name:
  tree=BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);probe_z=.005 if 'upper' in o.name else -.005;row['tube_bore_short_ray_clear']=tree.ray_cast(Vector((-.020,0,probe_z)),Vector((1,0,0)),.040)[0] is None;row['bolt_passages_clear']=[tree.ray_cast(Vector((0,y,.040)),Vector((0,0,-1)),.120)[0] is None for y in P['bolt_centres_y_m']];assert row['tube_bore_short_ray_clear'] and all(row['bolt_passages_clear']),row
 checks.append(row);bm.free();e.to_mesh_clear()
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.export_scene.gltf(filepath=str(HERE/'handlebar-clamps-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True)
floor_mat=mat('Clamp studio neutral',(.065,.075,.09),0,.7);bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.059));floor=move(bpy.context.object,studio);floor.name='CLAMPS_FLOOR';floor.data.materials.append(floor_mat)
world=bpy.data.worlds.new('Clamp neutral studio');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.36,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,location,power,size in [('CLAMPS_KEY',(.15,.05,.35),7,.30),('CLAMPS_FILL',(-.2,.1,.20),4,.25),('CLAMPS_EDGE',(.05,-.2,.2),6,.22)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=location;o.rotation_euler=(Vector((0,0,-.01))-o.location).to_track_quat('-Z','Y').to_euler()
camera=bpy.data.objects.new('CLAMPS_CAMERA',bpy.data.cameras.new('CLAMPS_CAMERA'));studio.objects.link(camera);scene.camera=camera;camera.location=(.30,.32,.23);camera.rotation_euler=(Vector((0,0,-.015))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=70
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE';scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'handlebar-clamps-v1.blend'),compress=True)
report={'component_id':P['component_id'],'source_sha256':hashlib.sha256((HERE/'handlebar-clamps-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'handlebar-clamps-inspection.glb').read_bytes()).hexdigest(),'objects':checks,'evaluated_seam_cleanup':cleanup_rows,'visible_parts':{'upper_saddles':2,'lower_saddles_with_stud':2,'flange_bolts':4},'catalogue_thread_status':'M6 and M10 related variant documented, lengths/pitch/profile estimated','clamp_to_tube_nominal_radial_clearance_m':.00007,'installed_preload_and_stack_verified':False,'female_threads_modelled':False,'dampers_nyloc_nuts_and_lower_washers_modelled':False,'all_dimensions_estimated':True,'art_accepted':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_CLAMPS_SOURCE',json.dumps(report))
