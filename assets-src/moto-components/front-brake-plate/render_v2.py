"""Render the exact saved source only after geometry/interface checks pass."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--revision',choices=['v1','v2'],default='v2');parser.add_argument('--samples',type=int,default=96);parser.add_argument('--resolution',type=int,default=1100);parser.add_argument('--views',default='quarter,front,rear,macro,cinematic-quarter');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
REV=args.revision;OUT=ROOT/('creative/reviews/front-brake-plate-'+REV)
check=json.loads((OUT/'source-geometry-check.json').read_text());geometry=json.loads((OUT/'geometry-check.json').read_text())
assert check['source_sha256']==hashlib.sha256((HERE/('front-brake-plate-'+REV+'.blend')).read_bytes()).hexdigest(),'Stale source evidence'
assert check['non_manifold_edges']==0 and check['connected_casting_shells']==1 and check['candidate_interface']['surface_triangle_crossings']==0,'Source/interface checks not passed'
assert not any(x['glTF_errors'] for x in geometry['exports']),'Invalid export'
for exported in geometry['exports']:assert exported['sha256']==hashlib.sha256((ROOT/exported['file']).read_bytes()).hexdigest(),'Stale export evidence'
bpy.ops.wm.open_mainfile(filepath=str(HERE/('front-brake-plate-'+REV+'.blend')))
scene=bpy.context.scene;scene.cycles.samples=args.samples;scene.render.resolution_x=args.resolution;scene.render.resolution_y=args.resolution;scene.render.image_settings.file_format='PNG'
fit=bpy.data.collections['FIT_INSPECTION_LINKED_CANDIDATES'];floor=bpy.data.objects['PANEL_STUDIO_FLOOR'];key=bpy.data.lights['PANEL_KEY'];fill=bpy.data.lights['PANEL_FILL'];edge=bpy.data.lights['PANEL_EDGE']
views={'front':((.50,0,.30),(.037,0,.29),80,False),'rear':((-.42,0,.30),(.031,0,.29),80,False),'quarter':((.45,-.25,.49),(.032,0,.29),80,False),'fit-neutral':((.95,-1.38,.84),(0,0,.29),70,True),'cinematic-quarter':((.45,-.25,.49),(.032,0,.29),80,False),'macro':((.19,-.10,.355),(.040,-.025,.31),100,False)}
report={'scope':'Actual saved Blender geometry. Whole-motorcycle generated target is separate. Fit view uses linked wheel inspection candidates.','source_sha256':check['source_sha256'],'samples':args.samples,'resolution_px':[args.resolution,args.resolution],'denoising':False,'views':[],'art_accepted':False}
for name in args.views.split(','):
 location,target,lens,show_fit=views[name];fit.hide_render=not show_fit;floor.location.z=-.0005 if show_fit else .2177
 scene.camera.location=location;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=lens
 warm=name.startswith('cinematic');key.color=(1,.70,.43) if warm else (1,1,1);key.energy=36 if warm else 27;fill.color=(.68,.79,1) if warm else (1,1,1);fill.energy=10 if warm else 15;edge.color=(1,.82,.63) if warm else (1,1,1)
 scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
 report['views'].append({'name':name,'camera_location_m':location,'camera_target_m':target,'lens_mm':lens,'wheel_fit_inspection':show_fit})
(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_PANEL_RENDERS',len(report['views']))
