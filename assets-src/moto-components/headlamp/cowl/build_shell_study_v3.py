"""True rear boundary cuts on immutable shell1, not section deformation.
Original exact CSG input-face provenance for normals/UVs, separate incomplete study.
"""
import bpy,bmesh,numpy as np,math,json,hashlib,tempfile,subprocess,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];P=R/'creative/reviews/headlamp-cowl-shell-study-v3';P.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();A=json.loads((R/'creative/reviews/headlamp-cowl-shell-study-v1/source-geometry-check.json').read_text());src=H/'headlamp-cowl-shell-study-v1.blend';assert sha(src)==A['source_sha256'];plan=R/'creative/research/headlamp-cowl/rear-negative-spaces-plan-v3.json';cfg=json.loads(plan.read_text())['rear_scallops']['new_construction'];bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;C=bpy.data.collections[A['collection']];root=bpy.data.objects[A['root']];base=bpy.data.objects[A['object']];K=bpy.data.collections.new('COWL_EDITABLE_CUTTING_INPUTS_v3_HIDDEN');s.collection.children.link(K);C.objects.unlink(base);K.objects.link(base);mat=base.active_material

def ellipse(name,cx):
 n=192;rx=cfg['ellipse_radius_X_m_estimated'];ry=cfg['ellipse_radius_Y_m_estimated'];cy=cfg['ellipse_centre_Y_m_estimated'];z0,z1=cfg['extrusion_Z_m_estimated'];v=[(cx+rx*math.cos(math.tau*j/n),cy+ry*math.sin(math.tau*j/n),z)for z in [z0,z1]for j in range(n)];f=[(j,(j+1)%n,(j+1)%n+n,j+n)for j in range(n)]+[tuple(reversed(range(n))),tuple(range(n,n*2))];m=bpy.data.meshes.new(name+' original elliptical cylinder');m.from_pydata(v,[],f);m.update();norm=[];uv=m.uv_layers.new(name='Original cutter wall UV')
 for p in m.polygons:
  p.use_smooth=p.index<n
  for k,li in enumerate(p.loop_indices):
   i=m.loops[li].vertex_index;theta=math.tau*(i%n)/n
   if p.index<n:
    no=np.array([math.cos(theta)/rx,math.sin(theta)/ry,0.]);no/=np.linalg.norm(no);u=p.index/n if k in[0,3]else(p.index+1)/n;uv.data[li].uv=(u,1 if i>=n else 0)
   else:no=np.array([0,0,-1 if p.index==n else 1]);uv.data[li].uv=(.5+.5*math.cos(theta),.5+.5*math.sin(theta))
   norm.append(no)
 m.normals_split_custom_set(norm);o=bpy.data.objects.new(name,m);K.objects.link(o);return o
cutters=[ellipse('Original rear scallop '+str(i+1)+' cutter - estimated',x)for i,x in enumerate(cfg['centre_X_m_estimated'])]

def input_row(o):
 m=o.data;m.calc_loop_triangles();uv=m.uv_layers.active
 return {'name':o.name,'vertices':[list(v.co)for v in m.vertices],'triangles':[list(t.vertices)for t in m.loop_triangles],'corner_normals':[[list(m.corner_normals[li].vector)for li in t.loops]for t in m.loop_triangles],'triangle_UV':[[list(uv.data[li].uv)for li in t.loops]for t in m.loop_triangles]}
inputs=[input_row(base)]+[input_row(o)for o in cutters]
with tempfile.TemporaryDirectory(prefix='wewa-cowl-csg-')as td:
 inp=Path(td)/'in.json';out=Path(td)/'out.json';inp.write_text(json.dumps({'base':inputs[0],'features':[],'drills':inputs[1:]}));subprocess.run([shutil.which('python'),str(H/'cowl_csg_worker_v1.py'),str(inp),str(out)],check=True);cs=json.loads(out.read_text())
