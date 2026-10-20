import bpy, math, json, os
from mathutils import Vector
OUT=os.environ.get('VIVA_WEWA_ASSET_OUTPUT',os.path.join(os.path.dirname(os.path.abspath(__file__)),'generated','motorcycle'))
os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M={}; parts=[]
def mat(name,color,metal=0,rough=.5):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;M[name]=m;return m
mat('Coral lacquer',(.63,.055,.025),.65,.27);mat('Black rubber',(.014,.017,.021),.05,.8);mat('Saddle vinyl',(.025,.028,.031),0,.62);mat('Graphite frame',(.043,.050,.057),.72,.38);mat('Aluminium',(.43,.48,.5),.85,.27);mat('Engine alloy',(.24,.27,.28),.78,.45);mat('Lamp ivory',(.88,.82,.56),.2,.22);mat('Amber lamp',(.95,.24,.012),.15,.24);mat('Red lamp',(.55,.009,.012),.15,.22);mat('Gauge glass',(.022,.065,.068),.25,.18)
for key,color,strength in [('Lamp ivory',(.8,.67,.3),.35),('Red lamp',(.7,.01,.001),.35),('Amber lamp',(1,.2,.001),.18)]:
 p=M[key].node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=strength

def finish(o,name,material,group='body',smooth=True):
 o.name=name;o.data.materials.append(M[material]);o['group']=group;parts.append(o)
 if smooth:
  for p in o.data.polygons:p.use_smooth=True
 return o

def box(name,loc,scale,material,bevel=.01,group='body'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=bevel;mod.segments=1;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,name,material,group,False)

def cyl(name,a,b,r,material,vertices=12,group='body'):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,name,material,group)

def sphere(name,loc,scale,material,group='body',seg=16,rings=8):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc);o=bpy.context.object;o.scale=scale;return finish(o,name,material,group)

def torus(name,loc,major,minor,material,group='body',normal=(1,0,0),segs=32,small=8):
 bpy.ops.mesh.primitive_torus_add(major_segments=segs,minor_segments=small,location=loc,major_radius=major,minor_radius=minor);o=bpy.context.object;o.rotation_euler=Vector(normal).to_track_quat('Z','Y').to_euler();return finish(o,name,material,group)

def tube(name,points,r,material,group='body',vertices=10):
 for i in range(len(points)-1):cyl(name,points[i],points[i+1],r,material,vertices,group)

def hull(name,sections,material,group='body',n=12):
 # Section tuple y, centre z, half width x, half height z. Longitudinal rings.
 verts=[];faces=[]
 for y,z,w,h in sections:
  for k in range(n):
   t=2*math.pi*k/n;verts.append((w*math.cos(t),y,z+h*math.sin(t)))
 for j in range(len(sections)-1):
  for k in range(n):a=j*n+k;b=j*n+(k+1)%n;faces.append((a,b,b+n,a+n))
 faces.extend([tuple(reversed(tuple(range(n)))),tuple((len(sections)-1)*n+k for k in range(n))])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return finish(o,name,material,group)

# Wheels. Exactly 1.285 m between wheel centres; Blender forward is -Y.
for name,y,width in [('front_wheel',-.650,.073),('rear_wheel',.635,.080)]:
 g=name;z=.295
 torus(name+' tyre',(0,y,z),.255,.040,'Black rubber',g,segs=36,small=8)
 torus(name+' alloy rim',(0,y,z),.213,.014,'Aluminium',g,segs=36,small=6)
 for side in [-1,1]:
  torus('Rim edge',(side*.020,y,z),.220,.005,'Aluminium',g,segs=32,small=4)
  for k in range(12):
   t=k*math.tau/12;u=t+.17
   cyl('Alloy spoke',(side*.018,y+.045*math.sin(t),z+.045*math.cos(t)),(side*.018,y+.205*math.sin(u),z+.205*math.cos(u)),.007,'Aluminium',6,g)
 cyl('Drum hub',(-.053,y,z),(.053,y,z),.063,'Engine alloy',20,g)
 cyl('Axle',(-.080,y,z),(.080,y,z),.014,'Aluminium',12,g)
 # tread blocks kept subtle, baked as original geometry
 for k in range(36):
  t=k*math.tau/36
  o=box('Tread',(0,y+.293*math.sin(t),z+.293*math.cos(t)),(.054,.010,.006),'Black rubber',0,g);o.rotation_euler.x=-t

