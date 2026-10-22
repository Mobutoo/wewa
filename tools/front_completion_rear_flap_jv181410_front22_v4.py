# Parent SHA256 27e717167088c3b968e3d48c8a612c995b034d4b6f0eb3ff868ab0c19d3f2427; omit unsupported cheek back-mouth returns while retaining true holes, parent unchanged.
# Parent SHA256 1c62abb28026d39d34608edc33b2ab505a57a006671eb01d0194cc4f48535f2f; analytic local gauge direction, flat-domain triangulation before surface mapping, no new hidden section.
# Parent SHA256 d9cb28674ada07075e649e6df5f77e0eee2d006388deee33dbbcc0c4cd0bd110; band envelope/rise and source-visible lower corners corrected, parent unchanged.
"""Original JV181410 outside skin, two physical poses; coordinator scope, no hidden reverse filler."""
import bpy,bmesh,math,json,runpy
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');K='rear-mudflap-jv181410-visible-front22-v4';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));NU=160;NT=240;HH=.260
sm=u['smooth']
def point(a,t):
 w=.078+.006*sm(t/.10)-.010*sm((t-.72)/.28);theta= .55+.97*sm((t-.70)/.30);x=w*math.sin(theta*a)/math.sin(theta)
 z=HH*t+.008*a*a*(1-sm(t/.08))+.036*a**4*sm((t-.78)/.22)
 dep=.020+.048*sm((t-.70)/.30);y=-dep*(1-math.cos(theta*a))/(1-math.cos(theta))
 # Source-observed lower turn/lip and curved upper band margin, no reverse ribs.
 y-=.005*math.exp(-((t-.032)/.024)**2)*(1-.25*a*a)
 y-=.0017*math.exp(-((t-.747)/.014)**2)*(1-.10*a*a)
 # Smooth rounded rectangular boss integrated into outside field.
 qx=abs(x)-(.0535-.010);qz=abs(z-.143)-(.035-.010);dist=math.hypot(max(qx,0),max(qz,0))+min(max(qx,qz),0)-.010
 y-=.008*(1-sm((dist+.003)/.007))
 return Vector((x,y,z))
# Dense parameter-plane grid as CSG cutting aid. Back and boolean hole walls discarded before mapping.
v=[]
for k in [0,1]:
 for j in range(NT+1):
  for i in range(NU+1):v.append((-1+2*i/NU,j/NT,-.01*k))
row=NU+1;layer=(NT+1)*row;f=[]
for j in range(NT):
 for i in range(NU):
  a=j*row+i;f.extend([(a,a+1,a+row+1,a+row),(a+layer+row,a+layer+row+1,a+layer+1,a+layer)])
border=list(range(row))+[j*row+NU for j in range(1,NT+1)]+[NT*row+i for i in range(NU-1,-1,-1)]+[j*row for j in range(NT-1,0,-1)]
for i,a in enumerate(border):b=border[(i+1)%len(border)];f.append((a,b,b+layer,a+layer))
ob=u['mesh_object']('JV181410_OBSERVED_OUTSIDE_FIELD_BAND_CHEEKS_BOSS_LIP',v,f)
# Round only the two observed lower outline corners in parameter space; no unseen reverse.
outline=[]
for i in range(33):
 a=-math.pi/2+(math.pi/2)*i/32;outline.append((.91+.09*math.cos(a),.035+.035*math.sin(a)))
outline.extend([(1,1),(-1,1)])
for i in range(33):
 a=math.pi+(math.pi/2)*i/32;outline.append((-.91+.09*math.cos(a),.035+.035*math.sin(a)))
n=len(outline);vv=[(x,y,z)for z in [-.04,.04]for x,y in outline];ff=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];cutter=u['mesh_object']('Temporary rounded outside outline clipping aid',vv,ff);u['boolean'](ob,cutter,'INTERSECT')
holes=[('upper_center',0,.885,.0033),('left_cheek',-.90,.952,.0030),('right_cheek',.90,.952,.0030),('boss_left',-.203,.550,.0027),('boss_right',.203,.550,.0027)];nominal=[]
for name,a,t,r in holes:
 da=(point(a+1e-5,t)-point(a-1e-5,t))/2e-5;dt=(point(a,t+1e-5)-point(a,t-1e-5))/2e-5;rx=r/da.length;ry=r/dt.length
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=1,depth=.10,location=(a,t,0));cut=bpy.context.object;cut.scale=(rx,ry,1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);u['boolean'](ob,cut);nominal.append({'id':name,'center_m':list(point(a,t)),'nominal_radius_m':r,'parameter_center':[a,t],'parameter_ellipse_radii':[rx,ry],'local_derivative_axes':[list(da.normalized()),list(dt.normalized())],'status':'estimated_unfitted_visible_passage'})
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
m=ob.data;polys=[p for p in m.polygons if all(abs(m.vertices[i].co.z)<1e-6 for i in p.vertices)];ids=sorted({i for p in polys for i in p.vertices});idx={old:i for i,old in enumerate(ids)};uvcoords=[tuple(m.vertices[i].co[:2])for i in ids];vv=[tuple(point(a,t))for a,t in uvcoords];ff=[tuple(idx[i]for i in p.vertices)for p in polys];old=ob.data;new=bpy.data.meshes.new('JV181410 mapped observed outside');new.from_pydata(vv,[],ff);new.update();ob.data=new;bpy.data.meshes.remove(old)
# Short edge and hole-mouth returns only; full unseen back remains open, no arbitrary hidden panel.
bm=bmesh.new();bm.from_mesh(ob.data);bm.normal_update();bm.verts.ensure_lookup_table();bm.verts.index_update()
def cheek_mouth(e):return all(.75<abs(uvcoords[v.index][0])<.99 and .86<uvcoords[v.index][1]<.999 for v in e.verts)
edges=[e for e in bm.edges if e.is_boundary and not cheek_mouth(e)];verts={v for e in edges for v in e.verts};bm.verts.ensure_lookup_table();bm.verts.index_update()
def gauge_normal(v):
 a,t=uvcoords[v.index];da=point(a+1e-5,t)-point(a-1e-5,t);dt=point(a,t+1e-5)-point(a,t-1e-5);return da.cross(dt).normalized()
