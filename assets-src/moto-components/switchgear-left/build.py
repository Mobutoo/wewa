"""JB401400-related candidate, not a certified current RDC control assembly."""
import bpy,bmesh,json,math,shutil,subprocess,tempfile,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=json.loads((HERE/'parameters.json').read_text());OUT=ROOT/'creative/reviews/switchgear-left-v1';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_SWITCHGEAR_LEFT');scene.collection.children.link(source)
construction=bpy.data.collections.new('LH_SWITCH_EDITABLE_CONSTRUCTION');scene.collection.children.link(construction)
studio=bpy.data.collections.new('LH_SWITCH_STUDIO');scene.collection.children.link(studio)
E=Vector(P['bar_endpoint_m']);I=Vector(P['axis_inward_vector']).normalized();Z=Vector((0,0,1));T=I.cross(Z).normalized();basis=Matrix((I,T,Z)).transposed()
def world(q,v,z):return E+I*q+T*v+Z*z
def move(o,c):
 for x in list(o.users_collection):x.objects.unlink(o)
 c.objects.link(o);return o
def mesh(name,verts,faces,col=construction):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free();o=bpy.data.objects.new(name,data);col.objects.link(o);return o
def rounded_profile(points,trim=.003,steps=8):
 # Quadratic corner fillets preserve long flat moulded faces while replacing
 # each photographic silhouette corner by a sampled continuous radius.
 result=[]
 for k,pair in enumerate(points):
  p=Vector(pair);previous=Vector(points[k-1]);nxt=Vector(points[(k+1)%len(points)]);a=previous-p;b=nxt-p
  distance=min(trim,a.length*.28,b.length*.28);start=p+a.normalized()*distance;end=p+b.normalized()*distance
  for j in range(steps+1):
   t=j/steps;point=(1-t)**2*start+2*(1-t)*t*p+t*t*end;result.append(tuple(point))
 return result

