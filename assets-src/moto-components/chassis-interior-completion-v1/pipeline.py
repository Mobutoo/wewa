"""Additive diagnostic kit. Read-only historical sources; no installed fit or G8."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d): (O/n).write_text(json.dumps(d,indent=2)+'\n')
stage=sys.argv[sys.argv.index('--')+1]
bpy.context.preferences.filepaths.save_version=0

def mesh(name,v,f,mat):
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.update();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);o['source_class']='documented_related_variant / estimated';o['reference']='D04 PDF sheet38 plate26 or sheet60 plate46; no dimensional scale';return o

def material(name,col,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m

def sweep(name,points,w,h,t,mat):
 # Explicit hollow rounded-rectangle section. Open review ends, no weld/cap.
 section=[]
 radius=min(w,h)*.22
 for a,b,start in [(w/2-radius,h/2-radius,0),(-w/2+radius,h/2-radius,90),(-w/2+radius,-h/2+radius,180),(w/2-radius,-h/2+radius,270)]:
  for j in range(5):
   ang=math.radians(start+j*22.5);section.append((a+radius*math.cos(ang),b+radius*math.sin(ang)))
 # section order starts top-right, progresses CCW
 N=len(section);v=[];frames=[]
 for k,p in enumerate(points):
  tangent=Vector(points[min(k+1,len(points)-1)])-Vector(points[max(k-1,0)]);tangent.normalize();u=Vector((1,0,0));u=(u-u.dot(tangent)*tangent).normalized();z=tangent.cross(u).normalized();frames.append((u,z))
  for factor in [1,1-2*t/min(w,h)]:
   for x,y in section:v.append(tuple(Vector(p)+u*x*factor+z*y*factor))
 f=[]
 for k in range(len(points)-1):
  for j in range(N):
   a=k*2*N+j;b=k*2*N+(j+1)%N;c=b+2*N;d=a+2*N;f.append((a,b,c,d));f.append((a+N,d+N,c+N,b+N))
 for k in [0,len(points)-1]:
  for j in range(N):
   a=k*2*N+j;b=k*2*N+(j+1)%N;f.append((a,a+N,b+N,b) if k==0 else (a,b,b+N,a+N))
 o=mesh(name,v,f,mat)
 # Recalculate consistent winding only in new construction.
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
 for p in o.data.polygons:p.use_smooth=True
 return o

def panel(name,x,ys,zs,holes,mat):
 # Planar carrier with actual open rectangular windows, not a solid filler box.
 v=[];f=[]
 for j in range(len(zs)-1):
  for i in range(len(ys)-1):
   if (i,j) in holes:continue
   a=len(v);v.extend([(x,ys[i],zs[j]),(x,ys[i+1],zs[j]),(x,ys[i+1],zs[j+1]),(x,ys[i],zs[j+1])]);f.append((a,a+1,a+2,a+3))
 o=mesh(name,v,f,mat);mod=o.modifiers.new('Estimated 1.5mm formed sheet','SOLIDIFY');mod.thickness=.0015;mod=o.modifiers.new('Small formed edge radius estimated','BEVEL');mod.width=.0006;mod.segments=3
 return o

def setup():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=640;s.render.resolution_y=600;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1;s.view_layers[0].cycles.denoising_store_passes=True
 if not s.world:s.world=bpy.data.worlds.new('Diagnostic neutral world')
 s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 target=Vector((0,.38,-.43))
 for name,loc,energy,size in [('Key',(1.6,-1,2),500,2),('Raking',(-1.6,1,1),450,1.5)]:
  l=bpy.data.lights.new(name,'AREA');l.energy=energy;l.shape='DISK';l.size=size;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 c=bpy.data.objects.new('Kit camera',bpy.data.cameras.new('Kit camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';c.data.ortho_scale=1.65;c.data.clip_start=.01;c.data.clip_end=30
 s['scope']='Interior context only; source-derived estimated child shapes; no installed fit, no G8';s.unit_settings.system='METRIC'

def save(name):
 for l in bpy.data.libraries:l.filepath=bpy.path.relpath(l.filepath,start=str(O))
 bpy.ops.wm.save_as_mainfile(filepath=str(O/name),compress=True)

def export(name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(O/name),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT')

def render(prefix,samples=12):
 s=bpy.context.scene;s.cycles.samples=samples;s.render.resolution_x=900 if samples==96 else 576;s.render.resolution_y=760 if samples==96 else 480
 views=[('quarter',(1.9,-1.2,.5)),('reverse',(-1.9,1.4,.3))]
 if samples==96:views.append(('profile',(2.5,.38,-.4)))
 result=[]
 for label,eye in views:
  c=s.camera;c.location=eye;target=Vector((0,.38,-.43));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/(prefix+'-'+label+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(prefix+'-'+label+'.png')),scene=s);result.append(dict(view=label,samples=samples,resolution=[s.render.resolution_x,s.render.resolution_y],eye=list(eye),target=list(target),ortho_scale_m=c.data.ortho_scale,png_sha256=sha(O/(prefix+'-'+label+'.png')),exr_sha256=sha(O/(prefix+'-'+label+'.exr'))));write(prefix+'-renders.json',result)

if stage=='context':
 bpy.ops.wm.open_mainfile(filepath=str(R/'assets-src/moto-components/whole-exterior-coverage-v14/whole-exterior-coverage-v14.blend'))
 keep=['frame-headtube','frame-front-backbone-v2','frame-front-downmember','frame-head-gusset','frame-lower-cradle-rail','frame-seat-rail-observed','swingarm-body','air-cleaner-box-outer-body-pf581003-v1','airbox-carb-boot-physical-study-v2']
 for o in list(bpy.context.scene.objects):
  if not any(o.name=='COVERAGE_PARENT ['+k+']'for k in keep):bpy.data.objects.remove(o,do_unlink=True)
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();copies=[];sources=[]
 for inst in dg.object_instances:
  if inst.is_instance and inst.object.type=='MESH':
   ob=inst.object;me=bpy.data.meshes.new_from_object(ob,preserve_all_data_layers=True,depsgraph=dg);n=bpy.data.objects.new(ob.name,me);n.matrix_world=inst.matrix_world.copy();copies.append(n)
 for o in bpy.context.scene.objects:
  if o.instance_collection:
   sources.append(dict(parent=o.name,matrix=[list(row)for row in o.matrix_world],collection=o.instance_collection.name))
 for o in list(bpy.context.scene.objects):bpy.data.objects.remove(o,do_unlink=True)
 for o in copies:bpy.context.scene.collection.objects.link(o);o['origin']='Evaluated source copy, unchanged shape, v14 rigid pose'
 # Omitted actual components; all poses rigid, no scale/reflection.
 extras=[('swingarm/pivot-shaft','swingarm-pivot-shaft-v1.blend','WEWA_SWINGARM_PIVOT_SHAFT_ISOLATED',(0,.34571263,-.7127853),(0,0,0)),('swingarm/pivot-bush','swingarm-pivot-bush-v1.blend','WEWA_SWINGARM_PIVOT_BUSH_ISOLATED',(.082,.34571263,-.7127853),(0,0,0)),('swingarm/chain-slider','swingarm-chain-slider-v1.blend','WEWA_SWINGARM_CHAIN_SLIDER_ISOLATED',(.086,.34571263,-.7127853),(-3,0,0)),('seat-base-observed-underside-v2','seat-base-observed-underside-v2.blend','WEWA_SEAT_BASE_OBSERVED_UNDERSIDE_V2',(0,.70,-.29),(0,0,0)),('seat-lateral-mount-lug-visible-v1','seat-lateral-mount-lug-visible-v1.blend','WEWA_SEAT_LATERAL_MOUNT_LUG_VISIBLE_V1',(.09,.60,-.34),(90,0,0)),('seat-damper-pedestal-v2','seat-damper-pedestal-v2.blend','WEWA_SEAT_DAMPER_PEDESTAL_V2',(.08,.65,-.29),(0,0,0))]
 for folder,file,col,pos,rot in extras:
  p=R/'assets-src/moto-components'/folder/file
  with bpy.data.libraries.load(str(p),link=True)as(a,b):assert col in a.collections;b.collections=[col]
  c=b.collections[0];bpy.context.scene.collection.children.link(c);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();pose=Matrix.Translation(pos)@__import__('mathutils').Euler([math.radians(v)for v in rot]).to_matrix().to_4x4();entries=[]
  for ob in c.all_objects:
   if ob.type!='MESH' or ob.hide_render:continue
   ev=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg);n=bpy.data.objects.new(ob.name,me);n.matrix_world=pose@ob.matrix_world;bpy.context.scene.collection.objects.link(n);n['origin']=str(p.relative_to(R));entries.append(dict(name=ob.name,local_bounds=[list(v)for v in ob.bound_box]))
  bpy.context.scene.collection.children.unlink(c);sources.append(dict(source=str(p.relative_to(R)),sha256=sha(p),collection=col,translation_m=pos,rotation_deg=rot,objects=entries,pose_status='estimated +/-30mm and +/-10deg, no fitted correspondence'))
 write('context-sources.json',sources);setup();save('context-native.blend');export('context-native.glb');render('context-gray',12)
elif stage=='gray':
 bpy.ops.wm.open_mainfile(filepath=str(O/'context-native.blend'))
 black=material('Estimated clean coated frame steel',(.022,.025,.028),.65,.36);rubber=material('Estimated battery polymer',(.018,.02,.022),0,.42);top=material('Estimated battery lid',(.07,.065,.055),0,.38)
 for ob in bpy.context.scene.objects:
  if ob.get('origin','').endswith('seat-base-observed-underside-v2.blend'):ob.matrix_world=Matrix.Translation((0,.70,-.265))@__import__('mathutils').Euler((0,math.pi,0)).to_matrix().to_4x4();ob['pose_revision']='underside ribs face down, rigid rotation Y180; +/-30mm remains'
 # Catalogue sheet38 observed central sweep and two side diagonal traces, dimensions bounded in plan.
 sweep('NEW central curved hollow member - related plate26',[(0,.251,-.313),(0,.27,-.35),(0,.294,-.40),(0,.312,-.46),(0,.326,-.53),(0,.34,-.61),(0,.346,-.705)],.043,.035,.002,black)
 for x in [.065,-.065]:sweep('NEW observed diagonal strut '+str(x),[(x,.345,-.65),(x,.43,-.54),(x,.53,-.43),(x,.64,-.34)],.018,.018,.0016,black)
 # Repeat the existing exemplar with rigid translation; no mirror/nonuniform scale.
 for token,dx in [('One observedface seatmember',-.16),('lowercradlerail',-.14)]:
  candidates=[o for o in bpy.context.scene.objects if o.type=='MESH' and token.lower() in o.name.lower()]
  for ob in candidates:
   n=ob.copy();n.data=ob.data;bpy.context.scene.collection.objects.link(n);n.name='PROVISIONAL opposite same exemplar '+ob.name;n.location.x+=dx;n['origin']='Approved provisional identical exemplar, rigid lateral translation only';n['uncertainty']='Side/section not confirmed; no mirrored hidden weld'
 # Carrier has 6 actual windows and open tray, based on plate46.
 panel('NEW battery case perforated back - six observed windows',-.07,[.405,.416,.45,.46,.494,.504,.538,.55],[-.566,-.554,-.52,-.51,-.476,-.464],{(i,j)for i in [1,3,5]for j in [1,3]},black)
 # open lower shelf and side folds, explicitly modelled as sheet profiles
 mesh('NEW battery case bent bottom shelf',[(-.07,.405,-.566),(-.15,.405,-.566),(-.15,.55,-.566),(-.07,.55,-.566)],[(0,1,2,3)],black).modifiers.new('1.5mm sheet','SOLIDIFY').thickness=.0015
 for y in [.405,.55]:
  mesh('NEW carrier folded side flange '+str(y),[(-.07,y,-.566),(-.15,y,-.566),(-.15,y,-.535),(-.07,y,-.535)],[(0,1,2,3)],black).modifiers.new('1.5mm sheet','SOLIDIFY').thickness=.0015
 # Battery is a separately identified observed component, no generic chassis hole filler.
 # Tapered case + stepped lid, made from measured-in-plan section loops.
 def battery(name,levels,mat):
  v=[]
  for z,x0,x1,y0,y1 in levels:v.extend([(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)])
  f=[(3,2,1,0)]
  for k in range(len(levels)-1):
   for j in range(4):a=k*4+j;b=k*4+(j+1)%4;f.append((a,b,b+4,a+4))
  f.append(tuple(range(4*(len(levels)-1),4*len(levels))))
  ob=mesh(name,v,f,mat);mod=ob.modifiers.new('Moulded case radius estimated','BEVEL');mod.width=.002;mod.segments=3;ob.modifiers.new('Weighted case normals','WEIGHTED_NORMAL');return ob
 battery('NEW battery JF401807 related envelope - no label or wiring',[(-.562,-.145,-.075,.418,.538),(-.455,-.148,-.072,.415,.541)],rubber)
 battery('NEW battery stepped lid observed plate46',[(-.455,-.15,-.07,.413,.543),(-.446,-.15,-.07,.413,.543)],top)
 # Visible rectangular strap at case midheight; no hidden buckle.
 mesh('NEW battery retention band - observed exterior strip',[(-.153,.415,-.505),(-.153,.543,-.505),(-.153,.543,-.489),(-.153,.415,-.489)],[(0,1,2,3)],rubber).modifiers.new('Estimated 2mm band','SOLIDIFY').thickness=.002
 write('new-children.json',[dict(name=o.name,source_class=o.get('source_class'),origin=o.get('origin'))for o in bpy.context.scene.objects if o.type=='MESH'])
 bpy.context.scene.view_layers[0].material_override=None
 save('kit-material.blend')
 # Gray export uses exact same geometry/material slots, texture maps retained in originals.
 gray=material('Diagnostic gray',(.25,.25,.25),0,.45)
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   o.data=o.data.copy()
   for i in range(len(o.data.materials)):o.data.materials[i]=gray
 save('kit-gray.blend');export('kit-gray.glb');render('gray-preview',12)
elif stage in ['material','final']:
 bpy.ops.wm.open_mainfile(filepath=str(O/'kit-material.blend'));export('kit-material.glb') if stage=='material' else None
 render('material-preview' if stage=='material' else 'material-96',12 if stage=='material' else 96)
else:raise ValueError(stage)
