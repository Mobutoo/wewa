"""Related PF401002 visible lead loop/branches/sleeves/rolled terminals; no pinout or mounted routing."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');key='front-completion-p09-leads-v1';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
P={'reference':'PF401002-173209 seller photo, visible loose harness below indicator','photo':'/workspace/wewa-assets/references/front-indicators-current-v1/PF401002-173209.jpg','frame':'isolated XY lay-flat review plane, +Y down photo; not mounted or rigid routing','jacket_radius_m':.0025,'radius_bounds_m':[.0018,.0035],'visible_loop_extent_m':.13,'extent_bounds_m':[.09,.18],'branch_radius_m':.00085,'sleeve_length_m':.010,'sleeve_length_bounds_m':[.007,.015],'sleeve_radius_m':.0022,'sleeve_radius_bounds_m':[.0016,.003],'terminal_length_m':.007,'terminal_length_bounds_m':[.004,.010],'terminal_radius_m':.0015,'terminal_radius_bounds_m':[.001,.0022],'all_dimensions_estimated':True,'terminal_shape':'exterior rolled/slit envelope, exact retention tongue and pinout not established','hidden_wire_conductor_or_pinout':'excluded','material':'gray first; black/gray insulation, green sleeves and brass-like ends are visual observations only'}
(H/'parameters.json').write_text(json.dumps(P,indent=2));reports=[]
def mesh(name,v,f,open_edges=0):
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update();ob=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(ob)
 for p in m.polygons:p.use_smooth=True
 m.set_sharp_from_angle(angle=.7);mat=bpy.data.materials.new('Gray '+name);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.25,.25,.25,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.35;m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);m.calc_loop_triangles();r={'object':name,'triangles':len(m.loop_triangles),'boundary_edges':sum(e.is_boundary for e in bm.edges),'branch_edges':sum(len(e.link_faces)>2 for e in bm.edges),'volume_m3':bm.calc_volume(signed=True),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles)};bm.free();assert r['boundary_edges']==open_edges and r['branch_edges']==0 and r['minimum_triangle_area_m2']>1e-18,(name,r);reports.append(r);return ob

def sweep(name,controls,radius):
 pts=[Vector(p)for p in controls];pts=[pts[0]]+pts+[pts[-1]];centres=[]
 for i in range(1,len(pts)-2):
  a,b,c,d=pts[i-1:i+3]
  for j in range(40):
   t=j/40;centres.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 centres.append(Vector(controls[-1]));v=[];f=[];n=48;last=None
 for i,c in enumerate(centres):
  tangent=(centres[min(i+1,len(centres)-1)]-centres[max(0,i-1)]).normalized();normal=tangent.cross(Vector((0,0,1))).normalized()if last is None else(last-tangent*last.dot(tangent)).normalized();last=normal;binormal=tangent.cross(normal).normalized()
  for j in range(n):a=2*math.pi*j/n;v.append(tuple(c+radius*(normal*math.cos(a)+binormal*math.sin(a))))
 for i in range(len(centres)-1):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
 mesh(name,v,f,2*n)

sweep('VISIBLE_BLACK_OUTER_JACKET_LOOP',[(0,0,0),(.018,.025,.001),(.020,.065,0),(-.015,.106,.003),(-.058,.121,0),(-.076,.103,.001),(-.052,.082,.002)],.0025)
branches=[([(-.052,.082,.002),(-.062,.077,.003),(-.073,.074,.004)],Vector((-.073,.074,.004)),Vector((-.85,-.52,0))),([(-.052,.082,.002),(-.027,.066,.003),(.003,.073,.002),(.024,.060,.003)],Vector((.024,.060,.003)),Vector((.65,-.76,0)))]
for k,(controls,origin,axis) in enumerate(branches):
 sweep('BRANCH_'+str(k+1)+'_INSULATION',controls,.00085);axis.normalize();a=axis.cross(Vector((0,0,1))).normalized();b=axis.cross(a).normalized()
 def lathe(name,profile,gap=0):
  n=96;v=[];f=[];count=n+1 if gap else n
  for z,r in profile:
   for j in range(count):
    angle=gap/2+(2*math.pi-gap)*j/(n if gap else n);v.append(tuple(origin+axis*z+r*(a*math.cos(angle)+b*math.sin(angle))))
  for i in range(len(profile)):
   for j in range(n):
    q=j+1 if gap else(j+1)%n;aa=i*count+j;bb=i*count+q;cc=((i+1)%len(profile))*count+q;dd=((i+1)%len(profile))*count+j;f.append((aa,bb,cc,dd))
  if gap:
   for j in [0,n]:
    f.append(tuple(i*count+j for i in (range(len(profile))if j==0 else reversed(range(len(profile))))))
  mesh(name,v,f)
 lathe('GREEN_SLEEVE_'+str(k+1)+'_GRAY_REVIEW',[(0,.0019),(.0005,.0022),(.0085,.0022),(.010,.0018),(.010,.0012),(.001,.0012),(0,.0013)])
 lathe('ROLLED_TERMINAL_'+str(k+1)+'_GRAY_REVIEW',[(.009,.0011),(.010,.00145),(.012,.00155),(.015,.00145),(.016,.0011),(.016,.00085),(.010,.00085)],.16)

bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.data.objects:
 if ob.type=='MESH':ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'leads-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'leads-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps({'objects':reports,'all_dimensions_estimated':True,'no_pinout_or_mounted_pose':True,'open_boundary_note':'Jacket and branch exteriors end at intentional review cuts; sleeves/rolled terminal walls are finite solids with open bores.'},indent=2))
