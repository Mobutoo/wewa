"""Original related PF402404 visual candidate. Uncalibrated photo guide, not OEM CAD."""
import bpy,bmesh,json,math,hashlib,subprocess,tempfile,shutil
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=json.loads((HERE/'parameters.json').read_text());OUT=ROOT/'creative/reviews/instrument-bracket-v1';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_INSTRUMENT_BRACKET_ISOLATED');s.collection.children.link(source)
construction=bpy.data.collections.new('BRACKET_ORIGINAL_GUIDES_AND_CUTTERS');s.collection.children.link(construction)
studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
def move(o,c):
 for col in list(o.users_collection):col.objects.unlink(o)
 c.objects.link(o);return o
def obj(name,vs,fs,col=construction):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);col.objects.link(o);return o
def xy(pixel):
 x,y=pixel;u=(x-P['photo_origin_pixels'][0])*P['working_scale_m_per_reference_pixel'];v=(P['photo_origin_pixels'][1]-y)*P['working_scale_m_per_reference_pixel'];a=P['photo_guide_rotation_radians'];return Vector((u*math.cos(a)-v*math.sin(a),u*math.sin(a)+v*math.cos(a)))
def forming(v):return P['maximum_arm_joggle_working_m']*math.exp(-(v/.045)**4)
land=[xy(p) for p in P['reference_outline_manual_pixels']];outline=[]
for i in range(len(land)):
 a,b,c,d=[land[j%len(land)] for j in [i-1,i,i+1,i+2]]
 for k in range(5):
  t=k/5;outline.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
area=sum(outline[i].x*outline[(i+1)%len(outline)].y-outline[(i+1)%len(outline)].x*outline[i].y for i in range(len(outline)))/2
constraints=list(range(len(outline)))
if area<0:constraints.reverse()
def inside(x,y):
 odd=False
 for i in range(len(outline)):
  a,b=outline[i],outline[(i+1)%len(outline)]
  if (a.y>y)!=(b.y>y) and x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x:odd=not odd
 return odd
points=outline.copy();lo=[min(v[i] for v in outline) for i in range(2)];hi=[max(v[i] for v in outline) for i in range(2)]
x=lo[0]
while x<hi[0]:
 y=lo[1]
 while y<hi[1]:
  if inside(x,y):points.append(Vector((x,y)))
  y+=.0012
 x+=.0012
coords,edges,caps,*_=delaunay_2d_cdt(points,[],[constraints],1,1e-8,False)
caps=[f for f in caps if inside(sum(coords[i].x for i in f)/len(f),sum(coords[i].y for i in f)/len(f))]
caparea=sum(abs(sum(coords[f[j]].x*coords[f[(j+1)%len(f)]].y-coords[f[(j+1)%len(f)]].x*coords[f[j]].y for j in range(len(f))))/2 for f in caps);assert abs(caparea-abs(area))<1e-8,(caparea,area)
used=sorted({i for f in caps for i in f});remap={i:j for j,i in enumerate(used)};coords=[coords[i] for i in used];caps=[tuple(remap[i] for i in f) for f in caps];n=len(coords);th=P['plate_thickness_working_m']
vs=[(v.x,v.y,forming(v.y)+z) for z in [-th/2,th/2] for v in coords];fs=[tuple(reversed(f)) for f in caps]+[tuple(i+n for i in f) for f in caps];count=Counter(tuple(sorted((f[j],f[(j+1)%len(f)]))) for f in caps for j in range(len(f)))
fs.extend((a,b,b+n,a+n) for (a,b),v in count.items() if v==1);base=obj('Original constrained formed sheet',vs,fs)
def cyl(name,pt,r,depth,z):
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=r,depth=depth,location=(pt.x,pt.y,z));o=move(bpy.context.object,construction);o.name=name
 if not name.startswith('True open'):
  bevel=o.modifiers.new('Original collar edge radius before CSG','BEVEL');bevel.width=.00025;bevel.segments=3
 return o
features=[];drills=[];holes=[]
for i,(p,r) in enumerate(zip(P['visible_holes_photo_pixels'],P['visible_hole_radii_working_m'])):
 pt=xy(p);z=forming(pt.y);holes.append({'local_centre_m':[pt.x,pt.y,z],'radius_m':r});features.append(cyl('Visible raised eye '+str(i+1)+' - composition unknown',pt,P['raised_eye_radius_working_m'],.0040,z+.0006));drills.append(cyl('True open passage '+str(i+1),pt,r,.060,0))
for i,pixel in enumerate(P['stud_heads_photo_pixels']):
 pt=xy(pixel);z=forming(pt.y);features.append(cyl('Observed circular head '+str(i+1),pt,.0075,.0030,z+.0018))
 # Reverse projecting rods appear in the related D15 illustration. Their thread
 # pitch and length remain candidate estimates, not measured PF402404 interfaces.
 nring=72;layers=90;v=[];length=P['stud_length_working_m'];pitch=P['stud_pitch_working_m']
 for k in range(layers+1):
  zz=z-.0005-k/layers*length
  for j in range(nring):
   phi=math.tau*j/nring;phase=((zz-z)/pitch-phi/math.tau)%1;r=P['stud_radius_working_m']-.00035+.00035*max(0,1-abs(phase-.5)/.4);v.append((pt.x+r*math.cos(phi),pt.y+r*math.sin(phi),zz))
 f=[tuple(reversed(range(nring))),tuple(range(layers*nring,(layers+1)*nring))]+[(k*nring+j,k*nring+(j+1)%nring,(k+1)*nring+(j+1)%nring,(k+1)*nring+j) for k in range(layers) for j in range(nring)];features.append(obj('Reverse rod '+str(i+1)+' estimated thread relief',v,f))
