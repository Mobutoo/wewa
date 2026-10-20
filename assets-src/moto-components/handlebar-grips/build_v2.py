"""Original separate rubber grip envelopes. Every grip dimension is estimated.
Run Blender --threads 2 --python-exit-code 1. No reference photo texture.
"""
import hashlib,json,math
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=json.loads((HERE/'parameters-v2.json').read_text())
OUT=ROOT/'creative/reviews/handlebar-grips-v2';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_HANDLEBAR_GRIP_ENVELOPES');scene.collection.children.link(source)
inspection=bpy.data.collections.new('GRIP_INSPECTION_EXPORTS');scene.collection.children.link(inspection)
studio=bpy.data.collections.new('GRIP_STUDIO_NOT_EXPORTED');scene.collection.children.link(studio)
def move(o,c):
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o);return o

# Standard metallic/roughness channels. Fine random roughness is original data;
# no painted photographic highlights and no runtime-only shader network.
N=256;rng=np.random.default_rng(191009);freq=np.fft.fftfreq(N);fx,fy=np.meshgrid(freq,freq)
field=np.fft.ifft2(np.fft.fft2(rng.normal(size=(N,N)))*np.exp(-2*math.pi**2*2.5**2*(fx*fx+fy*fy))).real
field=(field-field.mean())/field.std();rough=np.clip(.62+.025*field,.54,.70)
TEX=HERE/'textures-v2';TEX.mkdir(exist_ok=True)
image=bpy.data.images.new('Original rubber roughness 10mm tile',width=N,height=N,alpha=False);image.colorspace_settings.name='Non-Color'
pixels=np.stack((np.ones_like(rough),rough,np.zeros_like(rough),np.ones_like(rough)),axis=-1).astype(np.float32);image.pixels.foreach_set(pixels.ravel());image.filepath_raw=str(TEX/'rubber-metallic-roughness.png');image.file_format='PNG';image.save();image.pack()
rubber=bpy.data.materials.new('Grip black rubber - original candidate');rubber.use_nodes=True;n=rubber.node_tree.nodes;l=rubber.node_tree.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(.009,.0105,.012,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.62
tex=n.new('ShaderNodeTexImage');tex.image=image;sep=n.new('ShaderNodeSeparateColor');l.new(tex.outputs['Color'],sep.inputs['Color']);l.new(sep.outputs['Green'],p.inputs['Roughness']);l.new(sep.outputs['Blue'],p.inputs['Metallic'])

# q is distance inward from bare bar end. The exterior cap extends 3.5mm beyond
# the tube, cavity floor remains outside the tube end. Both depths are estimates.
profile=[(-.0035,0),(-.0035,.008),(-.0032,.0135),(-.0025,.0155),(-.001,.0160),(.0015,.0160),(.004,.0152),(.008,.0148),(.088,.0145),(.092,.0137),(.094,.0137),(.0948,.0140),(.0957,.0140),(.0965,.0137),(.099,.0137),(.0998,.0140),(.1007,.0140),(.1015,.0137),(.104,.0138),(.107,.0143),(.110,.0155),(.113,.0172),(.115,.0193),(.1168,.0205),(.118,.0205),(.119,.0198),(.120,.0187)]
outer=[]
for i,(a,b) in enumerate(zip(profile,profile[1:])):
 steps=max(1,math.ceil(abs(b[0]-a[0])/.00035))
 for k in range(steps):
  t=k/steps;outer.append((a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t))
outer.append(profile[-1])
axes={};objects={};exports={};checks=[]
def smoothstep(v):v=max(0,min(1,v));return v*v*(3-2*v)
for side in ['left','right']:
 axis=Vector(P[side+'_axis_inward_vector']).normalized();end=Vector(P[side+'_bar_endpoint_m']);z=Vector((0,0,1));b=axis.cross(z).normalized();axes[side]=(axis,end,b)
 cavity=P['LH_cavity_radius_working_m' if side=='left' else 'RH_cavity_radius_working_m']
 section=outer+[(.120,cavity),(.116,cavity),(.002,cavity),(-.0006,cavity),(-.001,0)]
 verts=[];rings=[];meta=[];radial=192
 for q,r in section:
  if r==0:rings.append([len(verts)]);verts.append(tuple(end+axis*q));meta.append((q,0));continue
  ids=[]
  for j in range(radial):
   a=math.tau*j/radial;rr=r
   if 0.004<q<.091 and r>.014:
    # Rounded longitudinal channels, not floating repeated strips. Eight and
    # inward relief are visual working hypotheses, not certified mould detail.
    da=abs(((a+math.pi/8)%(math.tau/8))-math.pi/8)*r
    du=max(.010-q,0,q-.083);distance=math.hypot(da,du)
    rr-=.00045*(1-smoothstep((distance-.0009)/.0006))
   ids.append(len(verts));verts.append(tuple(end+axis*q+z*(rr*math.cos(a))+b*(rr*math.sin(a))));meta.append((q,a/math.tau))
  rings.append(ids)
 faces=[]
 for aa,bb in zip(rings,rings[1:]):
  for j in range(radial):
   nj=(j+1)%radial
   if len(aa)==1:faces.append((aa[0],bb[j],bb[nj]))
   elif len(bb)==1:faces.append((aa[j],bb[0],aa[nj]))
   else:faces.append((aa[j],bb[j],bb[nj],aa[nj]))
 mesh=bpy.data.meshes.new(side+' rubber grip closed section');mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free();mesh.materials.append(rubber)
 uv=mesh.uv_layers.new(name='Physical rubber 10mm UV')
 for poly in mesh.polygons:
  poly.use_smooth=True
  angles=[meta[mesh.loops[i].vertex_index][1] for i in poly.loop_indices];seam=max(angles)-min(angles)>.5
  for li in poly.loop_indices:
   q,a=meta[mesh.loops[li].vertex_index]
   if seam and a<.5:a+=1
   uv.data[li].uv=(a*math.tau*.0148/.010,q/.010)
 obj=bpy.data.objects.new(side.title()+' rubber grip - editable candidate',mesh);source.objects.link(obj);objects[side]=obj
 obj['component_id']=P['component_id'];obj['dimensions_estimated']=True;obj['scope']='Rubber envelope only; right throttle carrier absent'
 bm=bmesh.new();bm.from_mesh(mesh);unseen=set(bm.verts);shells=0
 while unseen:
  shells+=1;queue=[unseen.pop()]
  while queue:
   for edge in queue.pop().link_edges:
    for vertex in edge.verts:
     if vertex in unseen:unseen.remove(vertex);queue.append(vertex)
 tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons]);start=end+axis*.14
 cap=tree.ray_cast(start,-axis,.2);short=tree.ray_cast(start,-axis,.10)
 row={'side':side,'vertices':len(bm.verts),'faces':len(bm.faces),'closed_connected_shells':shells,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True),'cavity_open_to_depth_80mm':short[0] is None,'cavity_floor_axial_q_m':float((cap[0]-end).dot(axis)) if cap[0] is not None else None,'bar_endpoint_m':list(end),'axis_inward':list(axis),'tube_to_rubber_radial_space_m_estimated':cavity-.0111,'right_space_reserved_for_absent_carrier':side=='right','art_accepted':False}
 assert shells==1 and row['non_manifold_edges']==0 and row['signed_volume_m3']>0 and row['cavity_open_to_depth_80mm'],row
 assert row['cavity_floor_axial_q_m'] is not None and row['cavity_floor_axial_q_m']<0,row
 checks.append(row);bm.free()
 duplicate=bpy.data.objects.new(side.title()+' rubber grip - inspection export',mesh.copy());inspection.objects.link(duplicate);exports[side]=duplicate
 bpy.context.view_layer.objects.active=duplicate;duplicate.select_set(True);mod=duplicate.modifiers.new('Inspection reduction only, not mobile LOD','DECIMATE');mod.ratio=.40;bpy.ops.object.modifier_apply(modifier=mod.name);duplicate.select_set(False)
