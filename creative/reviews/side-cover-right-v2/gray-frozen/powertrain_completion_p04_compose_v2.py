"""P04 v2 reuses immutable right skin/head; candidate-surface placement only, no hidden fit."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common_open_v1 import finish_source,sha,write,digest,export
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/side-cover-right-v2';O=R/'creative/reviews/side-cover-right-v2';H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
plan=json.loads((R/'creative/research/powertrain-completion-p04-v1/visible-head-composition-plan-v3.json').read_text())
for row in plan['source_inputs']:assert sha(R/row['path'])==row['sha256']
def full(ob):
 m=ob.data;m.calc_loop_triangles();return hashlib.sha256(repr(([tuple(v.co)for v in m.vertices],[tuple(p.vertices)for p in m.polygons],[tuple(u.uv)for u in m.uv_layers.active.data],[tuple(n.vector)for n in m.corner_normals])).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/plan['source_inputs'][0]['path']));skin=bpy.data.objects['RIGHT_COVER_OUTER_SKIN'];original_full=full(skin)
for ob in list(bpy.data.objects):
 if ob!=skin:bpy.data.objects.remove(ob,do_unlink=True)
for im in bpy.data.images:
 if im.source=='FILE'and not im.packed_file:im.filepath=bpy.path.abspath(im.filepath);im.pack()
sm=skin.data.materials[0];sm.name='P04_PRESERVED_ORIGINAL_SKIN_MATERIAL';sm.use_fake_user=True
with bpy.data.libraries.load(str(R/plan['source_inputs'][2]['path']),link=False)as(src,dst):dst.objects=[n for n in src.objects if n=='RIGHT_COVER_LOWER_ROUND_VISIBLE_HEAD_NO_DRIVE_CLAIM']
head=dst.objects[0];assert head;bpy.context.scene.collection.objects.link(head);hm=head.data.materials[0];hm.name='P04_PRESERVED_HEAD_MATERIAL';hm.use_fake_user=True
base_head_digest=digest(head.data);tree=BVHTree.FromPolygons([v.co for v in skin.data.vertices],[list(p.vertices)for p in skin.data.polygons],all_triangles=False);x,y=plan['placement']['nominal_local_xy_m'];hit,normal,index,distance=tree.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),2);assert hit is not None and normal.z>0
rotation=Vector((0,0,1)).rotation_difference(normal).to_matrix().to_4x4();matrix=Matrix.Translation(hit+normal*.0001)@rotation;head.data.transform(matrix);head.data.update();assert full(skin)==original_full
# Preserve original material graphs in the new gray source; finish_source assigns neutral gray to visible objects only.
counts=Counter(tuple(sorted((a,b)))for f in skin.data.polygons for a,b in zip(list(f.vertices),list(f.vertices[1:])+[f.vertices[0]]));boundary=sum(v==1 for v in counts.values());assert boundary==240
P={'schema':1,'package':'P04','component_id':'MOTO-SIDE-COVER-RIGHT-COMPOSITION-002','source':'creative/research/powertrain-completion-p04-v1/visible-head-composition-plan-v3.json','reused_sources':plan['source_inputs'],'head_landmark_px':[455,399],'landmark_uncertainty_px':2,'meters_per_pixel':1.285/527,'scale_range_m_per_pixel':[.0019621973929236495,.002932882011605416],'head_position_range_each_axis_m':.010,'head_normal_offset_m':.0001,'offset_range_m':[0,.001],'expected_boundaries_by_object':{skin.name:240,head.name:0},'all_dimensions_estimated':True,'material':{'name':'Preserved per-piece original analytic materials','base_color_linear':[.18,.18,.18,1],'metallic':0,'roughness':.3},'scope':'New composition only: immutable independently traced right skin/UV/normals/analytic paint reused, plus independently documented lower head at candidate-surface estimated pose. Skin retains deliberate open reverse loop. No shaft/retainer/backing or physical head contact/installed gap certified.','package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');write(O,'reuse-placement-check.json',{'source_inputs':plan['source_inputs'],'skin_full_digest_original':original_full,'skin_full_digest_current':full(skin),'skin_mesh_uv_normals_unchanged':True,'head_original_mesh_digest':base_head_digest,'head_rigid_transform_rows':[list(row)for row in matrix],'candidate_skin_hit_m':list(hit),'candidate_skin_normal':list(normal),'head_world_bounds_m':[[min(v.co[i]for v in head.data.vertices)for i in range(3)],[max(v.co[i]for v in head.data.vertices)for i in range(3)]],'preserved_materials':{skin.name:sm.name,head.name:hm.name},'scope':'Placement on actual analytic candidate geometry only; no OEM depth, retention or physical fit certification','art_accepted':False});finish_source(H,O,P)
for row in plan['source_inputs']:assert sha(R/row['path'])==row['sha256']
