"""Original v2 integrated bolt pads: no curved skin cutting their flat seats.
Main skin sampled from original construction; new supports/radii remain estimates.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-cover-left-v2';O.mkdir(exist_ok=True);P=json.loads((H/'parameters-v2.json').read_text());F=P['fixation_revision'];sys.path.insert(0,str(H));from hollow_profile_loft import closed_loft
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,mesh_object,csg,check_mesh,tree_world,export,studio
sys.path.insert(0,str(H.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_ENGINE_COVER_LEFT');s.collection.children.link(source);construction=bpy.data.collections.new('ENGINE_COVER_LEFT_V2_RETAINED_CONSTRUCTION');s.collection.children.link(construction);guides=bpy.data.collections.new('ENGINE_COVER_LEFT_V2_IMMUTABLE_INTERFACE_GUIDES');s.collection.children.link(guides);stage=bpy.data.collections.new('ENGINE_COVER_LEFT_V2_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
paint=material('LH engine silver coated casting - estimated PBR',(.43,.45,.47),.20,.40);scale=P['pixel_scale_working_m'];cx,cy=P['mapping_origin_uv_px'];uv=[Vector(((x-cx)*scale,(cy-y)*scale)) for x,y in P['outline_uv_px']];main=Vector(((P['main_boss_uv_px'][0]-cx)*scale,(cy-P['main_boss_uv_px'][1])*scale))
def smooth(t):t=min(1,max(0,t));return t*t*(3-2*t)
def old_height(p,t):return .005+.015*smooth((1-t)/.15)+.023*smooth((.072-(p-main).length)/.016)
oldv,oldf,oldoutline=closed_loft([tuple(p) for p in uv],old_height,wall=P['wall_working_m']);oldmesh=mesh_object('Retained original v1 skin construction for exact ray sampling',oldv,oldf,construction,paint);oldtree=BVHTree.FromPolygons([Vector(v) for v in oldv],oldf)
def old_front(p):
 hit=oldtree.ray_cast(Vector((p.x,p.y,.10)),Vector((0,0,-1)),.15);return hit[0].z if hit[0] is not None else .005
pads=[];rface=F['flat_pad_radius_working_m'];rfoot=F['pad_transition_foot_radius_working_m'];postR=F['rear_support_radius_working_m'];rootR=F['rear_support_root_true_radius_working_m'];wall=P['wall_working_m']
for station,(x,y) in enumerate(P['visible_fixation_candidate_uv_px']):
 p=Vector(((x-cx)*scale,(cy-y)*scale));values=[old_front(p)]
 for radial in range(1,10):
  for i in range(128):a=math.tau*i/128;values.append(old_front(p+Vector((math.cos(a),math.sin(a)))*(rfoot*radial/9)))
 top=F['pad_plane_local_w_m'][station];pads.append({'centre':p,'top':top,'inner_plane':top-wall,'original_skin_max_under_foot':max(values),'source_samples':len(values)})
# Original Catmull perimeter unchanged except support neighbourhoods.
def curve(t):
 i=int(t)%len(uv);f=t-math.floor(t);a,b,c,d=[uv[(i+k)%len(uv)] for k in [-1,0,1,2]];return .5*(2*b+(-a+c)*f+(2*a-5*b+4*c-d)*f*f+(-a+3*b-3*c+d)*f*f*f)
outline=[]
for j in range(384):
 q=curve(j/384*len(uv));sub=6 if min((q-p['centre']).length for p in pads)<rfoot*2.7 else 1
 for k in range(sub):
  q=curve((j+k/sub)/384*len(uv));direction=q.normalized();r=q.length
  for pad in pads:
   c=pad['centre'];dot=c.dot(direction);perp=c.length_squared-dot*dot;disc=rfoot*rfoot-perp
   if disc<0 or dot<0:continue
   other=dot+math.sqrt(disc);blend=.0012;h=max(blend-abs(r-other),0)/blend;r=max(r,other)+blend*h*h*.25
  outline.append(direction*r)
# New plateau extends beyond support flare, so inner root meets an actual flat plane.
def face_height(p):
 base=old_front(p)
 for pad in pads:
  d=(p-pad['centre']).length;weight=1-smooth((d-rface)/(rfoot-rface));base=base*(1-weight)+pad['top']*weight
 return base
N=len(outline)
from fixation_patch_mesh_v2 import patch_cup
verts,faces,patch_report=patch_cup(outline,pads,face_height,wall=wall,post_radius=postR,root_radius=rootR,lip_radius=F['rear_support_back_lip_true_radius_working_m'],face_radius=rface,foot_radius=rfoot)
base=mesh_object('Original integrated flat fixation pads and continuous curved shell',verts,faces,construction,paint)
def revolve(name,section,c,n=96):
 vv=[];rr=[];ff=[]
 for w,r in section:
  if r==0:rr.append([len(vv)]*n);vv.append((c.x,c.y,w))
  else:rr.append(list(range(len(vv),len(vv)+n)));vv.extend((c.x+r*math.cos(math.tau*i/n),c.y+r*math.sin(math.tau*i/n),w) for i in range(n))
 for j in range(len(section)):
  if section[j][1]==0 and section[(j+1)%len(section)][1]==0:continue
  for i in range(n):
   k=(i+1)%n;f=list(dict.fromkeys([rr[j][i],rr[(j+1)%len(rr)][i],rr[(j+1)%len(rr)][k],rr[j][k]]))
   if len(f)>=3:ff.append(f)
 return mesh_object(name,vv,ff,construction,paint)
features=[];drills=[];lip=F['rear_support_back_lip_true_radius_working_m'];bore=P['fastener_bore_working_m'];mouth=F['bore_front_lip_true_radius_working_m']
for k,pad in enumerate(pads):
 c=pad['centre']
 sec=[(-.03,0),(-.03,bore),(pad['top']-mouth,bore)]
 for i in range(1,11):a=math.pi*.5*i/10;sec.append((pad['top']-mouth+mouth*math.sin(a),bore+mouth*(1-math.cos(a))))
 sec.extend([(.10,bore+mouth),(.10,0)]);drills.append(revolve('Original rounded-mouth through bore '+str(k+1),sec,c))
bpy.context.view_layer.update();body,operations=csg(base,features,drills,source,paint,R,'LH magneto cover hollow casting - editable candidate');check_mesh(body);cleanup=clean_evaluated(body,construction);body.modifiers.clear();bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.mesh.customdata_custom_splitnormals_clear();body.data.update()
for f in body.data.polygons:f.use_smooth=not(abs(f.normal.z)>.99999 and any(math.hypot(f.center.x-p['centre'].x,f.center.y-p['centre'].y)<rface for p in pads))
checks=check_mesh(body);x,y,z=P['datum_world_m'];datum=bpy.data.objects.new('Engine LH cover provisional datum',None);source.objects.link(datum);datum.matrix_world=Matrix(((0,0,1,x),(1,0,0,y),(0,1,0,z),(0,0,0,1)));body.parent=datum;body['all_dimensions_estimated']=True;body['exact_RDC_part_certified']=False;body['art_accepted']=False
parent=H.parent/'engine-output-cover-left/engine-output-cover-left-v1.blend';parent_sha=hashlib.sha256(parent.read_bytes()).hexdigest();assert parent_sha=='92f528236a8d9e94669b0eed18e186cb8a2c46612bfb7200907cd6a9abc79399'
with bpy.data.libraries.load(str(parent),link=True) as (available,loaded):loaded.objects=['LH rear output cover provisional datum','LH rear output cover formed hollow wall - editable candidate']
for o in loaded.objects:guides.objects.link(o)
bpy.context.view_layer.update();other=bpy.data.objects['LH rear output cover formed hollow wall - editable candidate'];crossings=len(tree_world(body).overlap(tree_world(other)))
m=body.to_mesh();tree=BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);body.to_mesh_clear();opening_tests=[]
for p in pads:opening_tests.append(tree.ray_cast(Vector((p['centre'].x,p['centre'].y,-.03)),Vector((0,0,1)),.14)[0] is None)
assert all(opening_tests);construction.hide_render=True;construction.hide_viewport=True;guides.hide_render=True;guides.hide_viewport=True;export(H/'engine-cover-left-v2-inspection.glb',[datum,body]);points=[body.matrix_world@Vector(p) for p in body.bound_box];target=sum(points,Vector())/len(points);studio(s,stage,target);s.camera.data.clip_start=.001
for o in stage.objects:
 if o.type=='MESH':o.location.z=min(p.z for p in points)-.002
 if o.type=='LIGHT':o.data.energy*=.08
sourcefile=H/'engine-cover-left-v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(sourcefile),compress=True);report={'component_id':'MOTO-ENGINE-COVER-LEFT-001','revision':'engine-cover-left-v2','source_sha256':hashlib.sha256(sourcefile.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((H/'engine-cover-left-v2-inspection.glb').read_bytes()).hexdigest(),'geometry':[checks],'cleanup':cleanup,'custom_normals_present':body.data.has_custom_normals,'edge_policy':'Retain actual geometric creases above0.70rad from topology cleanup, smooth detailed C1 transitions; no non-rim blanket clear','adaptive_outline_points':N,'skin_sampling':patch_report,'pads':[dict(p,centre=list(p['centre'])) for p in pads],'bore_centres_unchanged':True,'all_three_bores_ray_clear':opening_tests,'rear_output_cover_source_sha256':parent_sha,'rear_output_cover_surface_crossings':crossings,'original_skin_sampled_for_new_pad_blends':True,'bounds_world_m':{'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]},'all_dimensions_estimated':True,'actual_OEM_pad_size_or_height_known':False,'art_accepted':False,'physical_iphone_tested':False};(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(H/'build-report-v2.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_LH_V2_PREFLIGHT',json.dumps(report))
