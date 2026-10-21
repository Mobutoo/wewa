"""True rear boundary cuts on immutable shell1, not section deformation.
Original exact CSG input-face provenance for normals/UVs, separate incomplete study.
"""
import bpy,bmesh,numpy as np,math,json,hashlib,tempfile,subprocess,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];P=R/'creative/reviews/headlamp-cowl-shell-study-v11';P.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();A=json.loads((R/'creative/reviews/headlamp-cowl-raw-return-study-v11/source-geometry-check.json').read_text());src=H/'headlamp-cowl-raw-return-study-v11.blend';assert sha(src)==A['source_sha256'];plan=R/'creative/research/headlamp-cowl/sixth-support-return-plan-v11.json';pc=json.loads(plan.read_text())['existing_scallop_cutters'];cfg={'centre_X_m_estimated':pc['centre_X_m'],'ellipse_radius_X_m_estimated':pc['radii_X_Y_m'][0],'ellipse_radius_Y_m_estimated':pc['radii_X_Y_m'][1],'ellipse_centre_Y_m_estimated':pc['centre_Y_m'],'extrusion_Z_m_estimated':pc['Z_cut_bounds_m']};bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;C=bpy.data.collections[A['collection']];root=bpy.data.objects[A['root']];base=bpy.data.objects[A['object']];K=bpy.data.collections.new('COWL_EDITABLE_CUTTING_INPUTS_v11_HIDDEN');s.collection.children.link(K);C.objects.unlink(base);K.objects.link(base);mat=base.active_material

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


for web in json.loads(plan.read_text())['first_pad_gussets']:
 zth=web['Y_thickness_m']/2;yc=web['Y_centre_m'];tri=web['triangle_XZ_m'];v=[(x,y,z)for y in[yc-zth,yc+zth]for x,z in tri];f=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)];mm=bpy.data.meshes.new('Original '+web['id']+' triangularsupport');mm.from_pydata(v,[],f);mm.update();bm0=bmesh.new();bm0.from_mesh(mm);bmesh.ops.recalc_face_normals(bm0,faces=bm0.faces);bm0.to_mesh(mm);bm0.free();mm.update();uu=mm.uv_layers.new(name='Original flatweb UV');nn=[];sc=mm.attributes.new('WEWA_surface_class','INT','FACE')
 for pp0 in mm.polygons:
  pp0.use_smooth=False;sc.data[pp0.index].value=5
  for k,li in enumerate(pp0.loop_indices):uu.data[li].uv=([(0,0),(1,0),(0,1)][k]if len(pp0.vertices)==3 else[(0,0),(1,0),(1,1),(0,1)][k]);nn.append(pp0.normal.copy())
 mm.normals_split_custom_set(nn);oo=bpy.data.objects.new('Original '+web['id']+' - estimated',mm);K.objects.link(oo);features.append(oo)

# Separate original boundedgeometry for four actuallyobserved supports.
from mathutils.bvhtree import BVHTree
from mathutils import Vector
reference7=H/'headlamp-cowl-shell-study-v7.blend';reference7report=json.loads((R/'creative/reviews/headlamp-cowl-shell-study-v7/source-geometry-check.json').read_text());assert sha(reference7)==reference7report['source_sha256']
with bpy.data.libraries.load(str(reference7),link=False)as(fr,to):to.objects=[reference7report['object']]
refobj=to.objects[0];refm=refobj.data;refbv=BVHTree.FromPolygons([v.co for v in refm.vertices],[p.vertices[:]for p in refm.polygons],all_triangles=True);bpy.data.objects.remove(refobj)

