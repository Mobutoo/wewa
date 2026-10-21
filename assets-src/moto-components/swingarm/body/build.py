"""Original related 52PF0219 body study. Every metric is explicitly estimated.
Build a partial base first; formed returns/tabs/welds are separate authoring stages.
Construction meshes stay in a hidden local collection, never exported or externally linked.
"""
import bpy,bmesh,math,json,hashlib,tempfile,subprocess,shutil,os,sys,struct
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/swingarm-body-v1';O.mkdir(parents=True,exist_ok=True);P=json.loads((H/'parameters.json').read_text());stage='full'if'--stage=full'in sys.argv else'base';N=320
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new(P['collection']);s.collection.children.link(col);construct=bpy.data.collections.new('LOCAL_ORIGINAL_CONSTRUCTION_VOLUMES_NOT_EXPORT');s.collection.children.link(construct)
def obj(name,vertices,faces):
 m=bpy.data.meshes.new(name);m.from_pydata(vertices,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);construct.objects.link(o);return o
def rounded_rect(half_a,half_b,r,steps=20):
 points=[]
 for a,b,start in[(half_a-r,half_b-r,0),(-half_a+r,half_b-r,90),(-half_a+r,-half_b+r,180),(half_a-r,-half_b+r,270)]:
  for j in range(steps+1):
   t=math.radians(start+j*90/steps);points.append((a+r*math.cos(t),b+r*math.sin(t)))
 return points
def extrude(name,profile,positions,xyz):
 # Concave caps tessellated in source, matching exact authored boundary.
 v=[xyz(a,b,t)for t in positions for a,b in profile];n=len(profile);f=[]
 for k in range(len(positions)-1):
  for j in range(n):jj=(j+1)%n;f.append((k*n+j,k*n+jj,(k+1)*n+jj,(k+1)*n+j))
 poly=[Vector((a,b,0))for a,b in profile];lookup={tuple(v):i for i,v in enumerate(poly)}
 for tri in tessellate_polygon([poly]):
  inds=[p if isinstance(p,int)else lookup[tuple(p)]for p in tri];f.append(tuple(inds));f.append(tuple((len(positions)-1)*n+j for j in reversed(inds)))
 return obj(name,v,f)
def lathe_x(name,cx,cy,cz,profile):
 v=[(cx+x,cy+r*math.cos(j*2*math.pi/N),cz+r*math.sin(j*2*math.pi/N))for x,r in profile for j in range(N)];f=[]
 for k in range(len(profile)-1):
  for j in range(N):jj=(j+1)%N;f.append((k*N+j,k*N+jj,(k+1)*N+jj,(k+1)*N+j))
 f.append(tuple(range(N-1,-1,-1)));f.append(tuple((len(profile)-1)*N+j for j in range(N)));return obj(name,v,f)
railwidth=P['rail_width_x_m_estimated'];railheight=P['rail_height_z_m_estimated'];wall=P['rail_wall_m_estimated'];end=P['working_body_rear_end_y_m_estimated'];slope=(.110-.103)/end
railx=lambda y:.103+slope*y
features=[];drills=[];base=None
for sign in[-1,1]:
 beam=extrude('Original rounded rectangular rail '+str(sign),rounded_rect(railwidth/2,railheight/2,.002),[-.008+(end+.008)*i/P['rail_longitudinal_bands'] for i in range(P['rail_longitudinal_bands']+1)],lambda a,b,y:(sign*railx(y)+a,y,b))
 if base is None:base=beam
 else:features.append(beam)
 # Real estimated enclosed cavity; leave front socket attachment and rear cap.
 drills.append(extrude('Estimated hollow rail cavity '+str(sign),rounded_rect(railwidth/2-wall,railheight/2-wall,.0002),[.022+(end-wall-.022)*i/P['rail_longitudinal_bands'] for i in range(P['rail_longitudinal_bands']+1)],lambda a,b,y:(sign*railx(y)+a,y,b)))
 cx=sign*.103;w=P['pivot_housing_axial_width_m_estimated']/2;rad=P['pivot_housing_outer_diameter_m_estimated']/2;be=.0006;prof=[(-w,rad-be)]
 for j in range(1,17):
  t=j*math.pi/32;prof.append((-w+be*(1-math.cos(t)),rad-be+be*math.sin(t)))
 prof.append((w-be,rad))
 for j in range(1,17):
  t=j*math.pi/32;prof.append((w-be+be*math.sin(t),rad-be+be*math.cos(t)))
 features.append(lathe_x('Separate pivot housing '+str(sign),cx,0,0,prof))
 # Two lateral walls pierced by each actual rear slot; no hidden adjustment thread invented.
 length=P['rear_axle_slot_length_m_estimated'];height=P['rear_axle_slot_height_m_estimated'];y=P['working_rear_slot_y_m_estimated'];x=sign*railx(y)
 drills.append(extrude('Rear axle slot '+str(sign),rounded_rect(length/2,height/2,P['rear_slot_corner_radius_m_estimated']),[x-.030,x+.030],lambda a,b,t:(t,y+a,b)))
