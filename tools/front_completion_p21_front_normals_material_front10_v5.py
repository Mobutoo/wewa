"""New source normals on the existing front exterior field. Positions/topology untouched; old freezes intact."""
import bpy,math,json,hashlib,shutil
from mathutils import Vector
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p21-front-material-front10-v5';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);old=R/'assets-src/moto-components/front-completion-p21-front-material-front10-v4';source=old/'carrier-material.blend';bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
records=[]
def field(x,y):
 r=math.hypot(x,y)
 if r<.028999:return None
 t=max(0,(.065-r)/.036);base=.025*t**1.4;dr=-.025*1.4/.036*t**.4 if t else 0.;w=0.;gx=gy=0.
 for a in [0,math.pi/2,math.pi,3*math.pi/2]:
  ca,sa=math.cos(a),math.sin(a);u=x*ca+y*sa;v=-x*sa+y*ca;du=u-min(.049,max(.032,u));rho=math.hypot(du,v);s=max(0,min(1,(.0125-rho)/.008));q=s*s*(3-2*s)
  if q>w:
   w=q
   if 1e-5<s<1-1e-5 and rho>1e-12:d=-6*s*(1-s)/.008;gu=d*du/rho;gv=d*v/rho;gx=gu*ca-gv*sa;gy=gu*sa+gv*ca
   else:gx=gy=0.
 h=base+(.027-base)*w;dx=(1-w)*dr*x/r+(.027-base)*gx;dy=(1-w)*dr*y/r+(.027-base)*gy
 return h,Vector((-dx,-dy,1)).normalized()
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 m=ob.data;m.update();oldnorms=[n.vector.copy()for n in m.corner_normals];fields=[field(v.co.x,v.co.y)for v in m.vertices];selected=set();flat=set()
 for f in m.polygons:
  if f.normal.z>0 and all(fields[i] is not None and abs(m.vertices[i].co.z-fields[i][0])<2e-6 for i in f.vertices):
   selected.add(f.index)
   if max(m.vertices[i].co.z for i in f.vertices)-min(m.vertices[i].co.z for i in f.vertices)<1e-10 and min(m.vertices[i].co.z for i in f.vertices)>.026999:flat.add(f.index)
 for f in m.polygons:
  if f.index in selected:f.use_smooth=f.index not in flat
 m.update();normals=[]
 for f in m.polygons:
  for li in f.loop_indices:normals.append(tuple(fields[m.loops[li].vertex_index][1]if f.index in selected else oldnorms[li]))
 m.normals_split_custom_set(normals);m.update();records.append({'object':ob.name,'analytic_field_faces':len(selected),'exact_flat_land_faces':len(flat),'positions_changed':False,'pocket_bore_thread_normals':'Original source normals retained outside top height field; re-encoding is checked in exported buffers'})
bpy.ops.object.select_all(action='DESELECT');objects=[o for o in bpy.data.objects if o.type=='MESH']
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0];shutil.copyfile(old/'roughness-original.png',H/'roughness-original.png');bpy.ops.wm.save_as_mainfile(filepath=str(H/'carrier-material.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'carrier-material.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
mat=bpy.data.materials.new('Gray exterior source normal review');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.25,.25,.25,1);bs.inputs['Roughness'].default_value=.3
for ob in objects:
 m=ob.data;m.materials.clear();m.materials.append(mat)
 for uv in list(m.uv_layers):m.uv_layers.remove(uv)
bpy.ops.wm.save_as_mainfile(filepath=str(H/'carrier-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'carrier-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
(O/'normal-method.json').write_text(json.dumps({'source':str(source.relative_to(R)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'Analytic derivative of original sampled front dish/capsule field on matching exterior faces; exact flat source shading on true horizontal lands','source_topology_and_positions_changed':False,'records':records,'G3_trigger':'v4 continuous scalar emission has no sawtooth but inherited highlight boundary remains dentellated','old_gray_and_G4_hold_modified':False,'art_accepted':False},indent=2));d=json.loads((R/'creative/reviews/front-completion-p21-front-material-front10-v4/material-plan.json').read_text());d['normal_revision']=str((O/'normal-method.json').relative_to(R));d['source_normals_changed']=True;d['original_scalar_image']=str((H/'roughness-original.png').relative_to(R));(O/'material-plan.json').write_text(json.dumps(d,indent=2));shutil.copyfile(R/'creative/reviews/front-completion-p21-front-material-front10-v4/detail-plan.json',O/'detail-plan.json');print(records)
