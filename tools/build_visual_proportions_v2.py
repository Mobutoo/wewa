"""Photo-guided chain line, headlamp depth and under-tank volumes. Metres, Blender axes.
Original component geometry is preserved; new identifiable exterior volumes are estimates.
"""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets-src/moto-components/visual-proportions-v2';REVIEW=ROOT/'creative/reviews/visual-proportions-v2'
plan=json.loads((ROOT/'creative/research/visual-proportions-v2/plan.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/plan['source_blend']));bpy.context.preferences.filepaths.save_version=0
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)));changes=[]
for c in plan['changes']:
 ob=bpy.data.objects[c['name']];before=ob.matrix_world.copy();p=Vector(c['pivot_blender_m'])
 delta=Matrix.Translation(Vector(c['translation_blender_m']))@Matrix.Translation(p)@Matrix.Rotation(math.radians(c['rotation_x_degrees']),4,'X')@Matrix.Diagonal((*c['scale'],1))@Matrix.Translation(-p)
 ob.matrix_world=delta@before
 changes.append({'name':ob.name,'delta_gltf':[list(r) for r in C@delta@C.inverted()],'before_blender':[list(r) for r in before],'after_blender':[list(r) for r in ob.matrix_world]})
bpy.context.view_layer.update()
def material(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
alloy=material('Upper rear crankcase cast aluminium',(.44,.47,.49),.72,.34)
black=material('Fork support black enamel',(.016,.020,.026),.5,.32)
plastic=material('Air cleaner neck polymer',(.022,.027,.032),0,.46)
rubber=material('Breather rubber',(.012,.015,.018),0,.65)
zinc=material('Carrier fastener zinc',(.4,.43,.45),.8,.28)
new=[];parents=[];current=None

def group(name):
 global current
 current=bpy.data.objects.new('PROPORTIONS ['+name+']',None);bpy.context.collection.objects.link(current);parents.append(current);new.append(current)
 current['provenance']='Official Bajaj RDC photographs; visually inferred envelope, no OEM dimensional claim'

def finish(ob,name,mat,bevel=.001):
 ob.name=name;ob.parent=current;ob.data.materials.append(mat);new.append(ob)
 if bevel:
  mod=ob.modifiers.new('Manufactured edge radius','BEVEL');mod.width=bevel;mod.segments=3
 for p in ob.data.polygons:p.use_smooth=True
 mod=ob.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 return ob

def loft(name,profile,sections,mat,bevel=.003):
 cy=sum(p[0] for p in profile)/len(profile);cz=sum(p[1] for p in profile)/len(profile)
 verts=[(x,cy+(y-cy)*s,cz+(z-cz)*s) for x,s in sections for y,z in profile];n=len(profile)
 faces=[tuple(reversed(range(n))),tuple((len(sections)-1)*n+i for i in range(n))]
 for k in range(len(sections)-1):
  for i in range(n):j=(i+1)%n;faces.append((k*n+i,k*n+j,(k+1)*n+j,(k+1)*n+i))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);return finish(ob,name,mat,bevel)

def cylinder(name,a,b,r,mat,verts=32,bevel=.0006):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=(b-a).length,location=(a+b)/2);ob=bpy.context.object;ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return finish(ob,name,mat,bevel)

def beam(name,a,b,width,thick,mat):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cube_add(size=1,location=(a+b)/2);ob=bpy.context.object;ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();ob.dimensions=(thick,width,(b-a).length);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(ob,name,mat)

def sleeve(name,a,b,ro,ri,mat):
 a,b=Vector(a),Vector(b);q=(b-a).to_track_quat('Z','Y');length=(b-a).length;n=48
 verts=[a+q@Vector((r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n),z)) for r,z in [(ro,0),(ro,length),(ri,length),(ri,0)] for i in range(n)]
 faces=[]
 for k in range(4):
  for i in range(n):j=(i+1)%n;faces.append((k*n+i,k*n+j,((k+1)%4)*n+j,((k+1)%4)*n+i))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);return finish(ob,name,mat,.0005)

# The two stamped chaincase halves need a recessed return behind their visible seam.
group('chaincase-inner-overlap-flange')
chainmat=material('Chaincase recessed return coating',(.48,.50,.53),.12,.42)
loft('Chaincase recessed joining return',[(.402,-.729),(.820,-.729),(.856,-.737),(.856,-.758),(.402,-.758)],[(.115,1),(.118,1)],chainmat,.001)
current.matrix_world=Matrix.Translation(Vector((0,.865,-.74)))@Matrix.Rotation(math.radians(-9),4,'X')@Matrix.Translation(Vector((0,-.865,.74)))
# 1. The upper rear casting joins the existing lower engine, below the carb bowl.
group('upper-rear-crankcase-shoulder')
profile=[(.163,-.563),(.187,-.528),(.214,-.512),(.234,-.493),(.262,-.491),(.285,-.507),(.330,-.509),(.355,-.537),(.347,-.583),(.265,-.582)]
loft('Upper rear crankcase continuous shoulder',profile,[(-.075,.90),(-.064,1),(.064,1),(.075,.90)],alloy,.005)
for side in [-1,1]:
 for i,(y,z) in enumerate([(.239,-.516),(.322,-.531)]):
  cylinder('Upper crankcase boss '+str(side)+' '+str(i),(side*.066,y,z),(side*.078,y,z),.010,alloy)
  cylinder('Upper crankcase bolt '+str(side)+' '+str(i),(side*.078,y,z),(side*.082,y,z),.005,zinc,6)
 beam('Casting reinforcement rib '+str(side),(side*.070,.205,-.553),(side*.070,.240,-.509),.009,.005,alloy)
