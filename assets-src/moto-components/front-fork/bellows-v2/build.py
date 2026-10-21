"""Original continuous currentRDC-looking bellows; all millimetres remain estimates."""
import bpy,bmesh,math,json,hashlib,sys,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(HERE));from bellows_profile import profiles,validate_profile,shape_vertices,validate_closed_meridian
from gltf_morph_tangent_compat import corrected_morph_tangent_export
P=json.loads((HERE/'parameters.json').read_text());OUT=ROOT/'creative/reviews/fork-bellows-v2';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('WEWA_FORK_BELLOWS_V2_ISOLATED');s.collection.children.link(col);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
N=P['radial_segments'];states={}
for name,H in [('Basis',P['length_working_m']),('Compression visual estimate H110mm',P['compression_review_length_m']),('Extension visual estimate H140mm',P['extension_review_length_m'])]:
 state=shape_vertices(P,H);state['length']=H;state['meridian_check']=validate_profile(state['outer'],state['inner'],state['wall']);states[name]=state
base=states['Basis'];M=len(base['outer']);rings=len(base['meridian']);faces=[];face_meta=[]
for k in range(rings):
 other=(k+1)%rings
 for j in range(N):
  a=k*N+j;b=k*N+(j+1)%N;c=other*N+(j+1)%N;d=other*N+j;faces.extend([(a,b,c),(a,c,d)]);face_meta.extend([(k,j,0),(k,j,1)])
base=states['Basis'];mesh=bpy.data.meshes.new('Original bellows v2 doublelip annularreturn and localbridges');mesh.from_pydata(base['vertices'].tolist(),[],faces);mesh.update();o=bpy.data.objects.new('Single revisedbellows - relatedcuff hypothesis, currentRDC identity open',mesh);col.objects.link(o)
arc=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(base['meridian'],axis=0),axis=1))]);closed_arc=arc[-1]+np.linalg.norm(base['meridian'][-1]-base['meridian'][0]);meridian_repeats=max(1,round(closed_arc/P['meridian_UV_reference_tile_m']));uv=mesh.uv_layers.new(name='14 angular repeats; continuous integerclosedmeridian reference10mm')
for f,(k,j,tri)in zip(mesh.polygons,face_meta):
 f.use_smooth=True;u0=j/N*P['circumferential_UV_repeats'];u1=(j+1)/N*P['circumferential_UV_repeats'];v0=arc[k]/closed_arc*meridian_repeats;v1=(arc[k+1]if k+1<rings else closed_arc)/closed_arc*meridian_repeats;coords=[(u0,v0),(u1,v0),(u1,v1)]if tri==0 else[(u0,v0),(u1,v1),(u0,v1)]
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
 profile_check=validate_profile(outer,inner,base['wall'],exact_normal_offset=all(w in[0,1]for w in weights));a=v[indices[:,0]];b=v[indices[:,1]];c=v[indices[:,2]];area=np.linalg.norm(np.cross(b-a,c-a),axis=1)/2;volume=float(np.einsum('ij,ij->i',a,np.cross(b,c)).sum()/6);clearance=float(np.linalg.norm(v[:,:2],axis=1).min()*math.cos(math.pi/N)-.0155);assert volume>0 and area.min()>1e-18 and clearance>0
 grid=v.reshape(rings,N,3);sectionchecks=[]
 for j in range(N//(2*P['lower_local_radial_bridge_count_working'])+1):
  rz=np.stack([np.linalg.norm(grid[:,j,:2],axis=1),grid[:,j,2]],-1);sectionchecks.append({'angular_index':j,**validate_closed_meridian(rz)})
 rows.append({'name':name,'weights':weights,'bounds_min_m':v.min(0).tolist(),'bounds_max_m':v.max(0).tolist(),'signed_volume_m3':volume,'min_triangle_area_m2':float(area.min()),'zero_area_triangles_at_1e18_m2':int((area<=1e-18).sum()),'tubeR15_5_conservative_radial_clearance_m':clearance,'profile_wall_check':profile_check,'closed_meridian_angles_checked':len(sectionchecks),'all_closed_meridians_without_crossing':True,'minimum_profile_segment_length_m':min(q['minimum_segment_length_m']for q in sectionchecks)})
 if name=='base':base_sections=sectionchecks
tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],faces,all_triangles=True);probes=[]
def probe(label,origin,direction,distance,clear,expected=None,tolerance=.00001):
 hit=tree.ray_cast(Vector(origin),Vector(direction),distance);assert(hit[0]is None)==clear,(label,hit)
 if expected is not None:assert abs(hit[3]-expected)<tolerance,(label,hit[3],expected)
 probes.append({'label':label,'origin_m':list(origin),'direction':list(direction),'distance_m':distance,'clear':clear,'actual_hit_distance_m':hit[3]if hit[0]is not None else None,'expected_hit_distance_m':expected,'digital_tolerance_m':tolerance if expected is not None else None})
