"""Bounded related DJ151041 exterior study; no installed stack or hidden head feature."""
import bpy,bmesh,math,json
from pathlib import Path
R=Path('/workspace/wewa');key='front-completion-p24-axle-v1';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
P={'part_branch':'DJ151041 related UG/Pulsar branch; not DZ151012 or confirmed RDC125HD','reference_photo':'/workspace/wewa-assets/references/front-completion-p24/DJ151041.jpg','overall_length_m':.205,'length_bounds_m':[.18,.24],'shaft_radius_m':.0065,'shaft_radius_bounds_m':[.0055,.008],'head_radius_m':.011,'head_radius_bounds_m':[.009,.015],'head_thickness_m':.005,'thread_length_m':.020,'thread_length_bounds_m':[.015,.030],'thread_pitch_working_m':.0015,'pitch_bounds_m':[.001,.002],'thread_hand':'right-hand working hypothesis, not verified','thread_crest_radius_m':.00615,'thread_root_radius_m':.00545,'all_dimensions_estimated':True,'hidden_head_face':'plain finite closure estimate; no invented socket/slot/hex','mounted_fit':False,'load_or_thread_standard_claim':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2))
rings=[(0,.0102),(.00025,.01065),(.00065,.011),(.0043,.011),(.00475,.0107),(.005,.0102),(.005,.0072),(.0053,.0068),(.0058,.0065),(.008,.0065),(.06,.0065),(.12,.0065),(.18,.0065),(.184,.0065),(.185,.00615)]
for i in range(1,801):rings.append((.185+.020*i/800,None))
n=192;v=[];f=[]
for z,r in rings:
 for j in range(n):
  a=2*math.pi*j/n
  if r is None:
   d=abs(((z-.185)/.0015-a/(2*math.pi))%1-.5);q=min(1,max(0,(d-.13)/.30));q=q*q*(3-2*q);env=min(1,(z-.185)/.0015,(.205-z)/.001);env=max(0,env);rr=.00615-.0007*q*env
   if z>.2045:rr-=.0005*(z-.2045)/.0005
  else:rr=r
  v.append((rr*math.cos(a),rr*math.sin(a),z))
for i in range(len(rings)-1):
 for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
for ring,z,rev in [(0,0,True),(len(rings)-1,.205,False)]:
 c=len(v);v.append((0,0,z))
 for j in range(n):a=ring*n+j;b=ring*n+(j+1)%n;f.append((c,b,a)if rev else(c,a,b))
m=bpy.data.meshes.new('Continuous head fillet shaft lead-in and helical external section');m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update();ob=bpy.data.objects.new('DJ151041_RELATED_EXTERNAL_AXLE_ESTIMATED',m);bpy.context.collection.objects.link(ob)
for p in m.polygons:p.use_smooth=len(p.vertices)==4 and p.index//n not in [4,5]
mat=bpy.data.materials.new('Neutral gray before material');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.25,.25,.25,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.3;m.materials.append(mat)
bm=bmesh.new();bm.from_mesh(m);m.calc_loop_triangles();report={'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles),'all_dimensions_estimated':True,'thread_form':'explicit unmeasured working crest/root/pitch, not certified screw standard','mounted_fit':False};bm.free();assert report['nonmanifold_edges']==0 and report['volume_m3']>0 and report['minimum_triangle_area_m2']>1e-18
ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'axle-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'axle-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2))
