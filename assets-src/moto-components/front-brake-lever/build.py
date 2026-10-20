"""Original photo-informed lever; dimensional estimates remain explicit.
Build/source/export preflight before rendering. No catalogue mesh imported.
"""
import json,math,shutil,subprocess,tempfile,hashlib
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
from collections import Counter

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=json.loads((HERE/'parameters.json').read_text())
OUT=ROOT/'creative/reviews/front-brake-lever-v1';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_FRONT_BRAKE_LEVER');scene.collection.children.link(source)
construction=bpy.data.collections.new('EDITABLE_LEVER_OUTLINE_AND_CUTTERS');scene.collection.children.link(construction)
studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');scene.collection.children.link(studio)
def move(o,c):
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o);return o
def mesh_obj(name,verts,faces,collection=construction):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free()
 o=bpy.data.objects.new(name,m);collection.objects.link(o);return o
def offset(z):
 # Smooth forming offsets; depth cannot be measured from the available views.
 return .0018*math.exp(-(z/.013)**4)+.0014*math.exp(-((z+.088)/.010)**4)
# Catmull–Rom outline between explicit landmarks. Keep the ends closed for CSG,
# then cut the open serrated shaft seat and end eye in the original volume.
land=P['outline_yz_m'];outline=[]
for i in range(len(land)):
 a,b,c,d=[np.array(land[j%len(land)]) for j in [i-1,i,i+1,i+2]]
 for k in range(8):
  t=k/8;outline.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
# A constrained interior grid is necessary before bending the sheet. A pair of
# non-planar n-gons gives long diagonal facets; that rejected attempt is not used.
count=len(outline);constraints=list(range(count))
area=sum(outline[i][0]*outline[(i+1)%count][1]-outline[(i+1)%count][0]*outline[i][1] for i in range(count))
if area<0:constraints.reverse()
points=[Vector((float(y),float(z))) for y,z in outline]
for y in np.arange(-.011,.014,.0008):
 for z in np.arange(-.099,.011,.0008):points.append(Vector((float(y),float(z))))
coords,edges,cap,*_=delaunay_2d_cdt(points,[],[constraints],1,1e-8,False)
def inside(y,z):
 odd=False
 for i in range(len(outline)):
  a,b=outline[i],outline[(i+1)%len(outline)]
  if (a[1]>z)!=(b[1]>z) and y<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:odd=not odd
 return odd
# Extra unconstrained grid points outside the outline must not become blade.
cap=[face for face in cap if inside(sum(coords[i].x for i in face)/len(face),sum(coords[i].y for i in face)/len(face))]
cap_area=sum(abs(sum(coords[face[j]].x*coords[face[(j+1)%len(face)]].y-coords[face[(j+1)%len(face)]].x*coords[face[j]].y for j in range(len(face))))/2 for face in cap)
assert abs(cap_area-abs(area)/2)<1e-8,(cap_area,abs(area)/2,'Outline area changed')
used=sorted({i for f in cap for i in f});mapping={old:new for new,old in enumerate(used)}
coords=[coords[i] for i in used];cap=[tuple(mapping[i] for i in face) for face in cap]
count=len(coords);th=P['working_blade_thickness_m'];verts=[]
for x in [-th/2,th/2]:
 for y,z in coords:verts.append((x+offset(float(z)),float(y),float(z)))
faces=[tuple(reversed(face)) for face in cap]+[tuple(i+count for i in face) for face in cap]
counts=Counter(tuple(sorted((face[j],face[(j+1)%len(face)]))) for face in cap for j in range(len(face)))
for (a,b),n in counts.items():
 if n==1:faces.append((a,b,b+count,a+count))
base=mesh_obj('Curved and joggled blade construction',verts,faces)
def bore(name,y,z,r,spline=False):
 n=240;v=[]
 for x in [-.015,.015]:
  for i in range(n):
   a=math.tau*i/n
   # Coarse visual tooth rhythm is estimated; no spline standard claimed.
   rr=r-(P['working_spline_depth_m']*(.5+.5*math.cos(P['working_spline_count']*a)) if spline else 0)
   v.append((x,y+rr*math.sin(a),z+rr*math.cos(a)))
 f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh_obj(name,v,f)
