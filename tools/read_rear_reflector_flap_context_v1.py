"""Fit a review plane to the actual candidate rear flap; no physical mount claim."""
import bpy,json,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector, Euler, Matrix
R=Path(__file__).resolve().parents[1]
D=R/'creative/research/rear-reflector-flap-context-v1'
D.mkdir(exist_ok=True)
source=R/'assets-src/moto-components/rear-mudflap-jv181410-visible-front22-v4/rear-flap-material.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source))
bpy.context.view_layer.update()
ob=bpy.data.objects['JV181410_OBSERVED_OUTSIDE_FIELD_BAND_CHEEKS_BOSS_LIP']
rows=json.loads((R/'creative/reviews/whole-exterior-coverage-v13/linked-parents-check.json').read_text())['parents']
row=next(r for r in rows if r['key']=='rear-flap-jv181410')
assert old==row['sha256']
rotation=Euler(tuple(math.radians(v)for v in row['rotation_degrees']),'XYZ').to_matrix()
translation=Vector(row['translation_m'])
zc=-.58
pts=[translation+rotation@(ob.matrix_world@v.co)for v in ob.data.vertices]
samples=np.array([tuple(p)for p in pts if abs(p.x)<=.04 and abs(p.z-zc)<=.025])
assert len(samples)>20
fit=np.column_stack((samples[:,0],samples[:,2]-zc,np.ones(len(samples))))
a,b,c=np.linalg.lstsq(fit,samples[:,1],rcond=None)[0]
res=samples[:,1]-fit@np.array([a,b,c])
assert abs(res).max()<.015,'Candidate field too curved for this simple review plane'
n=Vector((-a,1,-b)).normalized()
x=Vector((-1,-a,0)).normalized()
y=n.cross(x).normalized()
rot=Matrix((x,y,n)).transposed()
position=Vector((0,float(c+res.max()),zc))+n*.002
report=dict(scope='Candidate-only rear reflector presentation below fictional plate, not mounting geometry',flap_source=str(source.relative_to(R)),flap_source_sha256=old,flap_parent_pose=row,chosen_reflector_center_Z_m=zc,sampled_vertices=len(samples),field_plane_Y_equals_aX_plus_bZminusZc_plus_c=[float(a),float(b),float(c)],maximum_residual_m=float(abs(res).max()),outer_plane_shift_m=float(res.max()),proposed_translation_m=list(position),proposed_rotation_degrees=[math.degrees(v)for v in rot.to_euler('XYZ')],minimum_nominal_field_display_gap_m=.002,critical_limits=['Free exterior field chosen as a review site, not a documented M5 fixing datum','Catalogue M5 nut association does not reveal rear stud/bolt geometry or mounted contacts','Plane comes from unreceived authored flap, not calibrated physical surface','Reflector80x50x6mm and placement are estimates; plate/flap/corner clearances not certified','No hidden mounting bracket, pin, gasket or rear cap manufactured'],art_accepted=False)
(D/'native-field-read-v1.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==old
print(json.dumps(report,indent=2))