# Frame, swingarm and foot controls
for x in [-.065,.065]:
 tube('Main diamond frame',[(x,.60,.34),(x,.33,.67),(x,-.33,.72),(x,-.42,.69),(x,-.13,.29),(x,.29,.30),(x,.60,.34)],.018,'Graphite frame')
 tube('Seat rails',[(x,-.03,.70),(x,.38,.73),(x,.79,.70)],.015,'Graphite frame')
 cyl('Swingarm',(x,.18,.34),(x,.635,.295),.023,'Graphite frame')
 cyl('Passenger footpeg',(x,.43,.37),(x*2.7,.43,.37),.017,'Black rubber')
 cyl('Front footpeg',(x,.02,.30),(x*2.5,.02,.30),.016,'Black rubber')
# Fork leaned back at top: front axle y=-.65 and head y=-.44
for x in [-.074,.074]:
 cyl('Fork lower',(x,-.65,.295),(x,-.534,.665),.024,'Aluminium')
 cyl('Fork stanchion',(x,-.534,.665),(x,-.440,.925),.014,'Aluminium')
 # rubber gaiters rings on lower part
 for j in range(7):
  t=j/7;yy=-.55+t*.075;zz=.62+t*.22
  torus('Fork gaiter',(x,yy,zz),.019,.006,'Black rubber',normal=(0,.3,.95),segs=12,small=4)
box('Triple clamp',(0,-.447,.906),(.205,.057,.032),'Graphite frame',.009)
box('Lower clamp',(0,-.487,.790),(.194,.05,.025),'Graphite frame',.006)
# rear springs
for x in [-.102,.102]:
 a=Vector((x,.605,.35));b=Vector((x,.40,.69));cyl('Rear damper',a,b,.015,'Aluminium')
 cyl('Coral shock top',(x,.40,.65),(x,.42,.70),.027,'Coral lacquer')
 # helix mesh actual rings following slanted shock
 d=b-a;axis=d.normalized();u=Vector((1,0,0));v=axis.cross(u)
 pts=[]
 for k in range(49):
  t=k/48;pos=a+d*t+.025*(math.cos(t*math.tau*8)*u+math.sin(t*math.tau*8)*v);pts.append(tuple(pos))
 tube('Suspension spring',pts,.004,'Aluminium',vertices=5)

# Mudguards curved over wheels; only upper arcs
for name,y,z,w,r,start,end,material in [('Front mudguard',-.650,.295,.092,.318,-1.2,1.22,'Coral lacquer'),('Rear mudguard',.635,.295,.11,.322,-1.0,1.12,'Graphite frame')]:
 verts=[];faces=[]
 for k in range(21):
  a=start+(end-start)*k/20
  for x in [-w/2,w/2]:verts.append((x,y+r*math.sin(a),z+r*math.cos(a)))
 for k in range(20):faces.append((2*k,2*k+1,2*k+3,2*k+2))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);finish(o,name,material)
 mod=o.modifiers.new('Rolled steel','SOLIDIFY');mod.thickness=.006;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)

# Tank sculpted as changing oval sections, original geometry and paint.
hull('tank',[(.05,.704,.065,.052),(-.01,.756,.128,.105),(-.20,.775,.153,.129),(-.345,.758,.130,.110),(-.395,.734,.074,.074)],'Coral lacquer','tank',16)
cyl('Fuel cap',(0,-.19,.895),(0,-.19,.910),.033,'Aluminium',20)
# small original cream accent plates no brands
for x in [-1,1]:
 o=box('Tank accent',(x*.144,-.18,.776),(.003,.175,.018),'Lamp ivory',.006);o.rotation_euler.z=x*.08
# side fairings, battery box
for x in [-1,1]:
 o=box('Side cover',(x*.093,.155,.578),(.045,.23,.135),'Coral lacquer',.025);o.rotation_euler.x=-.1
box('Battery box',(0,.23,.54),(.12,.16,.12),'Graphite frame',.015)
# long broad saddle oval section
hull('Long two-person saddle',[(.73,.747,.065,.025),(.67,.776,.120,.046),(.38,.795,.132,.046),(.12,.797,.115,.042),(-.035,.784,.083,.038)],'Saddle vinyl',n=12)
# subtle saddle seams
for y in [.13,.22,.31,.40,.49,.58]:
 cyl('Saddle stitching',(-.10,y,.832),(.10,y,.832),.0016,'Graphite frame',6)
# luggage rack behind saddle
for x in [-.10,.10]:tube('Rack rails',[(x,.55,.71),(x,.83,.765),(x,1.0616,.765)],.010,'Graphite frame')
for y in [.77,.86,.96,1.0616]:cyl('Rack cross rail',(-.10,y,.765),(.10,y,.765),.008,'Graphite frame')

