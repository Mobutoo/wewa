"""Original DS181005-related plate and observed rim; no certified hidden pressing section."""
import bpy,bmesh,json,math,hashlib,tempfile,subprocess,shutil
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];P=json.loads((HERE/'parameters.json').read_text());OUT=ROOT/'creative/reviews/steering-upper-v1';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('WEWA_STEERING_UPPER_ISOLATED');s.collection.children.link(col);construction=bpy.data.collections.new('UPPER_ORIGINAL_GUIDES_CUTTERS');s.collection.children.link(construction);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
def xy(p):return Vector(((p[0]-P['photo_origin_px'][0])*P['working_scale_m_per_pixel'],(P['photo_origin_px'][1]-p[1])*P['working_scale_m_per_pixel']))
land=[xy(p) for p in P['outline_pixels']];outline=[]
for i in range(len(land)):
 a,b,c,d=[land[j%len(land)] for j in [i-1,i,i+1,i+2]]
 for k in range(16):
  t=k/16;outline.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
def inside(x,y):
 odd=False
 for i in range(len(outline)):
  a,b=outline[i],outline[(i+1)%len(outline)]
  if (a.y>y)!=(b.y>y) and x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x:odd=not odd
 return odd
def distance(q):
 best=1e10
 for i,a in enumerate(outline):
  b=outline[(i+1)%len(outline)];d=b-a;t=max(0,min(1,(q-a).dot(d)/d.length_squared));best=min(best,(q-a-d*t).length_squared)
 return math.sqrt(best)
area=sum(outline[i].x*outline[(i+1)%len(outline)].y-outline[(i+1)%len(outline)].x*outline[i].y for i in range(len(outline)))/2;ids=list(range(len(outline)))
if area<0:ids.reverse()
points=outline.copy()
# Explicit narrow transverse sampling resolves the visible rolled-return highlight.
for i,v in enumerate(outline):
 tangent=outline[(i+1)%len(outline)]-outline[(i-1)%len(outline)];inward=Vector((tangent.y,-tangent.x)) if area<0 else Vector((-tangent.y,tangent.x));inward.normalize()
 for off in [.00020,.00040,.00065,.00090,.00120,.00160,.0020]:
  q=v+inward*off
  if inside(q.x,q.y):points.append(q)
lo=[min(v[i] for v in outline) for i in range(2)];hi=[max(v[i] for v in outline) for i in range(2)];x=lo[0]
while x<hi[0]:
 y=lo[1]
 while y<hi[1]:
  if inside(x,y):points.append(Vector((x,y)))
  y+=.001
 x+=.001
co,edges,caps,*_=delaunay_2d_cdt(points,[],[ids],1,1e-8,False);caps=[f for f in caps if inside(sum(co[i].x for i in f)/len(f),sum(co[i].y for i in f)/len(f))];caparea=sum(abs(sum(co[f[j]].x*co[f[(j+1)%len(f)]].y-co[f[(j+1)%len(f)]].x*co[f[j]].y for j in range(len(f))))/2 for f in caps);assert abs(caparea-abs(area))<1e-8
used=sorted({i for f in caps for i in f});mapping={i:j for j,i in enumerate(used)};co=[co[i] for i in used];caps=[tuple(mapping[i] for i in f) for f in caps];n=len(co);dist=[distance(v) for v in co];th=P['plate_thickness_m_estimated'];drop=P['rim_drop_m_estimated'];width=P['rim_roll_width_m_estimated'];vs=[]
# The hidden return section is an explicit visual estimate, not a stamping CAD claim.
for side in ['lower','upper']:
 for v,d in zip(co,dist):
  fall=max(0,1-d/width)**2;z=-th-drop*fall if side=='lower' else -.00025*fall;vs.append((v.x,v.y,z))
fs=[tuple(reversed(f)) for f in caps]+[tuple(i+n for i in f) for f in caps];counts=Counter(tuple(sorted((f[j],f[(j+1)%len(f)]))) for f in caps for j in range(len(f)));fs.extend((a,b,b+n,a+n) for (a,b),count in counts.items() if count==1)
def obj(name,verts,faces,collection):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);collection.objects.link(o);return o
base=obj('Original photo contour plate with estimated rolled return',vs,fs,construction);drills=[];holes=[]
for i,(px,py,rp) in enumerate(P['holes_photo_pixels_and_radius']):
 c=xy([px,py]);r=rp*P['working_scale_m_per_pixel'];roll=P['hole_edge_roll_m_estimated'];profile=[(-.025,r+roll),(-th-roll,r+roll),(-th+roll,r),(-roll,r),(0,r+roll),(.025,r+roll)];vv=[]
 for z,rad in profile:
  for k in range(128):
   phi=math.tau*k/128;vv.append((c.x+rad*math.cos(phi),c.y+rad*math.sin(phi),z))
 ff=[tuple(reversed(range(128))),tuple(range(5*128,6*128))]+[(j*128+k,j*128+(k+1)%128,(j+1)*128+(k+1)%128,(j+1)*128+k) for j in range(5) for k in range(128)];o=obj('Observed true passage '+str(i+1)+' estimated edge break',vv,ff,construction);drills.append(o);holes.append({'id':i+1,'centre_m':[c.x,c.y,0],'radius_m_estimated':r})
