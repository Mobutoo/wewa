# Parent SHA256 8459c4a26ffcd31e3b423a31a6f58f7df81c4f7a9af69f643c406a01476dd207; visible web skew and short neck exteriors corrected, parent retained.
"""PF121025 two-pose visible-surface study. New source only; no PF121024 merge or hidden thickness."""
from pathlib import Path
import bpy,bmesh,math,json,runpy
from mathutils import Vector
R=Path('/workspace/wewa');K='front-completion-p25-fairing-structure-front20-v2';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True)
u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));objects=[];audits=[]
def finish(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);edges=[e for e in bm.edges if e.is_boundary];nb=len(edges);assert all(sum(e.is_boundary for e in v.link_edges)==2 for v in bm.verts if v.is_boundary);assert all(len(e.link_faces)<=2 for e in bm.edges);bm.free()
 u['orient'](ob);a=u['clean_audit'](ob,expected_boundary=nb);a['boundary_reason']='Deliberate single observed surface perimeter/hole contours or finite open bar join cuts; hidden faces omitted';objects.append(ob);audits.append(a);return ob

def rounded(poly,f=.13):
 out=[]
 for i,b in enumerate(poly):
  a=poly[i-1];c=poly[(i+1)%len(poly)];p=[b[k]+(a[k]-b[k])*f for k in [0,1]];q=[b[k]+(c[k]-b[k])*f for k in [0,1]]
  for j in range(7):
   t=j/6;out.append(tuple((1-t)**2*p[k]+2*t*(1-t)*b[k]+t*t*q[k] for k in [0,1]))
 return out

def plate(name,poly,holes,origin,U,V,fold=None):
 # CSG is only a temporary planar triangulation aid; final contains FRONT SKIN ONLY.
 p=rounded(poly);m=len(p);verts=[(a,b,t)for t in [0,-.001]for a,b in p];faces=[tuple(range(m)),tuple(reversed(range(m,2*m)))]+[(i,(i+1)%m,(i+1)%m+m,i+m)for i in range(m)]
 ob=u['mesh_object'](name,verts,faces)
 for x,y,rx,ry in holes:
  bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=1,depth=.02,location=(x,y,0));cut=bpy.context.object;cut.scale=(rx,ry,1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);u['boolean'](ob,cut)
 mesh=ob.data;keep=[p for p in mesh.polygons if all(abs(mesh.vertices[i].co.z)<1e-7 for i in p.vertices)];ids=sorted({i for p in keep for i in p.vertices});idx={v:i for i,v in enumerate(ids)};vv=[]
 for i in ids:
  a,b=mesh.vertices[i].co[:2];pos=Vector(origin)+a*Vector(U)+b*Vector(V)
  if fold:pos+=Vector(fold(a,b))
  vv.append(tuple(pos))
 ff=[tuple(idx[i] for i in p.vertices)for p in keep];old=ob.data;new=bpy.data.meshes.new(name+' observed face');new.from_pydata(vv,[],ff);new.update();ob.data=new;bpy.data.meshes.remove(old);return finish(ob)

def ribbon(name,rows):
 v=[p for row in rows for p in row];f=[]
 for i in range(len(rows)-1):a=i*2;f.append((a,a+1,a+3,a+2))
 return finish(u['mesh_object'](name,v,f))

def bar(name,z,bow,y,r,x0,x1):
 n=128;steps=96;v=[];f=[]
 for i in range(steps+1):
  t=i/steps;x=x0+(x1-x0)*t;zz=z-bow*math.sin(math.pi*t);slope=-bow*math.pi*math.cos(math.pi*t)/(x1-x0);normal=Vector((-slope,0,1)).normalized()
  for j in range(n):a=2*math.pi*j/n;v.append(tuple(Vector((x,y,zz))+r*(math.cos(a)*Vector((0,1,0))+math.sin(a)*normal)))
 for i in range(steps):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
 return finish(u['mesh_object'](name,v,f))
