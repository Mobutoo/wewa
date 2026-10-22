import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'assets-src/moto-components/chassis-interior-completion-v1/kit-linked-v2.blend'))
framev=[];framef=[];frames=[];dg=bpy.context.evaluated_depsgraph_get()
for ins in dg.object_instances:
 if not ins.is_instance or ins.object.type!='MESH':continue
 ob=ins.object
 if not any(t in ob.name.lower()for t in ['frame','seatmember','lowercradle','central curved','diagonal strut']):continue
 me=ob.to_mesh();me.calc_loop_triangles();base=len(framev);framev.extend(ins.matrix_world@v.co for v in me.vertices);framef.extend(tuple(base+i for i in t.vertices)for t in me.loop_triangles);frames.append(ob.name);ob.to_mesh_clear()
FB=BVHTree.FromPolygons(framev,framef,all_triangles=True)
# Read source LH/RH curves, calculate actual terminal aperture centres.
pars={s:json.loads((R/f'assets-src/moto-components/passenger-footrest-stay-{s}-v1/parameters.json').read_text())['shape_choices']for s in ['left','right']}
QL=Matrix(((0,0,1),(-2**-.5,-2**-.5,0),(2**-.5,-2**-.5,0)))
rows=[]
for side in ['left','right']:
 for clock in range(0,181,15):
  q=Matrix.Rotation(math.radians(clock),3,'X')@QL
  if side=='right':q=q@Matrix(((-1,0,0),(0,1,0),(0,0,-1)))
  anchor=Vector((-.006 if side=='left'else .004,.239,.0195));hinge=Vector((.10 if side=='left'else-.10,.65,-.555));tr=hinge-q@anchor;points={}
  for kind in ['long','short']:
   p=list(map(Vector,pars[side][kind+'_arm_bezier_source_m']));end=p[-1]+(p[-1]-p[-2]).normalized()*.001;world=q@end+tr;n=FB.find_nearest(world);points[kind]={'native':list(end),'world':list(world),'nearest_frame_point':list(n[0]),'distance_m':n[3],'frame_normal':list(n[1])}
  rows.append({'side':side,'clock_about_world_X_deg':clock,'matrix':[list(r)for r in q.to_4x4()],'translation':list(tr),'terminals':points,'max_terminal_distance':max(p['distance_m']for p in points.values())})
(O/'clocking-terminal-scan.json').write_text(json.dumps({'frames_evaluated':frames,'candidates':rows,'scope':'Actual surface nearest queries, not bolt identification or calibrated fit. Clock scan includes alternative donor-presentation interpretations, not accepted angle tolerance.'},indent=2))
for side in ['left','right']:
 print(side,[(r['clock_about_world_X_deg'],round(r['max_terminal_distance'],4),{k:round(v['distance_m'],4)for k,v in r['terminals'].items()})for r in rows if r['side']==side])
