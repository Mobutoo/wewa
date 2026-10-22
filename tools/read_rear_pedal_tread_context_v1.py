"""Existing pad at an estimated exposed terminal, without inventing a joint."""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector, Euler
R=Path(__file__).resolve().parents[1]
D=R/'creative/research/rear-pedal-tread-context-v1'
D.mkdir(exist_ok=True)
source=R/'assets-src/moto-components/rear-brake-pedal-exterior-context-v1/integration-wrapper.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source))
bpy.context.view_layer.update()
arm=bpy.data.objects['BRAKE_PEDAL_COMPOUND_ARM_METAL']
rotation=Euler(tuple(math.radians(v)for v in [90,0,-90]),'XYZ').to_matrix()
translation=Vector((-.12,.3288,-.6012))
endpoint=Vector((.19278,-.17577,.028))
terminal=[arm.matrix_world@v.co for v in arm.data.vertices if ((arm.matrix_world@v.co)-endpoint).length<.009]
assert len(terminal)>8
points=[translation+rotation@p for p in terminal]
center=translation+rotation@endpoint
base=[center.x,center.y,max(p.z for p in points)+.002]
report=dict(scope='Rigid display hypothesis for existing tread at candidate exposed arm terminal, not mounted pedal fit',source=str(source.relative_to(R)),source_sha256=old,authored_terminal_point_m=list(endpoint),global_arm_translation_m=list(translation),global_arm_rotation_degrees=[90,0,-90],sample_radius_m=.009,actual_terminal_vertex_count=len(points),actual_terminal_Z_range_m=[min(p.z for p in points),max(p.z for p in points)],proposed_pad_translation_m=base,proposed_pad_rotation_degrees=[0,0,0],display_gap_m=.002,critical_limits=['Terminal point is authored estimate, not manufacturer datum','Pad rigidly reoriented foot-up for world review; original parked kit unchanged','No joint, contact foot seat, weld or hidden support manufactured','Current RDC location uses uncalibrated profile context, transverseX unknown','Source morphology/material reception and G5/G8 unchanged'],art_accepted=False)
(D/'native-terminal-read-v1.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==old
print(json.dumps(report,indent=2))
