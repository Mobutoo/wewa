"""Checkpointed isolated whole pair and useful seal-section views, no mounted deformation."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-o-ring-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'build-report.json').read_text());source=H/'engine-intake-o-ring-v1.blend';assert sha(source)==B['source_sha256'];E=json.loads((O/'export-check.json').read_text());assert E['glTF_errors']==0 and E['source_sha256']==sha(source);sys.path.insert(0,str(H));from camera_preflight import check_component_camera
from render_checkpoint import checkpoint_view
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preview='--preview'in args;preflight='--preflight-only'in args;bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;objects=[bpy.data.objects[q['name']]for q in B['geometry']];s.cycles.samples=24 if preview else 96;s.render.resolution_x=1100 if preview else 1440;s.render.resolution_y=850 if preview else 1080;s.camera.data.clip_start=.0001
lights={o.name:(o.matrix_world.copy(),o.data.energy,o.data.size)for o in s.objects if o.type=='LIGHT'}
views=[('isolated-pair',(.09,-.13,.125),(0,0,0),False,65),('one-ring-normal',(-.0225,0,.110),(-.0225,0,0),True,70),('circular-section-detail',(-.0225,-.047,.025),(-.0225,-.01530,0),True,110),('raking-surface-control',(-.0225,-.041,.014),(-.0225,-.01530,0),True,110)]
if'--view'in args:views=[q for q in views if q[0]==args[args.index('--view')+1]]
out=Path('/workspace/wewa-assets/work-in-progress/engine-intake-o-ring')/sha(source)[:12]/'pbr/native24'if preview else O;report={'source_sha256':sha(source),'export_sha256':E['export_sha256'],'samples':s.cycles.samples,'camera_calibrated':False,'isolated_unmounted':True,'quantity_two_one_physical_type':True,'views':[],'art_accepted':False}
for name,position,aim,crop,lens in views:
 for n,(matrix,power,size)in lights.items():o=bpy.data.objects[n];o.matrix_world=matrix.copy();o.data.energy=power;o.data.size=size
 if name=='raking-surface-control':
  key=bpy.data.objects['CONTROL_KEY'];key.location=(-.0225,-.09,.006);key.rotation_euler=(Vector(aim)-key.location).to_track_quat('-Z','Y').to_euler();key.data.size=.025
 s.camera.location=position;s.camera.rotation_euler=(Vector(aim)-Vector(position)).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;bpy.context.view_layer.update();frame=check_component_camera(s,objects,allow_crop=crop,margin=.005);row={'name':name,'camera_preflight':frame,'rendered':False}
 if not preflight:row['outputs']=checkpoint_view(s,out,source,name)['outputs'];row['rendered']=True
 report['views'].append(row);out.mkdir(parents=True,exist_ok=True);(out/('camera-preflight.json'if preflight else'render-report.json')).write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==B['source_sha256']
