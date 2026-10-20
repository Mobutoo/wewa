"""Build hidden-render assembly guides from the explicit datum/uncertainty file.
These are not motorcycle parts, a calibrated reconstruction or an export asset.
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];INPUT=ROOT/'creative/workflow/motorcycle-datums-v1.json';P=json.loads(INPUT.read_text())
OUT=ROOT/'assets-src/moto-guides';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
c=bpy.data.collections.new('GUIDES_ONLY_NOT_MOTORCYCLE_PARTS');s.collection.children.link(c)
def guide(name,points):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';line=data.splines.new('POLY');line.points.add(len(points)-1)
 for p,co in zip(line.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,data);c.objects.link(o);o.hide_render=True;o.show_in_front=True;o['status']='Assembly guide only; no physical-part acceptance';return o
def marker(name,p):
 o=bpy.data.objects.new(name,None);c.objects.link(o);o.location=p;o.empty_display_type='PLAIN_AXES';o.empty_display_size=.08;o.hide_render=True;return o
g=P['provisional_guides_m'];front=g['front_axle'];rear=g['rear_axle']
marker('GUIDE bare bar centre clamp — origin',(0,0,0));marker('GUIDE front axle — estimated relative to bar',front);marker('GUIDE rear axle — estimated relative to bar',rear)
guide('CONSTRAINT published wheelbase1285mm — only axle separation fixed',[front,rear])
guide('GUIDE +X pilot LEFT',[(-.45,0,0),(.45,0,0)])
guide('GUIDE +Y rear/pilot',[(0,-.6,0),(0,.6,0)])
guide('GUIDE Z up',[(0,0,-.85),(0,0,.2)])
for label,axle in [('front',front),('rear',rear)]:
 guide('GUIDE '+label+' axle axis — estimated width',[tuple(Vector(axle)+Vector((-.12,0,0))),tuple(Vector(axle)+Vector((.12,0,0)))])
s['purpose']=P['purpose'];s['all_guide_local_positions_estimated']=True;s['not_a_fabricated_asset']=True;s['reference_camera_calibrated']=False;s['datum_json_sha256']=hashlib.sha256(INPUT.read_bytes()).hexdigest();s['guide_status']=P['guide_status']
path=OUT/'datum-guides-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
(OUT/'provenance.json').write_text(json.dumps({'kind':'hidden-render_coordinate_guides_not_parts','source':'../../creative/workflow/motorcycle-datums-v1.json','source_sha256':s['datum_json_sha256'],'blend_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'published_baseline_m':P['published_constraints']['wheelbase'],'local_positions_estimated':True,'camera_calibrated':False,'art_accepted':False},indent=2)+'\n')
print('WEWA_DATUM_GUIDES_ONLY',path)
