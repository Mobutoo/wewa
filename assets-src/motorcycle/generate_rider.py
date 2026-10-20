import bpy, math, json, os
from mathutils import Vector
OUT=os.environ.get('VIVA_WEWA_ASSET_OUTPUT',os.path.join(os.path.dirname(os.path.abspath(__file__)),'generated'));os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M={};parts=[]
def mat(name,col,rough=.6,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;M[name]=m
mat('Marine woven jacket',(.019,.034,.057),.81);mat('Grey denim',(.115,.128,.140),.88);mat('Brown skin',(.24,.105,.053),.55);mat('Black matte gear',(.012,.015,.019),.84);mat('Dark visor',(.022,.036,.041),.22,.25);mat('Stitch zip metal',(.09,.105,.12),.8,.2)
def xyz(p):return Vector((p[0],-p[2],p[1]))
def finish(o,name,m,smooth=True):
 o.name=name;o.data.materials.append(M[m]);parts.append(o)
 if smooth:
  for p in o.data.polygons:p.use_smooth=True
 return o

def ell(name,p,scale,m,segments=24,rings=12):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=xyz(p));o=bpy.context.object;o.scale=(scale[0],scale[2],scale[1]);return finish(o,name,m)
def tube(name,points,r,m,verts=8):
 for i in range(len(points)-1):
  a,b=xyz(points[i]),xyz(points[i+1]);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();finish(o,name,m)
def loft(name,rows,m,n=24,wrinkle=0):
 # rows: centre x,height,z + radius lateral and radius forward
 vs=[];fs=[]
 for j,(x,h,z,w,d) in enumerate(rows):
  for k in range(n):
   a=k*math.tau/n;f=1+wrinkle*math.sin(a*5+j*1.7);vs.append(tuple(xyz((x+w*math.cos(a)*f,h,z+d*math.sin(a)*f))))
 for j in range(len(rows)-1):
  for k in range(n):a=j*n+k;b=j*n+(k+1)%n;fs.append((a,b,b+n,a+n))
 fs.extend([tuple(reversed(range(n))),tuple((len(rows)-1)*n+k for k in range(n))])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return finish(o,name,m)
def limb(name,a,b,rad1,rad2,m,wrinkle=.01,n=18):
 aa=Vector(a);bb=Vector(b);axis=(bb-aa).normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<.1:u=axis.cross(Vector((1,0,0)))
 u.normalize();v=axis.cross(u);vs=[];fs=[]
 for j in range(7):
  t=j/6;c=aa.lerp(bb,t);r=rad1*(1-t)+rad2*t
  r*=.91+.09*math.sin(math.pi*t)
  for k in range(n):
   a0=k*math.tau/n;rr=r*(1+wrinkle*math.sin(a0*4+j*1.9));p=c+rr*(u*math.cos(a0)+v*math.sin(a0));vs.append(tuple(xyz(p)))
 for j in range(6):
  for k in range(n):a0=j*n+k;b0=j*n+(k+1)%n;fs.append((a0,b0,b0+n,a0+n))
 fs.extend([tuple(reversed(range(n))),tuple(6*n+k for k in range(n))]);mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return finish(o,name,m)
