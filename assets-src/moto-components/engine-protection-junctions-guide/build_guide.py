"""Context-only assembly hypothesis; copies frozen meshes, no new physical part."""
from pathlib import Path
import bpy,json,hashlib,math,numpy as np,sys
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];D=R/'creative/research/engine-protection-junctions-15-v1';O=R/'creative/reviews/engine-protection-junctions-guide-v1';T=H/'textures';T.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sys.path.insert(0,str(H));from camera_preflight import check_component_camera
plan=json.loads((D/'working-assembly-plan-v1.json').read_text());bfreeze=R/'creative/reviews/engine-protection-terminal-b-v1/source-freeze.json';assert all(sha(R/q['path'])==q['sha256']for q in json.loads(bfreeze.read_text())['files']);inputs=[]
def recipe(key,folder,name,col,angle,translation):
 p=R/'assets-src/moto-components'/folder/name;inputs.append({'role':key,'source':str(p.relative_to(R)),'source_sha256':sha(p),'collection':col,'EulerZ_deg_estimated':angle,'translation_m_estimated':translation});return inputs[-1]
recipe('tube','engine-protection-hoop','engine-protection-hoop-v1.blend','WEWA_ENGINE_PROTECTION_HOOP_TUBE_ISOLATED',0,[0,0,0])
recipe('terminalA','engine-protection-terminal-a','engine-protection-terminal-a-v1.blend','WEWA_ENGINE_PROTECTION_TERMINAL_A_ISOLATED',-90,[-.0435,0,-.255])
recipe('terminalB','engine-protection-terminal-b','engine-protection-terminal-b-v1.blend','WEWA_ENGINE_PROTECTION_TERMINAL_B_ISOLATED',90,[.0325,0,-.20355873274879294])
recipe('centreplate','engine-protection-centre-plate','engine-protection-centre-plate-v1.blend','WEWA_ENGINE_PROTECTION_CENTRE_PLATE_ISOLATED',0,[0,-.011,-.0295])
# This fourth placement is written before any Blender context is built.
extra={'state':'Working estimated centreplate placement before guide build','translation_m':[0,-.011,-.0295],'reason':'Return upper face near nominal undersideZ=-.010, front vertical plate behindY=-.010. Conditional formed-sheet/tube tangency hypothesis, not photo calibration/OEM datum.','unknowns':['Actual plate return/tube contact contour','Hidden joint and weld route','Whole guard installation/strength'],'no_new_physical_geometry':True}
p=D/'centreplate-contact-hypothesis-v1.json'
if p.exists():assert json.loads(p.read_text())==extra
else:p.write_text(json.dumps(extra,indent=2)+'\n')
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;context=bpy.data.collections.new('GUIDE_CONTEXT_ONLY_NO_NEW_PHYSICAL_COMPONENT');s.collection.children.link(context);objects={};digest=lambda a:hashlib.sha256(np.asarray(a).tobytes()).hexdigest()
for row in inputs:
 with bpy.data.libraries.load(str(R/row['source']),link=False)as(data,out):assert row['collection']in data.collections;out.collections=[row['collection']]
 col=out.collections[0];context.children.link(col);pose=Matrix.Translation(row['translation_m_estimated'])@Matrix.Rotation(math.radians(row['EulerZ_deg_estimated']),4,'Z');objects[row['role']]=[]
 for o in col.all_objects:
  assert o.type=='MESH'and not o.modifiers
  before=np.array([v.co[:]for v in o.data.vertices],np.float32);o.matrix_world=pose@o.matrix_world;after=np.array([v.co[:]for v in o.data.vertices],np.float32);assert np.array_equal(before,after);o['context_only']=True;o['source_sha256']=row['source_sha256'];objects[row['role']].append(o)
 row['local_mesh_position_digest']=digest(before);row['new_geometry_built']=False;row['actual_world_matrices']=[list(map(list,o.matrix_world))for o in objects[row['role']]]
linked=[{'name':db.name,'type':db.bl_rna.identifier,'library':db.library.filepath}for db in bpy.data.user_map()if db.library is not None]
print('GUIDE_LINKED_DATABLOCKS',linked,flush=True)
assert not linked,'Appended context must own every actual datablock before weakLibrary metadata removal'
weak_libraries=[{'filepath':l.filepath,'users':l.users}for l in bpy.data.libraries]
for l in list(bpy.data.libraries):bpy.data.libraries.remove(l)
assert not bpy.data.libraries
images=[]
for im in bpy.data.images:
 if im.source!='FILE':continue
 assert im.packed_file,'Guide must not depend on absolute loose image'
 data=bytes(im.packed_file.data);token=hashlib.sha256(data).hexdigest();name=token[:16]+'.png';p=T/name
 if p.exists():assert p.read_bytes()==data
 else:p.write_bytes(data)
 im.filepath='//textures/'+name;images.append({'image':im.name,'relative_path':im.filepath,'packed':True,'PNG_sha256':token,'bytes':len(data)})
