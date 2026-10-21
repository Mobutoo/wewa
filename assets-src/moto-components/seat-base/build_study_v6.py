"""Bare related seat plate, bounded original construction with finite rounded wall."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt,intersect_line_line_2d
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/seat-base-study-v6';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=json.loads((H/'parameters-study-v6.json').read_text());assert (R/'creative/research/seat-base/second-long-pad-plan-v6.json').exists();ctrl=[Vector(p)for p in P['outline_periodic_cubic_Bspline_controls_XY']];M=len(ctrl)
def outline(t):
 i=int(math.floor(t))%M;u=t-math.floor(t);w=[(1-u)**3,3*u**3-6*u*u+4,-3*u**3+3*u*u+3*u+1,u**3];return sum((ctrl[(i+k-1)%M]*w[k]for k in range(4)),Vector((0,0)))/6
C=M*P['samples_per_spline_segment'];curve=[outline(k*M/C)for k in range(C)];norm=[]
for i in range(C):
 d=(curve[(i+1)%C]-curve[(i-1)%C]).normalized();norm.append(Vector((d.y,-d.x)))
r=P['edge_radius_m'];th=P['plate_thickness_m'];assert th>2*r;inset=[p-r*n for p,n in zip(curve,norm)];area=sum(a.x*b.y-b.x*a.y for a,b in zip(inset,inset[1:]+inset[:1]))/2;assert area>0
for i in range(C):
 for k in range(i+2,C):
  if i==0 and k==C-1:continue
  assert intersect_line_line_2d(inset[i],inset[(i+1)%C],inset[k],inset[(k+1)%C])is None
Y=P['height_field_y'];Z=P['underside_z']
def slopes(xs,ys):
 d=[(ys[i+1]-ys[i])/(xs[i+1]-xs[i])for i in range(len(xs)-1)];m=[d[0]]
 for i in range(1,len(xs)-1):
  if d[i-1]*d[i]<=0:m.append(0.)
  else:
   h0=xs[i]-xs[i-1];h1=xs[i+1]-xs[i];a=2*h1+h0;b=h1+2*h0;m.append((a+b)/(a/d[i-1]+b/d[i]))
 return m+[d[-1]]
sl=slopes(Y,Z)
def centerheight(y):
 k=next((i for i in range(len(Y)-1)if y<=Y[i+1]),len(Y)-2);h=Y[k+1]-Y[k];t=(y-Y[k])/h;return(2*t**3-3*t*t+1)*Z[k]+(t**3-2*t*t+t)*h*sl[k]+(-2*t**3+3*t*t)*Z[k+1]+(t**3-t*t)*h*sl[k+1]
feature_list=[P['rear_raised_ledge']]+P['additional_raised_features']
def feature_sdf(p,f):
 cx,cy=f['center_XY_m'];hx,hy=f['outer_half_extents_m'];radius=f['footprint_corner_radius_m'];qx=abs(p.x-cx)-(hx-radius);qy=abs(p.y-cy)-(hy-radius);return math.hypot(max(qx,0),max(qy,0))+min(max(qx,qy),0)-radius
def feature_height(p,f):
 t=min(1.,max(0.,-feature_sdf(p,f)/f['transition_width_m']));return-f['rise_outward_m']*(6*t**5-15*t**4+10*t**3)
def height(p):return centerheight(p.y)+P['cross_camber_m']*(p.x/.14)**2+sum(feature_height(p,f)for f in feature_list)
def gradient(p):
 from types import SimpleNamespace as Pt
 e=1e-5;g=Vector((2*P['cross_camber_m']*p.x/(.14**2),(centerheight(p.y+e)-centerheight(p.y-e))/(2*e)))
 for f in feature_list:
  e=f['derivative_epsilon_m'];g+=Vector(((feature_height(Pt(x=p.x+e,y=p.y),f)-feature_height(Pt(x=p.x-e,y=p.y),f))/(2*e),(feature_height(Pt(x=p.x,y=p.y+e),f)-feature_height(Pt(x=p.x,y=p.y-e),f))/(2*e)))
 return g

def inside(p):
 hit=False
 for a,b in zip(inset,inset[1:]+inset[:1]):
  if (a.y>p.y)!=(b.y>p.y)and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
 return hit
# Additional inner clockwise boundary: rounded lip surrounding one proposed aperture.
loops=[{'id':'outer','curve':curve,'normal':norm,'inset':inset,'radius':r,'input_start':0}];constraint_points=list(inset)
for hole in P['apertures']:
 hc=Vector(hole['world_XY_m']);count=hole['ring_segments'];radius=hole['vertical_wall_radius_m'];hr=hole['lip_radius_m'];hp=[];hn=[]
 for k in range(count):
  angle=-2*math.pi*k/count;out=Vector((math.cos(angle),math.sin(angle)));hp.append(hc+radius*out);hn.append(-out)
 hi=[p-hr*n for p,n in zip(hp,hn)];loops.append({'id':hole['id'],'curve':hp,'normal':hn,'inset':hi,'radius':hr,'input_start':len(constraint_points)});constraint_points.extend(hi)
def inside_poly(p,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a.y>p.y)!=(b.y>p.y)and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
 return hit
def near_feature_contour(p):
 for f in feature_list:
  d=feature_sdf(p,f);tw=f['transition_width_m'];layers=f['transition_layers'];eps=P['interior_grid_exclusion_near_feature_constraint_m']
  if -tw-eps<=d<=eps and min(abs(d+tw*k/layers)for k in range(layers+1))<eps:return True
 return False
step=P['interior_grid_spacing_m'];lo=[min(p[i]for p in inset)for i in range(2)];hi=[max(p[i]for p in inset)for i in range(2)];inputs=list(constraint_points)
for xi in range(math.ceil(lo[0]/step),math.floor(hi[0]/step)+1):
 for yi in range(math.ceil(lo[1]/step),math.floor(hi[1]/step)+1):
  p=Vector((xi*step,yi*step))
  if inside(p)and not any(inside_poly(p,l['inset'])for l in loops[1:])and not near_feature_contour(p):inputs.append(p)
# Nested explicit feature contours sample the C2 height ramp; they are cap constraints only, not holes.
feature_contours=[]
for ledge in feature_list:
 lc0=Vector(ledge['center_XY_m']);hx,hy=ledge['outer_half_extents_m'];lr0=ledge['footprint_corner_radius_m'];tw=ledge['transition_width_m']
 for layer in range(ledge['transition_layers']+1):
  inset_distance=tw*layer/ledge['transition_layers'];radius=lr0-inset_distance;assert radius>0;points=[]
  corners=[(hx-lr0,hy-lr0),(-hx+lr0,hy-lr0),(-hx+lr0,-hy+lr0),(hx-lr0,-hy+lr0)]
  for ci,(cx,cy) in enumerate(corners):
   a0=math.pi*ci/2
   for k in range(ledge['corner_segments']+1):
    a=a0+math.pi*k/(2*ledge['corner_segments']);points.append(lc0+Vector((cx+radius*math.cos(a),cy+radius*math.sin(a))))
   end=points[-1];ncx,ncy=corners[(ci+1)%4];a1=a0+math.pi/2;nextp=lc0+Vector((ncx+radius*math.cos(a1),ncy+radius*math.sin(a1)));count=math.ceil((nextp-end).length/ledge['straight_segment_step_m'])
   for k in range(1,count):points.append(end.lerp(nextp,k/count))
  feature_contours.append((len(inputs),len(points)));inputs.extend(points)
 # Dense flat-plateau points, avoiding duplicate boundary vertices.
 local_step=ledge['interior_grid_spacing_m']
 for xi in range(math.ceil((lc0.x-hx)/local_step),math.floor((lc0.x+hx)/local_step)+1):
  for yi in range(math.ceil((lc0.y-hy)/local_step),math.floor((lc0.y+hy)/local_step)+1):
   p=Vector((xi*local_step,yi*local_step))
   if feature_sdf(p,ledge)<-tw-.00001 and not near_feature_contour(p):inputs.append(p)
constraints=[]
for start,count in feature_contours:constraints.extend((start+i,start+(i+1)%count)for i in range(count))
for loop in loops:
 start=loop['input_start'];count=len(loop['inset']);constraints.extend((start+i,start+(i+1)%count)for i in range(count))
xy,cdtedges,rawfaces,orig,_,_=delaunay_2d_cdt(inputs,constraints,[list(range(C))],1,P['CDT_epsilon_m'],True);assert all(len(f)==3 for f in rawfaces);cdtfaces=[]
for f in rawfaces:
 center=sum((xy[i]for i in f),Vector((0,0)))/3
 if not any(inside_poly(center,l['inset'])for l in loops[1:]):cdtfaces.append(f)
boundary={}
for i,ids in enumerate(orig):
 for old in ids:
  if old<len(constraint_points):assert old not in boundary;boundary[old]=i
assert len(boundary)==len(constraint_points);boundary_delta=max((xy[boundary[i]]-constraint_points[i]).length for i in range(len(constraint_points)));assert boundary_delta<1e-7
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.cycles.denoiser='OPENIMAGEDENOISE';sc.render.threads_mode='FIXED';sc.render.threads=1;col=bpy.data.collections.new('WEWA_SEAT_BASE_PLATE_STUDY');sc.collection.children.link(col);root=bpy.data.objects.new('SEAT_BASE_ESTIMATED_DATUM',None);col.objects.link(root)
verts=[Vector((p.x,p.y,height(p)))for p in xy];base_n=[Vector((*gradient(p),-1)).normalized()for p in xy];ncap=len(verts);verts +=[v+Vector((0,0,th))for v in verts];normals=base_n+[-n for n in base_n];faces=[];uvs=[];regions=[]
def capuv(p):return((p.x-lo[0])/(hi[0]-lo[0]),(p.y-lo[1])/(hi[1]-lo[1]))
def face(ix,uv,reg):faces.append(tuple(ix));uvs.append(uv);regions.append(reg)
for ids in cdtfaces:
 a,b,c=[xy[i]for i in ids]
 if (b-a).cross(c-a)<0:ids=ids[::-1]
 face(ids[::-1],[capuv(xy[i])for i in ids[::-1]],0);face([ncap+i for i in ids],[capuv(xy[i])for i in ids],1)
# Outer rim and inner hole wall share the same finite-wall construction.
q=P['edge_fillet_quarter_segments'];layers=[('lower',-math.pi/2+math.pi*k/(2*q))for k in range(1,q+1)]+[('wall',0)]+[('upper',math.pi*k/(2*q))for k in range(1,q)]
for loop in loops:
 lc=loop['curve'];ln=loop['normal'];lr=loop['radius'];count=len(lc);start=loop['input_start'];rings=[[boundary[start+i]for i in range(count)]]
 for typ,angle in layers:
  ring=[];ringpos=[];profile=[]
  for p,n in zip(lc,ln):
   if typ=='wall':v=p;z=height(v)+th-lr;der=Vector((0,0,1))
   else:
    v=p-n*lr+n*lr*math.cos(angle);z=height(v)+(lr if typ=='lower'else th-lr)+lr*math.sin(angle);dxy=-n*lr*math.sin(angle);der=Vector((dxy.x,dxy.y,gradient(v).dot(dxy)+lr*math.cos(angle)))
   ringpos.append(Vector((v.x,v.y,z)));profile.append(der)
  for i,p in enumerate(ringpos):
   tangent=ringpos[(i+1)%count]-ringpos[(i-1)%count];normal=tangent.cross(profile[i]).normalized();ring.append(len(verts));verts.append(p);normals.append(normal)
  rings.append(ring)
 rings.append([ncap+boundary[start+i]for i in range(count)]);arc=[0.]
 for a,b in zip(lc,lc[1:]+lc[:1]):arc.append(arc[-1]+(b-a).length)
 for k in range(len(rings)-1):
  for i in range(count):
   nxt=(i+1)%count;a=rings[k][i];b=rings[k][nxt];c=rings[k+1][i];d=rings[k+1][nxt];u0=arc[i]/arc[-1];u1=arc[i+1]/arc[-1];v0=k/(len(rings)-1);v1=(k+1)/(len(rings)-1);region=2 if loop['id']=='outer'else 3;face((a,b,d),[(u0,v0),(u1,v0),(u1,v1)],region);face((a,d,c),[(u0,v0),(u1,v1),(u0,v1)],region)
mesh=bpy.data.meshes.new('Finite bare molded plate with explicit rounded rim');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Bare related seat base plate - estimated',mesh);col.objects.link(ob);ob.parent=root;uv=mesh.uv_layers.new(name='Original plate UV');custom=[]
for p in mesh.polygons:
 p.use_smooth=True
 for k,li in enumerate(p.loop_indices):uv.data[li].uv=uvs[p.index][k];custom.append(tuple(normals[mesh.loops[li].vertex_index]))
mesh.normals_split_custom_set(custom);attr=mesh.attributes.new('PLATE_REGION','INT','FACE')
for i,v in enumerate(regions):attr.data[i].value=v
mat=bpy.data.materials.new('Neutral plate gray - not final resin');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.32;mesh.materials.append(mat);ob['scope']='Bare plate plus six proposed plate apertures. ONE rear ledge plus TWO longpads. Other pads/ribs/supports/mounts/foam not built.';ob['identity']='RelatedJV191001 exterior underside proposal, not exactcurrentRDC';ob['dimensions']='All outline/height/thickness/radius authored estimates'
world=bpy.data.worlds.new('Neutral plate studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);world.node_tree.nodes['Background'].inputs[1].default_value=.3;sc.world=world;target=Vector((0,.73,-.27))
for name,loc,power,size in [('Key',(-.5,.25,-.8),45,.55),('Fill',(.6,.8,-.55),25,.55),('Strip',(.05,1.35,-.65),35,.3)]:
 light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='RECTANGLE';light.size=size;light.size_y=.15 if name=='Strip'else size;o=bpy.data.objects.new(name,light);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Plate study camera');co=bpy.data.objects.new(cam.name,cam);sc.collection.objects.link(co);co.location=(-1,.12,-1.1);co.rotation_euler=(target-co.location).to_track_quat('-Z','Y').to_euler();cam.lens=60;cam.sensor_fit='HORIZONTAL';cam.sensor_width=36;cam.clip_start=.001;cam.clip_end=20;sc.camera=co;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100;bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=ob;source=H/'seat-base-study-v6.blend';export=H/'seat-base-study-v6.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
areas=[p.area for p in mesh.polygons];counts=Counter(tuple(sorted((a,b)))for f in faces for a,b in zip(f,f[1:]+f[:1]));ref=verts[0];vol=sum(sum((float(verts[a][i])-float(ref[i]))*((float(verts[b][(i+1)%3])-float(ref[(i+1)%3]))*(float(verts[c][(i+2)%3])-float(ref[(i+2)%3]))-(float(verts[b][(i+2)%3])-float(ref[(i+2)%3]))*(float(verts[c][(i+1)%3])-float(ref[(i+1)%3])))for i in range(3))/6 for a,b,c in faces);report={'schema':1,'source_sha256':sha(source),'export_sha256':sha(export),'builder_sha256':sha(Path(__file__)),'parameters_sha256':sha(H/'parameters-study-v6.json'),'object':ob.name,'objects':[ob.name],'collection':col.name,'vertices':len(verts),'triangles':len(faces),'cap_CDT_vertices':ncap,'cap_CDT_input_points':len(inputs),'cap_CDT_triangles':len(cdtfaces),'original_boundary_points':len(constraint_points),'outer_boundary_points':C,'aperture_boundaries':len(loops)-1,'raised_ledge_contour_constraints':len(feature_contours),'raised_feature_parameters':feature_list,'discarded_constrained_hole_triangles':len(rawfaces)-len(cdtfaces),'actual_CDT_boundary_displacement_m':boundary_delta,'CDT_epsilon_m':P['CDT_epsilon_m'],'CDT_is_metrology':False,'rounded_rim_profile_rings':len(rings),'minimum_triangle_area_m2':min(areas),'exact_zero_area_triangles':sum(a==0 for a in areas),'non_two_face_edges':sum(c!=2 for c in counts.values()),'plate_material_volume_m3':vol,'external_libraries':0,'external_images':[],'scope':'Bare plate plus six proposed finite plate apertures, six finite apertures and rear ledge plus two longpads, no ribs/supports/currentRDC fit reception','art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');assert min(areas)>0 and vol>0 and report['non_two_face_edges']==0;print(json.dumps(report))