def cloth_path(name, controls, material, n=20):
 # Smooth Catmull-Rom centreline and radius; single continuous bent fabric tube.
 points=[Vector(p[:3]) for p in controls];radii=[p[3] for p in controls]
 vs=[];fs=[];samples=[]
 for i in range(len(points)-1):
  p0=points[max(0,i-1)];p1=points[i];p2=points[i+1];p3=points[min(len(points)-1,i+2)]
  for k in range(5):
   t=k/5;t2=t*t;t3=t2*t
   pos=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t2+(-p0+3*p1-3*p2+p3)*t3)
   r=radii[i]*(1-t)+radii[i+1]*t
   samples.append((pos,r))
 samples.append((points[-1],radii[-1]))
 for j,(c,r) in enumerate(samples):
  axis=(samples[min(j+1,len(samples)-1)][0]-samples[max(0,j-1)][0]).normalized()
  u=axis.cross(Vector((0,0,1)))
  if u.length<.1:u=axis.cross(Vector((1,0,0)))
  u.normalize();v=axis.cross(u)
  for k in range(n):
   a=k*math.tau/n
   fold=1+.024*math.sin(a*4+j*.8)+.01*math.cos(a*7-j*.7)
   pos=c+r*fold*(u*math.cos(a)+v*math.sin(a))
   vs.append(tuple(xyz(pos)))
 for j in range(len(samples)-1):
  for k in range(n):a=j*n+k;b=j*n+(k+1)%n;fs.append((a,b,b+n,a+n))
 fs.extend([tuple(reversed(range(n))),tuple((len(samples)-1)*n+k for k in range(n))])
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return finish(o,name,material)
def fabric_pack(name, rows, material):
 # Rounded rectangular superellipse, flatter than an ellipsoid, with soft sewing irregularities.
 n=32;vs=[];fs=[]
 for j,(h,z,w,d) in enumerate(rows):
  for k in range(n):
   a=k*math.tau/n;c=math.cos(a);si=math.sin(a)
   xx=w*math.copysign(abs(c)**.52,c);zz=d*math.copysign(abs(si)**.52,si)
   vs.append(tuple(xyz((xx,h+.0015*math.sin(a*3+j),z+zz))))
 for j in range(len(rows)-1):
  for k in range(n):a=j*n+k;b=j*n+(k+1)%n;fs.append((a,b,b+n,a+n))
 fs.extend([tuple(reversed(range(n))),tuple((len(rows)-1)*n+k for k in range(n))])
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return finish(o,name,material)
# Seated hips rest on 0.80 m saddle, original human-scale silhouette.
loft('Seated trouser hips',[(0,.807,-.105,.105,.072),(0,.835,-.107,.143,.086),(0,.88,-.096,.146,.093),(0,.927,-.075,.134,.084)],'Grey denim',28,.02)
# Neck, chest, waist: lean toward handlebar.
loft('Jacket torso',[(0,.865,-.115,.145,.103),(0,.90,-.085,.149,.108),(0,.94,-.055,.155,.115),(0,1.015,-.008,.158,.112),(0,1.075,.018,.149,.113),(0,1.16,.054,.17,.121),(0,1.26,.09,.205,.122),(0,1.34,.111,.216,.108),(0,1.38,.121,.185,.094),(0,1.425,.13,.095,.071)],'Marine woven jacket',28,.025)
# Hem, collar, fabric creases represented by the surface rhythm, no graphic texture.
loft('Jacket hem',[(0,.921,-.075,.149,.111),(0,.938,-.065,.154,.115),(0,.953,-.054,.151,.111)],'Marine woven jacket',24,.016)
loft('Soft collar',[(0,1.398,.126,.082,.068),(0,1.43,.132,.076,.060),(0,1.451,.134,.068,.057)],'Marine woven jacket',24)
ell('Neck',(0,1.46,.132),(.062,.067,.057),'Brown skin',20,10)
# Arms and legs with articulated rounded joints.
for s in [-1,1]:
 shoulder=(s*.195,1.315,.102);elbow=(s*.291,1.105,.285);wrist=(s*.307,1.028,.489)
 cloth_path('Continuous jacket sleeve',[(s*.16,1.325,.105,.082),(s*.205,1.301,.119,.075),(s*.254,1.212,.19,.069),(s*.291,1.115,.278,.061),(s*.303,1.078,.37,.054),(s*.307,1.028,.489,.040)],'Marine woven jacket',24)
 # Curled hands hold grips. Individual joined fingers are rounded and subtle.
 ell('Hand palm',(s*.31,1.020,.519),(.040,.025,.043),'Brown skin',20,10)
 for k in range(4):
  xx=s*(.287+k*.014)
  limb('Curled fingers',(xx,1.02,.536),(xx,1.001,.545),.009,.008,'Brown skin',0,10)
 ell('Thumb',(s*.277,1.035,.523),(.014,.016,.025),'Brown skin',12,8)
 hip=(s*.112,.868,-.100);knee=(s*.194,.568,.268);ankle=(s*.172,.321,-.090)
 cloth_path('Continuous bent trouser leg',[(s*.104,.875,-.104,.095),(s*.139,.785,.02,.094),(s*.174,.666,.174,.083),(s*.191,.586,.245,.075),(s*.193,.549,.242,.073),(s*.188,.474,.157,.065),(s*.178,.367,-.034,.052),(s*.172,.307,-.102,.048)],'Grey denim',24)
 # Boot-to-sneaker profile and heel, black; foot sits near working footpeg.
 shoe=ell('Black shoe',(s*.172,.285,-.025),(.060,.045,.128),'Black matte gear',24,10)
 ell('Shoe sole',(s*.172,.252,-.025),(.061,.015,.126),'Black matte gear',22,8)
 # Outer seam down jeans, very dark and thin, not bright piping.
 tube('Denim seam',[(s*.201,.77,.05),(s*.257,.59,.254),(s*.229,.455,.11),(s*.218,.335,-.074)],.0017,'Marine woven jacket',6)
