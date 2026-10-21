"""Original bounded cowl shell study. Related PF7401X3 photos, not measured RDC.
Finite parametric wall and rolled boundaries, no hidden hardware, material or assembly.
"""
import bpy,bmesh,math,json,hashlib,bisect
import numpy as np
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/headlamp-cowl-raw-return-study-v11';O.mkdir(parents=True,exist_ok=True);plan=R/'creative/research/headlamp-cowl/angular-rear-profile-plan-v5.json';P=json.loads(plan.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
construction_plan=R/'creative/research/headlamp-cowl/sixth-support-return-plan-v11.json';rp=json.loads(construction_plan.read_text())['P6_return_candidate'];original5=H/'headlamp-cowl-raw-study-v5.blend';oldsha=sha(original5);bpy.ops.wm.open_mainfile(filepath=str(original5));oldobj=bpy.data.objects['Cowl continuous finite shell - partial conditional study'];oldm=oldobj.data;oldface={};oldbodypoints=set();oldm.calc_loop_triangles()
from mathutils.bvhtree import BVHTree
oldbv=BVHTree.FromPolygons([v.co for v in oldm.vertices],[t.vertices[:]for t in oldm.loop_triangles],all_triangles=True)
for f0 in oldm.polygons:
 key=tuple(sorted(tuple(oldm.vertices[i].co)for i in f0.vertices))
 if oldm.attributes['WEWA_surface_class'].data[f0.index].value in[1,2]:oldbodypoints.update(tuple(oldm.vertices[i].co)for i in f0.vertices)
 oldface[key]={tuple(oldm.vertices[oldm.loops[li].vertex_index].co):(tuple(oldm.corner_normals[li].vector),tuple(oldm.uv_layers.active.data[li].uv))for li in f0.loop_indices}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
C=bpy.data.collections.new('WEWA_HEADLAMP_COWL_SHELL_STUDY');s.collection.children.link(C);T=bpy.data.collections.new('Cowl shape studio - not exported');s.collection.children.link(T)
W=.0025;baseNA=256;angles=sorted(set([math.tau*j/baseNA for j in range(baseNA)]+[math.tau*(j+k/24)/baseNA for j in range(42,52)for k in range(1,24)]));NA=len(angles);NQ=112;NC=180
profile_file=H/'rear-profile-v5.json';profile=json.loads(profile_file.read_text());assert profile['plan_sha256']==sha(plan)

def rear_profile(th):
 t=th%math.tau;knots=profile['knots_radians'];i=min(len(knots)-2,bisect.bisect_right(knots,t)-1);u=t-knots[i]
 def value(key):
  a,b,c,d=[row[i]for row in profile[key]];return((a*u+b)*u+c)*u+d
 return value('radius_coefficients_descending_power'),value('Y_coefficients_descending_power')
def section(th):
 ct=math.cos(th);st=math.sin(th);w=(1-ct)/2;smooth=w*w*(3-2*w)
 zfront=.115+.023*smooth;outer=1/math.sqrt((st/.112)**2+(ct/zfront)**2)
 rr,rear=rear_profile(th)
 return [(.1035,0),(.1075,-.0007),(outer-.004,0),(outer,.004),(outer+.001,min(.014,rear*.22)),(outer+.0015,rear*.35),(rr,rear*.8),(rr-.0015,rear)]

def cat(pts,u):
 # Clamped cubic B-spline evaluated by de Boor; bounded by control polygon.
 n=len(pts)-1;p=3;knots=[0.]*(p+1)+[j/(n-p+1)for j in range(1,n-p+1)]+[1.]*(p+1)
 u=max(0,min(1,u));k=n if u==1 else next(i for i in range(p,n+1)if knots[i]<=u<knots[i+1]);d=[np.array(pts[k-p+j],dtype=np.float64)for j in range(p+1)]
 for r in range(1,p+1):
  for j in range(p,r-1,-1):
   lo=knots[j+k-p];hi=knots[j+1+k-r];alpha=(u-lo)/(hi-lo)if hi>lo else 0.;d[j]=(1-alpha)*d[j-1]+alpha*d[j]
 return d[p]

def mid(th,q):
 r,y=cat(section(th),q);return np.array((r*math.sin(th),y,r*math.cos(th)),dtype=np.float64)
def frame(th,q):
 e=1e-5;dt=(mid(th+e,q)-mid(th-e,q))/(2*e);lo=max(0,q-e);hi=min(1,q+e);dq=(mid(th,hi)-mid(th,lo))/(hi-lo);n=np.cross(dt,dq);n/=np.linalg.norm(n);b=dq-dt*np.dot(dq,dt)/np.dot(dt,dt);b/=np.linalg.norm(b);return n,b
