"""Original conditional two-bar front protection: currentRDC appearance + relatedDY photos.
One isolated body. All physical sections/diameter are estimates; no exactOEM fit.
"""
import bpy,bmesh,json,math,hashlib,tempfile,subprocess,shutil
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/headlamp-front-protector-study-v2';O.mkdir(parents=True,exist_ok=True);plan=json.loads((R/'creative/research/headlamp/protector-shape-plan-v1.json').read_text());P=plan['parameters'];val=lambda k:P[k]['value'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
C=bpy.data.collections.new('WEWA_HEADLAMP_FRONT_PROTECTOR_STUDY');s.collection.children.link(C);K=bpy.data.collections.new('Protector editable sections and rods - hidden');s.collection.children.link(K);T=bpy.data.collections.new('Protector studio - not exported');s.collection.children.link(T)
mat=bpy.data.materials.new('WEWA protector neutral gray original');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.29

def mesh(n,v,f,col=K):
 m=bpy.data.meshes.new(n);m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();a=bpy.data.objects.new(n,m);col.objects.link(a);return a
# Closed rounded rectangular annular crosssection, explicit 1mm working edge radii.
rad=val('outer_radius_m');rw=val('ring_radial_width_m');dep=val('ring_axial_depth_m');er=val('ring_small_edge_radius_m');qc=(dep/2-.003);rc=rad-rw/2;hq=dep/2;hr=rw/2;profile=[]
for cx,cy,start in [(hq-er,hr-er,0),(-hq+er,hr-er,90),(-hq+er,-hr+er,180),(hq-er,-hr+er,270)]:
 for j in range(7):
  a=math.radians(start+90*j/6);profile.append((qc+cx+er*math.cos(a),rc+cy+er*math.sin(a)))
# Neighbouring arcs do not share endpoints; straight section between them intentional.
N=256;v=[];f=[]
for q,r in profile:v.extend((r*math.cos(math.tau*j/N),q,r*math.sin(math.tau*j/N))for j in range(N))
for k in range(len(profile)):
 for j in range(N):f.append((k*N+j,k*N+(j+1)%N,((k+1)%len(profile))*N+(j+1)%N,((k+1)%len(profile))*N+j))
base=mesh('Editable annular rounded band section - estimated',v,f);features=[];rod_paths=[]
for name,end,centre in [('upper',val('upper_rod_end_Z_m'),val('upper_rod_centre_Z_m')),('lower',val('lower_rod_end_Z_m'),val('lower_rod_centre_Z_m'))]:
 span=math.sqrt(rc*rc-end*end);paths=[]
 for i in range(161):
  u=-1+2*i/160;x=u*span;y=-val('forward_bow_m')*(1-u*u);z=centre+(end-centre)*u**4;paths.append(Vector((x,y,z)))
 vs=[];fs=[];sides=40
 for i,c in enumerate(paths):
  tangent=(paths[min(i+1,len(paths)-1)]-paths[max(i-1,0)]).normalized();a=tangent.cross(Vector((0,1,0))).normalized();b=tangent.cross(a).normalized()
  for j in range(sides):
   th=math.tau*j/sides;vs.append(tuple(c+val('rod_radius_m')*(a*math.cos(th)+b*math.sin(th))))
 for i in range(len(paths)-1):
  for j in range(sides):fs.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
 fs.extend([tuple(reversed(range(sides))),tuple(range((len(paths)-1)*sides,len(paths)*sides))]);features.append(mesh('Editable '+name+' arched round rod - estimated',vs,fs));rod_paths.append({'name':name,'points_m':[list(x)for x in paths],'radius_m':val('rod_radius_m')})
bpy.context.view_layer.update()
def row(a):
 a.data.calc_loop_triangles();return {'name':a.name,'vertices':[list(a.matrix_world@v.co)for v in a.data.vertices],'triangles':[list(t.vertices)for t in a.data.loop_triangles]}
with tempfile.TemporaryDirectory(prefix='wewa-protector-')as tmp:
 inp=Path(tmp)/'in.json';out=Path(tmp)/'out.json';inp.write_text(json.dumps({'base':row(base),'features':[row(a)for a in features],'drills':[]}));subprocess.run([shutil.which('python'),str(H/'bucket_csg_worker_v1.py'),str(inp),str(out)],check=True);result=json.loads(out.read_text())
a=mesh('Conditional external two-bar headlamp protection - original gray study',result['vertices'],result['triangles'],C);a.data.materials.append(mat)
for p in a.data.polygons:p.use_smooth=True
# Surface ownership from actual original source volumes, not triangle-area weighting.
# Analytic normals: finite rounded band section and constant-radius curved pipes.
from mathutils.bvhtree import BVHTree
trees=[BVHTree.FromPolygons([v.co.copy()for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons])for o in [base]+features]
def band_normal(p):
 radius=math.hypot(p.x,p.z);dq=p.y-qc;dr=radius-rc;aq=dq-max(-hq+er,min(hq-er,dq));ar=dr-max(-hr+er,min(hr-er,dr));n=Vector((ar*p.x/radius,aq,ar*p.z/radius));assert n.length>1e-9;return n.normalized()
