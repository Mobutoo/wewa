"""Explicit finite rounded perimeter, no bevel/CSG, separate source study."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instrument-visor-shell-study-v3';OUT.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=json.loads((ROOT/'creative/reviews/instrument-visor-shell-study-v1/source-geometry-check.json').read_text());baseline=HERE/'instrument-visor-shell-study-v1.blend';assert sha(baseline)==old['source_sha256'];g=json.loads((HERE/'rounded-planar-grid-v3.json').read_text());outline=json.loads((HERE/'outline-rounded-v3.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(baseline));ob=bpy.data.objects[old['object']];U=Vector(old['frame']['U']);V=Vector(old['frame']['up_V']);N=Vector(old['frame']['front_N']);origin=Vector(old['frame']['origin_m']);k=.040/.125**2;a=2*k;r=.00025;h=.0025/2;count=len(g['vertices_2D_m'])
def surface(p):return origin+U*p[0]+V*p[1]-N*k*p[0]**2
def normal(x):return(N+U*a*x).normalized()
def normal_dx(x):
 n=normal(x);return(U*a-n*(n.dot(U)*a))/math.sqrt(1+(a*x)**2)
verts=[];norms=[]
for sign in [1,-1]:
 for p in g['vertices_2D_m']:verts.append(surface(p)+normal(p[0])*(sign*h));norms.append(normal(p[0])*sign)
faces=[tuple(f)for f in g['triangles']]+[tuple(i+count for i in reversed(f))for f in g['triangles']];directed={}
for f in g['triangles']:
 for q,w in zip(f,f[1:]+f[:1]):
  key=tuple(sorted((q,w)));directed[key]=None if key in directed else(q,w)
successor={q:w for edge in directed.values()if edge is not None for q,w in[edge]};start=next(iter(successor));order=[start]
while successor[order[-1]]!=start:order.append(successor[order[-1]])
assert len(order)==len(successor)
# Profile0=front core,1..4=front quarter,5=back side,6..8=back quarter,9=back core.
profile={};station={};circumference={order[0]:0.}
for ii,i in enumerate(order):
 row=g['boundary_station_map'][str(i)];O=Vector(row['outer_original_2D_m']);C=Vector(row['inner_core_2D_m']);delta=C-O;ids=[i];params=[(0,'front',C,h)]
 for j in range(1,9):
  if j<=4:alpha=j*math.pi/8;side='front';p=O+delta*(1-math.sin(alpha));d=h-r+r*math.cos(alpha)
  elif j==5:alpha=math.pi/2;side='side';p=O;d=-h+r
  else:alpha=(9-j)*math.pi/8;side='back';p=O+delta*(1-math.sin(alpha));d=-h+r-r*math.cos(alpha)
  ids.append(len(verts));verts.append(surface(p)+normal(p[0])*d);norms.append(Vector());params.append((alpha,side,p,d))
 ids.append(i+count);params.append((0,'back',C,-h));profile[i]=ids;station[i]=(O,delta,params)
 if ii:
  prev=order[ii-1];circumference[i]=circumference[prev]+(surface(O)-surface(station[prev][0])).length
perimeter=circumference[order[-1]]+(surface(station[order[-1]][0])-surface(station[order[0]][0])).length
cross_arc={}
for ii,i in enumerate(order):
 ids=profile[i];O,delta,params=station[i];arc=[0.]
 for j in range(1,10):arc.append(arc[-1]+(verts[ids[j]]-verts[ids[j-1]]).length)
 cross_arc[i]=arc
 for j in range(1,9):
  p0=verts[profile[order[ii-1]][j]];p1=verts[ids[j]];p2=verts[profile[order[(ii+1)%len(order)]][j]];l0=(p1-p0).length;l1=(p2-p1).length;ds=(p2-p1)*(l0/(l1*(l0+l1)))+(p1-p0)*(l1/(l0*(l0+l1)));alpha,side,p,d=params[j];n=normal(p[0])
  if side=='side':nn=ds.cross(n)
  else:
   dp=-delta*math.cos(alpha);dd=(-r if side=='front'else r)*math.sin(alpha);da=(U-N*a*p[0])*dp[0]+V*dp[1]+normal_dx(p[0])*dp[0]*d+n*dd;nn=da.cross(ds)if side=='front'else ds.cross(da)
  assert nn.length>0;norms[ids[j]]=nn.normalized()
for i in order:
 other=successor[i]
 for j in range(9):faces.append((profile[i][j],profile[i][j+1],profile[other][j+1],profile[other][j]))
data=bpy.data.meshes.new('Original explicitly rolled250um edge, metric offset core and continuous profile');data.from_pydata([tuple(v)for v in verts],[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free();materials=list(ob.data.materials);ob.data=data
for m in materials:data.materials.append(m)
for f in data.polygons:f.use_smooth=True
data.normals_split_custom_set([norms[l.vertex_index]for l in data.loops]);uv=data.uv_layers.new(name='Original midsurface10mm and continuous rolled-edge profile UV');triangles=len(g['triangles']);lookup={v:(i,j)for i,ids in profile.items()for j,v in enumerate(ids)}
def transverse_arc(x):return .5*(x*math.sqrt(1+(a*x)**2)+math.asinh(a*x)/a)
for f in data.polygons:
 if f.index<2*triangles:
  for li in f.loop_indices:
   p=g['vertices_2D_m'][data.loops[li].vertex_index%count];uv.data[li].uv=(transverse_arc(p[0])/.010,p[1]/.010)
 else:
  vals=[lookup[data.loops[li].vertex_index]for li in f.loop_indices];seam=max(circumference[i]for i,j in vals)-min(circumference[i]for i,j in vals)>perimeter/2
  for li in f.loop_indices:
   i,j=lookup[data.loops[li].vertex_index];s=circumference[i]+(perimeter if seam and circumference[i]<perimeter/2 else 0);uv.data[li].uv=(s/.010,cross_arc[i][j]/.010)
bm=bmesh.new();bm.from_mesh(data);todo=set(bm.verts);components=0
while todo:
 components+=1;stack=[todo.pop()]
 while stack:
  for edge in stack.pop().link_edges:
   for v in edge.verts:
    if v in todo:todo.remove(v);stack.append(v)
data.calc_loop_triangles();areas=[t.area for t in data.loop_triangles];dots=[f.normal.dot(norms[data.loops[li].vertex_index])for f in data.polygons for li in f.loop_indices];geometry={'vertices':len(data.vertices),'faces':len(data.polygons),'triangles':len(areas),'components':components,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True),'exact_zero_area_triangles':sum(v==0 for v in areas),'min_triangle_area_m2':min(areas),'min_face_custom_normal_dot':min(dots)};bm.free();assert components==1 and geometry['non_manifold_edges']==0 and geometry['signed_volume_m3']>0 and geometry['exact_zero_area_triangles']==0 and min(dots)>0,geometry
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.data.objects[old['root']].select_set(True);export=HERE/'instrument-visor-shell-study-v3.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False);dest=HERE/'instrument-visor-shell-study-v3.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);report=dict(old);report.update({'revision':'instrument-visor-shell-study-v3','source_sha256':sha(dest),'export_sha256':sha(export),'baseline_source_sha256':old['source_sha256'],'baseline_export_sha256':old['export_sha256'],'geometry':geometry,'rounded_grid_sha256':sha(HERE/'rounded-planar-grid-v3.json'),'rounded_outline_sha256':sha(HERE/'outline-rounded-v3.json'),'edge_method':{'source':'Explicit metric-offset inner chart + source quarter-round perimeter sections, no bevel or CSG','edge_radius_estimated_m':r,'quarter_segments':4,'tip_regularisation_estimated_m':.0004,'native_manual_point_max_error_px':outline['manual_native_points_max_distance_px'],'manual_working_band_px':3,'normals':'Normal of designed rolling crosssection crossed with local source station tangent; analytic front/back normals preserved at joins. Not normals inherited from an operation.','UV':'Continuous circumference/cross-profile chart for rolled edge, midsurface arc/height on front/back; no arbitrary tangent repair.'},'limits':[x for x in old['limits']if'sharp cut'not in x]+['Edge and tiny tip radii are working estimates inside native reading uncertainty, not physical/OEM measurements.']});(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(baseline)==old['source_sha256'];print('VISOR_ROLLED_EDGE_V3',geometry,report['source_sha256'],report['export_sha256'])