probe('centralaxisclear',(0,0,-.01),(0,0,1),.17,True)
probe('entrythroatR22_5free',(0.0225,0,-.01),(0,0,1),.013,True)
probe('innerlipmaterial',(.0236,0,-.01),(0,0,1),.015,False)
rr=.02485;probe('grooveopen_betweenbridges',(rr/math.sqrt(2),rr/math.sqrt(2),-.01),(0,0,1),.012,True)
probe('conditionalradialbridge',(.02485,0,-.01),(0,0,1),.012,False)
probe('entryradialsection',(0,0,.002),(1,0,0),.04,False,P['lower_cuff_opening_working_m']/2)
probe('innerradialseat',(0,0,.008),(1,0,0),.04,False,P['lower_inner_chamber_radius_m'])
axis_clear=True;rim_present=True
lip_mask=np.arange(rings)>=base['lower_lip_start_ring']
for target in targets:assert np.array_equal(target['vertices'].reshape(rings,N,3)[lip_mask],base['vertices'].reshape(rings,N,3)[lip_mask])
o['component_id']=P['component_id'];o['installed_pose_verified']=False;o['manufacturer_travel_verified']=False;o['morph_rule']='For110..125mm use compression only; for125..140mm extension only. Review deformation estimate.'
r={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'vertices':len(mesh.vertices),'triangles':len(faces),'non_manifold_edges':nonmanifold,'connected_shells':shells,'axis_clear':axis_clear,'lower_rim_present':rim_present,'morph_targets':list(states.keys())[1:],'morph_states':rows,'profile_rings':rings,'outer_rings':M,'upper_lip_rings':base['upper_lip_rings'],'lower_lip_rings':base['lower_lip_rings'],'base_closed_profile_checks':base_sections,'actual_source_probes':probes,'lower_lip_identical_across_length_morphs':True,'closed_meridian_UV_repeats':meridian_repeats,'closed_meridian_UV_actual_period_m':float(closed_arc/meridian_repeats),'signed_volume_m3':rows[0]['signed_volume_m3'],'all_dimensions_estimated':True,'fold_count_photo_inferred_uncertainty':1,'manufacturer_travel_verified':False,'art_accepted':False}
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
with corrected_morph_tangent_export(OUT/'morph-tangent-compatibility-check.json'):
 bpy.ops.export_scene.gltf(filepath=str(HERE/'fork-bellows-v2-inspection.glb'),export_format='GLB',use_selection=True,export_apply=False,export_texcoords=True,export_normals=True,export_tangents=True,export_morph=True,export_morph_normal=True,export_morph_tangent=True)
w=bpy.data.worlds.new('Bellows neutral studio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.30
for name,loc,power,size in [('KEY',(.12,.10,.22),.60,.15),('FILL',(-.16,.08,.12),.15,.14),('EDGE',(.12,-.15,.12),.35,.12),('LOWER',(-.10,.10,-.10),.25,.12)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;x=bpy.data.objects.new(name,d);studio.objects.link(x);x.location=loc;x.rotation_euler=(Vector((0,0,.0625))-x.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('BELLOWS_CAMERA',bpy.data.cameras.new('BELLOWS_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.14,.22,.14);cam.rotation_euler=(Vector((0,0,.0625))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.18;cam.data.clip_start=.001;cam.data.clip_end=5;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1000;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG';bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'fork-bellows-v2.blend'),compress=True);r['source_sha256']=hashlib.sha256((HERE/'fork-bellows-v2.blend').read_bytes()).hexdigest();r['export_sha256']=hashlib.sha256((HERE/'fork-bellows-v2-inspection.glb').read_bytes()).hexdigest();(OUT/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_BELLOWS_SOURCE',json.dumps(r))
