"""ONE documented partial centralrib, original finite rounded-top sweep then exact union."""
import bpy,bmesh,numpy as np,math,json,hashlib,tempfile,subprocess,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];P=R/'creative/reviews/headlamp-cowl-shell-study-v14';P.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();A=json.loads((R/'creative/reviews/headlamp-cowl-shell-study-v13/source-geometry-check.json').read_text());src=H/'headlamp-cowl-shell-study-v13.blend';assert sha(src)==A['source_sha256'];plan=R/'creative/research/headlamp-cowl/remaining-partial-ribs-plan-v14.json';pj=json.loads(plan.read_text());assert pj['baseline_source13_sha256']==A['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;C=bpy.data.collections[A['collection']];root=bpy.data.objects[A['root']];base=bpy.data.objects[A['object']];K=bpy.data.collections.new('COWL_EDITABLE_FIRST_RIB_v13_HIDDEN');s.collection.children.link(K);C.objects.unlink(base);K.objects.link(base);mat=base.active_material;features=[];cutters=[]
def make_rib(c):
 pp=np.array(c['proxy_surface_points_m_estimated'],np.float64);NN=np.array(c['proxy_smooth_normals_estimated'],np.float64);NN/=np.linalg.norm(NN,axis=1)[:,None];TT=np.gradient(pp,axis=0);TT-=NN*np.sum(TT*NN,axis=1)[:,None];TT/=np.linalg.norm(TT,axis=1)[:,None];UU=np.cross(TT,NN);UU/=np.linalg.norm(UU,axis=1)[:,None];rr=c['width_m_estimated']/2;depth=c['root_overlap_m_estimated'];n=len(pp);arcs=c['cross_top_semicircle_samples'];cross_count=arcs+3;lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(pp,axis=0),axis=1))];ss=lengths/lengths[-1];profiles=[];heights=[]
 def smooth(x):
  x=max(0.,min(1.,x));return x*x*x*(10-15*x+6*x*x)
 for t in ss:
  env=smooth(t/c['end_taper_fraction_estimated'])*smooth((1-t)/c['end_taper_fraction_estimated']);hh=c['minimum_end_height_m_estimated']+(c['maximum_height_m_estimated']-c['minimum_end_height_m_estimated'])*env;heights.append(hh);profiles.append([(-rr,-depth),(rr,-depth)]+[(rr*math.cos(math.pi*k/arcs),hh-rr+rr*math.sin(math.pi*k/arcs))for k in range(arcs+1)])
 ring=np.array([[p+U*x+N*y for x,y in profile]for p,U,N,profile in zip(pp,UU,NN,profiles)]);vertices=ring.reshape(-1,3).tolist();faces=[(i*cross_count+k,(i+1)*cross_count+k,(i+1)*cross_count+(k+1)%cross_count,i*cross_count+(k+1)%cross_count)for i in range(n-1)for k in range(cross_count)]+[tuple(range(cross_count)),tuple(reversed(range((n-1)*cross_count,n*cross_count)))];mm=bpy.data.meshes.new('Original '+c['id']+' finite roundedtop sweep');mm.from_pydata(vertices,[],faces);mm.update();uv0=mm.uv_layers.new(name='Original rib sweep UV');sc=mm.attributes.new('WEWA_surface_class','INT','FACE');norm=[]
 for p in mm.polygons:
  sc.data[p.index].value=8;p.use_smooth=p.index<(n-1)*cross_count
  for li in p.loop_indices:
   ix=mm.loops[li].vertex_index;r,k=divmod(ix,cross_count)
   if p.index>=(n-1)*cross_count:
    normal=TT[r]*(-1 if r==0 else 1);x,y=profiles[r][k];uv0.data[li].uv=(.5+x/(2*rr),(y+depth)/(heights[r]+depth))
   else:
    segment=p.index%cross_count;tangent=ring[min(n-1,r+1),k]-ring[max(0,r-1),k]
    if segment==0:derivative=UU[r]
    elif segment==1:derivative=NN[r]
    elif segment==cross_count-1:derivative=-NN[r]
    else:
     theta=math.pi*(k-2)/arcs;derivative=-UU[r]*math.sin(theta)+NN[r]*math.cos(theta)
    normal=np.cross(tangent,derivative);normal/=np.linalg.norm(normal);uv0.data[li].uv=((segment+(1 if k==(segment+1)%cross_count else 0))/cross_count,float(ss[r]))
   norm.append(normal)
 mm.normals_split_custom_set(norm);o=bpy.data.objects.new('Original '+c['id']+' partialrib - estimated sweptinput',mm);K.objects.link(o);features.append(o)