# One transverse cutter opens separated housings and overlapping rail noses, not a through tube.
drills.append(lathe_x('Open pivot axes through two separate housings',0,0,0,[(-.16,P['pivot_housing_bore_m_estimated']/2),(.16,P['pivot_housing_bore_m_estimated']/2)]))
# Broad formed U bridge, with splayed outer legs touching only the inner wall of each rail.
front=P['U_plate_front_y_m_estimated'];cy=P['U_plate_arch_center_y_m_estimated'];ir=P['U_plate_inner_radius_m_estimated'];last=P['U_plate_rear_leg_end_y_m_estimated'];outer=lambda y:railx(y)-railwidth/2+.0004
p=[]
for j in range(49):
 x=-outer(front)+2*outer(front)*j/48;y=front+.025*(1-(x/outer(front))**2);p.append((x,y))
def full_inner_path():
 def smooth(a,b,v):
  t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)
 right=[(ir+(outer(last)-ir-.004)*smooth(.300,last,y),y)for y in[last-(last-cy)*i/48 for i in range(49)]]
 return right+[(ir*math.cos(-math.pi*j/160),cy+ir*math.sin(-math.pi*j/160))for j in range(1,161)]+[(-x,y)for x,y in reversed(right[:-1])]
def pathnormals(path):
 normals=[]
 for k in range(len(path)):
  d=Vector(path[min(k+1,len(path)-1)])-Vector(path[max(k-1,0)]);normals.append(Vector((-d.y,d.x)).normalized())
 return normals
if stage=='full':
 path=full_inner_path();path_normals=pathnormals(path);topedge=[(x+n.x*.0024,y+n.y*.0024)for(x,y),n in zip(path,path_normals)]
 p.append((outer(last),last));p.extend(topedge);p.append((-outer(last),last))
else:
 p.extend([(outer(last),last),(ir,last),(ir,cy)])
 for j in range(1,161):
  t=-math.pi*j/160;p.append((ir*math.cos(t),cy+ir*math.sin(t)))
 p.extend([(-ir,last),(-outer(last),last)])
zt=P['U_plate_top_z_m_estimated'];th=P['U_plate_thickness_m_estimated'];features.append(extrude('Broad U plate original boundary',p,[zt-th,zt],lambda a,b,z:(a,b,z)))