# Perimeter: exterior front->rear; rounded rear cut; interior rear->front; rounded aperture cut.
rows=[]
for k in range(NQ+1):rows.append(('outer',k/NQ,0))
for k in range(1,NC):rows.append(('rear',1,k*math.pi/NC))
for k in range(NQ,-1,-1):rows.append(('inner',k/NQ,0))
for k in range(1,12):rows.append(('front',0,k*math.pi/12))

def point(th,desc):
 kind,q,a=desc;p=mid(th,q);n,b=frame(th,q)
 if kind=='outer':return p+n*W/2
 if kind=='inner':return p-n*W/2
 if kind=='rear':
  ta,tb=map(math.radians,rp['theta_bounds_degrees_estimated']);x=(th%math.tau-ta)/(tb-ta)
  def smooth(t):return t*t*t*(t*(t*6-15)+10)
  weight=0. if x<=0 or x>=1 else smooth(x/.25)if x<.25 else smooth((1-x)/.25)if x>.75 else 1.
  r=W/2;rad=rp['bend_mid_radius_m_estimated'];length=rp['straight_return_length_m_estimated']*weight;beta=weight*math.pi/2
  # Physicalsheetprofile, parameterized by actualcrosssection arclength.
  # Atweight0 onlythetipsemicircle remains, exactlytheoldrolledcap.
  s1=(rad-r)*beta;s2=length;s3=math.pi*r;s4=length;s5=(rad+r)*beta;dist=(a/math.pi)*(s1+s2+s3+s4+s5);endN=rad*(1-math.cos(beta))+length*math.sin(beta);endB=rad*math.sin(beta)+length*math.cos(beta)
  if dist<s1:
   ang=dist/(rad-r);u=rad+(r-rad)*math.cos(ang);v=(rad-r)*math.sin(ang)
  elif dist<s1+s2:
   d=dist-s1;u=rad+(r-rad)*math.cos(beta)+d*math.sin(beta);v=(rad-r)*math.sin(beta)+d*math.cos(beta)
  elif dist<=s1+s2+s3:
   ang=(dist-s1-s2)/r;u=endN+r*math.cos(ang-beta);v=endB+r*math.sin(ang-beta)
  elif dist<s1+s2+s3+s4:
   d=dist-s1-s2-s3;u=endN-r*math.cos(beta)-d*math.sin(beta);v=endB+r*math.sin(beta)-d*math.cos(beta)
  else:
   ang=max(0,beta-(dist-s1-s2-s3-s4)/(rad+r));u=rad-(rad+r)*math.cos(ang);v=(rad+r)*math.sin(ang)
  return p+n*u+b*v
 return p+(-n*math.cos(a)-b*math.sin(a))*W/2

verts=[tuple(point(angles[j],row))for row in rows for j in range(NA)];NN=len(rows);faces=[]
for i in range(NN):
 for j in range(NA):faces.append((i*NA+j,i*NA+(j+1)%NA,((i+1)%NN)*NA+(j+1)%NA,((i+1)%NN)*NA+j))
m=bpy.data.meshes.new('Original finite cowl spline sections with rounded wall returns');m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);volume=bm.calc_volume(signed=True);nonmanifold=sum(not e.is_manifold for e in bm.edges);components=0;todo=set(bm.verts)
while todo:
 components+=1;stack=[todo.pop()]
 while stack:
  for e in stack.pop().link_edges:
   for v in e.verts:
    if v in todo:todo.remove(v);stack.append(v)
bm.to_mesh(m);bm.free();assert volume>0 and nonmanifold==0 and components==1
# Actual finite surface normals from incident section derivatives; no WeightedNormal/global bevel.
for p in m.polygons:p.use_smooth=True
uv=m.uv_layers.new(name='Original cowl angular-section UV')
for i,p in enumerate(m.polygons):
 row=i//NA;j=i%NA
 def profileV(desc):
  kind,q,a=desc
  if kind=='outer':value=round(q*NQ)
  elif kind=='rear':value=NQ+12*a/math.pi
  elif kind=='inner':value=NQ+12+NQ-round(q*NQ)
  else:value=NQ+12+NQ+12*a/math.pi
  if abs(value-round(value))<1e-10:value=round(value)
  return value/248
 v0=profileV(rows[row]);v1=profileV(rows[row+1])if row+1<NN else 1.;u0=angles[j]/math.tau;u1=angles[j+1]/math.tau if j+1<NA else 1.;coords=[(u0,v0),(u1,v0),(u1,v1),(u0,v1)]
 for li,v in zip(p.loop_indices,coords):uv.data[li].uv=v
surface_attr=m.attributes.new('WEWA_surface_class','INT','FACE')
for poly in m.polygons:
 row=poly.index//NA;surface_attr.data[poly.index].value=1 if row<NQ else 2 if NQ+NC<=row<NQ+NC+NQ else 3
