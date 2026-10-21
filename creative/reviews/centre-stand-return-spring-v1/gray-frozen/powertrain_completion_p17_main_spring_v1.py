"""DH161121 separately referenced main-stand spring with larger open hook returns."""
import bpy,math,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import finish_source
from powertrain_continuation_sweep_v3 import round_wire,bezier,line
R=Path(__file__).resolve().parents[1];name='centre-stand-return-spring-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
radius=.0045;wire=.002;span=.046;turns=21.5;hook=.0065;lower_tail=.042;upper_tail=.044;lower_tip=.0345;upper_tip=.037;transition=.012;control=.0052;N=math.ceil(turns*64);path=[]
lower_cx=radius-hook;upper_cx=hook-radius;lower_free=radius-2*hook;upper_free=2*hook-radius
path+=line((lower_free,-lower_tip,0),(lower_free,-lower_tail,0))
path+=[Vector((lower_cx+hook*math.cos(a),-lower_tail+hook*math.sin(a),0))for a in [math.pi+math.pi*i/72 for i in range(73)]]
path+=line((radius,-lower_tail,0),(radius,-span/2-transition,0))
t0=Vector((0,span,math.tau*turns*radius)).normalized();start=Vector((radius,-span/2,0));p0=Vector((radius,-span/2-transition,0));path+=bezier(p0,p0+Vector((0,transition/2,0)),start-t0*control,start)
path+=[Vector((radius*math.cos(a),-span/2+span*i/N,radius*math.sin(a)))for i,a in [(i,math.tau*turns*i/N)for i in range(N+1)]]
end=path[-1];t1=Vector((0,span,-math.tau*turns*radius)).normalized();p3=Vector((-radius,span/2+transition,0));path+=bezier(end,end+t1*control,p3-Vector((0,transition/2,0)),p3)
path+=line((-radius,span/2+transition,0),(-radius,upper_tail,0))
path+=[Vector((upper_cx+hook*math.cos(a),upper_tail+hook*math.sin(a),0))for a in [math.pi-math.pi*i/72 for i in range(73)]]
path+=line((upper_free,upper_tail,0),(upper_free,upper_tip,0))
P={'schema':1,'package':'P17','component_id':'MOTO-CENTRE-STAND-RETURN-SPRING-001','source':'creative/research/powertrain-completion-p17-v1/main-return-spring-plan-v7.json','mean_coil_radius_m':radius,'wire_diameter_m':wire,'helical_span_m':span,'helical_turn_span':turns,'turn_span_range':[18,23],'working_pitch_m':span/turns,'working_coil_gap_m':span/turns-wire,'hook_radius_m':hook,'hook_center_y_m':[-lower_tail,upper_tail],'tip_y_m':[-lower_tip,upper_tip],'tail_transition_span_m':transition,'tail_transition_control_m':control,'all_dimensions_estimated':True,'camera_calibrated':False,'scope':'DH161121 independently referenced centre-stand spring exterior, longer coiled body, larger offset open hooks and unequal working tails. Turn span/hand, free length, planes and dimensions estimated; positive numerical coil gap not a measured rest gap. No actual spring rate/preload/anchor/covers/installed mechanism or current RDC fit qualification. Retained side spring and other stand sources untouched.','material':{'name':'Proposed clean dark main-spring metal','base_color_linear':[.028,.024,.020,1],'metallic':.7,'roughness':.34},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);ob,report=round_wire('MAIN_STAND_RETURN_SPRING_DISTINCT_BODY_AND_OFFSET_OPEN_HOOKS',path,wire/2);(O/'centerline-clearance-check.json').write_text(json.dumps(report,indent=2)+'\n');ob['scope']=P['scope'];finish_source(H,O,P)
