"""Add an observed open mouth to original skin, with explicitly estimated neck section."""
import bpy,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/fuel-tank-shell-study-v2';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base=H/'fuel-tank-shell-study-v1.blend';b=json.loads((R/'creative/reviews/fuel-tank-shell-study-v1/build-report.json').read_text());assert sha(base)==b['source_sha256'];P=json.loads((H/'parameters-study-v1.json').read_text());U=P['longitudinal_stations'];C=P['cross_profile'];ns={'Vector':Vector,'U':U,'C':C}
# Load only pure parametric functions from frozen original builder; never execute its writes.
tree=ast.parse((H/'build_study_v1.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['slopes','interp','surface','normal']];exec(compile(ast.Module(body=defs,type_ignores=[]),'<frozen-v1-surface-functions>','exec'),ns);surface=ns['surface'];normal=ns['normal'];bpy.ops.wm.open_mainfile(filepath=str(base));obj=bpy.data.objects[b['object']];old=obj.data;nu=P['grid']['longitudinal'];nv=P['grid']['cross'];n=(nu+1)*(nv+1);thick=P['skin_thickness_m'];verts=[v.co.copy()for v in old.vertices];faces=[];uvs=[];norms=[];regions=[];i0,i1,j0,j1=72,108,82,110;center=(0,.112);cut=.035
# Keep every original triangle outside the single patch, including the existing cut-thickness perimeter.
for p in old.polygons:
 skip=False
 if p.index<nu*nv*4:
  cell=p.index//4;i=cell//nv;j=cell%nv;skip=i0<=i<i1 and j0<=j<j1
 if skip:continue
 faces.append(tuple(p.vertices));uvs.append([tuple(old.uv_layers[0].data[l].uv)for l in p.loop_indices]);norms.append([tuple(old.corner_normals[l].vector)for l in p.loop_indices]);regions.append(int(old.attributes['SKIN_REGION'].data[p.index].value))
retained=len(faces)
def addv(p):verts.append(Vector(p));return len(verts)-1
def face(ids,uv,region,nn=None):
 faces.append(tuple(ids));uvs.append(uv);regions.append(region)
 if nn is None:
  no=(verts[ids[1]]-verts[ids[0]]).cross(verts[ids[2]]-verts[ids[0]]).normalized();nn=[tuple(no)]*3
 norms.append(nn)
def bodyuv(x,y):
 u=.51;v=x/.24
 for it in range(15):
  p=surface(u,v);err=Vector((p.x-x,p.y-y));e=1e-5;du=(surface(u+e,v)-surface(u-e,v))/(2*e);dv=(surface(u,v+e)-surface(u,v-e))/(2*e);det=du.x*dv.y-dv.x*du.y
  u-=(dv.y*err.x-dv.x*err.y)/det;v-=(-du.y*err.x+du.x*err.y)/det
  if err.length<1e-10:break
 assert 0<u<1 and -1<v<1 and err.length<1e-7
 return u,v
perim=[i0*(nv+1)+j for j in range(j0,j1+1)]+[i*(nv+1)+j1 for i in range(i0+1,i1+1)]+[i1*(nv+1)+j for j in range(j1-1,j0-1,-1)]+[i*(nv+1)+j0 for i in range(i1-1,i0,-1)]
phis=[math.atan2(verts[k].y-center[1],verts[k].x)for k in perim];holes=[bodyuv(cut*math.cos(p),center[1]+cut*math.sin(p))for p in phis];origuv=[(k//(nv+1)/nu,-1+2*(k%(nv+1))/nv)for k in perim];K=len(perim);annuli=[]
for inner in [False,True]:
 rows=[([k+n if inner else k for k in perim],origuv)]
 for ring in range(1,9):
  t=ring/8;coords=[(a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t)for a,b in zip(origuv,holes)];ids=[]
  for u,v in coords:ids.append(addv(surface(u,v)-thick*normal(u,v)if inner else surface(u,v)))
  rows.append((ids,coords))
 for ri in range(8):
  a,au=rows[ri];d,du=rows[ri+1]
  for k in range(K):
   h=(k+1)%K;aa=[a[k],a[h],d[h]];bb=[a[k],d[h],d[k]];uvA=[au[k],au[h],du[h]];uvB=[au[k],du[h],du[k]]
   for ids,uv in [(aa,uvA),(bb,uvB)]:
    nn=[tuple(-normal(u,v)if inner else normal(u,v))for u,v in uv]
    if inner:ids=list(reversed(ids));uv=list(reversed(uv));nn=list(reversed(nn))
    face(ids,[(u,(v+1)/2)for u,v in uv],1 if inner else 0,nn)
 annuli.append(rows[-1][0])
# Rounded section polyline. Values are a short visible neck candidate, not a measured hidden mechanism.
poly=[(.035,0),(.0345,.0005),(.034,.0015),(.033,.0025),(.0315,.003),(.0293,.003),(.0285,.0023),(.028,.0015),(.028,-.012),(.0283,-.013),(.029,-.013),(.0291,-.012),(.0291,-.002),(.0298,-.0012),(.034,-.001)]
prof=[Vector(poly[0])]
for q in range(1,len(poly)-1):
 a,bp,c=map(Vector,[poly[q-1],poly[q],poly[q+1]]);d=min(.00022,.20*(bp-a).length,.20*(c-bp).length);lo=bp+(a-bp).normalized()*d;hi=bp+(c-bp).normalized()*d;prof.append(lo)
 for step in range(1,7):
  t=step/6;prof.append((1-t)**2*lo+2*t*(1-t)*bp+t*t*hi)
prof.append(Vector(poly[-1]));rings=[annuli[0]]
for radius,dz in prof[1:]:
 ring=[]
 for ph,(u,v)in zip(phis,holes):p=surface(u,v);ring.append(addv((radius*math.cos(ph),center[1]+radius*math.sin(ph),p.z+dz)))
 rings.append(ring)
rings.append(annuli[1]);N=len(rings)
# Normals on collar derived from actual two-parameter neck surface; body joins remain independently documented.
cn={}
for ri,row in enumerate(rings):
 for k,idx in enumerate(row):
  tang=verts[row[(k+1)%K]]-verts[row[(k-1)%K]];ra=max(0,ri-1);rb=min(N-1,ri+1);cross=verts[rings[rb][k]]-verts[rings[ra][k]];cn[ri,k]=tuple(tang.cross(cross).normalized())
for ri in range(N-1):
 for k in range(K):
  h=(k+1)%K
  for refs in [[(ri,k),(ri,h),(ri+1,h)],[(ri,k),(ri+1,h),(ri+1,k)]]:
   ids=[rings[a][b]for a,b in refs];uv=[(b/K,a/(N-1))for a,b in refs];nn=[cn[a,b]for a,b in refs]
   # The angular seam receives v=1 on the last band, not a giant wrapped triangle.
   if k==K-1:uv=[(1 if b==0 else b/K,a/(N-1))for a,b in refs]
   face(ids,uv,3,nn)
# Remove unused interior patch vertices only; all referenced source positions remain exact.
used=sorted({i for f in faces for i in f});remap={v:i for i,v in enumerate(used)};coords=[verts[i]for i in used];faces=[tuple(remap[i]for i in f)for f in faces];mesh=bpy.data.meshes.new('Parametric skin plus open finite neck estimated');mesh.from_pydata(coords,[],faces);mesh.update();mesh.materials.clear()
for m in old.materials:mesh.materials.append(m)
uv=mesh.uv_layers.new(name='Original skin and neck charts');ln=[]
for p in mesh.polygons:
 p.use_smooth=regions[p.index]!=2
 for j,l in enumerate(p.loop_indices):uv.data[l].uv=uvs[p.index][j];ln.append(norms[p.index][j])
mesh.normals_split_custom_set(ln);att=mesh.attributes.new('SKIN_REGION','INT','FACE')
for i,r in enumerate(regions):att.data[i].value=r
obj.data=mesh;obj.name='Tank upper skin with open filler mouth - estimated';bpy.data.meshes.remove(old);obj['mouth_status']='Observed related mouth, all radius/section/depth estimates; no hidden lock/mechanism';source=H/'fuel-tank-shell-study-v2.blend';export=H/'fuel-tank-shell-study-v2.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
from collections import Counter
edges=Counter(tuple(sorted((a,b)))for f in faces for a,b in zip(f,f[1:]+f[:1]));vol=sum(coords[a].dot(coords[b].cross(coords[c]))/6 for a,b,c in faces);areas=[p.area for p in mesh.polygons];report={'source_sha256':sha(source),'export_sha256':sha(export),'base_source_sha256':b['source_sha256'],'builder_sha256':sha(Path(__file__)),'object':obj.name,'vertices':len(coords),'triangles':len(faces),'retained_source1_triangles':retained,'retained_source1_positions_exact_in_memory':True,'replaced_patch_ij':[i0,i1,j0,j1],'wall_volume_m3':vol,'non_two_face_edges':sum(v!=2 for v in edges.values()),'exact_zero_area_triangles':sum(a==0 for a in areas),'min_area_m2':min(areas),'neck_is':'Short finite visible mouth candidate, estimated dimension/section/depth; no hidden mechanism','external_libraries':len(bpy.data.libraries),'art_accepted':False}
(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');assert not report['non_two_face_edges']and vol>0 and min(areas)>0;print('TANK2',json.dumps(report))
