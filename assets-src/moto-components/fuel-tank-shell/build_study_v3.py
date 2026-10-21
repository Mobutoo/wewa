"""Two upper openings, editable annular patches; source2 history stays immutable."""
import bpy,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/fuel-tank-shell-study-v3';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();b=json.loads((R/'creative/reviews/fuel-tank-shell-study-v2/build-report.json').read_text());base=H/'fuel-tank-shell-study-v2.blend';assert sha(base)==b['source_sha256'];P=json.loads((H/'parameters-study-v1.json').read_text());U=P['longitudinal_stations'];C=P['cross_profile'];ns={'Vector':Vector,'U':U,'C':C};tree=ast.parse((H/'build_study_v1.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['slopes','interp','surface','normal']],type_ignores=[]),'<frozen-original-surface>','exec'),ns);surface=ns['surface'];normal=ns['normal'];bpy.ops.wm.open_mainfile(filepath=str(base));obj=bpy.data.objects[b['object']];old=obj.data;verts=[v.co.copy()for v in old.vertices];normals=old.corner_normals;lookup={tuple(v):i for i,v in enumerate(verts)};nu=P['grid']['longitudinal'];nv=P['grid']['cross'];thick=P['skin_thickness_m'];configs=[{'ij':[108,115,86,93],'centre':[-.018,.171]},{'ij':[108,115,99,106],'centre':[.018,.171]}]
def original(i,j,inner=False):
 u=i/nu;v=-1+2*j/nv;p=surface(u,v)
 if inner:p=p-thick*normal(u,v)
 return lookup[tuple(p)]
removed=set();rects=[]
for cfg in configs:
 i0,i1,j0,j1=cfg['ij']
 for i in range(i0,i1):
  for j in range(j0,j1):
   for inner in [False,True]:
    a=original(i,j,inner);bb=original(i,j+1,inner);c=original(i+1,j,inner);d=original(i+1,j+1,inner);removed.add(frozenset((a,bb,d)));removed.add(frozenset((a,d,c)))
 grid=[(i0,j)for j in range(j0,j1+1)]+[(i,j1)for i in range(i0+1,i1+1)]+[(i1,j)for j in range(j1-1,j0-1,-1)]+[(i,j0)for i in range(i1-1,i0,-1)];rects.append(grid)
faces=[];uvs=[];nn=[];regs=[];removed_count=0
for p in old.polygons:
 if frozenset(p.vertices)in removed:removed_count+=1;continue
 faces.append(tuple(p.vertices));uvs.append([tuple(old.uv_layers[0].data[l].uv)for l in p.loop_indices]);nn.append([tuple(normals[l].vector)for l in p.loop_indices]);regs.append(old.attributes['SKIN_REGION'].data[p.index].value)
assert removed_count==len(removed);retained=len(faces)
def add(p):verts.append(Vector(p));return len(verts)-1
def f(ids,uv,no,r):faces.append(tuple(ids));uvs.append(uv);nn.append(no);regs.append(r)
# Newton works in double scalar arithmetic; mathutils.Vector intentionally quantizes
# toFloat32 and cannot establish a1e-11 residual on coordinates near.17m.
def sxy(u,v):
 vals={k:ns['interp'](U['u'],U[k],u)for k in ['y','halfwidth','crown_sweep_y']};vv=abs(v);xf=ns['interp'](C['s'],C['halfwidth_fraction'],vv);zf=ns['interp'](C['s'],C['height_fraction'],vv,start=0)
 return((-1 if v<0 else 1)*vals['halfwidth']*xf,vals['y']+vals['crown_sweep_y']*zf)
def sxyz(u,v):
 x,y=sxy(u,v);low=ns['interp'](U['u'],U['lower_z'],u);high=ns['interp'](U['u'],U['crown_z'],u);zf=ns['interp'](C['s'],C['height_fraction'],abs(v),start=0);return(x,y,low+(high-low)*zf)
