"""True cone/hex intersection chamfers with freshly authored corner normals."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');key='front-completion-p09-nut-v3';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
P={'reference':'PF401002-173209 visible mounting nut exterior, related-photo study','all_dimensions_estimated':True,'across_flats_m':.014,'bounds_m':[.011,.018],'height_m':.0052,'height_bounds_m':[.003,.008],'bore_radius_m':.0045,'bore_bounds_m':[.003,.006],'end_outer_radius_m':.0068,'chamfer_radial_slope':1.7,'hidden_thread':'excluded; smooth open bore is estimated continuation only','frame':'isolated X axis, no mounted fit','change':'True conical surfaces cut by hex planes; replaces invalid circle/hex radial loft shading in v1/v2'}
(H/'parameters.json').write_text(json.dumps(P,indent=2));n=384;L=.0052;S=1.7
hexr=lambda a:.007/math.cos((a+math.pi/6)%(math.pi/3)-math.pi/6)
xcut=lambda a:(hexr(a)-.0068)/S
rings=[lambda a:(0,.0049),lambda a:(0,.0068)];tags=['front']
for i in range(1,33):
 t=i/32;rings.append(lambda a,t=t:(t*xcut(a),.0068+S*t*xcut(a)));tags.append('cone_front')
rings.append(lambda a:(L-xcut(a),hexr(a)));tags.append('hex')
for i in range(1,33):
 t=1-i/32;rings.append(lambda a,t=t:(L-t*xcut(a),.0068+S*t*xcut(a)));tags.append('cone_back')
rings.extend([lambda a:(L,.0049),lambda a:(L-.0004,.0045),lambda a:(.0004,.0045)]);tags.extend(['back','bore_back','bore']);tags.append('bore_front');assert len(tags)==len(rings)
v=[];f=[];kinds=[]
for ring in rings:
 for j in range(n):a=2*math.pi*j/n;x,r=ring(a);v.append((x,r*math.cos(a),r*math.sin(a)))
for i in range(len(rings)):
 for j in range(n):a=i*n+j;b=i*n+(j+1)%n;c=((i+1)%len(rings))*n+(j+1)%n;d=((i+1)%len(rings))*n+j;f.append((a,b,c,d));kinds.append(tags[i])
m=bpy.data.meshes.new('Exact conical chamfer and true hex flats parameterized intersection');m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update();custom=[]
for p,kind in zip(m.polygons,kinds):
 p.use_smooth=True
 # A hex face is constant across its planar sector; use face midpoint angle.
 ids=list(p.vertices);mean=Vector((0,0,0))
 for idx in ids:mean+=m.vertices[idx].co
 face_angle=math.atan2(mean.z,mean.y);flat=round(face_angle/(math.pi/3))*(math.pi/3)
 for li in p.loop_indices:
  idx=m.loops[li].vertex_index;a=2*math.pi*(idx%n)/n;c,s=math.cos(a),math.sin(a)
  nn={'front':(-1,0,0),'back':(1,0,0),'cone_front':(-S,c,s),'cone_back':(S,c,s),'hex':(0,math.cos(flat),math.sin(flat)),'bore':(0,-c,-s),'bore_front':(-1,-c,-s),'bore_back':(1,-c,-s)}[kind];custom.append(Vector(nn).normalized())
m.normals_split_custom_set(custom);m.update();ob=bpy.data.objects.new('INDICATOR_MOUNT_NUT_CONE_HEX_RELATED_STUDY',m);bpy.context.collection.objects.link(ob);mat=bpy.data.materials.new('Gray before material');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.25,.25,.25,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.3;m.materials.append(mat)
bm=bmesh.new();bm.from_mesh(m);m.calc_loop_triangles();report={'triangles':len(m.loop_triangles),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles),'minimum_corner_face_normal_dot':min(m.corner_normals[li].vector.dot(p.normal)for p in m.polygons for li in p.loop_indices),'normals':'Fresh analytical cones, planes, cylinder and bore chamfer normals in source; no buffer edits','all_dimensions_estimated':True};bm.free();assert report['nonmanifold_edges']==0 and report['volume_m3']>0 and report['minimum_triangle_area_m2']>1e-18 and report['minimum_corner_face_normal_dot']>0
ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'nut-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'nut-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2))
