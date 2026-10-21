"""Actual source voids and finite grooved rail; no claim of chain/swingarm fit."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/swingarm-chain-slider-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'swingarm-chain-slider-v1.blend';glb=H/'swingarm-chain-slider-inspection.glb';bpy.ops.wm.open_mainfile(filepath=str(src));o=bpy.data.collections['WEWA_SWINGARM_CHAIN_SLIDER_ISOLATED'].objects[0];m=o.data;m.calc_loop_triangles();b=BVHTree.FromPolygons([v.co for v in m.vertices],[t.vertices for t in m.loop_triangles],all_triangles=True);rows=[]
for name,y,z in [('ring',0,0),('smallwindow',.035,0),('longforkslot',.100,0)]:
 hit=b.ray_cast(Vector((-.1,y,z)),Vector((1,0,0)),.3);assert hit[0]is None;rows.append({'name':name,'source_ray_clear':True})
a=b.ray_cast(Vector((-.1,.100,.0175)),Vector((1,0,0)),.3)[0];c=b.ray_cast(Vector((.1,.100,.0175)),Vector((-1,0,0)),.3)[0];assert a is not None and c is not None;th=c.x-a.x;assert .02474<=th<=.025001;libs=[l.filepath for l in bpy.data.libraries];assert not libs;ims=[]
for im in bpy.data.images:
 if im.type=='IMAGE'and im.source=='FILE':assert im.filepath.startswith('//')and im.packed_file;ims.append({'name':im.name,'path':im.filepath,'packed':True})
r={'source_sha256':sha(src),'export_sha256':sha(glb),'void_probes':rows,'actual_grooved_rail_thickness_m':th,'designed_thickness_band_m':[.02474,.025001],'thickness_band_scope':'Nominal25mm extrusion minus author groove up to.25mm; geometric design envelope, not metrology/tolerance.','external_libraries':libs,'image_paths':ims,'tip_mouths_built':False,'opposed_runningface_documented':False,'chain_swept_or_swingarm_fit_verified':False,'materialgrade_hardness_or_strength_qualified':False,'art_accepted':False};(O/'source-interface-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
