"""Actual evaluated hub sections and bounded cut evidence, not measured dimensions."""
from pathlib import Path
import bpy,json,math,hashlib,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/kickstarter-v2';source=H/'kickstarter-v2.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source));o=bpy.data.objects['Kick split mounting clamp and clevis - fixed candidate'];mesh=o.data;tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(p.vertices)for p in mesh.polygons]);report={'source_sha256':before,'actual_fixed_mesh_exercised':True,'sections':[],'restored_lower_web_probes':[],'physical_measurement':False,'art_accepted':False}
# Exclude radial directions inside the real open pinch slit (negativev).
for w in [-.009,.004,.017]:
 rows=[]
 for i in range(112):
  a=math.tau*i/112;d=Vector((math.cos(a),math.sin(a),0));hit,n,idx,dist=tree.ray_cast(Vector((0,0,w)),d,.05)
  inside_slit=d.y<0 and abs(d.x)<.10
  if not inside_slit:assert hit is not None and .00749<dist<.00786,(w,i,dist)
  rows.append({'angle_deg':i*360/112,'distance_m':dist,'excluded_open_slit':inside_slit})
 report['sections'].append({'local_w_m':w,'rays':rows})
# True shaft bore central ray must pass all hub thickness.
hit,_,_,dist=tree.ray_cast(Vector((0,0,-.012)),Vector((0,0,1)),.034);assert hit is None,(hit,dist);report['hub_centre_axis_open']=True
# Outside hub, lower web is restored and uncut by the original overlong cutters.
for w in [.025,.030]:
 start=Vector((0,-.015,w));hit,_,_,dist=tree.ray_cast(start,Vector((0,1,0)),.03);assert hit is not None and -.006<hit.y<-.0005,(w,hit)
 report['restored_lower_web_probes'].append({'ray_start_local_m':list(start),'hit_local_m':list(hit),'distance_m':dist})
assert sha(source)==before;(O/'hub-section-check.json').write_text(json.dumps(report,indent=2)+'\n');print('HUB_CHECK',len(report['sections'])*112,'rays',report['hub_centre_axis_open'],report['restored_lower_web_probes'])
