"""PF401002-photo related visible mount nut; no hidden thread specification."""
import bpy,bmesh,math,json
from pathlib import Path
R=Path('/workspace/wewa');H=R/'assets-src/moto-components/front-completion-p09-nut-v1';O=R/'creative/reviews/front-completion-p09-nut-v1';H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
P={'reference':'PF401002-173209 photo: bright exposed polygonal mounting fastener at stem mounting end','all_dimensions_estimated':True,'across_flats_m':.014,'across_flats_bounds_m':[.011,.018],'height_m':.0052,'height_bounds_m':[.003,.008],'bore_radius_m':.0045,'bore_bounds_m':[.003,.006],'chamfer_axial_m':.00065,'frame':'isolated X axis, no mounted pose','hidden_thread':'not established; plain open bore for review only','photo':'/workspace/wewa-assets/references/front-indicators-current-v1/PF401002-173209.jpg','current_RDC_identity':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2));n=384
# Connected cross-section: two chamfered annular faces, six true flats,
# plain internal continuation explicitly excluded from thread fidelity.
profile=[(0,.0049,'circle'),(0,.0068,'circle'),(.00065,.007,'hex'),(.00455,.007,'hex'),(.0052,.0068,'circle'),(.0052,.0049,'circle'),(.0048,.0045,'circle'),(.0004,.0045,'circle')]
v=[];f=[]
for x,r,kind in profile:
 for j in range(n):
  a=2*math.pi*j/n;radius=r/math.cos((a+math.pi/6)%(math.pi/3)-math.pi/6) if kind=='hex' else r;v.append((x,radius*math.cos(a),radius*math.sin(a)))
for i in range(len(profile)):
 for j in range(n):a=i*n+j;b=i*n+(j+1)%n;c=((i+1)%len(profile))*n+(j+1)%n;d=((i+1)%len(profile))*n+j;f.append((a,b,c,d))
m=bpy.data.meshes.new('Connected authored six-flat mount nut section');m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
ob=bpy.data.objects.new('INDICATOR_VISIBLE_MOUNT_NUT_RELATED_STUDY',m);bpy.context.collection.objects.link(ob)
uv=m.uv_layers.new(name='Original source coordinates')
for p in m.polygons:
 p.use_smooth=False
 for li in p.loop_indices:
  idx=m.loops[li].vertex_index;uv.data[li].uv=(idx%n/n,idx//n/len(profile))
mat=bpy.data.materials.new('Neutral gray before material');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.25,.25,.25,1);bs.inputs['Roughness'].default_value=.3;m.materials.append(mat)
bm=bmesh.new();bm.from_mesh(m);m.calc_loop_triangles();report={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True),'triangles':len(m.loop_triangles),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles),'smooth_bore_not_thread':True,'all_dimensions_estimated':True};bm.free();assert report['nonmanifold_edges']==0 and report['volume_m3']>0 and report['minimum_triangle_area_m2']>1e-18
ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'nut-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'nut-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2))
