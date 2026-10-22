import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
col=bpy.data.collections.new('WEWA_ENGINE_UPPER_REAR_CAST_SHELL_V3');bpy.context.scene.collection.children.link(col)
# Each station is constrained by installed covers and the shoulder contour in RDC 04/00.
# World X lateral, Y rearward, Z up. Metres; bounded estimates, not measured OEM dimensions.
stations=[(.052,.018,-.606,-.635),(.060,.055,-.577,-.666),(.070,.078,-.553,-.685),(.095,.092,-.546,-.706),(.145,.100,-.540,-.716),(.185,.102,-.530,-.716),(.220,.102,-.514,-.708),(.265,.100,-.526,-.698),(.310,.094,-.550,-.681),(.340,.082,-.573,-.654),(.352,.067,-.590,-.638),(.362,.040,-.603,-.632),(.367,.012,-.614,-.623)]
# Rounded rectangular transverse loops; upper broad deck, rounded cast shoulders.
N=32;verts=[]
for inner in (False,True):
 for k,(y,w,top,bot) in enumerate(stations):
  if inner:
   thickness=min(.006,.3*(top-bot),.3*w)
   w-=thickness;top-=thickness;bot+=thickness
   if k==0:y+=min(thickness,.3*(stations[1][0]-stations[0][0]))
   if k==len(stations)-1:y-=min(thickness,.3*(stations[-1][0]-stations[-2][0]))
  assert w>0 and top>bot,(inner,k,w,top,bot)
  if inner:
   assert top<stations[k][2] and bot>stations[k][3] and w<stations[k][1]
   if k>0:assert y>verts[-N][1],('inner station reversal',k,y,verts[-N][1])
  mid=(top+bot)/2;h=(top-bot)/2
  for j in range(N):
   t=2*math.pi*j/N;c=math.cos(t);s=math.sin(t)
   left_extra=0
   lateral=w+left_extra if c>=0 else w
   verts.append((lateral*math.copysign(abs(c)**.8,c),y,mid+h*math.copysign(abs(s)**.8,s)))
L=len(stations);faces=[]
containment=[]
for k in range(L):
 loop=verts[L*N+k*N:L*N+(k+1)*N];y=loop[0][1]
 a=next(i for i in range(L-1) if stations[i][0]<=y<=stations[i+1][0]);f=(y-stations[a][0])/(stations[a+1][0]-stations[a][0])
 w,top,bot=[stations[a][j]*(1-f)+stations[a+1][j]*f for j in (1,2,3)]
 mid=(top+bot)/2;h=(top-bot)/2
 metric=max((abs(x)/w)**2.5+(abs(z-mid)/h)**2.5 for x,_,z in loop)
 assert metric<1,('inner outside outer envelope',k,metric)
 containment.append(dict(station=k,inner_y=y,max_superellipse_metric=metric))
(O/'inner-shell-containment.json').write_text(json.dumps(dict(method='Every inner section vertex inside interpolated outer rounded section; metric<1, strict positive inner widths/heights and monotone stations asserted',sections=containment),indent=2))
for side in range(2):
 off=side*L*N
 for k in range(L-1):
  for j in range(N):
   a=off+k*N+j;b=off+k*N+(j+1)%N;c=b+N;d=a+N
   faces.append((a,b,c,d) if not side else (d,c,b,a))
# Exterior end faces and inward cavity end faces: finite 6mm end walls.
for side in range(2):
 for k in (0,L-1):
  ids=[side*L*N+k*N+j for j in range(N)]
  faces.append(tuple(ids if (k==0)==(side==0) else reversed(ids)))
me=bpy.data.meshes.new('Photo_bounded_cast_shell_6mm');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('UPPER_REAR_CRANKCASE_EXTERIOR_CAST_SHELL_ESTIMATED',me);col.objects.link(ob)
bpy.context.view_layer.objects.active=ob;ob.select_set(True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
# Recalc orients disconnected shells independently. Explicitly turn cavity inward.
for p in me.polygons:
 if all(i>=L*N for i in p.vertices):p.flip()
 p.use_smooth=len(p.vertices)==4
me.update()
mat=bpy.data.materials.new('Neutral cast aluminium estimated');mat.diffuse_color=(.36,.39,.42,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.36,.39,.42,1);bs.inputs['Metallic'].default_value=.72;bs.inputs['Roughness'].default_value=.37;me.materials.append(mat)
ob['evidence']='Physical RDC 04/00 upper/rear crankcase contour; related JE541038 casting depth; no exact variant certification';ob['wall_thickness_estimate_m']=.006
bpy.ops.wm.save_as_mainfile(filepath=str(O/'upper-rear-cast-shell-v3.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(O/'upper-rear-cast-shell-v3.glb'),export_format='GLB',use_selection=True,export_extras=True)
me.calc_loop_triangles()
import bmesh
bm=bmesh.new();bm.from_mesh(me);checks=dict(vertices=len(me.vertices),triangles=len(me.loop_triangles),boundary_edges=sum(e.is_boundary for e in bm.edges),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),volume_m3=bm.calc_volume(signed=True),bounds=[[min(v.co[i] for v in me.vertices) for i in range(3)],[max(v.co[i] for v in me.vertices) for i in range(3)]])
outer=sum(f.calc_area()*f.normal.dot(f.calc_center_median())/3 for f in bm.faces if all(v.index<L*N for v in f.verts))
inner=sum(f.calc_area()*f.normal.dot(f.calc_center_median())/3 for f in bm.faces if all(v.index>=L*N for v in f.verts))
checks.update(outer_signed_volume_m3=outer,inner_signed_volume_m3=inner,net_material_volume_m3=outer+inner,bbox_volume_m3=math.prod(checks['bounds'][1][i]-checks['bounds'][0][i] for i in range(3)))
assert checks['nonmanifold_edges']==0 and outer>0 and inner<0 and 0<checks['volume_m3']<checks['bbox_volume_m3']
assert abs(checks['volume_m3']-(outer+inner))<1e-7
(O/'geometry-check.json').write_text(json.dumps(checks,indent=2));bm.free()
# Tiny linked diagnostic context; no historical source copies.
rows=json.loads((R/'assets-src/moto-components/engine-exterior-completion-v2/poses-and-sources.json').read_text())['parents']
for row in rows:
 with bpy.data.libraries.load(str(R/row['source']),link=True) as(a,b):b.objects=row['objects']
 c=bpy.data.collections.new('DIAG_'+row['key'])
 for obj in b.objects:c.objects.link(obj)
 inst=bpy.data.objects.new(row['key'],None);inst.instance_type='COLLECTION';inst.instance_collection=c;inst.matrix_world=Matrix(row['matrix']);bpy.context.scene.collection.objects.link(inst)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'diagnostic-linked-v3.blend'),compress=True)
print(checks)
