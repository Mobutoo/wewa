"""Source-only evaluated WeightedNormal bake with exact geometry/UV preservation."""
import bpy,hashlib,json
from pathlib import Path
def apply_source_weighting(o,construction):
 def geometry(m):
  return {'positions':[tuple(v.co)for v in m.vertices],'faces':[tuple(f.vertices)for f in m.polygons],'UV':[[tuple(x.uv)for x in layer.data]for layer in m.uv_layers]}
 before=geometry(o.data);mod=o.modifiers.new('V2 source FaceAreaCornerAngle weighting, keepSharp','WEIGHTED_NORMAL');mod.mode='FACE_AREA_WITH_ANGLE';mod.weight=50;mod.keep_sharp=True;mod.thresh=.01
 param=o.copy();param.data=o.data.copy();param.name='Retained editable originalmesh with sourceweightednormalmodifier';construction.objects.link(param);param.hide_render=True;param.hide_set(True)
 deps=bpy.context.evaluated_depsgraph_get();m=bpy.data.meshes.new_from_object(o.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps);assert geometry(m)==before,'Normalsoperation changed geometryorUV';o.modifiers.clear();o.data=m;m.update();assert m.has_custom_normals
 return {'method':'BlenderWeightedNormal evaluated and baked in source; originalmodifier retainedhidden','mode':'FACE_AREA_WITH_ANGLE','weight':50,'keep_sharp':True,'threshold':.01,'exact_positions_faces_and_UV_preserved':True,'source_custom_normals_intentional':True,'GLB_buffers_repaired':False}