for c in pj['ribs']:make_rib(c)
def input_row(o):
 m=o.data;m.calc_loop_triangles();uv=m.uv_layers.active
 input_min_dot=1.;input_min_area=1.
 for tri in m.loop_triangles:
  pa,pb,pc=[np.array(m.vertices[ix].co,dtype=np.float64)for ix in tri.vertices];cr=np.cross(pb-pa,pc-pa);le=np.linalg.norm(cr);input_min_area=min(input_min_area,float(le/2))
  if le>0:input_min_dot=min(input_min_dot,*[float(cr@np.array(m.corner_normals[li].vector)/le)for li in tri.loops])
 input_diag={'name':o.name,'minimum_input_area_m2':input_min_area,'minimum_input_corner_normal_dot':input_min_dot};print('INPUT_DIAG',json.dumps(input_diag),flush=True)
 return {'name':o.name,'vertices':[list(v.co)for v in m.vertices],'triangles':[list(t.vertices)for t in m.loop_triangles],'corner_normals':[[list(m.corner_normals[li].vector)for li in t.loops]for t in m.loop_triangles],'triangle_UV':[[list(uv.data[li].uv)for li in t.loops]for t in m.loop_triangles],'triangle_surface_class':[int(m.attributes['WEWA_surface_class'].data[t.polygon_index].value)if m.attributes.get('WEWA_surface_class')else 4 for t in m.loop_triangles]}
inputs=[input_row(base)]+[input_row(o)for o in features]+[input_row(o)for o in cutters]
with tempfile.TemporaryDirectory(prefix='wewa-cowl-csg-')as td:
 inp=Path(td)/'in.json';out=Path(td)/'out.json';inp.write_text(json.dumps({'base':inputs[0],'features':inputs[1:1+len(features)],'drills':inputs[1+len(features):]}));subprocess.run([shutil.which('python'),str(H/'cowl_csg_worker_pad_v5.py'),str(inp),str(out)],check=True);cs=json.loads(out.read_text())
 if cs.get('rejected'):
  (P/('construction-rejection-'+str(1+len(list(P.glob('construction-rejection-*.json'))))+'.json')).write_text(json.dumps(cs,indent=2)+'\n');raise RuntimeError(cs['reason'])
# Inspect actualFloat32CSGtransport BEFORE Blender and interpolation.
VV=np.asarray(cs['vertices'],dtype=np.float32).astype(np.float64);TT=np.asarray(cs['triangles'],dtype=np.int64);crosses=np.cross(VV[TT[:,1]]-VV[TT[:,0]],VV[TT[:,2]]-VV[TT[:,0]]);lens=np.linalg.norm(crosses,axis=1);zero_ids=np.where(lens==0)[0]
if len(zero_ids):
 rows=[]
 for tid in zero_ids[:30]:
  ids=TT[tid];points=VV[ids];owner=cs['triangle_source_owners'][int(tid)];rows.append({'triangle_index':int(tid),'owner':owner,'source_name':inputs[owner]['name'],'source_face':cs['triangle_source_face_ids'][int(tid)],'indices':ids.tolist(),'points':points.tolist(),'unique_position_count':len(set(map(tuple,points))),'edge_lengths_m':[float(np.linalg.norm(points[(i+1)%3]-points[i]))for i in range(3)]})
 (P/'CSG-Float32-quantization-rejection.json').write_text(json.dumps({'rejected':True,'zero_area_count':int(len(zero_ids)),'examples':rows,'no_source_or_export_written':True,'no_faces_or_normals_masked':True},indent=2)+'\n');cache=Path('/workspace/wewa-assets/work-in-progress/headlamp-cowl-shell-study-v14/CSG-Float32-rejected.json');cache.parent.mkdir(parents=True,exist_ok=True);cache.write_text(json.dumps(cs));raise RuntimeError('Float32 CSGzeroareas: see precisequantizationdiagnostic')
