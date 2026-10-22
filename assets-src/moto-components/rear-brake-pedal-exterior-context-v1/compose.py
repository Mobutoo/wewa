"""One source-linked four-parent P15 context. No actions on import, no source/mesh/material edits."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/workspace/wewa');K='rear-brake-pedal-exterior-context-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;D=R/'creative/research'/K
COLLECTION='REAR_BRAKE_PEDAL_EXTERIOR_CONTEXT_V1';ROOT='REAR_BRAKE_PEDAL_EXTERIOR_CONTEXT_ROOT'
NAMES=['brake-pedal-'+n+'-v1'for n in ['arm','pivot-sleeve','linkage-lug','textured-pad']]
POSITIONS=[[0,0,0],[-.0063,.0063,-.032],[.07434,-.1084,.010],[.20916,-.20475,.050]]
ROLES=['Canonical arm; origin is photo bend datum, not pivot','Separate sleeve: axisZ, projected guide only; axial seating unknown','Separate lug: photo hole guide, Z/root unknown','PARKED_PAD: original face-study orientation, NOT mounted foot-plane orientation']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def look(ob,t):
 back=(ob.location-Vector(t)).normalized();right=Vector((0,1,0)).cross(back).normalized();up=back.cross(right).normalized();ob.rotation_euler=Matrix((right,up,back)).transposed().to_euler()
def build():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene;col=bpy.data.collections.new(COLLECTION);s.collection.children.link(col);root=bpy.data.objects.new(ROOT,None);col.objects.link(root);root['physical_count_increment']=0;root['frame']='Arm projected +X front / +Y up / +Z estimated outward';root['fit_qualified']=False;rows=[];inp=json.loads((D/'parent-native-read.json').read_text())['parents']
 for name,pos,role in zip(NAMES,POSITIONS,ROLES):
  row=next(x for x in inp if x['name']==name);p=R/row['source'];assert sha(p)==row['sha256'];names=[x['name']for x in row['objects']]
  with bpy.data.libraries.load(str(p),link=True)as(a,b):b.objects=list(names)
  local=bpy.data.collections.new(name+'__EXACT_NATIVE')
  for ob in b.objects:assert ob and ob.type=='MESH';local.objects.link(ob)
  inst=bpy.data.objects.new(name+'__RIGID_CONTEXT',None);col.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=local;inst.parent=root;inst.location=pos;inst['role']=role;inst['fit_qualified']=False
  rows.append(dict(parent=name,source=row['source'],sha256=row['sha256'],objects=names,matrix=[list(r)for r in inst.matrix_basis],scale=[1,1,1],role=role,geometry_linked=True,materials_linked=True))
 s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.cycles.max_bounces=5;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1000;s.render.resolution_y=750;s.render.resolution_percentage=100;s.view_layers[0].cycles.denoising_store_passes=True;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';world=bpy.data.worlds.new('Neutral original material context studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.15,.15,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;s.world=world
 center=Vector((.065,-.075,.015))
 for name,di,power in [('Key',(-.6,1,1.5),10),('Fill',(.5,-.8,1),6),('Reverse',(.1,1,-1),7)]:
  light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=.35;ob=bpy.data.objects.new(name,light);s.collection.objects.link(ob);ob.location=center+Vector(di)*.38;look(ob,center)
 cam=bpy.data.objects.new('Review camera',bpy.data.cameras.new('Review camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.52;cam.data.clip_start=.001;cam.data.clip_end=10;cam.location=center+Vector((.6,.7,2))*.38;look(cam,center)
 for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
 bpy.ops.wm.save_as_mainfile(filepath=str(H/(K+'.blend')),compress=True)
 write(D/'native-links-and-transforms.json',dict(parents=rows,collection=COLLECTION,root=ROOT,new_physical_ids=0,pose_type='Source-linked bounded local review; NOT mounted foot-control assembly',art_accepted=False))

def render(mode):
 if mode=='preview':assert json.loads((O/'gray-read.json').read_text())['actually_read']
 if mode=='final':assert json.loads((O/'preview-read.json').read_text())['actually_read']
 bpy.ops.wm.open_mainfile(filepath=str(H/(K+'.blend')));s=bpy.context.scene
 if mode=='gray':
  m=bpy.data.materials.new('Render-only neutral gray override');m.use_nodes=True;n=m.node_tree.nodes['Principled BSDF'];n.inputs['Base Color'].default_value=(.18,.18,.18,1);n.inputs['Roughness'].default_value=.32;s.view_layers[0].material_override=m
 views=[('profile',(0,0,3)),('quarter',(.6,.7,2)),('neutral',(-.7,.4,2))]
 if mode=='preview':views=views[:2]
 center=Vector((.065,-.075,.015));rows=[];(O/'raw').mkdir(exist_ok=True)
 for label,di in views:
  s.camera.location=center+Vector(di)*.38;look(s.camera,center);s.cycles.samples=96 if mode=='final' else 16
  if mode=='final'and label=='neutral':
   for l in bpy.data.lights:l.energy=0
   w=bpy.data.worlds.new('Independent neutral uniform white environment');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);w.node_tree.nodes['Background'].inputs[1].default_value=.65;s.world=w;s.view_settings.look='None'
  stem=mode+'-'+label;s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(stem+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(stem+'.png')),scene=s)
  rows.append(dict(name=stem,view=stem,png=stem+'.png',exr='raw/'+stem+'.exr',PNG_sha256=sha(O/(stem+'.png')),EXR_sha256=sha(O/'raw'/(stem+'.exr')),samples=s.cycles.samples,actual_native_render=True,resolution_px=[1000,750],camera=list(s.camera.location),look=s.view_settings.look))
 write(O/(mode+'-render-report.json'),dict(source_sha256=sha(H/(K+'.blend')),protocol_sha256=sha(Path(__file__)),views=rows,gray_override_only=mode=='gray',original_linked_materials_unchanged=True,fit_qualified=False,art_accepted=False))
if __name__=='__main__':
 mode=sys.argv[-1]
 if mode=='build':build()
 elif mode in ['gray','preview','final']:render(mode)
 else:raise ValueError(mode)
