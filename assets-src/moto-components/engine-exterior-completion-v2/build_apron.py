import bpy,json,math,hashlib,bmesh,sys
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=Path('/workspace/wewa');P=json.loads((O/'G0-G2-apron-plan.json').read_text());source=R/'assets-src/moto-components/crankcase-lh-major-outer-envelope-donor-v1/child-candidate.blend';expected='3622f07d7d6b6aaef4f3b310470c88896715f020856c49c9a256310b31661085';assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
with bpy.data.libraries.load(str(source),link=False) as(a,b):b.objects=['MAJOR_LH_DONOR_EXTERIOR_PERIPHERAL_CAST_WALLS_OPEN_ENGINE_VOID']
body=b.objects[0];bpy.context.scene.collection.objects.link(body);body.hide_select=False;body.hide_viewport=False;body.hide_render=False;body.hide_set(False)
plan=json.loads((R/'creative/research/powertrain-completion-p18-v1/lh-major-outer-envelope-donor-plan-v97.json').read_text());C=[Vector(((x-350)*.00044,(550-y)*.00044))for x,y in plan['outline_controls_pixels_65221']]
curve=[]
for i in range(len(C)):
 for j in range(16):
  t=j/16;w=[(1-t)**3/6,(3*t**3-6*t*t+4)/6,(-3*t**3+3*t*t+3*t+1)/6,t**3/6];curve.append(sum((C[(i+k)%len(C)]*w[k]for k in range(4)),Vector((0,0))))
# Lower traced arc follows authored source perimeter exactly, away from cavity.
arc=[p+Vector((0,.001)) for p in curve if p.y<-.070 and -.115<p.x<.135]
# Preserve contour order rear->front (descending x around underside).
arc.sort(key=lambda p:p.x,reverse=True)
upper=[Vector(((x-350)*.00044,(550-y)*.00044))for x,y in P['upper_apron_edge_pixels']]
# End boundaries are within existing peripheral wall; no unseen corner added.
arc=[q for q in arc if upper[0].x<=q.x<=upper[-1].x]
pts=upper+arc
if sum(a.x*b.y-b.x*a.y for a,b in zip(pts,pts[1:]+pts[:1]))<0:pts.reverse()
N=len(pts);vs=[(p.x,p.y,z)for z in [-.007,0]for p in pts];faces=[tuple(reversed(range(N))),tuple(range(N,2*N))]
for i in range(N):j=(i+1)%N;faces.append((i,j,N+j,N+i))
me=bpy.data.meshes.new('Documented lower apron profile');me.from_pydata(vs,[],faces);me.update();apron=bpy.data.objects.new('Observed lower cast apron finite wall',me);bpy.context.scene.collection.objects.link(apron)
def recalc(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(ob.data);bm.free()
recalc(apron)
# Interior samples support a gentle source-observed broad cast crown, no flat closure disk.
bm=bmesh.new();bm.from_mesh(apron.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=2,use_grid_fill=True)
for v in bm.verts:
 if abs(v.co.z)>1e-8:continue
 q=Vector((v.co.x,v.co.y));distance=1e9
 for a,b in zip(pts,pts[1:]+pts[:1]):
  edge=b-a;t=max(0,min(1,(q-a).dot(edge)/max(edge.length_squared,1e-20)));distance=min(distance,(q-(a+t*edge)).length)
 v.co.z=-.0002+.0015*math.sin(min(1,distance/.012)*math.pi/2)**2
bm.to_mesh(apron.data);bm.free();recalc(apron)
# Round only finite plate contour; source perimeter remains original body.
bpy.context.view_layer.objects.active=apron;m=apron.modifiers.new('Bounded soft cast edge, not a weld','BEVEL');m.width=.0006;m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name)
def boolean(target,tool,label,operation):
 bpy.context.view_layer.objects.active=target;m=target.modifiers.new(label,'BOOLEAN');m.operation=operation;m.solver='EXACT';m.object=tool;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(tool,do_unlink=True)