def loft(name,scale=1,q0=.121,q1=.166):
 profile=rounded_profile(P['main_shell_cross_vz_m']);verts=[]
 rings=[(q0,.90),(q0+.0005,.947),(q0+.0015,.985),(q0+.003,1),(q1-.003,1),(q1-.0015,.985),(q1-.0005,.947),(q1,.90)]
 for q,s in rings:verts.extend((q,v*s*scale,z*s*scale) for v,z in profile)
 n=len(profile);faces=[tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
 for k in range(len(rings)-1):
  for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
 return mesh(name,verts,faces)
def box(name,loc,dim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=move(bpy.context.object,construction);o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def cyl(name,loc,r,depth,axis='Z'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=r,depth=depth,location=loc);o=move(bpy.context.object,construction);o.name=name;o.rotation_euler=(Vector((1,0,0)) if axis=='X' else Z).to_track_quat('Z','Y').to_euler();return o
def evaluate(o):
 deps=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles();row={'name':o.name,'vertices':[list(o.matrix_world@v.co) for v in m.vertices],'triangles':[list(t.vertices) for t in m.loop_triangles]};e.to_mesh_clear();return row
base=loft('LH switch outer loft - estimated');inner=loft('LH switch interior wall cavity',.82,.124,.163)
bore=cyl('Bar passage 22.5mm working',(.143,0,0),P['working_bar_bore_radius_m'],.09,'X')
features=[cyl('Estimated clamp screw boss'+str(q),(q,-.0165,-.008),.0043,.043) for q in P['working_boss_q_m']]
drills=[inner,bore]
for q in P['working_boss_q_m']:
 drills.extend([cyl('Estimated screw core'+str(q),(q,-.0165,-.008),.0015,.065),cyl('Estimated underside counterbore'+str(q),(q,-.0165,-.030),.003,.018)])
drills.extend([box('Dipper actuator aperture',(.131,.025,.013),(.010,.026,.016)),box('Turn selector slot',(.136,.025,-.008),(.020,.026,.004)),box('Horn actuator lower aperture',(.131,.025,-.035),(.011,.026,.017))])
# Shallow pocket exposes an inset front panel, retaining a real skin floor.
panel=box('Turn selector rectangular inset panel',(.136,.0312,-.009),(.025,.013,.015))
bpy.context.view_layer.objects.active=panel
bevel=panel.modifiers.new('Panel pocket corner radii','BEVEL');bevel.width=.00045;bevel.segments=4;bpy.ops.object.modifier_apply(modifier=bevel.name);drills.append(panel)
for cutter in drills:
 if cutter.type=='MESH' and ('actuator aperture' in cutter.name or 'selector slot' in cutter.name):
  bpy.context.view_layer.objects.active=cutter;edge=cutter.modifiers.new('Intentional aperture cutter lip radius','BEVEL');edge.width=.00025;edge.segments=3;bpy.ops.object.modifier_apply(modifier=edge.name)
N=256;rng=np.random.default_rng(401400);freq=np.fft.fftfreq(N);fx,fy=np.meshgrid(freq,freq);noise=np.fft.ifft2(np.fft.fft2(rng.normal(size=(N,N)))*np.exp(-2*math.pi**2*1.5**2*(fx*fx+fy*fy))).real;noise=(noise-noise.mean())/noise.std();rough=np.clip(.48+.018*noise,.42,.56)
texdir=HERE/'textures';texdir.mkdir(exist_ok=True);image=bpy.data.images.new('Original LH plastic roughness 10mm',width=N,height=N,alpha=False);image.colorspace_settings.name='Non-Color';image.pixels.foreach_set(np.stack((np.ones_like(rough),rough,np.zeros_like(rough),np.ones_like(rough)),axis=-1).astype(np.float32).ravel());image.filepath_raw=str(texdir/'plastic-metallic-roughness.png');image.file_format='PNG';image.save();image.pack()
def mat(name,color,metal,roughness):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=roughness;return m
plastic=mat('LH moulded black polymer - candidate',(.004,.005,.006),0,.48);n=plastic.node_tree.nodes;l=plastic.node_tree.links;t=n.new('ShaderNodeTexImage');t.image=image;s=n.new('ShaderNodeSeparateColor');l.new(t.outputs['Color'],s.inputs['Color']);l.new(s.outputs['Green'],n.get('Principled BSDF').inputs['Roughness']);l.new(s.outputs['Blue'],n.get('Principled BSDF').inputs['Metallic'])
# Original polymer relief at a declared physical scale: procedural estimate,
# not a measured/captured normal map. Height rms4um, tile10mm, slope-derived.
height=noise*.000004;dy,dx=np.gradient(height,.010/N);normal=np.stack((-dx,-dy,np.ones_like(dx)),axis=-1);normal/=np.linalg.norm(normal,axis=-1)[...,None]
normal_image=bpy.data.images.new('Original LH polymer relief 10mm RMS4um',width=N,height=N,alpha=False);normal_image.colorspace_settings.name='Non-Color';normal_image.pixels.foreach_set(np.concatenate((normal*.5+.5,np.ones((N,N,1))),axis=-1).astype(np.float32).ravel());normal_image.filepath_raw=str(texdir/'plastic-normal.png');normal_image.file_format='PNG';normal_image.save();normal_image.pack()
normal_tex=n.new('ShaderNodeTexImage');normal_tex.image=normal_image;normal_node=n.new('ShaderNodeNormalMap');normal_node.space='TANGENT';l.new(normal_tex.outputs['Color'],normal_node.inputs['Color']);l.new(normal_node.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
button=mat('LH buttons satin black',(.009,.011,.013),0,.25);steel=mat('LH estimated screw steel',(.20,.22,.24),.85,.28);ink=mat('LH original white printed markings',(.72,.75,.72),0,.5)
checks=[];objects=[];hist=[]
def physical_uv(data):
 data.update();uv=data.uv_layers.new(name='Physical 10mm box UV')
 for p in data.polygons:
  axis=max(range(3),key=lambda j:abs(p.normal[j]));sign=1 if p.normal[axis]>=0 else -1
  for li in p.loop_indices:
   co=data.vertices[data.loops[li].vertex_index].co;pair=(sign*co.y,co.z) if axis==0 else (-sign*co.x,co.z) if axis==1 else (sign*co.x,co.y);uv.data[li].uv=(pair[0]/.010,pair[1]/.010)
def finish(o,material,width=.00045):
 o.data.materials.append(material);bpy.context.view_layer.objects.active=o
 b=o.modifiers.new('Small moulded edge radius - estimate','BEVEL');b.width=(0 if 'shell - editable' in o.name else width);b.segments=4;b.limit_method='ANGLE';b.angle_limit=.35
 for f in o.data.polygons:f.use_smooth=True
 w=o.modifiers.new('Preserve broad polymer face normals','WEIGHTED_NORMAL');w.keep_sharp=True;w.weight=35
 evaluated=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()),depsgraph=bpy.context.evaluated_depsgraph_get())
 o.modifiers.clear();o.data=evaluated
 # The q/thumb/up frame has negative determinant. Rebuild face winding
 # after transforming original evaluated object coordinates into the shared
 # cockpit, then calculate normals there (do not carry stale local normals).
 coordinates=[tuple(world(*(o.matrix_world@v.co))) for v in o.data.vertices]
 faces=[tuple(p.vertices) for p in o.data.polygons]
 data=bpy.data.meshes.new(o.name+' world evaluated surface');data.from_pydata(coordinates,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free();data.materials.append(material)
 o.data=data;o.matrix_world=Matrix.Identity(4)
 # Boolean/bevel output contains near-coincident slivers below2um. Collapse
 # these construction residues before normals/UV/tangents; geometric features
 # are >=120um. Manifold/connected/positive-volume checks still follow.
 clean=bmesh.new();clean.from_mesh(o.data);bmesh.ops.remove_doubles(clean,verts=list(clean.verts),dist=.000002);bmesh.ops.dissolve_degenerate(clean,dist=.000002,edges=list(clean.edges));bmesh.ops.recalc_face_normals(clean,faces=clean.faces);clean.to_mesh(o.data);clean.free();o.data.update()
 for f in o.data.polygons:f.use_smooth=True
 o.data.set_sharp_from_angle(angle=.50)
 weighted=o.modifiers.new('World space broad face normals','WEIGHTED_NORMAL');weighted.keep_sharp=True;weighted.weight=35;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=weighted.name)
 triangulate=o.modifiers.new('Export-ready triangles preserving custom normals','TRIANGULATE')
 if hasattr(triangulate,'keep_custom_normals'):triangulate.keep_custom_normals=True
 bpy.ops.object.modifier_apply(modifier=triangulate.name)
 physical_uv(o.data);objects.append(o);return o
for half in ['upper','lower']:
 cutter=box('Split plane '+half,(.143,0,-.1 if half=='upper' else .1),(.2,.3,.2+P['working_main_seam_gap_m']))
 # Cutter top/bottom respectively +/-0.15mm, creating a real narrow seam.
 with tempfile.TemporaryDirectory(prefix='wewa-left-switch-') as tmp:
  inp=Path(tmp)/'in.json';out=Path(tmp)/'out.json';inp.write_text(json.dumps({'base':evaluate(base),'features':[evaluate(o) for o in features],'drills':[evaluate(o) for o in drills+[cutter]]}));subprocess.run([shutil.which('python'),str(HERE/'csg_worker.py'),str(inp),str(out)],check=True);r=json.loads(out.read_text())
 hist.append({k:v for k,v in r.items() if k not in ['vertices','triangles']});o=mesh('LH switch '+half+' shell - editable',r['vertices'],r['triangles'],source);finish(o,plastic)

# Controls are separate rigid objects and pivots; travel is a working review
# range, not an electrical or ergonomic qualification.
def actuator(name,centre,dim,bevel=.0007):
 o=box(name,centre,dim);construction.objects.unlink(o);source.objects.link(o);finish(o,button,bevel);return o
# Photographic two-slope rocker: a lower bulge, shallow central fold and
# flatter upper contact face. One rigid watertight part, not two fake buttons.
rocker_profile=[(.025,.006),(.029,.0065),(.032,.010),(.030,.0123),(.030,.019),(.029,.0195),(.025,.0195)]
vertices=[(q,v,z) for q in [.12675,.13525] for v,z in rocker_profile];nr=len(rocker_profile)
faces=[tuple(reversed(range(nr))),tuple(range(nr,2*nr))]+[(j,(j+1)%nr,(j+1)%nr+nr,j+nr) for j in range(nr)]
dipper=mesh('LH dipper rocker - high low',vertices,faces,source);finish(dipper,button,.0004)
turncap=box('Turn cap construction',(.136,.0305,-.008),(.008,.005,.008))
turnstem=box('Turn narrow sliding neck',(.136,.025,-.008),(.005,.011,.0022))
with tempfile.TemporaryDirectory(prefix='wewa-left-turn-') as tmp:
 inp=Path(tmp)/'in.json';out=Path(tmp)/'out.json';inp.write_text(json.dumps({'base':evaluate(turncap),'features':[evaluate(turnstem)],'drills':[]}));subprocess.run([shutil.which('python'),str(HERE/'csg_worker.py'),str(inp),str(out)],check=True);turnshape=json.loads(out.read_text())
turn=mesh('LH turn selector - centre push',turnshape['vertices'],turnshape['triangles'],source);finish(turn,button,.00055)
# The photographed horn tongue has straight shoulders and a U-rounded end.
qcentre=.131;top=-.028;shoulder=-.038;radius=.00475
outline=[(qcentre-radius,top),(qcentre+radius,top),(qcentre+radius,shoulder)]
outline.extend((qcentre+radius*math.cos(a),shoulder+radius*math.sin(a)) for a in np.linspace(0,-math.pi,25)[1:])
verts=[(q,v,z) for v in [.0245,.0315] for q,z in outline];count=len(outline)
faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count)]
horn=mesh('LH horn push tongue',verts,faces,source);finish(horn,button,.00055)
controls=[]
for obj,centre,travel in [(dipper,(.131,.025,.01275),{'rotation_degrees':[-9,9]}),(turn,(.136,.025,-.008),{'slide_metres':[-.003,.003],'push_metres':.0014}),(horn,(.131,.025,-.035),{'push_metres':.0014})]:
 pivot=world(*centre);o=bpy.data.objects.new(obj.name+' PIVOT',None);source.objects.link(o);o.location=pivot;o['review_travel_estimated']=json.dumps(travel);o.matrix_world=Matrix.Translation(pivot)
 for v in obj.data.vertices:v.co-=pivot
 obj.parent=o;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4);controls.append({'object':obj.name,'pivot_world_m':list(pivot),'travel_estimated':travel,'actual_electrical_state_tested':False})

