"""Photo-informed split ring, single closed helical strip volume; immutable snapshot guides."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,sys
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/ignition-key-ring-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not(H/'preflight-manifest.json').exists()
for k in['ignition','instruments']:assert sha(R/P[k+'_source'])==P[k+'_source_sha256']
assert sha(R/P['instruments_report'])==P['instruments_report_sha256'];sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import mesh_object,material,check_mesh,tree_world,studio,export
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;tmp=bpy.data.collections.new('READ_ONLY_SOURCE_SNAPSHOTS');s.collection.children.link(tmp)
keynames=['Ignition rotor and key state pivot','Ignition provisional datum under instruments','Ignition ribbed hollow housing and mounting ears - candidate','Ignition front rotor - presentation states','Key metal blade - generic nonfunctional cut','Key black moulded head - estimated']
# Root spelling is looked up from source, but the geometry/rotor names are explicit.
with bpy.data.libraries.load(str(R/P['ignition_source']),link=False)as(a,l):
 rootnames=[n for n in a.objects if'datum' in n.lower()];names=[n for n in keynames if n in a.objects];l.objects=list(set(names+rootnames))
for o in l.objects:tmp.objects.link(o)
s.frame_set(1);bpy.context.view_layer.update();moving=bpy.data.objects['Ignition rotor and key state pivot'];M=moving.matrix_world.copy();snapshots=[]
def capture(o,group):
 deps=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();r={'name':o.name,'group':group,'positions':[list(o.matrix_world@v.co)for v in m.vertices],'triangles':[list(t.vertices)for t in m.loop_triangles]};ev.to_mesh_clear();return r
for n in keynames[2:]:snapshots.append(capture(bpy.data.objects[n],'keymoving'if n in keynames[3:]else'casefixed'))
I=json.loads((R/P['instruments_report']).read_text());instrumentnames=[r['object']for r in I['structural_bodies']]
with bpy.data.libraries.load(str(R/P['instruments_source']),link=False)as(a,l):l.objects=instrumentnames+['INSTRUMENT_CLUSTER_MOUNT']
for o in l.objects:tmp.objects.link(o)
bpy.context.view_layer.update()
for o in l.objects:
 if o.type=='MESH':snapshots.append(capture(o,'instrumentsfixed'))
# Persist only own numeric geometry snapshots, never imported materials/images/library links.
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
C=bpy.data.collections.new('WEWA_IGNITION_KEY_RING');s.collection.children.link(C);G=bpy.data.collections.new('KEYRING_IMMUTABLE_WORLD_GEOMETRY_SNAPSHOTS_NOT_EXPORTED');s.collection.children.link(G);stage=bpy.data.collections.new('KEYRING_STUDIO_NOT_EXPORTED');s.collection.children.link(stage);root=bpy.data.objects.new('Key ring inherited OFF key pivot datum - conditional',None);C.objects.link(root);root.matrix_world=M
mat=material('Key ring geometry gray - finish not received',(.19,.19,.19),0,.45);guide=material('Own source geometry snapshot gray - no images',(.08,.09,.10),0,.55);guides=[]
for row in snapshots:
 o=mesh_object('GUIDE '+row['name'],row['positions'],row['triangles'],G,guide);o['snapshot_group']=row['group'];o['source_object']=row['name'];guides.append(o)
rad=P['working_mean_loop_radius_m'];turns=P['working_turns'];pitch=P['working_pitch_per_turn_m'];angle0=P['working_start_angle_rad'];span=turns*math.tau;N=math.ceil(turns*P['samples_per_turn']);halfU=P['working_radial_strip_width_m']/2;halfV=P['working_axial_strip_thickness_m']/2;corner=P['working_corner_radius_m'];section=[]
for cu,cv,base in[(halfU-corner,halfV-corner,0),(-halfU+corner,halfV-corner,math.pi/2),(-halfU+corner,-halfV+corner,math.pi),(halfU-corner,-halfV+corner,3*math.pi/2)]:
 for j in range(P['corner_samples']):
  a=base+math.pi/2*j/P['corner_samples'];section.append((cu+corner*math.cos(a),cv+corner*math.sin(a)))
K=len(section);vertices=[];centres=[]
for i in range(N+1):
 theta=angle0+span*i/N;centre=Vector(((i/N-.5)*pitch*turns,rad*math.cos(theta),P['working_centre_in_key_pivot_m'][2]+rad*math.sin(theta)));centres.append(centre);radial=Vector((0,math.cos(theta),math.sin(theta)));tangent=Vector((pitch/math.tau,-rad*math.sin(theta),rad*math.cos(theta))).normalized();axial=tangent.cross(radial).normalized()
 for u,v in section:vertices.append(tuple(centre+u*radial+v*axial))
faces=[]
for i in range(N):
 for j in range(K):a=i*K+j;b=i*K+(j+1)%K;c=(i+1)*K+(j+1)%K;d=(i+1)*K+j;faces.extend([(a,b,c),(a,c,d)])
flat=[]
for i,reverse in[(0,True),(N,False)]:
 centre=len(vertices);vertices.append(tuple(centres[i]))
 for j in range(K):
  f=(centre,i*K+j,i*K+(j+1)%K);faces.append(tuple(reversed(f))if reverse else f);flat.append(len(faces)-1)
o=mesh_object('Photo-informed split key ring - one continuous helical strip',vertices,faces,C,mat);o.parent=root
for i in flat:o.data.polygons[i].use_smooth=False
bm=bmesh.new();bm.from_mesh(o.data)
for e in bm.edges:
 if len(e.link_faces)==2 and e.calc_face_angle(0)>.5:e.smooth=False
bm.to_mesh(o.data);bm.free();o.data.update();m=o.data;m.calc_loop_triangles();assert all(t.area>0 for t in m.loop_triangles)
uv=m.uv_layers.new(name='Authored helical strip atlas - no photo')
for f in m.polygons:
 for li in f.loop_indices:
  idx=m.loops[li].vertex_index
  if f.index<2*N*K:uv.data[li].uv=((idx%K)/K,(idx//K)/N)
  else:
   v=m.vertices[idx].co;uv.data[li].uv=(v.y/(2*rad)+.5,(v.z-P['working_centre_in_key_pivot_m'][2])/(2*rad)+.5)
geom=check_mesh(o);area=P['working_radial_strip_width_m']*P['working_axial_strip_thickness_m']-(4-math.pi)*corner**2;expected=area*math.sqrt((rad*span)**2+(pitch*turns)**2);assert abs(geom['signed_volume_m3']/expected-1)<.005
# Conditional rigid presentation states; no hidden flexibility or spring mechanism claimed.
poses=[];Mi=M.inverted()
for deg in P['inspection_rotor_angles_degrees']:
 local=Matrix.Rotation(math.radians(deg),4,'Z');delta=M@local@Mi;root.matrix_world=M@local
 for g in guides:g.matrix_world=delta if g['snapshot_group']=='keymoving'else Matrix.Identity(4)
 bpy.context.view_layer.update();tree=tree_world(o);rows=[{'guide':g['source_object'],'group':g['snapshot_group'],'crossing_pairs':len(tree.overlap(tree_world(g)))}for g in guides];poses.append({'rotor_angle_degrees_estimated':deg,'surface_tests':rows});assert not any(r['crossing_pairs']for r in rows),poses[-1]
root.matrix_world=M
for g in guides:g.matrix_world=Matrix.Identity(4)
bpy.context.view_layer.update();G.hide_render=True;G.hide_viewport=True;target=M@Vector(P['working_centre_in_key_pivot_m']);studio(s,stage,target)
for q in stage.objects:
 if q.type=='MESH':q.hide_render=True
 if q.type=='LIGHT':q.data.energy*=.04
s.camera.data.clip_start=.0001;source=H/'ignition-key-ring-v1-geometry.blend';glb=H/'ignition-key-ring-v1-geometry.glb';export(glb,[root,o]);bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
for k in['ignition','instruments']:assert sha(R/P[k+'_source'])==P[k+'_source_sha256']
r={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':sha(glb),'collection':C.name,'root':root.name,'geometry':[geom],'triangles':len(m.loop_triangles),'authored_centreline_samples':N+1,'authored_section_samples':K,'closed_wire_volume_expected_m3':expected,'volume_relative_discretization_difference':geom['signed_volume_m3']/expected-1,'rest_keypivot_world_matrix':[list(row)for row in M],'guide_snapshots':[{'name':g['name'],'group':g['group'],'vertices':len(g['positions']),'triangles':len(g['triangles']),'world_geometry_sha256':hashlib.sha256(json.dumps({'positions':g['positions'],'triangles':g['triangles']},separators=(',',':')).encode()).hexdigest()}for g in snapshots],'conditional_rigid_rotor_pose_checks':poses,'source_libraries':len(bpy.data.libraries),'source_file_images':len([i for i in bpy.data.images if i.source=='FILE'and i.filepath]),'actual_elastic_compliance_certified':False,'all_dimensions_estimated':True,'art_accepted':False};assert r['source_libraries']==r['source_file_images']==0;(H/'geometry-report.json').write_text(json.dumps(r,indent=2)+'\n');(O/'geometry-source-check.json').write_text(json.dumps(r,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');print('KEY_RING_GEOMETRY',json.dumps(r),flush=True)