# Engine cylinder with visible cooling fins; longitudinal small single-cylinder engine
cyl('Crankcase',(-.095,-.07,.407),(.095,-.07,.407),.112,'Engine alloy',24)
cyl('Right clutch case',(.094,-.07,.408),(.123,-.07,.408),.078,'Aluminium',20)
cyl('Left alternator',(-.124,-.073,.414),(-.094,-.073,.414),.071,'Engine alloy',20)
for side in [-1,1]:
 for k in range(6):
  a=k*math.tau/6;cyl('Case screw',(side*.124,-.073+.059*math.sin(a),.414+.059*math.cos(a)),(side*.128,-.073+.059*math.sin(a),.414+.059*math.cos(a)),.005,'Graphite frame',6)
block=box('Cylinder block',(0,-.18,.538),(.13,.135,.17),'Graphite frame',.012);block.rotation_euler.x=-.18
for j in range(6):
 o=box('Air cooling fins',(0,-.167-j*.004,.482+j*.024),(.155,.15,.008),'Engine alloy',.003);o.rotation_euler.x=-.18
box('Cylinder head',(0,-.20,.637),(.13,.125,.043),'Aluminium',.008)
tube('Exhaust downpipe',[(.06,-.22,.56),(.075,-.34,.49),(.09,-.35,.30),(.14,-.15,.26),(.145,.17,.27)],.019,'Engine alloy')
cyl('Exhaust silencer',(.155,.13,.28),(.155,.72,.30),.041,'Graphite frame',20)
cyl('Exhaust tip',(.155,.71,.30),(.155,.77,.302),.029,'Engine alloy',16)
box('Exhaust heat shield',(.196,.39,.30),(.006,.38,.045),'Aluminium',.008)
# chain cover on opposite side
box('Chain housing',(-.10,.39,.338),(.026,.48,.045),'Graphite frame',.012)
tube('Brake pedal',[(.11,-.05,.29),(.17,-.16,.29),(.20,-.16,.29)],.009,'Engine alloy')

# Rear tail, indicators, licence blank and splashguard
box('Tail lamp',(0,.804,.683),(.105,.034,.043),'Red lamp',.008)
box('Rear mudflap',(0,.85,.458),(.108,.015,.17),'Black rubber',.006)
box('Blank registration plate',(0,.865,.525),(.14,.006,.07),'Lamp ivory',.004)
for side in [-1,1]:
 cyl('Tail indicator stalk',(side*.073,.76,.675),(side*.151,.76,.675),.009,'Graphite frame')
 box('Tail indicator',(side*.155,.76,.675),(.038,.038,.027),'Amber lamp',.008)
# front headlight along -Y, cylindrical round lamp
cyl('Round headlamp shell',(0,-.522,.84),(0,-.625,.84),.085,'Graphite frame',24)
cyl('Headlamp chrome ring',(0,-.619,.84),(0,-.635,.84),.087,'Aluminium',24)
cyl('Headlamp lens',(0,-.636,.84),(0,-.639,.84),.076,'Lamp ivory',24)
for x in [-.145,.145]:
 cyl('Front indicator stalk',(x*.6,-.52,.82),(x,-.52,.82),.01,'Graphite frame')
 box('Front indicator',(x,-.53,.82),(.037,.045,.028),'Amber lamp',.008)
# Handlebar separately named, 0.740 m span
for side in [-1,1]:
 pts=[(0,-.443,.942),(side*.11,-.44,.955),(side*.20,-.40,1.015),(side*.29,-.36,1.035),(side*.3677,-.345,1.035)]
 tube('handlebar',pts,.011,'Aluminium','handlebar')
 cyl('Rubber grip',(side*.277,-.361,1.035),(side*.3667,-.345,1.035),.019,'Black rubber',16,'handlebar')
 box('Switch box',(side*.253,-.368,1.035),(.036,.035,.040),'Graphite frame',.006,'handlebar')
 tube('Brake clutch lever',[(side*.26,-.388,1.033),(side*.32,-.41,1.028),(side*.366,-.401,1.028)],.006,'Aluminium','handlebar',8)
 tube('Mirror stalk',[(side*.245,-.36,1.065),(side*.26,-.40,1.16),(side*.30,-.42,1.205)],.005,'Graphite frame','handlebar',8)
 o=sphere('Mirror shell',(side*.305,-.423,1.218),(.045,.012,.034),'Graphite frame','handlebar',12,6)
 sphere('Mirror silver',(side*.305,-.410,1.218),(.037,.003,.027),'Aluminium','handlebar',12,6)
