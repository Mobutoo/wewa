import bpy,math,json,random,os
from mathutils import Vector
OUT=os.environ.get('VIVA_WEWA_ASSET_OUTPUT',os.path.join(os.path.dirname(os.path.abspath(__file__)),'generated','minibus'));random.seed(203)
os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M={};parts=[]
def mat(n,c,r=.5,m=.0):
 a=bpy.data.materials.new(n);a.diffuse_color=(*c,1);a.use_nodes=True;p=a.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=r;p.inputs['Metallic'].default_value=m;M[n]=a
mat('Weathered warm yellow',(.55,.405,.075),.64,.18);mat('Worn blue panels',(.020,.115,.19),.7,.15);mat('Black rubber and cabin',(.018,.021,.024),.83);mat('Metal alloy',(.24,.27,.28),.53,.75);mat('Tinted dusty glass',(.09,.135,.145),.24,.18);mat('Lamp ivory',(.80,.76,.53),.35,.15);mat('Red rear lens',(.44,.015,.009),.4);mat('Rust dust',(.16,.09,.035),.97)
def xyz(p):return Vector((p[0],-p[2],p[1]))
def finish(o,n,m,g='body',sm=True):
 o.name=n;o.data.materials.append(M[m]);o['group']=g;parts.append(o)
 if sm:
  for p in o.data.polygons:p.use_smooth=True
 return o

