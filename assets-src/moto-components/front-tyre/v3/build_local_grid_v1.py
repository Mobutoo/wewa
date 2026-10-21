"""Distinct local structured-grid diagnostic; never overwrites rejected v1."""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys,math
import numpy as np
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/front-tyre-v3'
sys.path.insert(0,str(H));from junction_field import JunctionField
P=json.loads((H/'parameters.json').read_text());Q=json.loads((H/'local-grid-parameters-v1.json').read_text());F=JunctionField(P)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();oldsource=R/Q['baseline_source'];assert sha(oldsource)==Q['baseline_sha256']
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('WEWA_FRONT_TYRE_V3_LOCAL_GRID_DIAGNOSTIC_V2');s.collection.children.link(col)
with bpy.data.libraries.load(str(oldsource),link=False)as(a,b):b.objects=[P['original_inspection_object']]
o=b.objects[0];col.objects.link(o);o.hide_set(False);o.hide_render=False;m=o.data;m.calc_loop_triangles()
def arr(c,k,n,dtype):
 a=np.empty(len(c)*n,dtype);c.foreach_get(k,a);return a.reshape(-1,n)if n>1 else a
oldV=arr(m.vertices,'co',3,np.float32);oldI=arr(m.loop_triangles,'vertices',3,np.int32);oldL=arr(m.loop_triangles,'loops',3,np.int32)
oldUV=arr(m.uv_layers[0].data,'uv',2,np.float32);oldN=arr(m.corner_normals,'vector',3,np.float32);oldPoly=arr(m.loop_triangles,'polygon_index',1,np.int32)
nu=1050;nv=len(oldV)//nu;assert nv*nu==len(oldV)and len(m.polygons)==len(oldV)and all(len(p.vertices)==4 for p in m.polygons)
quads=arr(m.polygons,'loop_start',1,np.int32)[:,None]+np.arange(4);quadids=arr(m.loops,'vertex_index',1,np.int32)[quads]
assert np.array_equal(quadids[:,0],np.arange(len(oldV)))
section=oldV[:nv,0].astype(float);tv=oldUV[quads[:nv,0],1].astype(float)
positive=np.flatnonzero((tv<5/30)&(section>=0));lo=positive[section[positive]<.0042][-1];hi=positive[section[positive]>.0078][0]
negative=np.flatnonzero((tv>25/30)&(section<0));nlo=negative[np.abs(section[negative])>.0078][-1];nhi=negative[np.abs(section[negative])<.0042][0]
# Two actual source-rail intervals, not a copied opposite-side triangle mesh.
intervals=[(int(lo),int(hi)),(int(nlo),int(nhi))];xlo=float(abs(section[lo]));xhi=float(abs(section[hi]));assert xlo<.0042<.0047<.0073<.0078<xhi
fu=Q['angular_subdivisions_per_old_cell'];fv=Q['section_subdivisions_per_old_cell'];phase_cells=Q['patch_angular_old_cells_either_side'];assert 15*70==nu
patch=np.zeros((nu,nv),bool)
for i in range(nu):
 if i%15<phase_cells or i%15>=15-phase_cells:
  for a,b in intervals:patch[i,a:b]=True
patch=patch.ravel();old_count=len(oldV);V=oldV.tolist();Nref=oldN[quads[:,0]].tolist();weights=np.zeros(old_count).tolist();grid={};edgepoints={};faces=[];uvs=[];norms=[];face_patch=[]
# Every original vertex stays available; unrelated original coordinates remain exact.
x=oldV[:,0].astype(float);yy=oldV[:,1].astype(float);zz=oldV[:,2].astype(float)-.29;rad=np.hypot(yy,zz);arc=np.arctan2(yy,zz)*F.R
outer=(np.tile(tv,nu)<5/30)|(np.tile(tv,nu)>25/30);delta=F.depth(x,arc)-F.depth(x,arc,False);changed=outer&(delta>1e-12)
for k in np.flatnonzero(changed):
 rr=rad[k]-delta[k];th=arc[k]/F.R;V[k]=[float(oldV[k,0]),float(rr*math.sin(th)),float(.29+rr*math.cos(th))]
triangles_by_poly=[[]for _ in range(len(m.polygons))]
for k,p in enumerate(oldPoly):triangles_by_poly[int(p)].append(k)
def source_point(qi,u,v):
 ids=quadids[qi];tlist=triangles_by_poly[qi];diagAC=any(int(ids[0])in oldI[k]and int(ids[2])in oldI[k]for k in tlist)
 if diagAC:
  bary=np.array([1-v,v-u,u,0.])if v>=u else np.array([1-u,0.,v,u-v])
 else:bary=np.array([1-u-v,v,0.,u])if u+v<=1 else np.array([0.,1-u,u+v-1,1-v])
 b=(oldV[ids].astype(float)*bary[:,None]).sum(0);n=(oldN[quads[qi]]*bary[:,None]).sum(0);n/=np.linalg.norm(n)
 return b,n

