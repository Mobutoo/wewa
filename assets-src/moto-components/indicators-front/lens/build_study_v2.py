"""Add one visible local attachment-region hypothesis; leave hidden termination open."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/indicator-front-lens-study-v2';O.mkdir(parents=True,exist_ok=True);P=json.loads((H/'parameters-study-v2.json').read_text());Q=P['pocket'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();baseline=H/'indicator-front-lens-study-v1.blend';assert sha(baseline)=='8afaee2eb0e79778e50be60f7aada0bd02bf0adf07eeab25e7f4a538e776f521';assert(R/'creative/research/indicator-front-lens/attachment-region-plan-v2.json').exists();bpy.ops.wm.open_mainfile(filepath=str(baseline));old=bpy.data.objects['Related lens gross exterior skin - estimated incomplete'];M=old.data;N=P['angular_segments'];NC=P['cap_radial_rings'];caplast=1+NC*N;capfaces=(2*NC-1)*N;sphere=(P['face_radius_m']**2+P['face_sag_m']**2)/(2*P['face_sag_m']);cx,cz=Q['center_xz_m'];lo=Q['mouth_radius_m'];hi=Q['outer_transition_radius_m'];points=[];keys={};original={}
def add(x,z,orig=None):
 key=(float(x),float(z))
 if key in keys:return keys[key]
 i=len(points);points.append(Vector(key));keys[key]=i
 if orig is not None:original[i]=orig
 return i
# Keep original cap sample positions wherever they are outside the proposed mouth.
for v in list(M.vertices)[:caplast]:
 x,y,z=v.co
 if math.hypot(x-cx,z-cz)>lo+1e-10:add(x,z,v.index)
outer=[add(*[M.vertices[1+(NC-1)*N+k].co[a]for a in [0,2]],orig=1+(NC-1)*N+k)for k in range(N)]
edges=[(outer[k],outer[(k+1)%N])for k in range(N)];rings=[]
for i in range(Q['transition_rings']+1):
 rr=lo+(hi-lo)*i/Q['transition_rings'];ring=[]
 for k in range(Q['angular_segments']):a=2*math.pi*k/Q['angular_segments'];ring.append(add(cx+rr*math.cos(a),cz+rr*math.sin(a)))
 rings.append(ring);edges.extend((ring[k],ring[(k+1)%len(ring)])for k in range(len(ring)))
verts2,edges2,faces2,origv,orige,origf=delaunay_2d_cdt(points,edges,[outer],1,1e-10)
def smooth(t):return t*t*t*(10+t*(-15+6*t))
def ds(t):return 30*t*t*(t-1)*(t-1)
def field(x,z):
 root=math.sqrt(sphere*sphere-x*x-z*z);y=(sphere-P['face_sag_m'])-root;gx=x/root;gz=z/root;d=math.hypot(x-cx,z-cz)
 if d<hi:
  t=max(0,min(1,(d-lo)/(hi-lo)));y+=Q['depression_m']*(1-smooth(t));slope=-Q['depression_m']*ds(t)/(hi-lo)
  if d>1e-12:gx+=slope*(x-cx)/d;gz+=slope*(z-cz)/d
 return y,Vector((gx,-1,gz)).normalized()
V=[];VN=[];UV=[];distmax=0;oldprof=json.loads((R/'creative/reviews/indicator-front-lens-study-v1/build-report.json').read_text())['profile'];last=(0,-P['face_sag_m'])
for rr,yy,_,_ in oldprof:distmax+=math.hypot(rr-last[0],yy-last[1]);last=(rr,yy)
for v in verts2:
 x,z=v;y,n=field(x,z);V.append((x,y,z));VN.append(tuple(n));r=math.hypot(x,z);w=.49*sphere*math.asin(r/sphere)/distmax;UV.append((.5+w*x/r,.5+w*z/r)if r else(.5,.5))
F=[];norm=[];uvs=[]
for f in faces2:
 assert len(f)==3
 x=sum(verts2[k].x for k in f)/3;z=sum(verts2[k].y for k in f)/3
 if math.hypot(x-cx,z-cz)<lo:continue
 a,b,c=f;cross=(Vector(V[b])-Vector(V[a])).cross(Vector(V[c])-Vector(V[a]));f=tuple(f)if cross.y<0 else tuple(reversed(f));F.append(f);norm.append([VN[k]for k in f]);uvs.append([UV[k]for k in f])
# Preserve evaluated old rim positions and per-corner normals/UV without recomputing it.
index_by_xz={(float(v.x),float(v.y)):i for i,v in enumerate(verts2)};old_to_new={}
for k in range(N):
 oi=1+(NC-1)*N+k;co=M.vertices[oi].co;ni=index_by_xz[(float(co.x),float(co.z))];old_to_new[oi]=ni;V[ni]=tuple(co)
for v in list(M.vertices)[caplast:]:old_to_new[v.index]=len(V);V.append(tuple(v.co))
for f in list(M.polygons)[capfaces:]:
 F.append(tuple(old_to_new[i]for i in f.vertices));norm.append([tuple(M.corner_normals[li].vector)for li in f.loop_indices]);uvs.append([tuple(M.uv_layers.active.data[li].uv)for li in f.loop_indices])
rim_triangles=len(M.polygons)-capfaces
# Short wall at the observed mouth, explicit open end, not a claimed full passage.
hole=[]
for k in range(Q['angular_segments']):
 a=2*math.pi*k/Q['angular_segments'];x=cx+lo*math.cos(a);z=cz+lo*math.sin(a);candidate=min(range(len(verts2)),key=lambda i:(verts2[i].x-x)**2+(verts2[i].y-z)**2);assert (verts2[candidate]-Vector((x,z))).length<1e-7;hole.append(candidate)
for j in range(Q['wall_rings']):
 ring0=hole if j==0 else ring1;ring1=[]
 for k in range(Q['angular_segments']):
  x,y,z=V[hole[k]];ring1.append(len(V));V.append((x,y+Q['visible_wall_depth_m']*(j+1)/Q['wall_rings'],z))
 for k in range(len(hole)):
  nk=(k+1)%len(hole);fs=[(ring0[k],ring1[k],ring1[nk]),(ring0[k],ring1[nk],ring0[nk])]
  for f in fs:
   # Wall exterior into mouth: inward radial normals, hard separation at lip.
   ns=[];us=[]
   for vid in f:
    x,y,z=V[vid];a=math.atan2(z-cz,x-cx);ns.append((-math.cos(a),0,-math.sin(a)));u=k/len(hole)if vid in[ring0[k],ring1[k]]else(k+1)/len(hole);level=j/Q['wall_rings']if vid in ring0 else(j+1)/Q['wall_rings'];us.append((u,level))
   cross=(Vector(V[f[1]])-Vector(V[f[0]])).cross(Vector(V[f[2]])-Vector(V[f[0]]));avg=sum((Vector(n)for n in ns),Vector())
   if cross.dot(avg)<0:f=tuple(reversed(f));ns.reverse();us.reverse()
   F.append(f);norm.append(ns);uvs.append(us)
oldmesh=old.data;mesh=bpy.data.meshes.new('Exterior cap with one estimated attachment mouth');mesh.from_pydata(V,[],F);mesh.update();uv=mesh.uv_layers.new(name='Original lens patch and mouth UV');custom=[]
for p in mesh.polygons:
 p.use_smooth=True
 for k,li in enumerate(p.loop_indices):uv.data[li].uv=uvs[p.index][k];custom.append(norm[p.index][k])
mesh.normals_split_custom_set(custom)
for m in oldmesh.materials:mesh.materials.append(m)
old.data=mesh;old.name='Related lens exterior with local attachment mouth - estimated incomplete';old['scope']='One estimated local attachment mouth/depression; short exposed wall ends open, no hidden socket or through-hole asserted';src=H/'indicator-front-lens-study-v2.blend';glb=H/'indicator-front-lens-study-v2.glb';bpy.ops.object.select_all(action='DESELECT');old.select_set(True);root=old.parent;root.select_set(True);bpy.context.view_layer.objects.active=old;bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
count=Counter(tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1]));boundary=sum(n==1 for n in count.values());assert boundary==N+Q['angular_segments'] and all(n in[1,2]for n in count.values());report={'schema':1,'source_sha256':sha(src),'export_sha256':sha(glb),'builder_sha256':sha(Path(__file__)),'parameters_sha256':sha(H/'parameters-study-v2.json'),'baseline_source_sha256':sha(baseline),'object':old.name,'objects':[old.name],'collection':'WEWA_FRONT_INDICATOR_LENS_STUDY','root':root.name,'vertices':len(V),'triangles':len(F),'preserved_rim_triangles':rim_triangles,'rim_preservation':'Actual source positions and per-corner normals/UV copied. Cap retriangulated on original analytic sphere outside the local pocket; no all-cap bit identity claim.','minimum_source_triangle_area_m2':min(p.area for p in mesh.polygons),'intentional_boundary_edges':boundary,'boundary_scope':'Rear exterior interface plus mouth-wall study open termination, not a certified through hole','external_libraries':[],'external_images':[],'installation_transform':None,'complete_lens':False,'art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('LENS_LOCAL_ATTACHMENT_BUILT',report['source_sha256'],report['export_sha256'],len(F))