drills=[bore('Estimated serrated shaft seat',0,0,P['working_shaft_bore_radius_m'],True),bore('Cable pin end eye',-.0015,-.088,P['working_eye_bore_radius_m'])]
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.008));slot=move(bpy.context.object,construction);slot.name='Open head slot - estimated';slot.dimensions=(.030,P['working_slot_width_m'],.020);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);drills.append(slot)
def volume(o):
 deps=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles();result={'name':o.name,'vertices':[list(o.matrix_world@v.co) for v in m.vertices],'triangles':[list(t.vertices) for t in m.loop_triangles]};e.to_mesh_clear();return result
with tempfile.TemporaryDirectory(prefix='wewa-lever-csg-') as temp:
 inp=Path(temp)/'input.json';out=Path(temp)/'output.json';inp.write_text(json.dumps({'base':volume(base),'features':[],'drills':[volume(o) for o in drills]}))
 subprocess.run([shutil.which('python'),str(HERE.parent/'front-brake-plate/csg.py'),str(inp),str(out)],check=True);fused=json.loads(out.read_text())
lever=mesh_obj('Front brake lever - editable candidate',fused['vertices'],fused['triangles'],source)
for o in construction.objects:o.hide_render=True;o.hide_set(True)
bev=lever.modifiers.new('Small formed edge radii - estimated','BEVEL');bev.width=.00028;bev.segments=4
bev.affect='EDGES';bev.limit_method='ANGLE';bev.angle_limit=.3
lever.location=(0,0,.105);lever['component_id']=P['component_id'];lever['all_dimensions_estimated']=True;lever['art_accepted']=False

# Original small PBR colour/roughness variation. Zinc-like appearance candidate,
# not chemically measured plating and not an angle-dependent iridescence model.
TEX=HERE/'textures';TEX.mkdir(exist_ok=True);N=512;tile=.025
rng=np.random.default_rng(131607);f=np.fft.fftfreq(N);fx,fy=np.meshgrid(f,f)
def noise(sigma):
 v=np.fft.ifft2(np.fft.fft2(rng.normal(size=(N,N)))*np.exp(-2*math.pi**2*sigma*sigma*(fx*fx+fy*fy))).real
 return (v-v.mean())/v.std()
wide=noise(32);fine=noise(1.5);blend=np.clip(.5+.18*wide,0,1)
gold=np.array([.43,.34,.15]);silver=np.array([.32,.39,.36]);color=gold[None,None,:]*blend[:,:,None]+silver[None,None,:]*(1-blend[:,:,None])
color=np.clip(color+fine[:,:,None]*.005,0,1)
def im(name,rgb,srgb=False):
 image=bpy.data.images.new(name,width=N,height=N,alpha=False);image.colorspace_settings.name='sRGB' if srgb else 'Non-Color'
 # Convert authored linear base colour to PNG sRGB explicitly.
 if srgb:rgb=np.where(rgb<=.0031308,rgb*12.92,1.055*np.power(rgb,1/2.4)-.055)
 rgba=np.concatenate([rgb,np.ones((N,N,1))],axis=2).astype(np.float32);image.pixels.foreach_set(rgba.ravel());image.filepath_raw=str(TEX/(name+'.png'));image.file_format='PNG';image.save();image.pack();return image
albedo=im('lever-finish-basecolor',color,True)
orm=im('lever-finish-metallic-roughness',np.stack([np.ones_like(fine),np.clip(.30+.018*fine,.23,.38),np.full_like(fine,.88)],axis=-1))
mat=bpy.data.materials.new('Lever plated steel appearance - estimated');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
a=n.new('ShaderNodeTexImage');a.image=albedo;l.new(a.outputs['Color'],p.inputs['Base Color'])
r=n.new('ShaderNodeTexImage');r.image=orm;s=n.new('ShaderNodeSeparateColor');l.new(r.outputs['Color'],s.inputs['Color']);l.new(s.outputs['Green'],p.inputs['Roughness']);l.new(s.outputs['Blue'],p.inputs['Metallic']);lever.data.materials.append(mat)
deps=bpy.context.evaluated_depsgraph_get();evaluated=bpy.data.meshes.new_from_object(lever.evaluated_get(deps),depsgraph=deps)
inspection=bpy.data.objects.new('Front brake lever - inspection export',evaluated);source.objects.link(inspection);inspection.location=lever.location
def uv(mesh):
 mesh.update();layer=mesh.uv_layers.new(name='Physical 25mm box mapping')
 for poly in mesh.polygons:
  ax=max(range(3),key=lambda i:abs(poly.normal[i]));sign=1 if poly.normal[ax]>=0 else -1
  for li in poly.loop_indices:
   co=mesh.vertices[mesh.loops[li].vertex_index].co;pair=(sign*co.y,co.z) if ax==0 else (-sign*co.x,co.z) if ax==1 else (sign*co.x,co.y)
   layer.data[li].uv=(pair[0]/tile,pair[1]/tile)
