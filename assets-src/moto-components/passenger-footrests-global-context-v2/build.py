import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector,Euler
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda n,d:(O/n).write_text(json.dumps(d,indent=2)+'\n')
phase=sys.argv[sys.argv.index('--')+1];bpy.context.preferences.filepaths.save_version=0

def attach(source,col=None,obj=None):
 p=R/source
 with bpy.data.libraries.load(str(p),link=True)as(a,b):
  if col:b.collections=[col]
  else:b.objects=[obj]
 return b.collections[0]if col else b.objects[0]

def flat(col,m,label,group):
 result=[]
 for ob in col.all_objects:
  if ob.type!='MESH'or ob.hide_render:continue
  cp=ob.copy();cp.name=label+' '+ob.name;cp.matrix_world=m@ob.matrix_world;group.objects.link(cp);cp['source_original_object']=ob.name;result.append(cp)
 return result

def bvh(obs):
 vs=[];fs=[];dg=bpy.context.evaluated_depsgraph_get()
 for ob,mat in obs:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();base=len(vs);vs.extend(mat@v.co for v in me.vertices);fs.extend(tuple(base+i for i in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
 return BVHTree.FromPolygons(vs,fs,all_triangles=True),vs

def render(prefix,samples,views):
 s=bpy.context.scene;s.cycles.samples=samples;s.render.resolution_x=1000 if samples==96 else 640;s.render.resolution_y=800 if samples==96 else 512;rows=[]
 for name,eye,target,scale in views:
  c=s.camera;c.location=eye;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/(prefix+'-'+name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(prefix+'-'+name+'.png')),scene=s);rows.append(dict(name=name,samples=samples,eye=eye,target=target,ortho_scale=scale,png_sha256=sha(O/(prefix+'-'+name+'.png')),exr_sha256=sha(O/(prefix+'-'+name+'.exr'))));write(prefix+'-report.json',rows)
views=[('LH',(1.8,1.6,.35),(0,.62,-.47),1.35),('RH',(-1.8,1.5,.3),(0,.62,-.47),1.35),('profile',(2.5,.62,-.3),(0,.62,-.47),1.35)]

if phase=='build':
 bpy.ops.wm.read_factory_settings(use_empty=True)
 contextfile=R/'assets-src/moto-components/chassis-interior-completion-v1/kit-linked-v2.blend'
 with bpy.data.libraries.load(str(contextfile),link=True)as(a,b):b.objects=[n for n in a.objects if n.startswith(('COVERAGE_PARENT','OMITTED source','PROVISIONAL opposite','NEW children observed'))]
 for ob in b.objects:bpy.context.scene.collection.objects.link(ob)
 s=bpy.context.scene
 # Existing SNS linked once per diagnostic side, not delivered as new passenger parts.
 col=attach('assets-src/moto-components/rear-sns/rest-assembly/rear-sns-rest-assembly-v3.blend',col='WEWA_REAR_SNS_REST_COMPOSITION')
 for side,x,rot in [('LH',.13,(0,20,-90)),('RH',-.13,(0,-20,90))]:
  ob=bpy.data.objects.new('SNS diagnostic '+side,None);s.collection.objects.link(ob);ob.instance_type='COLLECTION';ob.instance_collection=col;ob.location=(x,.826865,-.635223);ob.rotation_euler=[math.radians(v)for v in rot]
 # Instanced full chassis source remains linked, no geometry change.
 QL=Matrix.Rotation(math.radians(75),3,'X')@Matrix(((0,0,1),(-2**-.5,-2**-.5,0),(2**-.5,-2**-.5,0)));QR=QL@Matrix(((-1,0,0),(0,1,0),(0,0,-1)))
 sourceRows=json.loads((O/'rejected-parent-evaluation-integration-fragment.json').read_text());write('integration-fragment-initial-clock0.json',sourceRows)
 group=bpy.data.collections.new('PASSENGER_FOOTRESTS_GLOBAL_CONTEXT_V2');s.collection.children.link(group);allparts=[];partsBySide={};poses={}
 left=attach('assets-src/moto-components/passenger-footrest-left-exterior-context-v1/passenger-footrest-left-exterior-context-v1.blend',col='PASSENGER_FOOTREST_LEFT_EXTERIOR_CONTEXT_V1')
 rightstay=attach('assets-src/moto-components/passenger-footrest-stay-right-v1/child-candidate.blend',obj='PF113003_RIGHT_PASSENGER_STAY_FORMED_ARMS_EYE_GUSSET_U_CLEVIS')
 # Independent right source; common peg/rubber linked original data, authorised qty2.
 for side,q,anchor,hinge,foldangle in [('LH',QL,Vector((-.006,.239,.0195)),Vector((.1,.65,-.555)),-90),('RH',QR,Vector((.004,.239,.0195)),Vector((-.1,.65,-.555)),90)]:
  M=q.to_4x4();M.translation=hinge-q@anchor;F=Matrix.Translation(anchor)@Matrix.Rotation(math.radians(foldangle),4,'Y')@Matrix.Translation(-anchor);poses[side]={'stay_matrix':[list(r)for r in M],'peg_fold_in_stay_frame':[list(r)for r in F],'clock75_about_world_X':True,'fold_angle_deg':foldangle,'hinge':list(hinge)};parts=[]
  if side=='LH':
   for ob in left.all_objects:
    if ob.type!='MESH':continue
    cp=ob.copy();cp.parent=None;cp.name=side+' '+ob.name;native=ob.matrix_basis.copy();cp.matrix_world=M@(F if 'STAY'not in ob.name else Matrix.Identity(4))@native;group.objects.link(cp);cp['source_original_object']=ob.name;cp['source_part']='stay'if'STAY'in ob.name else'rubber'if'RUBBER'in ob.name else'peg';parts.append(cp)
  else:
   cp=rightstay.copy();cp.name='RH '+rightstay.name;cp.matrix_world=M@rightstay.matrix_world;cp['source_original_object']=rightstay.name;cp['source_part']='stay';group.objects.link(cp);parts.append(cp)
   for ob in left.all_objects:
    if ob.type!='MESH'or'STAY'in ob.name:continue
    local=ob.matrix_basis.copy();local.translation.x=.004;cp=ob.copy();cp.parent=None;cp.name='RH '+ob.name;cp.matrix_world=M@F@local;cp['source_original_object']=ob.name;cp['source_part']='rubber'if'RUBBER'in ob.name else'peg';group.objects.link(cp);parts.append(cp)
  for cp in parts:cp['side']=side
  partsBySide[side]=parts;allparts+=parts
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();environment=[];sns=[]
 for ins in dg.object_instances:
  if ins.is_instance and ins.object.type=='MESH'and not ins.object.hide_render:
   if ins.parent and ins.parent.original.name.startswith('SNS diagnostic'):sns.append((ins.object.original,ins.matrix_world.copy()))
   else:environment.append((ins.object.original,ins.matrix_world.copy()))
 # Aggregated exact surface intersections. Nearest sampled vertices are diagnostics, not clearance bounds.
 eb,ev=bvh(environment);sb,sv=bvh(sns);checks=[]
 # Bounded rigid search, actual mesh surfaces; prefer no intersections, then small departure.
 scan=[]
 for side,parts in partsBySide.items():
  originals=[ob.matrix_world.copy()for ob in parts];candidates=[]
  for dx0 in [-.025,-.015,0,.015,.025]:
   for dy in [-.06,-.03,0]:
    dx=dx0 if side=='LH'else-dx0;delta=Matrix.Translation((dx,dy,0));pb,pv=bvh([(ob,delta@m)for ob,m in zip(parts,originals)]);nframe=len(pb.overlap(eb));nsns=len(pb.overlap(sb));score=(dx*dx+dy*dy)**.5;candidates.append({'side':side,'delta_world':[dx,dy,0],'frame_surface_intersections':nframe,'sns_surface_intersections':nsns,'translation_norm_m':score})
  clean=[r for r in candidates if r['frame_surface_intersections']==0 and r['sns_surface_intersections']==0]
  chosen=min(clean,key=lambda r:r['translation_norm_m'])if clean else min(candidates,key=lambda r:(r['frame_surface_intersections']+r['sns_surface_intersections'],r['translation_norm_m']))
  delta=Matrix.Translation(chosen['delta_world'])
  for ob,m in zip(parts,originals):ob.matrix_world=delta@m
  poses[side]['bounded_translation_revision']=chosen;scan.extend(candidates)
 bpy.context.view_layer.update();write('bounded-placement-scan.json',{'candidates':scan,'chosen':{side:poses[side]['bounded_translation_revision']for side in partsBySide},'scope':'Rigid geometry-only search within visual hinge allowances. No mounting role, hidden bridge or accepted physical tolerance inferred.'})
 for ob in allparts:
  pb,pv=bvh([(ob,ob.matrix_world)]);er=pb.overlap(eb);sr=pb.overlap(sb);steps=max(1,len(pv)//5000);checks.append(dict(name=ob.name,side=ob['side'],part=ob['source_part'],frame_triangle_surface_intersections=len(er),sns_triangle_surface_intersections=len(sr),sampled_vertex_min_frame_distance_m=min(eb.find_nearest(v)[3]for v in pv[::steps]),sampled_vertex_min_sns_distance_m=min(sb.find_nearest(v)[3]for v in pv[::steps]),sampling_step=steps,matrix_world=[list(r)for r in ob.matrix_world]))
 write('collision-audit.json',{'clock_deg':75,'parts':checks,'SNS_RH_pose':'diagnostic inferred opposite same source; main must compare to final SNS matrices','surface_only':True,'no_hidden_pins_or_welds':True,'all_dimensions_estimated':True});write('poses-revised.json',poses)
 # Build integration from exact actual wrapper matrices, direct source objects, no mirrored stays.
 additions=[]
 origins=json.loads((R/'creative/research/passenger-footrest-left-exterior-context-v1/native-links-and-transforms.json').read_text())['parents']
 for ob in allparts:
  if ob['side']=='RH'and ob['source_part']=='stay':src='assets-src/moto-components/passenger-footrest-stay-right-v1/child-candidate.blend'
  else:src=next(r['source']for r in origins if ob['source_original_object']in r['objects'])
  additions.append({'key':ob.name,'source':src,'sha256':sha(R/src),'selected_objects':[ob['source_original_object']],'matrix_world':[list(r)for r in ob.matrix_world],'matrix_application':'instance parent applies this to original source object; source object native matrix identity in original child files','nested':[],'source_class':'documented_related_variant / estimated','side':ob['side'],'part':ob['source_part']})
 sourceRows['additions']=additions;sourceRows['status']='clock75 and folded peg candidate; actual collision audit in collision-audit.json';sourceRows['notes']=['Replaces initial clock0 candidate: its short terminal was217mm LH /210mm RH from frame.','Clock75 gives terminal centre-to-frame surface proximity3mm LH and10mm RH, not identified mounting holes.','Peg/rubber fold around existing native hinge axes, independent stay geometry unchanged.'];write('integration-fragment.json',sourceRows)
 # Native small linked collection: 6 objects referencing exact historical mesh/material data.
 # Separate libraries.write checkpoint omitted: Blender4.3.2 invalidates live name map after this operation; canonical collection is saved in context-material-linked.blend.
 bpy.ops.object.select_all(action='DESELECT')
 for ob in allparts:ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(O/'passenger-pair-material.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
 # Keep native geometry evidence and pair only. Context stays library-linked for render.
 vertexRows=[]
 for ob in allparts:
  me=ob.evaluated_get(dg).to_mesh();pts=[ob.matrix_world@v.co for v in me.vertices];vertexRows.append({'name':ob.name,'bounds':[[min(v[i]for v in pts)for i in range(3)],[max(v[i]for v in pts)for i in range(3)]],'matrix_world':[list(r)for r in ob.matrix_world]});ob.evaluated_get(dg).to_mesh_clear()
 write('native-evaluated-world.json',vertexRows)
 # lights from chassis baseline, no whole-bike surfaces added.
 s.view_layers[0].material_override=None;s.cycles.samples=12;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.view_layers[0].cycles.denoising_store_passes=True
 # Keep library paths as loaded; indirect library paths are relative to their parent libraries.
 s.render.engine='CYCLES';s.unit_settings.system='METRIC';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.resolution_percentage=100
 w=bpy.data.worlds.new('Neutral source-context world');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.13,.13,.13,1);w.node_tree.nodes['Background'].inputs[1].default_value=.5;s.world=w
 for lname,loc,power in [('Key',(2,0,2),550),('Fill',(-2,1,1),450)]:
  ld=bpy.data.lights.new(lname,'AREA');ld.energy=power;ld.shape='DISK';ld.size=2;lo=bpy.data.objects.new(lname,ld);s.collection.objects.link(lo);lo.location=loc;lo.rotation_euler=(Vector((0,.62,-.47))-lo.location).to_track_quat('-Z','Y').to_euler()
 cam=bpy.data.objects.new('Passenger context camera',bpy.data.cameras.new('Passenger context camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.clip_start=.01;cam.data.clip_end=30
 dups={}
 for typ in ['objects','meshes','materials','collections','images','libraries']:
  seen={};dups[typ]=[]
  for dd in getattr(bpy.data,typ):
   key=(dd.name,dd.library.filepath if dd.library else None)
   if key in seen:dups[typ].append([key,seen[key],str(dd.as_pointer())])
   seen[key]=str(dd.as_pointer())
 write('datablock-diagnostics.json',dups)
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'context-material-linked.blend'),compress=True,relative_remap=False)
 # Gray pair export is temporary evaluated mesh copies, only six selected objects.
 gray=bpy.data.materials.new('Pair neutral diagnostic gray');gray.use_nodes=True;bs=gray.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.25,.25,.25,1);bs.inputs['Roughness'].default_value=.45
 for ob in allparts:
  ob.data=ob.data.copy()
  for i in range(len(ob.data.materials)):ob.data.materials[i]=gray
 bpy.ops.export_scene.gltf(filepath=str(O/'passenger-pair-gray.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
 s.view_layers[0].material_override=gray
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'context-gray-linked.blend'),compress=True,relative_remap=False);render('gray-preview',12,views[:2])
elif phase in ['preview','final']:
 bpy.ops.wm.open_mainfile(filepath=str(O/'context-material-linked.blend'));render('material-preview'if phase=='preview'else'native-96',12 if phase=='preview'else 96,views[:2]if phase=='preview'else views)
else:raise ValueError(phase)
