"""Observable upholstery envelope only: authored section cage, no hidden seat base."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/seat-envelope-study-v1';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=json.loads((H/'parameters-study-v1.json').read_text());S=P['stations'];C=P['cross_profile']
assert (R/'creative/research/seat-envelope/section-and-comparison-plan-v1.json').exists()
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.cycles.denoiser='OPENIMAGEDENOISE';sc.render.threads_mode='FIXED';sc.render.threads=1
col=bpy.data.collections.new('WEWA_SEAT_ENVELOPE_STUDY');sc.collection.children.link(col);guides=bpy.data.collections.new('SEAT_EDITABLE_SECTION_CAGE_NOT_EXPORTED');sc.collection.children.link(guides);guides.hide_render=True
root=bpy.data.objects.new('SEAT_ENVELOPE_ESTIMATED_DATUM',None);col.objects.link(root)
vs=[];fs=[];fuv=[];ns=len(S['u']);cross=[(-1,i)for i in range(len(C['s'])-1,0,-1)]+[(1,i)for i in range(len(C['s']))];nr=len(cross)
for k in range(ns):
 for side,j in cross:
  f=C['height_fraction'][j];w=S['halfwidth_left'if side<0 else'halfwidth_right'][k];vs.append((side*w*C['halfwidth_fraction'][j],S['y'][k]+S['nose_lower_sweep_y'][k]*(1-f),S['lower_z'][k]+(S['top_z'][k]-S['lower_z'][k])*f))
for k in range(ns-1):
 for j in range(nr-1):
  a=k*nr+j;b=a+1;c=a+nr;d=c+1;fs.append((a,b,d,c));fuv.append([(S['u'][k],j/(nr-1)),(S['u'][k],(j+1)/(nr-1)),(S['u'][k+1],(j+1)/(nr-1)),(S['u'][k+1],j/(nr-1))])
for end in [0,ns-1]:
 ids=list(range(end*nr,(end+1)*nr));ids=ids[::-1]if end==0 else ids;fs.append(ids);w=max(S['halfwidth_left'][end],S['halfwidth_right'][end]);z0=S['lower_z'][end];hh=S['top_z'][end]-z0;fuv.append([(.5+vs[i][0]/(2*w),(vs[i][2]-z0)/hh)for i in ids])
me=bpy.data.meshes.new('Authored variable upholstery section cage');me.from_pydata(vs,[],fs);me.update();ca=bpy.data.objects.new('Editable seat envelope cage - estimated sections',me);guides.objects.link(ca);ca.hide_render=True
uv=me.uv_layers.new(name='Original seat parameter UV')
for poly,coords in zip(me.polygons,fuv):
 poly.use_smooth=True
 for li,xy in zip(poly.loop_indices,coords):uv.data[li].uv=xy
mod=ca.modifiers.new('Continuous upholstered rolls from section cage','SUBSURF');mod.subdivision_type='CATMULL_CLARK';mod.levels=P['subdivision_levels'];mod.render_levels=mod.levels;mod.uv_smooth='PRESERVE_BOUNDARIES';bpy.context.view_layer.update();ev=ca.evaluated_get(bpy.context.evaluated_depsgraph_get());m=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get());m.calc_loop_triangles();v=[x.co.copy()for x in m.vertices];norm=[x.vector.copy().normalized()for x in m.vertex_normals];n=len(v);v +=[v[i]-P['skin_thickness_m']*norm[i]for i in range(n)];faces=[];uvs=[];regions=[]
def face(ids,coords,reg):faces.append(tuple(ids));uvs.append(coords);regions.append(reg)
edge={};counts=Counter()
for t in m.loop_triangles:
 ids=list(t.vertices);coords=[tuple(m.uv_layers.active.data[l].uv)for l in t.loops];face(ids,coords,0);face([n+i for i in ids[::-1]],coords[::-1],1)
 for a,b in zip(ids,ids[1:]+ids[:1]):counts[tuple(sorted((a,b)))]+=1;edge[tuple(sorted((a,b)))]=(a,b)
boundary=[edge[k]for k,c in counts.items()if c==1]
for k,(a,b)in enumerate(boundary):
 s0=k/len(boundary);s1=(k+1)/len(boundary);face((a,n+b,b),[(s0,0),(s1,1),(s1,0)],2);face((a,n+a,n+b),[(s0,0),(s0,1),(s1,1)],2)
mesh=bpy.data.meshes.new('Finite seat cover skin - lower boundary open in scope');mesh.from_pydata(v,[],faces);mesh.update();ob=bpy.data.objects.new('Seat outer upholstered envelope - estimated',mesh);col.objects.link(ob);ob.parent=root;layer=mesh.uv_layers.new(name='Original seat parameter UV');normals=[]
for poly in mesh.polygons:
 poly.use_smooth=regions[poly.index]<2
 for j,li in enumerate(poly.loop_indices):
  layer.data[li].uv=uvs[poly.index][j];vi=mesh.loops[li].vertex_index;normals.append(tuple(norm[vi]if regions[poly.index]==0 else -norm[vi-n]if regions[poly.index]==1 else poly.normal))
mesh.normals_split_custom_set(normals);reg=mesh.attributes.new('COVER_SKIN_REGION','INT','FACE')
for i,x in enumerate(regions):reg.data[i].value=x
mat=bpy.data.materials.new('Neutral seat gray inspection - not black vinyl');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.32;mesh.materials.append(mat)
ob['scope']='Finite upper/side/front/rear upholstery skin. Lower perimeter is declared cut boundary. No internal foam/base/mount.';ob['dimensions']='All sections and1.2mm skin are authored estimates, not measured seat dimensions';ob['variant']='Current RDC exterior target, relatedJV191001 does not certify current underside or embossing';ca.hide_set(True);ca.hide_viewport=True
world=bpy.data.worlds.new('Neutral seat study studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);world.node_tree.nodes['Background'].inputs[1].default_value=.3;sc.world=world
for name,loc,power,size in [('Key',(-.6,.25,.6),65,.7),('Fill',(.75,.8,.35),35,.6),('Rear strip',(.10,1.45,.55),45,.35)]:
 light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='RECTANGLE';light.size=size;light.size_y=.18 if name=='Rear strip'else size;obj=bpy.data.objects.new(name,light);sc.collection.objects.link(obj);obj.location=loc;obj.rotation_euler=(Vector((0,.7,-.21))-obj.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Seat study camera');co=bpy.data.objects.new('Seat study camera',cam);sc.collection.objects.link(co);co.location=(-1.35,-.10,.85);co.rotation_euler=(Vector((0,.7,-.21))-co.location).to_track_quat('-Z','Y').to_euler();cam.type='PERSP';cam.lens=60;cam.sensor_fit='HORIZONTAL';cam.sensor_width=36;cam.clip_start=.001;cam.clip_end=20;sc.camera=co;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=ob;source=H/'seat-envelope-study-v1.blend';export=H/'seat-envelope-study-v1.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
area=[p.area for p in mesh.polygons];edges=Counter(tuple(sorted((a,b)))for f in faces for a,b in zip(f,f[1:]+f[:1]));volume=sum(Vector(v[a]).dot(Vector(v[b]).cross(Vector(v[c])))/6 for a,b,c in faces);report={'schema':1,'source_sha256':sha(source),'export_sha256':sha(export),'builder_sha256':sha(Path(__file__)),'parameters_sha256':sha(H/'parameters-study-v1.json'),'object':ob.name,'collection':col.name,'construction_collection':guides.name,'control_cage_vertices':len(vs),'evaluated_outer_vertices':n,'vertices':len(v),'triangles':len(faces),'minimum_triangle_area_m2':min(area),'exact_zero_area_triangles':sum(a==0 for a in area),'non_two_face_edges':sum(x!=2 for x in edges.values()),'wall_material_volume_m3':volume,'volume_is':'Estimated skin material, not foam volume or certified seat capacity','lower_boundary_segments':len(boundary),'external_libraries':len(bpy.data.libraries),'external_images':[],'source_closed_material_wall':True,'complete_seat':False,'actual_dimensions_measured':False,'art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');assert min(area)>0 and volume>0 and report['non_two_face_edges']==0;print(json.dumps(report))
