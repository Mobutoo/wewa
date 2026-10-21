"""Complete visible housing structure from related bare photos, still conditional gray.
Physical dimensions/sections estimated; exactRDC code, clip and installed fit unknown.
"""
import bpy,bmesh,json,hashlib,math,tempfile,subprocess,shutil,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import barycentric_transform
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(H));from housing_geometry_v3 import *
O=R/'creative/reviews/headlamp-housing-study-v5';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();basecheck=json.loads((R/'creative/reviews/headlamp-housing-core-study-v2/source-geometry-check.json').read_text());baseline=H/'headlamp-housing-core-study-v2.blend';assert sha(baseline)==basecheck['source_sha256'];p=json.loads((R/'creative/research/headlamp/housing-rear-structure-plan-v1.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(baseline));C=bpy.data.collections[basecheck['collection']];C.name='WEWA_HEADLAMP_HOUSING_STUDY';base=bpy.data.objects[basecheck['object']];root=bpy.data.objects[basecheck['root']];base.parent=None;K=bpy.data.collections.new('Housing editable rear mounting and bore construction - hidden');bpy.context.scene.collection.children.link(K);C.objects.unlink(base);K.objects.link(base);features=[];drills=[]
for item in p['upper_arms']:
 side=item['side'];sign=item['world_X_sign'];xc=lambda z,sg=sign:sg*(.045+.010*(z-.024)/.061);features.append(prism_yz(side+' upper formed housing support and terminal flange',item['YZ_outline_m'],xc,item['X_width_m'],K,.0008));slot=item['upper_slot'];drills.append(box(side+' upper visible slot cutter',(slot['centre_X_m'],slot['centre_Y_m'],slot['centre_Z_m']),(slot['XY_size_m'][0],slot['XY_size_m'][1],.030),K,.0012))
 # Two narrow rear edge ribs on the vertical support, ending before flange holes.
 for edge in [-1,1]:
  profile=[[.054,.028],[.055,.060],[.058,.076],[.064,.078],[.061,.058],[.060,.028]];features.append(prism_yz(side+' upper support edge rib '+str(edge),profile,lambda z,sg=sign,ed=edge:sg*(.045+.010*(z-.024)/.061)+ed*.0065,.0018,K,.0005))
for item in p['side_arms']:
 side=item['side'];sg=item['world_X_sign'];centre=item['tip_absX_m'];zz=item['tip_Z_m'];rad=item['tip_round_radius_m'];outline=[[sg*.047,.006],[sg*.075,.002]]
 for k in range(25):
  angle=math.radians(90+180*k/24);outline.append([sg*(centre-rad*math.cos(angle)),zz+rad*math.sin(angle)])
 outline +=[[sg*.075,-.030],[sg*.047,-.022]]
 fun=lambda x,z:.051+.019*smooth5((abs(x)-.045)/.080);features.append(formed_xz(side+' lateral formed mounting arm',outline,lambda x,z:fun(x,z)-.0015,lambda x,z:fun(x,z)+.0015,K,.0008));drills.append(hole_y(side+' lateral actual through-hole cutter',sg*centre,zz,item['hole_diameter_m'],K))
 for edge in ['upper','lower']:
  path=[]
  for k in range(5):
   xx=.052+(.111-.052)*k/4;t=(xx-.047)/(.124-.047);z=.004-.010*t if edge=='upper'else-.020-.008*t;path.append([sg*xx,z])
  out=ribbon(path,.0018);features.append(formed_xz(side+' lateral arm '+edge+' rear rib',out,lambda x,z:fun(x,z)+.0005,lambda x,z:fun(x,z)+.0065,K,.00045,step=.0025))
tip_plan=json.loads((R/'creative/research/headlamp/housing-lower-contour-plan-v4.json').read_text())
for item in p['lower_arms']:
 # Circular terminal follows the observable rounded foot, not a physical measure.
 sg=item['world_X_sign'];hx,hz=item['hole_centre_XZ_m'];radius=tip_plan['working_tip_radius_m'];arc=[[hx+sg*radius*math.cos(math.pi*k/32),hz-radius*math.sin(math.pi*k/32)]for k in range(33)];item['XZ_outline_m']=item['XZ_outline_m'][:5]+arc+item['XZ_outline_m'][8:]
 # Observed formed S-contour: tangent quadratic rounds at the coarse cage
 # knees, preserving the already sampled circular foot terminal.
 outline=item['XZ_outline_m'];rounded=[];last_arc=5+33
 for j,point in enumerate(outline):
  a,b,c=Vector(outline[j-1]),Vector(point),Vector(outline[(j+1)%len(outline)])
  if 5<=j<last_arc:rounded.append(list(b));continue
  cut=min(.004,(b-a).length*.25,(c-b).length*.25);left=b+(a-b).normalized()*cut;right=b+(c-b).normalized()*cut
  rounded.extend([list((1-t)**2*left+2*(1-t)*t*b+t*t*right)for t in [k/8 for k in range(9)]])
 item['XZ_outline_m']=rounded
 side=item['side'];fun=lambda x,z:.053+.022*smooth5((-z-.035)/.085);features.append(formed_xz(side+' curved lower mounting arm',item['XZ_outline_m'],lambda x,z:fun(x,z)-.0015,lambda x,z:fun(x,z)+.0015,K,.0008));x,z=item['hole_centre_XZ_m'];drills.append(hole_y(side+' lower actual through-hole cutter',x,z,item['hole_diameter_m'],K))
 for k,path in enumerate(item['rib_paths_XZ_m']):
  out=ribbon(path,.0018);features.append(formed_xz(side+' curved lower arm rear edge rib '+str(k),out,lambda x,z:fun(x,z)+.0005,lambda x,z:fun(x,z)+.0065,K,.00045,step=.0025))
item=p['top_centre'];features.append(prism_yz('Observed uppercentre support - clip detail unresolved',item['YZ_outline_m'],lambda z:0,item['X_width_m'],K,.0007))
inputs=[input_row(o)for o in [base]+features+drills]
from mathutils.bvhtree import BVHTree
input_checks=[]
for ref in inputs:
 dots=[]
 for tr,ns in zip(ref['triangles'],ref['corner_normals']):
  a,b,c=[Vector(ref['vertices'][k])for k in tr];normal=(b-a).cross(c-a).normalized();dots.extend(normal.dot(Vector(n))for n in ns)
 input_checks.append({'name':ref['name'],'triangles':len(ref['triangles']),'min_face_custom_normal_dot':min(dots),'loops_dot_below_point5':sum(d<.5 for d in dots)})
(O/'input-normal-diagnostic.json').write_text(json.dumps(input_checks,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath='/tmp/housing-current-debug.blend')
assert min(r['min_face_custom_normal_dot']for r in input_checks)>.5,input_checks
with tempfile.TemporaryDirectory(prefix='wewa-housing-full-')as td:
 inp=Path(td)/'in.json';out=Path(td)/'out.json';nf=len(features);inp.write_text(json.dumps({'base':inputs[0],'features':inputs[1:1+nf],'drills':inputs[1+nf:]}));subprocess.run([shutil.which('python'),str(H/'housing_csg_worker_v2.py'),str(inp),str(out)],check=True);cs=json.loads(out.read_text())
a=object_mesh('Headlamp housing with ribs and mounting ears - conditional gray',cs['vertices'],cs['triangles'],C);a.parent=root;a.data.materials.append(bpy.data.materials['WEWA housing core neutral shape gray']);m=a.data;normals=[];min_dot=1
for poly in m.polygons:
 poly.use_smooth=True;own=cs['triangle_source_owners'][poly.index];fid=cs['triangle_source_face_ids'][poly.index];ref=inputs[own];idx=ref['triangles'][fid];p0,p1,p2=[Vector(ref['vertices'][k])for k in idx];n0,n1,n2=[Vector(v)for v in ref['corner_normals'][fid]];assert set(poly.vertices)==set(cs['triangles'][poly.index])
 for li in poly.loop_indices:
  point=m.vertices[m.loops[li].vertex_index].co;n=barycentric_transform(point,p0,p1,p2,n0,n1,n2).normalized()
  if own>len(features):n=-n
  normals.append(n);min_dot=min(min_dot,n.dot(poly.normal))
assert min_dot>.5, min_dot
m.normals_split_custom_set(normals);m.uv_layers.new(name='ShapeStudyPlanarCharts')
for poly in m.polygons:
 axis=max(range(3),key=lambda k:abs(poly.normal[k]));other=[k for k in range(3)if k!=axis]
 for li in poly.loop_indices:
  co=m.vertices[m.loops[li].vertex_index].co;m.uv_layers.active.data[li].uv=(co[other[0]]/.1,co[other[1]]/.1)
K.hide_render=True;K.hide_viewport=True;bpy.context.view_layer.update();m.calc_loop_triangles();areas=[t.area for t in m.loop_triangles];bm=bmesh.new();bm.from_mesh(m);nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free();assert not nm and min(areas)>0 and vol>0
source=H/'headlamp-housing-study-v5.blend';glb=H/'headlamp-housing-study-v5.glb';bpy.ops.object.select_all(action='DESELECT');a.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=a;bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False,export_animations=False)
report={'schema':1,'revision':'headlamp-housing-study-v5','source_sha256':sha(source),'export_sha256':sha(glb),'collection':C.name,'root':root.name,'object':a.name,'triangles':len(areas),'exact_zero_area_triangles':sum(x==0 for x in areas),'min_triangle_area_m2':min(areas),'non_manifold_edges':nm,'signed_volume_m3':vol,'connected_components_actual_CSG':cs['connected_components'],'min_face_custom_normal_dot':min_dot,'feature_input_names':[x.name for x in features],'drill_input_names':[x.name for x in drills],'CSG_stages':cs['stages'],'core_source_sha256':basecheck['source_sha256'],'scope':'Conditional relatedYDY02002 visible housing and structures, estimated sections. Uppercentre clip detail, actualRDC identity and matingdimensions unresolved. Not completeheadlamp.','art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['CSG_stages','feature_input_names','drill_input_names']}))