# Two underside screw heads and cross slots, locations not photographically
# verified; visibly qualified estimates in parameters and review.
for q in P['working_boss_q_m']:
 head=cyl('LH underside screw head '+str(q),(q,-.0165,-.0287),.00255,.0014)
 construction.objects.unlink(head);source.objects.link(head)
 for loc,dim in [((q,-.0165,-.0295),(.0036,.00065,.0014)),((q,-.0165,-.0295),(.00065,.0036,.0014))]:
  cut=box('Cross slot cutter',loc,dim);bpy.context.view_layer.objects.active=head;mod=head.modifiers.new('Recessed screw drive','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name)
 finish(head,steel,.00012)

skin_trees=[BVHTree.FromPolygons([v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]) for o in source.objects if o.type=='MESH' and 'shell - editable' in o.name]
def surface(q,z):
 start=world(q,.10,z);hits=[t.ray_cast(start,-T,.15) for t in skin_trees];hits=[h for h in hits if h[0] is not None]
 assert hits,('No polymer face under authored marking',q,z)
 hit=min(hits,key=lambda h:h[3]);return hit[0]+hit[1]*.00005
rotation=Matrix((I,Z,T)).transposed().to_4x4()
def label(text,q,z,size=.003):
 curve=bpy.data.curves.new('Original marking '+text,'FONT');curve.body=text;curve.size=size;curve.extrude=.000018;curve.align_x='LEFT';curve.align_y='CENTER';o=bpy.data.objects.new('LH print '+text,curve);source.objects.link(o);o.matrix_world=rotation;o.location=surface(q,z);o.data.materials.append(ink);bpy.context.view_layer.update()
 # Project each glyph vertex, not only the baseline, onto the curved skin.
 # Preserve authored extruded print thickness as a separate normal offset.
 data=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()),depsgraph=bpy.context.evaluated_depsgraph_get());transform=o.matrix_world.copy()
 for vertex in data.vertices:
  original=vertex.co.copy();point=transform@original;offset=point-E;vertex.co=surface(offset.dot(I),offset.z)+T*original.z
 baked=bpy.data.objects.new(o.name+' projected mesh',data);source.objects.link(baked);baked['printed_marking']=True;bpy.data.objects.remove(o,do_unlink=True);objects.append(baked);return baked
