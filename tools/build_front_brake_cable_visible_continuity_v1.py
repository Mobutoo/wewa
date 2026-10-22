"""New visible upper-A extension only; old A/B native sources immutable."""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector
R=Path('/workspace/wewa');K='front-brake-cable-visible-continuity-v1';D=R/'creative/research'/K;H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
p=json.loads((D/'G0-G2-plan.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
col=bpy.data.collections.new('WEWA_FRONT_BRAKE_CABLE_VISIBLE_CONTINUITY_V1');bpy.context.scene.collection.children.link(col)
s=p['mm_per_px']/1000;ctrl=[Vector((0,(x-255)*s,(510-y)*s)) for x,y in p['trace_pixels']];pts=[]
for i in range(len(ctrl)-1):
 q0=ctrl[max(0,i-1)];q1=ctrl[i];q2=ctrl[i+1];q3=ctrl[min(len(ctrl)-1,i+2)]
 for j in range(12):
  t=j/12;pts.append(.5*((2*q1)+(-q0+q2)*t+(2*q0-5*q1+4*q2-q3)*t*t+(-q0+3*q1-3*q2+q3)*t*t*t))
pts.append(ctrl[-1]);v=[];f=[];N=32;r=.00275;g=.0005
for i,c in enumerate(pts):
 tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();u=Vector((1,0,0));w=tangent.cross(u).normalized()
 for rr in [r,r-g]:
  for j in range(N):a=2*math.pi*j/N;v.append(tuple(c+rr*(u*math.cos(a)+w*math.sin(a))))
for i in range(len(pts)-1):
 for j in range(N):
  k=(j+1)%N
  for layer in [0,1]:
   q=[i*2*N+layer*N+j,i*2*N+layer*N+k,(i+1)*2*N+layer*N+k,(i+1)*2*N+layer*N+j]
   if layer:q.reverse()
   f.extend([(q[0],q[1],q[2]),(q[0],q[2],q[3])])
# Upper is a diagnostic annular review cut. No lower cap: existingA keeps its cap.
i=len(pts)-1
for j in range(N):
 k=(j+1)%N;q=[i*2*N+j,i*2*N+N+j,i*2*N+N+k,i*2*N+k];f.extend([(q[0],q[1],q[2]),(q[0],q[2],q[3])])
# Preserve the actual originalA boundary orientation, including its tiny
# one-sided Catmull sampled-ring tilt, rather than assuming a perfectly level rim.
ring=json.loads((D/'actual-original-A-upper-ring.json').read_text());assert ring['source_sha256']=='c126e276c69114d5cf4f433862faf3b1526aba9987f35cea881418a968c226a9'
v[:64]=[tuple(p) for p in ring['actual_boundary_positions_local_m']]
m=bpy.data.meshes.new('Single newly observed continuation, no copied original route');m.from_pydata(v,[],f);m.update();ob=bpy.data.objects.new('P29_OBSERVED_A_UPPER_VISIBLE_CONTINUATION_ROLE_CONDITIONAL',m);col.objects.link(ob)
for face in m.polygons:face.use_smooth=True
for face in list(m.polygons)[-2*N:]:face.use_smooth=False
import bmesh
bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
mat=bpy.data.materials.new('Visible black cable polymer estimated');mat.use_nodes=True;b=mat.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.009,.011,.012,1);b.inputs['Roughness'].default_value=.43;m.materials.append(mat)
bpy.context.scene.unit_settings.system='METRIC';ob.select_set(True);bpy.context.view_layer.objects.active=ob
src=H/'visible-continuation-v1.blend';glb=H/'visible-continuation-v1.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
oldplan=json.loads((R/'creative/research/p29-lower-front-sheath-observed-a-v1/G0-G2.json').read_text());oldsrc=R/'assets-src/moto-components/p29-lower-front-sheath-observed-a-v1/sheath-material.blend';assert sha(oldsrc)=='c126e276c69114d5cf4f433862faf3b1526aba9987f35cea881418a968c226a9'
old=json.loads((R/'creative/reviews/whole-exterior-coverage-v20/linked-parents-check.json').read_text());parent=next(x for x in old['parents'] if x['key']=='observed-lower-sheath-a')
row={'key':'observed-front-sheath-a-upper-extension','source':str(src.relative_to(R)),'sha256':sha(src),'collection':col.name,'selected_objects':[],'translation_m':parent['translation_m'],'rotation_degrees':[0,0,0],'scale':[1,1,1],'placement_status':'Same recorded parent frame as existing observed-A; only upper newly observed portion; brake role conditional','nested_sources':[],'renderable_meshes':1}
frag={'revision':K,'baseline_parent_count':len(old['parents']),'result_parent_count':len(old['parents'])+1,'additions':[row],'replacements':[],'no_old_route_duplicated':True,'old_sources_unchanged':True,'glb':str(glb.relative_to(R)),'glb_sha256':sha(glb),'complete_control_to_JA_lever_cable':False,'hidden_route_created':False,'physical_part_increment':0}
(O/'integration-fragment.json').write_text(json.dumps(frag,indent=2)+'\n');(H/'parameters.json').write_text(json.dumps(p,indent=2)+'\n')
(O/'construction-check.json').write_text(json.dumps({'source_sha256':sha(src),'vertices':len(v),'triangles':len(f),'sampled_centerline_local_m':[list(x) for x in pts],'start_center_local_m':list(pts[0]),'end_center_local_m':list(pts[-1]),'radius_m':r,'newly_observed_length_m':sum((b-a).length for a,b in zip(pts,pts[1:])),'old_A_source_sha256_unchanged':sha(oldsrc),'no_new_lower_cap':True,'shape_not_full_factory_cable':True},indent=2))