if stage=='full':
 # Actual formed return envelope: 2.4mm outer radius and 0.6mm inner radius.
 # Its upper flat overlaps the U sheet, whose inner edge is offset by 2.4mm.
 cross=[(0,.0046),(0,.0096)]
 for j in range(1,25):
  t=j*math.pi/48;cross.append((.0024-.0024*math.cos(t),.0096+.0024*math.sin(t)))
 cross.extend([(.005,.012),(.005,.0102),(.0024,.0102)])
 for j in range(1,25):
  t=math.pi/2-j*math.pi/48;cross.append((.0024-.0006*math.cos(t),.0096+.0006*math.sin(t)))
 cross.extend([(.0018,.0046),(.0014,.0042),(.0004,.0042)])
 path=full_inner_path();path_normals=pathnormals(path)
 vv=[]
 for (x,y),normal in zip(path,path_normals):vv.extend([(x+normal.x*a,y+normal.y*a,z)for a,z in cross])
 nn=len(cross);ff=[]
 for k in range(len(path)-1):
  for j in range(nn):jj=(j+1)%nn;ff.append((k*nn+j,k*nn+jj,(k+1)*nn+jj,(k+1)*nn+j))
 cap=tessellate_polygon([[Vector((a,z,0))for a,z in cross]])
 for tri in cap:
  ff.append(tuple(tri));ff.append(tuple((len(path)-1)*nn+i for i in reversed(tri)))
 features.append(obj('Rolled inner U return - native radius section',vv,ff))
 def roundpoly(points,amount=.002,steps=10):
  result=[]
  for i,p in enumerate(points):
   p=Vector(p);prev=Vector(points[i-1]);nxt=Vector(points[(i+1)%len(points)]);a=p+(prev-p).normalized()*min(amount,(prev-p).length*.24);b=p+(nxt-p).normalized()*min(amount,(nxt-p).length*.24)
   for j in range(steps+1):
    t=j/steps;q=(1-t)**2*a+2*(1-t)*t*p+t*t*b;result.append(tuple(q))
  return result
 def plate(name,profile,cx,thick):
  # Convex profile inset rings form an actual rounded sheet edge, no Bevel modifier.
  signed=sum(profile[i][0]*profile[(i+1)%len(profile)][1]-profile[(i+1)%len(profile)][0]*profile[i][1]for i in range(len(profile)));orientation=1 if signed>0 else-1
  def inset(distance):
   out=[]
   for i,p in enumerate(profile):
    a=Vector(profile[i-1]);b=Vector(p);c=Vector(profile[(i+1)%len(profile)]);u=(b-a).normalized();v=(c-b).normalized();n1=Vector((-u.y,u.x))*orientation;n2=Vector((-v.y,v.x))*orientation;bis=n1+n2;den=bis.dot(n1);out.append(tuple(b+bis*(distance/den)))
   return out
  rad=.00025;rings=[]
  for j in range(9):
   t=j*math.pi/16;rings.append((-thick/2+rad*(1-math.cos(t)),inset(rad*(1-math.sin(t)))))
  for j in range(9):
   t=j*math.pi/16;rings.append((thick/2-rad+rad*math.sin(t),inset(rad*(1-math.cos(t)))))
  n=len(profile);verts=[(cx+off,y,z)for off,poly in rings for y,z in poly];faces=[]
  for k in range(len(rings)-1):
   for j in range(n):jj=(j+1)%n;faces.append((k*n+j,k*n+jj,(k+1)*n+jj,(k+1)*n+j))
  for k in[0,len(rings)-1]:
   poly=[Vector((a,b,0))for a,b in rings[k][1]]
   for tri in tessellate_polygon([poly]):faces.append(tuple(k*n+i for i in tri))
  return obj(name,verts,faces)
 ty=P['shock_tab_hole_y_m_estimated'];tz=P['shock_tab_hole_z_m_estimated'];t=P['tab_sheet_thickness_m_estimated'];gap=P['clevis_clear_gap_x_m_estimated'];hole=P['tab_hole_diameter_m_estimated']/2
 profile=roundpoly([(ty-.033,.013),(ty+.026,.013),(ty+.013,tz+.006),(ty+.005,tz+.012),(ty-.006,tz+.012),(ty-.016,tz+.004)])
 for sign in[-1,1]:
  rail=sign*railx(ty)
  for edge in[-1,1]:
   cx=rail+edge*(gap/2+t/2);features.append(plate('Paired pierced mounting tab '+str(sign)+' '+str(edge),profile,cx,t));drills.append(lathe_x('Tab open hole and mouth radius '+str(sign)+' '+str(edge),cx,ty,tz,[(-t/2-.002,hole+.00035),(-t/2,hole+.00035),(-t/2+.00035,hole),(t/2-.00035,hole),(t/2,hole+.00035),(t/2+.002,hole+.00035)]))
  # Small short transverse tubular attachment observed at the front of each rail.
  yy=P['small_mount_tube_y_m_estimated'];zz=.0185;xx=sign*railx(yy);tw=P['small_mount_tube_length_x_m_estimated']/2;rr=P['small_mount_tube_outer_diameter_m_estimated']/2
  features.append(lathe_x('Short hollow front attachment '+str(sign),xx,yy,zz,[(-tw,rr-.0003),(-tw+.0003,rr),(tw-.0003,rr),(tw,rr-.0003)]));drills.append(lathe_x('Short front attachment open axis '+str(sign),xx,yy,zz,[(-tw-.003,P['small_mount_tube_inner_diameter_m_estimated']/2),(tw+.003,P['small_mount_tube_inner_diameter_m_estimated']/2)]))
 ay=P['additional_tab_hole_y_m_estimated'];az=P['additional_tab_hole_z_m_estimated'];ax=-(railx(ay)+.0105)
 ap=roundpoly([(ay-.013,-.013),(ay+.013,-.013),(ay+.011,az-.010),(ay-.008,az-.013)])
 features.append(plate('Additional asymmetric downward tab - function side conditional',ap,ax,t));drills.append(lathe_x('Asymmetric tab actual open hole',ax,ay,az,[(-.005,.00325),(.005,.00325)]))


