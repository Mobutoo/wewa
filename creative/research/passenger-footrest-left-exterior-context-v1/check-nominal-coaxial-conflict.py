"""Read-only comparison: source estimated nominal hinge versus explicit separated display pose."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');K='passenger-footrest-left-exterior-context-v1';D=R/'creative/research'/K;H=R/'assets-src/moto-components'/K;bpy.ops.wm.open_mainfile(filepath=str(H/(K+'.blend')));bpy.context.view_layer.update();data={}
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 key=ob['source_parent']
 if key not in ['passenger-footrest-stay-left-v1','passenger-footpeg-metal-v1']:continue
 m=ob.data;m.calc_loop_triangles();data[key]=([ob.matrix_world@v.co for v in m.vertices],[list(t.vertices)for t in m.loop_triangles])
stay_v,stay_f=data['passenger-footrest-stay-left-v1'];peg_v,peg_f=data['passenger-footpeg-metal-v1'];s=BVHTree.FromPolygons(stay_v,stay_f,all_triangles=True);actual=BVHTree.FromPolygons(peg_v,peg_f,all_triangles=True);nominal=BVHTree.FromPolygons([p-Vector((0,0,.005))for p in peg_v],peg_f,all_triangles=True);a=len(s.overlap(actual));n=len(s.overlap(nominal));assert a==0 and n>0
(D/'nominal-coaxial-conflict.json').write_text(json.dumps({'nominal_coaxial_translation_m':[-.006,.239,.0025],'nominal_surface_intersection_pairs':n,'review_translation_m':[-.006,.239,.0075],'review_surface_intersection_pairs':a,'display_axis_separation_m':.005,'finding':'The exact preserved author meshes conflict at nominal coaxial estimate. A display offset is retained instead of changing root/clevis or inventing a seat. Not measured mechanics or a prescribed functional assembly.','physical_fit_qualified':False},indent=2)+'\n')
