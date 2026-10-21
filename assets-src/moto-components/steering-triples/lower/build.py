"""Original lower casting, relatedDS181020; stem and bolts deliberately separate."""
import bpy,bmesh,json,math,hashlib,tempfile,subprocess,shutil
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];P=json.loads((HERE/'parameters.json').read_text());OUT=ROOT/'creative/reviews/steering-lower-v1';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('WEWA_STEERING_LOWER_BODY_ISOLATED');s.collection.children.link(col);construction=bpy.data.collections.new('LOWER_ORIGINAL_VOLUMES_AND_CUTTERS');s.collection.children.link(construction);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
def obj(name,vs,fs):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);construction.objects.link(o);return o
def curve(land,steps=7):
 land=[Vector(v) for v in land];res=[]
 for i in range(len(land)):
  a,b,c,d=[land[j%len(land)] for j in [i-1,i,i+1,i+2]]
  for k in range(steps):
   t=k/steps;res.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 return res
def prism(name,outline,z0,z1):
 n=len(outline);vs=[(q.x,q.y,z) for z in [z0,z1] for q in outline];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return obj(name,vs,fs)
def lathe(name,c,profile,N=192):
 v=[(c[0]+r*math.cos(math.tau*j/N),c[1]+r*math.sin(math.tau*j/N),z) for r,z in profile for j in range(N)];f=[(k*N+j,k*N+(j+1)%N,((k+1)%len(profile))*N+(j+1)%N,((k+1)%len(profile))*N+j) for k in range(len(profile)) for j in range(N)];return obj(name,v,f)
def cylinder(name,r,depth,loc,axis='Z'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=r,depth=depth,location=loc);o=bpy.context.object
 for c in list(o.users_collection):c.objects.unlink(o)
 construction.objects.link(o);o.name=name
 if axis=='X':o.rotation_euler.y=math.pi/2
 return o
def box(name,dimensions,loc):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object
 for c in list(o.users_collection):c.objects.unlink(o)
 construction.objects.link(o);o.name=name;o.scale=dimensions;return o
outline=curve([[-.098,.015],[-.073,.024],[-.051,.035],[-.028,.051],[-.021,.059],[-.012,.065],[0,.068],[.012,.065],[.021,.059],[.028,.051],[.051,.035],[.073,.024],[.098,.015],[.098,-.012],[.076,-.009],[.053,0],[.035,.008],[.031,.005],[.028,0],[.023,-.002],[.017,0],[.014,.006],[.011,.008],[-.011,.008],[-.014,.006],[-.017,0],[-.023,-.002],[-.028,0],[-.031,.005],[-.035,.008],[-.053,0],[-.076,-.009],[-.098,-.012]])
base=prism('Original broad bridge contour',outline,P['web_bottom_z_m'],P['web_top_z_m']);bevel=base.modifiers.new('Original cast perimeter radius before union','BEVEL');bevel.width=.00065;bevel.segments=4;bevel.limit_method='ANGLE';bevel.angle_limit=.5;features=[];drills=[];axial=[]
for side,cx in [('left',-.0875),('right',.0875)]:
 ir=P['fork_bore_radius_working_m']-.0002;ro=P['fork_ring_outer_radius_m'];profile=[(ir,-.007),(ir+.0004,-.0075),(ro-.0007,-.0075),(ro-.00015,-.0072),(ro,-.0065),(ro,.0065),(ro-.00015,.0072),(ro-.0007,.0075),(ir+.0004,.0075),(ir,.0071)];features.append(lathe('Original rounded split-ring '+side,(cx,0),profile))
 ear=cylinder('Original tightening ear barrel '+side,.0085,.025,(cx,.021,0),'X');bevel=ear.modifiers.new('Original ear end radius before union','BEVEL');bevel.width=.0006;bevel.segments=4;bevel.limit_method='ANGLE';bevel.angle_limit=.5;features.append(ear)
 drills.append(box('True radial split '+side,(P['fork_split_width_m'],.05,.05),(cx,.031,0)));drills.append(cylinder('RelatedM10 candidate tightening bore '+side,.0052,.035,(cx+(-.0025 if cx<0 else .0025),.021,0),'X'))
 drills.append(cylinder('True fork bore '+side,P['fork_bore_radius_working_m'],.08,(cx,0,0)));axial.append({'name':'fork_'+side,'centre_m':[cx,0,0],'radius_m_estimated':P['fork_bore_radius_working_m']})
c=P['stem_centre_working_m'];ir=P['stem_bore_radius_working_m']-.0002;ro=P['stem_seat_outer_radius_m'];features.append(lathe('Original central stem seat collar',c,[(ir,-.0045),(ro-.001,-.0045),(ro,-.0035),(ro,.0065),(ro-.0005,.008),(ro-.0015,.009),(ir+.0005,.009),(ir,.0085)]));drills.append(cylinder('True central stem passage',P['stem_bore_radius_working_m'],.08,(c[0],c[1],0)));axial.append({'name':'stem','centre_m':c,'radius_m_estimated':P['stem_bore_radius_working_m']})
for i,c in enumerate(P['small_boss_centres_m']):
 boss=cylinder('Observed small edge boss '+str(i+1),.0056,.010,c);bevel=boss.modifiers.new('Original boss edge radius before union','BEVEL');bevel.width=.00035;bevel.segments=3;bevel.limit_method='ANGLE';bevel.angle_limit=.5;features.append(boss);drills.append(cylinder('Visible small aperture '+str(i+1),P['small_bore_radius_working_m'],.08,c));axial.append({'name':'small_'+str(i+1),'centre_m':c,'radius_m_estimated':P['small_bore_radius_working_m']})
