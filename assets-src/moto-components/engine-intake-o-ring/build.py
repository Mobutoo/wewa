"""Original nominal periodic seal surface. Dimensions are related published, not RDC metrology."""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-o-ring-v1';P=json.loads((H/'parameters.json').read_text());assert not(H/'preflight-manifest.json').exists();sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,check_mesh,export,studio
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;parts=bpy.data.collections.new('WEWA_ENGINE_INTAKE_O_RING');stage=bpy.data.collections.new('INTAKE_O_RING_STUDIO_NOT_EXPORTED');s.collection.children.link(parts);s.collection.children.link(stage);datum=bpy.data.objects.new('Intake O-rings isolated review datum - not installed',None);parts.objects.link(datum)
N=P['tessellation']['major_segments'];M=P['tessellation']['section_segments'];r=P['calculated']['tube_radius_m'];A=P['calculated']['centreline_radius_m'];vs=[];norms=[];faces=[];uvs=[]
for i in range(N):
 u=math.tau*i/N
 for j in range(M):
  v=math.tau*j/M;vs.append(((A+r*math.cos(v))*math.cos(u),(A+r*math.cos(v))*math.sin(u),r*math.sin(v)));norms.append((math.cos(v)*math.cos(u),math.cos(v)*math.sin(u),math.sin(v)))
for i in range(N):
 for j in range(M):
  q=[i*M+j,((i+1)%N)*M+j,((i+1)%N)*M+(j+1)%M,i*M+(j+1)%M];t=[(i/N,j/M),((i+1)/N,j/M),((i+1)/N,(j+1)/M),(i/N,(j+1)/M)]
  for abc in [(0,1,2),(0,2,3)]:faces.append(tuple(q[k]for k in abc));uvs.append([t[k]for k in abc])
m=bpy.data.meshes.new('Analytic nominal torus 28.7 ID x1.9 section');m.from_pydata(vs,[],faces);m.update()
for p in m.polygons:p.use_smooth=True
m.normals_split_custom_set([norms[l.vertex_index]for l in m.loops]);uv=m.uv_layers.new(name='Original periodic torus seam UV')
for f,values in zip(m.polygons,uvs):
 for li,value in zip(f.loop_indices,values):uv.data[li].uv=value
C=P['material_baseline'];m.materials.append(material('Gray nominal seal geometry review',C['linear_basecolor'],C['metallic'],C['roughness']));objects=[]
for index,centre in enumerate(P['review_occurrences_centres_m']):
 o=bpy.data.objects.new('LJA00011 nominal intake O-ring '+str(index+1)+' - uncompressed',m);parts.objects.link(o);o.parent=datum;o.location=centre;objects.append(o)
bpy.context.view_layer.update();checks=[check_mesh(o)for o in objects];m.calc_loop_triangles();assert min(t.area for t in m.loop_triangles)>0
exact=2*math.pi**2*A*r*r
for q in checks:assert abs(q['signed_volume_m3']/exact-1)<.003
# Actual retained geometry extrema and normals are compared to nominal, not a supplier image.
radial=[math.hypot(v.co.x,v.co.y)for v in m.vertices];assert abs(min(radial)*2-.0287)<1e-8 and abs(max(radial)*2-.0325)<1e-8
assert abs(max(v.co.z for v in m.vertices)-r)<1e-9 and abs(min(v.co.z for v in m.vertices)+r)<1e-9
studio(s,stage,Vector((0,0,0)));s.camera.data.clip_start=.0001
for q in stage.objects:
 if q.type=='MESH':q.hide_render=True
 if q.type=='LIGHT':q.data.energy*=.035
source=H/'engine-intake-o-ring-v1-geometry.blend';glb=H/'engine-intake-o-ring-v1-geometry.glb';export(glb,[datum,*objects]);bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':sha(glb),'collection':parts.name,'root':datum.name,'geometry':checks,'triangles_per_type':len(m.loop_triangles),'drawn_triangles_two_occurrences':2*len(m.loop_triangles),'unique_meshes':1,'occurrences':2,'analytic_volume_per_ring_m3':exact,'nominal_published_related_ID_m':.0287,'nominal_published_related_section_m':.0019,'actual_mesh_ID_m':2*min(radial),'actual_mesh_OD_m':2*max(radial),'actual_mesh_section_z_m':max(v.co.z for v in m.vertices)-min(v.co.z for v in m.vertices),'source_normals_analytic':True,'automatic_attachment_allowed':False,'frame_isolated_not_motorcycle_world':True,'art_accepted':False};(H/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'geometry-source-check.json').write_text(json.dumps(report,indent=2)+'\n');print('NOMINAL_INTAKE_O_RING_GEOMETRY',json.dumps(report),flush=True)
