"""Original visible DJ151034 outer skin only; no inferred bore, end annulus, wall or stack."""
import bpy,math,json,runpy
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p23-collar-outer-front12-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));N=256;L=.036;radius=.010;edge=.00015;profile=[]
# Two observed exterior edge breaks only; open limiting rings are intentional review cuts.
for i in range(13):
 a=math.pi/2*i/12;profile.append((-L/2+edge*(1-math.cos(a)),radius-edge+edge*math.sin(a)))
for i in range(1,5):profile.append((-L/2+edge+(L-2*edge)*i/4,radius))
for i in range(1,13):
 a=math.pi/2*i/12;profile.append((L/2-edge+edge*math.sin(a),radius-edge+edge*math.cos(a)))
v=[(x,r*math.cos(2*math.pi*j/N),r*math.sin(2*math.pi*j/N))for x,r in profile for j in range(N)];f=[]
for i in range(len(profile)-1):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.append((a,b,b+N,a+N))
ob=u['mesh_object']('DJ151034_VISIBLE_OUTER_SKIN_ONLY_TWO_OPEN_REVIEW_CUTS',v,f);audit=u['clean_audit'](ob,expected_boundary=2*N)
# Orient by radial sign, since this open skin has no signed solid volume.
if sum(p.normal.y*p.center.y+p.normal.z*p.center.z for p in ob.data.polygons)<0:
 for p in ob.data.polygons:p.flip()
 ob.data.update()
normals=[]
for p in ob.data.polygons:
 for li in p.loop_indices:
  c=ob.data.vertices[ob.data.loops[li].vertex_index].co;x=c.x;r=math.hypot(c.y,c.z)
  if x<-L/2+edge-1e-9:n=((x-(-L/2+edge))/edge,(r-(radius-edge))/edge*c.y/r,(r-(radius-edge))/edge*c.z/r)
  elif x>L/2-edge+1e-9:n=((x-(L/2-edge))/edge,(r-(radius-edge))/edge*c.y/r,(r-(radius-edge))/edge*c.z/r)
  else:n=(0,c.y/r,c.z/r)
  normals.append(n)
ob.data.normals_split_custom_set(normals);ob.data.update();P={'package':'P23','code':'DJ151034','scope':'Observed exterior cylindrical skin only, two intentional open axial review cuts. No end face, internal bore, wall thickness or installed stack fabricated.','axis':'X along isolated collar; no installed pose','working_dimensions_m':{'length':L,'outer_radius':radius,'edge_break':edge},'estimated_bounds_m':{'length':[.028,.048],'outer_radius':[.008,.013],'edge_break':[.00005,.0003]},'basis':'Single physical pose constrains outer length/diameter proportion only; no measurements. Two exposures are not opposite views.','all_dimensions_estimated':True,'internal_hole':'Unresolved, not modelled; empty review openings are not a specified bore','material':'Uniform clean silver hypothesis, no plating, scratches or cast grain measurement'};(H/'parameters.json').write_text(json.dumps(P,indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'intentional_open_boundary_loops':2,'not_a_closed_solid':True,'bore_or_wall_claimed':False},indent=2));u['gray_save'](H,'collar',[ob]);print(audit)