me=apron.data;me.calc_loop_triangles();print('BEFORE CUT',len(me.vertices),len(me.loop_triangles),sum(me.vertices[t.vertices[0]].co.dot(me.vertices[t.vertices[1]].co.cross(me.vertices[t.vertices[2]].co))/6 for t in me.loop_triangles),flush=True)
(O/'apron-polygon.json').write_text(json.dumps([list(p)for p in pts]))
# Service opening is cut once in the combined casting to avoid coincident cylinder seams.
apron.data.calc_loop_triangles()
apron_vol=sum(apron.data.vertices[t.vertices[0]].co.dot(apron.data.vertices[t.vertices[1]].co.cross(apron.data.vertices[t.vertices[2]].co))/6 for t in apron.data.loop_triangles)
print('APRON PREUNION',len(apron.data.vertices),len(apron.data.loop_triangles),'VOLUME',apron_vol,'POLYGON AREA',sum(a.x*b.y-b.x*a.y for a,b in zip(pts,pts[1:]+pts[:1]))/2,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'apron-before-union-diagnostic.blend'),compress=True)
# Robust triangular solid operation; Blender exact attempt is retained as rejected evidence.
import numpy as np,subprocess,os
bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=.022,depth=.10,location=(-.07436,-.0924,0));tool=bpy.context.object;arrays={}
for key,ob in [('body',body),('apron',apron),('tool',tool)]:
 me=ob.data;me.calc_loop_triangles();arrays[key+'_v']=np.array([ob.matrix_world@v.co for v in me.vertices],dtype=np.float32);arrays[key+'_f']=np.array([list(t.vertices)for t in me.loop_triangles],dtype=np.uint32)
np.savez_compressed(O/'csg-inputs.npz',**arrays)
env=dict(os.environ,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',TBB_NUM_THREADS='2');subprocess.run(['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python',str(O/'csg_manifold.py')],check=True,env=env)
data=np.load(O/'csg-result.npz');new=bpy.data.meshes.new('Same donor completed cast apron manifold triangles');new.from_pydata(data['vertices'].tolist(),[],data['triangles'].tolist());new.update()
for mat in body.data.materials:new.materials.append(mat)
body.data=new
for ob in [apron,tool]:bpy.data.objects.remove(ob,do_unlink=True)
body.name='LH_JE541038_DONOR_PERIPHERY_AND_OBSERVED_LOWER_CAST_APRON';recalc(body)
# Remove numerical coincident and zero-area topology from the Boolean, without global remeshing.
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.dissolve_degenerate(bm,dist=1e-10,edges=bm.edges);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(body.data);bm.free();body.data.update();me=body.data;me.calc_loop_triangles()
for f in me.polygons:f.use_smooth=True
if hasattr(me,'set_sharp_from_angle'):me.set_sharp_from_angle(angle=math.radians(40))
# Retain proposed source cast material; do not package private source pixels.
body['scope']=P['scope'];body['variant']=P['variant'];body['source_parent_sha256']=expected
coll=bpy.data.collections.new('WEWA_LH_DONOR_LOWER_APRON_COMPLETION_V2');bpy.context.scene.collection.children.link(coll)
for c in list(body.users_collection):c.objects.unlink(body)
coll.objects.link(body);bpy.context.scene.unit_settings.system='METRIC'
from collections import Counter
edges=Counter(tuple(sorted((a,b)))for f in me.polygons for a,b in zip(f.vertices,list(f.vertices[1:])+[f.vertices[0]]));vol=sum(me.vertices[t.vertices[0]].co.dot(me.vertices[t.vertices[1]].co.cross(me.vertices[t.vertices[2]].co))/6 for t in me.loop_triangles);area=min(t.area for t in me.loop_triangles)
report=dict(vertices=len(me.vertices),triangles=len(me.loop_triangles),boundary_edges=sum(n==1 for n in edges.values()),branch_edges=sum(n>2 for n in edges.values()),volume_m3=vol,min_triangle_area_m2=area,source_parent_sha256=expected,boolean='Same casting union, no physical weld invented',photos=P['sources'],void_probes='Pending evaluated ray check',expected_open_engine_void=True)
(O/'apron-geometry-check.json').write_text(json.dumps(report,indent=2));assert report['boundary_edges']==report['branch_edges']==0 and vol>.00028 and area>1e-16,report
bpy.context.view_layer.objects.active=body;body.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'lh-donor-lower-apron-v2.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(O/'lh-donor-lower-apron-v2.glb'),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False,export_cameras=False,export_lights=False)
print(json.dumps(report))
