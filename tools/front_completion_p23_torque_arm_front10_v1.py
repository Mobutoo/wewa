"""JW122004 bounded pressed exterior. Single missing child, not P15 actuator rod."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p23-torque-arm-front10-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(parents=True,exist_ok=False);O.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
P=json.loads((R/'creative/research/front-completion-p23-v1/torque-arm-G0-G2.json').read_text());P.update({'frame':'X long axis; Z photographed raised face; underside offset sheet hypothesis','left_hole_x_m':-.135,'right_hole_x_m':.132,'hole_positions_estimated':True,'reverse':'Estimated formed sheet continuation, not independently photographed','finish':'Uniform clean black coating estimate; no surface grain/wear/chemistry measurement','profile':'Bounded smooth longitudinal bead fading into flat broad asymmetric ears; no hidden bushing or reinforcing boss','all_metric_values_estimated':True});(H/'parameters.json').write_text(json.dumps(P,indent=2))
# Nonuniform longitudinal sampling resolves shoulders and cropped end chamfers.
xs=sorted(set([-.150+i*.300/400 for i in range(401)]+[-.148,-.146,-.132,-.116,-.100,.100,.116,.132,.144,.148]));NY=64;V=[]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def width(x):
 # Wide unequal ears and narrower pressed waist, shaped tips rather than rectangular bar.
 w=.008+.004*smooth((abs(x)-.097)/.024)
 if x<-.146:w-=.0015*smooth((-.146-x)/.004)
 if x>.144:w-=.004*smooth((x-.144)/.006)
 return w
for x in xs:
 w=width(x);fade=smooth((.119-abs(x))/.023)
 for j in range(NY+1):
  t=-1+2*j/NY;y=w*t
  # Broad continuous bead, two rounded shoulders, smoothly flat at sheet margins.
  q=min(1,abs(y)/.006);z=.0035*fade*(1-smooth(q))
  # Opposed asymmetric end trims are represented in X at the boundary station.
  xx=x
  if x<-.146:xx+=.0015*abs(t)**6*smooth((-.146-x)/.004)
  if x>.144:xx-=.0025*max(0,t)**2*smooth((x-.144)/.006)
  V.append((xx,y,z))
L=len(V);V += [(x,y,z-.0022)for x,y,z in V[:]];F=[];NX=len(xs)
for off,rev in [(0,False),(L,True)]:
 for i in range(NX-1):
  for j in range(NY):
   a=off+i*(NY+1)+j;f=(a,a+NY+1,a+NY+2,a+1);F.append(f[::-1]if rev else f)
loop=list(range(NY+1))+[i*(NY+1)+NY for i in range(1,NX)]+list(range((NX-1)*(NY+1)+NY-1,(NX-1)*(NY+1)-1,-1))+[i*(NY+1)for i in range(NX-2,0,-1)]
for a,b in zip(loop,loop[1:]+loop[:1]):F.append((a,b,b+L,a+L))
m=bpy.data.meshes.new('Dense continuous pressed sheet with two real ear holes');m.from_pydata(V,[],F);m.update();ob=bpy.data.objects.new('JW122004_RELATED_BEAD_STRAP_ESTIMATED_REVERSE',m);bpy.context.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob
for x,r in [(-.135,.0048),(.132,.004)]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=r,depth=.05,location=(x,0,0));c=bpy.context.object;bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Observed ear opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(c,do_unlink=True)
m=ob.data;bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-9);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-10);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
for p in m.polygons:p.use_smooth=True
bm=bmesh.new();bm.from_mesh(m);bm.edges.ensure_lookup_table()
for e in bm.edges:
 if e.is_manifold and e.calc_face_angle()>math.radians(40):m.edges[e.index].use_edge_sharp=True
report={'vertices':len(m.vertices),'triangles':len(m.polygons),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True),'minimum_triangle_area_m2':min(p.area for p in m.polygons),'all_metric_values_estimated':True,'two_real_apertures':True,'no_hidden_bushing':True,'reverse_sheet_estimated':True};bm.free();assert report['nonmanifold_edges']==0 and report['signed_volume_m3']>0 and report['minimum_triangle_area_m2']>1e-18
mat=bpy.data.materials.new('Gray form review');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.25,.25,.25,1);p.inputs['Roughness'].default_value=.3;m.materials.append(mat);bpy.context.scene.unit_settings.system='METRIC';bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.wm.save_as_mainfile(filepath=str(H/'torque-arm-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'torque-arm-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2));print(report)
