"""Actual world mesh separation context, not a physical contact simulation."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/rear-sns-body-end-closure-study-v1';A=R/'creative/reviews/rear-sns-rest-assembly-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();new=json.loads((O/'build-report.json').read_text());inputs=json.loads((A/'exact-inputs-v1.json').read_text())['inputs'];source=H/'rear-sns-body-end-closure-study-v1.blend';assert sha(source)==new['source_sha256'];bpy.ops.wm.read_factory_settings(use_empty=True)
rows=[{'unit':'new-closure','source':str(source.relative_to(R)),'source_sha256':new['source_sha256'],'collection':new['collection']}]+[q for q in inputs if q['unit']in ['body-side-seat-rim','lower-collar','damper-body','rod','outer-spring','inner-spring']];geometry={}
for q in rows:
 p=R/q['source'];assert sha(p)==q['source_sha256']
 with bpy.data.libraries.load(str(p),link=True)as(fr,to):to.collections=[q['collection']]
 c=to.collections[0];bpy.context.scene.collection.children.link(c);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();V=[];F=[]
 for ob in c.all_objects:
  if ob.type!='MESH':continue
  ev=ob.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();off=len(V);V.extend([ob.matrix_world@v.co for v in m.vertices]);F.extend([tuple(off+i for i in t.vertices)for t in m.loop_triangles]);ev.to_mesh_clear()
 geometry[q['unit']]={'v':V,'tree':BVHTree.FromPolygons(V,F,all_triangles=True,epsilon=0),'triangles':len(F)}
newg=geometry['new-closure'];pairs=[]
for name,g in geometry.items():
 if name=='new-closure':continue
 overlaps=newg['tree'].overlap(g['tree']);pairs.append({'component':name,'intersecting_triangle_pairs':len(overlaps),'first_pairs':overlaps[:12]})
rad=lambda name:[math.hypot(v.x,v.y)for v in geometry[name]['v']];a=newg['v'];radrim=rad('body-side-seat-rim');radnew=rad('new-closure');radrod=rad('rod');head=geometry['lower-collar']['v'];inner_min_radius=min(rad('inner-spring'));out={'schema':1,'source_sha256':new['source_sha256'],'source_checks':[{k:v for k,v in q.items()if k in ['unit','source','source_sha256']}for q in rows],'new_against_exact_context':pairs,'candidate_axial_upper_to_inner_coil_bound_m':min(v.z for v in geometry['inner-spring']['v'])-max(v.z for v in a if math.hypot(v.x,v.y)>=inner_min_radius),'intermediate_collar_not_omitted':True,'candidate_radial_gap_to_original_rim_m':min(radrim)-max(radnew),'candidate_radial_gap_at_rod_passage_m':min(radnew)-max(radrod),'method':'Evaluated exact linked world mesh vertices and triangle surfaces; zero epsilon. Radial and axial bounds describe this authored frame, not global closest surface distance.','limitations':['Positive gaps are chosen mesh separation, not OEM tolerance/press-fit/contact','No containment, load, damping or installed fit certification','Full support section and hidden plate count remain unmeasured'],'art_accepted':False};(O/'exact-context-check.json').write_text(json.dumps(out,indent=2)+'\n');assert sha(source)==new['source_sha256'];print('CONTEXT_TRIANGLE_PAIRS',sum(q['intersecting_triangle_pairs']for q in pairs));assert all(q['intersecting_triangle_pairs']==0 for q in pairs)