m=bpy.data.meshes.new('Original finite cowl shell with true elliptical rear cuts');m.from_pydata(cs['vertices'],[],cs['triangles']);m.update();uv=m.uv_layers.new(name='Original input-face interpolated angular-section UV');norm=[];max_plane=0.;min_bary=1.;owners={str(i):0 for i in range(len(inputs))}
for p in m.polygons:
 own=cs['triangle_source_owners'][p.index];fid=cs['triangle_source_face_ids'][p.index];ref=inputs[own];ids=ref['triangles'][fid];a,b,c=[np.array(ref['vertices'][i],dtype=np.float64)for i in ids];ns=np.array(ref['corner_normals'][fid],dtype=np.float64);us=np.array(ref['triangle_UV'][fid],dtype=np.float64);v0=b-a;v1=c-a;d00=v0@v0;d01=v0@v1;d11=v1@v1;denom=d00*d11-d01*d01;assert denom>0;face=np.cross(v0,v1);face/=np.linalg.norm(face);p.use_smooth=True;owners[str(own)]+=1
 for li in p.loop_indices:
  pos=np.array(m.vertices[m.loops[li].vertex_index].co,dtype=np.float64);v2=pos-a;d20=v2@v0;d21=v2@v1;beta=(d11*d20-d01*d21)/denom;gamma=(d00*d21-d01*d20)/denom;w=np.array([1-beta-gamma,beta,gamma]);min_bary=min(min_bary,float(w.min()));max_plane=max(max_plane,abs(float(v2@face)));no=w@ns;no/=np.linalg.norm(no);norm.append(no if own==0 else-no);uv.data[li].uv=w@us
m.normals_split_custom_set(norm);m.materials.append(mat);obj=bpy.data.objects.new('Cowl finite shell with two true rear scallops - partial study',m);C.objects.link(obj);obj.parent=root;obj['structural_closed_volume']=True;obj['estimated_geometry']=True;K.hide_render=True;K.hide_viewport=True
bm=bmesh.new();bm.from_mesh(m);nm=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();m.calc_loop_triangles();areas=[];min_dot=1.
for t in m.loop_triangles:
 a,b,c=[np.array(m.vertices[i].co,dtype=np.float64)for i in t.vertices];cross=np.cross(b-a,c-a);length=np.linalg.norm(cross);areas.append(float(length/2));assert length>0;fn=cross/length
 for li in t.loops:min_dot=min(min_dot,float(fn@np.array(m.corner_normals[li].vector,dtype=np.float64)))
assert nm==0 and volume>0 and min(areas)>0 and min_dot>.9,(nm,volume,min(areas),min_dot);assert max_plane<1e-7 and min_bary>-.001,(max_plane,min_bary)
bpy.context.view_layer.update();source=H/'headlamp-cowl-shell-study-v3.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=obj;export=H/'headlamp-cowl-shell-study-v3.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_yup=True,export_extras=True)
report={'schema':1,'revision':'headlamp-cowl-shell-study-v3','source_sha256':sha(source),'export_sha256':sha(export),'baseline_source_sha256':A['source_sha256'],'baseline_export_sha256':A['export_sha256'],'shape_plan_sha256':sha(plan),'CSG_worker_sha256':sha(H/'cowl_csg_worker_v1.py'),'collection':C.name,'root':root.name,'object':obj.name,'actual_triangles':len(areas),'min_triangle_area_m2':min(areas),'minimum_triangle_corner_normal_dot':min_dot,'non_manifold_edges':nm,'connected_components':cs['connected_components'],'positive_signed_volume_m3':volume,'CSG_stages':cs['stages'],'exact_original_triangle_owner_counts':owners,'max_actual_point_to_original_triangle_plane_distance_m':max_plane,'minimum_original_face_barycentric_coordinate':min_bary,'normal_UV_provenance':'Exact inputvolume and triangle IDs, barycentric interpolation inFloat64. Reverse subtractivecutter normals only. No nearest-surface ownership or globalpost-CSGbevel.','all_dimensions_estimated':True,'state':'Partial shell with true negative spaces; central keyhole/pads/ribs/hardware/mouldedcreases/paint NOT built yet. Identity/mount/depth conditional.','art_accepted':False};(P/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(src)==A['source_sha256'];print('COWL_TRUE_CUT_STUDY',json.dumps(report))