def box(n,p,scale,m,b=.02,g='body'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.dimensions=(scale[0],scale[2],scale[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  mod=o.modifiers.new('Sheet metal rounded edges','BEVEL');mod.width=b;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,n,m,g,False)
def cyl(n,a,b,r,m,verts=16,g='body'):
 a,b=xyz(a),xyz(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,n,m,g)
def torus(n,p,major,minor,m,g='body',seg=32,small=8):
 bpy.ops.mesh.primitive_torus_add(major_segments=seg,minor_segments=small,major_radius=major,minor_radius=minor,location=xyz(p));o=bpy.context.object;o.rotation_euler.y=math.pi/2;return finish(o,n,m,g)
def panel(n,vs,fs,m):
 mesh=bpy.data.meshes.new(n);mesh.from_pydata([xyz(p) for p in vs],[],fs);mesh.update();o=bpy.data.objects.new(n,mesh);bpy.context.collection.objects.link(o);return finish(o,n,m,sm=False)
def beam(n,pts,r,m):
 for a,b in zip(pts,pts[1:]):cyl(n,a,b,r,m,10)
# Core body left open under windows and along wheel arches, not a cube hidden behind wheels.
box('Chassis',(0,.58,-.10),(1.57,.18,4.35),'Black rubber and cabin',.025)
box('Interior floor',(0,.72,-.15),(1.80,.09,4.20),'Worn blue panels',.025)
# Roof and upper window rails
box('Rounded high roof',(0,2.17,-.20),(1.90,.17,4.45),'Weathered warm yellow',.075)
for side in [-1,1]:
 x=side*.929
 box('Upper side header',(x,2.037,-.28),(.045,.11,4.18),'Weathered warm yellow',.025)
 # lower side blue waist continuous, wheel arches below it
 box('Blue side waist',(x,1.08,-.30),(.05,.34,4.17),'Worn blue panels',.008)
 # metal panels between and beyond wheel openings
 for z,l in [(-2.12,.44),(-.05,1.99),(2.00,.48)]:
  box('Lower skirt panel',(x,.752,z),(.05,.34,l),'Worn blue panels',.015)
 # Side passenger windows: no opaque full body behind them
 for k,z in enumerate([-1.82,-1.10,-.38,.34,1.06]):
  # last window is cab/driver; window height slightly varied
  box('Window rubber surround',(x,1.662,z),(.058,.66,.651),'Black rubber and cabin',.045)
  box('Passenger side glass',(x+side*.031,1.669,z),(.007,.568,.565),'Tinted dusty glass',.040)
  box('Window B pillar',(x,1.63,z+.34),(.055,.89,.053),'Weathered warm yellow',.010)
  if k<4:
   box('Sliding window divider',(x+side*.038,1.67,z),(.012,.575,.012),'Metal alloy',.002)
 # Wheel arches, blue metal narrow curve + black inner recess arc
 for zc in [1.44,-1.41]:
  vs=[];fs=[]
  for k in range(19):
   a=math.pi*k/18
   for r in [.395,.445]:vs.append((side*.953,.36+r*math.sin(a),zc+r*math.cos(a)))
  for k in range(18):fs.append((k*2,k*2+1,k*2+3,k*2+2))
  panel('Wheel arch painted lip',vs,fs,'Worn blue panels')
  cover=[];coverfaces=[]
  for k in range(19):
   a=math.pi*k/18;zz=zc+.445*math.cos(a)
   cover.extend([(side*.953,.36+.445*math.sin(a),zz),(side*.953,1.0,zz)])
  for k in range(18):coverfaces.append((k*2,k*2+1,k*2+3,k*2+2))
  panel('Sheet metal above wheel arch',cover,coverfaces,'Worn blue panels')
 # Side door outlines/hinges indicate converted passenger van
 for zz in [-.77,.62]:
  box('Door vertical seam',(side*.960,1.12,zz),(.004,.67,.008),'Black rubber and cabin',0)
 for zz in [.51,-.64]:
  box('Recessed door handle',(side*.966,1.23,zz),(.025,.044,.13),'Black rubber and cabin',.009)
 # blue rub rail and grime at sill
 box('Side protective rub strip',(side*.968,1.234,-.30),(.025,.037,4.16),'Black rubber and cabin',.007)
 box('Dusty sill',(side*.958,.636,-.14),(.008,.045,2.04),'Rust dust',.005)
# Rear body: split doors, upper windows, tail corners
for x in [-.46,.46]:
 box('Rear door lower',(x,1.05,-2.40),(.90,.65,.054),'Worn blue panels',.015)
 box('Rear window surround',(x,1.69,-2.407),(.85,.64,.045),'Black rubber and cabin',.045)
 box('Rear window glass',(x,1.69,-2.434),(.75,.54,.009),'Tinted dusty glass',.035)
box('Rear centre seam',(0,1.37,-2.441),(.014,1.28,.009),'Weathered warm yellow',.003)
box('Rear header',(0,2.05,-2.36),(1.86,.13,.10),'Weathered warm yellow',.025)
for side in [-1,1]:
 box('Rear corner pillar',(side*.891,1.665,-2.34),(.12,.85,.16),'Weathered warm yellow',.025)
 box('Rear tail light',(side*.84,.95,-2.444),(.12,.26,.018),'Red rear lens',.015)
 for h in [1.07,1.76]:box('Rear hinge',(side*.80,h,-2.453),(.09,.035,.018),'Metal alloy',.004)
box('Rear bumper',(0,.555,-2.43),(1.96,.12,.10),'Black rubber and cabin',.025)
box('Rear registration blank',(0,.85,-2.447),(.39,.14,.015),'Lamp ivory',.004)
for side in [-1,1]:
 box('Forward cab door metal',(side*.941,1.145,1.962),(.046,.51,.39),'Weathered warm yellow',.012)
# Forward cab side windows close the naturally triangular A-pillar region.
for side in [-1,1]:
 panel('Cab side glass',[(side*.935,1.40,1.42),(side*.935,1.40,2.08),(side*.875,2.03,1.87),(side*.935,2.03,1.42)],[(0,1,2,3)],'Tinted dusty glass')
# Cabin front windshield is slightly raked, T1 short bonnet candidate shape.
# Forward +Z, upper edge pulled back .22m.
verts=[(-.89,1.38,2.12),(.89,1.38,2.12),(.86,2.04,1.89),(-.86,2.04,1.89)]
panel('Wide windshield',verts,[(0,1,2,3)],'Tinted dusty glass')
for side in [-1,1]:beam('Front A pillar',[(side*.92,1.28,2.12),(side*.89,1.46,2.11),(side*.86,2.08,1.87)],.035,'Weathered warm yellow')
beam('Windshield rubber', [(-.89,1.38,2.12),(.89,1.38,2.12),(.86,2.04,1.89),(-.86,2.04,1.89),(-.89,1.38,2.12)],.015,'Black rubber and cabin')
box('Cab roof brow',(0,2.11,1.87),(1.84,.10,.17),'Weathered warm yellow',.035)
# pressed metal short bonnet and front radiator plate
box('Short bonnet',(0,1.24,2.10),(1.82,.20,.62),'Weathered warm yellow',.045)
box('Front radiator panel',(0,.997,2.36),(1.82,.35,.045),'Weathered warm yellow',.018)
box('Blue front valance',(0,.72,2.32),(1.83,.24,.13),'Worn blue panels',.020)
box('Front bumper',(0,.58,2.40),(1.96,.14,.10),'Black rubber and cabin',.025)
box('Dark rectangular grille',(0,1.02,2.39),(.89,.20,.03),'Black rubber and cabin',.008)
for j in range(4):box('Horizontal grille slat',(0,.952+j*.045,2.414),(.87,.014,.008),'Metal alloy',.002)
for side in [-1,1]:
 box('Square headlight surround',(side*.66,1.026,2.391),(.35,.235,.025),'Black rubber and cabin',.008)
 box('Headlight lens',(side*.66,1.04,2.411),(.255,.174,.015),'Lamp ivory',.009)
 box('Front turn lens',(side*.847,1.005,2.414),(.068,.14,.017),'Lamp ivory',.004)
 beam('Mirror arm',[(side*.91,1.64,1.76),(side*1.13,1.66,1.79),(side*1.15,1.79,1.81)],.012,'Black rubber and cabin')
 box('Mirror black shell',(side*1.16,1.80,1.80),(.14,.25,.065),'Black rubber and cabin',.03)
 box('Mirror face',(side*1.16,1.80,1.761),(.115,.21,.005),'Metal alloy',.025)
 # two wipers follow angled windshield
 beam('Windshield wiper',[(side*.31,1.4,2.14),(side*.46,1.72,2.025),(side*.61,1.84,1.982)],.008,'Black rubber and cabin')
box('Front blank number plate',(0,.74,2.426),(.37,.13,.015),'Lamp ivory',.004)
# Wheels actual radii and hub bolts
for side in [-1,1]:
 for zc in [1.44,-1.41]:
  g=('front' if zc>0 else 'rear')+('_right_wheel' if side>0 else '_left_wheel');x=side*.865
  torus('Van tyre',(x,.34,zc),.257,.083,'Black rubber and cabin',g,32,8)
  cyl('Steel rim',(x-side*.055,.34,zc),(x+side*.086,.34,zc),.215,'Metal alloy',24,g)
  cyl('Dark hub',(x+side*.087,.34,zc),(x+side*.099,.34,zc),.10,'Black rubber and cabin',16,g)
  for k in range(6):
   a=k*math.tau/6;cyl('Wheel bolt',(x+side*.10,.34+.064*math.sin(a),zc+.064*math.cos(a)),(x+side*.113,.34+.064*math.sin(a),zc+.064*math.cos(a)),.012,'Metal alloy',6,g)
 # dusted black flaps behind wheel
 for zc in [1.44,-1.41]:box('Mudflap',(side*.88,.38,zc-.38),(.22,.28,.019),'Black rubber and cabin',.005)
# Interior bench seats and dashboard visible through window silhouettes
for z in [-1.65,-.88,-.12,.65]:
 box('Bench cushion',(0,.94,z),(1.49,.12,.37),'Black rubber and cabin',.055)
 box('Bench backrest',(0,1.22,z-.19),(1.50,.50,.10),'Black rubber and cabin',.045)
 for x in [-.59,.59]:cyl('Seat leg',(x,.75,z),(x,.91,z),.022,'Metal alloy',10)
box('Cab dashboard',(0,1.34,1.81),(1.67,.16,.39),'Black rubber and cabin',.04)
for x in [-.46,.46]:
 box('Front seat cushion',(x,1.0,1.22),(.58,.17,.50),'Black rubber and cabin',.07)
 box('Front seat backrest',(x,1.32,.96),(.56,.63,.13),'Black rubber and cabin',.065)
# restrained original patches: geometry colour variation for dust/scuffed lower panels
for side in [-1,1]:
 for k in range(18):
  z=random.uniform(-2.17,2.14);h=random.uniform(.73,1.17)
  if abs(z-1.44)<.45 or abs(z+1.41)<.45:continue
  o=box('Localized weathered chip',(side*.958,h,z),(.003,random.uniform(.008,.028),random.uniform(.025,.10)),'Rust dust',0)
# Group static mesh by materials, preserve wheel pivots.
by={}
for o in parts:
 g=o.get('group');key=(g,o.data.materials[0].name) if g=='body' else (g,'assembly');by.setdefault(key,[]).append(o)
meshes=[]
for (g,m),items in by.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in items:o.select_set(True)
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name='minibus_'+(m.replace(' ','_') if g=='body' else g)
 if 'wheel' in g:
  side=1 if 'right' in g else -1;zc=1.44 if g.startswith('front') else -1.41;bpy.context.scene.cursor.location=xyz((side*.865,.34,zc));bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);meshes.append(o)
tri=0
for o in meshes:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
if tri>11900:
 for o in meshes:
  mod=o.modifiers.new('Mobile geometry budget','DECIMATE');mod.ratio=11500/tri;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
tri=0
for o in meshes:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT+'/minibus.glb',export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
report={'asset':'Viva Wewa T1-family minibus original prototype','status':'needs-art-and-local-review','triangles':tri,'mesh_count':len(meshes),'materials':len(M),'dimensions_intent_m':{'length':4.9,'width_excluding_mirrors':1.9,'height':2.25},'wheelbase_m':2.85,'provenance':'Original procedural Blender mesh and PBR colours. Supplied documentary references: Radio Okapi/John Bompengo and Le360 Afrique T1 family, research only. No photograph, logo, trademark, external mesh or texture incorporated.','identification_limit':'T1/TN-family form, not a certified Mercedes 207 D variant. Local vehicle transforms vary.','coordinates':'GLB Y up, X right,+Z forward. Wheel nodes rotate local X.','features':['Slightly raked wide windshield','Short bonnet, grille and rectangular headlights','Side and rear glazing, rails, door handles and mirror arms','Four wheels with tyre/rim/bolts, actual arch gaps','Interior bench silhouette, front seats and dashboard','Yellow upper / blue lower livery, restrained original dust/scuff geometry'],'limitations':['Prototype shape, no manufacturer CAD dimensions.','Glass solid tint for performance; does not show interior benches clearly.','No doors, steering or suspension animation; wheel pivots ready.','Artistic/local review still required; not photographic realism certified.']}
open(OUT+'/provenance.json','w').write(json.dumps(report,indent=2))
# Studio preview
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005));g=bpy.context.object;mg=bpy.data.materials.new('Preview studio');mg.diffuse_color=(.10,.12,.13,1);g.data.materials.append(mg)
for p,power,size in [((4,-5,7),1600,5),((-4,-2,5),1200,4),((1,5,6),1400,4)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6,-8,4.5));c=bpy.context.object;c.rotation_euler=(Vector((0,0,1.10))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=6.8
s=bpy.context.scene;s.camera=c;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=OUT+'/preview.png';s.world.color=(.25,.25,.25);s.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/minibus.blend');bpy.ops.render.render(write_still=True);print(json.dumps(report))
