"""Original conditional52JV0145 castbody only; separatemetalstub remainsunmade."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,sys
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-ohc-cover-v1';O.mkdir(exist_ok=True);P=json.loads((H/'parameters.json').read_text());sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,mesh_object,csg,check_mesh,tree_world,export,studio,cylinder
sys.path.insert(0,str(H.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parent=R/P['parent_source'];assert sha(parent)==P['parent_source_sha256'];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_ENGINE_OHC_COVER_BODY');s.collection.children.link(source);construction=bpy.data.collections.new('OHC_COVER_RETAINED_CONSTRUCTION');s.collection.children.link(construction);guides=bpy.data.collections.new('OHC_COVER_IMMUTABLE_HEAD_GUIDE');s.collection.children.link(guides);stage=bpy.data.collections.new('OHC_COVER_STUDIO_NOT_EXPORTED');s.collection.children.link(stage);paint=material('Original dark OHC cover clean coating - estimated',(.012,.014,.016),.12,.39)
def curve(points,n=14):
 pts=[Vector((u,v-P['local_v_centre_head_z_m']))for u,v in points];result=[]
 for i,b in enumerate(pts):
  a=pts[(i-1)%len(pts)];c=pts[(i+1)%len(pts)];d=pts[(i+2)%len(pts)]
  for j in range(n):
   t=j/n;result.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 area=sum(a.x*b.y-b.x*a.y for a,b in zip(result,result[1:]+result[:1]));return result if area>0 else list(reversed(result))
outer=curve(P['outline_YZ_working_m']);crown=curve(P['crown_YZ_working_m']);pad=curve(P['pad_YZ_working_m']);
def loft(name,contour,sections):
 centre=sum(contour,Vector((0,0)))/len(contour);N=len(contour);normals=[]
 for i,p in enumerate(contour):
  tangent=(contour[(i+1)%N]-contour[(i-1)%N]).normalized();normals.append(Vector((tangent.y,-tangent.x)))
 vv=[];ff=[];rings=[]
 for w,scale,inset in sections:
  ring=[centre+(p-centre)*scale-normal*inset for p,normal in zip(contour,normals)];rings.append(list(range(len(vv),len(vv)+N)));vv.extend((p.x,p.y,w)for p in ring)
 for j in range(len(rings)-1):
  for i in range(N):k=(i+1)%N;ff.append((rings[j][i],rings[j][k],rings[j+1][k],rings[j+1][i]))
 for j in [0,len(rings)-1]:
  # These silhouettes are star-shaped from their owncentre, checked beforefan.
  ring=[Vector(vv[i][:2])-centre for i in rings[j]];assert all(a.cross(b)>0 for a,b in zip(ring,ring[1:]+ring[:1])),('Notstarshaped',name,j)
  index=len(vv);vv.append((centre.x,centre.y,sections[j][0]))
  for i in range(N):k=(i+1)%N;ff.append((index,rings[j][k],rings[j][i])if j==0 else(index,rings[j][i],rings[j][k]))
 return mesh_object(name,vv,ff,construction,paint)
ed=P['plate_edge_radius_working_m'];th=P['plate_thickness_working_m'];sec=[(0,1,ed)]
for i in range(1,13):a=math.pi*.5*i/12;sec.append((ed*(1-math.cos(a)),1,ed*(1-math.sin(a))))
sec.append((th-ed,1,0))
for i in range(1,13):a=math.pi*.5*i/12;sec.append((th-ed+ed*math.sin(a),1,ed*(1-math.cos(a))))
plate=loft('Original3ear continuous plate outline',outer,sec)
# Continuous source heightfield joins the shallow photographed panel to the
# cast front, avoiding a separate intersecting block and its pointed CSG roots.
centre=sum(crown,Vector((0,0)))/len(crown);N=384;K=72
padcentre=sum(pad,Vector((0,0)))/len(pad)
def inside(point,polygon):
 answer=False
 for a,b in zip(polygon,polygon[1:]+polygon[:1]):
  if (a.y>point.y)!=(b.y>point.y) and point.x<(b.x-a.x)*(point.y-a.y)/(b.y-a.y)+a.x:answer=not answer
 return answer
def distance_segment(point,a,b):
 d=b-a;t=max(0,min(1,(point-a).dot(d)/d.length_squared));return (point-a-d*t).length
def radial_radius(angle):
 direction=Vector((math.cos(angle),math.sin(angle)));hits=[]
 for a,b in zip(crown,crown[1:]+crown[:1]):
  edge=b-a;den=direction.cross(edge)
  if abs(den)<1e-15:continue
  rel=a-centre;radius=rel.cross(edge)/den;t=rel.cross(direction)/den
  if radius>0 and -1e-8<=t<=1+1e-8:hits.append(radius)
 assert hits,angle
 return max(hits)
def smoothstep(value):t=max(0,min(1,value));return t*t*(3-2*t)
angles=[math.tau*i/N for i in range(N)];radii=[radial_radius(a)for a in angles]
def height(point,fraction):
 if fraction>=.94:return .014+.008*math.sqrt(max(0,1-((fraction-.94)/.06)**2))
 signed=min(distance_segment(point,a,b)for a,b in zip(pad,pad[1:]+pad[:1]));signed=signed if inside(point,pad)else-signed
 panel=smoothstep((signed+.00375)/.0075);rim=smoothstep((.94-fraction)/.07)
 return .022+.003*panel*rim
vv=[];ff=[];rings=[]
# Concentric front grid, actual curved shoulder/panel surface allone mesh.
for k in range(1,K+1):
 fraction=k/K;indices=[]
 for a,radius in zip(angles,radii):
  point=centre+Vector((math.cos(a),math.sin(a)))*(fraction*radius);indices.append(len(vv));vv.append((point.x,point.y,height(point,fraction)))
 rings.append(indices)
frontcentre=len(vv);vv.append((centre.x,centre.y,height(centre,0)))
for j in range(N):q=(j+1)%N;ff.append((frontcentre,rings[0][j],rings[0][q]))
for k in range(K-1):
 for j in range(N):q=(j+1)%N;ff.append((rings[k][j],rings[k+1][j],rings[k+1][q],rings[k][q]))
backring=[]
for a,radius in zip(angles,radii):
 point=centre+Vector((math.cos(a),math.sin(a)))*radius;backring.append(len(vv));vv.append((point.x,point.y,.002))
backcentre=len(vv);vv.append((centre.x,centre.y,.002))
for j in range(N):q=(j+1)%N;ff.append((backring[j],backring[q],rings[-1][q],rings[-1][j]));ff.append((backcentre,backring[q],backring[j]))
body=mesh_object('Originalcontinuousdomedfrontandshallowpanel',vv,ff,construction,paint);features=[body];drills=[]
# Two visible parallel shallowreliefs. Positive vsrecessedexactsection unmeasured.
aff=P['affine_coefficients_3x2']
def mapped(x,y):return Vector((x*aff[0][0]+y*aff[1][0]+aff[2][0],x*aff[0][1]+y*aff[1][1]+aff[2][1]-P['local_v_centre_head_z_m'],.0247))
def rounded_relief(name,start,end,r=.001):
 axis=(end-start).normalized();U=Vector((0,0,1));V=axis.cross(U).normalized();centre=(start+end)/2;L=(end-start).length;section=[(-L/2-r,0)]
 for j in range(1,13):a=math.pi*.5*j/12;section.append((-L/2-r*math.cos(a),r*math.sin(a)))
 section.append((L/2,r))
 for j in range(1,13):a=math.pi*.5*j/12;section.append((L/2+r*math.sin(a),0 if j==12 else r*math.cos(a)))
 vv=[];rings=[];ff=[];n=64
 for x,radius in section:
  if radius==0:rings.append([len(vv)]*n);vv.append(tuple(centre+axis*x))
  else:rings.append(list(range(len(vv),len(vv)+n)));vv.extend(tuple(centre+axis*x+radius*(U*math.cos(math.tau*k/n)+V*math.sin(math.tau*k/n)))for k in range(n))
 ff=[]
 for j in range(len(rings)-1):
  for k in range(n):
   q=(k+1)%n;face=list(dict.fromkeys([rings[j][k],rings[j][q],rings[j+1][q],rings[j+1][k]]))
   if len(face)>=3:ff.append(face)
 return mesh_object(name,vv,ff,construction,paint)
for i,(a,b)in enumerate([((367,323),(609,323)),((346,359),(630,359))]):features.append(rounded_relief('Original estimated rounded parallel relief '+str(i+1),mapped(*a),mapped(*b)))
# Blind cavity, backs/section notdocumented; nointernalmechanism.
drills.append(loft('Estimated blind inner cavity',crown,[(-.01,.87,0),(.004,.87,0),(.012,.80,0),(.018,.59,0)]))
for i,(u,v)in enumerate(P['bore_centres_YZ_working_m']):drills.append(cylinder('Actual cast cover fastener bore '+str(i+1),(u,v-P['local_v_centre_head_z_m'],.015),P['bore_radius_working_m'],.06,construction,axis=(0,0,1),n=96))
stubaxis=Vector(P['stub_axis_local_uvw_working']).normalized();stubcentre=Vector(P['stub_seat_centre_local_uvw_working_m']);drills.append(cylinder('Estimated open seat for separate metallic stub',stubcentre,.004,.050,construction,axis=stubaxis,n=96));bpy.context.view_layer.update();cover,ops=csg(plate,features,drills,source,paint,R,'UG5 OHC cast cover body - conditional candidate');cleanup=clean_evaluated(cover,construction);cover.modifiers.clear();bpy.ops.object.select_all(action='DESELECT');cover.select_set(True);bpy.context.view_layer.objects.active=cover;bpy.ops.mesh.customdata_custom_splitnormals_clear();cover.data.update()
for f in cover.data.polygons:f.use_smooth=not (abs(abs(f.normal.z)-1)<1e-7 and abs(f.center.z)<1e-7)
geometry=check_mesh(cover);localtree=BVHTree.FromPolygons([v.co for v in cover.data.vertices],[tuple(f.vertices)for f in cover.data.polygons]);bores=[]
for u,v in P['bore_centres_YZ_working_m']:bores.append(localtree.ray_cast(Vector((u,v-P['local_v_centre_head_z_m'],-.01)),Vector((0,0,1)),.08)[0]is None)
assert all(bores),bores
with bpy.data.libraries.load(str(parent),link=True)as(available,loaded):loaded.objects=['Engine head base provisional datum','Engine UG5 head hollow exterior casting - editable candidate']
for obj in loaded.objects:guides.objects.link(obj)
bpy.context.view_layer.update();headdatum=bpy.data.objects['Engine head base provisional datum'];head=bpy.data.objects['Engine UG5 head hollow exterior casting - editable candidate'];datum=bpy.data.objects.new('OHC cover inherited estimated head datum',None);source.objects.link(datum);datum.matrix_world=headdatum.matrix_world@Matrix(((0,0,1,P['parent_mount_plane_head_x_m']+P['mount_gap_working_m']),(1,0,0,0),(0,1,0,P['local_v_centre_head_z_m']),(0,0,0,1)));cover.parent=datum;bpy.context.view_layer.update();cross=len(tree_world(head).overlap(tree_world(cover)));construction.hide_render=True;construction.hide_viewport=True;guides.hide_render=True;guides.hide_viewport=True;cover['all_dimensions_estimated']=True;cover['metal_stub_separate_unmade']=True;cover['art_accepted']=False;export(H/'engine-ohc-cover-inspection.glb',[datum,cover]);points=[cover.matrix_world@Vector(v)for v in cover.bound_box];target=sum(points,Vector())/len(points);studio(s,stage,target);s.camera.data.clip_start=.001
for obj in stage.objects:
 if obj.type=='MESH':obj.location.z=min(v.z for v in points)-.002
 if obj.type=='LIGHT':obj.data.energy*=.08
file=H/'engine-ohc-cover-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True);assert sha(parent)==P['parent_source_sha256'];report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(file),'export_sha256':sha(H/'engine-ohc-cover-inspection.glb'),'parent_source_sha256':sha(parent),'geometry':[geometry],'cleanup':cleanup,'actual_fastener_bores_ray_clear':bores,'head_surface_crossings':cross,'head_interface_status':'blocked'if cross else'candidate_surfaces_clear_notmeasuredmating','metal_stub_created':False,'back_cavity_estimated':True,'all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False};(H/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('OHC_BODY_PREFLIGHT',json.dumps(report))
