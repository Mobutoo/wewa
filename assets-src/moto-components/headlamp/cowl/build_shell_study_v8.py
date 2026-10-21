"""True rear boundary cuts on immutable shell1, not section deformation.
Original exact CSG input-face provenance for normals/UVs, separate incomplete study.
"""
import bpy,bmesh,numpy as np,math,json,hashlib,tempfile,subprocess,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];P=R/'creative/reviews/headlamp-cowl-shell-study-v8';P.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();A=json.loads((R/'creative/reviews/headlamp-cowl-raw-study-v5/source-geometry-check.json').read_text());src=H/'headlamp-cowl-raw-study-v5.blend';assert sha(src)==A['source_sha256'];plan=R/'creative/research/headlamp-cowl/first-upper-pad-plan-v8.json';pc=json.loads(plan.read_text())['existing_scallop_cutters'];cfg={'centre_X_m_estimated':pc['centre_X_m'],'ellipse_radius_X_m_estimated':pc['radii_X_Y_m'][0],'ellipse_radius_Y_m_estimated':pc['radii_X_Y_m'][1],'ellipse_centre_Y_m_estimated':pc['centre_Y_m'],'extrusion_Z_m_estimated':pc['Z_cut_bounds_m']};bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;C=bpy.data.collections[A['collection']];root=bpy.data.objects[A['root']];base=bpy.data.objects[A['object']];K=bpy.data.collections.new('COWL_EDITABLE_CUTTING_INPUTS_v8_HIDDEN');s.collection.children.link(K);C.objects.unlink(base);K.objects.link(base);mat=base.active_material

def ellipse(name,cx,rx=None,ry=None,cy=None,zbounds=None):
 n=192;rx=cfg['ellipse_radius_X_m_estimated'] if rx is None else rx;ry=cfg['ellipse_radius_Y_m_estimated'] if ry is None else ry;cy=cfg['ellipse_centre_Y_m_estimated'] if cy is None else cy;z0,z1=cfg['extrusion_Z_m_estimated'] if zbounds is None else zbounds;v=[(cx+rx*math.cos(math.tau*j/n),cy+ry*math.sin(math.tau*j/n),z)for z in [z0,z1]for j in range(n)];f=[(j,(j+1)%n,(j+1)%n+n,j+n)for j in range(n)]+[tuple(reversed(range(n))),tuple(range(n,n*2))];m=bpy.data.meshes.new(name+' original elliptical cylinder');m.from_pydata(v,[],f);m.update();norm=[];uv=m.uv_layers.new(name='Original cutter wall UV')
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


kp=json.loads(plan.read_text())['central_keyhole'];cutters.append(ellipse('Original central keyhole circular cut - estimated',kp['circle_centre_X_Y_m'][0],rx=kp['radius_m'],ry=kp['radius_m'],cy=kp['circle_centre_X_Y_m'][1]))
x0,x1=-kp['throat_width_m']/2,kp['throat_width_m']/2;y0,y1=kp['throat_Y_extent_m'];z0,z1=kp['cut_Z_m'];verts=[(x,y,z)for z in[z0,z1]for y in[y0,y1]for x in[x0,x1]];faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)];mm=bpy.data.meshes.new('Original central narrow straightthroat cutter');mm.from_pydata(verts,[],faces);mm.update();uu=mm.uv_layers.new(name='Original flat throat UV');nn=[]
for pp in mm.polygons:
 pp.use_smooth=False
 for k,li in enumerate(pp.loop_indices):uu.data[li].uv=[(0,0),(1,0),(1,1),(0,1)][k];nn.append(pp.normal.copy())
mm.normals_split_custom_set(nn);oo=bpy.data.objects.new('Original openedge keyhole narrow throat cut - estimated',mm);K.objects.link(oo);cutters.append(oo)


# One original tapered trapezoidal pad; non-concurrent detail candidate only.
pp=json.loads(plan.read_text())['first_pad'];poly=np.array(pp['footprint_XY_m'],dtype=np.float64);foot=[];ch=pp['corner_chamfer_m']
for i,p in enumerate(poly):
 a=poly[(i-1)%len(poly)]-p;b=poly[(i+1)%len(poly)]-p;foot.extend([p+a/np.linalg.norm(a)*ch,p+b/np.linalg.norm(b)*ch])
