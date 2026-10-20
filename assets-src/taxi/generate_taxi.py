import bpy, math, json, random, os
from mathutils import Vector
OUT=os.environ.get('VIVA_WEWA_ASSET_OUTPUT',os.path.join(os.path.dirname(os.path.abspath(__file__)),'generated'));os.makedirs(OUT,exist_ok=True);random.seed(51)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M={};parts=[]
def mat(n,c,r=.4,m=0):
 a=bpy.data.materials.new(n);a.diffuse_color=(*c,1);a.use_nodes=True;p=a.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=r;p.inputs['Metallic'].default_value=m;M[n]=a
mat('Taxi aged yellow',(.69,.47,.024),.43,.38);mat('Black rubber trim',(.012,.015,.018),.77);mat('Smoked automotive glass',(.022,.043,.052),.17,.35);mat('Brushed steel',(.32,.35,.36),.35,.84);mat('Headlight reflector',(.69,.73,.67),.18,.5);mat('Tail light red',(.50,.011,.008),.25,.3);mat('Road dust',(.115,.08,.038),.93);mat('Cabin charcoal',(.027,.033,.038),.9)
def xyz(p):return Vector((p[0],-p[2],p[1]))
def fin(o,n,m,g='body',sm=True):
 o.name=n;o.data.materials.append(M[m]);o['group']=g;parts.append(o)
 if sm:
  for p in o.data.polygons:p.use_smooth=True
 return o

