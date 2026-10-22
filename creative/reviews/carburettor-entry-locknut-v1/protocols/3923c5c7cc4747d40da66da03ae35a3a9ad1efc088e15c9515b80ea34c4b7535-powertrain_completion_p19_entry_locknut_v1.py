"""Original separate source-visible entry locknut: softened polygon annulus, plain open lumen."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_loft_v4 import clean_smooth,recalc
R=Path(__file__).resolve().parents[1];name='carburettor-entry-locknut-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
P=dict(schema=1,package='P19',component_id='MOTO-CARBURETTOR-ENTRY-LOCKNUT-001',source='creative/research/powertrain-completion-p19-v1/entry-locknut-plan-v11.json',across_flats_m=.014,height_m=.004,plain_bore_diameter_m=.007,working_polygon_sides=6,corner_cut_m=.00055,all_dimensions_estimated=True,camera_calibrated=False,scope='Separate source-visible polygon locknut immediately below entry barrel: softened working six-flat annulus, real plain axial passage. Full flat count, internal thread, seats and all dimensions unqualified. Adjacent thin grip ring/barrel/elbow excluded and unchanged; no fitted engagement or actual thread claimed.',material=dict(name='Proposed plain bright entry locknut metal',base_color_linear=[.38,.40,.42,1],metallic=.85,roughness=.28),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
rad=.007/math.cos(math.pi/6);points=[Vector((rad*math.cos(math.pi/6+i*math.pi/3),rad*math.sin(math.pi/6+i*math.pi/3)))for i in range(6)];corners=[]
for i,b in enumerate(points):a,c=points[(i-1)%6],points[(i+1)%6];corners.append((b-(b-a).normalized()*.00055,b,b+(c-b).normalized()*.00055))
curve=[]
for i,(a,b,c)in enumerate(corners):
 for j in range(6):t=j/6;curve.append((1-t)**2*a+2*(1-t)*t*b+t*t*c)
 for j in range(10):curve.append(c.lerp(corners[(i+1)%6][0],j/10))
rings=[('outer',.94,0),('outer',.975,.00008),('outer',.995,.00020),('outer',1,.00030),('outer',1,.00370),('outer',.995,.00380),('outer',.975,.00392),('outer',.94,.004),('circle',.0037,.004),('circle',.0035,.0038),('circle',.0035,.0002),('circle',.0037,0)]
V=[];F=[];N=len(curve)
for mode,r,z in rings:
 for p in curve:
  v=p*r if mode=='outer'else p.normalized()*r;V.append((v.x,v.y,z))
for k in range(len(rings)):
 for j in range(N):F.append((k*N+j,k*N+(j+1)%N,((k+1)%len(rings))*N+(j+1)%N,((k+1)%len(rings))*N+j))
ob=mesh_object('SOURCE_VISIBLE_ENTRY_LOCKNUT_SOFTENED_HEX_ANNULUS',V,F);recalc(ob);clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
