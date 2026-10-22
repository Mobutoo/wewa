"""Original bounded exterior completion; no hidden bore or retention geometry."""
import bpy,json,math,sys,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
R=Path('/workspace/wewa');K='passenger-rubber-completion-v3';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
sys.path.insert(0,str(R/'tools'));import powertrain_completion_common_open_v1 as c
P=json.loads((R/'assets-src/moto-components/passenger-footrest-rubber-jk113008-v1/parameters.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
profile=P['source_profile_x_radius_m'];n=192
V=[(x,r*math.cos(math.radians(-45+360*j/n)),r*math.sin(math.radians(-45+360*j/n)))for x,r in profile for j in range(n)]
F=[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j)for i in range(len(profile)-1)for j in range(n)]
ob=c.mesh_object('JK113008_BOUNDED_OUTER_ENVELOPE_V3',V,F);col=bpy.data.collections.new('WEWA_PASSENGER_RUBBER_COMPLETION_V3');bpy.context.scene.collection.children.link(col)
for old in list(ob.users_collection):old.objects.unlink(ob)
col.objects.link(ob)
P.update(revision=K,collection=col.name,angular_extent_degrees=[-45,315],body_visible_angular_extent_degrees=[-45,315],unobserved_lower_sector_degrees=None,expected_boundary_edges=384,scope='Continuous bounded outer envelope; lower sector interpolated rotationally from unchanged estimated axial profile with new physical oblique support. Both terminal boundary loops open. No deep bore, wall thickness, cap, seat or retention.',package_complete=False)
P['completion_basis']='New Scooter City physical JK113008 oblique shows returning lower rib crests/valleys and continuous mouth rim. Full underside not directly imaged: 90deg continuation is an explicit bounded estimated rotational interpolation, not measured topology.'
P['remaining_unknowns']=['Deep bore and retention','Distal closure','Exact current RDC applicability','Calibrated dimensions','Unseen mould underside detail']
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');c.finish_source(H,O,P)
s=bpy.context.scene;s.render.resolution_x=800;s.render.resolution_y=600;s.camera.data.ortho_scale=.155
rows=[]
def render(label,eye,samples):
 s.camera.location=eye;c.look(s.camera,(.05,0,0));s.cycles.samples=samples;s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.filepath=str(O/(label+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(label+'.png')),scene=s);rows.append(dict(view=label,samples=samples,png=label+'.png',exr=label+'.exr'))
render('gray-underside',(.02,-.04,-.19),16)
m=ob.data.materials[0];b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.012,.013,.015,1);b.inputs['Roughness'].default_value=.64
bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-candidate.blend'),compress=True);c.export(H,'child-candidate.glb')
for label,eye in [('material-quarter',(-.12,-.14,.10)),('material-underside',(.02,-.04,-.19)),('material-profile',(.05,-.2,.02))]:render(label,eye,96)
(O/'render-report.json').write_text(json.dumps(dict(views=rows,art_accepted=False,fit_qualified=False),indent=2)+'\n')
# Preserve both actual placement matrices from current 140-parent assembly.
parents=json.loads((R/'creative/reviews/whole-exterior-coverage-v19/linked-parents-check.json').read_text())['parents'];adds=[]
for old in parents:
 if 'passenger-footrest-rubber-jk113008-v1/' in old.get('source',''):
  row=dict(old);row.update(source=str((H/'child-candidate.blend').relative_to(R)),sha256=c.sha(H/'child-candidate.blend'),collection=col.name,selected_objects=[]);adds.append(row)
assert len(adds)==2
(H/'integration-fragment.json').write_text(json.dumps(dict(parents_to_remove=[a['key']for a in adds],additions=adds,retained_parent_count=140,shape_only_replacement=True,matrices_unchanged=True,conditional_estimated_completion=True),indent=2)+'\n')