# Visible source uses evaluated bevel + same UV field as export. Original outline,
# cutters and un-bevelled fused source are preserved in the construction collection.
param=lever.copy();param.data=lever.data.copy();param.name='Parametric lever bevel - retained hidden';construction.objects.link(param);param.hide_render=True;param.hide_set(True)
lever.modifiers.clear();lever.data=evaluated.copy();uv(lever.data);uv(inspection.data)
for poly in lever.data.polygons:poly.use_smooth=True
for poly in inspection.data.polygons:poly.use_smooth=True

# Actual connectedness and through-opening checks before any render.
bm=bmesh.new();bm.from_mesh(lever.data);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;pending=[unseen.pop()]
 while pending:
  for e in pending.pop().link_edges:
   for v in e.verts:
    if v in unseen:unseen.remove(v);pending.append(v)
tree=BVHTree.FromPolygons([v.co for v in lever.data.vertices],[tuple(p.vertices) for p in lever.data.polygons])
probes={}
for name,y,z in [('shaft',0,0),('eye',-.0015,-.088),('open_slot',0,.008),('blade',.004,-.040)]:probes[name]=tree.ray_cast(Vector((.02,y,z)),Vector((-1,0,0)),.04)[0] is not None
check={'vertices':len(bm.verts),'faces':len(bm.faces),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'connected_shells':shells,'signed_volume_m3':bm.calc_volume(signed=True),'axial_probe_surface_hit':probes,'estimated_dimensions':True,'installed_interface_verified':False,'art_accepted':False}
assert shells==1 and check['non_manifold_edges']==0 and check['signed_volume_m3']>0,check
assert not probes['shaft'] and not probes['eye'] and not probes['open_slot'] and probes['blade'],check
bm.free()
bpy.ops.object.select_all(action='DESELECT');inspection.select_set(True);bpy.context.view_layer.objects.active=inspection
bpy.ops.export_scene.gltf(filepath=str(HERE/'front-brake-lever-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False)
inspection.hide_render=True;inspection.hide_set(True)
floor_mat=bpy.data.materials.new('Lever studio charcoal');floor_mat.diffuse_color=(.09,.105,.12,1)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.004));floor=move(bpy.context.object,studio);floor.name='LEVER_FLOOR';floor.data.materials.append(floor_mat)
world=bpy.data.worlds.new('Lever studio world');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.30,.33,.37,1);world.node_tree.nodes['Background'].inputs[1].default_value=.20
for name,location,energy,size in [('LEVER_KEY',(.15,-.15,.35),8,.23),('LEVER_FILL',(-.10,.12,.20),5,.20),('LEVER_EDGE',(.06,.22,.12),7,.16)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=location;o.rotation_euler=(Vector((0,0,.06))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('LEVER_CAMERA',bpy.data.cameras.new('LEVER_CAMERA'));studio.objects.link(cam);scene.camera=cam;cam.location=(.32,-.12,.14);cam.rotation_euler=(Vector((0,.002,.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=80
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=False;scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
bpy.ops.object.select_all(action='DESELECT');lever.select_set(True);bpy.context.view_layer.objects.active=lever
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'front-brake-lever-v1.blend'),compress=True)
check['source_sha256']=hashlib.sha256((HERE/'front-brake-lever-v1.blend').read_bytes()).hexdigest();check['export_sha256']=hashlib.sha256((HERE/'front-brake-lever-inspection.glb').read_bytes()).hexdigest()
(OUT/'source-geometry-check.json').write_text(json.dumps(check,indent=2)+'\n')
(HERE/'build-report.json').write_text(json.dumps({'parameters':P,'CSG':{k:v for k,v in fused.items() if k not in ['vertices','triangles']},'source_geometry':check,'texture_origin':'Original periodic mathematical data, no reference photo pixels','shader_limit':'Static colour variation approximates appearance only; no spectral or angle-dependent plating model'},indent=2)+'\n');print('WEWA_LEVER_CHECK',json.dumps(check))