def volume(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();v={'name':o.name,'vertices':[list(o.matrix_world@v.co) for v in m.vertices],'triangles':[list(t.vertices) for t in m.loop_triangles]};e.to_mesh_clear();return v
with tempfile.TemporaryDirectory(prefix='wewa-steer-upper-') as t:
 inp=Path(t)/'in.json';out=Path(t)/'out.json';inp.write_text(json.dumps({'base':volume(base),'features':[],'drills':[volume(o) for o in drills]}));subprocess.run([shutil.which('python'),str(ROOT/'assets-src/moto-components/front-brake-plate/csg.py'),str(inp),str(out)],check=True);fused=json.loads(out.read_text())
o=obj('Upper steering plate - related DS181005 candidate',fused['vertices'],fused['triangles'],col);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();o.data.update()
for f in o.data.polygons:f.use_smooth=abs(f.normal.z)<.99995
o.data.set_sharp_from_angle(angle=.65);m=bpy.data.materials.new('Neutral geometry review - not final coating');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.22,.24,.26,1);p.inputs['Metallic'].default_value=.15;p.inputs['Roughness'].default_value=.3;o.data.materials.append(m);tri=o.modifiers.new('Evaluated tangent-ready triangulation','TRIANGULATE');tri.keep_custom_normals=True
for x in construction.objects:x.hide_render=True;x.hide_set(True)
e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=e.to_mesh();mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;stack=[unseen.pop()]
 while stack:
  for ed in stack.pop().link_edges:
   for v in ed.verts:
    if v in unseen:unseen.remove(v);stack.append(v)
areas=[(mesh.vertices[t.vertices[1]].co-mesh.vertices[t.vertices[0]].co).cross(mesh.vertices[t.vertices[2]].co-mesh.vertices[t.vertices[0]].co).length/2 for t in mesh.loop_triangles];tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(f.vertices) for f in mesh.polygons]);probes=[]
for h in holes:
 x,y,z=h['centre_m'];clear=tree.ray_cast(Vector((x,y,.025)),Vector((0,0,-1)),.05)[0] is None;rim=tree.ray_cast(Vector((x+h['radius_m_estimated']+.0008,y,.025)),Vector((0,0,-1)),.05)[0] is not None;assert clear and rim,(h,clear,rim);probes.append({**h,'clear':clear,'rim_present':rim})
r={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'non_manifold_edges':sum(not ed.is_manifold for ed in bm.edges),'connected_shells':shells,'signed_volume_m3':bm.calc_volume(signed=True),'zero_area_triangles_at_1e18_m2':sum(a<=1e-18 for a in areas),'min_triangle_area_m2':min(areas),'cap_area_m2':caparea,'outline_area_m2':abs(area),'open_passages':probes,'hidden_rim_section_estimated':True,'current_RDC_identity_verified':False,'installed_pose_applied':False,'art_accepted':False};assert shells==1 and not r['non_manifold_edges'] and not r['zero_area_triangles_at_1e18_m2'] and r['signed_volume_m3']>0;bm.free();e.to_mesh_clear()
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.gltf(filepath=str(HERE/'steering-upper-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True)
w=bpy.data.worlds.new('Upper neutral studio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.3,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.45
for name,loc,power,size in [('KEY',(.12,-.08,.30),2,.25),('FILL',(-.20,.12,.18),1,.22),('EDGE',(.10,.2,-.16),2,.20)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;x=bpy.data.objects.new(name,d);studio.objects.link(x);x.location=loc;x.rotation_euler=(Vector((0,.04,0))-x.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('UPPER_CAMERA',bpy.data.cameras.new('UPPER_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.10,-.18,.32);cam.rotation_euler=(Vector((0,.04,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.30;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG';bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'steering-upper-v1.blend'),compress=True);r['source_sha256']=hashlib.sha256((HERE/'steering-upper-v1.blend').read_bytes()).hexdigest();r['export_sha256']=hashlib.sha256((HERE/'steering-upper-inspection.glb').read_bytes()).hexdigest();(OUT/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_STEERING_UPPER',json.dumps(r))
