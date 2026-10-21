"""Single DH151029 photographed exterior hypothesis; no repeated product copies or invented grade/pin."""
import bpy,bmesh,math,json,runpy
from pathlib import Path
from math import sin,cos,pi
R=Path('/workspace/wewa');K='front-completion-p23-torque-bolt-front10-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(parents=True,exist_ok=False);O.mkdir(parents=True,exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True)
U=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));globals().update({k:v for k,v in U.items()if not k.startswith('__')})
P=json.loads((R/'creative/research/front-completion-p23-v1/torque-bolt-G0-G2.json').read_text());P.update({'frame':'Local Z from head outerface0 to tip32mm; object rotatedY=-90deg so exposed photographed bore faces world+Z; not installed','mouth':'One positive-local-X exterior mouth, open inner axial-plane review cut atX=0; opposite exit unknown','grade_marks':'Unreadable, none built','pin':'Not built; type and fitted position not known','thread':'Right hand author hypothesis, no standard/fit certification','finish':'Uniform silver clean-metal estimate; photo yellow/green passivation not reproduced','all_metric_values_estimated':True});(H/'parameters.json').write_text(json.dumps(P,indent=2))
profile=[(0,.0060,'hex'),(.0005,.0065,'hex'),(.0045,.0065,'hex'),(.005,.0060,'hex'),(.005,.0050,'circle'),(.0054,.0050,'circle'),(.0167,.0050,'circle'),(.0174,.0046,'circle'),(.018,.004,'circle')]
steps=672
for i in range(1,steps+1):profile.append((.018+.014*i/steps,None,'thread'))
n=384;v=[];f=[]
for z,r,kind in profile:
 for j in range(n):
  a=2*pi*(j+.173)/n
  if kind=='hex':rr=r/cos((a+pi/6)%(pi/3)-pi/6)
  elif kind=='thread':
   d=abs(((z-.018)/.00125-a/(2*pi))%1-.5);env=min(1,max(0,(z-.018)/.00125),max(0,(.032-z)/.0005));rr=.004-.00055*smooth((d-.10)/.32)*env
   if z>.0315:rr-=.0004*(z-.0315)/.0005
  else:rr=r
  v.append((rr*cos(a),rr*sin(a),z))
for i in range(len(profile)-1):
 for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
for row,z,rev in [(0,0,True),(len(profile)-1,.032,False)]:
 c=len(v);v.append((0,0,z))
 for j in range(n):a=row*n+j;b=row*n+(j+1)%n;f.append((c,b,a)if rev else(c,a,b))
ob=mesh_object('DH151029_SINGLE_HEX_SHOULDER_THREAD_OPEN_MOUTH_STUDY',v,f);bpy.context.view_layer.objects.active=ob
bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=.0012,depth=.040,location=(.020,0,.029),rotation=(0,pi/2,0));boolean(ob,bpy.context.object)
bm=bmesh.new();bm.from_mesh(ob.data);caps=[face for face in bm.faces if all(abs(v.co.x)<1e-7 for v in face.verts)and abs(face.normal.x)>.99];assert caps,'Missing deliberate axial review cap';bmesh.ops.delete(bm,geom=caps,context='FACES');bm.to_mesh(ob.data);bm.free();row=clean_audit(ob,128)
# Sharp hex flats and face retained, cylinder/thread smooth; no weighted/buffer repair.
for p in ob.data.polygons:
 if p.center.z<.00499:p.use_smooth=False
ob.rotation_euler[1]=-pi/2;gray_save(H,'torque-bolt',[ob]);(O/'geometry-check.json').write_text(json.dumps({'objects':[row],'one_visible_mouth_only':True,'inner_bore_review_cut_local_X_m':0,'head_marks_built':False,'separate_pin_built':False,'all_metric_values_estimated':True},indent=2));print(row)