preserved_faces=0;preserved_body_faces=0;preserved_corners=0;newnorm=[tuple(n.vector)for n in m.corner_normals]
for f0 in m.polygons:
 key=tuple(sorted(tuple(m.vertices[i].co)for i in f0.vertices));ref=oldface.get(key)
 if ref is not None:
  preserved_faces+=1
  if surface_attr.data[f0.index].value in[1,2]:preserved_body_faces+=1
  for li in f0.loop_indices:
   normal,tex=ref[tuple(m.vertices[m.loops[li].vertex_index].co)];newnorm[li]=normal;uv.data[li].uv=tex;preserved_corners+=1
# Normals derived from THIS continuoussurface, not a tangent/buffer repair.
# Float64 derivatives are evaluated before mesh quantization; actualfaces still mustpass.
cap_normals={}
for vr in range(NQ,NQ+NC+1):
 a=math.pi*(vr-NQ)/NC
 for aj,theta in enumerate(angles):
  eps=1e-5;dt=(point(theta+eps,('rear',1,a))-point(theta-eps,('rear',1,a)))/(2*eps);da=(point(theta,('rear',1,a+eps))-point(theta,('rear',1,a-eps)))/(2*eps);normal=np.cross(dt,da);normal/=np.linalg.norm(normal);cap_normals[vr*NA+aj]=tuple(normal)
