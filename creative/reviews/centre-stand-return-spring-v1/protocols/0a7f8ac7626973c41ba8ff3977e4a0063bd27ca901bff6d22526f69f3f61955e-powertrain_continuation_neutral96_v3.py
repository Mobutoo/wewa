"""Third independent neutral native96 view, additive to this resume's new children only."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import R,sha,digest,bounds,look,write
name=sys.argv[sys.argv.index('--')+1];H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
assert Path(name).name==name and not (O/'delivery.json').exists()
assert json.loads((H/'parameters.json').read_text())['package'] in ['P01','P04','P14','P15','P16','P17','P18','P19','P20','P26','P27']
assert json.loads((O/'preview-review.json').read_text())['read_for_exterior_study']
bpy.ops.wm.open_mainfile(filepath=str(H/'child-candidate.blend'));s=bpy.context.scene
before={ob.name:digest(ob.data)for ob in s.objects if ob.type=='MESH'and not ob.hide_render}
c,size,lo,hi=bounds();direction=(-.8,-1.0,2.8)if name!='centre-stand-main-frame-v1'else(-.4,-.6,3)
s.camera.location=c+Vector(direction)*size;look(s.camera,c);bpy.context.view_layer.update()
points=[world_to_camera_view(s,s.camera,ob.matrix_world@v.co)for ob in s.objects if ob.name in before for v in ob.data.vertices]
mins=[min(v[i]for v in points)for i in range(3)];maxs=[max(v[i]for v in points)for i in range(3)]
assert min(mins[:2])>.01 and max(maxs[:2])<.99
assert mins[2]>s.camera.data.clip_start and maxs[2]<s.camera.data.clip_end
s.cycles.samples=96;s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100
assert all(tuple(light.data.color)==(1,1,1)for light in s.objects if light.type=='LIGHT')
label='final-neutral-independent';s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(label+'.exr'));bpy.ops.render.render(write_still=True)
s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(label+'.png')),scene=s)
assert all(digest(bpy.data.objects[n].data)==v for n,v in before.items())
row=dict(view=label,samples=96,resolution_px=[900,700],png=label+'.png',exr='raw/'+label+'.exr',png_sha256=sha(O/(label+'.png')),camera=list(s.camera.location),target=list(c),ortho_scale=s.camera.data.ortho_scale,actual_vertex_frame_min=mins,actual_vertex_frame_max=maxs,independent_direction=list(direction),lights_rgb='Neutral white; same source rig, no material change',protocol_sha256=sha(Path(__file__)))
write(O,'neutral96-render-report.json',dict(views=[row],source_sha256=sha(H/'child-candidate.blend'),geometry_unchanged=True,art_accepted=False))
p=O/'final-render-report.json';report=json.loads(p.read_text());archive=O/'final-two-view-report-before-neutral.json'
if not archive.exists():archive.write_bytes(p.read_bytes())
report['views']=[r for r in report['views']if r['view']!=label]+[row];report['independent_neutral_protocol_sha256']=sha(Path(__file__));report['native96_views']=len(report['views']);report['minimum_three_views']=True
assert len(report['views'])>=3 and all(r['samples']==96 for r in report['views']);p.write_text(json.dumps(report,indent=2)+'\n')
