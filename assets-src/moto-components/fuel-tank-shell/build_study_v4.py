"""Bounded externally visible frontreturn hypothesis, no claimed tunnel or mechanism."""
import bpy,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/fuel-tank-shell-study-v4';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base=H/'fuel-tank-shell-study-v3.blend';b=json.loads((R/'creative/reviews/fuel-tank-shell-study-v3/build-report.json').read_text());assert sha(base)==b['source_sha256'];P=json.loads((H/'parameters-study-v1.json').read_text());U=P['longitudinal_stations'];C=P['cross_profile'];ns={'Vector':Vector,'U':U,'C':C};tree=ast.parse((H/'build_study_v1.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['slopes','interp','surface','normal']],type_ignores=[]),'<frozen-original-parametric-skin>','exec'),ns);surface=ns['surface'];normal=ns['normal'];bpy.ops.wm.open_mainfile(filepath=str(base));obj=bpy.data.objects[b['object']];old=obj.data;verts=[v.co.copy()for v in old.vertices];lookup={tuple(v):i for i,v in enumerate(verts)};nv=P['grid']['cross'];thick=P['skin_thickness_m'];faces=[];uvs=[];norms=[];regs=[]
outer=[];inner=[]
for j in range(nv+1):
 v=-1+2*j/nv;p=surface(0,v);outer.append(lookup[tuple(p)]);inner.append(lookup[tuple(p-thick*normal(0,v))])
remove=set()
for j in range(nv):
 a,bb,c,d=outer[j],outer[j+1],inner[j],inner[j+1];remove.add(frozenset((a,d,bb)));remove.add(frozenset((a,c,d)))
removed=0
for p in old.polygons:
 if frozenset(p.vertices)in remove:removed+=1;continue
 faces.append(tuple(p.vertices));uvs.append([tuple(old.uv_layers[0].data[l].uv)for l in p.loop_indices]);norms.append([tuple(old.corner_normals[l].vector)for l in p.loop_indices]);regs.append(old.attributes['SKIN_REGION'].data[p.index].value)
assert removed==len(remove);retained=len(faces)
def add(p):verts.append(Vector(p));return len(verts)-1
def f(ids,no,region):
 faces.append(tuple(ids));uvs.append([(.5+verts[i].x/.06,(verts[i].z+.35)/.13)for i in ids]);norms.append(no);regs.append(region)
# Seen from front(-Y): CCW X/Z contour. Only short bottomedge added, not a tank pan.
outer=list(reversed(outer));inner=list(reversed(inner));ends=[]
for isinner,row in [(False,outer),(True,inner)]:
 a=verts[row[-1]];bb=verts[row[0]];new=list(row)
 for q in range(1,17):new.append(add(a.lerp(bb,q/17)))
 ends.append(new)
K=len(ends[0]);nr=24;boundrings=[]
def spline_value_derivative(xs,ys,x):
 ss=ns['slopes'](xs,ys);i=next((k for k in range(len(xs)-1)if x<=xs[k+1]),len(xs)-2);h=xs[i+1]-xs[i];f=(x-xs[i])/h
 val=(2*f**3-3*f*f+1)*ys[i]+(f**3-2*f*f+f)*h*ss[i]+(-2*f**3+3*f*f)*ys[i+1]+(f**3-f*f)*h*ss[i+1]
 der=((6*f*f-6*f)*ys[i]+(3*f*f-4*f+1)*h*ss[i]+(-6*f*f+6*f)*ys[i+1]+(3*f*f-2*f)*h*ss[i+1])/h
 return val,der