def original_mesh_feature(name,verts,faces,surface=5):
 mm=bpy.data.meshes.new(name+' originalfinitegeometry');mm.from_pydata(verts,[],faces);mm.update();bm0=bmesh.new();bm0.from_mesh(mm);bmesh.ops.recalc_face_normals(bm0,faces=bm0.faces);bm0.to_mesh(mm);bm0.free();mm.update();uv0=mm.uv_layers.new(name='Original perface local UV');nn=[];sc=mm.attributes.new('WEWA_surface_class','INT','FACE')
 for f0 in mm.polygons:
  f0.use_smooth=False;sc.data[f0.index].value=surface
  # Each convexplanar face gets its own 2D orthogonalbasis; no flattenedUV.
  no=Vector(f0.normal);a0=mm.vertices[f0.vertices[0]].co;axis=(mm.vertices[f0.vertices[1]].co-a0).normalized();other=no.cross(axis).normalized()
  for li in f0.loop_indices:
   v0=mm.vertices[mm.loops[li].vertex_index].co-a0;uv0.data[li].uv=(v0.dot(axis)/.05,v0.dot(other)/.05);nn.append(no.copy())
 mm.normals_split_custom_set(nn);oo=bpy.data.objects.new(name,mm);K.objects.link(oo);return oo

for pad in json.loads(plan.read_text())['four_next_pads']:
 name=pad['id'];side=pad['side_in_isolated_frame'];cent=Vector(pad['hole_centre_m_estimated']);U=Vector(pad['U_axis_world_estimated']);V=Vector(pad['V_axis_world_estimated']);N=Vector(pad['N_axis_world_estimated']);th=pad['thickness_m_estimated'];dep=pad['half_depth_Y_m_estimated'];inner=pad['inner_extension_m_estimated']
 def local(u,v,z):return cent+U*u+V*v+N*z
 def wall_u(v,z):
  origin=local(-side*.025,v,z);pos,no,idx,distance=refbv.ray_cast(origin,U*side,.12);assert pos is not None,(name,'no originalwall atmargin',v,z);return(pos-cent-V*v-N*z).dot(U)
 # Differentouteredges top/bottom follow the actualproxywall, extending0.8mm into it.
 rings=[]
 for z in[-th,0]:
  inneru=-side*inner;vs=np.linspace(-dep,dep,17);row=[(inneru,-dep)]+[(wall_u(float(vv),z)+side*.001,float(vv))for vv in vs]+[(inneru,dep)]
  corners={0,1,len(row)-2,len(row)-1}
  if side<0:
   corners={len(row)-1-k for k in corners};row=list(reversed(row))
  points2=[]
  for k,p0 in enumerate(row):
   p0=np.array(p0,dtype=np.float64)
   if k not in corners:points2.append(p0);continue
   a0=np.array(row[(k-1)%len(row)])-p0;b0=np.array(row[(k+1)%len(row)])-p0;ch=.00035;points2.extend([p0+a0/np.linalg.norm(a0)*ch,p0+b0/np.linalg.norm(b0)*ch])
  rings.append([tuple(local(float(u),float(v),z))for u,v in points2])
 nv=len(rings[0]);faces=[tuple(reversed(range(nv))),tuple(range(nv,nv*2))]+[(k,(k+1)%nv,(k+1)%nv+nv,k+nv)for k in range(nv)];o=original_mesh_feature('Original '+name+' shelf - estimated',rings[0]+rings[1],faces);features.append(o);o['native8495holecontrol_px']=pad['image8495_hole_native_px'];o['axis_depth_estimated_not_measured']=True
 for margin,vc in[('front',-dep*.7),('rear',dep*.7)]:
  ztop=-th+.0003;uo=wall_u(vc,ztop)+side*.0008;footz=-th-.008;uf=wall_u(vc,footz)+side*.0008;tri=[(-side*(inner-.002),ztop),(uo,ztop),(uf,footz)];vtx=[tuple(local(u,vc+vy,z))for vy in[-.00065,.00065]for u,z in tri];ff=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)];features.append(original_mesh_feature('Original '+name+' '+margin+' web - estimated',vtx,ff))
 # One bounded true throughhole along thispad's OWNnormal, not copiedglobalZ.
 nn=128;rad=pad['hole_radius_m_estimated'];zvals=[-th-.001,.001];vv=[tuple(local(rad*math.cos(math.tau*k/nn),rad*math.sin(math.tau*k/nn),z))for z in zvals for k in range(nn)];ff=[(k,(k+1)%nn,(k+1)%nn+nn,k+nn)for k in range(nn)]+[tuple(reversed(range(nn))),tuple(range(nn,nn*2))];mm=bpy.data.meshes.new(name+' originalorientedcylinder');mm.from_pydata(vv,[],ff);mm.update();uv0=mm.uv_layers.new(name='Original orientedpad hole UV');nos=[]
 for f0 in mm.polygons:
  f0.use_smooth=f0.index<nn
  for k,li in enumerate(f0.loop_indices):
   ix=mm.loops[li].vertex_index;ang=math.tau*(ix%nn)/nn
   if f0.index<nn:no=U*math.cos(ang)+V*math.sin(ang);uv0.data[li].uv=(f0.index/nn if k in[0,3]else(f0.index+1)/nn,1 if ix>=nn else 0)
   else:no=N*(-1 if f0.index==nn else 1);uv0.data[li].uv=(.5+.5*math.cos(ang),.5+.5*math.sin(ang))
   nos.append(no)
 mm.normals_split_custom_set(nos);oo=bpy.data.objects.new('Original '+name+' pad throughhole - estimated',mm);K.objects.link(oo);cutters.append(oo)