def pipe_normal(p,which):
 end=val('upper_rod_end_Z_m')if which==1 else val('lower_rod_end_Z_m');centre=val('upper_rod_centre_Z_m')if which==1 else val('lower_rod_centre_Z_m');span=math.sqrt(rc*rc-end*end);bow=val('forward_bow_m');dz=end-centre;u=max(-1,min(1,p.x/span))
 for _ in range(8):
  c=Vector((u*span,-bow*(1-u*u),centre+dz*u**4));der=Vector((span,2*bow*u,4*dz*u**3));dd=Vector((0,2*bow,12*dz*u*u));f=(c-p).dot(der);df=der.dot(der)+(c-p).dot(dd);u=max(-1,min(1,u-f/df))
 c=Vector((u*span,-bow*(1-u*u),centre+dz*u**4));n=p-c;assert n.length>1e-9;return n.normalized()
norms=[None]*len(a.data.loops);ownership=[0,0,0];min_dot=1
for poly in a.data.polygons:
 centre=sum((a.data.vertices[i].co for i in poly.vertices),Vector())/len(poly.vertices);owner=min(range(3),key=lambda i:trees[i].find_nearest(centre)[3]);ownership[owner]+=1
 for li in poly.loop_indices:
  p=a.data.vertices[a.data.loops[li].vertex_index].co;n=band_normal(p)if owner==0 else pipe_normal(p,owner);norms[li]=n;min_dot=min(min_dot,n.dot(poly.normal))
a.data.normals_split_custom_set(norms)

m=a.data;m.uv_layers.new(name='GrayStudyPlanarCharts')
for p in m.polygons:
 axis=max(range(3),key=lambda i:abs(p.normal[i]));other=[i for i in range(3)if i!=axis]
 for li in p.loop_indices:
  v=m.vertices[m.loops[li].vertex_index].co;m.uv_layers.active.data[li].uv=(v[other[0]]/.1,v[other[1]]/.1)
root=bpy.data.objects.new('HEADLAMP_PROTECTOR_ISOLATED_ORIGIN_UNPLACED',None);C.objects.link(root);a.parent=root;K.hide_render=True;K.hide_viewport=True
w=bpy.data.worlds.new('Protector neutral studio');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.2,.2,.2,1);w.node_tree.nodes['Background'].inputs[1].default_value=.3;s.world=w
for n,c,e,size in [('key',(.12,-.18,.3),22,.25),('fill',(-.2,-.02,.1),12,.30),('edge',(.15,.15,.2),20,.2)]:
 l=bpy.data.lights.new('Protector '+n,'AREA');l.energy=e;l.size=size;o=bpy.data.objects.new(l.name,l);T.objects.link(o);o.location=c;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Protector inspection camera',bpy.data.cameras.new('Protector inspection camera'));T.objects.link(cam);s.camera=cam;cam.location=(.26,-.44,.18);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=65;cam.data.clip_start=.001;cam.data.clip_end=10;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.resolution_x=700;s.render.resolution_y=650;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-1
em=bpy.data.meshes.new_from_object(a.evaluated_get(bpy.context.evaluated_depsgraph_get()));em.calc_loop_triangles();areas=[t.area for t in em.loop_triangles];bm=bmesh.new();bm.from_mesh(em);nm=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();bpy.data.meshes.remove(em);assert not nm and min(areas)>0 and volume>0
source=H/'headlamp-front-protector-study-v2.blend';glb=H/'headlamp-front-protector-study-v2.glb';bpy.ops.object.select_all(action='DESELECT');a.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=a;bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False,export_animations=False)
report={'schema':1,'revision':'headlamp-front-protector-study-v2','source_sha256':sha(source),'export_sha256':sha(glb),'collection':C.name,'root':root.name,'object':a.name,'triangles':len(areas),'min_triangle_area_m2':min(areas),'non_manifold_edges':nm,'signed_volume_m3':volume,'source_profile':profile,'rod_paths':rod_paths,'CSG_stages':result['stages'],'parameters_plan':'creative/research/headlamp/protector-shape-plan-v1.json','scope':'Conditional original protection only, unplaced; all physical sections estimates; identity/separability and backfixings unknown.','normal_method':{'method':'Actual source-surface ownership and analytic rounded-section/constant-radius-pipe normals; no weighted normals or global bevel','owned_face_counts_band_upper_lower':ownership,'min_face_custom_normal_dot':min_dot},'art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items()if k not in ['rod_paths','source_profile','CSG_stages']})
