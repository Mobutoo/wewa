"""Separate visible head child; no hidden shaft or resolved drive type claimed."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/side-cover-left-v2';O=R/'creative/reviews/side-cover-left-v2';P=json.loads((H/'parameters-v2.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(H/'side-cover-left-gray-v2.blend'))
ob=bpy.data.objects['LEFT_COVER_OUTER_SKIN'];x=(525-568)*P['meters_per_pixel'];y=(359-391)*P['meters_per_pixel'];hit,loc,normal,index=ob.ray_cast(Vector((x,y,1)),Vector((0,0,-1)));assert hit
# Continuous revolved visible perimeter and face; unobtainable drive is intentionally unresolved.
profile=[(.000,0),(.0092,0),(.0103,.0006),(.0104,.0012),(.0098,.0018),(.0082,.0020),(.0078,.0026),(.0068,.0031),(.0030,.0034),(.000,.0034)]
V=[(0,0,profile[0][1])];F=[];N=128
for radius,z in profile[1:-1]:
 for i in range(N):
  a=2*math.pi*i/N;V.append((radius*math.cos(a),radius*math.sin(a),z))
for i in range(N):F.append((0,1+(i+1)%N,1+i))
for ring in range(len(profile)-3):
 a=1+ring*N;b=a+N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
top=len(V);V.append((0,0,profile[-1][1]));a=1+(len(profile)-3)*N
for i in range(N):F.append((a+i,a+(i+1)%N,top))
m=bpy.data.meshes.new('Photo bounded continuous fastener face');m.from_pydata(V,[],F);m.update();assert not m.validate()
head=bpy.data.objects.new('LEFT_COVER_VISIBLE_LOWER_FASTENER',m);bpy.context.scene.collection.objects.link(head);head.location=loc-normal*.0003;head.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
for f in m.polygons:f.use_smooth=True
mat=bpy.data.materials.new('Gray visible head review');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.3;m.materials.append(mat)
head['scope']='Visible perimeter/head only. Plain face represents unresolved drive; no hidden shaft, true recess or mounting compatibility.'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(H/'side-cover-left-head-gray-v2.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);head.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.gltf(filepath=str(H/'side-cover-left-head-gray-v2.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_tangents=False)
(O/'fastener-geometry-check.json').write_text(json.dumps(dict(center_pixels=[525,391],estimated_head_diameter_m=.0208,diameter_range_m=[.014,.025],projection_m=.0034,surface_hit=list(loc),surface_normal=list(normal),vertices=len(V),triangles=sum(len(f)-2 for f in F),drive_unresolved=True,hidden_fit_certified=False,art_accepted=False),indent=2)+'\n')
