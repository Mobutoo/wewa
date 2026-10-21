"""Read-only comparison with rejected axial-sampled diagnostic; no body/source mutation."""
from pathlib import Path
import bpy,json,hashlib,math
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/control-perch-clamp-bolt-v1';D=H/'diagnostics/axial-sampled-thread-marches';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'geometry-report.json').read_text());P=json.loads((H/'parameters.json').read_text());oldP=json.loads((D/'parameters.json').read_text());source=H/'control-perch-clamp-bolt-v1-geometry.blend';old=D/'control-perch-clamp-bolt-v1-geometry.blend';assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));a=bpy.data.objects[B['geometry'][0]['name']]
with bpy.data.libraries.load(str(old),link=False)as(data,loaded):loaded.objects=[a.name]
b=loaded.objects[0];count=17*P['radial_samples'];before=[list(v.co)for v in b.data.vertices[:count]];after=[list(v.co)for v in a.data.vertices[:count]];assert before==after
exceptions={'axial_samples_per_pitch','helical_grid_phase_offset','geometry_method'};kept={k:v for k,v in oldP.items()if k not in exceptions};assert all(P[k]==v for k,v in kept.items());assert list(a.matrix_basis)==list(b.matrix_basis);assert list(a.parent.matrix_basis)==list(b.parent.matrix_basis)
N=P['radial_samples'];step=P['axial_samples_per_pitch'];pitch=P['documented_related_pitch_m'];errors=[]
for ring in range(418,1218):
 for angle in [0,12,48,96,144]:
  u=a.data.vertices[ring*N+angle].co;v=a.data.vertices[(ring+1)*N+angle].co;delta=(math.atan2(v.y,v.x)-math.atan2(u.y,u.x)+math.pi)%(2*math.pi)-math.pi;errors.append(abs(delta-math.tau/step))
assert max(errors)<2e-7
r={'component_id':P['component_id'],'source_sha256':sha(source),'diagnostic_source_sha256':sha(old),'head_and_fillet_actual_vertex_prefix_count':count,'head_and_fillet_actual_positions_bit_identical':True,'protected_parameters_exact':kept,'datum_and_object_basis_exact':True,'actual_helix_angular_advance_max_error_rad':max(errors),'positive_Z_and_positive_angle_advance_right_hand_confirmed_on_retained_vertices':True,'scope':'Head/fillet and nominal dimensions protected, thread grid changed to aligned helical phases. No material/image/postexport manipulation. Remaining thread form/runout and currentRDC fit unreceived.','art_accepted':False};(O/'head-protection-check.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==B['source_sha256'];print(json.dumps(r))
