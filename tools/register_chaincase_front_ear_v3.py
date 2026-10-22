"""Rigid source-constrained registration of the observed inboard ear, no fabricated weld or second ear."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];N='chaincase-front-registration-v3';H=R/'assets-src/moto-components'/N;O=R/'creative/reviews'/N;D=R/'creative/research'/N
for p in (H,O,D,O/'raw'):p.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC'
inputs=[('shell','assets-src/moto-components/chaincase-upper/chaincase-upper-v1.blend','WEWA_CHAINCASE_UPPER_ISOLATED'),('ear','assets-src/moto-components/chaincase-front-ear-root-v2/child-candidate.blend',None)]
rows=[]
for key,src,colname in inputs:
 selected=[]
 with bpy.data.libraries.load(str(R/src),link=True)as(a,b):
  if colname:b.collections=[colname]
  else:
   selected=['COMPACT_INBOARD_EAR_PLAIN_BORE_CONTINUOUS_FORMED_ROOT'];b.objects=list(selected)
 if selected:
  col=bpy.data.collections.new('Observed ear selection');colname=col.name
  for ob in b.objects:col.objects.link(ob)
 else:col=b.collections[0]
 o=bpy.data.objects.new('REGISTRATION ['+key+']',None);s.collection.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=col
 if key=='ear':o.matrix_world=Matrix(((0,0,1,-.021),(1,0,0,-.405),(0,1,0,-.0347),(0,0,0,1)))
 rows.append(dict(key=key,source=src,sha256=sha(R/src),collection=colname,selected_objects=selected,matrix_world=[list(x)for x in o.matrix_world]))
# Actual source root-to-shell distances; agreement with an estimated layout is not measured fit.
shell=next(x for x in bpy.data.collections[rows[0]['collection']].all_objects if x.type=='MESH');verts=[shell.matrix_world@v.co for v in shell.data.vertices];bvh=BVHTree.FromPolygons(verts,[tuple(p.vertices)for p in shell.data.polygons],all_triangles=False)
ear=next(x for x in bpy.data.collections[rows[1]['collection']].all_objects if x.type=='MESH');M=Matrix(rows[1]['matrix_world']);root=[M@ear.matrix_world@v.co for v in ear.data.vertices if v.co.y>.0305];ds=[bvh.find_nearest(p)[3] for p in root];assert root and min(ds)<.001
report=dict(inputs=rows,root_samples=len(ds),root_nearest_distance_m=min(ds),root_max_distance_m=max(ds),scope='Rigid visual registration of existing isolated ear to estimated shell inner return; no weld, axis certification, hidden spacer or source deformation',all_dimensions_estimated=True,registration_uncertainty_m={'longitudinal':.015,'depth':.008,'height':.010},source_physical_views='creative/research/powertrain-completion-p26-v1/front-ear-root-new-evidence-v73.json',images_actually_reopened=['61486','61487','61488','61489'],art_accepted=False,mechanical_fit_accepted=False)
(D/'G0-G2-registration.json').write_text(json.dumps(report,indent=2)+'\n')
T=Matrix(rows[1]['matrix_world']);T.translation+=Vector((.13,.865,-.74));fragment=dict(key='chaincase-front-ear-root-observed',source_blend=rows[1]['source'],blend_sha256=rows[1]['sha256'],catalog_collection=None,matrix_world=[list(x)for x in T],selected_objects=rows[1]['selected_objects'],placement_status='Bounded source-constrained visual registration, no common fastener-axis or weld certification')
(O/'add-only-fragment.json').write_text(json.dumps(fragment,indent=2)+'\n')
s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=960;s.render.resolution_y=640;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.world=bpy.data.worlds.new('Neutral');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.15,.15,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
center=Vector((-.024,-.37,.054))
def aim(o):o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power in [('Key',(.2,-.4,.4),25),('Fill',(-.3,-.4,.2),20)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=.3;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=loc;aim(o)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';c.data.ortho_scale=.24;c.data.clip_start=.001;c.data.clip_end=10;c.location=(-.3,-.52,.14);aim(c)
bpy.context.preferences.filepaths.save_version=0
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
bpy.ops.wm.save_as_mainfile(filepath=str(H/'linked-registration.blend'),compress=True)
views=[]
for name,eye in [('inboard',(-.3,-.40,.055)),('root-quarter',(-.3,-.52,.20)),('outboard',(.3,-.48,.08))]:
 c.location=eye;aim(c);s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s);views.append(dict(name=name,samples=96,png_sha256=sha(O/(name+'.png')),exr_sha256=sha(O/'raw'/(name+'.exr'))));(O/'render-report.json').write_text(json.dumps(dict(source_sha256=sha(H/'linked-registration.blend'),views=views),indent=2)+'\n')