bpy.ops.object.select_all(action='DESELECT')
for obj in exports.values():obj.select_set(True)
bpy.context.view_layer.objects.active=exports['left'];bpy.ops.export_scene.gltf(filepath=str(HERE/'handlebar-grips-v2-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False)
for obj in exports.values():obj.hide_render=True;obj.hide_set(True)

# Neutral studio only; originals retain shared cockpit coordinates.
floor_mat=bpy.data.materials.new('Grip studio slate');floor_mat.use_nodes=True;floor_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.08,.095,.11,1);floor_mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.0835));floor=move(bpy.context.object,studio);floor.data.materials.append(floor_mat)
world=bpy.data.worlds.new('Grip neutral studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.28,.32,.38,1);world.node_tree.nodes['Background'].inputs[1].default_value=.30
for name,pos,power,size in [('GRIP_KEY',(0,-.22,.55),30,.4),('GRIP_FILL',(0,.38,.35),15,.35),('GRIP_EDGE',(-.6,.1,.35),18,.30)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,.05,.105))-o.location).to_track_quat('-Z','Y').to_euler()
camera=bpy.data.objects.new('GRIP_CAMERA',bpy.data.cameras.new('GRIP_CAMERA'));studio.objects.link(camera);scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=False;scene.render.resolution_x=1100;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
axis,end,b=axes['left'];target=end+axis*.058;camera.location=target+axis*.07+b*.26+Vector((0,0,.16));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=65
bpy.ops.object.select_all(action='DESELECT');objects['left'].select_set(True);bpy.context.view_layer.objects.active=objects['left']
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'handlebar-grips-v2.blend'),compress=True)
report={'revision':'handlebar-grips-v2','source_sha256':hashlib.sha256((HERE/'handlebar-grips-v2.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'handlebar-grips-v2-inspection.glb').read_bytes()).hexdigest(),'checks':checks,'geometry_scope':'Two separate original rubber envelopes; no controls or throttle carrier','grooves':'Physical integrated shallow longitudinal channels; count, depth and relief sign estimated','UV_tile_m':.010,'material':'Original nonmetallic standard PBR, roughness .54–.70; no micro-normal or photo texture','installed_fit_certified':False,'physical_iphone_tested':False,'art_accepted':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report-v2.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_GRIP_PREFLIGHT',json.dumps(report))
