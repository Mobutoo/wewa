"""DH161066 attributed side-stand spring, continuous wire with opposed open J hooks."""
import bpy,math,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import finish_source
from powertrain_continuation_sweep_v3 import round_wire,bezier,line
R=Path(__file__).resolve().parents[1];name='side-stand-return-spring-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
radius=.0045;wire=.0018;span=.029;turns=14.5;tail=.0355;tip=.0285;transition=.010;control=.0045;N=math.ceil(turns*64);path=[]
path+=line((-radius,-tip,0),(-radius,-tail,0))
path+=[Vector((radius*math.cos(a),-tail+radius*math.sin(a),0))for a in [math.pi+math.pi*i/64 for i in range(65)]]
path+=line((radius,-tail,0),(radius,-span/2-transition,0))
t0=Vector((0,span,math.tau*turns*radius)).normalized();start=Vector((radius,-span/2,0));p0=Vector((radius,-span/2-transition,0));path+=bezier(p0,p0+Vector((0,transition/2,0)),start-t0*control,start)
path+=[Vector((radius*math.cos(a),-span/2+span*i/N,radius*math.sin(a)))for i,a in [(i,math.tau*turns*i/N)for i in range(N+1)]]
end=path[-1];t1=Vector((0,span,-math.tau*turns*radius)).normalized();p3=Vector((-radius,span/2+transition,0));path+=bezier(end,end+t1*control,p3-Vector((0,transition/2,0)),p3)
path+=line((-radius,span/2+transition,0),(-radius,tail,0))
path+=[Vector((radius*math.cos(a),tail+radius*math.sin(a),0))for a in [math.pi-math.pi*i/64 for i in range(65)]]
path+=line((radius,tail,0),(radius,tip,0))
P={'schema':1,'package':'P17','component_id':'MOTO-SIDE-STAND-RETURN-SPRING-001','source':'creative/research/powertrain-completion-p17-v1/side-return-spring-plan-v6.json','mean_coil_radius_m':radius,'wire_diameter_m':wire,'helical_span_m':span,'helical_turn_span':turns,'turn_span_range':[13,17],'working_pitch_m':span/turns,'working_coil_gap_m':span/turns-wire,'hook_radius_m':radius,'working_tail_hook_center_y_m':tail,'open_tip_y_m':tip,'all_dimensions_estimated':True,'camera_calibrated':False,'scope':'DH161066 related-part exterior spring study, continuous round wire, opposed open J hooks and rounded tail transitions. Turn span/hand, free length, hook planes and wire/coil dimensions estimated. Numerical intercoil gap prevents overlap and is not a measured rest gap. Spring rate/preload/material and actual pin/frame installation unqualified; other stand parts excluded.','material':{'name':'Proposed dark metal spring finish','base_color_linear':[.028,.024,.020,1],'metallic':.7,'roughness':.34},'package_complete':False,'art_accepted':False}
P['tail_transition_span_m']=transition;P['tail_transition_control_m']=control
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);ob,report=round_wire('SIDE_STAND_SPRING_CONTINUOUS_WIRE_OPPOSED_OPEN_HOOKS',path,wire/2);(O/'centerline-clearance-check.json').write_text(json.dumps(report,indent=2)+'\n');ob['scope']=P['scope'];finish_source(H,O,P)
