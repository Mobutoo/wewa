"""One original hollow metallic OHC stub, conditional photos, no copied texture."""
from pathlib import Path
import bpy,json,hashlib,math,sys
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-ohc-stub-v1';P=json.loads((H/'parameters.json').read_text());sys.path.insert(0,str(H.parent/'throttle-control'))
from control_geometry import material,lathe,check_mesh,tree_world,export,studio
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for kind in ['cover','head']:assert sha(R/P[kind+'_source'])==P[kind+'_sha256']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
collection=bpy.data.collections.new('WEWA_ENGINE_OHC_STUB');s.collection.children.link(collection);guides=bpy.data.collections.new('OHC_STUB_IMMUTABLE_GUIDES');s.collection.children.link(guides);stage=bpy.data.collections.new('OHC_STUB_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
with bpy.data.libraries.load(str(R/P['cover_source']),link=True)as(a,l):l.objects=['OHC cover inherited estimated head datum','UG5 OHC cast cover body - conditional candidate']
for o in l.objects:guides.objects.link(o)
cover=next(o for o in l.objects if o.type=='MESH')
with bpy.data.libraries.load(str(R/P['head_source']),link=True)as(a,l):l.objects=['Engine head base provisional datum','Engine UG5 head hollow exterior casting - editable candidate']
for o in l.objects:guides.objects.link(o)
head=next(o for o in l.objects if o.type=='MESH')
guides.hide_viewport=False;bpy.context.view_layer.update();A=Vector(P['outward_cover_local']).normalized();U=A.cross(Vector((0,0,1))).normalized();V=A.cross(U).normalized();C=Vector(P['seat_cover_local_m']);datum=bpy.data.objects.new('OHC metallic stub inherited provisional seat datum',None);collection.objects.link(datum);datum.matrix_world=cover.matrix_world@Matrix(((A.x,U.x,V.x,C.x),(A.y,U.y,V.y,C.y),(A.z,U.z,V.z,C.z),(0,0,0,1)))
# C1 rounded profile, single distal lip; no invented second visible root collar.
# 2D quarter arcs are actual geometry, not a post-CSG bevel.
section=[]
def point(x,r):section.append((x,r))
def arc(cx,cr,r,a,b,n=10):
 for i in range(n+1):
  t=a+(b-a)*i/n;point(cx+r*math.cos(t),cr+r*math.sin(t))
back=P['insertion_back_x_m'];end=P['tip_x_m'];ri=P['inner_radius_m'];rs=P['insertion_radius_m'];rb=P['barrel_radius_m'];roundr=P['rim_round_radius_m'];bead=P['bead_centre_x_m'];half=P['bead_half_width_m'];rise=P['bead_radius_m']-rb
arc(back+roundr,rs-roundr,roundr,math.pi,math.pi/2)
point(P['shoulder_start_x_m'],rs)
for i in range(1,25):
 t=i/24;smooth=t*t*(3-2*t);point(P['shoulder_start_x_m']+(P['barrel_start_x_m']-P['shoulder_start_x_m'])*t,rs+(rb-rs)*smooth)
point(bead-half,rb)
for i in range(1,49):
 t=i/48;point(bead-half+2*half*t,rb+rise*math.sin(math.pi*t)**2)
point(end-roundr,rb);arc(end-roundr,rb-roundr,roundr,math.pi/2,0);point(end,ri+roundr);arc(end-roundr,ri+roundr,roundr,0,-math.pi/2);point(back+roundr,ri);arc(back+roundr,ri+roundr,roundr,-math.pi/2,-math.pi)
# Remove exactly duplicated profile endpoints while preserving every distinct radius.
section=[p for i,p in enumerate(section)if i==0 or math.dist(p,section[i-1])>1e-12]
if math.dist(section[0],section[-1])<1e-12:section.pop()
mat=material('Original estimated plated metal - no photo texture',P['material']['base_color_linear'],1,.24);tube=lathe('OHC metallic hollow tube with one distal retention lip - editable candidate',section,collection,mat,n=P['angular_segments']);tube.parent=datum;bpy.context.view_layer.update()
geometry=check_mesh(tube);mesh=tube.data;mesh.calc_loop_triangles();assert all(t.area>0 for t in mesh.loop_triangles)
# End annuli remain planes; all barrel/profile curves are smooth.
for f in mesh.polygons:f.use_smooth=abs(abs(f.normal.x)-1)>1e-6
tree=tree_world(tube);lumen=[]
for y,z in [(0,0),(.001,0),(-.001,0),(0,.001),(0,-.001)]:
 origin=datum.matrix_world@Vector((back-.001,y,z));direction=datum.matrix_world.to_3x3()@Vector((1,0,0));lumen.append(tree.ray_cast(origin,direction,.06)[0]is None)
assert all(lumen),lumen
crossings={'cast_cover':len(tree.overlap(tree_world(cover))),'head_v3':len(tree.overlap(tree_world(head)))}
assert not any(crossings.values()),crossings
guides.hide_render=True;guides.hide_viewport=True;tube['all_dimensions_estimated']=True;tube['art_accepted']=False;tube['one_visible_distal_lip']=True
export(H/'engine-ohc-stub-inspection.glb',[datum,tube]);points=[tube.matrix_world@Vector(v)for v in tube.bound_box];target=sum(points,Vector())/8;studio(s,stage,target)
for o in stage.objects:
 if o.type=='MESH':o.hide_render=True
 if o.type=='LIGHT':o.data.energy*=.04
s.camera.data.clip_start=.0005
file=H/'engine-ohc-stub-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True)
for kind in ['cover','head']:assert sha(R/P[kind+'_source'])==P[kind+'_sha256']
report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(file),'export_sha256':sha(H/'engine-ohc-stub-inspection.glb'),'geometry':[geometry],'triangles':len(mesh.loop_triangles),'lumen_axial_five_rays_clear':lumen,'surface_crossing_pairs':crossings,'interface_scope':'Actual candidate surfaces only, not measured fit or certification; no hidden mating thread or hose fabricated.','profile_x_r_m':section,'datum_world_matrix':[list(r)for r in datum.matrix_world],'guide_sources':{k:{'path':P[k+'_source'],'sha256':P[k+'_sha256']}for k in ['cover','head']},'all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False}
(H/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('OHC_STUB_PREFLIGHT',json.dumps(report))
