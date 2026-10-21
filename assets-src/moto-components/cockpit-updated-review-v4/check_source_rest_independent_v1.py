"""Compare separately opened primary sources with composed evaluated frame1 poses."""
from pathlib import Path
import bpy,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/cockpit-updated-review-v4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((O/'source-geometry-check.json').read_text());source=H/'cockpit-updated-review-v4.blend';assert sha(source)==B['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();composed={}
for row in B['linked_sources']:
 c=next(c for c in s.collection.children if c.name==row['source_collection']);composed[row['asset']]={o.name:{'type':o.type,'world':[list(q)for q in o.matrix_world],'basis':[list(q)for q in o.matrix_basis],'parent_inverse':[list(q)for q in o.matrix_parent_inverse]}for o in c.all_objects}
rows=[]
for row in B['linked_sources']:
 path=R/row['source'];assert sha(path)==row['sha256'];bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();c=bpy.data.collections[row['source_collection']];current={o.name:{'type':o.type,'world':[list(q)for q in o.matrix_world],'basis':[list(q)for q in o.matrix_basis],'parent_inverse':[list(q)for q in o.matrix_parent_inverse]}for o in c.all_objects}
 assert current==composed[row['asset']],row['asset'];rows.append({'asset':row['asset'],'primary_source_sha256':sha(path),'objects':len(current),'type_counts':{t:sum(q['type']==t for q in current.values())for t in sorted({q['type']for q in current.values()})},'all_evaluated_world_basis_parent_inverse_identical':True})
assert sha(source)==B['source_sha256'];(O/'independent-source-rest-comparison.json').write_text(json.dumps({'source_sha256':sha(source),'frame':1,'same_depsgraph_state':'frame_set1+view_layer.update in separately opened primary and composed files','sources':rows,'source_count':18,'source_files_modified':False,'scope':'All linked objects, including fonts/empties, independently compared. No geometric/pose correction, no hardware or artistic receipt.','art_accepted':False},indent=2)+'\n');print('INDEPENDENT18_PRIMARY_REST_PASS')
