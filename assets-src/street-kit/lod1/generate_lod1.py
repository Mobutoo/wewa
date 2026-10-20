import bpy,json,math,hashlib
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent
source=json.loads((BASE/'manifest.json').read_text());original={a['id']:a for a in source['assets'] if a['kind']=='facade'}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(BASE/'viva-wewa-street-kit.blend'),link=False) as (fr,to):to.materials=[m for m in fr.materials if m.startswith('VVK_')]
M={m.name:m for m in bpy.data.materials if m.name.startswith('VVK_')};C='VVK_concrete_CC0';S='VVK_painted_steel';G='VVK_dark_glass';W='VVK_weathered_wood';B='VVK_masonry'
assets=[];parts=[];coll=None

def xyz(p):return Vector((p[0],-p[2],p[1]))
def begin(n):
 global parts,coll
 parts=[];coll=bpy.data.collections.new(n);bpy.context.scene.collection.children.link(coll)
def finish(o,n,m):
 o.name=n;o.data.materials.append(M[m]);parts.append(o)
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);return o
def box(n,p,sc,m=C):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.dimensions=(sc[0],sc[2],sc[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,m)
def quad(n,points,m):
 me=bpy.data.meshes.new(n);me.from_pydata([xyz(p) for p in points],[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new(n,me);coll.objects.link(o);parts.append(o);o.data.materials.append(M[m]);return o
def rect(n,x,h,z,w,hh,m):return quad(n,[(x-w/2,h-hh/2,z),(x+w/2,h-hh/2,z),(x+w/2,h+hh/2,z),(x-w/2,h+hh/2,z)],m)
def beamface(n,x,h,z,w,hh,m=S):return rect(n,x,h,z,w,hh,m)
def window(x,h,z,w,hh,door=False):
 t=.05
 for xx in [x-w/2+t/2,x+w/2-t/2]:rect('LOD jamb',xx,h,z,t,hh,S)
 for yy in [h-hh/2+t/2,h+hh/2-t/2]:rect('LOD sill/lintel',x,yy,z,w,t,S)
 rect('LOD recessed glass',x,h,z-.035,w-2*t,hh-2*t,G)
 if door:rect('LOD centre mullion',x,h,z+.001,.045,hh,S)
def structural():
 for x in [-1.65,1.65]:box('Edge pier',(x,1.5,.005),(.1,3,.09))
 box('Top lintel',(0,2.95,.012),(3.2,.1,.12))
 # Bottom seam is a true visible face at Y0 and not a full backing slab.
 box('Bottom edge',(0,.04,.005),(3.2,.08,.08))
def sill(x,h,w,z=.095):box('Window sill',(x,h,z),(w,.055,.22))
def ac(x,h,z=.16):
 box('LOD AC cabinet',(x,h,z),(.52,.35,.26),S)
 rect('LOD AC dark grille',x,h,z+.143,.43,.26,G)
def shade(z=.17):box('Concrete sun hood',(0,2.62,z),(3.14,.10,.40))
def roller(x,h,w,hh,open=.999):
 # Few folds represented by a profile strip, not20 separate slats.
 top=h+hh/2;count=4;vs=[];fs=[]
 for j in range(count*2+1):
  yy=top-j*hh*open/(count*2);zz=.075+(.015 if j%2 else -.012)
  vs.extend([(x-w/2,yy,zz),(x+w/2,yy,zz)])
 for j in range(count*2):fs.append((2*j,2*j+1,2*j+3,2*j+2))
 me=bpy.data.meshes.new('LOD corrugation');me.from_pydata([xyz(p) for p in vs],[],fs);me.update();o=bpy.data.objects.new('LOD corrugation',me);coll.objects.link(o);o.data.materials.append(M[S]);parts.append(o)
def sign(w=2.6):box('LOD shop sign',(0,2.64,.10),(w,.32,.07),S)
def build(family,upper):
 name='facade_'+family+('_upper' if upper else '_ground');begin(name);structural()
 if family=='aged_office':
  for x in [-.79,.79]:window(x,1.58 if upper else 1.48,.09,1.25,1.82 if upper else 2.15,True);sill(x,.64 if upper else .40,1.38)
  shade()
  if upper:ac(.94,.37,.18)
 elif family=='tropical_apartment':
  if upper:
   window(0,1.70,.07,2.2,2.12,True)
   box('LOD balcony slab',(0,.37,.29),(2.85,.09,.62))
   # Front and side rail strips preserve the .60m balcony silhouette with much fewer polygons.
   rect('Balcony top railing',0,1.32,.5925,2.82,.035,S)
   rect('Balcony lower railing',0,.47,.5925,2.82,.025,S)
   for j in range(7):rect('LOD baluster',-1.34+j*2.68/6,.895,.5925,.026,.83,S)
   for x in [-1.38,1.38]:quad('Balcony end rail',[(x,.47,.045),(x,.47,.595),(x,1.32,.595),(x,1.32,.045)],S)
  else:
   box('Entrance door',(-.95,1.20,.025),(.88,2.25,.065),W)
   window(.55,1.65,.09,1.65,1.45);sill(.55,.90,1.8)
   for y in [.34,.48,.62]:rect('Vent block line',.55,y,.08,1.54,.035,B)
  box('Roof shade',(0,2.77,.19),(3.16,.10,.42))
 elif family=='retail_shutter':
  if upper:
   for x in [-.81,.81]:window(x,1.70,.09,1.30,1.5);sill(x,.91,1.39)
   rect('Masonry spandrel',0,.48,.065,3.18,.66,B)
   o=box('Sloped metal awning',(0,2.61,.21),(3.12,.045,.44),S);o.rotation_euler.x=-.14
  else:
   roller(0,1.22,2.92,2.22);sign()
   box('Raised threshold',(0,.10,.13),(3,.08,.25))
 elif family=='workshop':
  if upper:
   window(0,1.65,.09,2.92,1.64)
   for x in [-.99,0,.99]:rect('Industrial mullion',x,1.65,.10,.03,1.60,S)
   rect('Industrial transom',0,1.66,.10,2.89,.035,S)
   sill(0,.79,3.10);rect('Masonry infill',0,.39,.065,3.18,.68,B);ac(1.02,2.66,.16)
  else:
   roller(-.42,1.25,2.02,2.25,.62);window(1.10,1.73,.08,.77,1.15)
   box('Service counter',(1.10,1.12,.17),(.86,.07,.35),W);sign(2.82)
 elif family=='compound_gate':
  if upper:
   for x in [-1.5,1.5]:box('Masonry pier',(x,1.45,.02),(.20,2.8,.12),B)
   for h in [.24,2.76]:box('Coping',(0,h,.06),(3.10,.08,.18))
   for h in [.65,1.5,2.35]:rect('Screen horizontal',0,h,.08,2.8,.04,B)
   for j in range(6):rect('Screen vertical',-1.4+j*.56,1.5,.08,.04,2.30,B)
  else:
   for x in [-1.47,1.47]:box('Gate masonry pier',(x,1.33,.045),(.26,2.58,.18),B)
   for x in [-.655,.655]:
    rect('Lower gate panel',x,.74,.1025,1.27,1.22,S)
    rect('Upper gate rail',x,2.42,.10,1.27,.04,S)
    for j in range(4):rect('Gate upright',x-.5+j/3,1.87,.10,.02,1.06,S)
   box('Gate latch',(.07,1.25,.115),(.16,.045,.05),S)
 elif family=='louvered_office':
  window(0,1.50,.025,3,2.75)
  if upper:
   # Four deeper fins preserve edge, depth and rhythm; fine fins omitted at distance.
   for x in [-1.35,-.45,.45,1.35]:
    o=box('LOD vertical fin',(x,1.5,.1692783),(.055,2.75,.37));o.rotation_euler.z=.12
   sill(0,.10,3.1,.14)
  else:
   for j in range(5):
    o=box('LOD horizontal shade',(0,.24+j*2.45/4,.15),(2.99,.045,.35));o.rotation_euler.x=.12
   box('Entrance pull',(1.08,1.38,.37),(.025,.42,.025),S)
 export(name)

def uv_physical(o):
 uv=o.data.uv_layers.new(name='Surface_2m').data
 for p in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]))
  for li in p.loop_indices:
   v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
   a,b=(v.y,v.z) if axis==0 else ((v.x,v.z) if axis==1 else (v.x,v.y));uv[li].uv=(a/2,b/2)