for isinner,bound in [(False,ends[0]),(True,ends[1])]:
 # Both layer profiles are the original sourceboundary, independent of surfacefill.
 # Half U runs from topcentre to rightlower corner in the reversed contour.
 half=[verts[bound[k]]for k in range(nv//2,-1,-1)];half.sort(key=lambda p:p.z);zs=[p.z for p in half];ws=[p.x for p in half];bys=[p.y for p in half];z0,z1=zs[0],zs[-1];depth=.021
 def graph(x,z):
  by,byd=spline_value_derivative(zs,bys,z);w,wd=spline_value_derivative(zs,ws,z);t=(z-z0)/(z1-z0);st=math.sin(math.pi*t)**2;std=math.pi*math.sin(2*math.pi*t)/(z1-z0)
  if abs(w)<1e-9:return by,0,byd
  g=1-x*x/(w*w);y=by-depth*st*g;dx=2*depth*st*x/(w*w);dz=byd-depth*(std*g+st*2*x*x*wd/(w**3));return y,dx,dz
 centre=Vector((0,graph(0,-.287)[0],-.287));ci=add(centre);rings=[];no={}
 for ri in range(1,nr+1):
  r=ri/nr;row=[]
  for idx in bound:
   p=verts[idx];x=centre.x+(p.x-centre.x)*r;z=centre.z+(p.z-centre.z)*r;y,dx,dz=graph(x,z);row.append(idx if ri==nr else add((x,y,z)))
  rings.append(row)
 for ri,row in enumerate(rings):
  for k,idx in enumerate(row):
   p=verts[idx];y,dx,dz=graph(p.x,p.z);n=Vector((dx,-1,dz)).normalized();no[ri,k]=tuple(-n if isinner else n)
 cy,cx,cz=graph(centre.x,centre.z);centralnormal=Vector((cx,-1,cz)).normalized();centralnormal=-centralnormal if isinner else centralnormal
 def captri(ids,ns0):
  if isinner:ids=list(reversed(ids));ns0=list(reversed(ns0))
  f(ids,ns0,5)
 for k in range(K):
  h=(k+1)%K;captri([ci,rings[0][k],rings[0][h]],[tuple(centralnormal),no[0,k],no[0,h]])
 for ri in range(nr-1):
  a=rings[ri];bb=rings[ri+1]
  for k in range(K):
   h=(k+1)%K;captri([a[k],bb[k],bb[h]],[no[ri,k],no[ri+1,k],no[ri+1,h]]);captri([a[k],bb[h],a[h]],[no[ri,k],no[ri+1,h],no[ri,h]])
 boundrings.append(bound)
# Only added bottom segment is a new finite skin boundary, never closed underneath.
a,bb=boundrings
for k in range(nv,K):
 h=(k+1)%K
 for ids in [(a[k],bb[k],bb[h]),(a[k],bb[h],a[h])]:
  n=(verts[ids[1]]-verts[ids[0]]).cross(verts[ids[2]]-verts[ids[0]]).normalized();faces.append(ids);uvs.append([(k/K,0),(k/K,1),((k+1)/K,1)]if ids[1]==bb[k]else[(k/K,0),((k+1)/K,1),((k+1)/K,0)]);norms.append([tuple(n)]*3);regs.append(2)
used=sorted({i for face in faces for i in face});mp={v:k for k,v in enumerate(used)};coords=[verts[i]for i in used];faces=[tuple(mp[i]for i in f0)for f0 in faces];mesh=bpy.data.meshes.new('Upper skin and observed frontreturn estimatedsurface');mesh.from_pydata(coords,[],faces);mesh.update()
for mat in old.materials:mesh.materials.append(mat)
uv=mesh.uv_layers.new(name='Original skin and separate frontreturn charts');ln=[]
for p in mesh.polygons:
 p.use_smooth=regs[p.index]!=2
 for k,l in enumerate(p.loop_indices):uv.data[l].uv=uvs[p.index][k];ln.append(norms[p.index][k])
mesh.normals_split_custom_set(ln);reg=mesh.attributes.new('SKIN_REGION','INT','FACE')
for i,x in enumerate(regs):reg.data[i].value=x
obj.data=mesh;obj.name='Tank upper skin with observed frontreturn hypothesis';obj['front_return']='Opaque exteriorsurface hypothesis only. Realopening/blindcavity/reflection not distinguished; no tunnel or mechanism.';bpy.data.meshes.remove(old);source=H/'fuel-tank-shell-study-v4.blend';export=H/'fuel-tank-shell-study-v4.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
from collections import Counter
edges=Counter(tuple(sorted((a,b)))for f0 in faces for a,b in zip(f0,f0[1:]+f0[:1]));areas=[p.area for p in mesh.polygons];volume=sum(coords[a].dot(coords[b].cross(coords[c]))/6 for a,b,c in faces);report={'source_sha256':sha(source),'export_sha256':sha(export),'base_source_sha256':b['source_sha256'],'builder_sha256':sha(Path(__file__)),'object':obj.name,'triangles':len(faces),'vertices':len(coords),'retained_source3_triangles':retained,'removed_provisional_front_cut_triangles':removed,'non_two_face_edges':sum(v!=2 for v in edges.values()),'minimum_triangle_area_m2':min(areas),'exact_zero_area_triangles':sum(a==0 for a in areas),'wall_volume_m3':volume,'front_return':'Observed silhouette+face only, opaque candidate, realopening unresolved','no_pan_tunnel_capacity_or_mount_added':True,'art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');assert not report['non_two_face_edges']and min(areas)>0 and volume>0;print('TANK4',json.dumps(report))
