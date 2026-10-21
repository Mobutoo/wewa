"""Related14T outer-rim hypothesis with two OPEN inner review boundaries; no inferred drive center."""
import bpy,bmesh,math,json
from pathlib import Path
from math import sin,cos,pi,sqrt
R=Path('/workspace/wewa');key='front-completion-p22-pinion-rim-v1';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);P=json.loads((R/'creative/research'/key/'G0-G2.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
N=14;pitch=.0127;rp=pitch/(2*sin(pi/N));roller=.00425;half=pi/N;seat_end=.85*math.asin(roller/rp);crest_start=.94*half;crest=rp+.0035

def seat(a):return rp*cos(a)-sqrt(max(0,roller*roller-rp*rp*sin(a)**2))
def radius(a):
 d=abs((a+half)%(2*half)-half)
 if d<seat_end:return seat(d)
 if d>=crest_start:return crest
 t=(d-seat_end)/(crest_start-seat_end);r0=seat(seat_end);h=1e-6;der=(seat(seat_end+h)-seat(seat_end-h))/(2*h);return (2*t**3-3*t*t+1)*r0+(t**3-2*t*t+t)*(crest_start-seat_end)*der+(-2*t**3+3*t*t)*crest
n=N*96;v=[];f=[]
for z,outer in [(0,True),(0,False),(.005,True),(.005,False)]:
 for j in range(n):a=2*pi*(j+.173)/n;r=radius(a)if outer else .012;v.append((r*cos(a),r*sin(a),z))
for j in range(n):
 k=(j+1)%n;f.extend([(j,n+j,n+k,k),(2*n+j,2*n+k,3*n+k,3*n+j),(j,k,2*n+k,2*n+j)])
m=bpy.data.meshes.new('14T bounded tooth rim with open center review cut');m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update();ob=bpy.data.objects.new('RELATED_14T_OUTER_RIM_OPEN_REVIEW_BOUNDARY',m);bpy.context.collection.objects.link(ob)
for p in m.polygons:p.use_smooth=(p.index%3==2)
bm=bmesh.new();bm.from_mesh(m);m.calc_loop_triangles();report={'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'boundary_edges':sum(e.is_boundary for e in bm.edges),'expected_boundary_edges':2*n,'branch_edges':sum(len(e.link_faces)>2 for e in bm.edges),'minimum_triangle_area_m2':min(t.area for t in m.loop_triangles),'teeth':14,'inner_boundary_kind':'Two open author review-cut loops; no inner cylindrical wall, aperture or spline claim','working_pitch_radius_m':rp,'all_metric_values_estimated':True};bm.free();assert report['boundary_edges']==2*n and report['branch_edges']==0 and report['minimum_triangle_area_m2']>1e-18
mat=bpy.data.materials.new('Gray form review');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.25,.25,.25,1);p.inputs['Roughness'].default_value=.3;m.materials.append(mat);P['working_pitch_radius_m']=rp;P['working_crest_radius_m']=crest;(H/'parameters.json').write_text(json.dumps(P,indent=2));ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.scene.unit_settings.system='METRIC';bpy.ops.wm.save_as_mainfile(filepath=str(H/'pinion-rim-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'pinion-rim-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'geometry-check.json').write_text(json.dumps(report,indent=2));print(report)
