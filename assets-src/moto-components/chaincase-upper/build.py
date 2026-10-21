"""Original open formed-sheet upper-case candidate. Native CDT+shared returns.
No imported geometry, hidden backplate or GLB buffer repair; all metrics estimated.
"""
import bpy,bmesh,json,math,hashlib,sys,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/chaincase-upper-v1';sys.path.insert(0,str(H));from formed_profile import outline,inside,distance_to_path,rib_path,face_points_and_normals
P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();poly=outline(P);holes=[];hr=P['mount_hole_diameter_m_estimated']/2
for center in P['mount_holes_candidate_YZ_m']:
 a=np.linspace(0,math.tau,160,endpoint=False);holes.append(np.array(center)+hr*np.column_stack([np.cos(a),np.sin(a)]))
loops=[poly]+holes;points=[];edges=[]
for loop in loops:
 start=len(points);points.extend(loop.tolist());edges.extend((start+i,start+(i+1)%len(loop))for i in range(len(loop)))
print('CONSTRAINTS',len(points),flush=True)
# Distributed wall topology before forming. Finer grid only in observed detail envelopes.
for pitch,detail in [(.0015,False),(.00060,True)]:
 yy,zz=np.meshgrid(np.arange(poly[:,0].min()+pitch*.37,poly[:,0].max(),pitch),np.arange(poly[:,1].min()+pitch*.41,poly[:,1].max(),pitch));p=np.column_stack([yy.ravel(),zz.ravel()]);keep=inside(p,poly)
 for hole in holes:keep&=~inside(p,hole)
 p=p[keep];p=p[distance_to_path(p,poly,True)>.00022]
 for c in P['mount_holes_candidate_YZ_m']:p=p[np.linalg.norm(p-np.array(c),axis=1)>hr+.00015]
 if detail:
  keep=distance_to_path(p,rib_path())<.0055
  for c in P['mount_holes_candidate_YZ_m']:keep|=np.linalg.norm(p-np.array(c),axis=1)<.014
  keep|=np.linalg.norm(p-np.array([-.065,.060]),axis=1)<.009;p=p[keep]
 points.extend(p.tolist())
# Exact shared constraints: interior duplicates are eliminated before invoking CDT.
print('GRID_INPUT',len(points),flush=True)
unique=[];seen=set()
for p in points:
 key=tuple(round(float(x),9)for x in p)
 if key not in seen:seen.add(key);unique.append(Vector(p))
# Constraints were inserted first and contain no duplicates; IDs remain valid.
assert len(seen)>=sum(map(len,loops));coords,_,cap,*_=delaunay_2d_cdt(unique,edges,[list(range(len(poly)))],1,1e-8,False);xy=np.array([p[:]for p in coords],float);faces=[]
cap=np.asarray(cap,dtype=np.int64);assert cap.ndim==2 and cap.shape[1]==3
centres=xy[cap].mean(axis=1);keep=inside(centres,poly)
for hole in holes:keep&=~inside(centres,hole)
cap=cap[keep];tri=xy[cap];delta1=tri[:,1]-tri[:,0];delta2=tri[:,2]-tri[:,0];areasigned=delta1[:,0]*delta2[:,1]-delta1[:,1]*delta2[:,0];assert np.all(areasigned!=0);cap[areasigned<0]=cap[areasigned<0,::-1];faces=[tuple(map(int,f))for f in cap];area2d=float(np.abs(areasigned).sum()/2);signed=lambda p:.5*np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1]);expected=abs(signed(poly))-sum(abs(signed(h))for h in holes);assert abs(area2d-expected)<1e-8,(area2d,expected)
print('CDT_DOMAIN',len(xy),len(faces),area2d,flush=True)
used=sorted({i for f in faces for i in f});remap={old:new for new,old in enumerate(used)};xy=xy[used];faces=[tuple(remap[i]for i in f)for f in faces];v,n=face_points_and_normals(xy,P,poly);v=v.tolist();n=n.tolist();mfaces=faces.copy();muv=[tuple(xy[i]/.010)for f in faces for i in f];labels=['formed wall']*len(faces);lookup={tuple(np.round(a,8)):i for i,a in enumerate(xy)}
def find(p):
 key=tuple(np.round(p,8))
 if key in lookup:return lookup[key]
 distances=np.linalg.norm(xy-p,axis=1);j=int(distances.argmin());assert distances[j]<2e-8,(p,distances[j]);return j