def export(name):
 source_parts=list(parts);groups={}
 for o in source_parts:groups.setdefault(o.data.materials[0].name,[]).append(o)
 exports=[]
 for mat,items in groups.items():
  clones=[]
  for o in items:
   d=o.copy();d.data=o.data.copy();bpy.context.scene.collection.objects.link(d);clones.append(d)
  bpy.ops.object.select_all(action='DESELECT')
  for d in clones:d.select_set(True)
  bpy.context.view_layer.objects.active=clones[0]
  if len(clones)>1:bpy.ops.object.join()
  o=bpy.context.object;o.name='lod1_'+name+'__'+mat;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  mod=o.modifiers.new('LOD topology triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);uv_physical(o);o.data.calc_loop_triangles();exports.append(o)
 tri=sum(len(o.data.loop_triangles) for o in exports);assert tri<=180,(name,tri)
 bpy.context.view_layer.update();vs=[o.matrix_world@Vector(v) for o in exports for v in o.bound_box];gv=[(v.x,v.z,-v.y) for v in vs]
 lo=[min(v[i] for v in gv) for i in range(3)];hi=[max(v[i] for v in gv) for i in range(3)];old=original[name]
 for i in range(3):
  assert abs(lo[i]-old['bounds_m']['min'][i])<.0001,(name,'min',lo,old['bounds_m'])
  assert abs(hi[i]-old['bounds_m']['max'][i])<.0001,(name,'max',hi,old['bounds_m'])
 bpy.ops.object.select_all(action='DESELECT')
 for o in exports:o.select_set(True)
 filepath=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(filepath),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_tangents=True,export_cameras=False,export_lights=False)
 assets.append({'id':name,'file':name+'.glb','lod':1,'node_prefix':'lod1_'+name+'__','triangles':tri,'triangles_lod0':old['triangles'],'bounds_m':{'min':[round(x,5) for x in lo],'max':[round(x,5) for x in hi]},'dimensions_m':old['dimensions_m'],'front':[0,0,1],'up':[0,1,0],'origin':old['origin'],'materials':list(groups),'sha256':hashlib.sha256(filepath.read_bytes()).hexdigest(),'bytes':filepath.stat().st_size,'family':old['family'],'level':old['level']})
 for o in exports:bpy.data.objects.remove(o,do_unlink=True)
 root=bpy.data.objects.new(name+'__EDITABLE_LOD1',None);coll.objects.link(root)
 for o in source_parts:o.parent=root
 i=len(assets)-1;root.location=(i%6*4.15,0,(i//6)*3.7)

for upper in [False,True]:
 for family in ['aged_office','tropical_apartment','retail_shutter','workshop','compound_gate','louvered_office']:build(family,upper)
manifest={'library':'Viva Wewa architecture LOD1','version':1,'source_lod0_manifest':'../manifest.json','intended_distance_m':[45,180],'coordinate_system':source['coordinate_system'],'construction':'Original manual Blender retopology with intact frame/glass and simplified rails/louvers; not automatic silhouette collapse.','bounds_contract':'All12LOD1 preserve the corresponding LOD0 bounds, dimensions, origin, facing and metre units.','materials':'Exact material datablocks loaded from original editable .blend; concrete world UV scale remains2m.','triangle_budget_each':180,'geometry_license':source['geometry_license'],'textures':source['textures'],'acceptance_limit':'Distant geometry optimization only. No new survey or photographic acceptance.','assets':assets}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
# Actual Blender contact sheet.
for loc,energy,size in [((5,-5,13),2400,9),((20,-4,10),2200,8),((10,5,11),1800,7)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.size=size;o.rotation_euler=(Vector((10,0,3))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(10.4,-23,11));c=bpy.context.object;c.rotation_euler=(Vector((10.4,0,3.2))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=25.8
s=bpy.context.scene;s.camera=c;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=2600;s.render.resolution_y=1150;s.render.resolution_percentage=100;s.render.filepath=str(OUT/'lod1-preview.png');s.world.color=(.3,.3,.3);s.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'viva-wewa-facades-lod1.blend'));bpy.ops.render.render(write_still=True)
print('LOD1_COMPLETE',sum(a['triangles'] for a in assets))
