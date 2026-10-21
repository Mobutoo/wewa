import bpy,json,hashlib,sys
from pathlib import Path
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');file,out=sys.argv[sys.argv.index('--')+1:][:2];p=R/file;O=R/out;O.parent.mkdir(exist_ok=True,parents=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));bpy.context.view_layer.update();obs=[o for o in bpy.data.objects if o.type=='MESH'];trees={}
for ob in obs:
 m=ob.data;m.calc_loop_triangles();trees[ob.name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True)
pairs=[]
for i,left in enumerate(obs):
 for right in obs[i+1:]:pairs.append({'left':left.name,'right':right.name,'triangle_surface_crossing_pairs':len(trees[left.name].overlap(trees[right.name]))})
r={'actual_GL B'.replace(' ',''):file,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'imported_meshes':len(obs),'pairs':pairs,'total_crossing_pairs':sum(p['triangle_surface_crossing_pairs']for p in pairs),'scope':'Actual GLB imported independently into clean Blender; world-space triangle BVH overlap, not a global minimum clearance, electrical fit, current variant or mechanical contact proof'};O.write_text(json.dumps(r,indent=2));assert r['total_crossing_pairs']==0,r;print('ACTUAL_EXPORT_INTERFACES',len(obs),len(pairs),0)
