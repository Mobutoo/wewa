"""Original instrument candidate from official visible-side reference.
All physical dimensions estimated. No photographed face used as a texture.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=json.loads((HERE/'parameters.json').read_text())
OUT=ROOT/'creative/reviews/instruments-v1';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
parts=bpy.data.collections.new('WEWA_INSTRUMENTS_SEPARATE_PARTS');scene.collection.children.link(parts)
studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');scene.collection.children.link(studio)
assembly=bpy.data.objects.new('INSTRUMENT_CLUSTER_MOUNT',None);parts.objects.link(assembly)
assembly.location=P['cockpit_origin_xyz_m_estimated'];assembly.rotation_euler=tuple(math.radians(v) for v in P['cockpit_rotation_degrees_xyz'])
assembly['component_id']=P['component_id'];assembly['all_dimensions_estimated']=True;assembly['art_accepted']=False
def mat(name,color,rough=.4,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=rough;n.inputs['Metallic'].default_value=metal;return m
shell=mat('Black injection moulding - estimated',(.012,.014,.017),.36)
rim=mat('Satin black bezel',(.018,.021,.025),.29)
face=mat('Charcoal printed dial',(.009,.011,.013),.62)
white=mat('Dial white ink',(.80,.83,.80),.68);orange=mat('Dial amber orange ink',(.95,.31,.025),.55);red=mat('Pointer and red warning ink',(.65,.012,.009),.40)
green=mat('Fuel F green ink',(.025,.48,.19),.55);steel=mat('Small fastener steel',(.10,.11,.12),.28,.82)
rubber=mat('USB cap black elastomer',(.008,.009,.011),.64)
glass=mat('Clear instrument cover - transmission candidate',(.94,.97,1),.065)
g=glass.node_tree.nodes.get('Principled BSDF');g.inputs['Transmission Weight'].default_value=1;g.inputs['IOR'].default_value=1.49
glass['runtime_limit']='KHR_materials_transmission, compare actual runtime refraction; no physical lens measurement'
def move(o,c=parts):
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o);return o
def mesh(name,verts,faces,material,parent=assembly,structural=True):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free()
 o=bpy.data.objects.new(name,data);parts.objects.link(o);o.parent=parent;data.materials.append(material);o['structural_closed_volume']=structural;return o
def lathe(name,section,centre,material,n=192):
 v=[];rings=[]
 for radius,z in section:
  ids=[]
  for i in range(n if radius>1e-9 else 1):
   a=math.tau*i/n;ids.append(len(v));v.append((centre[0]+radius*math.cos(a),centre[1]+radius*math.sin(a),z))
  rings.append(ids)
 faces=[]
 for j,aa in enumerate(rings):
  bb=rings[(j+1)%len(rings)]
  if len(aa)==len(bb)==1:continue
  for i in range(n):
   faces.append((aa[0],bb[(i+1)%n],bb[i]) if len(aa)==1 else (aa[i],aa[(i+1)%n],bb[0]) if len(bb)==1 else (aa[i],aa[(i+1)%n],bb[(i+1)%n],bb[i]))
 o=mesh(name,v,faces,material)
 for p in o.data.polygons:p.use_smooth=True
 return o
def box(name,location,dimensions,material,bevel=0,parent=assembly,structural=True):
 bpy.ops.mesh.primitive_cube_add(size=1);o=move(bpy.context.object);o.name=name;o.dimensions=dimensions;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.location=location;o.parent=parent;o.data.materials.append(material);o['structural_closed_volume']=structural
 if bevel:
  b=o.modifiers.new('Small moulding radii','BEVEL');b.width=bevel;b.segments=5
 return o
def text(name,value,location,size,material,align='CENTER'):
 data=bpy.data.curves.new(name,'FONT');data.body=value;data.align_x=align;data.align_y='CENTER';data.size=size;data.resolution_u=8;data.extrude=0
 o=bpy.data.objects.new(name,data);parts.objects.link(o);o.parent=assembly;o.location=location;data.materials.append(material);o['structural_closed_volume']=False;o['surface_role']='Original ink marking, planar geometry, not solid hardware';return o
def line(name,coords,thickness,material):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=1;data.bevel_depth=thickness/2;data.bevel_resolution=2;data.use_fill_caps=True;s=data.splines.new('POLY');s.points.add(len(coords)-1)
 for p,co in zip(s.points,coords):p.co=(*co,1)
 o=bpy.data.objects.new(name,data);parts.objects.link(o);o.parent=assembly;data.materials.append(material);o['structural_closed_volume']=False;return o
centres=[(-.064,0),(.064,0)]
# A connecting front/rear cover is separate from each hollow pod. Hidden sections
# are bounded estimates, not a claimed recovered OEM mould or complete wiring.
outline=[(-.012,.053),(.012,.053),(.026,.046),(.029,.030),(.020,.012),(.015,-.008),(.022,-.031),(.037,-.043),(.040,-.050),(.033,-.056),(0,-.058),(-.033,-.056),(-.040,-.050),(-.037,-.043),(-.022,-.031),(-.015,-.008),(-.020,.012),(-.029,.030),(-.026,.046)]
controls=[Vector(p) for p in outline];outline=[]
for i in range(len(controls)):
 a,b,c,d=[controls[j%len(controls)] for j in [i-1,i,i+1,i+2]]
 for k in range(8):
  t=k/8;point=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t);outline.append(tuple(point))
verts=[(x,y,z) for z in [-.016,.031] for x,y in outline];count=len(outline)
faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
bridge=mesh('Shaped central cluster cover',verts,faces,shell)
bevel=bridge.modifiers.new('Moulded central cover edge radius','BEVEL');bevel.width=.0014;bevel.segments=5
normal=bridge.modifiers.new('Weighted moulding normals','WEIGHTED_NORMAL');normal.keep_sharp=True
for index,(cx,cy) in enumerate(centres):
 side='SPEED' if index==0 else 'FUEL_GEAR'
 lathe(side+' hollow rear pod',[(0,-.022),(.043,-.022),(.047,-.019),(.050,-.009),(.050,.025),(.049,.034),(.047,.037),(.045,.035),(.044,.025),(.044,-.010),(0,-.010)],(cx,cy),shell)
 lathe(side+' stepped bezel',[(.0424,.029),(.046,.029),(.049,.034),(.049,.038),(.0475,.040),(.044,.040),(.0424,.037)],(cx,cy),rim)
 lathe(side+' dial plate',[(0,.026),(.0425,.026),(.0425,.028),(0,.028)],(cx,cy),face)
 lathe(side+' lens sealing lip',[(.042,.036),(.043,.036),(.043,.038),(.042,.038)],(cx,cy),rubber)
 # Slight lens convexity, two distinct surfaces and a closed edge, not a flat
 # opaque disc. Actual curvature and thickness still need an edge/reference view.
 lens_section=[(0,.0412),(.014,.0410),(.028,.0404),(.040,.0395),(.042,.0390),(.042,.0378),(.040,.0383),(.028,.0392),(.014,.0398),(0,.0400)]
 lens=lathe(side+' clear closed lens',lens_section,(cx,cy),glass)
 lens.visible_shadow=False;lens['shadow_approximation']='Transparent cover omitted from Cycles shadow rays; refractive caustics not simulated, matching non-shadow-casting runtime review'
 # Reverse-side bosses are independent provisional mounting volumes.
 lathe(side+' rear mounting boss',[(.003,-.037),(.0065,-.037),(.007,-.032),(.007,-.020),(.003,-.020)],(cx,cy-.025),shell,n=96)

cx=-.064;z=.02815
for speed in range(0,141,2):
 a=math.radians(225-speed*270/140);major=speed%20==0;medium=speed%10==0;r0=.0339 if major else .0355 if medium else .037
 ink=red if speed>=120 and major else orange if major else white
 line('Speed tick '+str(speed),[(cx+r0*math.cos(a),r0*math.sin(a),z),(cx+.040*math.cos(a),.040*math.sin(a),z)],.00070 if major else .00022,ink)
 if major:
  text('Speed value '+str(speed),str(speed),(cx+.0296*math.cos(a),.0296*math.sin(a),z+.0001),.0041,red if speed>=120 else white)
# Three short colour arcs correspond to the visibly printed bands; appearance
# traced from photo, not speed-dependent gameplay thresholds.
for start,end,radius,ink in [(0,58,.0398,orange),(60,100,.0410,white),(104,140,.0398,red)]:
 points=[]
 for i in range(41):
  a=math.radians(225-(start+(end-start)*i/40)*270/140);points.append((cx+radius*math.cos(a),radius*math.sin(a),z+.00008))
 line('Speed printed arc '+str(start),points,.00045,ink)
text('Speed units','km/h',(cx,-.029,z+.0001),.0028,white)
box('Odometer recessed frame',(cx,.010,.0283),(.034,.007,.0011),rim,.0005)
for i in range(5):
 x=cx+(i-2)*.0058;box('Odometer drum '+str(i),(x,.010,.0289),(.0054,.0058,.0003),face,.0002);text('Odometer digit '+str(i),'0',(x,.010,.02915),.0042,white)

cx=.064
for i in range(9):
 a=math.radians(225-i*10);r0=.033 if i%4==0 else .036
 line('Fuel tick '+str(i),[(cx+r0*math.cos(a),r0*math.sin(a),z),(cx+.040*math.cos(a),.040*math.sin(a),z)],.0007 if i%4==0 else .00028,orange)
for value,angle,ink in [('E',225,red),('F',145,green)]:
 a=math.radians(angle);text('Fuel '+value,value,(cx+.028*math.cos(a),.028*math.sin(a),z+.0001),.0042,ink)
# Original simplified white fuel-pump pictogram, no imported icon/image.
line('Fuel pump outline',[(cx-.025,-.003,z),(cx-.025,.003,z),(cx-.021,.003,z),(cx-.021,-.003,z),(cx-.025,-.003,z)],.00045,white)
line('Fuel pump hose',[(cx-.021,.002,z),(cx-.019,.001,z),(cx-.019,-.002,z),(cx-.018,-.002,z)],.00035,white)
for gear in range(1,6):
 a=math.radians(-80+(gear-1)*40);x=cx+.032*math.cos(a);y=.032*math.sin(a)
 line('GEAR_RING_'+str(gear),[(x+.0043*math.cos(t*math.tau/64),y+.0043*math.sin(t*math.tau/64),z+.0001) for t in range(65)],.00055,white)
 digit_mat=mat('Gear '+str(gear)+' white indicator',(.82,.84,.80),.65)
 text('GEAR_DIGIT_'+str(gear),str(gear),(x,y,z+.00015),.0047,digit_mat)
text('Gear label','GEAR',(cx+.020,-.001,z+.0001),.0022,white)

for name,cx,angle,length in [('SPEED',-.064,225,.036),('FUEL',.064,225-.65*80,.032)]:
 pivot=bpy.data.objects.new(name+'_NEEDLE_PIVOT',None);parts.objects.link(pivot);pivot.parent=assembly;pivot.location=(cx,0,.0312);pivot.rotation_euler.z=math.radians(angle);pivot['axis']='Local +Z';pivot['input_range']=[0,140] if name=='SPEED' else [0,1]
 needle=mesh(name+' red needle',[(length,0,0),(.002,.0011,0),(-.007,.0013,0),(-.007,-.0013,0),(.002,-.0011,0)],[(0,1,2,3,4)],red,parent=pivot,structural=False)
 lathe(name+' pointer centre cap',[(0,.031),(.0038,.031),(.0045,.0325),(.0038,.034),(0,.034)],(cx,0),rim,n=96)

cap=lathe('USB rounded elastomer cap - closed',[(0,.034),(.010,.034),(.012,.036),(.012,.040),(.009,.042),(0,.042)],(0,.038),rubber,n=128)
for v in cap.data.vertices:v.co.y=.038+(v.co.y-.038)*1.20
usb_mark=mat('USB moulded symbol',(.026,.030,.035),.50)
line('USB symbol stem',[(0,.034,.04225),(0,.043,.04225)],.00045,usb_mark)
line('USB symbol arrow',[(-.001,.0415,.04225),(0,.043,.04225),(.001,.0415,.04225)],.00045,usb_mark)
line('USB symbol left branch',[(0,.037,.04225),(-.0025,.039,.04225),(-.0025,.041,.04225)],.0004,usb_mark)
line('USB symbol right branch',[(0,.0385,.04225),(.0025,.040,.04225),(.0025,.042,.04225)],.0004,usb_mark)
lathe('USB symbol lower dot',[(0,.0422),(.00065,.0422),(.00065,.0424),(0,.0424)],(0,.0335),usb_mark,n=32)
line('Charge caution triangle',[(-.003,-.004,.032),(0,.002,.032),(.003,-.004,.032),(-.003,-.004,.032)],.0006,red)
for i,word in enumerate(['DO NOT','CHARGE','MOBILE','WHEN','ENGINE IS OFF']):text('Charge warning '+str(i),word,(0,-.010-i*.005,.032),.00245,white)
text('WEWA original wordmark','WEWA',(0,-.049,.032),.0070,white)
for cx in [-.064,.064]:
 for sx in [-1,1]:
  xx=cx+sx*.019;yy=-.009
  lathe('Dial recessed screw',[(0,.0283),(.0013,.0283),(.0013,.0292),(0,.0292)],(xx,yy),steel,n=48)
  line('Screw slot',[(xx-.0008,yy,.02925),(xx+.0008,yy,.02925)],.00025,face)

# Evaluate all exported curves/bevels before checking bodies or saving inspection.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();checks=[]
for obj in list(parts.objects):
 if obj.type not in ['MESH','CURVE','FONT']:continue
 evaluated=obj.evaluated_get(deps);data=bpy.data.meshes.new_from_object(evaluated,depsgraph=deps)
 if obj.get('structural_closed_volume'):
  bm=bmesh.new();bm.from_mesh(data);non=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);unseen=set(bm.verts);shells=0
  while unseen:
   shells+=1;pending=[unseen.pop()]
   while pending:
    for e in pending.pop().link_edges:
     for v in e.verts:
      if v in unseen:unseen.remove(v);pending.append(v)
  row={'name':obj.name,'non_manifold_edges':non,'connected_shells':shells,'signed_volume_m3':volume};assert non==0 and shells==1 and volume>0,row;checks.append(row);bm.free()
 bpy.data.meshes.remove(data)

# Independent inspection copies retain hierarchy/pivots, not studio objects.
bpy.ops.object.select_all(action='DESELECT')
for obj in parts.objects:obj.select_set(True)
bpy.context.view_layer.objects.active=assembly
bpy.ops.export_scene.gltf(filepath=str(HERE/'instruments-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False)

floor_mat=mat('Instrument studio charcoal',(.08,.09,.105),.68)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.03));floor=move(bpy.context.object,studio);floor.name='INSTRUMENT_STUDIO_FLOOR';floor.data.materials.append(floor_mat)
world=bpy.data.worlds.new('Instrument studio world');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs[0].default_value=(.26,.29,.34,1);world.node_tree.nodes['Background'].inputs[1].default_value=.25
for name,location,energy,size in [('METER_KEY',(-.60,-.20,.70),40,.30),('METER_FILL',(.55,-.05,.6),25,.40),('METER_EDGE',(.1,-.60,.25),19,.35)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=location;o.rotation_euler=(Vector((0,-.12,.09))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('INSTRUMENT_CAMERA',bpy.data.cameras.new('INSTRUMENT_CAMERA'));studio.objects.link(cam);scene.camera=cam;cam.location=(.18,.40,.44);cam.rotation_euler=(Vector((0,-.12,.10))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=70
scene.render.engine='CYCLES';scene.cycles.samples=128;scene.cycles.use_denoising=False;scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False;scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
bpy.ops.object.select_all(action='DESELECT');assembly.select_set(True);bpy.context.view_layer.objects.active=assembly
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'instruments-v1.blend'),compress=True)
report={'scope':'Separate instrument assembly candidate; housings/lenses are closed bodies; markings and pointers are planar ink/sheet surfaces','source_sha256':hashlib.sha256((HERE/'instruments-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'instruments-inspection.glb').read_bytes()).hexdigest(),'closed_structural_bodies':checks,'mesh_and_curve_parts':sum(o.type in ['MESH','CURVE','FONT'] for o in parts.objects),'pose':P['initial_pose'],'pivots':['SPEED_NEEDLE_PIVOT','FUEL_NEEDLE_PIVOT'],'all_dimensions_estimated':True,'camera_calibrated':False,'physical_iphone_tested':False,'art_accepted':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_INSTRUMENTS_SOURCE',json.dumps(report))
