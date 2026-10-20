import bpy, math, json, os
from mathutils import Vector
OUT=os.environ.get('VIVA_WEWA_ASSET_OUTPUT',os.path.join(os.path.dirname(os.path.abspath(__file__)),'generated','rider'))
os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M={};parts=[]
def mat(name,col,rough=.6,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;M[name]=m
mat('Marine woven jacket',(.019,.034,.057),.81);mat('Grey denim',(.115,.128,.140),.88);mat('Brown skin',(.24,.105,.053),.55);mat('Black matte gear',(.012,.015,.019),.66);mat('Dark visor',(.022,.036,.041),.22,.25);mat('Stitch zip metal',(.24,.27,.29),.5,.55)
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
# Seated hips rest on 0.80 m saddle, original human-scale silhouette.
ell('Seated pelvis',(0,.875,-.12),(.155,.095,.135),'Grey denim')
# Neck, chest, waist: lean toward handlebar.
loft('Jacket torso',[(0,.90,-.085,.135,.105),(0,.94,-.055,.155,.115),(0,1.015,-.008,.158,.112),(0,1.075,.018,.149,.113),(0,1.16,.054,.17,.121),(0,1.26,.09,.205,.122),(0,1.34,.111,.216,.108),(0,1.38,.121,.185,.094),(0,1.425,.13,.095,.071)],'Marine woven jacket',28,.025)
# Hem, collar, fabric creases represented by the surface rhythm, no graphic texture.
loft('Jacket hem',[(0,.921,-.075,.149,.111),(0,.938,-.065,.154,.115),(0,.953,-.054,.151,.111)],'Marine woven jacket',24,.016)
loft('Soft collar',[(0,1.398,.126,.082,.068),(0,1.43,.132,.076,.060),(0,1.451,.134,.068,.057)],'Marine woven jacket',24)
ell('Neck',(0,1.46,.132),(.062,.067,.057),'Brown skin',20,10)
# Arms and legs with articulated rounded joints.
for s in [-1,1]:
 shoulder=(s*.195,1.315,.102);elbow=(s*.291,1.105,.285);wrist=(s*.307,1.028,.489)
 ell('Shoulder cloth',shoulder,(.080,.086,.084),'Marine woven jacket',20,10)
 limb('Upper jacket sleeve',shoulder,elbow,.076,.064,'Marine woven jacket',.045)
 ell('Elbow cloth',elbow,(.061,.063,.064),'Marine woven jacket',18,8)
 limb('Forearm sleeve',elbow,wrist,.062,.044,'Marine woven jacket',.035)
 limb('Sleeve cuff',(s*.307,1.037,.468),(s*.308,1.023,.494),.046,.042,'Marine woven jacket',.015,16)
 # Curled hands hold grips. Individual joined fingers are rounded and subtle.
 ell('Hand palm',(s*.31,1.020,.519),(.040,.025,.043),'Brown skin',20,10)
 for k in range(4):
  xx=s*(.287+k*.014)
  limb('Curled fingers',(xx,1.02,.536),(xx,1.001,.545),.009,.008,'Brown skin',0,10)
 ell('Thumb',(s*.277,1.035,.523),(.014,.016,.025),'Brown skin',12,8)
 hip=(s*.112,.868,-.100);knee=(s*.194,.568,.268);ankle=(s*.172,.321,-.090)
 limb('Denim thigh',hip,knee,.103,.078,'Grey denim',.032,22)
 ell('Folded knee',knee,(.078,.081,.082),'Grey denim',22,10)
 limb('Denim calf',knee,ankle,.074,.050,'Grey denim',.027,20)
 limb('Jean cuff',(s*.172,.341,-.071),(s*.172,.305,-.102),.052,.050,'Grey denim',.012,18)
 # Boot-to-sneaker profile and heel, black; foot sits near working footpeg.
 shoe=ell('Black shoe',(s*.172,.285,-.025),(.060,.045,.128),'Black matte gear',24,10)
 ell('Shoe sole',(s*.172,.252,-.025),(.061,.015,.126),'Black matte gear',22,8)
 # Outer seam down jeans, very dark and thin, not bright piping.
 tube('Denim seam',[(s*.201,.77,.05),(s*.257,.59,.254),(s*.229,.455,.11),(s*.218,.335,-.074)],.0017,'Marine woven jacket',6)
# Helmeted head: no photographic face, restrained adult proportions.
ell('Head under helmet',(0,1.573,.145),(.087,.116,.088),'Brown skin',24,12)
ell('Matte black helmet',(0,1.635,.136),(.112,.142,.113),'Black matte gear',32,16)
# Visor front (not visible in rear view), brow + chin guard.
ell('Dark face visor',(0,1.627,.219),(.092,.069,.031),'Dark visor',28,12)
loft('Helmet lower rim',[(0,1.535,.143,.095,.093),(0,1.551,.142,.107,.105),(0,1.57,.141,.108,.107)],'Black matte gear',28)
# Backpack rounded shell on back, following spine lean. Small volume, original seams.
pack=ell('Small black backpack',(0,1.214,-.084),(.142,.184,.071),'Black matte gear',28,16)
pack.rotation_euler.x=math.radians(10)
ell('Backpack front pocket',(0,1.157,-.145),(.107,.088,.026),'Black matte gear',24,12)
# Tubular webbing is flattened along the torso to read as fabric straps, no block shoulders.
for s in [-1,1]:
 loft('Backpack shoulder strap',[(s*.123,1.014,-.023,.016,.009),(s*.151,1.12,.166,.020,.010),(s*.156,1.25,.206,.020,.009),(s*.13,1.35,.175,.020,.010),(s*.102,1.386,.092,.019,.010),(s*.10,1.34,-.016,.019,.01)],'Black matte gear',10)
 tube('Backpack zip',[(s*.115,1.15,-.150),(s*.126,1.23,-.153),(s*.117,1.315,-.125)],.0022,'Stitch zip metal',6)
# Jacket centre zip follows chest. Tiny seams and puller.
tube('Jacket front zipper',[(0,.96,.057),(0,1.055,.126),(0,1.16,.177),(0,1.26,.214),(0,1.36,.212),(0,1.42,.19)],.0018,'Stitch zip metal',6)
ell('Zip puller',(0,1.374,.212),(.004,.009,.002),'Stitch zip metal',8,6)
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
 ratio=14600/tri
 for o in meshes:
  mod=o.modifiers.new('Mobile detail budget','DECIMATE');mod.ratio=ratio;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 tri=0
 for o in meshes:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT+'/rider.glb',export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
report={'asset':'Viva Wewa seated adult rider','status':'original-prototype-needs-art-review','triangles':tri,'materials':len(M),'meshes':len(meshes),'provenance':'Original procedural Blender geometry, solid PBR materials; no photographic textures, logos or external mesh. User description: navy jacket, grey denim, black shoes, dark backpack, brown hands, matte black helmet.','coordinates':'GLB X right, Y up, +Z forward; origin motorcycle ground0; seated hips .875m with lowest pelvis near saddle .80m.','anchor_positions_m':{'hips':[0,.875,-.12],'hand_left':[-.31,1.02,.519],'hand_right':[.31,1.02,.519],'shoe_centres':[[-.172,.285,-.025],[.172,.285,-.025]],'helmet_centre':[0,1.635,.136]},'limitations':['No armature/animation; posed static model for first implementation.','Photographic realism not claimed; rounded human proportions and restrained materials require in-game lighting and art review.','Rider feet rest near pegs; legs and tank overlap should be checked in combined game scene.']}
open(OUT+'/provenance.json','w').write(json.dumps(report,indent=2))
# Preview on motorcycle: reference mesh only in .blend preview scene, not exported rider GLB.
bpy.ops.import_scene.gltf(filepath=os.environ.get('VIVA_WEWA_MOTORCYCLE_GLB',os.path.abspath(os.path.join(os.path.dirname(__file__),'../../app/public/models/motorcycle.glb'))))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));ground=bpy.context.object;gm=bpy.data.materials.new('Preview ground');gm.diffuse_color=(.10,.12,.14,1);ground.data.materials.append(gm)
for loc,power,size in [((3,-3,5),1000,4),((-3,-1,4),850,4),((0,4,3),700,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,.9))-o.location).to_track_quat('-Z','Y').to_euler()
# Rear quarter, showing the passenger silhouette and believable posture.
bpy.ops.object.camera_add(location=(2.6,3.8,2.1));c=bpy.context.object;c.rotation_euler=(Vector((0,0,.91))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=2.7
s=bpy.context.scene;s.camera=c;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=OUT+'/preview-on-motorcycle.png';s.world.color=(.25,.25,.25);s.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/rider.blend');bpy.ops.render.render(write_still=True)
print(json.dumps(report))
