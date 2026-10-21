"""Two observed finite tabs; isolated guideposes estimated, no hiddenmount copied."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/fuel-tank-shell-study-v6';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base=H/'fuel-tank-shell-study-v4.blend';b=json.loads((R/'creative/reviews/fuel-tank-shell-study-v4/build-report.json').read_text());assert sha(base)==b['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(base));body=bpy.data.objects[b['object']];root=body.parent;coll=body.users_collection[0];guide=bpy.data.collections.new('TAB_EDITABLE_CONTOURS_NOT_EXPORTED');bpy.context.scene.collection.children.link(guide);meshes=[body];sourcecurves=[];exact_welds=[]
def rounded(poly,r=.003):
 p=[Vector(v)for v in poly];out=[]
 for i,b in enumerate(p):
  a=p[(i-1)%len(p)];c=p[(i+1)%len(p)];d=min(r,.25*(a-b).length,.25*(c-b).length);lo=b+(a-b).normalized()*d;hi=b+(c-b).normalized()*d;out.append(tuple(lo))
  for k in range(1,9):
   t=k/8;out.append(tuple((1-t)**2*lo+2*t*(1-t)*b+t*t*hi))
 return out
def capsule(r,half,y=0):
 return [(r*math.cos(t),y+half+r*math.sin(t))for t in [k*math.pi/64 for k in range(65)]]+[(r*math.cos(t),y-half+r*math.sin(t))for t in [math.pi+k*math.pi/64 for k in range(65)]]
def pose(a,b,origin):
 a=Vector(a).normalized();b=Vector(b);b=(b-a*b.dot(a)).normalized();n=a.cross(b);m=Matrix((a,b,n)).transposed().to_4x4();m.translation=Vector(origin);return m
specs=[{'name':'Visible rear terminal flange with open aperture - estimated','polygon':[(.002,0),(.015,.010),(.047,.065),(.052,.081),(.050,.102),(0,.105),(-.006,.080),(-.004,.038)],'hole':[(.014+.004*math.cos(k*2*math.pi/128),.028+.004*math.sin(k*2*math.pi/128))for k in range(128)],'pose':pose((0,1,0),(0,0,-1),(-.060,.353,-.200)),'kind':'Rear terminalflank band per observed lowerreturn reading; wholeplane/upperroot/axes/depth estimated, not certifiedmount'},{'name':'Single observed lower pierced ear - estimated','polygon':[(-.018,0),(.018,0),(.017,.015),(.012,.026),(0,.029),(-.012,.026),(-.017,.015)],'hole':[(.00325*math.cos(k*2*math.pi/128),.018+.00325*math.sin(k*2*math.pi/128))for k in range(128)],'pose':pose((.30,1,.25),(0,0,-1),(-.0909,.294,-.3085)),'kind':'Only visible photo-near ear, assigned-X by construction hypothesis; no oppositeear invented'}]
for spec in specs:
 cu=bpy.data.curves.new(spec['name']+' original closedcontours','CURVE');cu.dimensions='2D';cu.resolution_u=1;cu.fill_mode='BOTH';cu.extrude=.00055;cu.bevel_depth=.0002;cu.bevel_resolution=4
 for coords in [rounded(spec['polygon']),list(reversed(spec['hole']))]:
  sp=cu.splines.new('POLY');sp.points.add(len(coords)-1)
  for p,(x,y)in zip(sp.points,coords):p.co=(x,y,0,1)
  sp.use_cyclic_u=True
 curve=bpy.data.objects.new(spec['name']+' editable source contour',cu);guide.objects.link(curve);curve.matrix_world=spec['pose'];bpy.context.view_layer.update();mesh=bpy.data.meshes.new_from_object(curve.evaluated_get(bpy.context.evaluated_depsgraph_get()));raw=mesh;unique={};coords=[];mapping=[]
 for vertex in raw.vertices:
  key=tuple(vertex.co)
  if key not in unique:unique[key]=len(coords);coords.append(key)
  mapping.append(unique[key])
 polys=[tuple(mapping[i]for i in p.vertices)for p in raw.polygons];mesh=bpy.data.meshes.new(spec['name']+' finite roundedwall exactseams');mesh.from_pydata(coords,[],polys);mesh.update();exact_welds.append({'object':spec['name'],'original_vertices':len(raw.vertices),'unique_vertices':len(coords),'moved_vertices':0,'epsilon_used':False,'method':'Identical Float32 position tuples only, all orientedpolygonposition sequences retained'});bpy.data.meshes.remove(raw);obj=bpy.data.objects.new(spec['name'],mesh);coll.objects.link(obj);obj.parent=root;obj.matrix_world=spec['pose'];obj['status']=spec['kind'];obj['estimated_dimensions']='1.5mm finitewall with0.2mm edge radius, original construction only';obj['mount']='Narrow rootcontact pose candidate only; not certifiedweld/mount';mesh.materials.append(body.data.materials[0]);uv=mesh.uv_layers.new(name='Original tab charts, cap and cutwall separated')
 for p in mesh.polygons:
  p.use_smooth=abs(p.normal.z)<.99999;axis=max(range(3),key=lambda i:abs(p.normal[i]));ij=[i for i in range(3)if i!=axis]
  for l in p.loop_indices:
   v=mesh.vertices[mesh.loops[l].vertex_index].co;uv.data[l].uv=(.5+v[ij[0]]/.1,.5+v[ij[1]]/.1)
 curve.hide_render=True;curve.hide_set(True);sourcecurves.append(curve.name);meshes.append(obj)
guide.hide_render=True;guide.hide_viewport=True;bpy.ops.object.select_all(action='DESELECT')
for o in meshes+[root]:o.select_set(True)
bpy.context.view_layer.objects.active=body;source=H/'fuel-tank-shell-study-v6.blend';export=H/'fuel-tank-shell-study-v6.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
reports=[]
for o in meshes:
 m=o.data;m.calc_loop_triangles();tri=[tuple(t.vertices)for t in m.loop_triangles];ed=Counter(tuple(sorted((a,b)))for f in tri for a,b in zip(f,f[1:]+f[:1]));v=[x.co for x in m.vertices];areas=[(v[b]-v[a]).cross(v[c]-v[a]).length/2 for a,b,c in tri];vol=sum(v[a].dot(v[b].cross(v[c]))/6 for a,b,c in tri);reports.append({'object':o.name,'triangles':len(tri),'vertices':len(v),'non_two_face_edges':sum(c!=2 for c in ed.values()),'zero_area_triangles':sum(a==0 for a in areas),'min_area_m2':min(areas),'signed_volume_local_m3':vol,'matrix_world':[list(a)for a in o.matrix_world]})
report={'source_sha256':sha(source),'export_sha256':sha(export),'base_source_sha256':b['source_sha256'],'builder_sha256':sha(Path(__file__)),'object':body.name,'objects':[o.name for o in meshes],'source_curves_not_exported':sourcecurves,'exact_curve_seam_welds':exact_welds,'geometry':reports,'only_one_observed_ear':True,'poses':'Original estimatedguide, rootcontacts notcertified, externalphotosnotcalibrated','external_libraries':len(bpy.data.libraries),'art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('TANK5',json.dumps(report));assert all(not g['non_two_face_edges']and not g['zero_area_triangles']and g['signed_volume_local_m3']>0 for g in reports)
