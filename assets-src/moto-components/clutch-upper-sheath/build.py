"""Bounded short outer sheath departure, open lumen, distal REVIEW CUT, no hidden route."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,sys
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/clutch-upper-sheath-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not(H/'preflight-manifest.json').exists()
for k in['clutch','instruments']:
 assert sha(R/P[k+'_source'])==P[k+'_source_sha256'];assert sha(R/P[k+'_report'])==P[k+'_report_sha256']
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,mesh_object,check_mesh,tree_world,studio,export
CR=json.loads((R/P['clutch_report']).read_text())['preflight'];IR=json.loads((R/P['instruments_report']).read_text());snapshots=[];bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;tmp=bpy.data.collections.new('READONLY_SNAPSHOT_INPUTS');s.collection.children.link(tmp)
def capture(o,group):
 deps=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();row={'name':o.name,'group':group,'positions':[list(o.matrix_world@v.co)for v in m.vertices],'triangles':[list(t.vertices)for t in m.loop_triangles]};ev.to_mesh_clear();return row
with bpy.data.libraries.load(str(R/P['clutch_source']),link=False)as(a,l):l.objects=[r['name']for r in CR['geometry']]
for o in l.objects:tmp.objects.link(o)
s.frame_set(1);bpy.context.view_layer.update()
for o in l.objects:snapshots.append(capture(o,'levermoving'if o.name=='Clutch lever - moving candidate'else'clutchfixed'))
with bpy.data.libraries.load(str(R/P['instruments_source']),link=False)as(a,l):l.objects=[r['object']for r in IR['structural_bodies']]+['INSTRUMENT_CLUSTER_MOUNT']
for o in l.objects:tmp.objects.link(o)
bpy.context.view_layer.update()
for o in l.objects:
 if o.type=='MESH':snapshots.append(capture(o,'instrumentsfixed'))
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;C=bpy.data.collections.new('WEWA_CLUTCH_UPPER_SHEATH');s.collection.children.link(C);G=bpy.data.collections.new('CLUTCH_UPPER_IMMUTABLE_WORLD_SNAPSHOTS_NOT_EXPORTED');s.collection.children.link(G);stage=bpy.data.collections.new('CLUTCH_UPPER_STUDIO_NOT_EXPORTED');s.collection.children.link(stage);root=bpy.data.objects.new('Upper clutch sheath common cockpit datum - partial route',None);C.objects.link(root);mat=material('Upper sheath geometry gray - finish not received',(.19,.19,.19),0,.45);guide=material('Own geometry guides gray - no textures',(.08,.09,.10),0,.55);guides=[]
for row in snapshots:
 g=mesh_object('GUIDE '+row['name'],row['positions'],row['triangles'],G,guide);g['source_object']=row['name'];g['snapshot_group']=row['group'];guides.append(g)
Q=[Vector(p)for p in P['bezier_control_points_world_m']];N=P['length_samples'];K=P['radial_samples'];Ro=P['working_outer_radius_m'];Ri=P['working_lumen_radius_m'];centres=[];normals=[];binormals=[];tangents=[];curvatures=[]
for i in range(N+1):
 t=i/N;u=1-t;c=u**3*Q[0]+3*u*u*t*Q[1]+3*u*t*t*Q[2]+t**3*Q[3];d=3*(u*u*(Q[1]-Q[0])+2*u*t*(Q[2]-Q[1])+t*t*(Q[3]-Q[2]));dd=6*(u*(Q[2]-2*Q[1]+Q[0])+t*(Q[3]-2*Q[2]+Q[1]));T=d.normalized();up=Vector((0,0,1));normal=(up-T*up.dot(T)).normalized();binormal=T.cross(normal).normalized();centres.append(c);tangents.append(T);normals.append(normal);binormals.append(binormal);curvatures.append(d.cross(dd).length/d.length**3)
assert max(curvatures)*Ro<.25,'Sweep too tight for constantannulus';vertices=[]
for radius in[Ro,Ri]:
 for i in range(N+1):
  for j in range(K):a=math.tau*j/K;vertices.append(tuple(centres[i]+radius*(normals[i]*math.cos(a)+binormals[i]*math.sin(a))))
offset=(N+1)*K;faces=[]
for layer in range(2):
 for i in range(N):
  for j in range(K):
   a=layer*offset+i*K+j;b=layer*offset+i*K+(j+1)%K;c=layer*offset+(i+1)*K+(j+1)%K;d=layer*offset+(i+1)*K+j;tris=[(a,b,c),(a,c,d)];faces.extend([tuple(reversed(f))for f in tris]if layer else tris)
flat=[]
for i,flip in[(0,False),(N,True)]:
 for j in range(K):
  a=i*K+j;b=i*K+(j+1)%K;ia=offset+a;ib=offset+b;tris=[(a,ia,ib),(a,ib,b)];faces.extend([tuple(reversed(f))for f in tris]if flip else tris);flat.extend([len(faces)-2,len(faces)-1])
o=mesh_object('Visible short upper clutch outer sheath - distal review cut',vertices,faces,C,mat);o.parent=root
for i in flat:o.data.polygons[i].use_smooth=False
bm=bmesh.new();bm.from_mesh(o.data)
for e in bm.edges:
 if len(e.link_faces)==2 and e.calc_face_angle(0)>.5:e.smooth=False
bm.to_mesh(o.data);bm.free();o.data.update();m=o.data;m.calc_loop_triangles();assert all(t.area>0 for t in m.loop_triangles);uv=m.uv_layers.new(name='Authored sheath cylinder atlas - no photo')
for f in m.polygons:
 vals=[((idx%offset)%K)/K for idx in f.vertices]
 if max(vals)-min(vals)>.5:vals=[v+1 if v<.5 else v for v in vals]
 for li,u in zip(f.loop_indices,vals):
  idx=m.loops[li].vertex_index;ri=(idx%offset)//K
  if f.index>=4*N*K:
   v=m.vertices[idx].co-centres[ri];uv.data[li].uv=(v.dot(normals[ri])/(2*Ro)+.5,v.dot(binormals[ri])/(2*Ro)+.5)
  else:uv.data[li].uv=(u,ri/N)
geom=check_mesh(o);length=sum((b-a).length for a,b in zip(centres,centres[1:]));expected=math.pi*(Ro*Ro-Ri*Ri)*length;assert abs(geom['signed_volume_m3']/expected-1)<.005
pivot=Vector(CR['pivot_world_m']);poses=[]
for deg in P['inspection_clutch_pull_degrees']:
 delta=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(deg),4,'Z')@Matrix.Translation(-pivot)
 for g in guides:g.matrix_world=delta if g['snapshot_group']=='levermoving'else Matrix.Identity(4)
 bpy.context.view_layer.update();tree=tree_world(o);rows=[{'guide':g['source_object'],'crossing_pairs':len(tree.overlap(tree_world(g)))}for g in guides];poses.append({'clutch_pull_degrees_estimated':deg,'surface_tests':rows});assert not any(r['crossing_pairs']for r in rows),poses[-1]
for g in guides:g.matrix_world=Matrix.Identity(4)
bpy.context.view_layer.update();tree=tree_world(o);mouths=[]
for i,sign in[(0,1),(N,-1)]:
 hit=tree.ray_cast(centres[i]+tangents[i]*sign*1e-6,tangents[i]*sign,.0015);mouths.append({'end':'control_review_gap'if i==0 else'distal_REVIEW_CUT_not_terminal','finite_centre_ray_clear':hit[0]is None,'direction_into_lumen':[float(v)for v in tangents[i]*sign]});assert hit[0]is None
thickness=[(m.vertices[i*K].co-m.vertices[offset+i*K].co).length for i in range(N+1)];assert max(abs(t-(Ro-Ri))for t in thickness)<5e-8;G.hide_render=True;G.hide_viewport=True;target=(centres[0]+centres[-1])/2;studio(s,stage,target)
for q in stage.objects:
 if q.type=='MESH':q.hide_render=True
 if q.type=='LIGHT':q.data.energy*=.04
s.camera.data.clip_start=.0001;source=H/'clutch-upper-sheath-v1-geometry.blend';glb=H/'clutch-upper-sheath-v1-geometry.glb';export(glb,[root,o]);bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
for k in['clutch','instruments']:assert sha(R/P[k+'_source'])==P[k+'_source_sha256']
r={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':sha(glb),'collection':C.name,'root':root.name,'geometry':[geom],'triangles':len(m.loop_triangles),'centreline_arc_length_authored_m':length,'minimum_authored_curve_radius_m':1/max(curvatures),'volume_relative_discretization_difference':geom['signed_volume_m3']/expected-1,'actual_wall_thickness_samples_minmax_m':[min(thickness),max(thickness)],'mouth_finite_lumen_rays':mouths,'centreline_first_world_m':list(centres[0]),'centreline_last_REVIEW_CUT_world_m':list(centres[-1]),'first_tangent_world':list(tangents[0]),'last_tangent_world':list(tangents[-1]),'conditional_clutch_pull_surface_checks':poses,'guide_snapshots':[{'name':q['name'],'group':q['group'],'vertices':len(q['positions']),'triangles':len(q['triangles']),'world_geometry_sha256':hashlib.sha256(json.dumps({'positions':q['positions'],'triangles':q['triangles']},separators=(',',':')).encode()).hexdigest()}for q in snapshots],'source_libraries':len(bpy.data.libraries),'source_file_images':len([i for i in bpy.data.images if i.source=='FILE'and i.filepath]),'complete_Bowden_cable_created':False,'hidden_route_created':False,'ferrule_boot_or_installed_fit_received':False,'all_dimensions_estimated':True,'art_accepted':False};assert r['source_libraries']==r['source_file_images']==0;(H/'geometry-report.json').write_text(json.dumps(r,indent=2)+'\n');(O/'geometry-source-check.json').write_text(json.dumps(r,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');print('CLUTCH_UPPER_SHEATH_GEOMETRY',json.dumps({k:v for k,v in r.items()if k not in['guide_snapshots','conditional_clutch_pull_surface_checks']}),flush=True)