m=bpy.data.meshes.new('Original finite cowl shell with true elliptical rear cuts');m.from_pydata(cs['vertices'],[],cs['triangles']);m.update();uv=m.uv_layers.new(name='Original input-face interpolated angular-section UV');normal_owner=m.attributes.new('WEWA_source_input_index','INT','FACE');original_triangle=m.attributes.new('WEWA_source_triangle_index','INT','FACE');surface_class=m.attributes.new('WEWA_surface_class','INT','FACE');norm=[];max_plane=0.;min_bary=1.;owners={str(i):0 for i in range(len(inputs))}
for p in m.polygons:
 own=cs['triangle_source_owners'][p.index];fid=cs['triangle_source_face_ids'][p.index];ref=inputs[own];normal_owner.data[p.index].value=own;original_triangle.data[p.index].value=fid;surface_class.data[p.index].value=ref['triangle_surface_class'][fid];ids=ref['triangles'][fid];a,b,c=[np.array(ref['vertices'][i],dtype=np.float64)for i in ids];ns=np.array(ref['corner_normals'][fid],dtype=np.float64);us=np.array(ref['triangle_UV'][fid],dtype=np.float64);v0=b-a;v1=c-a;d00=v0@v0;d01=v0@v1;d11=v1@v1;denom=d00*d11-d01*d01;assert denom>0;face=np.cross(v0,v1);face/=np.linalg.norm(face);p.use_smooth=True;owners[str(own)]+=1
 for li in p.loop_indices:
  pos=np.array(m.vertices[m.loops[li].vertex_index].co,dtype=np.float64);v2=pos-a;d20=v2@v0;d21=v2@v1;beta=(d11*d20-d01*d21)/denom;gamma=(d00*d21-d01*d20)/denom;w=np.array([1-beta-gamma,beta,gamma]);min_bary=min(min_bary,float(w.min()));max_plane=max(max_plane,abs(float(v2@face)));no=w@ns;no/=np.linalg.norm(no);norm.append(no if own<=len(features) else-no);uv.data[li].uv=w@us
m.normals_split_custom_set(norm);m.materials.append(mat);obj=bpy.data.objects.new('Cowl finite shell seven partialribs candidates - study',m);C.objects.link(obj);obj.parent=root;obj['structural_closed_volume']=True;obj['estimated_geometry']=True;K.hide_render=True;K.hide_viewport=True
bm=bmesh.new();bm.from_mesh(m);nm=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();m.calc_loop_triangles();areas=[];min_dot=1.
for t in m.loop_triangles:
 a,b,c=[np.array(m.vertices[i].co,dtype=np.float64)for i in t.vertices];cross=np.cross(b-a,c-a);length=np.linalg.norm(cross);areas.append(float(length/2));assert length>0;fn=cross/length
 for li in t.loops:min_dot=min(min_dot,float(fn@np.array(m.corner_normals[li].vector,dtype=np.float64)))

