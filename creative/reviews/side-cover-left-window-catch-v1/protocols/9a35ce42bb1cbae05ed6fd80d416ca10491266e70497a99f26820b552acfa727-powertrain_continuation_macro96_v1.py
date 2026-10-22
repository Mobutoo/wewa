"""Additional actual native96 ROI macro for NEW unfrozen children, never a screenshot crop."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import R,sha,digest,bounds,look,write
name=sys.argv[sys.argv.index('--')+1];H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
assert Path(name).name==name and not (O/'delivery.json').exists(),'Never append proofs to frozen children'
cfgpath=O/'macro96-camera.json';cfg=json.loads(cfgpath.read_text());label=cfg['label'];assert label.startswith('final-macro-')and Path(label).name==label
reportpath=O/'final-render-report.json';report=json.loads(reportpath.read_text());assert len(report['views'])>=3 and any(v['view']=='final-neutral-independent'for v in report['views'])
assert all(v['samples']==96 for v in report['views']);assert json.loads((O/'preview-review.json').read_text())['read_for_exterior_study']
source=H/'child-candidate.blend';source_sha=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
before={ob.name:digest(ob.data)for ob in s.objects if ob.type=='MESH'and not ob.hide_render};assert before
c,size,lo,hi=bounds();target=Vector(cfg['target_source']);direction=Vector(cfg['direction_source']);assert direction.length>0
s.camera.location=target+direction.normalized()*max(size*3,cfg['ortho_scale_m']*3);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=cfg['ortho_scale_m'];look(s.camera,target);bpy.context.view_layer.update()
roi=[]
for ob in s.objects:
 if ob.name not in before:continue
 for v in ob.data.vertices:
  p=ob.matrix_world@v.co
  if all(cfg['roi_min_source'][i]<=p[i]<=cfg['roi_max_source'][i]for i in range(3)):roi.append(world_to_camera_view(s,s.camera,p))
assert len(roi)>16,'Macro ROI must contain actual mesh vertices'
mins=[min(p[i]for p in roi)for i in range(3)];maxs=[max(p[i]for p in roi)for i in range(3)]
assert min(mins[:2])>.01 and max(maxs[:2])<.99,'Actual detail ROI cropped unintentionally'
assert mins[2]>s.camera.data.clip_start and maxs[2]<s.camera.data.clip_end
assert all(tuple(light.data.color)==(1,1,1)for light in s.objects if light.type=='LIGHT')
s.cycles.samples=96;s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100
s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(label+'.exr'));bpy.ops.render.render(write_still=True)
s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(label+'.png')),scene=s)
assert sha(source)==source_sha and all(digest(bpy.data.objects[n].data)==d for n,d in before.items())
row=dict(view=label,samples=96,resolution_px=[900,700],png=label+'.png',exr='raw/'+label+'.exr',png_sha256=sha(O/(label+'.png')),camera=list(s.camera.location),target=list(target),ortho_scale=s.camera.data.ortho_scale,allow_deliberate_crop=True,crop_scope='Explicit native detail ROI, three whole views remain separately required',roi_min_source=cfg['roi_min_source'],roi_max_source=cfg['roi_max_source'],actual_roi_vertices=len(roi),actual_roi_frame_min=mins,actual_roi_frame_max=maxs,source_sha256=source_sha,geometry_unchanged=True,camera_config_sha256=sha(cfgpath),protocol_sha256=sha(Path(__file__)),lights_rgb='Same neutral white source area rig',manual_read_required=True)
write(O,label+'-render-report.json',dict(views=[row],scope=cfg['reason'],art_accepted=False))
assert not any(v['view']==label for v in report['views']),'Do not overwrite a prior native macro proof'
report['views'].append(row);report['native96_views']=len(report['views']);reportpath.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(name=name,macro=label,actual_roi_vertices=len(roi),manual_image_read_required=True)))