for i,(a,b) in enumerate(P['ribs_photo_endpoints_pixels']):
 a,b=xy(a),xy(b);mid=(a+b)/2;delta=b-a
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=(mid.x,mid.y,forming(mid.y)+.0005));o=move(bpy.context.object,construction);o.name='Observed short formed rib '+str(i+1);o.scale=(delta.length/2+.0018,.0016,.0013);o.rotation_euler.z=math.atan2(delta.y,delta.x);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);features.append(o)
def volume(o):
 dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();row={'name':o.name,'vertices':[list(o.matrix_world@v.co) for v in m.vertices],'triangles':[list(t.vertices) for t in m.loop_triangles]};e.to_mesh_clear();return row
with tempfile.TemporaryDirectory(prefix='wewa-bracket-') as t:
 inp=Path(t)/'in.json';out=Path(t)/'out.json';inp.write_text(json.dumps({'base':volume(base),'features':[volume(o) for o in features],'drills':[volume(o) for o in drills]}));subprocess.run([shutil.which('python'),str(HERE.parent/'front-brake-plate/csg.py'),str(inp),str(out)],check=True);fused=json.loads(out.read_text())
body=obj('Instrument fork bracket - related visual candidate',fused['vertices'],fused['triangles'],source)
# CSG coplanar triangles contain near-coincident seams at float32 precision.
# Dissolve those before bevel so tiny sliver faces cannot poison cap normals.
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(body.data);bm.free();body.data.update()
b=body.modifiers.new('Small sheet edge radii - estimated','BEVEL');b.width=0;b.segments=3;b.limit_method='ANGLE';b.angle_limit=.4
dg=bpy.context.evaluated_depsgraph_get();evaluated=bpy.data.meshes.new_from_object(body.evaluated_get(dg),depsgraph=dg);backup=body.copy();backup.data=body.data.copy();construction.objects.link(backup);backup.name='Unbevelled fused source plus edge modifier';body.modifiers.clear();body.data=evaluated
for p in body.data.polygons:p.use_smooth=abs(p.normal.z)<.99995
body.data.set_sharp_from_angle(angle=.65)
# No global weighted normals: tiny CSG cap seams must not generate false facets.
m=bpy.data.materials.new('Black protective coating - appearance only');m.use_nodes=True;node=m.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.015,.020,.026,1);node.inputs['Roughness'].default_value=.34;node.inputs['Metallic'].default_value=.25;m.diffuse_color=(.015,.020,.026,1);body.data.materials.clear();body.data.materials.append(m)
for face in body.data.polygons:face.material_index=0
body['component_id']=P['component_id'];body['all_dimensions_estimated']=True;body['installed_fit_verified']=False
for o in construction.objects:o.hide_render=True;o.hide_set(True)
dg=bpy.context.evaluated_depsgraph_get();e=body.evaluated_get(dg);mesh=e.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;pending=[unseen.pop()]
 while pending:
  for ed in pending.pop().link_edges:
   for v in ed.verts:
    if v in unseen:unseen.remove(v);pending.append(v)
tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons]);probes=[]
for h in holes:
 x,y,z=h['local_centre_m'];clear=tree.ray_cast(Vector((x,y,.03)),Vector((0,0,-1)),.07)[0] is None;rim=tree.ray_cast(Vector((x+h['radius_m']+.0015,y,.03)),Vector((0,0,-1)),.07)[0] is not None;assert clear and rim,(h,clear,rim);probes.append({'centre_m':[x,y,z],'radius_m':h['radius_m'],'clear':clear,'surrounding_rim_present':rim})
report={'component_id':P['component_id'],'name':body.name,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'connected_shells':shells,'signed_volume_m3':bm.calc_volume(signed=True),'open_passages':probes,'cap_area_m2':caparea,'outline_area_m2':abs(area),'construction_grid_step_m':.0012,'collection':source.name,'local_frame':'XY presentation plane, +Z photographed face; origin midpoint of two observed head centres','cockpit_pose_applied':False,'exact_RDC_compatibility_confirmed':False,'all_dimensions_estimated':True,'art_accepted':False};assert report['non_manifold_edges']==0 and shells==1 and report['signed_volume_m3']>0,report;bm.free();e.to_mesh_clear()
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.export_scene.gltf(filepath=str(HERE/'instrument-bracket-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True)
world=bpy.data.worlds.new('Bracket neutral studio');world.use_nodes=True;s.world=world;world.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.36,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45
for name,location,power,size in [('BRACKET_KEY',(.10,.10,.30),1,.25),('BRACKET_FILL',(-.20,-.10,.15),.5,.22),('BRACKET_EDGE',(.08,-.25,.10),.75,.20),('BRACKET_REVERSE',(-.10,-.03,-.25),1,.25)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=location;o.rotation_euler=(Vector((0,-.05,0))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('BRACKET_CAMERA',bpy.data.cameras.new('BRACKET_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.10,-.16,.30);cam.rotation_euler=(Vector((0,-.05,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=60
s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG';s.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'instrument-bracket-v1.blend'),compress=True);report['source_sha256']=hashlib.sha256((HERE/'instrument-bracket-v1.blend').read_bytes()).hexdigest();report['export_sha256']=hashlib.sha256((HERE/'instrument-bracket-inspection.glb').read_bytes()).hexdigest();(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_BRACKET_SOURCE',json.dumps(report))