def ndouble(u,v):
 e=1e-5;ap=sxyz(u+e,v);am=sxyz(u-e,v);bp=sxyz(u,v+e);bm=sxyz(u,v-e);a=[(ap[k]-am[k])/(2*e)for k in range(3)];b=[(bp[k]-bm[k])/(2*e)for k in range(3)];n=[b[1]*a[2]-b[2]*a[1],b[2]*a[0]-b[0]*a[2],b[0]*a[1]-b[1]*a[0]];q=math.sqrt(sum(x*x for x in n));return[x/q for x in n]
solver_errors=[]
def invert(x,y,inner=False):
 def xy(u,v):
  a=sxy(u,v)
  if not inner:return a
  n=ndouble(u,v);return(a[0]-thick*n[0],a[1]-thick*n[1])
 u=.625;v=x/.26
 for it in range(20):
  px,py=xy(u,v);ex=px-x;ey=py-y;d=1e-5;ap=xy(u+d,v);am=xy(u-d,v);bp=xy(u,v+d);bm=xy(u,v-d);ax=(ap[0]-am[0])/(2*d);ay=(ap[1]-am[1])/(2*d);bx=(bp[0]-bm[0])/(2*d);by=(bp[1]-bm[1])/(2*d);det=ax*by-bx*ay;u-=(by*ex-bx*ey)/det;v-=(-ay*ex+ax*ey)/det
  if math.hypot(ex,ey)<1e-12:break
 px,py=xy(u,v);assert math.hypot(px-x,py-y)<1e-12;p=surface(u,v)-thick*normal(u,v)if inner else surface(u,v);solver_errors.append(math.hypot(p.x-x,p.y-y));return(u,v)

for cfg,grid in zip(configs,rects):
 centre=cfg['centre'];M=len(grid);sub=4;K=M*sub;uv0=[(i/nu,-1+2*j/nv)for i,j in grid];ph=[]
 for i,j in grid:
  p=surface(i/nu,-1+2*j/nv);ph.append(math.atan2(p.y-centre[1],p.x-centre[0]))
 for k in range(1,M):
  while ph[k]<=ph[k-1]:ph[k]+=2*math.pi
 phend=ph[0]+2*math.pi;angles=[];outline=[]
 for k in range(M):
  h=(k+1)%M
  for q in range(sub):
   t=q/sub;angles.append(ph[k]*(1-t)+(ph[h]if h else phend)*t);outline.append((uv0[k][0]*(1-t)+uv0[h][0]*t,uv0[k][1]*(1-t)+uv0[h][1]*t))
 hole=[invert(centre[0]+.003*math.cos(p),centre[1]+.003*math.sin(p))for p in angles];annuli=[]
 for inner in [False,True]:
  localhole=[invert(centre[0]+.003*math.cos(p),centre[1]+.003*math.sin(p),True)for p in angles]if inner else hole
  rows=[]
  for ri in range(1,9):
   t=ri/8;uv=[(a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t)for a,b in zip(outline,localhole)];ids=[add(surface(u,v)-thick*normal(u,v)if inner else surface(u,v))for u,v in uv];rows.append((ids,uv))
  def skintri(ids,uv):
   no=[tuple(-normal(u,v)if inner else normal(u,v))for u,v in uv]
   if inner:ids=list(reversed(ids));uv=list(reversed(uv));no=list(reversed(no))
   f(ids,[(u,(v+1)/2)for u,v in uv],no,1 if inner else 0)
  a=[original(i,j,inner)for i,j in grid];b0,bu=rows[0]
  for k in range(M):
   h=(k+1)%M;hi=(k+1)*sub%K;skintri([a[k],a[h],b0[hi]],[uv0[k],uv0[h],bu[hi]])
   for q in range(sub-1,-1,-1):
    aa=(k*sub+q)%K;bb=(aa+1)%K;skintri([a[k],b0[bb],b0[aa]],[uv0[k],bu[bb],bu[aa]])
  for ri in range(7):
   a,au=rows[ri];bb,bu=rows[ri+1]
   for k in range(K):
    h=(k+1)%K;skintri([a[k],a[h],bb[h]],[au[k],au[h],bu[h]]);skintri([a[k],bb[h],bb[k]],[au[k],bu[h],bu[k]])
  annuli.append(rows[-1][0])
 # Short rounded cut edge between outer and inner skin; no separate bushing or invented fastener.
 rings=[annuli[0]]
 for radius,dz in [(.00294,-.00004),(.00286,-.00013),(.00282,-.00023),(.00282,-.00077),(.00286,-.00087),(.00294,-.00096)]:
  rings.append([add((centre[0]+radius*math.cos(p),centre[1]+radius*math.sin(p),surface(u,v).z+dz))for p,(u,v)in zip(angles,hole)])
 rings.append(annuli[1]);N=len(rings);no={}
 for ri,row in enumerate(rings):
  for k in range(K):
   tangent=verts[row[(k+1)%K]]-verts[row[(k-1)%K]];through=verts[rings[min(N-1,ri+1)][k]]-verts[rings[max(0,ri-1)][k]];no[ri,k]=tuple(tangent.cross(through).normalized())
 for ri in range(N-1):
  for k in range(K):
   h=(k+1)%K
   for refs in [[(ri,k),(ri,h),(ri+1,h)],[(ri,k),(ri+1,h),(ri+1,k)]]:
    ids=[rings[a][b]for a,b in refs];uv=[((1 if k==K-1 and b==0 else b/K),a/(N-1))for a,b in refs];f(ids,uv,[no[a,b]for a,b in refs],4)
