"""Read-only sampling of original curved skin versus original bolt-pad top planes."""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];source=H/'engine-cover-left-v1.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)=='7e27606ef19b7a49e932ac13841b1da15c6d0d4936f1cef8f095bb233c3ce1d4';P=json.loads((H/'parameters.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(source));base=bpy.data.objects['LH original asymmetric hollow loft construction'];m=base.data;tree=BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);rows=[]
for k in range(3):
 c=bpy.data.objects['LH visible fixation collar candidate '+str(k+1)];u,v=c.location.x,c.location.y;top=c.location.z+c.dimensions.z/2;values=[];outside=0
 for radius in [.0033,.0044,.0055]:
  for i in range(128):
   a=math.tau*i/128;p=Vector((u+radius*math.cos(a),v+radius*math.sin(a),.11));hit=tree.ray_cast(p,Vector((0,0,-1)),.15)
   if hit[0] is None:outside+=1
   else:values.append(hit[0].z)
 rows.append({'station':k+1,'centre_local_uv_m':[u,v],'original_pad_top_w_m':top,'original_base_skin_w_min_max_m':[min(values),max(values)],'sampled_original_base_above_pad_top':sum(x>top+1e-6 for x in values),'sample_count_hit':len(values),'outside_base_samples':outside,'max_base_projection_above_pad_m':max(values)-top,'all_dimensions_estimated':True})
o=bpy.data.objects['LH magneto cover hollow casting - editable candidate'];j={'source_sha256':sha(source),'historical_source_not_modified':True,'custom_normals_present':o.data.has_custom_normals,'construction_mesh_actually_sampled':'LH original asymmetric hollow loft construction','method':'384front rays per collar annulus, actual original source skin versus original collar plane; no physical measurement','stations':rows,'interpretation':'A collar top set1mm above the skin only at its centre can be cut by the rising curved skin around it; no conclusion yet about OEM pad height','art_accepted':False};out=R/'creative/research/engine-cover-left/fixation-diagnostic-v2.json';out.write_text(json.dumps(j,indent=2)+'\n');print('WEWA_LH_FIXATION_DIAG',json.dumps(j))
