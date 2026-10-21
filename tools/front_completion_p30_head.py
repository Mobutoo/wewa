"""Current official visor visible fastener-head envelope; drive and shank unresolved."""
import bpy,bmesh,math,json
from pathlib import Path
R=Path('/workspace/wewa');key='front-completion-p30-head-v1';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
P={'reference':'Official R00/R01 small bright circular fastener heads on visor-side area','private_photos':['/workspace/wewa-assets/references/exterior-completion-current/00.png','/workspace/wewa-assets/references/exterior-completion-current/01.png'],'status':'visible head-envelope study, not a completed screw','radius_m':.004,'radius_bounds_m':[.003,.006],'height_m':.0018,'height_bounds_m':[.001,.003],'drive_form':'unresolved at available image resolution; no Phillips/slot/socket invented','shaft_thread_washer_nut':'excluded; hidden/identity unresolved','all_dimensions_estimated':True,'replication':'one isolated exemplar, no four-instance mounting layout or artistic acceptance'}
(H/'parameters.json').write_text(json.dumps(P,indent=2));n=256;profile=[(.0036,0),(.00395,.00015),(.004,.0004)]
for i in range(1,65):
 a=(math.pi/2)*i/65;profile.append((.004*math.cos(a),.0004+.0014*math.sin(a)))
v=[(r*math.cos(2*math.pi*j/n),r*math.sin(2*math.pi*j/n),z)for r,z in profile for j in range(n)];f=[]
for i in range(len(profile)-1):
 for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
for row,z,rev in [(0,0,True),(len(profile)-1,.0018,False)]:
 c=len(v);v.append((0,0,z))
 for j in range(n):a=row*n+j;b=row*n+(j+1)%n;f.append((c,b,a)if rev else(c,a,b))
m=bpy.data.meshes.new('Continuous circular rim and shallow dome envelope');m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update();ob=bpy.data.objects.new('VISOR_FASTENER_VISIBLE_HEAD_ENVELOPE_ONLY',m);bpy.context.collection.objects.link(ob)
for p in m.polygons:p.use_smooth=True
m.set_sharp_from_angle(angle=.7);mat=bpy.data.materials.new('Neutral gray incomplete head');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.25,.25,.25,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.3;m.materials.append(mat)
bm=bmesh.new();bm.from_mesh(m);m.calc_loop_triangles();report={'triangles':len(m.loop_triangles),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles),'incomplete_drive_region':True,'all_dimensions_estimated':True};bm.free();assert report['nonmanifold_edges']==0 and report['volume_m3']>0 and report['minimum_triangle_area_m2']>1e-18
ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'head-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'head-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2))
