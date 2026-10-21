"""Original smooth formed band and pierced integral lugs; working dimensions, no mounted clamp proof."""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-clamp-band-v1';P=json.loads((H/'parameters.json').read_text());assert not(H/'preflight-manifest.json').exists();sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,mesh_object,csg,check_mesh,export,studio
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;parts=bpy.data.collections.new('WEWA_ENGINE_INTAKE_CLAMP_BAND');con=bpy.data.collections.new('INTAKE_CLAMP_BAND_CONSTRUCTION_NOT_EXPORTED');stage=bpy.data.collections.new('INTAKE_CLAMP_BAND_STUDIO_NOT_EXPORTED')
for c in [parts,con,stage]:s.collection.children.link(c)
t=P['working_thickness_m'];w=P['working_width_m'];rm=P['working_radius_inner_m']+t/2;rb=P['working_turn_back_radius_m'];half=math.radians(P['working_loop_opening_degrees']/2);start=-math.pi/2+half;end=3*math.pi/2-half
# Right side straight folded ear root followed by analytic tangent turn-back then main circle.
# Working gap60deg gives start-60; return tangent rotates60deg clockwise, no miter at ring.
assert abs(half-math.pi/6)<1e-10
cx=rm*.5+rb*.5;cy=-(rm+rb)*math.sqrt(3)/2;earx=cx-rb;right=[]
for k in range(5):right.append((earx,P['working_ear_hole_Y_m']+(cy-P['working_ear_hole_Y_m'])*k/4,0,1))
for k in range(1,P['bend_samples']+1):
 a=math.pi-(math.pi/3)*k/P['bend_samples'];right.append((cx+rb*math.cos(a),cy+rb*math.sin(a),math.sin(a),-math.cos(a)))
path=right[:]
for k in range(1,P['main_arc_samples']+1):
 a=start+(end-start)*k/P['main_arc_samples'];path.append((rm*math.cos(a),rm*math.sin(a),-math.sin(a),math.cos(a)))
path.extend([(-x,y,tx,-ty)for x,y,tx,ty in right[::-1]][1:])
def rounded_rectangle(a,b,r,n):
 points=[]
 for ca,cb,begin in [(a/2-r,-b/2+r,-math.pi/2),(a/2-r,b/2-r,0),(-a/2+r,b/2-r,math.pi/2),(-a/2+r,-b/2+r,math.pi)]:
  for j in range(n+1):angle=begin+math.pi/2*j/n;points.append((ca+r*math.cos(angle),cb+r*math.sin(angle)))
 return points
section=rounded_rectangle(t,w,P['working_strip_edge_radius_m'],P['cross_section_samples_per_corner']);vs=[];fs=[];N=len(section)
for x,y,tx,ty in path:
 n=Vector((ty,-tx,0))
 for a,z in section:vs.append(tuple(Vector((x,y,z))+a*n))
for i in range(len(path)-1):
 for j in range(N):fs.append((i*N+j,(i+1)*N+j,(i+1)*N+(j+1)%N,i*N+(j+1)%N))
fs.extend([tuple(range(N)),tuple((len(path)-1)*N+j for j in range(N-1,-1,-1))]);base=mesh_object('Editable continuous strip main loop turnbacks and folded roots',vs,fs,con);check_mesh(base)
# Ear contour is built before union, edge radii before CSG; no global post-CSG bevel.
def lug(sign):
 x0=sign*earx;lo=P['working_ear_Y_min_m'];hi=P['working_ear_Y_max_m'];mid=(hi+lo)/2;rad=P['working_ear_end_round_m'];edge=.00010;layers=[]
 for k in range(7):
  a=math.pi/2*k/6;layers.append((-t/2+edge-edge*math.cos(a),edge-edge*math.sin(a)))
 layers.append((t/2-edge,0))
 for k in range(1,7):
  a=math.pi/2*k/6;layers.append((t/2-edge+edge*math.sin(a),edge-edge*math.cos(a)))
 points=[];faces=[];C=None
 for dx,inset in layers:
  outline=rounded_rectangle(hi-lo-2*inset,w-2*inset,rad-inset,20);C=len(outline)
  for y,z in outline:points.append((x0+dx,mid+y,z))
 for i in range(len(layers)-1):
  for j in range(C):faces.append((i*C+j,i*C+(j+1)%C,(i+1)*C+(j+1)%C,(i+1)*C+j))
 faces.extend([tuple(range(C-1,-1,-1)),tuple((len(layers)-1)*C+j for j in range(C))]);o=mesh_object('Editable integral rounded folded lug '+str(sign),points,faces,con);check_mesh(o);return o