# Each side independently parameterized from its visible silhouette, not mirrored meshes.
leftweb=[(-.021,-.069),(-.028,-.041),(-.022,-.012),(-.023,.043),(-.029,.068),(-.019,.089),(-.012,.109),(.009,.112),(.014,.093),(.006,.073),(.029,.052),(.040,.018),(.028,-.025),(.024,-.068)]
rightweb=[(-.023,-.068),(-.027,-.043),(-.022,-.008),(-.024,.044),(-.027,.069),(-.018,.093),(-.010,.111),(.010,.111),(.016,.091),(.008,.070),(.031,.049),(.039,.016),(.029,-.026),(.024,-.067)]
plate('PF121025_LEFT_VISIBLE_FOLDED_SIDE_WEB',leftweb,[(.018,.011,.011,.0085)],(-.120,0,0),(-.38,1,0),(0,0,1),lambda a,b:(-.003*math.sin((b+.07)/.18*math.pi),0,0))
plate('PF121025_RIGHT_VISIBLE_FOLDED_SIDE_WEB',rightweb,[(.018,.009,.0105,.008)],(.121,0,0),(.38,1,0),(0,0,1),lambda a,b:(.0025*math.sin((b+.07)/.18*math.pi),0,0))
# Broad outer upright ears are pressed sheet faces, NOT cylindrical PF121024 fork sleeves.
leftwing=[(-.158,.075),(-.166,.078),(-.164,.088),(-.146,.108),(-.145,.169),(-.138,.179),(-.114,.179),(-.110,.169),(-.112,.103),(-.133,.082),(-.149,.074)]
rightwing=[(.150,.074),(.166,.081),(.168,.091),(.148,.110),(.147,.170),(.139,.180),(.115,.180),(.110,.170),(.113,.103),(.135,.081)]
plate('PF121025_LEFT_UPPER_WING_TWO_OBSERVED_HOLES',leftwing,[(-.129,.166,.0042,.0042),(-.154,.084,.0044,.0044)],(0,.008,0),(1,0,0),(0,0,1),lambda a,b:(0,.010*max(0,min(1,(b-.100)/.075)),0))
plate('PF121025_RIGHT_UPPER_WING_TWO_OBSERVED_HOLES',rightwing,[(.131,.166,.0042,.0042),(.156,.086,.0044,.0044)],(0,.009,0),(1,0,0),(0,0,1),lambda a,b:(0,.009*max(0,min(1,(b-.102)/.075)),0))
# Outboard middle ears seen frontally, individually outlined, two holes only on source-right clear face.
plate('PF121025_LEFT_OUTBOARD_MIDDLE_EAR', [(-.163,-.002),(-.161,.034),(-.149,.045),(-.116,.040),(-.115,-.002),(-.139,-.014),(-.156,-.013)],[(-.148,.018,.0046,.006)],(0,-.009,0),(1,0,0),(0,0,1),lambda a,b:(0,-.018*max(0,(-a-.115)/.05),0))
plate('PF121025_RIGHT_OUTBOARD_MIDDLE_EAR',[(.116,-.003),(.117,.040),(.151,.045),(.165,.032),(.165,-.002),(.154,-.014),(.137,-.013)],[(.149,.018,.0067,.0080),(.135,.027,.0030,.0035)],(0,-.010,0),(1,0,0),(0,0,1),lambda a,b:(0,-.017*max(0,(a-.115)/.05),0))
# Inner top ears and lower turned mounting tabs: holes are true voids through single skins, no inferred bore walls.
plate('PF121025_LEFT_INNER_TOP_TAB',[(-.116,.063),(-.111,.105),(-.103,.116),(-.096,.114),(-.094,.080),(-.103,.063)],[(-.104,.098,.0040,.0052)],(0,-.023,0),(1,0,0),(0,0,1))
plate('PF121025_RIGHT_INNER_TOP_TAB',[(.104,.062),(.095,.081),(.096,.115),(.104,.116),(.112,.105),(.117,.063)],[(.104,.098,.0040,.0052)],(0,-.024,0),(1,0,0),(0,0,1))
plate('PF121025_LEFT_LOWER_TURNED_TAB',[(-.115,-.043),(-.113,-.068),(-.104,-.079),(-.096,-.077),(-.094,-.054),(-.103,-.043)],[(-.104,-.063,.0042,.0068)],(0,-.019,0),(1,0,0),(0,0,1),lambda a,b:(0,-.008*max(0,(-b-.045)/.035),0))
plate('PF121025_RIGHT_LOWER_TURNED_TAB',[(.104,-.043),(.094,-.055),(.097,-.078),(.105,-.080),(.114,-.068),(.117,-.044)],[(.105,-.064,.0042,.0065)],(0,-.020,0),(1,0,0),(0,0,1),lambda a,b:(0,-.007*max(0,(-b-.045)/.035),0))
# A few actually visible folded-edge strips, not complete unobserved rear returns.
ribbon('PF121025_LEFT_UPPER_VISIBLE_FOLD_STRIP',[[(-.113,.009,.103),(-.108,.014,.104)],[(-.111,.015,.140),(-.106,.020,.140)],[(-.111,.018,.170),(-.106,.023,.170)]])
ribbon('PF121025_RIGHT_UPPER_VISIBLE_FOLD_STRIP',[[(.114,.010,.103),(.109,.015,.104)],[(.112,.015,.140),(.107,.020,.140)],[(.111,.018,.170),(.106,.023,.170)]])
bar('PF121025_UPPER_BOWED_TRANSVERSE_OUTER_SKIN',.061,.008,-.021,.0054,-.112,.113)
bar('PF121025_LOWER_TRANSVERSE_OUTER_SKIN',-.047,.0007,-.021,.0058,-.112,.113)
# Short source-visible upright neck outside skins under upper wings, not long fork sleeves.
for name,x,y,z0,z1,r in [('PF121025_LEFT_VISIBLE_SHORT_NECK',-.132,.011,.026,.088,.0048),('PF121025_RIGHT_VISIBLE_SHORT_NECK',.133,.012,.025,.089,.0049)]:
 n=128;v=[];f=[]
 for z in [z0,z1]:
  for j in range(n):a=2*math.pi*j/n;v.append((x+r*math.cos(a),y+r*math.sin(a),z))
 for j in range(n):a=j;b=(j+1)%n;f.append((a,b,b+n,a+n))
 finish(u['mesh_object'](name,v,f))
