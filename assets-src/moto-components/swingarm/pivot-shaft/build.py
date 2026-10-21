"""Original continuous shared-ring shaft, estimated collar/head/helix; no CSG/GLB repairs."""
import bpy,bmesh,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/swingarm-pivot-shaft-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;col=bpy.data.collections.new(P['collection']);s.collection.children.link(col);studio=bpy.data.collections.new('LOCAL_NEUTRAL_STUDIO_NOT_EXPORT');s.collection.children.link(studio)
L=P['vendor_related_overall_length_m'];xmin=-L/2;xmax=L/2;rs=P['vendor_related_shank_diameter_m']/2;major=P['vendor_related_thread_diameter_m']/2;depth=P['thread_full_depth_m_estimated'];pitch=P['thread_pitch_m_estimated'];A=P['head_across_flats_m_estimated']/2;corner=P['head_hex_corner_radius_m_estimated'];tip=xmin+.0006;fullstart=xmin+.0012;runout=xmin+P['thread_length_m_estimated']-.002;threadend=xmin+P['thread_length_m_estimated'];shoulderend=threadend+.002;headbase=xmax-P['head_thickness_m_estimated'];flangeR=P['collar_outer_diameter_m_estimated']/2;flangeface=headbase-P['collar_thickness_m_estimated'];flangeC=.00025
angles=set(math.tau*k/P['radial_uniform_sectors']for k in range(P['radial_uniform_sectors']))
# Add explicit samples near actual rounded-hex corner transitions, not a faceted six-vertex prism.
dcrit=math.atan((A-corner)*math.tan(math.pi/6)/A)
for k in range(6):
 center=k*math.pi/3+math.pi/6;span=math.pi/6-dcrit
 for i in range(P['additional_corner_angle_samples']+1):angles.add((center-span+2*span*i/P['additional_corner_angle_samples'])%math.tau)
angles=sorted(angles);angles=[a for i,a in enumerate(angles)if i==0 or a-angles[i-1]>1e-10];N=len(angles)
def ss(x,a,b):
 u=max(0.,min(1.,(x-a)/(b-a)));return u*u*(3-2*u),6*u*(1-u)/(b-a)if a<x<b else 0.
def sp(x,e=.015):
 return(0.,0.)if x<=-e else(x,1.)if x>=e else((x+e)**2/(4*e),(x+e)/(2*e))
def thread(x,t):
 u=(x-xmin)/pitch-t/math.tau;v=u-round(u);d=abs(v);p,dp=sp(d-.0625);q,dq=sp(d-.375);h=1-(p-q)/.3125;hd=-(dp-dq)/.3125*(1 if v>=0 else-1);w,wx=ss(x,xmin,fullstart);f,fx=ss(x,runout,threadend);base=major-depth+depth*f;profile=base+depth*(1-f)*h;rx=depth*fx*(1-h)+depth*(1-f)*hd/pitch;rt=-depth*(1-f)*hd/math.tau;r=(1-w)*.005+w*profile;return r,wx*(profile-.005)+w*rx,w*rt

def hexrad(t):
 delta=(t+math.pi/6)%(math.pi/3)-math.pi/6;flat=A/math.cos(delta)
 if abs(flat*math.sin(delta))<=(A-corner)*math.tan(math.pi/6):return flat
 ca=math.copysign(math.pi/6,delta);base=(A-corner)/math.cos(math.pi/6);proj=base*math.cos(delta-ca);ort=base*math.sin(delta-ca);return proj+math.sqrt(max(0.,corner*corner-ort*ort))
def hexder(t):return(hexrad(t+1e-6)-hexrad(t-1e-6))/2e-6
segments=[]
def linear(name,x0,x1,c0,c1,b0=0,b1=0,count=1):
 def f(u,t):
  b=b0+(b1-b0)*u;c=c0+(c1-c0)*u;return x0+(x1-x0)*u,c+b*hexrad(t),x1-x0,c1-c0+(b1-b0)*hexrad(t),b*hexder(t)
 segments.append((name,f,count))