# 2. Continue the existing air cleaner beneath the front edge of the side cover.
group('air-cleaner-lower-neck')
loft('Air cleaner lower continuous neck',[(.332,-.405),(.408,-.418),(.495,-.448),(.500,-.532),(.425,-.540),(.388,-.510),(.355,-.466)],[(-.066,.93),(-.056,1),(.061,1),(.071,.93)],plastic,.007)
for side in [-1,1]:cylinder('Air cleaner lower mounting screw '+str(side),(side*.063,.414,-.477),(side*.073,.414,-.477),.004,zinc,6)
cylinder('Crankcase breather boss',(.015,.298,-.531),(.015,.298,-.495),.014,alloy)
cylinder('Breather union to air cleaner',(.015,.298,-.495),(.015,.368,-.460),.008,rubber)
# 3. The official front fork carries long black headlamp support sleeves.
for side in [-1,1]:
 group('fork-headlamp-support-sleeve-'+str(side));x=side*.0875
 sleeve('Long black fork headlamp support '+str(side),(x,-.126,-.078),(x,-.230,-.307),.0225,.0163,black)
 sleeve('Fork sleeve upper collar '+str(side),(x,-.126,-.078),(x,-.1293,-.0853),.025,.0162,black)
 sleeve('Fork sleeve lower collar '+str(side),(x,-.2267,-.2997),(x,-.230,-.307),.025,.0162,black)
# Reprofile the existing cowl continuously; no separate overlapping cheek panel.
group('headlamp-cowl-reprofiled')
cowl=bpy.data.objects['PARENT [headlamp-cowl]']
replacement_names=[]
for original in list(cowl.children_recursive):
 if original.type!='MESH':continue
 mesh=original.data.copy();ob=bpy.data.objects.new('Reprofiled headlamp cowl shell',mesh);bpy.context.collection.objects.link(ob);ob.parent=current;ob.matrix_world=original.matrix_world.copy();new.append(ob);replacement_names.append(ob.name)
 original_positions=[v.co.copy() for v in mesh.vertices]
 original_normals=[n.vector.copy() for n in mesh.corner_normals]
 inv=ob.matrix_world.inverted();M=ob.matrix_world.to_3x3();Mi=M.inverted();normal_maps=[]
 def weight(v):
  t=max(0,min(1,v));return t*t*(3-2*t),6*t*(1-t) if 0<v<1 else 0
 for v in mesh.vertices:
  p=ob.matrix_world@v.co;wy,dy=weight((p.y+.322)/.142);wz,dz=weight((p.z+.202)/.064)
  J=Matrix(((1,0,0),(0,1,0),(0,.075*dy/.142*wz,1+.075*wy*dz/.064)))
  normal_maps.append((Mi@J@M).inverted().transposed())
  p.z+=.075*wy*wz;v.co=inv@p
 mesh.update()
 mesh.normals_split_custom_set([(normal_maps[loop.vertex_index]@original_normals[i]).normalized() for i,loop in enumerate(mesh.loops)])
for ob in [cowl,*list(cowl.children_recursive)]:ob.hide_render=True;ob.hide_set(True)
# 4. Lower black front carrier, visible on the exact official front view.
group('lower-front-carrier-bar')
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-.333,-.295));bar=bpy.context.object;bar.dimensions=(.254,.006,.033);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
finish(bar,'Lower headlamp front carrier bar',black,.007)
# Apply corner bevel before drilling to retain the rounded bar silhouette.
bpy.context.view_layer.objects.active=bar;bpy.ops.object.modifier_apply(modifier=bar.modifiers[0].name)
for x in [-.053,.053]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.0038,depth=.025,location=(x,-.333,-.295),rotation=(math.pi/2,0,0));cut=bpy.context.object
 bpy.context.view_layer.objects.active=bar;mod=bar.modifiers.new('Observed carrier fixing hole','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
for side in [-1,1]:beam('Lower carrier attachment '+str(side),(side*.088,-.209,-.272),(side*.088,-.330,-.295),.017,.004,black)
# 5. Tie the raised swingarm pivot to the existing central frame.
group('swingarm-pivot-frame-lugs')
for side in [-1,1]:
 x=side*.066
 loft('Pivot frame mounting cheek '+str(side),[(.297,-.604),(.357,-.617),(.377,-.638),(.338,-.677),(.310,-.665)],[(x-.0025,1),(x+.0025,1)],black,.002)
 cylinder('Pivot frame mounting spacer '+str(side),(side*.052,.356,-.632),(side*.080,.356,-.632),.012,black)

# Freeze only new surfaces before measuring/exporting; old source stays editable.
bpy.ops.object.select_all(action='DESELECT')
for ob in new:
 if ob.type=='MESH':ob.select_set(True)
bpy.context.view_layer.objects.active=next(ob for ob in new if ob.type=='MESH');bpy.ops.object.convert(target='MESH');checks=[]
for ob in new:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data)
 if ob.name not in replacement_names:
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data)
 row={'name':ob.name,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':abs(bm.calc_volume(signed=True))};checks.append(row);bm.free()
 if ob.name not in replacement_names:assert row['non_manifold_edges']==0 and row['volume_m3']>0,row
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'motorcycle-proportions.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for ob in new:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'proportion-additions-raw.glb'),export_format='GLB',use_selection=True,export_apply=True)
(REVIEW/'native-check.json').write_text(json.dumps({'changes':changes,'new_meshes':checks,'new_roots':[p.name for p in parents],'replacement_meshes':replacement_names,'deactivated_roots':plan['deactivated_roots'],'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
print('PROPORTIONS_NATIVE',len(changes),len(checks))