# Actual transformed native triangles, not primitive bounds, for sampled contact witness.
def tree(obs):
 v=[];f=[]
 for o in obs:
  o.data.calc_loop_triangles();offset=len(v);v.extend([o.matrix_world@p.co for p in o.data.vertices]);f.extend([tuple(i+offset for i in t.vertices)for t in o.data.loop_triangles])
 return BVHTree.FromPolygons(v,f,all_triangles=True)
contacts=[]
for role,xx in [('terminalA',-.045),('terminalB',.045)]:
 tr=tree(objects[role]);rows=[]
 for rr in [.0085,.00925,.010]:
  for i in range(64):
   theta=2*math.pi*i/64;p=Vector((xx,rr*math.cos(theta),-.255+rr*math.sin(theta)));loc,n,index,distance=tr.find_nearest(p);assert loc is not None;rows.append({'nominal_tube_end_annulus_sample_m':list(p),'nearest_actual_plate_triangle':index,'nearest_actual_plate_point_m':list(loc),'distance_m':distance})
 contacts.append({'plate':role,'samples':rows,'max_sampled_distance_m':max(q['distance_m']for q in rows),'scope':'192 nominal annulus locations queried against actual transformed plate triangles; tube ring chosen from estimated tube radii. Sampled witness only, not full contact/overlap/strength proof.'})
# Explicit material/lights: geometry render is an override in RAM, source keeps PBR.
studio=bpy.data.collections.new('GUIDE_STUDIO_ONLY');s.collection.children.link(studio);s.world=bpy.data.worlds.new('Neutral guide world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.19,.22,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.25
for name,loc,power,size in [('KEY',(.6,-.8,.6),45,.65),('FILL',(-.6,-.2,.1),22,.55),('EDGE',(.2,.5,.3),30,.45)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,-.13))-o.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.cameras.new('Guide camera');c.type='ORTHO';c.clip_start=.001;c.clip_end=5;o=bpy.data.objects.new(c.name,c);studio.objects.link(o);s.camera=o;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.8
allobs=[o for group in objects.values()for o in group];views=[('whole-quarter',(.75,-1.1,.45),(0,0,-.13),.82,False),('terminal-a-contact',(-.11,-.095,-.205),(-.045,0,-.255),.095,True),('terminal-b-contact',(.11,-.095,-.205),(.045,0,-.255),.095,True)]
s.camera.location=views[0][1];s.camera.rotation_euler=(Vector(views[0][2])-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=views[0][3];bpy.context.view_layer.update();check_component_camera(s,allobs,allow_crop=False);src=H/'engine-protection-junctions-guide-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True,relative_remap=False);sources_unchanged=all(sha(R/q['source'])==q['source_sha256']for q in inputs);assert sources_unchanged;report={'scope':'Four unchanged frozen candidate meshes in a working author pose. No weld/new physical component/installed or OEM fit receipt.','source_sha256':sha(src),'source_inputs':inputs,'source_meshes_unchanged':sources_unchanged,'all_poses_estimated':True,'no_external_libraries':True,'removed_append_weak_library_metadata':weak_libraries,'actual_linked_datablocks_before_removal':linked,'images':images,'contact_witnesses':contacts,'whole_guard_complete':False,'lower_B_perforation_unresolved':True,'art_accepted':False};(O/'guide-build-report.json').write_text(json.dumps(report,indent=2)+'\n')
mat=bpy.data.materials.new('Geometry gray override only');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.30,.32,.35,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.40
for o in allobs:o.data.materials.clear();o.data.materials.append(mat)
rr=[]
for name,eye,target,scale,crop in views:
 if crop:eye=Vector(target)+(Vector(eye)-Vector(target))*4
 s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;bpy.context.view_layer.update();pre=check_component_camera(s,allobs,allow_crop=crop);png=O/('gray-'+name+'.png');s.render.filepath=str(png);bpy.ops.render.render(write_still=True);q={'source_sha256':sha(src),'name':name,'PNG_sha256':sha(png),'samples':12,'resolution_px':[1400,1000],'camera_eye_m':list(eye),'camera_target_m':target,'ortho_scale_m':scale,'camera_preflight':pre,'gray_override_not_saved_in_source':True,'all_poses_estimated':True,'art_accepted':False};png.with_suffix('.json').write_text(json.dumps(q,indent=2)+'\n');rr.append(q);(O/'gray-render-report.json').write_text(json.dumps({'views':rr,'source_sha256':sha(src),'art_accepted':False},indent=2)+'\n')
assert sha(src)==report['source_sha256']and all(sha(R/q['source'])==q['source_sha256']for q in inputs);print('GUARD_CONTACT_GUIDE_THREE_GRAYS_EXIT0',flush=True)
