"""Original continuous currentRDC-looking bellows; all millimetres remain estimates."""
import bpy,bmesh,math,json,hashlib,sys,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(HERE));from bellows_profile import profiles,validate_profile
from gltf_morph_tangent_compat import corrected_morph_tangent_export
P=json.loads((HERE/'parameters.json').read_text());OUT=ROOT/'creative/reviews/fork-bellows-v1';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('WEWA_FORK_BELLOWS_ISOLATED');s.collection.children.link(col);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
N=P['radial_segments'];states={}
for name,H in [('Basis',P['length_working_m']),('Compression visual estimate H110mm',P['compression_review_length_m']),('Extension visual estimate H140mm',P['extension_review_length_m'])]:
 outer,inner,wall=profiles(P,H);check=validate_profile(outer,inner,wall);meridian=np.concatenate([outer,inner[::-1]]);phi=np.arange(N)*math.tau/N;vertices=np.stack([meridian[:,0,None]*np.cos(phi),meridian[:,0,None]*np.sin(phi),np.broadcast_to(meridian[:,1,None],(len(meridian),N))],axis=-1).reshape(-1,3);states[name]={'length':H,'outer':outer,'inner':inner,'wall':wall,'vertices':vertices,'meridian_check':check}
M=len(states['Basis']['outer']);rings=2*M;faces=[];face_meta=[]
for k in range(rings):
 other=(k+1)%rings;lip=k in [M-1,rings-1]
 for j in range(N):
  a=k*N+j;b=k*N+(j+1)%N;c=other*N+(j+1)%N;d=other*N+j;faces.extend([(a,b,c),(a,c,d)]);face_meta.extend([(k,j,lip,0),(k,j,lip,1)])
base=states['Basis'];mesh=bpy.data.meshes.new('Continuous original bellows wall with normal-offset meridians');mesh.from_pydata(base['vertices'].tolist(),[],faces);mesh.update();o=bpy.data.objects.new('Single fork bellows - estimated currentRDC visual candidate',mesh);col.objects.link(o)
outer_arc=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(base['outer'],axis=0),axis=1))]);inner_arc=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(base['inner'],axis=0),axis=1))]);arc=np.concatenate([outer_arc,inner_arc[::-1]]);uv=mesh.uv_layers.new(name='14 circumferential repeats and10mm meridian reference')
for f,(k,j,lip,tri) in zip(mesh.polygons,face_meta):
 f.use_smooth=not lip
 if lip:
  for li in f.loop_indices:
   q=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(q.x/.010,q.y/.010)
 else:
  u0=j/N*P['circumferential_UV_repeats'];u1=(j+1)/N*P['circumferential_UV_repeats'];v0=arc[k]/P['meridian_UV_reference_tile_m'];v1=arc[(k+1)%rings]/P['meridian_UV_reference_tile_m'];coords=[(u0,v0),(u1,v0),(u1,v1)] if tri==0 else [(u0,v0),(u1,v1),(u0,v1)]
  for li,co in zip(f.loop_indices,coords):uv.data[li].uv=co
mesh.set_sharp_from_angle(angle=.8)
m=bpy.data.materials.new('Neutral bellows geometry - final rubber pending');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.20,.22,.24,1);p.inputs['Roughness'].default_value=.38;p.inputs['Metallic'].default_value=0;mesh.materials.append(m)
for name,state in states.items():
 key=o.shape_key_add(name=name,from_mix=False);key.data.foreach_set('co',state['vertices'].astype(np.float32).ravel());key.slider_min=0;key.slider_max=1
for key in o.data.shape_keys.key_blocks:key.value=0
# Verify topology once, then the actual vertex geometry of five exclusive morph states.
bm=bmesh.new();bm.from_mesh(mesh);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;stack=[unseen.pop()]
 while stack:
  for ed in stack.pop().link_edges:
   for v in ed.verts:
    if v in unseen:unseen.remove(v);stack.append(v)
nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free();assert shells==1 and not nonmanifold
indices=np.array(faces,dtype=np.int32);rows=[];state_mix=[('base',[0,0]),('half_compression',[.5,0]),('compression',[1,0]),('half_extension',[0,.5]),('extension',[0,1])];targets=list(states.values())[1:]
for name,weights in state_mix:
 v=base['vertices'].copy();outer=base['outer'].copy();inner=base['inner'].copy()
 for w,target in zip(weights,targets):v+=w*(target['vertices']-base['vertices']);outer+=w*(target['outer']-base['outer']);inner+=w*(target['inner']-base['inner'])
 profile_check=validate_profile(outer,inner,base['wall'],exact_normal_offset=all(w in [0,1] for w in weights));a=v[indices[:,0]];b=v[indices[:,1]];c=v[indices[:,2]];area=np.linalg.norm(np.cross(b-a,c-a),axis=1)/2;volume=float(np.einsum('ij,ij->i',a,np.cross(b,c)).sum()/6);clearance=float(np.linalg.norm(v[:,:2],axis=1).min()*math.cos(math.pi/N)-.0155);assert volume>0 and area.min()>1e-18 and clearance>0
 rows.append({'name':name,'weights':weights,'bounds_min_m':v.min(0).tolist(),'bounds_max_m':v.max(0).tolist(),'signed_volume_m3':volume,'min_triangle_area_m2':float(area.min()),'zero_area_triangles_at_1e18_m2':int((area<=1e-18).sum()),'tubeR15_5_conservative_radial_clearance_m':clearance,'profile_wall_check':profile_check})
tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],faces,all_triangles=True);axis_clear=tree.ray_cast(Vector((0,0,-.01)),Vector((0,0,1)),.17)[0] is None;rim_present=tree.ray_cast(Vector((.0215,0,-.01)),Vector((0,0,1)),.03)[0] is not None;assert axis_clear and rim_present
o['component_id']=P['component_id'];o['installed_pose_verified']=False;o['manufacturer_travel_verified']=False;o['morph_rule']='For110..125mm use compression only; for125..140mm extension only. Review deformation estimate.'
r={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'vertices':len(mesh.vertices),'triangles':len(faces),'non_manifold_edges':nonmanifold,'connected_shells':shells,'axis_clear':axis_clear,'lower_rim_present':rim_present,'morph_targets':list(states.keys())[1:],'morph_states':rows,'signed_volume_m3':rows[0]['signed_volume_m3'],'all_dimensions_estimated':True,'fold_count_photo_inferred_uncertainty':1,'manufacturer_travel_verified':False,'art_accepted':False}
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
with corrected_morph_tangent_export(OUT/'morph-tangent-compatibility-check.json'):
 bpy.ops.export_scene.gltf(filepath=str(HERE/'fork-bellows-inspection.glb'),export_format='GLB',use_selection=True,export_apply=False,export_texcoords=True,export_normals=True,export_tangents=True,export_morph=True,export_morph_normal=True,export_morph_tangent=True)
w=bpy.data.worlds.new('Bellows neutral studio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.45
for name,loc,power,size in [('KEY',(.12,.10,.22),2,.20),('FILL',(-.16,.08,.12),1,.18),('EDGE',(.12,-.15,.12),1.5,.16),('LOWER',(-.10,.10,-.10),.7,.15)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;x=bpy.data.objects.new(name,d);studio.objects.link(x);x.location=loc;x.rotation_euler=(Vector((0,0,.0625))-x.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('BELLOWS_CAMERA',bpy.data.cameras.new('BELLOWS_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.14,.22,.14);cam.rotation_euler=(Vector((0,0,.0625))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.16;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1000;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG';bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'fork-bellows-v1.blend'),compress=True);r['source_sha256']=hashlib.sha256((HERE/'fork-bellows-v1.blend').read_bytes()).hexdigest();r['export_sha256']=hashlib.sha256((HERE/'fork-bellows-inspection.glb').read_bytes()).hexdigest();(OUT/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_BELLOWS_SOURCE',json.dumps(r))
