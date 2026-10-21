"""Finite actual-source lumen/hole rays; no installed or bolt fit certification."""
from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/front-footrest-right-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/('build-report.json'if'--final'in sys.argv else'geometry-report.json')).read_text());P=json.loads((H/'parameters.json').read_text());source=H/('front-footrest-right-v1.blend'if'--final'in sys.argv else'front-footrest-right-v1-geometry.blend');assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));o=bpy.data.objects[B['geometry'][0]['name']];m=o.data;m.calc_loop_triangles();tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True);rows=[]
def clear(label,start,axis,length):
 hit=tree.ray_cast(Vector(start),Vector(axis),length);row={'label':label,'origin_m':list(start),'direction':list(axis),'length_m':length,'hit':hit[0] is not None};rows.append(row);assert hit[0]is None,row
for j,(y,z)in enumerate(P['base_hole_YZ_m']):
 for dy,dz in [(0,0),(.002,0),(-.002,0),(0,.002),(0,-.002)]:clear('mount-hole-'+str(j),(-.020,y+dy,z+dz),(1,0,0),.060)
y,z=P['tube_YZ_m']
for dy,dz in [(0,0),(.004,0),(-.004,0),(0,.004),(0,-.004)]:clear('tube-visible-lumen',(.248,y+dy,z+dz),(-1,0,0),.225)
# Middle ear aperture excludes tube, which remains below the finite test interval.
for dx,dz in [(0,0),(.003,0),(-.003,0),(0,.003),(0,-.003)]:clear('middle-ear-eye',(.075+dx,.055,dz),(0,-1,0),.033)
# Outer saddle holes/slot are only pierced through saddle. Tube remains behind them.
for x in [*P['saddle_circle_X_m'],sum(P['saddle_slot_X_extent_m'])/2]:clear('saddle-opening-before-tube',(x,-.025,0),(0,1,0),.0133)
# Positive ring witnesses reject the previous wrongly oriented vertical-slot cutter.
solid_witnesses=[]
def solid(label,start,axis,length):
 hit=tree.ray_cast(Vector(start),Vector(axis),length);row={'label':label,'origin_m':list(start),'direction':list(axis),'length_m':length,'hit':hit[0]is not None};solid_witnesses.append(row);assert hit[0]is not None,row
for j in range(8):
 a=math.tau*j/8;solid('middle-eye-surrounding-annulus',(.075+.0105*math.cos(a),.055,.0105*math.sin(a)),(0,-1,0),.034)
for x in P['saddle_circle_X_m']:
 for j in range(8):
  a=math.tau*j/8;solid('saddle-circular-surrounding-annulus',(x+.0045*math.cos(a),-.025,.0045*math.sin(a)),(0,1,0),.0142)
for z in [-.0075,.0075]:solid('saddle-slot-long-side-remains',(.1725,-.025,z),(0,1,0),.016)
protected_tube=[]
for x in [*P['saddle_circle_X_m'],sum(P['saddle_slot_X_extent_m'])/2]:
 hit=tree.ray_cast(Vector((x,-.025,0)),Vector((0,1,0)),.025);assert hit[0]is not None;assert abs(hit[0].y+.011)<5e-6;protected_tube.append({'X_m':x,'actual_tube_surface_Y_m':hit[0].y,'saddle_cutter_did_not_drill_tube':True})
walls=[]
for j in range(4):
 a=math.tau*j/4;d=Vector((0,math.cos(a),math.sin(a)));start=Vector((.225,y,z));entry=tree.ray_cast(start,d,.03);assert entry[0]is not None;exit=tree.ray_cast(entry[0]+d*1e-6,d,.03);assert exit[0]is not None;th=(exit[0]-entry[0]).length;assert .0015<th<.0025;walls.append({'angle_rad':a,'sampled_radial_wall_m':th})
x={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':B['export_sha256'],'clear_rays':rows,'positive_ring_and_slot_witnesses':solid_witnesses,'tube_wall_samples':walls,'tube_protected_behind_saddle_openings':protected_tube,'scope':'23 finite clear rays through two base holes, tube lumen, middle eye and terminal saddle perforations before tube; three true outer tube surfaces remain behind saddle holes. Four positive radial wall samples. Hidden base closure is technical estimated; no frame, rubber, fastener diameter, weld strength or installed safety/clearance certified.','art_accepted':False};(O/'opening-envelope-check.json').write_text(json.dumps(x,indent=2)+'\n');assert sha(source)==B['source_sha256'];print(json.dumps(x))
