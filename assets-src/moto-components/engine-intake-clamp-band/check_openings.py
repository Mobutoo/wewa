"""Actual retained band/rims, finite lug holes and witnesses. No complete screw/bridge or rigid fit asserted."""
from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-clamp-band-v1';final='--final'in sys.argv;B=json.loads((H/('build-report.json'if final else'geometry-report.json')).read_text());P=json.loads((H/'parameters.json').read_text());source=H/('engine-intake-clamp-band-v1.blend'if final else'engine-intake-clamp-band-v1-geometry.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));o=bpy.data.objects[B['geometry'][0]['name']];m=o.data;m.calc_loop_triangles();tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True)
assert tree.ray_cast(Vector((0,0,.020)),Vector((0,0,-1)),.040)[0]is None
assert tree.ray_cast(Vector((0,-.040,0)),Vector((0,1,0)),.025)[0]is None
rows=[];e=B['working_ear_X_abs_m'];Y=P['working_ear_hole_Y_m']
for sign in [-1,1]:
 x=sign*e;centre=Vector((x,Y,0));direction=Vector((1,0,0));assert tree.ray_cast(centre-Vector((.002,0,0)),direction,.004)[0]is None;witness=[]
 for dy,dz in [(0,.0035),(0,-.0035),(.0035,0),(-.0035,0)]:
  start=centre+Vector((-.002,dy,dz));a=tree.ray_cast(start,direction,.004)[0];assert a is not None;z=tree.ray_cast(centre+Vector((.002,dy,dz)),-direction,.004)[0];assert z is not None;thick=abs(z.x-a.x);assert .0003<thick<.0008;witness.append({'offsetYZ_m':[dy,dz],'true_finite_axisX_entry_m':list(a),'true_finite_axisX_exit_m':list(z),'actual_crossing_thickness_m':thick})
 rows.append({'lug_X_m':x,'finite_axisX_hole_clear':True,'positive_surrounding_material_witnesses':witness})
radial=[];step=math.radians(300/P['main_arc_samples']);error=(P['working_radius_inner_m']+P['working_thickness_m'])*(1-math.cos(step/2))+1e-7
for degrees in [0,45,90,135,180]:
 a=math.radians(degrees);d=Vector((math.cos(a),math.sin(a),0));inner=tree.ray_cast(Vector((0,0,0)),d,.04)[0];outer=tree.ray_cast(d*.04,-d,.04)[0];assert inner is not None and outer is not None;ri=math.hypot(inner.x,inner.y);ro=math.hypot(outer.x,outer.y);assert abs(ri-P['working_radius_inner_m'])<error and abs(ro-(P['working_radius_inner_m']+P['working_thickness_m']))<error;radial.append({'angle_degrees':degrees,'inner_radius_m':ri,'outer_radius_m':ro,'working_nominal_comparison_bound_from_polygon_sagitta_m':error})
q={'source_sha256':sha(source),'export_sha256':B['export_sha256'],'centre_axial_ray_clear':True,'front_gap_finite_ray_clear':True,'two_lug_hole_rows':rows,'band_radial_actual_samples':radial,'automatic_attachment_allowed':False,'scope':'Actual retained mesh finite rays and material witnesses; not screw engagement, complete clamp, sleeve compliance or currentRDC dimensions. Working loop radius compared with its own sagitta bound, no photo calibration.','art_accepted':False};(O/'opening-envelope-check.json').write_text(json.dumps(q,indent=2)+'\n');assert sha(source)==B['source_sha256'];print('CLAMP_BAND_OPENINGS',json.dumps(q),flush=True)
