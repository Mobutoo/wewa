"""ONE related exterior chain motif: plate, head envelopes and roller outer review skins. No hidden pins or repetition."""
import bpy,bmesh,math,json
from pathlib import Path
from math import pi,sin,cos,sqrt
R=Path('/workspace/wewa');key='front-completion-p22-chain-motif-v1';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);P=json.loads((R/'creative/research'/key/'G0-G2.json').read_text());(H/'parameters.json').write_text(json.dumps(P,indent=2));bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
mat=bpy.data.materials.new('Gray exterior motif review');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.25,.25,.25,1);bs.inputs['Roughness'].default_value=.3
pitch=.0127;half=pitch/2;radius=.0046;waist=.0026;th=.0013;objects=[]
def mesh(name,v,f,smooth):
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update();ob=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(ob);m.materials.append(mat)
 for p in m.polygons:p.use_smooth=smooth(p)
 objects.append(ob);return ob

def width(x):
 a=abs(x)
 if a>=half:return sqrt(max(0,radius*radius-(a-half)**2))
 t=a/half;return waist+(radius-waist)*(3*t*t-2*t*t*t)
outline=[];steps=256;extent=half+radius
for i in range(steps+1):x=-extent*cos(pi*i/steps);outline.append((x,width(x)))
for i in range(steps-1,0,-1):x=-extent*cos(pi*i/steps);outline.append((x,-width(x)))
outline.reverse();n=len(outline);v=[(x,y,z)for z in [0,th]for x,y in outline];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n)for j in range(n)];plate=mesh('ONE_WAISTED_EXTERIOR_PLATE_ESTIMATED',v,f,lambda p:p.index>=2)
for index,cx in enumerate([-half,half]):
 profile=[(.0021,th),(.0021,th+.00025),(.0019,th+.00055),(.0014,th+.00072),(.0007,th+.00079)];n=128;v=[];f=[]
 for r,z in profile:
  for j in range(n):a=2*pi*j/n;v.append((cx+r*cos(a),r*sin(a),z))
 for i in range(len(profile)-1):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
 for row,z,reverse in [(0,th,True),(len(profile)-1,th+.0008,False)]:
  c=len(v);v.append((cx,0,z))
  for j in range(n):a=row*n+j;b=row*n+(j+1)%n;f.append((c,b,a)if reverse else(c,a,b))
 mesh('VISIBLE_HEAD_ENVELOPE_'+str(index+1),v,f,lambda p:p.index<(len(profile)-1)*n or p.index>=(len(profile))*n)
 n=128;v=[(cx+.0038*cos(2*pi*j/n),.0038*sin(2*pi*j/n),z)for z in [-.0065,0]for j in range(n)];f=[(j,(j+1)%n,(j+1)%n+n,j+n)for j in range(n)];mesh('OPEN_ROLLER_EXTERIOR_REVIEW_SKIN_'+str(index+1),v,f,lambda p:True)
rows=[]
for ob in objects:
 m=ob.data;bm=bmesh.new();bm.from_mesh(m);m.calc_loop_triangles();skin='SKIN'in ob.name;row={'object':ob.name,'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'boundary_edges':sum(e.is_boundary for e in bm.edges),'branch_edges':sum(len(e.link_faces)>2 for e in bm.edges),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles),'expected_boundary_edges':256 if skin else 0}
 if not skin:row['volume_m3']=bm.calc_volume(signed=True);assert row['volume_m3']>0
 bm.free();assert row['boundary_edges']==row['expected_boundary_edges']and row['branch_edges']==0 and row['minimum_triangle_area_m2']>1e-18;rows.append(row)
plate_z=[v.co.z for v in plate.data.vertices];contacts=[]
for ob in objects:
 if ob==plate:continue
 zs=[v.co.z for v in ob.data.vertices]
 if 'HEAD'in ob.name:gap=min(zs)-max(plate_z)
 else:gap=min(plate_z)-max(zs)
 assert gap>=-1e-9;contacts.append({'object':ob.name,'signed_axial_clearance_to_plate_m':gap,'intended':'Exterior head-base or open roller-rim review-plane contact; no hidden joint inference'})
report={'objects':rows,'single_motif_only':True,'head_plate_and_roller_halfspace_contacts':contacts,'hidden_pin_shanks_bores_bushings_built':False,'functional_articulation_claimed':False,'all_metric_values_estimated':True};(O/'geometry-check.json').write_text(json.dumps(report,indent=2));bpy.ops.object.select_all(action='DESELECT')
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=plate;bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'motif-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'motif-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);print(report)