for side in [-1,1]:
 x=side*.0315;y=.031;v=[(x+dx,y+dy,z) for z,half,shift in [(.0035,.005,0),(.016,.0038,.0015)] for dx,dy in [(-half,-.003+shift),(half,-.003+shift),(half,.003+shift),(-half,.003+shift)]];f=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];o=obj('Observed tapered projection '+str(side)+' - function unconfirmed',v,f);b=o.modifiers.new('Original projection edge radius before union','BEVEL');b.width=.0006;b.segments=3;features.append(o)
# Two separately bounded recesses preserve the real underside rib network.
pocket=[[-.075,.006],[-.056,.017],[-.034,.032],[-.026,.043],[-.022,.042],[-.020,.032],[-.012,.026],[-.012,.020],[-.022,.018],[-.034,.015],[-.045,.009],[-.061,.001],[-.073,-.002]]
for side in [-1,1]:
 path=curve([[abs(x)*side,y] for x,y in pocket],8);o=prism('Original underside recessed panel '+str(side),path,-.030,P['pocket_floor_z_m']);b=o.modifiers.new('Rounded recess lip before subtraction','BEVEL');b.width=.0007;b.segments=4;drills.append(o)
def volume(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();r={'name':o.name,'vertices':[list(o.matrix_world@v.co) for v in m.vertices],'triangles':[list(t.vertices) for t in m.loop_triangles]};e.to_mesh_clear();return r
with tempfile.TemporaryDirectory(prefix='wewa-lower-cast-') as t:
 inp=Path(t)/'in.json';out=Path(t)/'out.json';inp.write_text(json.dumps({'base':volume(base),'features':[volume(o) for o in features],'drills':[volume(o) for o in drills]}));subprocess.run([shutil.which('python'),str(ROOT/'assets-src/moto-components/front-brake-plate/csg.py'),str(inp),str(out)],check=True);fused=json.loads(out.read_text())
o=obj('Lower steering casting only - relatedDS181020 candidate',fused['vertices'],fused['triangles']);construction.objects.unlink(o);col.objects.link(o);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();o.data.update()
for f in o.data.polygons:f.use_smooth=abs(f.normal.z)<.99995
o.data.set_sharp_from_angle(angle=.65);m=bpy.data.materials.new('Neutral geometry review - not final coating');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.22,.24,.26,1);p.inputs['Metallic'].default_value=.15;p.inputs['Roughness'].default_value=.28;o.data.materials.append(m);tri=o.modifiers.new('Evaluated export triangulation','TRIANGULATE');tri.keep_custom_normals=True
for x in construction.objects:x.hide_render=True;x.hide_set(True)
e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=e.to_mesh();mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;stack=[unseen.pop()]
 while stack:
  for ed in stack.pop().link_edges:
   for v in ed.verts:
    if v in unseen:unseen.remove(v);stack.append(v)
areas=[(mesh.vertices[t.vertices[1]].co-mesh.vertices[t.vertices[0]].co).cross(mesh.vertices[t.vertices[2]].co-mesh.vertices[t.vertices[0]].co).length/2 for t in mesh.loop_triangles];tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(f.vertices) for f in mesh.polygons]);probes=[]
for h in axial:
 x,y,z=h['centre_m'];clear=tree.ray_cast(Vector((x,y,.04)),Vector((0,0,-1)),.08)[0] is None;assert clear,h;probes.append({**h,'clear':clear})
slotprobes=[]
for x in [-.0875,.0875]:
 clear=tree.ray_cast(Vector((x,.055,0)),Vector((0,-1,0)),.045)[0] is None;assert clear;slotprobes.append({'centre_x_m':x,'clear':clear})
r={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'non_manifold_edges':sum(not ed.is_manifold for ed in bm.edges),'connected_shells':shells,'signed_volume_m3':bm.calc_volume(signed=True),'zero_area_triangles_at_1e18_m2':sum(a<=1e-18 for a in areas),'min_triangle_area_m2':min(areas),'open_passages':probes,'true_radial_splits':slotprobes,'underside_recesses':2,'stem_bolts_bearings_included':False,'hidden_pocket_depth_estimated':True,'small_internal_threads_modelled':False,'manufacturing_process_verified':False,'current_RDC_identity_verified':False,'installed_pose_applied':False,'art_accepted':False,'nonmanifold_edge_detail':[{'ends_m':[list(v.co) for v in ed.verts],'face_count':len(ed.link_faces)} for ed in bm.edges if not ed.is_manifold]};(OUT/'preflight-diagnostic.json').write_text(json.dumps(r,indent=2)+'\n');assert shells==1 and not r['non_manifold_edges'] and not r['zero_area_triangles_at_1e18_m2'] and r['signed_volume_m3']>0,r;bm.free();e.to_mesh_clear()
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.gltf(filepath=str(HERE/'steering-lower-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True)
w=bpy.data.worlds.new('Lower cast neutral studio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.45
for name,loc,power,size in [('KEY',(.12,-.15,.30),2,.25),('FILL',(-.20,.12,.18),1,.22),('EDGE',(.18,-.15,-.25),1,.20)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;x=bpy.data.objects.new(name,d);studio.objects.link(x);x.location=loc;x.rotation_euler=(Vector((0,.025,0))-x.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('LOWER_CAMERA',bpy.data.cameras.new('LOWER_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.13,-.21,.23);cam.rotation_euler=(Vector((0,.025,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.28;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG';bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'steering-lower-v1.blend'),compress=True);r['source_sha256']=hashlib.sha256((HERE/'steering-lower-v1.blend').read_bytes()).hexdigest();r['export_sha256']=hashlib.sha256((HERE/'steering-lower-inspection.glb').read_bytes()).hexdigest();(OUT/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_STEERING_LOWER',json.dumps(r))
