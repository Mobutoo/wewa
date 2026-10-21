"""Add only observed-related rear piping/stitches; protect frozen envelope2."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
from collections import defaultdict,Counter
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/seat-envelope-study-v3';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();b=json.loads((R/'creative/reviews/seat-envelope-study-v2/build-report.json').read_text());source2=H/'seat-envelope-study-v2.blend';assert sha(source2)==b['source_sha256'];plan=json.loads((R/'creative/research/seat-envelope/rear-piping-detail-plan-v3.json').read_text());assert plan['master_source_sha256']==b['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source2));sc=bpy.context.scene;col=bpy.data.collections[b['collection']];root=bpy.data.objects['SEAT_ENVELOPE_ESTIMATED_DATUM'];body=bpy.data.objects[b['object']];cage=bpy.data.objects['Editable seat envelope cage - estimated sections'];cage.hide_viewport=False;cage.hide_set(False);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();m=bpy.data.meshes.new_from_object(cage.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);m.calc_loop_triangles();N=len(m.vertices);assert max((body.data.vertices[i].co-m.vertices[i].co).length for i in range(N))==0
section=body.data.attributes.new('EXTERIOR_SECTION','INT','FACE');assert len(m.loop_triangles)*2+2*b['lower_boundary_segments']==len(body.data.polygons)
for k,t in enumerate(m.loop_triangles):
 assert tuple(body.data.polygons[2*k].vertices)==tuple(t.vertices)
 reg=m.attributes['SECTION_REGION'].data[t.polygon_index].value;section.data[2*k].value=reg;section.data[2*k+1].value=reg
for i in range(2*len(m.loop_triangles),len(body.data.polygons)):section.data[i].value=-1
adj=defaultdict(list)
for f in m.polygons:
 reg=m.attributes['SECTION_REGION'].data[f.index].value
 for e in f.edge_keys:adj[e].append(reg)
edges=[e for e,regs in adj.items()if set(regs)=={0,2}];graph=defaultdict(list)
for a,c in edges:graph[a].append(c);graph[c].append(a)
ends=[i for i,v in graph.items()if len(v)==1];assert len(ends)==2 and all(len(v)in[1,2]for v in graph.values());start=min(ends,key=lambda i:m.vertices[i].co.x);chain=[start];prev=None
while True:
 opts=[v for v in graph[chain[-1]]if v!=prev]
 if not opts:break
 prev=chain[-1];chain.append(opts[0])
assert len(chain)==len(edges)+1
points=[m.vertices[i].co.copy()for i in chain];norms=[m.vertex_normals[i].vector.copy().normalized()for i in chain];cage.hide_set(True);cage.hide_viewport=True;par=plan['authored_estimates_m'];dist=[0.]
for a,c in zip(points,points[1:]):dist.append(dist[-1]+(c-a).length)
def sample(s):
 k=next((k for k in range(len(dist)-1)if s<=dist[k+1]),len(dist)-2);t=(s-dist[k])/(dist[k+1]-dist[k]);p=points[k].lerp(points[k+1],t);n=norms[k].lerp(norms[k+1],t).normalized();tangent=(points[k+1]-points[k]).normalized();return p,n,tangent
# A tube mesh with finite caps and explicit per-corner normals/UV; no coincident pole.
def tube_mesh(name,paths,radius,cross=12,transport=False):
 vv=[];nn=[];ff=[];uv=[];region=[]
 def f(ids,xy,reg):ff.append(tuple(ids));uv.append(xy);region.append(reg)
 for path,normal_hints in paths:
  off=len(vv);ts=[];ns=[];bs=[];arc=[0.]
  for p,q in zip(path,path[1:]):arc.append(arc[-1]+(q-p).length)
  for k,p in enumerate(path):
   t=((path[min(k+1,len(path)-1)]-path[max(k-1,0)])).normalized();hint=(ts[-1].rotation_difference(t)@ns[-1])if transport and k else normal_hints[k];n=hint-t*hint.dot(t);n.normalize();bn=t.cross(n).normalized();ts.append(t);ns.append(n);bs.append(bn)
   for j in range(cross):
    normal=math.cos(2*math.pi*j/cross)*n+math.sin(2*math.pi*j/cross)*bn;vv.append(p+radius*normal);nn.append(normal)
  for k in range(len(path)-1):
   for j in range(cross):
    a=off+k*cross+j;c=off+(k+1)*cross+j;bb=off+k*cross+(j+1)%cross;d=off+(k+1)*cross+(j+1)%cross;s0=arc[k]/arc[-1];s1=arc[k+1]/arc[-1];v0=j/cross;v1=(j+1)/cross;f((a,bb,d),[(s0,v0),(s0,v1),(s1,v1)],0);f((a,d,c),[(s0,v0),(s1,v1),(s1,v0)],0)
  for end in [0,len(path)-1]:
   center=len(vv);vv.append(path[end]);nn.append(-ts[end]if end==0 else ts[end]);base=off+end*cross
   for j in range(cross):
    a=base+j;c=base+(j+1)%cross;xy=[(.5,.5),(.5+.5*math.cos(2*math.pi*j/cross),.5+.5*math.sin(2*math.pi*j/cross)),(.5+.5*math.cos(2*math.pi*(j+1)/cross),.5+.5*math.sin(2*math.pi*(j+1)/cross))];ids=(center,c,a)if end==0 else(center,a,c);f(ids,[xy[0],xy[2],xy[1]]if end==0 else xy,1)
 me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.update();ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.parent=root;me.materials.append(body.data.materials[0]);layer=me.uv_layers.new(name='Original tube parameter UV');custom=[]
 for p in me.polygons:
  p.use_smooth=region[p.index]==0
  for k,li in enumerate(p.loop_indices):layer.data[li].uv=uv[p.index][k];custom.append(tuple(nn[me.loops[li].vertex_index]if region[p.index]==0 else p.normal))
 me.normals_split_custom_set(custom);counts=Counter(tuple(sorted((a,b)))for f in ff for a,b in zip(f,f[1:]+f[:1]));vol=sum(sum((float(vv[a][i])-float(vv[0][i]))*((float(vv[bb][(i+1)%3])-float(vv[0][(i+1)%3]))*(float(vv[c][(i+2)%3])-float(vv[0][(i+2)%3]))-(float(vv[bb][(i+2)%3])-float(vv[0][(i+2)%3]))*(float(vv[c][(i+1)%3])-float(vv[0][(i+1)%3])))for i in range(3))/6 for a,bb,c in ff);areas=[p.area for p in me.polygons];print('TUBE_DIAG',name,min(areas),vol,sum(x!=2 for x in counts.values()));assert min(areas)>0 and vol>0 and all(x==2 for x in counts.values());return ob,{'name':name,'triangles':len(ff),'parts':len(paths),'minimum_area_m2':min(areas),'non_two_face_edges':sum(x!=2 for x in counts.values()),'material_volume_m3':vol}
# C1 chord-length Hermite path through every observed evaluated seam anchor.
# Densification changes only new piping geometry, not frozen cover or stitch placement.
raw_pipe=[p+par['piping_outward_center_offset']*n for p,n in zip(points,norms)];der=[]
for k,p in enumerate(raw_pipe):
 if k==0:der.append((raw_pipe[1]-p).normalized())
 elif k==len(raw_pipe)-1:der.append((p-raw_pipe[k-1]).normalized())
 else:
  d0=(p-raw_pipe[k-1]).length;d1=(raw_pipe[k+1]-p).length;der.append(((p-raw_pipe[k-1])*(d1/d0)+(raw_pipe[k+1]-p)*(d0/d1))/(d0+d1))
piping_path=[];pipe_hints=[];max_path_polyline_deviation=0.
for k in range(len(raw_pipe)-1):
 delta=(raw_pipe[k+1]-raw_pipe[k]).length
 for j in range(4):
  t=j/4;v=(2*t**3-3*t*t+1)*raw_pipe[k]+(t**3-2*t*t+t)*delta*der[k]+(-2*t**3+3*t*t)*raw_pipe[k+1]+(t**3-t*t)*delta*der[k+1];piping_path.append(v);pipe_hints.append(norms[k].lerp(norms[k+1],t).normalized());max_path_polyline_deviation=max(max_path_polyline_deviation,(v-raw_pipe[k].lerp(raw_pipe[k+1],t)).length)
piping_path.append(raw_pipe[-1]);pipe_hints.append(norms[-1]);pipe,pipe_report=tube_mesh('Observed related rear panel piping - estimated',[(piping_path,pipe_hints)],par['piping_radius'],transport=True);pipe['scope']='RelatedJV191001 visible rear arc; low continuation to cover cut edge estimated, no hidden full front seam';paths=[];projection_distances=[];outer_tris=[tuple(t.vertices)for t in m.loop_triangles];tree=BVHTree.FromPolygons([v.co for v in m.vertices],outer_tris,all_triangles=True);pitch=par['stitch_pitch'];count=int(dist[-1]/pitch)
for k in range(count):
 s=(k+.5)*dist[-1]/count;p,n,t=sample(s);toward=t.cross(n).normalized()
 if toward.y>0:toward=-toward
 center=p+par['stitch_surface_offset']*toward+n*.00012;path=[];hints=[]
 for j in range(9):
  q=j/8;target=center+t*(par['thread_length']*(q-.5));near,_,ti,dd=tree.find_nearest(target);ids=outer_tris[ti];nh=barycentric_transform(near,*[m.vertices[i].co for i in ids],*[m.vertex_normals[i].vector for i in ids]).normalized();projection_distances.append(dd);path.append(near+nh*(.00012+par['thread_raise']*math.sin(math.pi*q)));hints.append(nh)
 paths.append((path,hints))
stitches,stitch_report=tube_mesh('Rear piping stitch strands - estimated pitch',paths,par['thread_radius']);stitches['scope']='Original finite thread strand candidates, count/pitch/radius and current cover identity unknown';bpy.ops.object.select_all(action='DESELECT')
for obj in [body,pipe,stitches,root]:obj.select_set(True)
bpy.context.view_layer.objects.active=body;source=H/'seat-envelope-study-v3.blend';export=H/'seat-envelope-study-v3.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True);report={'schema':1,'source_sha256':sha(source),'export_sha256':sha(export),'master_source_sha256':b['source_sha256'],'master_export_sha256':b['export_sha256'],'builder_sha256':sha(Path(__file__)),'plan_sha256':sha(R/'creative/research/seat-envelope/rear-piping-detail-plan-v3.json'),'object':body.name,'objects':[body.name,pipe.name,stitches.name],'collection':col.name,'original_evaluated_boundary_segments':len(edges),'piping_centerline_length_authored_m':dist[-1],'piping_C1_anchor_count':len(raw_pipe),'piping_resampled_ring_count':len(piping_path),'max_path_interpolation_vs_polyline_deviation_m':max_path_polyline_deviation,'stitch_count_estimated':count,'thread_path_conforms_to_actual_outer_triangles':True,'max_actual_projection_distance_m':max(projection_distances),'new_objects':[pipe_report,stitch_report],'triangles':len(body.data.polygons)+pipe_report['triangles']+stitch_report['triangles'],'external_libraries':len(bpy.data.libraries),'external_images':[],'complete_seat':False,'art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(source2)==b['source_sha256'];print(json.dumps(report))
