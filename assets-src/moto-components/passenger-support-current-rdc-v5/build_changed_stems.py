import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;R=O.parents[2];S=json.loads((O/'spec.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda n,d:(O/n).write_text(json.dumps(d,indent=2)+'\n')
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene;s.unit_settings.system='METRIC';group=bpy.data.collections.new('CURRENT_RDC_UPPER_CUT_CORRECTION_V5');s.collection.children.link(group)
mat=bpy.data.materials.new('Current RDC visible black tube estimated clean coating');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.015,.018,.021,1);bs.inputs['Metallic'].default_value=.3;bs.inputs['Roughness'].default_value=.34

def pixel(side,x,y,depth):
 q=S[side];k=q['scale_m_per_px'];u,v=q['rear_axle_px'];return Vector((depth,.865+(x-u)*k*(1 if side=='LH'else-1),-.74+(v-y)*k))

def pathrounded(pts,r):
 path=[pts[0]]
 for i in range(1,len(pts)-1):
  p0,p,p2=pts[i-1:i+2];a=(p0-p).normalized();b=(p2-p).normalized();angle=a.angle(b)
  if abs(math.pi-angle)<.03:continue
  tangent=min(r/max(math.tan(angle/2),.1),(p0-p).length*.32,(p2-p).length*.32);u=p+a*tangent;v=p+b*tangent;center=p+(a+b).normalized()*tangent/math.cos(angle/2);rad=u-center;end=v-center;axis=rad.cross(end).normalized();arc=rad.angle(end);distance=(u-path[-1]).length
  for j in range(1,max(2,int(distance/.006))+1):path.append(path[-1].lerp(u,1/(max(2,int(distance/.006))-j+1)))
  for j in range(1,13):path.append(center+Matrix.Rotation(arc*j/12,3,axis)@rad)
 last=path[-1];d=(pts[-1]-last).length
 for j in range(1,max(2,int(d/.006))+1):path.append(last.lerp(pts[-1],j/max(2,int(d/.006))))
 return path

def tube(name,points):
 path=pathrounded(points,S['construction']['working_corner_radius_m']);N=48;rad=S['construction']['tube_outer_diameter_m']/2;wall=S['construction']['working_wall_m'];vs=[];fs=[]
 for k,p in enumerate(path):
  t=(path[min(k+1,len(path)-1)]-path[max(0,k-1)]).normalized();a=Vector((1,0,0));a=(a-t*a.dot(t)).normalized();b=t.cross(a).normalized()
  for rr in [rad,rad-wall]:
   for j in range(N):ang=j*math.tau/N;vs.append(p+rr*(a*math.cos(ang)+b*math.sin(ang)))
 for k in range(len(path)-1):
  for j in range(N):
   a=k*N*2+j;b=k*N*2+(j+1)%N;c=b+N*2;d=a+N*2;fs.extend([(a,b,c,d),(a+N,d+N,c+N,b+N)])
 for k in [0,len(path)-1]:
  for j in range(N):a=k*N*2+j;b=k*N*2+(j+1)%N;fs.append((a,a+N,b+N,b)if k==0 else(a,b,b+N,a+N))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);group.objects.link(ob);me.materials.append(mat)
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False)
 for p in me.polygons:p.use_smooth=True
 ob['source_class']='photo_inferred contour / estimated depth, section, bend and material';ob['scope']='Observed open-end visible cut, no hidden connectors, code not identified';return ob,path

rows=[]
for side in ['LH','RH']:
 pts=[pixel(side,x,y,z)for x,y,z in S[side]['front_support_trace_px_x_m']];ob,path=tube(side+' CURRENT_RDC forward-peg-support observed',pts);rows.append({'key':ob.name,'side':side,'control_samples_m':[list(v)for v in pts],'sweep_centres_m':[list(v)for v in path]})
write('changed-traces.json',rows)
bpy.data.libraries.write(str(O/'upper-cut-correction-v5.blend'),{group},fake_user=True,compress=True)
print('V5_TWO_STEMS_READY')
