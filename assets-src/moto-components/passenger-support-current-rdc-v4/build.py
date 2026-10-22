import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;R=O.parents[2];S=json.loads((O/'spec.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda n,d:(O/n).write_text(json.dumps(d,indent=2)+'\n')
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene;s.unit_settings.system='METRIC';group=bpy.data.collections.new('CURRENT_RDC_PASSENGER_SUPPORT_V4');s.collection.children.link(group)
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
objects=[];traces=[]
for side in ['LH','RH']:
 for role,key in [('rear-sideguard','guard_trace_px_x_m'),('forward-peg-support','front_support_trace_px_x_m')]:
  pts=[pixel(side,x,y,z)for x,y,z in S[side][key]];ob,path=tube(side+' CURRENT_RDC '+role+' observed',pts);objects.append(ob);traces.append({'name':ob.name,'side':side,'role':role,'pixel_depth_samples':S[side][key],'world_control_samples_m':[list(v)for v in pts],'actual_sweep_centres_m':[list(v)for v in path],'ends_open_visible_cuts':True})
# Only two repeated, documentarily qty2 existing common exemplars. Native geometry/materials unchanged.
for side in ['LH','RH']:
 q=S[side];hinge=pixel(side,*q['peg_hinge_px'],q['peg_hinge_X_m']);sign=q['outward_sign'];theta=math.radians(75);axisX=Vector((sign*math.cos(theta),math.sin(theta)*2**-.5,math.sin(theta)*2**-.5));axisZ=Vector((0,sign*2**-.5,-sign*2**-.5));axisY=axisZ.cross(axisX);rot=Matrix((axisX,axisY,axisZ)).transposed();M=rot.to_4x4();M.translation=hinge-rot@Vector((.012,0,0))
 for role,folder,name,offset in [('peg','passenger-footpeg-metal-v1','PASSENGER_PEG_SHAPED_ROOT_FLANGE_AND_STOP_TAB',0),('rubber','passenger-footrest-rubber-jk113008-v1','JK113008_PASSENGER_RUBBER_VISIBLE_ENVELOPE_ONLY',.026)]:
  p=R/'assets-src/moto-components'/folder/'child-candidate.blend'
  with bpy.data.libraries.load(str(p),link=True)as(a,b):b.objects=[name]
  orig=b.objects[0];ob=orig.copy();ob.parent=None;ob.name=side+' '+role+' unchanged original';group.objects.link(ob);ob.matrix_world=M@Matrix.Translation((offset,0,0));ob['source']=str(p.relative_to(R));ob['source_object']=name;ob['side']=side;ob['role']=role;ob['hinge_world']=hinge;objects.append(ob)
bpy.context.view_layer.update();write('observed-traces.json',traces)
# Save standalone new observed tube source first; only four original new meshes, no old donor stays.
newcol=bpy.data.collections.new('CURRENT_RDC_OBSERVED_TUBES_V4')
for ob in objects[:4]:newcol.objects.link(ob)
bpy.data.libraries.write(str(O/'current-rdc-observed-tubes.blend'),{newcol},fake_user=True,compress=True)
# Source-writing invalidates live4.3.2 namemap; reopen source before assembling final pair in another pass.
write('peg-matrices.json',[{'key':ob.name,'source':ob['source'],'sha256':sha(R/ob['source']),'selected_objects':[ob['source_object']],'matrix_world':[list(r)for r in ob.matrix_world],'hinge_world_m':list(ob['hinge_world']),'side':ob['side'],'role':ob['role'],'nested':[],'source_class':'documented_related_variant mesh / photo_inferred pose with estimated X'}for ob in objects[4:]])
write('new-tube-identities.json',[{'key':ob.name,'selected_objects':[ob.name],'matrix_world':[list(r)for r in ob.matrix_world],'source_class':ob['source_class']}for ob in objects[:4]])
print('OBSERVED_SOURCE_READY',len(objects),[list(pixel(side,*S[side]['peg_hinge_px'],S[side]['peg_hinge_X_m']))for side in ['LH','RH']])