def sm(a,b,x):
 t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def crown_scalar(x,distance):
 ax=abs(x);c=F.coefficients[0];u=max(0.,min(1.,ax/.012))
 for _ in range(9):
  f=c[0,0]+u*(c[1,0]+u*(c[2,0]+u*c[3,0]))-ax
  der=c[1,0]+u*(2*c[2,0]+3*u*c[3,0]);u=max(0.,min(1.,u-f/der))
 radius=c[0,1]+u*(c[1,1]+u*(c[2,1]+u*c[3,1]))
 a=.003*(1-sm(.00035,.00130,distance));b=.0016*(1-sm(.0003,.0010,abs(ax-.006)))
 return radius-(a**4+b**4)**.25

def vertex(qi,ki,kj):
 i=qi//nv;j=qi%nv;key=((i*fu+ki)%(nu*fu),j*fv+kj)
 if key in grid:return grid[key]
 u=ki/fu;v=kj/fv;b,n=source_point(qi,u,v);ax=abs(b[0]);phase=((i+u)/15)%1;distance=min(phase,1-phase)*F.pitch
 w=sm(xlo,.0047,ax)*(1-sm(.0073,xhi,ax))*(1-sm(.0013,phase_cells/15*F.pitch,distance))
 if ki in(0,fu)and kj in(0,fv):
  idx=((i+(ki==fu))%nu)*nv+j+(kj==fv);grid[key]=idx;weights[idx]=max(weights[idx],w);return idx
 theta=math.tau*((i+u)/nu+.68*ax/.031/70);rr=crown_scalar(b[0],distance);a=np.array([b[0],rr*math.sin(theta),.29+rr*math.cos(theta)])
 p=(b+w*(a-b)).astype(np.float32);idx=len(V);V.append(p.tolist());Nref.append(n.tolist());weights.append(w);grid[key]=idx
 # Boundary neighbours are split on the original straight edge, not projected.
 if ki in(0,fu):
  edge=(int(quadids[qi,0 if ki==0 else 3]),int(quadids[qi,1 if ki==0 else 2]));t=v
  edgepoints.setdefault(tuple(sorted(edge)),{})[idx]=(edge,t)
 if kj in(0,fv):
  edge=(int(quadids[qi,0 if kj==0 else 1]),int(quadids[qi,3 if kj==0 else 2]));t=u
  edgepoints.setdefault(tuple(sorted(edge)),{})[idx]=(edge,t)
 return idx
# Build all shared structured grid points first, so adjacent source faces know every split.
patch_ids=np.flatnonzero(patch)
for seq,qi in enumerate(patch_ids):
 for ki in range(fu+1):
  for kj in range(fv+1):vertex(int(qi),ki,kj)
 if seq%500==0:print('LOCAL_GRID_POINTS',seq,len(patch_ids),len(V),flush=True)

def add(face,uv,normal,ispatch):faces.append(face);uvs.append(uv);norms.append(normal);face_patch.append(ispatch)
for qi in patch_ids:
 qi=int(qi);i=qi//nv;j=qi%nv;v0=tv[j];v1=tv[j+1]if j+1<nv else 1.
 for ki in range(fu):
  for kj in range(fv):
   ids=[vertex(qi,ki,kj),vertex(qi,ki,kj+1),vertex(qi,ki+1,kj+1),vertex(qi,ki+1,kj)]
   uv=[[(i+(ki+a)/fu)/nu,v0+(v1-v0)*(kj+b)/fv]for a,b in[(0,0),(0,1),(1,1),(1,0)]]
   for local in[(0,1,2),(0,2,3)]:add([ids[z]for z in local],[uv[z]for z in local],[Nref[ids[z]]for z in local],True)
# Exact original triangles outside patch, split only where their boundary neighbours acquired shared points.
outside_split_faces=0
for k,tri in enumerate(oldI):
 if patch[oldPoly[k]]:continue
 uv=oldUV[oldL[k]];nr=oldN[oldL[k]];per=[];pu=[];pn=[]
 for e in range(3):
  a=int(tri[e]);b=int(tri[(e+1)%3]);per.append(a);pu.append(uv[e]);pn.append(nr[e]);key=tuple(sorted((a,b)))
  more=[]
  for idx,(edge,t)in edgepoints.get(key,{}).items():
   t=t if edge==(a,b)else 1-t
   if 0<t<1:more.append((t,idx))
  for t,idx in sorted(more):per.append(idx);pu.append(uv[e]*(1-t)+uv[(e+1)%3]*t);n=nr[e]*(1-t)+nr[(e+1)%3]*t;pn.append(n/np.linalg.norm(n))
 if len(per)==3:add(per,pu,pn,False);continue
 outside_split_faces+=1;centroid=np.mean(oldV[tri].astype(float),axis=0).astype(np.float32);idx=len(V);V.append(centroid.tolist());Nref.append(np.mean(nr,axis=0).tolist());weights.append(0.)
 cu=np.mean(uv,axis=0);cn=np.mean(nr,axis=0);cn/=np.linalg.norm(cn)
 for z in range(len(per)):add([idx,per[z],per[(z+1)%len(per)]],[cu,pu[z],pu[(z+1)%len(per)]],[cn,pn[z],pn[(z+1)%len(per)]],False)
