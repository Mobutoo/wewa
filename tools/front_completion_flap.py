"""Related PF181430 isolated external-form study; all dimensions bounded estimates."""
import bpy,math,json,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');H=R/'assets-src/moto-components/front-completion-p03-flap-v1';O=R/'creative/reviews/front-completion-p03-flap-v1';H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
P={'reference':'PF181430 related seller-labelled three-hole Boxer150 flap; not certified current RDC or DF161245','length_m':.245,'length_bounds_m':[.19,.30],'width_max_m':.09,'width_bounds_m':[.07,.115],'thickness_m':.003,'thickness_bounds_m':[.002,.005],'hole_radius_m':.0035,'hole_radius_bounds_m':[.0025,.005],'hole_centres_m':[[0,.012],[-.021,.038],[.021,.038]],'channel_depth_m':.012,'channel_depth_bounds_m':[.007,.02],'surface':'longitudinally curved channel with raised side shoulders and rounded lower paddle; simplified unseen reverse','all_dimensions_estimated':True,'mounted_fit':False,'markings':'small moulded symbol visible but unreadable; not invented'}
(H/'parameters.json').write_text(json.dumps(P,indent=2));bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
# Width stations constrain the observed narrow perforated tongue, flared shoulders,
# long shallow channel, and round lower paddle. Smooth cosine spans, no generic primitive.
st=[(0,.021),(.10,.029),(.19,.043),(.52,.039),(.70,.037),(.79,.044),(.84,.043)]
def width(t):
 if t>=.84:return .043*math.sqrt(max(.0001,1-((t-.84)/.16)**2))
 for (a,x),(b,y) in zip(st,st[1:]):
  if a<=t<=b:return x+(y-x)*(.5-.5*math.cos(math.pi*(t-a)/(b-a)))
 return st[0][1]
N=200;M=80;v=[];f=[]
for i in range(N+1):
 t=i/N;w=width(t)
 for j in range(M+1):
  q=-1+2*j/M;x=w*q;y=t*.245
  ramp=.5-.5*math.cos(math.pi*min(1,max(0,(t-.12)/.10)))
  fade=1-(.5-.5*math.cos(math.pi*min(1,max(0,(t-.69)/.13))))
  shoulder=.012*(abs(q)**5)*ramp*fade
  z=.016*math.sin(math.pi*t*.85)+shoulder+.004*(1-q*q)*math.sin(math.pi*t)
  v.append((x,y,z))
for i in range(N):
 for j in range(M):
  a=i*(M+1)+j;f.append((a,a+1,a+M+2,a+M+1))
m=bpy.data.meshes.new('Authored channel and tongue surface');m.from_pydata(v,[],f);m.update();ob=bpy.data.objects.new('PF181430_RELATED_FLAP_CHANNEL_TONGUE',m);bpy.context.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob;ob.select_set(True)
uv=m.uv_layers.new(name='Original planar metric UV')
for p in m.polygons:
 p.use_smooth=True
 for li in p.loop_indices:
  co=m.vertices[m.loops[li].vertex_index].co;uv.data[li].uv=(co.x/.02,co.y/.02)
sol=ob.modifiers.new('Estimated finite reverse thickness','SOLIDIFY');sol.thickness=.003;sol.offset=-1;bpy.ops.object.modifier_apply(modifier=sol.name)
for k,(x,y) in enumerate(P['hole_centres_m']):
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=P['hole_radius_m'],depth=.1,location=(x,y,.015));cut=bpy.context.object;cut.name='Temporary hole cutter';bpy.context.view_layer.objects.active=ob
 mod=ob.modifiers.new('Observed through hole '+str(k+1),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-10);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
mat=bpy.data.materials.new('Gray before material review');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.25,.25,.25,1);bs.inputs['Roughness'].default_value=.32;ob.data.materials.append(mat)
ob['study_only']=True;ob['all_dimensions_estimated']=True;ob['source_photo_private']=True;ob['mounted_fit']=False
s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1400;s.render.resolution_y=1000;s.view_settings.view_transform='AgX'
w=bpy.data.worlds.new('Neutral studio');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.25,.25,.25,1);w.node_tree.nodes['Background'].inputs[1].default_value=.4;s.world=w
for name,loc,power,size in [('KEY',(.15,-.1,.4),12,.23),('FILL',(-.2,.2,.3),8,.2),('RIM',(.05,.4,.15),10,.15)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,.12,0))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Study camera',bpy.data.cameras.new('Study camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.37;cam.data.clip_start=.001;cam.data.clip_end=10;cam.location=(.25,-.15,.4);cam.rotation_euler=(Vector((0,.12,0))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
ob.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(ob.data);report={'vertices':len(bm.verts),'triangles':len(ob.data.loop_triangles),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True),'minimum_triangle_area_m2':min(t.area for t in ob.data.loop_triangles),'dimensions_m':list(ob.dimensions),'all_dimensions_estimated':True,'reverse':'simple thickness estimate; no unseen retaining features','art_accepted':False};bm.free();print('SOURCE_AUDIT',report,flush=True);assert report['nonmanifold_edges']==0 and report['volume_m3']>0 and report['minimum_triangle_area_m2']>1e-18
bpy.ops.wm.save_as_mainfile(filepath=str(H/'flap-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'flap-gray.glb'),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False)
(O/'geometry-check.json').write_text(json.dumps(report,indent=2))