for face0 in m.polygons:
 if not(NQ<=face0.index//NA<NQ+NC):continue
 for li in face0.loop_indices:newnorm[li]=cap_normals[m.loops[li].vertex_index]
m.normals_split_custom_set(newnorm)
# CORNERattributeallocation invalidates cachedUVlayer RNA; reacquire actualmeshUV.
uv=m.uv_layers['Original cowl angular-section UV']
expected_unchanged_body_faces=(baseNA-10)*2*NQ
assert preserved_body_faces==expected_unchanged_body_faces,(preserved_body_faces,expected_unchanged_body_faces)
currentpoints={tuple(v.co)for v in m.vertices};assert oldbodypoints<=currentpoints
max_body_sample_distance_old_surface=0.;bodyids=set()
for f0 in m.polygons:
 if surface_attr.data[f0.index].value in[1,2]:bodyids.update(f0.vertices)
for vi in bodyids:
 co=m.vertices[vi].co
 if tuple(co)not in oldbodypoints:
  near,no,idx,dist=oldbv.find_nearest(co);max_body_sample_distance_old_surface=max(max_body_sample_distance_old_surface,float(dist))
max_preserved_normal_encoding_delta=0.;unchanged_UV_exact=True
for f0 in m.polygons:
 key=tuple(sorted(tuple(m.vertices[i].co)for i in f0.vertices));ref=oldface.get(key)
 if ref is None:continue
 for li in f0.loop_indices:
  refn,refu=ref[tuple(m.vertices[m.loops[li].vertex_index].co)];max_preserved_normal_encoding_delta=max(max_preserved_normal_encoding_delta,float(np.linalg.norm(np.array(m.corner_normals[li].vector)-refn)));unchanged_UV_exact=unchanged_UV_exact and tuple(uv.data[li].uv)==refu
if not unchanged_UV_exact:
 diff=[]
 for face0 in m.polygons:
  key=tuple(sorted(tuple(m.vertices[i].co)for i in face0.vertices));ref=oldface.get(key)
  if ref is None:continue
  for li in face0.loop_indices:
   refn,refu=ref[tuple(m.vertices[m.loops[li].vertex_index].co)];actual=tuple(uv.data[li].uv)
   if actual!=refu:diff.append({'polygon':face0.index,'actualUV':actual,'oldUV':refu,'max_delta':max(abs(a-b)for a,b in zip(actual,refu))})
 debug=Path('/workspace/wewa-assets/work-in-progress/headlamp-cowl-raw-return-study-v11');debug.mkdir(parents=True,exist_ok=True);(debug/'UV-rejection-1.json').write_text(json.dumps({'count':len(diff),'max_delta':max(v['max_delta']for v in diff),'examples':diff[:20]},indent=2)+'\n');raise RuntimeError('UVpreservation failed, see diagnostic')
m.update();m.calc_loop_triangles();areas=[t.area for t in m.loop_triangles];mindot=1
for t in m.loop_triangles:
 a,b,c=[m.vertices[k].co for k in t.vertices];normal=(b-a).cross(c-a).normalized()
 for li in t.loops:mindot=min(mindot,normal.dot(m.corner_normals[li].vector))
bad=[]
for t in m.loop_triangles:
 a,b,c=[m.vertices[k].co for k in t.vertices];normal=(b-a).cross(c-a).normalized();dot=min(normal.dot(m.corner_normals[li].vector)for li in t.loops)
 if dot<.9:bad.append({'polygon':t.polygon_index,'row_index':t.polygon_index//NA,'theta_index':t.polygon_index%NA,'section':rows[t.polygon_index//NA],'min_normal_dot':dot,'triangle':list(t.vertices),'points':[list(v)for v in [a,b,c]]})
if bad:
 debug=Path('/workspace/wewa-assets/work-in-progress/headlamp-cowl-raw-return-study-v11');debug.mkdir(parents=True,exist_ok=True);(debug/'bad-triangles.json').write_text(json.dumps({'recipe_sha256':sha(Path(__file__)),'bad_count':len(bad),'bad':sorted(bad,key=lambda r:r['min_normal_dot'])[:40]},indent=2)+'\n')
assert min(areas)>0 and mindot>.9,(min(areas),mindot)
mat=bpy.data.materials.new('WEWA cowl neutral shape gray - study only');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.19,.19,.19,1);bs.inputs['Roughness'].default_value=.32
obj=bpy.data.objects.new('Cowl continuous finite shell - partial conditional study',m);C.objects.link(obj);m.materials.append(mat);obj['structural_closed_volume']=True;obj['estimated_geometry']=True
root=bpy.data.objects.new('HEADLAMP_COWL_ISOLATED_FRAME_UNPLACED',None);C.objects.link(root);obj.parent=root
w=bpy.data.worlds.new('Cowl neutral shape world');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);w.node_tree.nodes['Background'].inputs[1].default_value=.25;s.world=w
for name,loc,power,size in [('key',(-.22,-.25,.33),12,.3),('fill',(.28,.05,.17),8,.3),('edge',(-.12,.30,.25),15,.22)]:
 l=bpy.data.lights.new('Cowl '+name,'AREA');l.energy=power;l.size=size;o=bpy.data.objects.new(l.name,l);T.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,.05,0))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Cowl inspection camera',bpy.data.cameras.new('Cowl inspection camera'));T.objects.link(cam);s.camera=cam;cam.location=(.30,-.52,.27);cam.rotation_euler=(Vector((0,.05,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=65;cam.data.clip_start=.001;cam.data.clip_end=10
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.resolution_x=900;s.render.resolution_y=850;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-2
bpy.context.view_layer.update();source=H/'headlamp-cowl-raw-return-study-v11.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=obj;export=H/'headlamp-cowl-raw-return-study-v11.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_yup=True,export_extras=True)
report={'schema':1,'revision':'headlamp-cowl-raw-return-study-v11','source_sha256':sha(source),'export_sha256':sha(export),'shape_plan_sha256':sha(construction_plan),'base_profile5_plan_sha256':sha(plan),'original5_sha256':oldsha,'unchanged_original_body_faces_with_identicalpositions_and_UV':preserved_body_faces,'all_exact_geometrical_faces_preserved_with_reference_corner_normals_UV':preserved_faces,'max_preserved_corner_normal_encoding_delta':max_preserved_normal_encoding_delta,'UV_bitidentical_on_exactlypreservedfaces':unchanged_UV_exact,'all_old_body_sample_positions_present_bitidentically':True,'new_body_samples_max_distance_to_old_closedpolyhedron_m':max_body_sample_distance_old_surface,'adaptive_angularstation_count':NA,'local_body_retessellated_oldangularcell_count':10,'exactly_preserved_corners':preserved_corners,'libraries_count':len(bpy.data.libraries),'external_images_count':len([im for im in bpy.data.images if im.source=='FILE'and not im.packed_file]),'collection':C.name,'root':root.name,'object':obj.name,'vertices':len(m.vertices),'actual_triangles':len(areas),'min_triangle_area_m2':min(areas),'minimum_triangle_corner_normal_dot':mindot,'non_manifold_edges':nonmanifold,'connected_components':components,'positive_signed_volume_m3':volume,'all_dimensions_estimated':True,'nominal_mid_surface_normal_wall_m':W,'state':'Partialraw11finiteLreturn sharedboundary, no Booleanroot. Bodyanalyticprofile5/alloldsamples preserved;10cellsretessellated. Exactlyunchangedfaces UVexact/normalsreferencepackingdelta measured; rearcap180usesanalyticalnormals, frontcap12. Otherfeatures appliedlater.','first_gray_and_reflection_required':True,'art_accepted':False};report['angular_profile_sha256']=sha(profile_file);report['source_face_semantics']={'attribute':'WEWA_surface_class','1':'Original exterior','2':'Original interior','3':'Finite roundedwall edges'};(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('COWL_SHELL_STUDY',json.dumps(report))
