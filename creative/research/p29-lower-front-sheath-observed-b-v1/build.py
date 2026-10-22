# Reused protocol source SHA256 0f342f6853e51342e3569c2eeabbe2ceb0f1711c6bad0f2597bc56b42aa0b296; own namespace/observed controls.
"""One bounded visible sleeve only; no mechanical endpoints or hidden route."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');K='p29-lower-front-sheath-observed-b-v1';D=R/'creative/research'/K;H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;p=json.loads((D/'G0-G2.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
col=bpy.data.collections.new('P29_LOWER_FRONT_SHEATH_OBSERVED_B');bpy.context.scene.collection.children.link(col);root=bpy.data.objects.new('P29_LOWER_SHEATH_REVIEW_ROOT',None);col.objects.link(root)
s=p['G2']['mm_per_pixel']/1000;trace=p['trace_pixels'];a,b=trace[0];ctrl=[Vector((0,(x-a)*s,(b-y)*s))for x,y in trace];pts=[]
for i in range(len(ctrl)-1):
 q0=ctrl[max(0,i-1)];q1=ctrl[i];q2=ctrl[i+1];q3=ctrl[min(len(ctrl)-1,i+2)]
 for j in range(12):
  t=j/12;pts.append(.5*((2*q1)+(-q0+q2)*t+(2*q0-5*q1+4*q2-q3)*t*t+(-q0+3*q1-3*q2+q3)*t*t*t))
pts.append(ctrl[-1]);verts=[];faces=[];N=32;r=.0025;g=.0005
for i,v in enumerate(pts):
 tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();u=Vector((1,0,0));w=tangent.cross(u).normalized()
 for radius in [r,r-g]:
  for j in range(N):verts.append(tuple(v+radius*(u*math.cos(2*math.pi*j/N)+w*math.sin(2*math.pi*j/N))))
for i in range(len(pts)-1):
 for j in range(N):
  k=(j+1)%N
  for layer in [0,1]:
   f=[i*2*N+layer*N+j,i*2*N+layer*N+k,(i+1)*2*N+layer*N+k,(i+1)*2*N+layer*N+j]
   if layer:f.reverse()
   faces.extend([(f[0],f[1],f[2]),(f[0],f[2],f[3])])
for i,reverse in [(0,True),(len(pts)-1,False)]:
 for j in range(N):
  k=(j+1)%N;f=[i*2*N+j,i*2*N+N+j,i*2*N+N+k,i*2*N+k]
  if reverse:f.reverse()
  faces.extend([(f[0],f[1],f[2]),(f[0],f[2],f[3])])
mesh=bpy.data.meshes.new('Observed sleeve bounded static annular mesh');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Observed lower front sheath B - function unassigned - review cuts',mesh);col.objects.link(ob);ob.parent=root
for f in mesh.polygons:f.use_smooth=True
# Annular cut faces are flat, visibly distinct from a real termination.
for f in list(mesh.polygons)[-4*N:]:f.use_smooth=False
m=bpy.data.materials.new('Review gray');m.diffuse_color=(.22,.22,.22,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.22,.22,.22,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.4;mesh.materials.append(m)
bpy.context.scene.unit_settings.system='METRIC';ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.wm.save_as_mainfile(filepath=str(H/'sheath-gray.blend'),compress=True)
# Explicit ring edge incidence and source-axis profile correspondence.
from collections import Counter
edges=Counter(tuple(sorted((f[i],f[(i+1)%3])))for f in faces for i in range(3));assert set(edges.values())=={2}
report={'vertices':len(verts),'triangles':len(faces),'ring_count':len(pts),'mesh_edge_incidence_two':True,'source_control_pixels':trace,'source_control_points_local_m':[list(v)for v in ctrl],'sampled_centerline_local_m':[list(v)for v in pts],'radius_m':r,'estimated_wall_m':g,'review_cuts_not_fittings':True,'single_observed_span':True,'function':'unassigned','new_hidden_mechanism':False,'protocol_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'fit_qualified':False,'art_accepted':False};(O/'geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