label('TURN',.133,.003,.0025)
def line(name,points,r=.00012):
 c=bpy.data.curves.new('Original marking curve '+name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,(q,z) in zip(s.points,points):p.co=(*surface(q,z),1)
 o=bpy.data.objects.new('LH print '+name,c);source.objects.link(o);o.data.materials.append(ink);objects.append(o)
for z,angle in [(.014,0),(.006,-.0007)]:
 line('beam housing '+str(z),[(.145,z-.0015),(.147,z-.0015),(.148,z),(.147,z+.0015),(.145,z+.0015),(.145,z-.0015)])
 for k in range(3):line('beam ray '+str(z)+' '+str(k),[(.1432,z-.001+k*.001),(.1408,z-.001+k*.001+angle)])
line('left arrow',[(.130,.003),(.126,.003),(.1275,.0045),(.126,.003),(.1275,.0015)])
line('right arrow',[(.146,.003),(.150,.003),(.1485,.0045),(.150,.003),(.1485,.0015)])
line('horn',[(.130,-.0215),(.133,-.0215),(.135,-.0205),(.135,-.0230),(.133,-.0220),(.130,-.0220),(.130,-.0215)])
line('horn lower loop',[(.1305,-.022),(.131,-.023),(.132,-.0232),(.133,-.022)])

# Exclude construction and validate every actual rigid body before exporting.
for o in construction.objects:o.hide_render=True;o.hide_set(True)
for o in source.objects:
 if o.type!='MESH' or o.get('printed_marking'):continue
 bm=bmesh.new();bm.from_mesh(o.data);unseen=set(bm.verts);shells=0
 while unseen:
  shells+=1;pending=[unseen.pop()]
  while pending:
   for edge in pending.pop().link_edges:
    for v in edge.verts:
     if v in unseen:unseen.remove(v);pending.append(v)
 report={'object':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'shells':shells,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True)}
 assert shells==1 and report['non_manifold_edges']==0 and report['signed_volume_m3']>0,report
 checks.append(report);bm.free()
