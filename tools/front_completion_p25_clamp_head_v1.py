"""PF121026-photo related exposed fork cap; no hidden threaded shank."""
import bpy,bmesh,math,json
from pathlib import Path
R=Path('/workspace/wewa');key='front-completion-p25-clamp-head-v1';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
P={'reference': 'Matriz PF121026 lower bridge front-facing exposed hex bolt head and circular rim; D04 related M10 label is not a head dimension', 'private_photo': '/workspace/wewa-assets/references/front-completion-p25/fork.jpg', 'all_dimensions_estimated': True, 'head_across_flats_m': 0.017, 'head_AF_bounds_m': [0.014, 0.02], 'rim_radius_m': 0.0105, 'rim_radius_bounds_m': [0.0085, 0.0125], 'exposed_height_m': 0.0065, 'height_bounds_m': [0.004, 0.009], 'frame': 'Isolated +Z outward bolt axis; no mounted placement', 'circular_rim_identity': 'Could be separate washer or integral flange; one exterior envelope only, not a proven fused manufactured part', 'hidden_shank_thread_and_clamping_faces': 'excluded; plain base review closure only', 'grade_markings': 'unreadable; none invented', 'current_RDC_identity': False}
(H/'parameters.json').write_text(json.dumps(P,indent=2));profile=[(0,.0100,'circle'),(.0003,.0105,'circle'),(.0010,.0105,'circle'),(.0014,.0100,'circle'),(.0014,.0085,'hex'),(.0058,.0085,'hex'),(.0065,.0081,'hex')];n=384;v=[];f=[]
for z,r,kind in profile:
 for j in range(n):
  a=2*math.pi*j/n;rr=r/math.cos((a+math.pi/6)%(math.pi/3)-math.pi/6)if kind=='hex'else r;v.append((rr*math.cos(a),rr*math.sin(a),z))
for i in range(len(profile)-1):
 for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
for row,z,reverse in [(0,0,True),(len(profile)-1,.0065,False)]:
 c=len(v);v.append((0,0,z))
 for j in range(n):a=row*n+j;b=row*n+(j+1)%n;f.append((c,b,a)if reverse else(c,a,b))
m=bpy.data.meshes.new('Connected circular collar true hex flats and top chamfer');m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update();ob=bpy.data.objects.new('RELATED_VISIBLE_LOWER_CLAMP_BOLT_HEAD_ENVELOPE',m);bpy.context.collection.objects.link(ob)
for p in m.polygons:p.use_smooth=p.index<3*n
mat=bpy.data.materials.new('Gray form review');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.25,.25,.25,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.3;m.materials.append(mat)
bm=bmesh.new();bm.from_mesh(m);m.calc_loop_triangles();report={'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles),'hidden_shank_built':False,'all_dimensions_estimated':True};bm.free();assert report['nonmanifold_edges']==0 and report['volume_m3']>0 and report['minimum_triangle_area_m2']>1e-18
ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'clamp-head-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'clamp-head-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2))
