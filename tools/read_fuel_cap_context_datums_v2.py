"""Derive candidate-only filler plane for existing cap review, never measured/OEM fit."""
import bpy, json, hashlib, math
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parents[1]
D=R/'creative/research/fuel-cap-tank-context-audit-v1'
D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cat=json.loads((R/'tools/motorcycle-lab/catalog.json').read_text())['assets']
inputs={}
points=[]
for key in ['fuel-tank-shell','fuel-cap-exterior-envelope-v2']:
 cfg=cat[key]
 source=R/'assets-src/moto-components'/cfg['source']
 with bpy.data.libraries.load(str(source),link=True) as (a,b):
  assert cfg['collection'] in a.collections
  b.collections=[cfg['collection']]
 col=b.collections[0]
 bpy.context.scene.collection.children.link(col)
 bpy.context.view_layer.update()
 pts=[o.matrix_world@v.co for o in col.all_objects if o.type=='MESH'and not o.hide_render for v in o.data.vertices]
 inputs[key]=dict(source=str(source.relative_to(R)),sha256=sha(source),bounds={'min':[min(p[i]for p in pts)for i in range(3)],'max':[max(p[i]for p in pts)for i in range(3)]})
 if key=='fuel-tank-shell':
  bodies=[o for o in col.all_objects if o.type=='MESH' and o.name.startswith('Tank upper skin')]
  assert len(bodies)==1
  points=[bodies[0].matrix_world@v.co for v in bodies[0].data.vertices]
samples=[]
for p in points:
 radius=math.hypot(p.x,p.y-.112)
 if .0293<=radius<=.0315:samples.append(tuple(p))
assert len(samples)>32
# Use the topmost actual neck point per angular bin, avoiding the lower return.
bins={}
for p in samples:
 angle=math.atan2(p[1]-.112,p[0]);b=int((angle+math.pi)/math.tau*64)%64
 if b not in bins or p[2]>bins[b][2]:bins[b]=p
assert len(bins)>24
pts=np.array(list(bins.values()))
mat=np.column_stack((pts[:,0],pts[:,1]-.112,np.ones(len(pts))))
a,b,c=np.linalg.lstsq(mat,pts[:,2],rcond=None)[0]
residual=pts[:,2]-mat@np.array([a,b,c])
normal=Vector((-a,-b,1)).normalized()
axis_x=Vector((1,0,a)).normalized()
axis_y=normal.cross(axis_x).normalized()
rotation=Matrix((axis_x,axis_y,normal)).transposed()
assert abs(residual).max()<.002,'Filler plane estimate rejected: sample inconsistency'
report=dict(rejected_prior_probe='native-datums-v1.json mixed unlinked accessory local transforms with tank body sampling,100mm residual; not a usable pose',scope='Exact authored tank/cap candidate datums; estimated review relation, not physical registration',inputs=inputs,filler_center_XY_m=[0,.112],selected_actual_top_neck_bins=len(pts),plane_z_equals_aX_plus_bYminus0112_plus_c=[float(a),float(b),float(c)],max_plane_residual_m=float(abs(residual).max()),proposed_translation_m=[0,.112,float(c)+.002],proposed_rotation_degrees=[math.degrees(v)for v in rotation.to_euler('XYZ')],display_gap_m=.002,critical_limits=['All source dimensions are historical estimates','Cap working68x47mm versus tank inner-mouth diameter56mm leaves nominal width/height mismatch; not received fit','2mm display gap is not a physical spacer or gasket','Lock/key slot/hinge/underside omitted in existing cap source; do not invent to hide mismatch','Plane is candidate sampling only, no calibrated photo or manufacturer measure'],art_accepted=False)
(D/'native-datums-v2.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(sha(R/r['source'])==r['sha256']for r in inputs.values())
print(json.dumps(report,indent=2))