if not(nm==0 and volume>0 and min(areas)>0 and min_dot>.9):
 bad=[]
 for tri in m.loop_triangles:
  pa,pb,pc=[np.array(m.vertices[ix].co,dtype=np.float64)for ix in tri.vertices];cr=np.cross(pb-pa,pc-pa);le=np.linalg.norm(cr);dot=min(float(cr@np.array(m.corner_normals[li].vector)/le)for li in tri.loops)if le>0 else -1
  if dot<.9:bad.append({'triangle_index':tri.index,'source_owner':cs['triangle_source_owners'][tri.polygon_index],'source_name':inputs[cs['triangle_source_owners'][tri.polygon_index]]['name'],'source_face':cs['triangle_source_face_ids'][tri.polygon_index],'area_m2':float(le/2),'min_dot':dot,'points':[list(m.vertices[ix].co)for ix in tri.vertices],'corner_normals':[list(m.corner_normals[li].vector)for li in tri.loops]})
 (P/('normal-geometry-rejection-'+str(1+len(list(P.glob('normal-geometry-rejection-*.json'))))+'.json')).write_text(json.dumps({'rejected':True,'min_dot':min_dot,'min_area_m2':min(areas),'bad_count':len(bad),'bad':sorted(bad,key=lambda x:x['min_dot'])[:30],'no_export_written':True,'no_normals_or_tangents_arbitrarily_repaired':True},indent=2)+'\n')
 raise RuntimeError('Source14 geometry/normals rejected; see normal-geometry-rejection-1.json')
assert max_plane<1e-7 and min_bary>-.001,(max_plane,min_bary)
bpy.context.view_layer.update();source=H/'headlamp-cowl-shell-study-v14.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=obj;export=H/'headlamp-cowl-shell-study-v14.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_yup=True,export_extras=True)
report={'schema':1,'revision':'headlamp-cowl-shell-study-v14','source_sha256':sha(source),'export_sha256':sha(export),'baseline_source_sha256':A['source_sha256'],'baseline_export_sha256':A['export_sha256'],'shape_plan_sha256':sha(plan),'CSG_worker_sha256':sha(H/'cowl_csg_worker_pad_v5.py'),'float32_transport_normalization':cs.get('float32_transport_normalization'),'float32_diagonal_transport':cs.get('float32_diagonal_transport'),'collection':C.name,'root':root.name,'object':obj.name,'actual_triangles':len(areas),'min_triangle_area_m2':min(areas),'minimum_triangle_corner_normal_dot':min_dot,'non_manifold_edges':nm,'connected_components':cs['connected_components'],'positive_signed_volume_m3':volume,'CSG_stages':cs['stages'],'exact_original_triangle_owner_counts':owners,'max_actual_point_to_original_triangle_plane_distance_m':max_plane,'minimum_original_face_barycentric_coordinate':min_bary,'normal_UV_provenance':'Exact inputvolume and triangle IDs, barycentric interpolation inFloat64. Reverse subtractivecutter normals only. No nearest-surface ownership or globalpost-CSGbevel.','persistent_authoring_face_attributes':['WEWA_source_input_index','WEWA_source_triangle_index','WEWA_surface_class'],'surface_class_codes':{'1':'Original exterior','2':'Original interior','3':'Finite roundedwall edges','4':'Truecut walls','5':'Originalsupport candidates','6':'P6returnexterior','7':'P6returninterior','8':'Observedpartialribscandidates'},'surface_class_face_counts':{str(k):sum(v.value==k for v in surface_class.data)for k in[1,2,3,4,5,6,7,8]},'original_input_volume_names':[row['name'] for row in inputs],'features_count':len(features),'all_dimensions_estimated':True,'state':'Partial shell with true negative spaces; sixestimatedsupports/twoupperwall openings/sevenobservedpartialrib candidates built; unidentifiedhiddenreturns/hardware/mouldedcreases/paint NOT built. Boundedshape stop, not fullRDCshape reception. Identity/mount/depth conditional.','art_accepted':False};(P/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(src)==A['source_sha256'];print('COWL_TRUE_CUT_STUDY',json.dumps(report))