def arc(name,xc,rc,radius,t0,t1,count=12,hexweight=0):
 def f(u,t):
  a=t0+(t1-t0)*u;da=t1-t0;return xc+radius*math.cos(a),rc+radius*math.sin(a)+hexweight*hexrad(t),-radius*math.sin(a)*da,radius*math.cos(a)*da,hexweight*hexder(t)
 segments.append((name,f,count))
# Adaptive exact planes: start, lead-in, runout and shoulder boundaries are explicit rows.
for x0,x1 in zip([xmin,tip,fullstart,runout,threadend],[tip,fullstart,runout,threadend,shoulderend]):
 if x0==threadend:
  def f(u,t,x0=x0,x1=x1):
   v,d=ss(u,0,1);return x0+(x1-x0)*u,major+(rs-major)*v,x1-x0,(rs-major)*d,0.
 else:
  def f(u,t,x0=x0,x1=x1):
   x=x0+(x1-x0)*u;r,rx,rt=thread(x,t);return x,r,x1-x0,rx*(x1-x0),rt
 segments.append(('thread/lead/shoulder',f,max(4,math.ceil((x1-x0)/pitch*P['axial_samples_per_thread_pitch']))))
rootC=.0004;rootX=flangeface-rootC
linear('smooth load-bearing shank',shoulderend,rootX,rs,rs,count=12)
arc('under-collar root',rootX,rs+rootC,rootC,-math.pi/2,0)
linear('collar underface',flangeface,flangeface,rs+rootC,flangeR-flangeC,count=5)
arc('collar underside edge',flangeface+flangeC,flangeR-flangeC,flangeC,math.pi,math.pi/2)
linear('collar outer band',flangeface+flangeC,headbase-flangeC,flangeR,flangeR,count=3)
arc('collar upper edge',headbase-flangeC,flangeR-flangeC,flangeC,math.pi/2,0)
linear('collar upper face',headbase,headbase,flangeR-flangeC,.00015,b1=1,count=6)
arc('head root return',headbase+.00015,.00015,.00015,math.pi,3*math.pi/2,hexweight=1)
linear('six rounded hex head faces',headbase+.00015,xmax-.0008,0,0,b0=1,b1=1,count=6)
linear('head top chamfer',xmax-.0008,xmax,0,A-.0006,b0=1,b1=0,count=12)
verts=[];faces=[];uvs=[];norms=[];regions=[];rings=[];suv=0.;tile=P['nominal_UV_tile_m_estimated'];U=round(math.tau*rs/tile)
def sample(f,u):return[f(u,t)for t in angles]
def normal(row,t):
 x,r,dx,dr,rt=row;n=np.array([-dr,dx*(math.cos(t)+rt/r*math.sin(t)),dx*(math.sin(t)-rt/r*math.cos(t))]);n/=np.linalg.norm(n);return tuple(n)
last=None;segment_rows=[]
for name,f,count in segments:
 points=[sample(f,k/count)for k in range(count+1)];ids=[]
 for j,row in enumerate(points):
  coords=[(x,r*math.cos(t),r*math.sin(t))for(x,r,*_),t in zip(row,angles)]
  if last is not None and j==0:
   assert max(math.dist(verts[i],v)for i,v in zip(last,coords))<1e-12,(name,'boundary mismatch');ids.append(last)
  else:
   ids.append(list(range(len(verts),len(verts)+N)));verts.extend(coords)
 for j in range(count):
  delta=sum(math.hypot(points[j+1][k][0]-points[j][k][0],points[j+1][k][1]-points[j][k][1])for k in range(N))/N;assert delta>0;s0=suv;suv+=delta/tile
  for k,t in enumerate(angles):
   kn=(k+1)%N;tn=angles[kn]if kn else math.tau;a,b,c,d=ids[j][k],ids[j+1][k],ids[j+1][kn],ids[j][kn];tex=[(t/math.tau*U,s0),(t/math.tau*U,suv),(tn/math.tau*U,suv),(tn/math.tau*U,s0)];ns=[normal(points[j][k],t),normal(points[j+1][k],t),normal(points[j+1][kn],tn),normal(points[j][kn],tn)]
   for ix in [(0,3,2),(0,2,1)]:faces.append(tuple([a,b,c,d][i]for i in ix));uvs.extend(tex[i]for i in ix);norms.extend(ns[i]for i in ix);regions.append(name)
 if not rings:rings.append(ids[0])
 last=ids[-1];segment_rows.append({'name':name,'axial_intervals':count})
