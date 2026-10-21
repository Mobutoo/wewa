"""Read historical source, compare ordinary/custom normals without mutating it.
Diagnostic renders are private, explicitly changed only in memory, no v2 acceptance.
"""
from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];source=H/'engine-cover-right-v1.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)=='185274d117291007e185fba8209abac91153ece3ae9e4a0a8ce5a67667c4331f';O=Path('/workspace/wewa-assets/work-in-progress/engine-cover-right-v2');O.mkdir(exist_ok=True);sys.path.insert(0,str(H.parent/'kickstarter'));from camera_preflight import check_component_camera
from render_checkpoint_local import checkpoint_view
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;o=bpy.data.objects['RH clutch cover hollow casting - editable candidate'];m=o.data
coords=np.empty(len(m.vertices)*3);m.vertices.foreach_get('co',coords);faces=[tuple(p.vertices) for p in m.polygons];geometry_sha=hashlib.sha256(coords.tobytes()+json.dumps(faces).encode()).hexdigest();before=np.array([list(n.vector) for n in m.corner_normals]);had_custom=m.has_custom_normals
# Preserve real geometry, face smooth sectors and old source, compare normals only.
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.mesh.customdata_custom_splitnormals_clear();m.update();bpy.context.view_layer.update();after=np.array([list(n.vector) for n in m.corner_normals]);angles=np.degrees(np.arccos(np.clip((before*after).sum(1),-1,1)));newcoords=np.empty_like(coords);m.vertices.foreach_get('co',newcoords);assert np.array_equal(coords,newcoords);assert faces==[tuple(p.vertices) for p in m.polygons]
report={'base_source_sha256':sha(source),'historical_source_not_saved_or_modified':True,'diagnostic_only':True,'geometry_sha256_before_and_after':geometry_sha,'vertices_exactly_unchanged':True,'faces_exactly_unchanged':True,'custom_normals_present_before':had_custom,'custom_normals_present_after':m.has_custom_normals,'corner_normal_angle_difference_deg':{'max':float(angles.max()),'p50':float(np.percentile(angles,50)),'p95':float(np.percentile(angles,95)),'p99':float(np.percentile(angles,99)),'corners_over5deg':int((angles>5).sum()),'corners_total':len(angles)},'views':[],'art_accepted':False}
(O/'normal-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_NORMAL_DIAG',json.dumps(report),flush=True)
old=json.loads((R/'creative/reviews/engine-cover-right-v1/render-report.json').read_text());s.cycles.samples=8;s.render.resolution_x=1100;s.render.resolution_y=850;s.camera.data.clip_start=.001
for view in old['views']:
 name='normal-clear-'+view['name'];target=Vector(view['target_m']);s.camera.location=view['camera_m'];s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=view['lens_mm'];bpy.context.view_layer.update();frame=check_component_camera(s,[o],allow_crop=False);cp=checkpoint_view(s,O,source,name);report['views'].append({'name':name,'samples':8,'source_geometry_unchanged':True,'only_custom_normals_cleared_in_memory':True,'camera_preflight':frame,'checkpoint':name+'.checkpoint.json','outputs':cp['outputs']});(O/'normal-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)=='185274d117291007e185fba8209abac91153ece3ae9e4a0a8ce5a67667c4331f'
