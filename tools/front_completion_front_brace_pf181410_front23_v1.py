"""PF181410 FRONT brace, one observed U band; coordinator dispatch, no blind fastener/reverse duplication."""
import bpy,bmesh,math,json,runpy
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');K='front-brace-pf181410-visible-front23-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));sm=u['smooth'];RR=.060;AA=.080;LL=2*AA+math.pi*RR;NS=280;NT=80;objects=[];audits=[]
def path(s):
 if s<AA:return Vector((RR,AA-s,0)),Vector((1,0,0))
 if s<AA+math.pi*RR:
  a=-(s-AA)/RR;return Vector((RR*math.cos(a),RR*math.sin(a),0)),Vector((math.cos(a),math.sin(a),0))
 return Vector((-RR,s-AA-math.pi*RR,0)),Vector((-1,0,0))
def halfheight(s):return .030+.008*(1-sm(min(s,LL-s)/.035))
def point(s,t):
 p,n=path(s);z=t*halfheight(s);h=0
 # Three separately specified source-visible shallow ridges; no hidden reverse copy or repeated motif.
 for sc,zc,ls,ws,amp in [(.057,.022,.041,.0020,.0009),(.055,-.022,.039,.0021,.00085),(LL-.050,.022,.033,.0019,-.0007)]:h+=amp*math.exp(-((s-sc)/ls)**8)*math.exp(-((z-zc)/ws)**2)
 return p+n*h+Vector((0,0,z))
def finish(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);nb=sum(e.is_boundary for e in bm.edges);assert all(len(e.link_faces)<=2 for e in bm.edges);bm.free();u['orient'](ob);a=u['clean_audit'](ob,expected_boundary=nb);a['boundary_reason']='Intentional observed skin perimeter/collar root and short-mouth cuts; full hidden reverse omitted';objects.append(ob);audits.append(a);return ob
# Planar parameter-domain cutting aid, discarded backs/bores before formed-skin mapping.
v=[(LL*i/NS,-1+2*j/NT,z)for z in [0,-.01]for j in range(NT+1)for i in range(NS+1)];row=NS+1;layer=(NT+1)*row;f=[]
for j in range(NT):
 for i in range(NS):
  a=j*row+i;f.extend([(a,a+1,a+row+1,a+row),(a+layer+row,a+layer+row+1,a+layer+1,a+layer)])
border=list(range(row))+[j*row+NS for j in range(1,NT+1)]+[NT*row+i for i in range(NS-1,-1,-1)]+[j*row for j in range(NT-1,0,-1)]
for i,a in enumerate(border):b=border[(i+1)%len(border)];f.append((a,b,b+layer,a+layer))
ob=u['mesh_object']('PF181410_OBSERVED_FORMED_U_BAND_SIX_PASSAGES_AND_THREE_RELIEFS',v,f)
# Rounded terminal corners only; independent collar positions remain estimated, not bolt patterns copied from parent.
outline=[]
for cx,cy,a0 in [(.008,-.82,math.pi),(LL-.008,-.82,-math.pi/2),(LL-.008,.82,0),(.008,.82,math.pi/2)]:
 for j in range(25):a=a0+(math.pi/2)*j/24;outline.append((cx+.008*math.cos(a),cy+.18*math.sin(a)))
n=len(outline);vv=[(x,y,z)for z in [-.04,.04]for x,y in outline];ff=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];clip=u['mesh_object']('Temporary rounded terminal outline',vv,ff);u['boolean'](ob,clip,'INTERSECT')
bend_s=AA+RR*math.radians(120);holes=[('near_upper',.012,.026,.0043),('near_lower',.0125,-.026,.0044),('far_upper',LL-.012,.0255,.0048),('far_lower',LL-.0125,-.0255,.0047),('bend_upper',bend_s,.021,.0025),('bend_lower',bend_s+.001,-.021,.0025)];nominal=[]
for name,s,z,r in holes:
 t=z/halfheight(s);ds=(point(s+1e-6,t)-point(s-1e-6,t))/2e-6;dt=(point(s,t+1e-5)-point(s,t-1e-5))/2e-5;rx=r/ds.length;ry=r/dt.length
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=1,depth=.10,location=(s,t,0));cut=bpy.context.object;cut.scale=(rx,ry,1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);u['boolean'](ob,cut);nominal.append({'id':name,'center_m':list(point(s,t)),'radius_m':r,'parameter_center':[s,t],'nominal_surface_normal':list((-ds.cross(dt)).normalized()),'status':'estimated_visible_aperture_no_fit_assignment'})
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();m=ob.data;polys=[p for p in m.polygons if all(abs(m.vertices[i].co.z)<1e-6 for i in p.vertices)];ids=sorted({i for p in polys for i in p.vertices});idx={old:i for i,old in enumerate(ids)};uv=[tuple(m.vertices[i].co[:2])for i in ids];vv=[tuple(point(s,t))for s,t in uv];ff=[tuple(idx[i]for i in p.vertices)for p in polys];old=ob.data;new=bpy.data.meshes.new('PF181410 mapped single observed skin');new.from_pydata(vv,[],ff);new.update();ob.data=new;bpy.data.meshes.remove(old)
# One short perimeter edge skin, no full opposite wall and no invented band-hole engagement.
bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();bm.verts.index_update();remaining={e for e in bm.edges if e.is_boundary};groups=[]
while remaining:
 e=remaining.pop();group={e};todo=list(e.verts)
 while todo:
  v=todo.pop()
  for q in v.link_edges:
   if q in remaining:remaining.remove(q);group.add(q);todo.extend(q.verts)
 groups.append(group)