rings.append(last)
for end,ring in enumerate(rings):
 x=xmin if end==0 else xmax;center=len(verts);verts.append((x,0,0));n=(-1,0,0)if end==0 else(1,0,0)
 for k in range(N):
  kn=(k+1)%N;f=(center,ring[kn],ring[k])if end==0 else(center,ring[k],ring[kn]);faces.append(f);norms.extend([n]*3);uvs.extend((verts[i][1]/tile,verts[i][2]/tile)for i in f);regions.append('flat threaded tip'if end==0 else'flat head face')
m=bpy.data.meshes.new('Original shared-ring head/collar/shank/helix');m.from_pydata(verts,[],faces);m.update();assert not m.validate(clean_customdata=False);m.polygons.foreach_set('use_smooth',np.ones(len(faces),bool));u=m.uv_layers.new(name='Original 5mm working tile, varying-radius head scale');u.data.foreach_set('uv',np.array(uvs,np.float32).ravel());m.normals_split_custom_set(norms);m.update();m.calc_loop_triangles();areas=np.array([t.area for t in m.loop_triangles]);bm=bmesh.new();bm.from_mesh(m);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert not nonmanifold and volume>0 and areas.min()>1e-18;o=bpy.data.objects.new('Pivot shaft head collar and reduced helix candidate',m);col.objects.link(o);o['component_id']=P['component_id'];o['vendor_260_14_12_related_only']=True;o['collar_separate_or_integrated_unknown']=True;o['thread_form_pitch_handedness_estimated']=True
mat=bpy.data.materials.new('Neutral gray geometry not final metal');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.20,.21,.23,1);p.inputs['Roughness'].default_value=.30;m.materials.append(mat)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.max_bounces=8;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.8;s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.20,.23,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
for name,loc,power,size in [('KEY',(.1,-.16,.20),3.,.15),('FILL',(-.12,-.05,.10),1.2,.12),('EDGE',(.04,.14,.12),2.,.12),('LOWER',(.04,.07,-.13),.6,.12)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(name,l);studio.objects.link(o);o.location=loc;o.rotation_euler=(-Vector(loc)).to_track_quat('-Z','Y').to_euler()
c=bpy.data.cameras.new('Pivot shaft isolated camera');cam=bpy.data.objects.new('CAMERA',c);studio.objects.link(cam);s.camera=cam;cam.location=(.16,-.34,.20);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=.34;c.clip_start=.001;c.clip_end=5
bpy.ops.object.select_all(action='DESELECT');obj=col.objects[0];obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.export_scene.gltf(filepath=str(H/'swingarm-pivot-shaft-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True);bpy.ops.wm.save_as_mainfile(filepath=str(H/'swingarm-pivot-shaft-v1.blend'),compress=True)
r={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(H/'swingarm-pivot-shaft-v1.blend'),'export_sha256':sha(H/'swingarm-pivot-shaft-inspection.glb'),'object':obj.name,'vertices':len(verts),'triangles':len(faces),'nonmanifold_edges':nonmanifold,'signed_volume_m3':volume,'minimum_triangle_area_m2':float(areas.min()),'actual_bounds_m':[list(obj.bound_box[0]),list(obj.bound_box[6])],'connected_solids':1,'actual_radial_samples':N,'segments':segment_rows,'working_thread_pitch_m_estimated':pitch,'vendor_related_260_14_12_only':True,'original_thread_not_certified_ISO':True,'collar_integrated_interpretation_provisional':True,'source_N_analytical_surface_derivatives':True,'external_libraries':[],'art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(H/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('PIVOT_SHAFT_SOURCE',json.dumps(r))
