"""Read-only authored sweep versus actual cornernormal audit, no render."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa-github');H=R/'assets-src/moto-components/frame/front-backbone-v2';O=R/'creative/reviews/frame-front-backbone-v2';P=json.loads((H/'parameters.json').read_text());src=H/'frame-front-backbone-v2.blend';bpy.ops.wm.open_mainfile(filepath=str(src));o=list(bpy.data.collections['WEWA_FRAME_FRONT_BACKBONE_ISOLATED'].objects)[0];m=o.data;m.update()
def state(t):
 u=1-t;a=Vector((0,0,0));b=Vector((0,.13,-.035));c=Vector((0,.3,-.12));d=Vector((0,P['length_working_m'],-P['rear_drop_working_m']));C=u**3*a+3*u*u*t*b+3*u*t*t*c+t**3*d;D=3*u*u*(b-a)+6*u*t*(c-b)+3*t*t*(d-c);DD=6*u*(c-2*b+a)+6*t*(d-2*c+b);T=D.normalized();DT=(DD-T*T.dot(DD))/D.length;V=Vector((0,-T.z,T.y));DV=Vector((0,-DT.z,DT.y));return C,D,DD,V,DV

def project(q):
 t=max(0,min(1,q.y/P['length_working_m']))
 for _ in range(15):
  C,D,DD,V,DV=state(t);f=(q-C).dot(D);fp=-D.dot(D)+(q-C).dot(DD)
  if abs(fp)<1e-12:break
  t=max(0,min(1,t-f/fp))
 C,D,DD,V,DV=state(t);return t,(q-C).dot(V),C,D,V,DV
rows=[];ids=set()
for f in m.polygons:
 q=f.center;t,v,C,D,V,DV=project(q);w=(P['front_outer_width_m']*(1-t)+P['rear_outer_width_m']*t)/2;hh=(P['front_outer_height_m']*(1-t)+P['rear_outer_height_m']*t)/2
 if not(.005<q.y<.07 and abs(q.x-w)<.00003 and abs(v)<hh-P['corner_radius_working_m']-.0001 and f.normal.x>.8):continue
 for li in f.loop_indices:
  loop=m.loops[li];q=m.vertices[loop.vertex_index].co;t,v,C,D,V,DV=project(q);Ft=D+DV*v+Vector(((P['rear_outer_width_m']-P['front_outer_width_m'])/2,0,0));expected=Ft.cross(V).normalized();actual=m.corner_normals[li].vector;err=math.degrees(math.atan2(actual.cross(expected).length,actual.dot(expected)));rows.append({'face':f.index,'loop':li,'vertex':loop.vertex_index,'position_m':list(q),'actual_normal':list(actual),'authored_sweep_side_normal':list(expected),'error_degrees':err,'t':t,'crosssection_v_m':v});ids.add(f.index)
assert rows
out={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'method':'Analytical side of original swept rounded-rect profile, closest crosssection Newton solve, actual Blendercorner normals; no source alteration','region':'Outer+X broadwall,Y5..70mm beforefirstsidefeature, corners of matchingflatwall triangles','sample_loops':len(rows),'sample_faces':len(ids),'maximum_error_degrees':max(x['error_degrees']for x in rows),'minimum_error_degrees':min(x['error_degrees']for x in rows),'worst_samples':sorted(rows,key=lambda x:x['error_degrees'],reverse=True)[:24],'custom_normals_present':m.has_custom_normals,'source_geometry_or_normals_modified':False,'manufacturer_shape_or_accuracy_claimed':False};(O/'source-normal-audit.json').write_text(json.dumps(out,indent=2)+'\n');print('WEWA_BACKBONE_SOURCE_NORMALS',out['sample_loops'],out['maximum_error_degrees'],out['minimum_error_degrees'])