params={'package':'P25','code':'PF121025','source':'Actual Matriz near frontal and Mundimotos oblique, Russian same capture not third pose','scope':'Large visible fairing structure: independent folded/perforated side webs, upper wings, middle ears, inner top and lower tabs, visible fold strips and short upright neck exteriors, two transverse exterior skins including bowed upper. Hidden plate backs/thickness, weld sections and bar interiors omitted.','all_working_dimensions_estimated':True,'working_m':{'crossbar_end_span':.225,'upper_bar_sag':.008,'bar_radii':[.0054,.0058],'outer_width':.336,'visible_height':.260},'working_ranges_not_measured_m':{'outer_width':[.27,.40],'visible_height':[.21,.32],'bar_radius':[.004,.008],'upper_sag':[.003,.016],'depth_layout':[.02,.09]},'depth_caution':'Working ranges are modeling hypotheses, not photogrammetric/source-derived depth bounds; true opposite/profile unresolved','axes':'X horizontal across frame, Z upright, front approximately -Y, origin midway bars','hidden_omitted':['Plate thickness and hidden backs/returns','Unseen holes and hidden weld cross-sections','Bar inside walls/end plugs','Grommets, bolts, fork sleeves and PF121024','Current RDC fitting transform'],'independent_surfaces':len(objects),'art_accepted':False,'mounted_fit':False}
(H/'parameters.json').write_text(json.dumps(params,indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':audits,'surfaces':len(objects),'intentional_open_review_boundaries':True,'source_supported_partial_exterior_not_complete_casting':True},indent=2));(O/'child-plan.json').write_text(json.dumps({'package':'P25','component_id':'MOTO-FAIRING-STRUCTURE-PF121025-VISIBLE-STUDY-001','child':'PF121025 visible fairing structure two-pose exterior study','scope':params['scope']+' Dimensions and current RDC identity estimated, no PF121024 merge.','protocols':['front_completion_p25_fairing_structure_front20_v2.py','front_completion_p25_fairing_structure_front20_v1.py','front_completion_front10_mesh_helpers_v1.py','front_completion_fairing_render_front20_v1.py','front_completion_front10_material_v1.py'],'remaining':params['hidden_omitted']},indent=2));u['gray_save'](H,'fairing-structure',objects)