if stage=='full':
 # Original continuous weld envelopes. Dimensions, ripple and path are estimates,
 # not sampled photopixels or an assertion about a real welding process.
 def weld(name,points,preferred,r1,r2,phase=0):
  pp=[Vector(q)for q in points];arc=[0.0]
  for a,b in zip(pp,pp[1:]):arc.append(arc[-1]+(b-a).length)
  verts=[];nr=20;pitch=P['weld_ripple_pitch_m_estimated']
  for k,(q,d)in enumerate(zip(pp,arc)):
   tangent=(pp[min(k+1,len(pp)-1)]-pp[max(k-1,0)]).normalized();u=Vector(preferred);u=(u-tangent*u.dot(tangent)).normalized();v=tangent.cross(u).normalized()
   aa=min(1,max(0,d/.003));bb=min(1,max(0,(arc[-1]-d)/.003));taper=.25+.75*(aa*aa*(3-2*aa))*(bb*bb*(3-2*bb));ripple=1+.065*math.sin(2*math.pi*d/pitch+phase)+.025*math.sin(2*math.pi*d/(3.7*pitch)+phase*.71)
   for j in range(nr):
    t=j*2*math.pi/nr;verts.append(tuple(q+taper*ripple*(r1*math.cos(t)*u+r2*math.sin(t)*v)))
  faces=[]
  for k in range(len(pp)-1):
   for j in range(nr):jj=(j+1)%nr;faces.append((k*nr+j,k*nr+jj,(k+1)*nr+jj,(k+1)*nr+j))
  faces.extend([tuple(range(nr-1,-1,-1)),tuple((len(pp)-1)*nr+j for j in range(nr))]);features.append(obj(name,verts,faces))
 def line(a,b,step=.00035):
  a=Vector(a);b=Vector(b);n=math.ceil((b-a).length/step);return[tuple(a+(b-a)*i/n)for i in range(n+1)]
 for sign in[-1,1]:
  for iz,z in enumerate([zt-.00020,zt-th+.00020]):
   yy=[.112+(.376-.112)*i/760 for i in range(761)];weld('U plate to rail weld '+str(sign)+' '+str(iz),[(sign*(railx(y)-railwidth/2),y,z)for y in yy],(0,0,1),.0007,.0013,sign+iz*.8)
  # Short half-ring housing/rail junction; no invented full front ring.
  aa=[-math.pi/2+math.pi*i/260 for i in range(261)];weld('Rear half pivot-housing weld '+str(sign),[(sign*.1152,.0158*math.cos(a),.0158*math.sin(a))for a in aa],(1,0,0),.0009,.0012,sign*.6)
  ty=P['shock_tab_hole_y_m_estimated'];cx0=sign*railx(ty);t=P['tab_sheet_thickness_m_estimated'];gap=P['clevis_clear_gap_x_m_estimated']
  for edge in[-1,1]:
   cx=cx0+edge*(gap/2+t/2)
   for side in[-1,1]:
    wx=max(cx0-.0109,min(cx0+.0109,cx+side*t/2));weld('Mount tab base weld '+str(sign)+' '+str(edge)+' '+str(side),line((wx,ty-.034,.0147),(wx,ty+.027,.0147)),(0,0,1),.0007,.0013,sign*.7+edge+side*.4)
  yy=P['small_mount_tube_y_m_estimated'];xx=sign*railx(yy)
  for side in[-1,1]:weld('Front attachment root weld '+str(sign)+' '+str(side),line((xx-.011,yy+side*.003,.0148),(xx+.011,yy+side*.003,.0148)),(0,0,1),.0007,.0010,sign+side)
 ay=P['additional_tab_hole_y_m_estimated'];cx0=-railx(ay);ax=-(railx(ay)+.0105);t=P['tab_sheet_thickness_m_estimated']
 for side in[-1,1]:
  wx=max(cx0-.0111,ax+side*t/2);weld('Additional asymmetric tab root weld '+str(side),line((wx,ay-.015,-.0145),(wx,ay+.015,-.0145)),(0,0,1),.0007,.0013,side*.9)

