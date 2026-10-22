"""One independent LH stay + original peg + original JK exemplar; rigid reuse only."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/workspace/wewa');K='passenger-footrest-left-exterior-context-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;D=R/'creative/research'/K;COL='PASSENGER_FOOTREST_LEFT_EXTERIOR_CONTEXT_V1';ROOT='PASSENGER_FOOTREST_LEFT_EXTERIOR_CONTEXT_ROOT';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def look(ob,t):
 back=(ob.location-Vector(t)).normalized();right=Vector((0,1,0)).cross(back).normalized();up=back.cross(right).normalized();ob.rotation_euler=Matrix((right,up,back)).transposed().to_euler()
def build():
 rows=json.loads((D/'native-parent-audit.json').read_text())['parents'];plan=json.loads((D/'plan.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene;col=bpy.data.collections.new(COL);s.collection.children.link(col);root=bpy.data.objects.new(ROOT,None);col.objects.link(root);root['physical_count_increment']=0;root['world_pose']='Unknown; source stay frame only, no frame/shock attachment assigned'
 poses=[(Matrix.Identity(3),[0,0,0]),(Matrix(plan['peg_R_rows']),plan['peg_translation_m']),(Matrix(plan['rubber_R_rows']),plan['rubber_translation_m'])];result=[]
 for row,(rot,pos) in zip(rows,poses):
  source=R/row['source'];assert sha(source)==row['sha256'];names=[x['name']for x in row['objects']]
  with bpy.data.libraries.load(str(source),link=True)as(a,b):b.objects=list(names)
  mat=rot.to_4x4();mat.translation=Vector(pos);assert abs(rot.determinant()-1)<1e-6
  for original in b.objects:
   ob=original.copy();col.objects.link(ob);ob.parent=root;ob.matrix_basis=mat@original.matrix_world;ob['source_parent']=row['parent'];ob['source_original_object']=original.name;ob['fit_qualified']=False;ob['physical_count_increment']=0
   assert ob.data==original.data and ob.data.library and all(a.material==b.material for a,b in zip(ob.material_slots,original.material_slots))
  result.append(dict(parent=row['parent'],source=row['source'],sha256=row['sha256'],objects=names,matrix=[list(r)for r in mat],scale=[1,1,1],mesh_data_linked_unchanged=True,source_materials_linked_unchanged=True))
 s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.cycles.max_bounces=5;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1000;s.render.resolution_y=750;s.render.resolution_percentage=100;s.view_layers[0].cycles.denoising_store_passes=True;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';w=bpy.data.worlds.new('Neutral uncalibrated local kit studio');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.15,.15,.15,1);w.node_tree.nodes['Background'].inputs[1].default_value=.6;s.world=w
 target=Vector((-.02,.16,.055))
 for name,di,power in [('Key',(-.7,1,1.5),18),('Fill',(.8,-.5,1),9),('Reverse',(.1,1,-1),10)]:
  l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=.35;ob=bpy.data.objects.new(name,l);s.collection.objects.link(ob);ob.location=target+Vector(di)*.38;look(ob,target)
 cam=bpy.data.objects.new('Kit review camera',bpy.data.cameras.new('Kit review camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.50;cam.data.clip_start=.001;cam.data.clip_end=10;cam.location=target+Vector((.8,.6,2))*.38;look(cam,target)
 for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
 bpy.ops.wm.save_as_mainfile(filepath=str(H/(K+'.blend')),compress=True)
 write(D/'native-links-and-transforms.json',dict(parents=result,collection=COL,root=ROOT,main_direct_mesh_wrappers=True,new_physical_ids=0,fit_qualified=False))

def render(mode):
 if mode=='preview':assert json.loads((O/'gray-read.json').read_text())['actually_read']
 if mode=='final':assert json.loads((O/'preview-read.json').read_text())['actually_read']
 bpy.ops.wm.open_mainfile(filepath=str(H/(K+'.blend')));s=bpy.context.scene
 if mode=='gray':
  m=bpy.data.materials.new('Render-only neutral gray override');m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.18,.18,.18,1);b.inputs['Roughness'].default_value=.32;s.view_layers[0].material_override=m
 target=Vector((-.02,.16,.055));views=[('source-facing',(0,0,3)),('quarter',(.8,.6,2)),('reverse',(-.7,.4,-2))]
 if mode=='preview':views=views[:2]
 if mode=='final':views=[views[0],views[1],('neutral',(-.6,.5,2)),('hinge-macro',(1,1.5,1))]
 rows=[];(O/'raw').mkdir(exist_ok=True)
 for label,di in views:
  t=target if label!='hinge-macro' else Vector((-.006,.239,.030));scale=.50 if label!='hinge-macro'else .115;dist=.38 if label!='hinge-macro'else .12;s.camera.data.ortho_scale=scale;s.camera.location=t+Vector(di)*dist;look(s.camera,t);s.cycles.samples=96 if mode=='final' else 16
  if label=='neutral':
   for light in bpy.data.lights:light.energy=0
   w=bpy.data.worlds.new('Independent neutral uniform white kit environment');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);w.node_tree.nodes['Background'].inputs[1].default_value=.65;s.world=w;s.view_settings.look='None'
  stem=mode+'-'+label;s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(stem+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(stem+'.png')),scene=s)
  rows.append(dict(name=stem,view=stem,png=stem+'.png',exr='raw/'+stem+'.exr',PNG_sha256=sha(O/(stem+'.png')),EXR_sha256=sha(O/'raw'/(stem+'.exr')),samples=s.cycles.samples,actually_saved=True,camera=list(s.camera.location),target=list(t),ortho_scale=scale,resolution_px=[1000,750],look=s.view_settings.look))
 write(O/(mode+'-render-report.json'),dict(source_sha256=sha(H/(K+'.blend')),protocol_sha256=sha(Path(__file__)),views=rows,gray_override_only=mode=='gray',original_materials_unchanged=True,fit_qualified=False,art_accepted=False))
if __name__=='__main__':
 mode=sys.argv[-1]
 if mode=='build':build()
 elif mode in ['gray','preview','final']:render(mode)
 else:raise ValueError(mode)