z0,z1=pp['Z_bottom_top_m'];vv=[(float(p[0]),float(p[1]),z)for z in[z0,z1]for p in foot];nnn=len(foot);ff=[tuple(reversed(range(nnn))),tuple(range(nnn,2*nnn))]+[(i,(i+1)%nnn,(i+1)%nnn+nnn,i+nnn)for i in range(nnn)];pm=bpy.data.meshes.new('Original oneupperpad tapered shelf candidate');pm.from_pydata(vv,[],ff);pm.update();pu=pm.uv_layers.new(name='Original onepad planarandwall UV');pn=[];attr=pm.attributes.new('WEWA_surface_class','INT','FACE')
for f in pm.polygons:
 f.use_smooth=False;attr.data[f.index].value=5
 for k,li in enumerate(f.loop_indices):
  p=pm.vertices[pm.loops[li].vertex_index].co;pu.data[li].uv=((p.x-.10)/.05,(p.y-.06)/.05)if f.index<2 else([(0,0),(1,0),(1,1),(0,1)][k]);pn.append(f.normal.copy())
pm.normals_split_custom_set(pn);po=bpy.data.objects.new('Original firstupperpad shelf - geometry estimated',pm);K.objects.link(po);features=[po];cutters.append(ellipse('Original firstupperpad true throughhole - estimated',pp['hole_centre_XY_m'][0],rx=pp['hole_radius_m'],ry=pp['hole_radius_m'],cy=pp['hole_centre_XY_m'][1],zbounds=pp['hole_extrusion_Z_m']));cutters[-1]['nativephoto_variant_uncertain']=True

def input_row(o):
 m=o.data;m.calc_loop_triangles();uv=m.uv_layers.active
 return {'name':o.name,'vertices':[list(v.co)for v in m.vertices],'triangles':[list(t.vertices)for t in m.loop_triangles],'corner_normals':[[list(m.corner_normals[li].vector)for li in t.loops]for t in m.loop_triangles],'triangle_UV':[[list(uv.data[li].uv)for li in t.loops]for t in m.loop_triangles],'triangle_surface_class':[int(m.attributes['WEWA_surface_class'].data[t.polygon_index].value)if m.attributes.get('WEWA_surface_class')else 4 for t in m.loop_triangles]}
inputs=[input_row(base)]+[input_row(o)for o in features]+[input_row(o)for o in cutters]
with tempfile.TemporaryDirectory(prefix='wewa-cowl-csg-')as td:
 inp=Path(td)/'in.json';out=Path(td)/'out.json';inp.write_text(json.dumps({'base':inputs[0],'features':inputs[1:1+len(features)],'drills':inputs[1+len(features):]}));subprocess.run([shutil.which('python'),str(H/'cowl_csg_worker_pad_v1.py'),str(inp),str(out)],check=True);cs=json.loads(out.read_text())
m=bpy.data.meshes.new('Original finite cowl shell with true elliptical rear cuts');m.from_pydata(cs['vertices'],[],cs['triangles']);m.update();uv=m.uv_layers.new(name='Original input-face interpolated angular-section UV');normal_owner=m.attributes.new('WEWA_source_input_index','INT','FACE');original_triangle=m.attributes.new('WEWA_source_triangle_index','INT','FACE');surface_class=m.attributes.new('WEWA_surface_class','INT','FACE');norm=[];max_plane=0.;min_bary=1.;owners={str(i):0 for i in range(len(inputs))}
for p in m.polygons:
 own=cs['triangle_source_owners'][p.index];fid=cs['triangle_source_face_ids'][p.index];ref=inputs[own];normal_owner.data[p.index].value=own;original_triangle.data[p.index].value=fid;surface_class.data[p.index].value=ref['triangle_surface_class'][fid];ids=ref['triangles'][fid];a,b,c=[np.array(ref['vertices'][i],dtype=np.float64)for i in ids];ns=np.array(ref['corner_normals'][fid],dtype=np.float64);us=np.array(ref['triangle_UV'][fid],dtype=np.float64);v0=b-a;v1=c-a;d00=v0@v0;d01=v0@v1;d11=v1@v1;denom=d00*d11-d01*d01;assert denom>0;face=np.cross(v0,v1);face/=np.linalg.norm(face);p.use_smooth=True;owners[str(own)]+=1
 for li in p.loop_indices:
  pos=np.array(m.vertices[m.loops[li].vertex_index].co,dtype=np.float64);v2=pos-a;d20=v2@v0;d21=v2@v1;beta=(d11*d20-d01*d21)/denom;gamma=(d00*d21-d01*d20)/denom;w=np.array([1-beta-gamma,beta,gamma]);min_bary=min(min_bary,float(w.min()));max_plane=max(max_plane,abs(float(v2@face)));no=w@ns;no/=np.linalg.norm(no);norm.append(no if own<=len(features) else-no);uv.data[li].uv=w@us
