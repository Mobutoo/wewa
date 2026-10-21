"""Original partial external weld solid, no donor mesh/photo/hidden penetration."""
from pathlib import Path
import bpy,json,math,hashlib,numpy as np
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-protection-end-weld-a-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(R/P['guide_source'])==P['guide_source_sha256'];bpy.ops.wm.read_factory_settings(use_empty=True);N=P['angular_segments'];M=P['outer_profile_segments'];r=P['tube_outer_radius_m_estimated'];tile=P['UV_tile_m_estimated'];start=math.radians(P['arc_start_deg_estimated']);end=math.radians(P['arc_end_deg_estimated']);K=M+2
# Nonperiodic constructionwindow: the rear is unbuilt, not silently closed into a ring.
def legs(phi):
 a=P['axial_leg_m_estimated']*(1+P['leg_variation_fraction_estimated']*(.65*math.sin(11*phi+.3)+.35*math.sin(4*phi-1.0)))
 b=P['radial_leg_m_estimated']*(1+P['leg_variation_fraction_estimated']*(.60*math.sin(9*phi-.7)+.40*math.sin(3*phi+.8)))
 return a,b
def pt(phi,t):
 a,b=legs(phi);s=a*t;crown=b*(1-t)+b*(P['crown_bulge_fraction_estimated']+P['crown_variation_fraction_estimated']*math.sin(23*phi+1.3*t))*math.sin(math.pi*t)**2;rr=r+crown;return np.array([s,rr*math.cos(phi),rr*math.sin(phi)],float)
def ring(phi):return [np.array([0,r*math.cos(phi),r*math.sin(phi)])]+[pt(phi,j/M)for j in range(M+1)]
V=[];faces=[];tags=[]
for i in range(N+1):V.extend(ring(start+(end-start)*i/N))
for i in range(N):
 for j in range(K):
  k=(j+1)%K;a=i*K+j;b=(i+1)*K+j;c=(i+1)*K+k;d=i*K+k;kind='plate_contact'if j==0 else'tube_contact'if j==K-1 else'outer';faces.extend([(a,b,c),(a,c,d)]);tags.extend([(kind,j),(kind,j)])
for ii,phi in [(0,start),(N,end)]:
 positions=ring(phi);poly=[Vector((float(p[0]),float(math.hypot(p[1],p[2])),0))for p in positions];lookup={tuple(p):i for i,p in enumerate(poly)};tris=tessellate_polygon([poly]);want=np.array([0,-math.sin(phi),math.cos(phi)])*(-1 if ii==0 else 1)
 assert len(tris)==K-2
 for tri in tris:
  ids=[int(p)if isinstance(p,int)else lookup[tuple(p)]for p in tri];xyz=[positions[i]for i in ids];n=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0])
  if np.dot(n,want)<0:ids.reverse()
  faces.append(tuple(ii*K+i for i in ids));tags.append(('cap_start'if ii==0 else'cap_end',0))
