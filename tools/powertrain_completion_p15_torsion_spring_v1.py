"""Original JV161014 pedal torsion spring; unequal tangent legs, not extension hooks."""
import bpy,math,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import finish_source
from powertrain_continuation_sweep_v3 import round_wire,bezier,line
R=Path(__file__).resolve().parents[1];name='brake-pedal-torsion-spring-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
radius=.016;wire=.003;span=.012;turns=3.25;long=.065;short=.022;tip=.010;bend=.008;N=math.ceil(turns*96);path=[]
y=-span/2
path+=line((radius-bend-tip,y,-long-bend),(radius-bend,y,-long-bend))
path+=[Vector((radius-bend+bend*math.cos(a),y,-long+bend*math.sin(a)))for a in [-math.pi/2+math.pi/2*i/48 for i in range(49)]]
path+=line((radius,y,-long),(radius,y,-.012))
start=Vector((radius,y,0));t0=Vector((0,span,math.tau*turns*radius)).normalized();a=Vector((radius,y,-.012));path+=bezier(a,a+Vector((0,0,.004)),start-t0*.004,start)
path+=[Vector((radius*math.cos(a),-span/2+span*i/N,radius*math.sin(a)))for i,a in [(i,math.tau*turns*i/N)for i in range(N+1)]]
end=path[-1];t1=Vector((-math.tau*turns*radius,span,0)).normalized();p3=end+Vector((-.012,0,0));path+=bezier(end,end+t1*.004,p3+Vector((.004,0,0)),p3)
path+=line(p3,end+Vector((-short,0,0)))
P=dict(schema=1,package='P15',component_id='MOTO-BRAKE-PEDAL-TORSION-SPRING-001',source='creative/research/powertrain-completion-p15-v1/pedal-torsion-spring-plan-v10.json',mean_coil_radius_m=radius,wire_diameter_m=wire,coil_span_m=span,turn_span=turns,turn_span_range=[2.75,4.0],long_tangent_leg_m=long,short_tangent_leg_m=short,terminal_bend_radius_m=bend,upturned_terminal_length_m=tip,tail_transition_m=.012,all_dimensions_estimated=True,scope='JV161014 separately referenced torsion spring with few large close coils, long tangent leg and rounded upturned end, and distinct shorter tangent leg. Rest angle/handedness/planes, exact turns, dimensions and end shapes estimated; no actual torque/preload/operating travel or pedal/pivot engagement qualification. Not 30191035 compression spring or stand return springs.',material=dict(name='Proposed warm plated pedal spring metal',base_color_linear=[.34,.24,.065,1],metallic=.8,roughness=.32),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);ob,report=round_wire('PEDAL_TORSION_SPRING_LARGE_COILS_UNEQUAL_LEGS_AND_UPTURN',path,wire/2);(O/'centerline-clearance-check.json').write_text(json.dumps(report,indent=2)+'\n');ob['scope']=P['scope'];finish_source(H,O,P)