copies={v:bm.verts.new(v.co-gauge_normal(v)*.0018)for v in verts}
for e in edges:
 a,b=e.verts;bm.faces.new((a,b,copies[b],copies[a]))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
bm=bmesh.new();bm.from_mesh(ob.data);boundary=[e for e in bm.edges if e.is_boundary];nb=len(boundary);components=[];remaining=set(boundary)
while remaining:
 seed=remaining.pop();group={seed};todo=list(seed.verts)
 while todo:
  v=todo.pop()
  for e in v.link_edges:
   if e in remaining:remaining.remove(e);group.add(e);todo.extend(e.verts)
 components.append(len(group))
bm.free();assert len(components)==6,components
u['orient'](ob);audit=u['clean_audit'](ob,expected_boundary=nb)
params={'package':'LEGACY15-REAR-FLAP','component_id':'MOTO-REAR-MUDFLAP-JV181410-VISIBLE-STUDY-001','scope':'One JV181410 continuous observed outside field, deep upper concave band and pierced cheeks, middle rounded two-hole boss, raised lower lip, five real skin passages and short estimated perimeter/three front-mouth gauge; two cheek back-mouths omitted. Full unseen reverse/roots/ribs excluded.','all_working_dimensions_estimated':True,'working_m':{'field_height':HH,'max_halfwidth':.084,'upper_corner_extension':.036,'body_depth':.020,'upper_depth':.068,'boss_height':.008,'boss_width':.107,'boss_height_in_plane':.070,'lip_height':.005,'short_edge_gauge':.0018},'estimate_ranges_m':{'field_height':[.22,.30],'width':[.145,.195],'body_depth':[.012,.032],'upper_depth':[.040,.090],'boss_height':[.004,.012],'lip_height':[.002,.008],'edge_gauge':[.001,.0035]},'estimate_justification':'Matriz near-front constrains outline and relative boss/field positions. RU oblique shows depth ordering/concavity, raised boss and lip. Numeric ranges bracket working hypotheses, not measured or camera-calibrated mm bounds; no adjacent part dimensions transferred.','nominal_hole_landmarks':nominal,'boundary_loops':components,'boundary_reason':'One perimeter return cut, three front-mouth cuts and two cheek skin-void boundaries with no unseen mouth wall; no full reverse invented','material':'Uniform black polymer hypothesis, not certified rubber/elastomer/resin/flexibility; no copied photo texture or invented grain','omitted':['Hidden reverse/ribs/attachment backs','Exact lip section and full wall thickness','30201069 reflector and all hardware','Front PF181430/PF181408, shell JV181408, brace PF181410','Current RDC identity/installed transform/contacts'],'provenance':{'user':'Autonomous motorcycle completion objective','coordinator':'JV181410 single rear flap exterior detailed dispatch'},'art_accepted':False,'mounted_fit':False}
(H/'parameters.json').write_text(json.dumps(params,indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'boundary_loops':components,'real_visible_passages':5,'one_exemplar':True,'arbitrary_back_ribs':False},indent=2));(O/'child-plan.json').write_text(json.dumps({'package':params['package'],'component_id':params['component_id'],'child':'JV181410 rear mudflap observed exterior study','scope':params['scope']+' Dimensions and current RDC applicability estimated, black polymer hypothesis not rubber certification.','instruction_provenance':params['provenance'],'protocols':['front_completion_rear_flap_jv181410_front22_v4.py','front_completion_rear_flap_jv181410_front22_v3.py','front_completion_rear_flap_jv181410_front22_v2.py','front_completion_rear_flap_jv181410_front22_v1.py','front_completion_rear_flap_render_front22_v1.py','front_completion_front10_mesh_helpers_v1.py','front_completion_rear_flap_material_front22_v1.py','front_completion_front10_material_v1.py'],'remaining':params['omitted']},indent=2));u['gray_save'](H,'rear-flap',[ob])