outer=[find(p)for p in poly];boundary_rows=[];dist=0.;along=[0.]
for a,b in zip(poly,np.roll(poly,-1,axis=0)):dist+=math.dist(a,b);along.append(dist/.010)
# Smooth contour normals computed from actual sampled curve tangents, in its YZ plane.
tan=np.roll(poly,-1,axis=0)-np.roll(poly,1,axis=0);out=np.column_stack([tan[:,1],-tan[:,0]]);out/=np.linalg.norm(out,axis=1,keepdims=True);r=.003;last=outer;previous_profile=0.;returnrows=[]
# Main topside deep return, matinglowerseam/arch shallower as explicit estimates.
for a in np.linspace(0,math.pi/2,13)[1:]:returnrows.append(('formed bend',-r*(1-math.cos(a)),r*math.sin(a),math.cos(a),math.sin(a),r*a/.010))
depth=[]
for y,z in poly:
 if abs(math.hypot(y,z)-P['rear_opening_radius_m_estimated'])<.0005:dep=.020
 elif z<.010:dep=.012
 elif y<-.47:dep=.018
 else:dep=P['return_depth_m_estimated']
 depth.append(dep)
# Smooth provisional depth across adjacent changes, no hidden tabs/tubes invented.
depth=np.asarray(depth)
for _ in range(8):depth=(np.roll(depth,-1)+2*depth+np.roll(depth,1))/4
for u in np.linspace(0,1,9)[1:]:returnrows.append(('return band',None,r,0,1,None,u))
for row in returnrows:
 name,xoff,offset,nx,nr,profile=row[:6];ids=[];pu=[]
 for i,p in enumerate(poly):
  if name=='return band':u=row[6];xoff=-r-u*(depth[i]-r);profile=(r*math.pi/2+u*(depth[i]-r))/.010
  pos=(xoff,p[0]+offset*out[i,0],p[1]+offset*out[i,1]);ids.append(len(v));v.append(pos);n.append((nx,nr*out[i,0],nr*out[i,1]));pu.append(profile)
 for i in range(len(poly)):
  j=(i+1)%len(poly);a,b,c,d=last[i],last[j],ids[j],ids[i];u0,u1=along[i],along[i+1];oldv=previous_profile if isinstance(previous_profile,float)else previous_profile[i];oldvn=previous_profile if isinstance(previous_profile,float)else previous_profile[j];q=[(u0,oldv),(u1,oldvn),(u1,pu[j]),(u0,pu[i])]
  for ind in [(0,3,2),(0,2,1)]:mfaces.append(tuple([a,b,c,d][k]for k in ind));muv.extend(q[k]for k in ind);labels.append(name)
 last=ids;previous_profile=pu
boundary_rows.append(last)
# Two actual thin skins around one shared midsurface; endfaces connect, no closed hollow back.
v=np.asarray(v,float);n=np.asarray(n,float);n/=np.linalg.norm(n,axis=1,keepdims=True);th=P['sheet_thickness_m_estimated'];N=len(v);verts=np.vstack([v+th/2*n,v-th/2*n]);solidfaces=list(mfaces)+[tuple(i+N for i in reversed(f))for f in mfaces];uvs=list(muv)
for k,f in enumerate(mfaces):uvs.extend(list(reversed(muv[3*k:3*k+3])))
# Open midsurface boundary contains the last return ring and the3 drilled passages.
counts=Counter(tuple(sorted((f[i],f[(i+1)%3])))for f in mfaces for i in range(3));open_edges=[(f[i],f[(i+1)%3])for f in mfaces for i in range(3)if counts[tuple(sorted((f[i],f[(i+1)%3])))]==1]
for a,b in open_edges:
 base=len(solidfaces);q=(b,a,a+N,b+N);length=np.linalg.norm(v[b]-v[a]);tex=[(0,0),(length/.010,0),(length/.010,th/.010),(0,th/.010)]
 for ind in [(0,1,2),(0,2,3)]:solidfaces.append(tuple(q[k]for k in ind));uvs.extend(tex[k]for k in ind)