# Helmeted head: no photographic face, restrained adult proportions.
ell('Head under helmet',(0,1.573,.145),(.087,.116,.088),'Brown skin',24,12)
loft('Matte black helmet shell',[(0,1.535,.136,.094,.096),(0,1.55,.136,.105,.107),(0,1.59,.136,.112,.113),(0,1.638,.136,.108,.109),(0,1.69,.136,.094,.094),(0,1.729,.136,.066,.065),(0,1.751,.136,.027,.027),(0,1.756,.136,.003,.003)],'Black matte gear',32)
# Visor front (not visible in rear view), brow + chin guard.
ell('Dark face visor',(0,1.627,.219),(.092,.069,.031),'Dark visor',28,12)
loft('Helmet lower rim',[(0,1.532,.136,.093,.095),(0,1.539,.136,.100,.102),(0,1.548,.136,.102,.104)],'Black matte gear',28)
# Fabric backpack follows leaned spine, broad flat panels with soft rectangular corners.
fabric_pack('Flat fabric backpack',[(1.005,-.145,.09,.019),(1.018,-.147,.117,.030),(1.046,-.139,.128,.040),(1.13,-.112,.132,.043),(1.235,-.077,.128,.043),(1.31,-.051,.118,.035),(1.337,-.041,.105,.025),(1.345,-.038,.085,.017)],'Black matte gear')
fabric_pack('Backpack flat outer pocket',[(1.035,-.184,.076,.006),(1.048,-.185,.101,.012),(1.105,-.169,.104,.015),(1.165,-.150,.098,.012),(1.18,-.145,.08,.005)],'Black matte gear')
# Rounded top carry loop and subdued stitch/zip perimeter.
tube('Backpack carry loop',[(-.035,1.34,-.049),(-.029,1.377,-.038),(.029,1.377,-.038),(.035,1.34,-.049)],.004,'Black matte gear',8)
# Tubular webbing is flattened along the torso to read as fabric straps, no block shoulders.
for s in [-1,1]:
 loft('Backpack shoulder strap',[(s*.123,1.014,-.023,.016,.009),(s*.151,1.12,.166,.020,.010),(s*.156,1.25,.206,.020,.009),(s*.13,1.35,.175,.020,.010),(s*.102,1.386,.092,.019,.010),(s*.10,1.34,-.016,.019,.01)],'Black matte gear',10)
 tube('Backpack zip',[(s*.115,1.065,-.180),(s*.12,1.18,-.144),(s*.109,1.30,-.094)],.0012,'Stitch zip metal',6)