# Robust source CSG, pinned to one available CPU; no repair of exported buffers.
def volume(o):
 m=o.data;bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-9);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-11);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert not sum(not e.is_manifold for e in bm.edges),(o.name,'operand not closed');assert bm.calc_volume(signed=True)>0;bm.to_mesh(m);bm.free();m.calc_loop_triangles();return{'name':o.name,'vertices':[list(v.co)for v in m.vertices],'triangles':[list(t.vertices)for t in m.loop_triangles]}
with tempfile.TemporaryDirectory(prefix='wewa-swingarm-')as t:
 inp=Path(t)/'in.json';out=Path(t)/'out.json';inp.write_text(json.dumps({'base':volume(base),'features':[volume(o)for o in features],'drills':[volume(o)for o in drills]}));cpu=min(os.sched_getaffinity(0));subprocess.run([shutil.which('python'),str(H/'csg.py'),str(inp),str(out)],check=True,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'},preexec_fn=lambda:os.sched_setaffinity(0,{cpu}));fused=json.loads(out.read_text())
o=obj('Related swingarm welded body - estimated reconstruction'if stage=='full'else'Partial base body study - no tabs returns or welds yet',fused['vertices'],fused['triangles']);construct.objects.unlink(o);col.objects.link(o);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-11);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
# Reconnect coplanar diagonals only, with exact position/volume preservation.
retri=[]
plane_specs=[((0,0,1),z)for z in[zt,zt-th,railheight/2,-railheight/2,railheight/2-wall,-railheight/2+wall]]+[((0,1,0),y)for y in[.022,end-wall,end,-.008]]
for sign in[-1,1]:
 for edge in[-railwidth/2,railwidth/2,-railwidth/2+wall,railwidth/2-wall]:plane_specs.append(((1,-sign*slope,0),sign*.103+edge))
 for side in[-1,1]:plane_specs.append(((1,0,0),sign*.103+side*P['pivot_housing_axial_width_m_estimated']/2))
for normal,value in plane_specs:
 axis=next((a for a in range(3)if normal[a]==1 and sum(abs(v)for v in normal)==1),None)
 if axis is not None:value=struct.unpack('f',struct.pack('f',value))[0]
 nv=Vector(normal);fs=[f for f in bm.faces if all(abs(nv.dot(v.co)-value)<3e-8 for v in f.verts)];ss=set(fs);es=[e for e in bm.edges if len(e.link_faces)==2 and all(f in ss for f in e.link_faces)]
 if not es:continue
 before=bm.calc_volume(signed=True);pts={tuple(v.co)for v in bm.verts};bmesh.ops.beautify_fill(bm,faces=fs,edges=es,method='AREA');after=bm.calc_volume(signed=True);assert pts=={tuple(v.co)for v in bm.verts}and abs(after/before-1)<1e-7;retri.append({'normal':normal,'offset_m':value,'faces':len(fs),'volume_relative_change':abs(after/before-1),'positions_preserved':True})
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.to_mesh(o.data);bm.free();o.data.update();o.data.set_sharp_from_angle(angle=.55)
for f in o.data.polygons:
 # Native flats stay exactly flat; small roundovers/cylinders interpolate.
 n=f.normal;flat=abs(n.z)>.999999 or abs(n.y)>.999999 or abs(n.x)>.999999 or any(abs(abs(n.x)-1/math.sqrt(1+slope*slope))<1e-6 and abs(n.z)<1e-6 for _ in[0]);f.use_smooth=not flat