# gauge faces tilted backward toward rider at +Y
axis=Vector((0,.30,.954))
for x,r in [(-.043,.037),(.042,.030)]:
 a=Vector((x,-.425,1.00));b=a+axis*.028
 cyl('Gauge housing',a,b,r,'Graphite frame',20,'handlebar')
 cyl('Gauge face',b,b+axis*.002,r*.89,'Gauge glass',20,'handlebar')
 # needle white visible from rider view
 tube('Gauge needle',[(x,-.416,1.030),(x+.015,-.425,1.033)],.002,'Lamp ivory','handlebar',6)
 for j in range(7):
  t=-2.0+j*.65;xx=x+math.cos(t)*r*.68;yy=-.416+math.sin(t)*r*.68
  box('Gauge tick',(xx,yy,1.031),(.003,.004,.001),'Lamp ivory',0,'handlebar')

# consolidate by material for static body, preserve wheel rotation pivots and tank/handlebar names
all_original=list(parts)
grouped_parts={g:[o for o in all_original if o.get('group')==g] for g in ['front_wheel','rear_wheel','tank','handlebar','body']}
for group in ['front_wheel','rear_wheel','tank','handlebar','body']:
 objs=grouped_parts[group]
 buckets={}
 for o in objs:
  key='assembly' if group!='body' else o.data.materials[0].name
  buckets.setdefault(key,[]).append(o)
 for k,items in buckets.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in items:o.select_set(True)
  bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object
  o.name=group if group!='body' else 'body_'+k.replace(' ','_')
  if group.endswith('wheel'):
   y=-.650 if group=='front_wheel' else .635
   bpy.context.scene.cursor.location=(0,y,.295);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
  elif group=='handlebar':
   bpy.context.scene.cursor.location=(0,-.443,.925);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
  # bake scale and rotation to export stable axes; local wheel X remains lateral
  bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
# Position tiny tread bevel lowest point exactly on ground.
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.location.z+=.001
# gather export meshes before adding preview scene
bpy.context.view_layer.update()
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];verts=[];triangles=0
for o in meshes:
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 verts.extend([o.matrix_world@Vector(c) for c in o.bound_box])
bounds={axis:[round(min(v[i] for v in verts),4),round(max(v[i] for v in verts),4)] for i,axis in enumerate(['x','y','z'])}
size=[round(bounds[a][1]-bounds[a][0],4) for a in ['x','y','z']]
# GLB export selected geometry only
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT+'/viva-wewa-motorcycle.glb',export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False,export_extras=True)
report={'asset':'viva-wewa-motorcycle','status':'original-prototype-needs-art-review','reference_manifest':'/workspace/wewa-assets/references/motorcycle-reference.json','source':'Original procedural mesh and materials authored in Blender; manufacturer photographs used only as visual references, no photos, logos or external textures embedded.','license':'Original generated work for user project; no third-party texture or mesh license dependency.','coordinates':'GLB X right, Y up, +Z forward. Blender forward -Y and Z up.','wheelbase_m':1.285,'triangle_count':triangles,'mesh_count':len(meshes),'materials':len(M),'blender_bounds':bounds,'actual_dimensions_m':{'width':size[0],'length':size[1],'height_including_mirrors':size[2]},'manufacturer_reference_dimensions_m':{'width':.740,'length':2.016,'height':1.134},'limits':['Prototype detail, not manufacturer CAD. Visual review needed.','Reference height convention and mirror inclusion unspecified; prototype mirrors may exceed stated overall height.','No rider integrated. No physics collider included.','Wheels rotate about local X; named front_wheel and rear_wheel.','Rear wheel and front wheel primitives include multiple materials; static body fused by material.'],'files':['generate_motorcycle.py','viva-wewa-motorcycle.blend','viva-wewa-motorcycle.glb','preview.png']}
open(OUT+'/provenance.json','w').write(json.dumps(report,indent=2))
# Presentation render, ground and rig not in GLB
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));ground=bpy.context.object;gm=bpy.data.materials.new('Studio ground');gm.diffuse_color=(.07,.085,.10,1);ground.data.materials.append(gm)
world=bpy.context.scene.world;world.color=(.25,.25,.25)
for loc,energy,sizeL in [((2,-3,5),900,4),((-3,-1,3),700,3),((0,3,4),1100,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=sizeL;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.55,-3.4,2.0));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.60))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.8;bpy.context.scene.camera=cam
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=OUT+'/preview.png';s.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/viva-wewa-motorcycle.blend');bpy.ops.render.render(write_still=True)
print('WEWA_ASSET_REPORT',json.dumps(report))
