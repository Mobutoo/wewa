"""Apply explicit registrations to an editable native copy and build estimated mounts.
Blender coordinates throughout: X left, Y rear, Z up; metres.
"""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets-src/moto-components/assembly-alignment-v1'
REVIEW=ROOT/'creative/reviews/assembly-alignment-v1'
plan=json.loads((ROOT/'creative/research/assembly-alignment-v1/plan.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/plan['source_blend']))
bpy.context.preferences.filepaths.save_version=0
changes=[]
# Axis conversion Blender -> glTF: (x,z,-y).
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
for c in plan['changes']:
 ob=bpy.data.objects[c['name']];before=ob.matrix_world.copy()
 pivot=Vector(c['pivot_blender_m']);scale=Matrix.Diagonal((*c['scale'],1))
 delta=Matrix.Translation(Vector(c['translation_blender_m']))@Matrix.Translation(pivot)@scale@Matrix.Translation(-pivot)
 ob.matrix_world=delta@before
 changes.append({'name':ob.name,'delta_gltf':[list(r) for r in C@delta@C.inverted()], 'before_blender':[list(r) for r in before], 'after_blender':[list(r) for r in ob.matrix_world]})
bpy.context.view_layer.update()
visor_mat=bpy.data.materials.get(plan['material_change']['name'])
assert visor_mat is not None
bs=visor_mat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Transmission Weight'].default_value=0
bs.inputs['Base Color'].default_value=plan['material_change']['base_color']
bs.inputs['Roughness'].default_value=plan['material_change']['roughness']
mat=bpy.data.materials.new('Alignment mounts - satin black steel');mat.diffuse_color=(.027,.032,.038,1);mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Metallic'].default_value=.65;bs.inputs['Roughness'].default_value=.37
rubber=bpy.data.materials.new('Seat support rubber');rubber.diffuse_color=(.018,.020,.023,1);rubber.use_nodes=True
rubber.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=rubber.diffuse_color
rubber.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.7
new=[];connections=[]
def group(name):
 ob=bpy.data.objects.new('ALIGNMENT ['+name+']',None);bpy.context.collection.objects.link(ob);new.append(ob);return ob

def finish(ob,name,parent,material=mat,bevel=.001):
 ob.name=name;ob.data.materials.append(material);ob.parent=parent;new.append(ob)
 if bevel:
  m=ob.modifiers.new('Small edge radius','BEVEL');m.width=bevel;m.segments=3
  m=ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return ob

def beam(name,a,b,width,thick,parent,material=mat):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cube_add(size=1,location=(a+b)/2);ob=bpy.context.object
 ob.rotation_mode='QUATERNION';ob.rotation_quaternion=(b-a).to_track_quat('Z','Y');ob.dimensions=(thick,width,(b-a).length)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 connections.append({'part':name,'a_blender_m':list(a),'b_blender_m':list(b),'length_m':(b-a).length,'status':'estimated_visual_mount'})
 return finish(ob,name,parent,material)

def pin(name,a,b,r,parent):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=(b-a).length,location=(a+b)/2)
 ob=bpy.context.object;ob.rotation_mode='QUATERNION';ob.rotation_quaternion=(b-a).to_track_quat('Z','Y')
 for p in ob.data.polygons:p.use_smooth=True
 return finish(ob,name,parent,bevel=.0005)

def gusset(name,points,thick,parent):
 # Extruded triangular bracket in the YZ plane.
 verts=[(p[0]+dx,p[1],p[2]) for dx in [-thick/2,thick/2] for p in points]
 faces=[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
 return finish(ob,name,parent)

def closest_surface(group_name,point):
 ob=bpy.data.objects['PARENT ['+group_name+']'];best=None
 for child in ob.children_recursive:
  if child.type!='MESH':continue
  verts=[child.matrix_world@v.co for v in child.data.vertices]
  tree=BVHTree.FromPolygons(verts,[list(p.vertices) for p in child.data.polygons])
  hit=tree.find_nearest(Vector(point))
  if hit and hit[0] is not None and (best is None or hit[3]<best[3]):best=hit
 assert best is not None
 return best[0]

for side in [-1,1]:
 g=group('headlamp-stays-'+str(side));x=side*.0875
 beam('Upper fork-to-lamp stay '+str(side),(x,-.126,-.065),(x,-.254,-.065),.020,.005,g)
 beam('Lower fork-to-lamp stay '+str(side),(x,-.177,-.240),(x,-.289,-.240),.020,.005,g)
 for y,z in [(-.126,-.065),(-.177,-.240),(-.254,-.065),(-.289,-.240)]:
  pin('Headlamp stay bolt',(x-.009,y,z),(x+.009,y,z),.0055,g)
 g=group('peg-support-continuation-'+str(side))
 x0=side*.096
 frame='frame-seat-rail-observed' if side==1 else 'PROVISIONAL opposite frame-seat-rail-observed'
 guard=('LH' if side==1 else 'RH')+' CURRENT_RDC rear-sideguard observed'
 pin('Peg support upper continuation '+str(side),closest_surface(frame,(x0,.600,-.367)),(side*.096,.600,-.440),.008,g)
 pin('Peg support lower continuation '+str(side),(side*.141,.651 if side==1 else .666,-.587),closest_surface(guard,(side*.180,.680,-.634)),.008,g)
 g=group('seat-buffer-'+str(side));x=side*.09
 beam('Seat underside rubber buffer '+str(side),(x,.594,-.365),(x,.594,-.301),.028,.026,g,rubber)
 g=group('shock-upper-mount-'+str(side));x=side*.112
 gusset('Frame to upper shock triangular mount '+str(side),[(x,.735,-.343),(x,.825,-.308),(x,.7516,-.4285)],.006,g)
 pin('Upper shock pivot '+str(side),(side*.103,.7516,-.4285),(side*.145,.7516,-.4285),.008,g)
 g=group('rear-light-carrier-'+str(side));x=side*.08
 beam('Rack to lamp carrier '+str(side),(x,1.176,-.106),(x,1.176,-.275),.025,.005,g)
 beam('Rear indicator carrier arm '+str(side),(x,1.176,-.280),(side*.110,1.130,-.280),.018,.005,g)
 pin('Rear indicator mounting spindle '+str(side),(side*.078,1.130,-.280),(side*.114,1.130,-.280),.0075,g)
# The transverse bracket connects both lamp stays to the plate's retained upper bracket.
g=group('rear-light-crossmember')
beam('Rear light carrier transverse bridge',(-.086,1.176,-.272),(.086,1.176,-.272),.022,.005,g)
bpy.ops.object.select_all(action='DESELECT')
for ob in new:ob.select_set(True)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'motorcycle-aligned.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'alignment-mounts.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True)
report={'changes':changes,'new_objects':[o.name for o in new],'connections':connections,'estimated_mounts':True,'source_blend':plan['source_blend'],'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(REVIEW/'native-check.json').write_text(json.dumps(report,indent=2)+'\n')
print('ALIGNMENT_NATIVE',len(changes),len(new))
