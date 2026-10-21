"""30191035 separate open-pitch brake-rod spring with closer end coils."""
import bpy,math,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import finish_source
from powertrain_continuation_sweep_v3 import round_wire
R=Path(__file__).resolve().parents[1];name='brake-rod-compression-spring-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
span=.100;radius=.0048;wire=.0012;turns=24;N=turns*64
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
weights=[.30+.70*smooth((i+.5)/N/.08)*smooth((1-(i+.5)/N)/.08)for i in range(N)];total=sum(weights);y=-span/2;path=[]
for i in range(N+1):
 a=math.tau*turns*i/N;path.append(Vector((radius*math.cos(a),y,radius*math.sin(a))))
 if i<N:y+=span*weights[i]/total
P=dict(schema=1,package='P15',component_id='MOTO-BRAKE-ROD-COMPRESSION-SPRING-001',source='creative/research/powertrain-completion-p15-v1/rod-compression-spring-plan-v9.json',wire_diameter_m=wire,mean_coil_radius_m=radius,body_span_m=span,turns_working=turns,turns_range=[21,28],terminal_pitch_m=span*.30/total*64,body_pitch_m=span/total*64,pitch_transition_fraction=.08,terminal_wire_ends='Flat local wire caps, not axial bore caps; no ground or squared-end claim',all_dimensions_estimated=True,scope='30191035 independently referenced compression spring only. Slender open-pitch coiled wire and closer terminal turns. No hooks or substitution for JV161014 torsion spring. Exact free length, winding, end form, force/stiffness and installed linkage/adjuster engagement unqualified.',material=dict(name='Proposed plain brake rod spring metal',base_color_linear=[.19,.21,.23,1],metallic=.75,roughness=.34),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);ob,report=round_wire('BRAKE_ROD_COMPRESSION_SPRING_VARIABLE_PITCH_FINITE_WIRE',path,wire/2);(O/'centerline-clearance-check.json').write_text(json.dumps(report,indent=2)+'\n');ob['scope']=P['scope'];finish_source(H,O,P)