# Jacket centre zip follows chest. Tiny seams and puller.
tube('Jacket front zipper',[(0,.96,.057),(0,1.055,.126),(0,1.16,.177),(0,1.26,.214),(0,1.36,.212),(0,1.42,.19)],.0018,'Stitch zip metal',6)
ell('Zip puller',(0,1.374,.212),(.004,.009,.002),'Stitch zip metal',8,6)
# Weld intersecting torso/sleeve and trouser components into continuous fabric surfaces.
# The union prevents shoulder spheres, elbow seams and mannequin-like knee balls.
for cloth in ['Marine woven jacket','Grey denim']:
 objs=[o for o in parts if o.data.materials[0].name==cloth]
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 # Explicit outward winding before signed-volume remesh.
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
 o.data.remesh_voxel_size=.0075;bpy.ops.object.voxel_remesh()
 mod=o.modifiers.new('Relax cloth seams','SMOOTH');mod.factor=.45;mod.iterations=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 for face in o.data.polygons:face.use_smooth=True
 # Replace invalid joined objects in source registry immediately.
 parts=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
# Assembly per material, preserves a small draw-call budget.
by={m:[o for o in parts if o.data.materials[0].name==m] for m in M}
meshes=[]
for m,items in by.items():
 if not items:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in items:o.select_set(True)
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name='rider_'+m.lower().replace(' ','_');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);meshes.append(o)
bpy.context.view_layer.update();tri=0
for o in meshes:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
# fit strict prototype budget using conservative collapse for hidden rounded surfaces if needed
if tri>14900:
 cloth_meshes=[o for o in meshes if o.data.materials[0].name in ['Marine woven jacket','Grey denim']]
 static_meshes=[o for o in meshes if o not in cloth_meshes]
 # Keep hands and helmet/backpack contours well resolved; allocate 14600 total triangles.
 static_count=sum(len(o.data.loop_triangles) for o in static_meshes)
 cloth_count=sum(len(o.data.loop_triangles) for o in cloth_meshes)
 ratio=max(.025,min(1,(14600-static_count)/cloth_count))
 for o in cloth_meshes:
  mod=o.modifiers.new('Continuous fabric detail budget','DECIMATE');mod.ratio=ratio;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 tri=0
 for o in meshes:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT+'/rider.glb',export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
report={'asset':'Viva Wewa seated adult rider','status':'original-prototype-needs-art-review','triangles':tri,'materials':len(M),'meshes':len(meshes),'revision':'continuous-cloth-v2','provenance':'Original procedural Blender geometry with welded continuous jacket/trousers, flattened sewn fabric backpack and solid rough PBR materials; no photographic textures, logos or external mesh. User description: navy jacket, grey denim, black shoes, dark backpack, brown hands, matte black helmet.','coordinates':'GLB X right, Y up, +Z forward; origin motorcycle ground0; seated hips .875m with lowest pelvis near saddle .80m.','anchor_positions_m':{'hips':[0,.875,-.12],'hand_left':[-.31,1.02,.519],'hand_right':[.31,1.02,.519],'shoe_centres':[[-.172,.285,-.025],[.172,.285,-.025]],'helmet_centre':[0,1.635,.136]},'limitations':['No armature/animation; posed static model for first implementation.','Photographic realism not claimed; continuous fabric silhouette requires in-game art review.','Rider feet rest near pegs; legs and tank overlap should be checked in combined game scene.']}
open(OUT+'/provenance.json','w').write(json.dumps(report,indent=2))
# Preview on motorcycle: reference mesh only in .blend preview scene, not exported rider GLB.
bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../app/public/models/motorcycle.glb'))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));ground=bpy.context.object;gm=bpy.data.materials.new('Preview ground');gm.diffuse_color=(.10,.12,.14,1);ground.data.materials.append(gm)
for loc,power,size in [((3,-3,5),1000,4),((-3,-1,4),850,4),((0,4,3),700,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,.9))-o.location).to_track_quat('-Z','Y').to_euler()
# Rear quarter, showing the passenger silhouette and believable posture.
bpy.ops.object.camera_add(location=(2.6,3.8,2.1));c=bpy.context.object;c.rotation_euler=(Vector((0,0,.91))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=2.7
s=bpy.context.scene;s.camera=c;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=OUT+'/preview-on-motorcycle.png';s.world.color=(.25,.25,.25);s.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/rider.blend');bpy.ops.render.render(write_still=True)
print(json.dumps(report))