# Correct winding/volume is measured, not inferred from the source surface names.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;col=bpy.data.collections.new(P['collection']);s.collection.children.link(col);studio=bpy.data.collections.new('LOCAL_NEUTRAL_STUDIO_NOT_EXPORT');s.collection.children.link(studio);mesh=bpy.data.meshes.new('Native finite sheet distributed wall bends and three passages');mesh.from_pydata(verts.tolist(),[],solidfaces);mesh.update();assert not mesh.validate(clean_customdata=False);mesh.polygons.foreach_set('use_smooth',np.ones(len(solidfaces),bool));layer=mesh.uv_layers.new(name='Original 10mm working tiles with separate bend/openedge charts');layer.data.foreach_set('uv',np.asarray(uvs,np.float32).ravel());norm=[]
for f in mfaces:norm.extend(n[i]for i in f)
for f in mfaces:norm.extend(-n[i]for i in reversed(f))
for f in solidfaces[2*len(mfaces):]:
 a,b,c=verts[list(f)];fn=np.cross(b-a,c-a);fn/=np.linalg.norm(fn);norm.extend([fn]*3)
mesh.normals_split_custom_set(norm);mesh.update();mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh);nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);chi=len(bm.verts)-len(bm.edges)+len(bm.faces);bm.free();assert nm==0 and vol>0 and chi==-4,(nm,vol,chi);areas=[a.area for a in mesh.loop_triangles];assert min(areas)>1e-18;o=bpy.data.objects.new('Upper formed chaincase shell related PF181202 candidate',mesh);col.objects.link(o);o['component_id']=P['component_id'];o['all_metric_parameters_estimated']=True;o['halfcode_attribution_conditional']=True;o['no_hidden_backplate']=True;mat=bpy.data.materials.new('Neutral gray geometry only, not final silverpaint');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.20,.21,.23,1);p.inputs['Roughness'].default_value=.30;mesh.materials.append(mat)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.max_bounces=8;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.8;s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.20,.23,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
for name,loc,power,size in [('KEY',(.45,-.30,.45),16.,.40),('FILL',(-.35,-.4,.10),9.,.30),('EDGE',(.15,.25,.30),11.,.35),('LOWER',(.3,-.05,-.30),5.,.30)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;lo=bpy.data.objects.new(name,l);studio.objects.link(lo);lo.location=loc;lo.rotation_euler=(Vector((0,-.20,.04))-lo.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.cameras.new('Chaincase upper isolated camera');cam=bpy.data.objects.new('CAMERA',c);studio.objects.link(cam);s.camera=cam;cam.location=(.65,-.6,.4);cam.rotation_euler=(Vector((0,-.20,.04))-cam.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=.75;c.clip_start=.001;c.clip_end=10;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.gltf(filepath=str(H/'chaincase-upper-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True);bpy.ops.wm.save_as_mainfile(filepath=str(H/'chaincase-upper-v1.blend'),compress=True);report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(H/'chaincase-upper-v1.blend'),'export_sha256':sha(H/'chaincase-upper-inspection.glb'),'vertices':len(verts),'triangles':len(solidfaces),'nonmanifold_edges':nm,'euler_characteristic':chi,'signed_volume_m3':vol,'minimum_triangle_area_m2':min(areas),'source_CDT_domain_area_m2':area2d,'expected_domain_area_m2':expected,'genuine_throughholes':3,'closed_relief_not_drilled':True,'no_hidden_backplate':True,'whole_installed_fit_verified':False,'all_metric_parameters_estimated':True,'halfcode_attribution_conditional':True,'current_RDC_identity_verified':False,'art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(H/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('CHAINCASE_UPPER_SOURCE',json.dumps(report))