m.normals_split_custom_set(norm);m.materials.append(mat);obj=bpy.data.objects.new('Cowl finite shell plus first estimated upper pad - partial study',m);C.objects.link(obj);obj.parent=root;obj['structural_closed_volume']=True;obj['estimated_geometry']=True;K.hide_render=True;K.hide_viewport=True
bm=bmesh.new();bm.from_mesh(m);nm=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();m.calc_loop_triangles();areas=[];min_dot=1.
for t in m.loop_triangles:
 a,b,c=[np.array(m.vertices[i].co,dtype=np.float64)for i in t.vertices];cross=np.cross(b-a,c-a);length=np.linalg.norm(cross);areas.append(float(length/2));assert length>0;fn=cross/length
 for li in t.loops:min_dot=min(min_dot,float(fn@np.array(m.corner_normals[li].vector,dtype=np.float64)))
assert nm==0 and volume>0 and min(areas)>0 and min_dot>.9,(nm,volume,min(areas),min_dot);assert max_plane<1e-7 and min_bary>-.001,(max_plane,min_bary)
bpy.context.view_layer.update();source=H/'headlamp-cowl-shell-study-v8.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=obj;export=H/'headlamp-cowl-shell-study-v8.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_yup=True,export_extras=True)
report={'schema':1,'revision':'headlamp-cowl-shell-study-v8','source_sha256':sha(source),'export_sha256':sha(export),'baseline_source_sha256':A['source_sha256'],'baseline_export_sha256':A['export_sha256'],'shape_plan_sha256':sha(plan),'CSG_worker_sha256':sha(H/'cowl_csg_worker_pad_v1.py'),'collection':C.name,'root':root.name,'object':obj.name,'actual_triangles':len(areas),'min_triangle_area_m2':min(areas),'minimum_triangle_corner_normal_dot':min_dot,'non_manifold_edges':nm,'connected_components':cs['connected_components'],'positive_signed_volume_m3':volume,'CSG_stages':cs['stages'],'exact_original_triangle_owner_counts':owners,'max_actual_point_to_original_triangle_plane_distance_m':max_plane,'minimum_original_face_barycentric_coordinate':min_bary,'normal_UV_provenance':'Exact inputvolume and triangle IDs, barycentric interpolation inFloat64. Reverse subtractivecutter normals only. No nearest-surface ownership or globalpost-CSGbevel.','persistent_authoring_face_attributes':['WEWA_source_input_index','WEWA_source_triangle_index','WEWA_surface_class'],'surface_class_codes':{'1':'Original exterior','2':'Original interior','3':'Finite roundedwall edges','4':'Truecut walls','5':'Originalfirstpad candidate'},'surface_class_face_counts':{str(k):sum(v.value==k for v in surface_class.data)for k in[1,2,3,4,5]},'all_dimensions_estimated':True,'state':'Partial shell with true negative spaces; oneestimatedupperpad built; other5pads/gussets/ribs/endwallposts/hardware/mouldedcreases/paint NOT built yet. Identity/mount/depth conditional.','art_accepted':False};(P/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(src)==A['source_sha256'];print('COWL_TRUE_CUT_STUDY',json.dumps(report))