V=np.asarray(V,np.float32);I=np.asarray(faces,np.int32);UV=np.asarray(uvs,np.float32);NN=np.asarray(norms,np.float32);W=np.asarray(weights,float)
assert np.array_equal(V[:old_count][~changed],oldV[~changed])and np.array_equal(V[:old_count,0],oldV[:,0]);assert np.array_equal(V.min(0),oldV.min(0))and np.array_equal(V.max(0),oldV.max(0))
tri=V[I].astype(float);cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(cross,axis=1)*.5;assert area.min()>1e-18,area.min()
volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);assert volume>0
mesh=bpy.data.meshes.new('Local structured U and section grid at existing groove junctions');mesh.from_pydata(V,[],I);mesh.update();assert not mesh.validate(clean_customdata=False)
layer=mesh.uv_layers.new(name=m.uv_layers[0].name);layer.data.foreach_set('uv',UV.ravel());mesh.polygons.foreach_set('use_smooth',np.ones(len(I),bool));mesh.update();fresh=arr(mesh.corner_normals,'vector',3,np.float32).reshape(-1,3,3)
weight=W[I];blended=NN*(1-weight[:,:,None])+fresh*weight[:,:,None];blended/=np.linalg.norm(blended,axis=2)[:,:,None];mesh.normals_split_custom_set(blended.reshape(-1,3));stored=arr(mesh.corner_normals,'vector',3,np.float32).reshape(-1,3,3)
unitface=cross/np.linalg.norm(cross,axis=1)[:,None];dots=(stored*unitface[:,None,:]).sum(2);angles=np.degrees(np.arccos(np.clip(dots,-1,1)))
bm=bmesh.new();bm.from_mesh(mesh);nm=sum(not e.is_manifold for e in bm.edges);chi=len(bm.verts)-len(bm.edges)+len(bm.faces);bm.free();assert nm==0 and chi==0,(nm,chi)
o.data=mesh;o.name='Front tyre local structured junction diagnostic v2';o['component_id']=P['component_id'];o['art_accepted']=False
mat=bpy.data.materials.new('G3 constant gray no grain');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.22,.24,.26,1);bs.inputs['Roughness'].default_value=.4;mesh.materials.append(mat)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
stem='front-tyre-v3-local-grid-diagnostic-v2';glb=H/(stem+'-inspection.glb');bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_normals=True,export_texcoords=True,export_tangents=False)
s.world=bpy.data.worlds.new('FRONT TYRE G3 WORLD');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.20,.23,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
for name,loc,power,size in [('KEY',(.7,-.7,1),30,.6),('FILL',(-.5,-.3,.6),12,.6),('EDGE',(.25,.7,.65),20,.5)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;q=bpy.data.objects.new(name,d);s.collection.objects.link(q);q.location=loc;q.rotation_euler=(Vector((0,0,.29))-q.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('FRONT TYRE G3 CAMERA',bpy.data.cameras.new('FRONT TYRE G3 CAMERA'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.clip_start=.001;cam.data.clip_end=5;cam.location=(.075,-.17,.69);cam.rotation_euler=(Vector((.012,-.1,.562))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.05
s.render.engine='CYCLES';s.render.threads_mode='FIXED';s.render.threads=1;s.cycles.samples=24;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.5
source=H/(stem+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False)
report={'component_id':P['component_id'],'revision':Q['revision'],'source_path':str(source.relative_to(R)),'source_sha256':sha(source),'export_path':str(glb.relative_to(R)),'export_sha256':sha(glb),'script_sha256':sha(Path(__file__)),'field_script_sha256':sha(H/'junction_field.py'),'collection':col.name,'source_object':o.name,'vertices':len(V),'triangles':len(I),'minimum_triangle_area_m2':float(area.min()),'signed_volume_m3':volume,'nonmanifold_edges':nm,'euler_characteristic':chi,'patch_old_quads':int(patch.sum()),'outside_source_triangles_split':outside_split_faces,'actual_patch_boundary_absX_m':[xlo,xhi],'source_section_intervals':intervals,'old_vertices_radially_modified':int(changed.sum()),'protected_old_vertex_coordinates_exact':True,'all_old_vertex_X_exact':True,'axis_aligned_bounds_exact':True,'old_vertex_max_radial_extra_depth_m':float(delta[changed].max()),'new_vertices_are_not_bounded_by_old_vertex_p4_displacement':True,'C1_weight_does_not_make_reference_globally_C1':True,'normal_storage_max_error':float(np.linalg.norm(stored-blended,axis=2).max()),'normal_vs_face_angle_deg_p50_p95_max':np.quantile(angles,[.5,.95,1]).tolist(),'normal_corners_opposed_to_face':int((dots<0).sum()),'sampled20um_goal_met':False,'sampled20um_not_retested_or_received':True,'diagnostic_only_no_production_freeze':True,'material_built':False,'art_accepted':False}
(O/'local-grid-source-geometry-check-v1.json').write_text(json.dumps(report,indent=2)+'\n');print('LOCAL_GRID_DIAGNOSTIC_BUILT',json.dumps(report),flush=True)