# Finite X-axis drilled bore, small estimated entry chamfer modeled in cutter profile.
def drill(sign):
 r=P['working_ear_hole_diameter_m']/2;x0=sign*earx;section=[(-.002,r+.00007),(-t/2,r+.00007),(-t/2+.00005,r),(t/2-.00005,r),(t/2,r+.00007),(.002,r+.00007)];vs=[];fs=[];n=96
 for x,radius in section:
  for k in range(n):a=math.tau*k/n;vs.append((x0+x,P['working_ear_hole_Y_m']+radius*math.cos(a),radius*math.sin(a)))
 for i in range(len(section)-1):
  for k in range(n):fs.append((i*n+k,i*n+(k+1)%n,(i+1)*n+(k+1)%n,(i+1)*n+k))
 fs.extend([tuple(range(n-1,-1,-1)),tuple((len(section)-1)*n+k for k in range(n))]);o=mesh_object('Editable finite bore Xaxis lug '+str(sign),vs,fs,con);check_mesh(o);return o
C=P['material_baseline'];mat=material('Gray formed band geometry review',C['linear_basecolor'],C['metallic'],C['roughness']);bpy.context.view_layer.update();result,data=csg(base,[lug(-1),lug(1)],[drill(-1),drill(1)],parts,mat,R,'DP101198 related smooth band and formed ears - isolated')
bm=bmesh.new();bm.from_mesh(result.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for e in bm.edges:e.smooth=len(e.link_faces)==2 and e.calc_face_angle(0)<.50
bm.to_mesh(result.data);bm.free();result.data.update()
for f in result.data.polygons:f.use_smooth=True
result.data.calc_loop_triangles();assert all(q.area>0 for q in result.data.loop_triangles);uv=result.data.uv_layers.new(name='Original100mm planar sectors')
for f in result.data.polygons:
 dominant=max(range(3),key=lambda k:abs(f.normal[k]));a,b=[k for k in range(3)if k!=dominant]
 for li in f.loop_indices:
  p=result.data.vertices[result.data.loops[li].vertex_index].co;uv.data[li].uv=(float(p[a])/.1+.5,float(p[b])/.1+.5)
checks=[check_mesh(result)];datum=bpy.data.objects.new('Intake clamp band isolated datum - not tightened',None);parts.objects.link(datum);result.parent=datum;con.hide_render=True;con.hide_viewport=True;studio(s,stage,Vector((0,0,0)));s.camera.data.clip_start=.0001
for q in stage.objects:
 if q.type=='MESH':q.hide_render=True
 if q.type=='LIGHT':q.data.energy*=.04
source=H/'engine-intake-clamp-band-v1-geometry.blend';glb=H/'engine-intake-clamp-band-v1-geometry.glb';export(glb,[datum,result]);bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':sha(glb),'collection':parts.name,'root':datum.name,'geometry':checks,'triangles':len(result.data.loop_triangles),'working_ear_X_abs_m':earx,'working_ear_bore_diameter_m':P['working_ear_hole_diameter_m'],'all_dimensions_estimated':True,'automatic_attachment_allowed':False,'remaining_observed_parts':['Tangential screw/external hardware','Curved inner overlapping bridge','Second occurrence and installed pose'],'CSG_report':{k:v for k,v in data.items()if k not in['vertices','triangles']},'no_global_post_csg_bevel':True,'art_accepted':False};(H/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'geometry-source-check.json').write_text(json.dumps(report,indent=2)+'\n');print('CLAMP_BAND_GEOMETRY',json.dumps(report),flush=True)