def box(n,p,sc,m,b=.015,g='body'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.dimensions=(sc[0],sc[2],sc[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  mod=o.modifiers.new('Manufactured edge radius','BEVEL');mod.width=b;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return fin(o,n,m,g,False)
def ell(n,p,sc,m,g='body',seg=24,rings=12):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=xyz(p));o=bpy.context.object;o.scale=(sc[0],sc[2],sc[1]);return fin(o,n,m,g)
def cyl(n,a,b,r,m,v=16,g='body'):
 a,b=xyz(a),xyz(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return fin(o,n,m,g)
def beam(n,ps,r,m,g='body',v=8):
 for a,b in zip(ps,ps[1:]):cyl(n,a,b,r,m,v,g)
def mesh(n,vs,fs,m,g='body',sm=True):
 me=bpy.data.meshes.new(n);me.from_pydata([xyz(p) for p in vs],[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);return fin(o,n,m,g,sm)
def patch(n,corners,m,nu=10,nv=5,bulge=.012):
 # corners lowerLeft, lowerRight, upperRight, upperLeft; bilinear surface with light convexity
 vs=[];fs=[]
 for j in range(nv+1):
  v=j/nv;a=Vector(corners[0]).lerp(Vector(corners[3]),v);b=Vector(corners[1]).lerp(Vector(corners[2]),v)
  for i in range(nu+1):
   u=i/nu;p=a.lerp(b,u);p.y+=bulge*math.sin(math.pi*u)*math.sin(math.pi*v);vs.append(tuple(p))
 for j in range(nv):
  for i in range(nu):a=j*(nu+1)+i;fs.append((a,a+1,a+nu+2,a+nu+1))
 return mesh(n,vs,fs,m)
# Original compact high-roof 5-door hatchback. Design proportions, not a certified Toyota asset.
# Longitudinal stations (forwardZ, half-width, belt height).
stations=[(-1.93,.67,.88),(-1.87,.75,.94),(-1.72,.80,.975),(-1.50,.832,.99),(-1.27,.847,.99),(-.98,.85,.992),(-.65,.85,.995),(-.32,.85,1.0),(0,.848,1.005),(.35,.844,1.005),(.70,.835,1.005),(.95,.825,.98),(1.10,.817,.94),(1.32,.80,.907),(1.55,.765,.88),(1.75,.73,.865),(1.88,.66,.835),(1.93,.57,.80)]
# Densify side profile so true wheel-arch openings are curved rather than square.
zs=sorted(set([s[0] for s in stations]+[c+.337*math.cos(math.pi*k/20) for c in [1.10,-1.27] for k in range(21)]))
def interp(z,col):
 for i in range(len(stations)-1):
  a,b=stations[i],stations[i+1]
  if a[0]<=z<=b[0]:t=(z-a[0])/(b[0]-a[0]);return a[col]*(1-t)+b[col]*t
 return stations[0 if z<stations[0][0] else -1][col]
def bottom(z):
 h=.365
 for c in [1.10,-1.27]:
  d=abs(z-c)
  if d<.337:h=max(h,.286+math.sqrt(.337**2-d*d))
 return h
for side in [-1,1]:
 vs=[];fs=[]
 for z in zs:
  w=interp(z,1);top=interp(z,2);low=bottom(z)
  for t,xf in [(0,.975),(.17,1.0),(.65,1.0),(1,.973)]:vs.append((side*w*xf,low+(top-low)*t,z))
 for j in range(len(zs)-1):
  for k in range(3):a=j*4+k;fs.append((a,a+1,a+5,a+4))
 mesh('Sculpted steel side',vs,fs,'Taxi aged yellow')
 # Wheel arches with rolled lips, no photographic texture.
 for c in [1.10,-1.27]:
  ps=[]
  for k in range(25):
   a=math.pi*k/24;z=c+.337*math.cos(a);ps.append((side*(interp(z,1)*.981),.286+.337*math.sin(a),z))
  beam('Wheel arch edge',ps,.009,'Black rubber trim',v=6)
 # Long moulding, restrained separation lines and handles.
 beam('Door side moulding',[(side*.834,.70,-1.66),(side*.858,.72,-.95),(side*.861,.735,-.15),(side*.848,.74,.75)],.015,'Black rubber trim')
 for z in [-.36,.83]:
  beam('Door shut line',[(side*.829,.405,z),(side*.851,.71,z),(side*.827,.993,z)],.0025,'Black rubber trim',v=6)
 for z in [-.56,.57]:
  ell('Door handle recess',(side*.854,.945,z),(.009,.026,.075),'Black rubber trim',seg=14,rings=6)
  box('Yellow door handle',(side*.865,.950,z),(.016,.019,.105),'Taxi aged yellow',.008)
 # Rear quarter short styling crease and small refuelling flap.
 if side==-1:
  box('Fuel flap',(side*.853,.863,-1.57),(.006,.135,.16),'Taxi aged yellow',.018)
 # sill thin road grime
 beam('Dust lower sill',[(side*.835,.393,-.88),(side*.847,.399,-.30),(side*.838,.40,.66)],.008,'Road dust',v=6)
# Underbody black, hidden inside car; frontal and rear lower bumper skin rounded.
box('Underbody',(0,.375,-.08),(1.43,.10,3.35),'Black rubber trim',.04)
# Hood curved surface (not an ellipsoid / toy balloon).
vs=[];fs=[]
hood=[(.84,.813,1.01),(1.04,.808,.97),(1.31,.79,.935),(1.56,.755,.902),(1.79,.705,.883),(1.90,.61,.855)]
for z,w,h in hood:
 for k in range(17):
  x=(k/16*2-1)*w;vs.append((x,h+.026*(1-(x/w)**2),z))
for j in range(len(hood)-1):
 for k in range(16):a=j*17+k;fs.append((a,a+1,a+18,a+17))
mesh('Pressed bonnet',vs,fs,'Taxi aged yellow')
box('Front bumper',(0,.552,1.795),(1.49,.30,.27),'Taxi aged yellow',.10)
box('Rear bumper',(0,.545,-1.802),(1.59,.29,.27),'Taxi aged yellow',.09)
box('Lower front air intake',(0,.491,1.926),(.82,.113,.024),'Black rubber trim',.025)
box('Front small radiator grille',(0,.746,1.920),(.51,.105,.020),'Black rubber trim',.014)
for k in range(3):box('Grille subtle slat',(0,.715+k*.03,1.934),(.485,.008,.005),'Brushed steel',.002)
# Rear hatch panel tapered under glazing.
patch('Rear hatch metal',[(-.73,.69,-1.93),(.73,.69,-1.93),(.757,1.05,-1.775),(-.757,1.05,-1.775)],'Taxi aged yellow',12,6,.01)
box('Hatch blank plate recess',(0,.81,-1.938),(.41,.16,.013),'Black rubber trim',.014)
box('Rear blank plate',(0,.81,-1.949),(.35,.115,.006),'Headlight reflector',.005)
box('Front blank plate',(0,.62,1.948),(.35,.115,.008),'Headlight reflector',.005)
# Cabin pillars and low-crown roof.
roofsecs=[(-1.22,.605,1.42),(-1.08,.642,1.495),(-.80,.658,1.527),(-.35,.664,1.533),(.15,.645,1.529),(.48,.620,1.48)]
vs=[];fs=[]
for z,w,h in roofsecs:
 for k in range(17):
  t=k/16*2-1;vs.append((w*t,h+.020*(1-t*t),z))
for j in range(len(roofsecs)-1):
 for k in range(16):a=j*17+k;fs.append((a,a+1,a+18,a+17))
mesh('High hatchback roof',vs,fs,'Taxi aged yellow')
# Windshield smoothly raked and slightly curved.
wind=[(-.777,1.011,.863),(.777,1.011,.863),(.607,1.476,.479),(-.607,1.476,.479)]
patch('Front windshield',wind,'Smoked automotive glass',16,8,.012)
beam('Windshield rubber',wind+[wind[0]],.009,'Black rubber trim',v=8)
# Rear hatch glass follows roof and rear panel.
rear=[(-.738,1.067,-1.763),(.738,1.067,-1.763),(.592,1.421,-1.225),(-.592,1.421,-1.225)]
patch('Rear hatch glass',rear,'Smoked automotive glass',14,7,.014)
beam('Rear windshield rubber',rear+[rear[0]],.009,'Black rubber trim')
for side in [-1,1]:
 # main side opening, front door glass is trapezoid; B pillar visibly thicker black.
 front=[(side*.806,1.024,.79),(side*.659,1.471,.43),(side*.670,1.490,-.29),(side*.818,1.025,-.32)]
 rearw=[(side*.819,1.022,-.39),(side*.669,1.491,-.37),(side*.653,1.467,-1.02),(side*.801,1.028,-1.34)]
 # surface coordinates don't assume lower corners, mesh simple quad and normals.
 mesh('Front side glass',front,[(0,1,2,3)],'Smoked automotive glass')
 mesh('Rear side glass',rearw,[(0,1,2,3)],'Smoked automotive glass')
 beam('Side window rubber',front+[front[0]],.009,'Black rubber trim')
 beam('Rear window rubber',rearw+[rearw[0]],.009,'Black rubber trim')
 beam('A pillar',[(side*.825,.99,.85),(side*.632,1.483,.467)],.027,'Taxi aged yellow',v=10)
 beam('B pillar',[(side*.826,1.016,-.355),(side*.672,1.505,-.33)],.029,'Black rubber trim',v=10)
 beam('C pillar',[(side*.817,1.0,-1.45),(side*.627,1.453,-1.16)],.048,'Taxi aged yellow',v=12)
 beam('Roof side rail',[(side*.627,1.484,.467),(side*.670,1.534,-.33),(side*.653,1.50,-.98),(side*.622,1.43,-1.23)],.022,'Taxi aged yellow',v=10)
 # Mirrors: black stalks and yellow caps, original no logos.
 beam('Mirror stem',[(side*.80,1.07,.725),(side*.894,1.085,.71)],.016,'Black rubber trim')
 ell('Mirror housing',(side*.93,1.107,.70),(.096,.054,.105),'Taxi aged yellow',seg=20,rings=10)
 ell('Mirror glass',(side*.93,1.107,.622),(.076,.041,.005),'Smoked automotive glass',seg=16,rings=8)
 # Broad original clear headlamp with a dark trim and lens reflector; no marque shape copied.
 # Original automotive rectangular lenses seated on front/rear metal panels.
 box('Front lamp black surround',(side*.525,.789,1.924),(.255,.145,.018),'Black rubber trim',.018)
 box('Front headlamp lens',(side*.525,.791,1.936),(.230,.122,.012),'Headlight reflector',.014)
 for k in [-1,1]:
  box('Reflector cell',(side*.525+k*.055,.792,1.945),(.072,.084,.004),'Brushed steel',.010)
 box('Rear lamp seal',(side*.683,.833,-1.944),(.125,.272,.020),'Black rubber trim',.022)
 box('Rear red lens',(side*.683,.833,-1.959),(.104,.247,.018),'Tail light red',.018)
 box('Rear clear band',(side*.683,.856,-1.971),(.098,.039,.006),'Headlight reflector',.006)
 # Black wheel well underside local patches keep arches physically open.
 for zc in [1.1,-1.27]:
  g=('front' if zc>0 else 'rear')+('_right_wheel' if side>0 else '_left_wheel');x=side*.76
  bpy.ops.mesh.primitive_torus_add(major_segments=36,minor_segments=10,major_radius=.228,minor_radius=.058,location=xyz((x,.286,zc)));o=bpy.context.object;o.rotation_euler.y=math.pi/2;fin(o,'Road tyre','Black rubber trim',g)
  # Rim and hub all rotate with wheel, moderate steel-wheel original design.
  cyl('Steel wheel', (x-side*.048,.286,zc),(x+side*.061,.286,zc),.184,'Brushed steel',24,g)
  cyl('Hub centre',(x+side*.061,.286,zc),(x+side*.073,.286,zc),.073,'Black rubber trim',18,g)
  for k in range(8):
   a=k*math.tau/8;yy=.286+.133*math.sin(a);zz=zc+.133*math.cos(a)
   cyl('Wheel ventilation holes',(x+side*.062,yy,zz),(x+side*.066,yy,zz),.025,'Black rubber trim',12,g)
  for k in range(5):
   a=k*math.tau/5;cyl('Wheel bolt',(x+side*.075,.286+.048*math.sin(a),zc+.048*math.cos(a)),(x+side*.080,.286+.048*math.sin(a),zc+.048*math.cos(a)),.009,'Brushed steel',6,g)
# Wipers and hatch rear wiper, antenna; visible from rear player viewpoint.
for side in [-1,1]:beam('Windshield wiper',[(side*.25,1.035,.85),(side*.37,1.19,.725),(side*.53,1.22,.70)],.005,'Black rubber trim',v=6)
beam('Hatch wiper',[(0,1.09,-1.762),(.27,1.15,-1.67),(.39,1.20,-1.60)],.006,'Black rubber trim',v=6)
beam('Roof radio antenna',[(0,1.555,-.93),(0,1.76,-1.02)],.004,'Black rubber trim',v=6)
# Cab interior silhouettes, dark and very simple behind glass.
for x in [-.38,.38]:
 for z in [-.85,.22]:
  box('Seat base',(x,.55,z),(.54,.14,.48),'Cabin charcoal',.06)
  o=box('Seat back',(x,.85,z-.22),(.53,.64,.14),'Cabin charcoal',.06);o.rotation_euler.x=.11
  ell('Headrest',(x,1.18,z-.24),(.18,.11,.065),'Cabin charcoal',seg=16,rings=8)
box('Dashboard',(0,.945,.68),(1.40,.16,.36),'Cabin charcoal',.06)
# Original restrained wear: small lower-body chips, subtle directional grime. No photographic maps.
for side in [-1,1]:
 for k in range(18):
  z=random.uniform(-.86,.70);h=random.uniform(.42,.62);w=interp(z,1)
  box('Small paint abrasion',(side*(w+.001),h,z),(.002,random.uniform(.002,.008),random.uniform(.01,.04)),'Road dust',0)
# Consolidate materials, preserve wheel pivots.
by={}
for o in parts:
 g=o['group'];key=(g,o.data.materials[0].name) if g=='body' else (g,'assembly');by.setdefault(key,[]).append(o)
meshes=[]
for (g,m),items in by.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in items:o.select_set(True)
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name='taxi_'+(m.replace(' ','_') if g=='body' else g)
 if 'wheel' in g:
  side=1 if 'right' in g else -1;zc=1.10 if g.startswith('front') else -1.27;bpy.context.scene.cursor.location=xyz((side*.76,.286,zc));bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);meshes.append(o)
tri=0
for o in meshes:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
if tri>17500:
 for o in meshes:
  mod=o.modifiers.new('Traffic mesh budget','DECIMATE');mod.ratio=17200/tri;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
tri=0
for o in meshes:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT+'/taxi.glb',export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
report={'asset':'Viva Wewa original yellow compact hatchback taxi','status':'prototype_art_review_required','triangles':tri,'mesh_count':len(meshes),'materials':len(M),'provenance':'Original procedural Blender geometry and solid PBR materials. Loose proportions inspired by early Toyota ist class and supplied Kinshasa taxi photographs. No logo, photograph, external mesh or paid asset used.','license':'Original generated work for user Viva Wewa project, no third-party texture/mesh dependencies.','dimensions_intent_m':{'length':3.86,'width_excluding_mirrors':1.70,'height_roof':1.553,'wheelbase':2.37},'orientation':'GLB X right, Y up,+Z forward, wheel contact floor0, wheel rotation about local X.','wheel_nodes':['taxi_front_right_wheel','taxi_front_left_wheel','taxi_rear_right_wheel','taxi_rear_left_wheel'],'features':['Continuous sculpted body and bonnet surfaces','Sloping windscreen, high curved roof, 4 side window openings and hatch glazing','Rounded bumpers, door seams, handles and mirrors','True semicircular wheel arches and separate tyres/steel wheels','Front and rear light assemblies, blank plates, wipers, antenna','Interior seat/headrest silhouettes, restrained original surface chips'],'limitations':['No marque identification or exact manufacturer CAD promised.','Procedural solid materials have no photo-scanned surface microdetail.','Photographic realism remains an unvalidated art target.','No physics collider or steering animation; wheel nodes ready.']}
open(OUT+'/provenance.json','w').write(json.dumps(report,indent=2))
# Studio preview, primarily rear-quarter since player follows vehicle.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));g=bpy.context.object;gm=bpy.data.materials.new('Studio ground');gm.diffuse_color=(.11,.13,.14,1);g.data.materials.append(gm)
for loc,power,size in [((4,5,6),1200,5),((-4,1,4),1000,4),((1,-5,5),1100,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,.7))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5.2,6.8,3.4));c=bpy.context.object;c.rotation_euler=(Vector((0,0,.75))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=5.3
s=bpy.context.scene;s.camera=c;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False;s.render.resolution_x=1300;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=OUT+'/preview.png';s.world.color=(.22,.22,.22);s.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/taxi.blend');bpy.ops.render.render(write_still=True);print(json.dumps(report))
