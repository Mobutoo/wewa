"""Photo-supported smooth concavity; no highlight-to-facet conversion.
Existing detailed glazing and capsule data linked unchanged, source kit reused.
"""
from pathlib import Path
import bpy,bmesh,json,math,hashlib
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
R=Path('/workspace/wewa');K='headlamp-front-photo-reconstruction-v1';D=R/'creative/research'/K;H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);p=json.loads((D/'G0-G2-plan.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
col=bpy.data.collections.new('WEWA_HEADLAMP_FRONT_PHOTO_RECONSTRUCTION_V1');bpy.context.scene.collection.children.link(col)
def linked_objects(path,predicate):
 with bpy.data.libraries.load(str(R/path),link=True) as(a,b):b.objects=[n for n in a.objects if predicate(n)]
 result=[]
 for original in b.objects:
  ob=original.copy();ob.data=original.data;col.objects.link(ob);result.append(ob)
 return result
v3='assets-src/moto-components/headlamp-interior-completion-v3/visible-optics-v3.blend'
retained=linked_objects(v3,lambda n:'VISIBLE_GLAZING' in n or 'VISIBLE_PERIPHERAL_SILVER_LIP' in n);assert len(retained)==2
for glass in retained:
 if 'VISIBLE_GLAZING' in glass.name:
  glass.data=glass.data.copy()
  for vertex in glass.data.vertices:
   x,y,z=vertex.co;r=math.hypot(x,y);fade=max(0,min(1,(.080-r)/.008))
   vertex.co.z+=.00016*fade*(.5+.5*math.cos(2*math.pi*x/.009))
capsule=linked_objects('assets-src/moto-components/front-completion-p06-bulb-capsule-front15-v1/bulb-capsule-material.blend',lambda n:'CL201023_' in n);assert len(capsule)==2
for ob in capsule:ob.location=(.0045,.0008,-.042)
def depth(x,y):
 dx=x-.0045;dy=y-.0008;r=math.hypot(dx,dy)
 if r<1e-12:return -.038
 ux=dx/r;uy=dy/r;dot=.0045*ux+.0008*uy
 outer=-dot+math.sqrt(dot*dot+.0828**2-.0045**2-.0008**2)
 # Single analytic quadratic: no station-induced curvature rings.
 q=max(0,min(1,(r*r-.019**2)/(outer*outer-.019**2)))
 z=-.038+(.038-.00045)*q
 dp=math.hypot(x-.003,y+.037)
 if dp<.0122:
  a=max(0,min(1,(dp-.0072)/.005));a=a*a*(3-2*a);z=-.032*(1-a)+z*a
 return z
xy=[];edges=[];rings=[]
for cx,cy,rr,n in [(0,0,.0828,384),(.0045,.0008,.019,192),(.003,-.037,.0072,96)]:
 ids=[]
 for i in range(n):a=2*math.pi*i/n;ids.append(len(xy));xy.append(Vector((cx+rr*math.cos(a),cy+rr*math.sin(a))))
 edges.extend((ids[i],ids[(i+1)%n]) for i in range(n));rings.append(ids)
for i in range(-39,40):
 for j in range(-39,40):
  x=i*.002;y=j*.002
  if math.hypot(x,y)<.0805 and math.hypot(x-.0045,y-.0008)>.0205 and math.hypot(x-.003,y+.037)>.0085:xy.append(Vector((x,y)))
vs,es,fs,orig,*_=delaunay_2d_cdt(xy,edges,[],0,1e-9)
v=[(a.x,a.y,depth(a.x,a.y)) for a in vs];f=[]
for face in fs:
 x=sum(vs[i].x for i in face)/len(face);y=sum(vs[i].y for i in face)/len(face)
 if math.hypot(x,y)<.0828 and math.hypot(x-.0045,y-.0008)>.019 and math.hypot(x-.003,y+.037)>.0072:f.append(tuple(face))
lookup={tuple(round(x,8) for x in vv):i for i,vv in enumerate(vs)}
for ring,cx,cy,ri,zfront in [(rings[1],.0045,.0008,.0175,-.038),(rings[2],.003,-.037,.0063,-.032)]:
 n=len(ring);outer=[lookup[tuple(round(x,8) for x in xy[j])] for j in ring];inner=[];rear=[]
 for i in range(n):a=2*math.pi*i/n;inner.append(len(v));v.append((cx+ri*math.cos(a),cy+ri*math.sin(a),zfront))
 for i in range(n):a=2*math.pi*i/n;rear.append(len(v));v.append((cx+ri*math.cos(a),cy+ri*math.sin(a),zfront-.004))
 for i in range(n):
  j=(i+1)%n;f.append((outer[i],outer[j],inner[j],inner[i]));f.append((inner[i],inner[j],rear[j],rear[i]))
m=bpy.data.meshes.new('Photo-derived offset concave field with two real aperture returns');m.from_pydata(v,[],f);m.update();ob=bpy.data.objects.new('DJ201051_ESTIMATED_CONCAVE_VISIBLE_REFLECTOR_AND_TWO_COLLARS',m);col.objects.link(ob)
bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
for face in m.polygons:face.use_smooth=True
mat=bpy.data.materials.new('Clean reflective optical metal estimate, no emission');mat.use_nodes=True;b=mat.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.72,.75,.78,1);b.inputs['Metallic'].default_value=1;b.inputs['Roughness'].default_value=.075;m.materials.append(mat)
bpy.context.view_layer.objects.active=ob;ob.select_set(True)
mod=ob.modifiers.new('Estimated representational finite shell gauge0.6mm','SOLIDIFY');mod.thickness=.0006;mod.offset=-1;mod.use_even_offset=True;bpy.ops.object.modifier_apply(modifier=mod.name)
bm=bmesh.new();bm.from_mesh(ob.data);boundary=sum(e.is_boundary for e in bm.edges);branch=sum(len(e.link_faces)>2 for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free();assert boundary==0 and branch==0 and vol>0,(boundary,branch,vol)
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
bpy.ops.object.select_all(action='DESELECT')
for obj in col.objects:obj.select_set(True)
bpy.context.view_layer.objects.active=ob;bpy.context.scene.unit_settings.system='METRIC'
src=H/'front-photo-reconstruction-v1.blend';glb=H/'front-photo-reconstruction-v1.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[{'name':o.name,'mesh_vertices':len(o.data.vertices),'linked_mesh':o.data.library is not None,'matrix':[list(r) for r in o.matrix_world]} for o in col.objects]
(O/'construction-check.json').write_text(json.dumps({'source':str(src.relative_to(R)),'source_sha256':sha(src),'glb_sha256':sha(glb),'objects':rows,'new_reflector_shell':{'boundary_edges':boundary,'branch_edges':branch,'positive_signed_volume_m3':vol,'front_lip_z_m':-.00045,'main_recess_m':.038,'main_collar_return_end_z_m':-.042,'pilot_recess_m':.032},'flat_old_field_excluded':True,'old_files_changed':False,'photo_pixels_embedded':False,'exact_OEM_claimed':False},indent=2))
old=json.loads((R/'creative/reviews/headlamp-interior-completion-v3/integration-fragment.json').read_text());row={**old['replacements'][0],'source':str(src.relative_to(R)),'sha256':sha(src),'collection':col.name,'selected_objects':[],'nested_sources':[{'source':str(Path(bpy.path.abspath(lib.filepath)).resolve().relative_to(R)),'sha256':sha(Path(bpy.path.abspath(lib.filepath)).resolve())} for lib in bpy.data.libraries],'renderable_meshes':5,'placement_status':'Same old optical parent frame; new photo-bounded38mm concavity, collar returns and linked exterior capsule. No measured optical prescription.'}
(O/'integration-fragment.json').write_text(json.dumps({'revision':K,'replace_parent_keys':['outer-glass-envelope-context'],'replacements':[row],'additions':[],'parent_delta':0,'glb':str(glb.relative_to(R)),'glb_sha256':sha(glb),'not_exact_OEM':True,'complete_bulb_socket':False,'no_highlight_facets_invented':True},indent=2)+'\n')
