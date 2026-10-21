"""Read-only optical diagnostic. In-memory variants only; never save/export source.
Variants distinguish area-light patterns, inherited corner-normal averaging and
coincident sealing surface influence. They are not replacement artwork.
"""
import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PUBLIC=ROOT/'creative/research/instruments-v2';OUT=Path('/workspace/wewa-assets/work-in-progress/instruments-v2/optical-edge-diagnostic');OUT.mkdir(parents=True,exist_ok=True);source=HERE/'instruments-v2.blend';export=HERE/'instruments-v2-inspection.glb';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sourceSHA=sha(source);exportSHA=sha(export);expected=json.loads((ROOT/'creative/reviews/instruments-v2/source-geometry-check.json').read_text());assert sourceSHA==expected['source_sha256']and exportSHA==expected['export_sha256'];sys.path.insert(0,str(ROOT/'tools'));from blender_component_camera_preflight import check_component_camera
variants=['baseline','uniform-environment','glass-sharp-30deg','glass-and-bezel-sharp-30deg','sealing-lip-hidden'];report={'schema':1,'source_sha256':sourceSHA,'export_sha256':exportSHA,'source_or_export_saved':False,'variants':{},'art_accepted':False}
def analyse(o):
 o.data.update();m=o.data;rows=[]
 # Read actual evaluated split-corner normals on the outer front transition.
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());em=ev.to_mesh()
 for p in em.polygons:
  points=[em.vertices[em.loops[i].vertex_index].co for i in p.loop_indices]
  if all(abs(v.z-.039)<1e-7 or abs(v.z-.0395)<1e-7 for v in points):
   for li in p.loop_indices:
    co=em.vertices[em.loops[li].vertex_index].co
    if abs(co.z-.039)<1e-7:
     n=em.corner_normals[li].vector;angle=math.degrees(math.acos(max(-1,min(1,n.dot(p.normal)))));rows.append(angle)
 ev.to_mesh_clear();return{'outer_front_strip_corner_normal_vs_face_degrees':{'min':min(rows),'max':max(rows),'mean':sum(rows)/len(rows),'samples':len(rows)},'meaning':'Difference from local polygon plane, not an OEM normal measurement. Shared smoothing can intentionally interpolate a curved surface; steep edge mixing must be interpreted against construction.'}
for mode in variants:
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;assembly=bpy.data.objects['INSTRUMENT_CLUSTER_MOUNT'];lens=bpy.data.objects['SPEED clear closed lens'];bezel=bpy.data.objects['SPEED stepped bezel'];lip=bpy.data.objects['SPEED lens sealing lip'];s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.cycles.max_bounces=12;s.cycles.transmission_bounces=8;s.render.resolution_x=640;s.render.resolution_y=640;s.render.resolution_percentage=100;s.camera.data.clip_start=.001;s.camera.data.clip_end=10;s.camera.data.dof.use_dof=False
 if mode=='uniform-environment':
  for o in bpy.data.objects:
   if o.type=='LIGHT':o.hide_render=True
  bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(1,1,1,1);bg.inputs['Strength'].default_value=1
 if mode in ['glass-sharp-30deg','glass-and-bezel-sharp-30deg']:
  lens.data.set_sharp_from_angle(angle=math.radians(30));lens.data.update()
 if mode=='glass-and-bezel-sharp-30deg':bezel.data.set_sharp_from_angle(angle=math.radians(30));bezel.data.update()
 if mode=='sealing-lip-hidden':lip.hide_render=True
 N=assembly.matrix_world.to_3x3()@Vector((0,0,1));target=assembly.matrix_world@Vector((-.064,0,.031));s.camera.location=target+N*.255;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=70;bpy.context.view_layer.update();frame=check_component_camera(s,[bpy.data.objects[n]for n in ['SPEED hollow rear pod','SPEED stepped bezel','SPEED clear closed lens']],allow_crop=False,margin=.025);analysis=analyse(lens);png=OUT/(mode+'.png');s.render.image_settings.file_format='PNG';s.render.filepath=str(png);bpy.ops.render.render(write_still=True);report['variants'][mode]={'PNG_private_path':str(png),'PNG_sha256':sha(png),'actually_saved':True,'samples':8,'resolution_px':[640,640],'camera_location_m':list(s.camera.location),'camera_target_m':list(target),'lens_mm':70,'actual_frame_check':frame,'analysis':analysis,'in_memory_change':mode};tmp=OUT/'checkpoints.tmp';tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(OUT/'checkpoints.json');print('OPTICAL_DIAGNOSTIC_SAVED',mode)
assert sha(source)==sourceSHA and sha(export)==exportSHA;report['original_source_and_export_hashes_unchanged']=True;(PUBLIC/'optical-edge-diagnostic-v2.json').write_text(json.dumps(report,indent=2)+'\n')