# TheP6return is already integrated in thisRAWbase; bore is a separatebounded truecut.
import ast,bisect
ns={'np':np,'math':math,'bisect':bisect,'profile':json.loads((H/'rear-profile-v5.json').read_text())};nodes=[n for n in ast.parse((H/'build_raw_study_v5.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name in['rear_profile','section','cat','mid','frame']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen-profile-functions-only','exec'),ns);rp=json.loads(plan.read_text())['P6_return_candidate'];th=math.radians(rp['theta_centre_degrees_estimated']);p0=ns['mid'](th,1);n,b=ns['frame'](th,1);eps=1e-5;T=ns['mid'](th+eps,1)-ns['mid'](th-eps,1);T/=np.linalg.norm(T);axis=b;basis1=T;basis2=np.cross(axis,basis1);basis2/=np.linalg.norm(basis2);centre=p0+n*rp['hole_normal_offset_from_original_rear_m_estimated']+b*rp['hole_back_offset_m_estimated'];nseg=128;rad=rp['hole_radius_m_estimated'];half=rp['hole_depth_m_estimated']/2;vv=[tuple(centre+(basis1*math.cos(math.tau*k/nseg)+basis2*math.sin(math.tau*k/nseg))*rad+axis*z)for z in[-half,half]for k in range(nseg)];ff=[(k,(k+1)%nseg,(k+1)%nseg+nseg,k+nseg)for k in range(nseg)]+[tuple(reversed(range(nseg))),tuple(range(nseg,nseg*2))];hm=bpy.data.meshes.new('Original P6 integratedreturn throughbore');hm.from_pydata(vv,[],ff);hm.update();uv0=hm.uv_layers.new(name='Original P6 bore UV');hn=[]
for pp0 in hm.polygons:
 pp0.use_smooth=pp0.index<nseg
 for k,li in enumerate(pp0.loop_indices):
  ix=hm.loops[li].vertex_index;a6=math.tau*(ix%nseg)/nseg
  if pp0.index<nseg:no=basis1*math.cos(a6)+basis2*math.sin(a6);uv0.data[li].uv=(pp0.index/nseg if k in[0,3]else(pp0.index+1)/nseg,1 if ix>=nseg else 0)
  else:no=axis*(-1 if pp0.index==nseg else 1);uv0.data[li].uv=(.5+.5*math.cos(a6),.5+.5*math.sin(a6))
  hn.append(no)
hm.normals_split_custom_set(hn);ho=bpy.data.objects.new('Original P6 shapedreturn bore - estimated',hm);K.objects.link(ho);cutters.append(ho);(P/'P6-control-geometry.json').write_text(json.dumps({'hole_centre_m_estimated':centre.tolist(),'hole_axis_world_estimated':axis.tolist(),'wall_m_estimated':rp['wall_m_estimated'],'integratedsharedboundary_no_root_CSG':True,'trueflat_section_faces':True,'construction_hypothesis_only':True,'art_accepted':False},indent=2)+'\n')

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
 inp=Path(td)/'in.json';out=Path(td)/'out.json';inp.write_text(json.dumps({'base':inputs[0],'features':inputs[1:1+len(features)],'drills':inputs[1+len(features):]}));subprocess.run([shutil.which('python'),str(H/'cowl_csg_worker_pad_v4.py'),str(inp),str(out)],check=True);cs=json.loads(out.read_text())
 if cs.get('rejected'):
  (P/('construction-rejection-'+str(1+len(list(P.glob('construction-rejection-*.json'))))+'.json')).write_text(json.dumps(cs,indent=2)+'\n');raise RuntimeError(cs['reason'])
# Inspect actualFloat32CSGtransport BEFORE Blender and interpolation.
VV=np.asarray(cs['vertices'],dtype=np.float32).astype(np.float64);TT=np.asarray(cs['triangles'],dtype=np.int64);crosses=np.cross(VV[TT[:,1]]-VV[TT[:,0]],VV[TT[:,2]]-VV[TT[:,0]]);lens=np.linalg.norm(crosses,axis=1);zero_ids=np.where(lens==0)[0]
if len(zero_ids):
 rows=[]
 for tid in zero_ids[:30]:
  ids=TT[tid];points=VV[ids];owner=cs['triangle_source_owners'][int(tid)];rows.append({'triangle_index':int(tid),'owner':owner,'source_name':inputs[owner]['name'],'source_face':cs['triangle_source_face_ids'][int(tid)],'indices':ids.tolist(),'points':points.tolist(),'unique_position_count':len(set(map(tuple,points))),'edge_lengths_m':[float(np.linalg.norm(points[(i+1)%3]-points[i]))for i in range(3)]})
 (P/'CSG-Float32-quantization-rejection.json').write_text(json.dumps({'rejected':True,'zero_area_count':int(len(zero_ids)),'examples':rows,'no_source_or_export_written':True,'no_faces_or_normals_masked':True},indent=2)+'\n');cache=Path('/workspace/wewa-assets/work-in-progress/headlamp-cowl-shell-study-v11/CSG-Float32-rejected.json');cache.parent.mkdir(parents=True,exist_ok=True);cache.write_text(json.dumps(cs));raise RuntimeError('Float32 CSGzeroareas: see precisequantizationdiagnostic')
m=bpy.data.meshes.new('Original finite cowl shell with true elliptical rear cuts');m.from_pydata(cs['vertices'],[],cs['triangles']);m.update();uv=m.uv_layers.new(name='Original input-face interpolated angular-section UV');normal_owner=m.attributes.new('WEWA_source_input_index','INT','FACE');original_triangle=m.attributes.new('WEWA_source_triangle_index','INT','FACE');surface_class=m.attributes.new('WEWA_surface_class','INT','FACE');norm=[];max_plane=0.;min_bary=1.;owners={str(i):0 for i in range(len(inputs))}
for p in m.polygons:
 own=cs['triangle_source_owners'][p.index];fid=cs['triangle_source_face_ids'][p.index];ref=inputs[own];normal_owner.data[p.index].value=own;original_triangle.data[p.index].value=fid;surface_class.data[p.index].value=ref['triangle_surface_class'][fid];ids=ref['triangles'][fid];a,b,c=[np.array(ref['vertices'][i],dtype=np.float64)for i in ids];ns=np.array(ref['corner_normals'][fid],dtype=np.float64);us=np.array(ref['triangle_UV'][fid],dtype=np.float64);us=us-us[0] if (own,fid)==(16,196) else us;v0=b-a;v1=c-a;d00=v0@v0;d01=v0@v1;d11=v1@v1;denom=d00*d11-d01*d01;assert denom>0;face=np.cross(v0,v1);face/=np.linalg.norm(face);p.use_smooth=True;owners[str(own)]+=1
 for li in p.loop_indices:
  pos=np.array(m.vertices[m.loops[li].vertex_index].co,dtype=np.float64);v2=pos-a;d20=v2@v0;d21=v2@v1;beta=(d11*d20-d01*d21)/denom;gamma=(d00*d21-d01*d20)/denom;w=np.array([1-beta-gamma,beta,gamma]);min_bary=min(min_bary,float(w.min()));max_plane=max(max_plane,abs(float(v2@face)));no=w@ns;no/=np.linalg.norm(no);norm.append(no if own<=len(features) else-no);uv.data[li].uv=w@us
m.normals_split_custom_set(norm);m.materials.append(mat);obj=bpy.data.objects.new('Cowl finite shell plus six estimated support features - study',m);C.objects.link(obj);obj.parent=root;obj['structural_closed_volume']=True;obj['estimated_geometry']=True;K.hide_render=True;K.hide_viewport=True
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
 raise RuntimeError('Source11 geometry/normals rejected; see normal-geometry-rejection-1.json')
assert max_plane<1e-7 and min_bary>-.001,(max_plane,min_bary)
bpy.context.view_layer.update();source=H/'headlamp-cowl-shell-study-v11.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=obj;export=H/'headlamp-cowl-shell-study-v11.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_yup=True,export_extras=True)
report={'schema':1,'revision':'headlamp-cowl-shell-study-v11','source_sha256':sha(source),'export_sha256':sha(export),'baseline_source_sha256':A['source_sha256'],'baseline_export_sha256':A['export_sha256'],'shape_plan_sha256':sha(plan),'CSG_worker_sha256':sha(H/'cowl_csg_worker_pad_v4.py'),'float32_transport_normalization':cs.get('float32_transport_normalization'),'collection':C.name,'root':root.name,'object':obj.name,'actual_triangles':len(areas),'min_triangle_area_m2':min(areas),'minimum_triangle_corner_normal_dot':min_dot,'non_manifold_edges':nm,'connected_components':cs['connected_components'],'positive_signed_volume_m3':volume,'CSG_stages':cs['stages'],'exact_original_triangle_owner_counts':owners,'max_actual_point_to_original_triangle_plane_distance_m':max_plane,'minimum_original_face_barycentric_coordinate':min_bary,'UV_precision_rebase':{'source_input':16,'source_face':196,'operation':'Subtract original source triangle first UV in Float64 BEFORE interpolation. A translation only; unchanged derivative/chart scale, one new chart seam. Original gray material has no texture/normal map.','reason':'One geometrically nonzero 7.45nm-edge triangle lost distinct UVs at Float32 absolute chart values.'},'normal_UV_provenance':'Exact inputvolume and triangle IDs, barycentric interpolation inFloat64. Reverse subtractivecutter normals only. No nearest-surface ownership or globalpost-CSGbevel.','persistent_authoring_face_attributes':['WEWA_source_input_index','WEWA_source_triangle_index','WEWA_surface_class'],'surface_class_codes':{'1':'Original exterior','2':'Original interior','3':'Finite roundedwall edges','4':'Truecut walls','5':'Originalsupport candidates','6':'P6returnexterior','7':'P6returninterior'},'surface_class_face_counts':{str(k):sum(v.value==k for v in surface_class.data)for k in[1,2,3,4,5,6,7]},'original_input_volume_names':[row['name'] for row in inputs],'features_count':len(features),'all_dimensions_estimated':True,'state':'Partial shell with true negative spaces; sixestimatedsupports built; mainribs/endwallposts/hardware/mouldedcreases/paint NOT built yet. Identity/mount/depth conditional.','art_accepted':False};(P/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(src)==A['source_sha256'];print('COWL_TRUE_CUT_STUDY',json.dumps(report))