mesh=bpy.data.meshes.new('Finite external frontal weld-A section sweep');mesh.from_pydata(V,[],faces);mesh.update();uv=mesh.uv_layers.new(name='Original weld approximately10mm metric tile');phi_for_vertex=[start+(end-start)*(i//K)/N for i in range(len(V))]
def normal(phi,t):
 e=1e-5;pa=(pt(phi+e,t)-pt(phi-e,t))/(2*e);lo=max(0,t-e);hi=min(1,t+e);pb=(pt(phi,hi)-pt(phi,lo))/(hi-lo);n=np.cross(pa,pb);return n/np.linalg.norm(n)
ns=[];min_dot=1;opposed=0
for face,tag in zip(mesh.polygons,tags):
 kind,j=tag;face.use_smooth=kind in ['outer','tube_contact']
 for li in face.loop_indices:
  vi=mesh.loops[li].vertex_index;phi=phi_for_vertex[vi];section=vi%K;p=np.array(mesh.vertices[vi].co);rad=math.hypot(p[1],p[2]);t=max(0,(section-1)/M)
  if kind=='outer':n=normal(phi,t)
  elif kind=='plate_contact':n=np.array([-1.,0,0])
  elif kind=='tube_contact':n=np.array([0,-math.cos(phi),-math.sin(phi)])
  else:n=np.array([0,-math.sin(phi),math.cos(phi)])*(-1 if kind=='cap_start'else 1)
  ns.append(n.tolist());fd=float(np.dot(n,np.array(face.normal)));min_dot=min(min_dot,fd);opposed+=fd<0
  if kind.startswith('cap'):tex=(p[0]/tile,(rad-r)/tile)
  elif kind=='plate_contact':tex=(phi*r/tile,(rad-r)/tile)
  elif kind=='tube_contact':tex=(phi*r/tile,-p[0]/tile)
  else:tex=(phi*r/tile,(1+t)*max(P['axial_leg_m_estimated'],P['radial_leg_m_estimated'])/tile)
  uv.data[li].uv=tex
mesh.normals_split_custom_set(ns);mesh.update();col=bpy.data.collections.new(P['collection']);bpy.context.scene.collection.children.link(col);o=bpy.data.objects.new('Weld-A frontal exterior only, rear and penetration absent',mesh);col.objects.link(o);o['all_dimensions_estimated']=True;o['rear_continuation_built']=False;o['internal_penetration_built']=False
mat=bpy.data.materials.new('Neutral geometry gray, no final coating');mat.use_nodes=True;node=mat.node_tree.nodes['Principled BSDF'];node.inputs['Base Color'].default_value=(.30,.32,.35,1);node.inputs['Roughness'].default_value=.40;mesh.materials.append(mat)
mesh.calc_loop_triangles();co=np.array([v.co[:]for v in mesh.vertices],np.float64);tr=np.array([t.vertices[:]for t in mesh.loop_triangles],np.int32);A=co[tr[:,0]];B=co[tr[:,1]];C=co[tr[:,2]];areas=np.linalg.norm(np.cross(B-A,C-A),axis=1)/2;volume=float(np.einsum('ij,ij->i',A,np.cross(B,C)).sum()/6);edges={}
for a,b,c in tr:
 for x,y in [(a,b),(b,c),(c,a)]:key=tuple(sorted((int(x),int(y))));edges[key]=edges.get(key,0)+1
nm=sum(x!=2 for x in edges.values());chi=len(co)-len(edges)+len(tr);assert volume>0 and nm==0 and chi==2 and np.min(areas)>1e-18 and opposed==0,(volume,nm,chi,np.min(areas),opposed)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;src=H/'engine-protection-end-weld-a-v1.blend';glb=H/'engine-protection-end-weld-a-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True);bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True,relative_remap=False)
h=hashlib.sha256()
for a in [co.astype(np.float32),tr]:h.update(a.tobytes())
report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(src),'export_sha256':sha(glb),'source_script_sha256':sha(Path(__file__)),'actual_vertices':len(co),'actual_triangles':len(tr),'signed_volume_m3':volume,'minimum_triangle_area_m2':float(areas.min()),'zero_area_triangles':int(np.sum(areas<=1e-18)),'nonmanifold_edges':nm,'euler_characteristic':chi,'minimum_authored_corner_normal_dot_geometric_face':min_dot,'opposed_authored_corner_normals':opposed,'bounds_m':[co.min(0).tolist(),co.max(0).tolist()],'native_POSITION_triangle_digest':h.hexdigest(),'axial_extent_m':float(co[:,0].max()),'radial_minmax_m':[float(np.hypot(co[:,1],co[:,2]).min()),float(np.hypot(co[:,1],co[:,2]).max())],'closed_partial_window_caps_not_real_weld_ends':True,'rear_continuation_built':False,'second_junction_built':False,'internal_penetration_built':False,'actual_section_source_recipe':'Explicit axial/radial legs + smooth original crown surface, finite closed contact faces, no modifiers or normal-buffer repair','all_dimensions_estimated':True,'guide_source_sha256':P['guide_source_sha256'],'current_RDC_identity_verified':False,'installed_fit_or_strength_verified':False,'art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(H/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(R/P['guide_source'])==P['guide_source_sha256'];print('WELD_A_G3_BUILT',json.dumps(report),flush=True)