used=sorted({i for f0 in faces for i in f0});mp={i:k for k,i in enumerate(used)};coords=[verts[i]for i in used];faces=[tuple(mp[i]for i in f0)for f0 in faces];mesh=bpy.data.meshes.new('Upper skin with filler and two actual openings - estimates');mesh.from_pydata(coords,[],faces);mesh.update()
for m in old.materials:mesh.materials.append(m)
uv=mesh.uv_layers.new(name='Original surface and separate opening charts');ln=[]
for p in mesh.polygons:
 p.use_smooth=regs[p.index]!=2
 for k,l in enumerate(p.loop_indices):uv.data[l].uv=uvs[p.index][k];ln.append(nn[p.index][k])
mesh.normals_split_custom_set(ln);att=mesh.attributes.new('SKIN_REGION','INT','FACE')
for i,r in enumerate(regs):att.data[i].value=r
obj.data=mesh;obj.name='Tank upper skin with filler and nearby openings - estimated';bpy.data.meshes.remove(old);source=H/'fuel-tank-shell-study-v3.blend';export=H/'fuel-tank-shell-study-v3.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
from collections import Counter
edges=Counter(tuple(sorted((a,b)))for f0 in faces for a,b in zip(f0,f0[1:]+f0[:1]));areas=[p.area for p in mesh.polygons];vol=sum(coords[a].dot(coords[b].cross(coords[c]))/6 for a,b,c in faces);report={'source_sha256':sha(source),'export_sha256':sha(export),'base_source_sha256':b['source_sha256'],'builder_sha256':sha(Path(__file__)),'object':obj.name,'triangles':len(faces),'vertices':len(coords),'retained_source2_triangles':retained,'removed_source2_triangles':removed_count,'patches':configs,'non_two_face_edges':sum(v!=2 for v in edges.values()),'exact_zero_area_triangles':sum(a==0 for a in areas),'minimum_area_m2':min(areas),'wall_volume_m3':vol,'max_actual_Float32_XY_circle_residual_m':max(solver_errors),'double_inverse_convergence_m':1e-12,'status':'Estimated gray visible detail, not complete tank/OEMshape','art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');assert min(areas)>0 and vol>0 and not report['non_two_face_edges'];print('TANK3',json.dumps(report))