shells=[o for o in source.objects if o.type=='MESH' and 'shell - editable' in o.name]
deps=bpy.context.evaluated_depsgraph_get();trees=[BVHTree.FromObject(o,deps) for o in shells];origin=world(.10,0,0);axis_probe=[t.ray_cast(origin,I,.09)[0] is None for t in trees];assert all(axis_probe),axis_probe
bpy.ops.object.select_all(action='DESELECT')
for o in source.objects:o.select_set(True)
bpy.context.view_layer.objects.active=shells[0];bpy.ops.export_scene.gltf(filepath=str(HERE/'switchgear-left-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True)
subprocess.run(['node',str(HERE/'finalize_export.mjs')],cwd=str(ROOT),check=True)

floor_mat=mat('LH switch studio slate',(.09,.105,.12),0,.8)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.0615));floor=move(bpy.context.object,studio);floor.data.materials.append(floor_mat)
target=world(.143,.002,-.008)
worlddata=bpy.data.worlds.new('LH switch neutral world');scene.world=worlddata;worlddata.use_nodes=True;worlddata.node_tree.nodes['Background'].inputs[0].default_value=(.30,.34,.40,1);worlddata.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,pos,power,size in [('LH_KEY',target+T*.18+Z*.26+I*.04,3,.22),('LH_FILL',target-T*.18+Z*.16,2,.20),('LH_EDGE',target+I*.18+Z*.15,3,.16)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=pos;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('LH_SWITCH_CAMERA',bpy.data.cameras.new('LH_SWITCH_CAMERA'));studio.objects.link(cam);scene.camera=cam;cam.location=target+T*.21+Z*.10+I*.08;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=80
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE';scene.cycles.denoising_use_gpu=False;scene.view_layers[0].cycles.denoising_store_passes=True;scene.render.resolution_x=1100;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'switchgear-left-v1.blend'),compress=True)
report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':hashlib.sha256((HERE/'switchgear-left-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'switchgear-left-inspection.glb').read_bytes()).hexdigest(),'checks':checks,'bar_axis_clear_in_both_shells':axis_probe,'controls':controls,'CSG':hist,'datum':{'endpoint_m':list(E),'inward_axis':list(I),'thumb_side_radial':list(T),'left_is_positive_X':True},'all_dimensions_estimated':True,'exact_current_RDC_identity_confirmed':False,'functional_electrical_controls':False,'accepted_art':False}
(HERE/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_LH_SWITCH_CHECK',json.dumps(report))
