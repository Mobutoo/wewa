import bpy,json,struct,hashlib,collections,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'upper-rear-cast-shell-v3.blend'));src=next(o for o in bpy.context.scene.objects if o.type=='MESH');vs=sorted(tuple(round(v.co[i],6) for i in range(3)) for v in src.data.vertices);src.data.calc_loop_triangles();nt=len(src.data.loop_triangles)
native_triangles=collections.Counter(tuple(sorted(tuple(round(src.data.vertices[i].co[j],6) for j in range(3)) for i in t.vertices)) for t in src.data.loop_triangles)
native_exact={tuple(round(v.co[j],6) for j in range(3)):tuple(v.co) for v in src.data.vertices}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(O/'upper-rear-cast-shell-v3.glb'));ob=next(o for o in bpy.context.scene.objects if o.type=='MESH');actual=sorted(set(tuple(round((ob.matrix_world@v.co)[i],6) for i in range(3)) for v in ob.data.vertices));assert sorted(set(vs))==actual
ob.data.calc_loop_triangles();assert len(ob.data.loop_triangles)==nt
exported_triangles=collections.Counter(tuple(sorted(tuple(round((ob.matrix_world@ob.data.vertices[i].co)[j],6) for j in range(3)) for i in t.vertices)) for t in ob.data.loop_triangles)
assert exported_triangles==native_triangles
max_error=max(math.dist(native_exact[tuple(round((ob.matrix_world@v.co)[j],6) for j in range(3))],tuple(ob.matrix_world@v.co)) for v in ob.data.vertices)
assert max_error<1e-7
# Exterior occupancy rays on deck and rear; frame-space probes must miss.
probes=[]
for label,p,d,expected in [('rear-deck',(0,.265,-.45),(0,0,-1),True),('cylinder-landing',(0,.145,-.50),(0,0,-1),True),('rear-wall',(0,.40,-.615),(0,-1,0),True),('frame-above',(0,.30,-.45),(0,1,0),False),('behind-case',(0,.39,-.55),(0,0,-1),False)]:
 hit,loc,n,idx=ob.ray_cast(ob.matrix_world.inverted()@Vector(p),ob.matrix_world.inverted().to_3x3()@Vector(d),distance=.5);assert hit==expected,(label,hit);probes.append(dict(label=label,origin=p,direction=d,expected=expected,hit=hit,location=list(ob.matrix_world@loc) if hit else None))
r=dict(native_glb_unique_positions_equal_1um=True,triangle_coordinate_multiset_equal_1um=True,max_vertex_error_m=max_error,triangles=nt,probes=probes,files={n:dict(bytes=(O/n).stat().st_size,sha256=hashlib.sha256((O/n).read_bytes()).hexdigest()) for n in ['upper-rear-cast-shell-v3.blend','upper-rear-cast-shell-v3.glb']})
(O/'export-parity-and-occupancy.json').write_text(json.dumps(r,indent=2));print(r)