assert len(groups)==7,[len(g)for g in groups];perimeter=max(groups,key=len);verts={v for e in perimeter for v in e.verts}
def normal(v):
 s,t=uv[v.index];ds=point(s+1e-6,t)-point(s-1e-6,t);dt=point(s,t+1e-5)-point(s,t-1e-5);return (-ds.cross(dt)).normalized()
copies={v:bm.verts.new(v.co-normal(v)*.0012)for v in verts}
for e in perimeter:
 a,b=e.verts;bm.faces.new((a,b,copies[b],copies[a]))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();finish(ob)
# Only the two actual near-side raised collar exteriors; no bolts, threads or guessed far-side duplicates.
for name,y,z,ro,ri,rot in [('PF181410_NEAR_UPPER_OBSERVED_COLLAR_SKIN',AA-.012,.026,.0070,.0043,.12),('PF181410_NEAR_LOWER_OBSERVED_COLLAR_SKIN',AA-.0125,-.026,.0072,.0044,.22)]:
 profile=[(ro,RR+.0001,'hex'),(ro,RR+.0008,'hex'),(ro*.98,RR+.0013,'hex'),(ro*.94,RR+.0017,'round'),(ro*.90,RR+.0038,'round'),(ro*.86,RR+.0048,'round'),(ri*1.08,RR+.0048,'round'),(ri,RR+.0041,'round'),(ri,RR+.0024,'round')];n=192;v=[];f=[]
 for r,x,mode in profile:
  for j in range(n):a=2*math.pi*j/n;rr=r/(math.cos((a+rot+math.pi/6)%(math.pi/3)-math.pi/6))if mode=='hex'else r;v.append((x,y+rr*math.cos(a),z+rr*math.sin(a)))
 for i in range(len(profile)-1):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
 finish(u['mesh_object'](name,v,f))
params={'package':'LEGACY15-FRONT-BRACE','component_id':'MOTO-FRONT-FENDER-BRACE-PF181410-VISIBLE-STUDY-001','scope':'One PF181410 FRONT formed U-band observed skin with rounded/flared terminal edges, six actual skin apertures, three individually observed shallow reliefs and two source-visible near-terminal raised collar exteriors/short mouths only. No full hidden reverse, internal thread, unobserved far collars, bolt/clamp or parent geometry.','working_dimensions_estimated':True,'working_m':{'bend_radius':RR,'straight_arm_length':AA,'overall_width':2*RR,'overall_depth':AA+RR,'band_height':.060,'terminal_height':.076,'short_perimeter_gauge':.0012,'collar_projection':.0048,'ridge_heights':[.0009,.00085,.0007]},'ranges_m':{'overall_width':[.095,.155],'overall_depth':[.110,.185],'band_height':[.045,.080],'terminal_height':[.060,.095],'short_gauge':[.0008,.0020],'collar_projection':[.0025,.007],'ridge_height':[.0004,.0016]},'estimate_justification':'Single physical inside/top oblique: relative U envelope, terminal/band ratios and visible shallow/ring depth ordering. Metric scale/ranges are modeling hypotheses, not manufacturer measurements or calibrated depth bounds. No dimensions borrowed from fender/adjacent model.','nominal_holes':nominal,'source':'Bajajonline PF181410 exact seller association; BM1502016 sheet37 item19 FRONT qty1. D04 does not separately list this article.','variant':'Related BM150 family; exact current RDC identity and mounting contacts unconfirmed','surface_limit':'Observed formed sheet skin shown double-sided for isolated inspection, no detailed full opposite back topology; short edge gauge is estimated','omitted':['Full hidden reverse and collar roots/backside welds','Internal threads and engagement','Unobserved far collars, bolts, nuts, clamp','Current RDC fender/fork fitting transform and tyre clearance'],'material':'Dark coated-metal hypothesis, no certified alloy/paint/edge treatment/roughness or wear','provenance':{'user':'Autonomous motorcycle completion objective','coordinator':'PF181410 one FRONT brace separate child under LEGACY15-FRONT-BRACE'},'art_accepted':False,'mounted_fit':False}
(H/'parameters.json').write_text(json.dumps(params,indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':audits,'independent_meshes':len(objects),'observed_band_apertures':6,'collars':2,'hidden_thread_generated':False,'no_fastener_or_clamp':True},indent=2));(O/'child-plan.json').write_text(json.dumps({'package':params['package'],'component_id':params['component_id'],'child':'PF181410 FRONT fender brace visible exterior study','scope':params['scope']+' All dimensions estimated, current RDC fit unknown.','instruction_provenance':params['provenance'],'protocols':['front_completion_front_brace_pf181410_front23_v1.py','front_completion_front_brace_render_front23_v1.py','front_completion_front10_mesh_helpers_v1.py','front_completion_front10_material_v1.py'],'remaining':params['omitted']},indent=2));u['gray_save'](H,'front-brace',objects)