mat=bpy.data.materials.new('Geometry neutral gray - finish pending');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.21,.23,.25,1);bs.inputs['Roughness'].default_value=.28;o.data.materials.append(mat)
uv=o.data.uv_layers.new(name='Estimated 10mm dominant projection')
for f in o.data.polygons:
 axis=max(range(3),key=lambda a:abs(f.normal[a]));sign=1 if f.normal[axis]>=0 else-1
 for li in f.loop_indices:
  v=o.data.vertices[o.data.loops[li].vertex_index].co;pair=(sign*v.y,v.z)if axis==0 else(-sign*v.x,v.z)if axis==1 else(sign*v.x,v.y);uv.data[li].uv=(pair[0]/.010,pair[1]/.010)
for ob in construct.objects:ob.hide_render=True;ob.hide_set(True)
o.data.calc_loop_triangles();areas=[(o.data.vertices[t.vertices[1]].co-o.data.vertices[t.vertices[0]].co).cross(o.data.vertices[t.vertices[2]].co-o.data.vertices[t.vertices[0]].co).length/2 for t in o.data.loop_triangles];assert nm==0 and vol>0 and min(areas)>1e-18,(nm,vol,min(areas))
tree=BVHTree.FromPolygons([v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True);probes=[]
for name,origin,direction,length,expected in[('open pivot axis',(-.16,0,0),(1,0,0),.32,True),('no central transverse tube',(0,-.04,.014),(0,1,0),.08,True),('open rear slots',(-.16,.520,0),(1,0,0),.32,True),('open U centre',(0,.250,.05),(0,0,-1),.10,True),('U front bridge material',(0,.13,.05),(0,0,-1),.10,False)]:
 clear=tree.ray_cast(Vector(origin),Vector(direction),length)[0]is None;probes.append({'name':name,'origin_m':origin,'direction':direction,'length_m':length,'clear':clear,'expected_clear':expected});assert clear==expected,probes[-1]
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.gltf(filepath=str(H/('swingarm-body-raw-inspection.glb'if stage=='full'else'swingarm-body-base-study.glb')),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
studio=bpy.data.collections.new('LOCAL_NEUTRAL_STUDIO_NOT_EXPORT');s.collection.children.link(studio)
s.world=bpy.data.worlds.new('Neutral gray');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.12,.12,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
for name,loc,power,size in[('KEY',(.4,.1,.7),25,.65),('FILL',(-.5,.4,.4),12,.6),('RIM',(.1,.65,.5),18,.45),('LOWER_FILL',(.1,.3,-.5),12,.6)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;ob=bpy.data.objects.new(name,l);studio.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,.26,0))-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('SWINGARM_CAMERA',bpy.data.cameras.new('SWINGARM_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.6,.8,.6);cam.rotation_euler=(Vector((0,.27,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.72;cam.data.clip_start=.001;cam.data.clip_end=5;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
bpy.ops.wm.save_as_mainfile(filepath=str(H/('swingarm-body-raw-v1.blend'if stage=='full'else'swingarm-body-base-study.blend')),compress=True)
r={'component_id':P['component_id'],'revision':'swingarm-body-v1'if stage=='full'else'swingarm-body-base-study','partial_not_finished_candidate':stage!='full','scope':'Rails, slots, pivot housings, formed tapered U return, paired mounting tabs, two short front tubes, one asymmetric tab and original estimated weld envelopes.'if stage=='full'else'Two hollow rails with rear slots, two separated pivot housings and U plate. Returns, tabs and welds NOT yet modelled.','vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'connected_shells':fused['solid_components'],'nonmanifold_edges':nm,'signed_volume_m3':vol,'min_triangle_area_m2':min(areas),'zero_area_at_1e18_m2':sum(a<=1e-18 for a in areas),'probes':probes,'source_only_csg_stages':fused['stages'],'coplanar_diagonals_only':retri,'all_dimensions_estimated':True,'current_RDC_identity_verified':False,'external_libraries':[l.filepath for l in bpy.data.libraries],'art_accepted':False,'source_sha256':hashlib.sha256((H/('swingarm-body-raw-v1.blend'if stage=='full'else'swingarm-body-base-study.blend')).read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((H/('swingarm-body-raw-inspection.glb'if stage=='full'else'swingarm-body-base-study.glb')).read_bytes()).hexdigest()};(O/('raw-source-geometry-check.json'if stage=='full'else'base-study-geometry-check.json')).write_text(json.dumps(r,indent=2)+'\n');print('WEWA_SWINGARM_BASE_STUDY',json.dumps(r))
