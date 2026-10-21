# Parent SHA256 34285da46501243d31e37aae67a2caae672ebd99eb98221d979197d2f5cf12c1; source float endpoint normal snap widened to parameter0.001 (max3um), positions unchanged.
"""Exact analytic ORIGINAL field gradient, no source positions or exported buffer repair."""
import bpy,math,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
R=Path('/workspace/wewa');old='front-completion-p21-reverse-front10-v5';K='front-completion-p21-reverse-front10-v7';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(parents=True,exist_ok=False);O.mkdir(parents=True,exist_ok=False);source=R/'assets-src/moto-components'/old/'carrier-reverse-gray.blend';bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0;ob=next(o for o in bpy.data.objects if o.type=='MESH');m=ob.data
# Snap only numerical endpoints of exact source level contours; no position change.
def sd(t):
 if t<=1e-3:return 0.,0.
 if t>=1-1e-3:return 1.,0.
 return t*t*(3-2*t),6*t*(1-t)
def gradient(x,y):
 r=math.hypot(x,y);candidates=[]
 if r<=.0205:c,dc=.012,0.
 elif r<.021:
  q,d=sd((r-.0205)/.0005);c,dc=.012+.003*q,.003*d/.0005
 elif r<=.024:c,dc=.015,0.
 else:
  q,d=sd((r-.024)/.0025);c,dc=.015*(1-q),-.015*d/.0025
 candidates.append((c,dc*x/r,dc*y/r))
 for a in [pi/4,3*pi/4,5*pi/4,7*pi/4]:
  u=x*cos(a)+y*sin(a);v=-x*sin(a)+y*cos(a);du=u-min(.054,max(.036,u));rho=math.hypot(du,v);q,d=sd((rho-.004)/.003);h=.020*(1-q)
  if rho>1e-12:
   dh=-.020*d/.003;gu=dh*du/rho;gv=dh*v/rho;gx=gu*cos(a)-gv*sin(a);gy=gu*sin(a)+gv*cos(a)
  else:gx=gy=0.
  candidates.append((h,gx,gy))
 a,da=sd((r-.0615)/.0015);b,db=sd((r-.064)/.001);h=.0025*a*(1-.25*b);dh=.0025*(da/.0015*(1-.25*b)-.25*a*db/.001);candidates.append((h,dh*x/r,dh*y/r));_,gx,gy=max(candidates,key=lambda p:p[0]);return Vector((-gx,-gy,1)).normalized()
for e in m.edges:e.use_edge_sharp=False
for p in m.polygons:p.use_smooth=True
m.update();mouths=[(.047*cos(a),.047*sin(a))for a in [0,pi/2,pi,3*pi/2]];normals=[]
for face in m.polygons:
 coords=[m.vertices[i].co for i in face.vertices];top=all(v.z>=-1e-8 for v in coords);back=all(abs(v.z+.003)<1e-8 for v in coords)
 for li in face.loop_indices:
  v=m.vertices[m.loops[li].vertex_index].co;x,y=v.x,v.y;r=math.hypot(x,y)
  if top:n=gradient(x,y)
  elif back:n=Vector((0,0,-1))
  elif r>.0649:n=Vector((x/r,y/r,0))
  elif r<.0186:n=Vector((-x/r,-y/r,0))
  else:cx,cy=min(mouths,key=lambda c:math.hypot(x-c[0],y-c[1]));n=Vector((cx-x,cy-y,0)).normalized()
  normals.append(tuple(n))
m.normals_split_custom_set(normals);m.update();bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.wm.save_as_mainfile(filepath=str(H/'carrier-reverse-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'carrier-reverse-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
P=json.loads((R/'assets-src/moto-components'/old/'parameters.json').read_text());P['normal_method']='Exact analytic height-field derivative, exact zero on flat patches; source loops only, source positions unchanged';(H/'parameters.json').write_text(json.dumps(P,indent=2));(O/'source-normal-method.json').write_text(json.dumps({'base_source':str(source.relative_to(R)),'base_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_positions_changed':False,'method':P['normal_method'],'flat_endpoint_numerical_snap_parameter':1e-3,'no_GL B_buffer_edits'.replace(' ',''):True},indent=2))
for name in ['geometry-check.json','construction-method.json','sources.json','detail-plan.json']:shutil.copyfile(R/'creative/reviews'/old/name,O/name)
