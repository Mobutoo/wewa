"""Official R04 lower brake-sheath visible bow; review cuts, no hidden routing."""
import bpy,math,json,bmesh
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');key='front-completion-p29-bow-v1';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
controls=[(0,0,0),(0,.045,.028),(.003,.085,.068),(.006,.112,.155),(.009,.115,.265),(.011,.108,.385),(.012,.090,.50)]
P={'reference':'Official current RDC R04: external brake-cable bow behind left fork; isolated visible segment only','private_photo':'/workspace/wewa-assets/references/exterior-completion-current/04.png','controls_m':controls,'frame':'origin lower visible review cut, +Z up, +Y rear, +X transverse; unmounted','outer_radius_m':.0028,'outer_radius_bounds_m':[.002,.0038],'visible_height_m':.50,'height_bounds_m':[.40,.65],'depth_excursion_m':.115,'depth_bounds_m':[.07,.16],'all_dimensions_estimated':True,'depth_method':'Side image bounds silhouette; transverse offsets and perspective depth are explicit artist estimates','hidden_routes':'excluded beyond two review cuts','inner_wire_and_housing_structure':'not modeled; open external skin only','installed_endpoints':False,'steering_slack_verified':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2));p=[Vector(v)for v in controls];p=[p[0]]+p+[p[-1]];centres=[]
for i in range(1,len(p)-2):
 a,b,c,d=p[i-1:i+3]
 for j in range(50):
  t=j/50;centres.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
centres.append(Vector(controls[-1]));v=[];f=[];n=64;last=None
for i,c in enumerate(centres):
 tangent=(centres[min(i+1,len(centres)-1)]-centres[max(0,i-1)]).normalized();normal=tangent.cross(Vector((1,0,0))).normalized()if last is None else(last-tangent*last.dot(tangent)).normalized();binormal=tangent.cross(normal).normalized();last=normal
 for j in range(n):a=2*math.pi*j/n;v.append(tuple(c+.0028*(normal*math.cos(a)+binormal*math.sin(a))))
for i in range(len(centres)-1):
 for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
m=bpy.data.meshes.new('Authored transported cable bow exterior');m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();ob=bpy.data.objects.new('VISIBLE_LOWER_BRAKE_SHEATH_BOW_REVIEW_CUTS',m);bpy.context.collection.objects.link(ob)
uv=m.uv_layers.new(name='Original cable arc UV')
for p in m.polygons:
 p.use_smooth=True
 for li in p.loop_indices:
  idx=m.loops[li].vertex_index;u=idx%n/n
  if idx%n==0 and any(q%n==n-1 for q in p.vertices):u=1
  uv.data[li].uv=(u,(idx//n)/(len(centres)-1))
mat=bpy.data.materials.new('Neutral gray before material');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.25,.25,.25,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.4;m.materials.append(mat)
bm=bmesh.new();bm.from_mesh(m);m.calc_loop_triangles();report={'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'boundary_edges':sum(e.is_boundary for e in bm.edges),'branch_edges':sum(len(e.link_faces)>2 for e in bm.edges),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles),'two_intentional_open_review_cuts':True,'all_dimensions_estimated':True};bm.free();assert report['boundary_edges']==2*n and report['branch_edges']==0 and report['minimum_triangle_area_m2']>1e-18
ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'bow-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'bow-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2))
