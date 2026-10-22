import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');K='passenger-footrest-left-exterior-context-v1';H=R/'assets-src/moto-components'/K;D=R/'creative/research'/K;O=R/'creative/reviews'/K;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(H/(K+'.blend')));bpy.context.view_layer.update();rows=[];trees={}
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 assert ob.data.library and all(m.library for m in ob.data.materials);m=ob.data;M=ob.matrix_world;ps=[M@v.co for v in m.vertices];m.calc_loop_triangles();tree=BVHTree.FromPolygons(ps,[list(t.vertices)for t in m.loop_triangles],all_triangles=True);key=ob['source_parent'];trees[key]=(tree,ps)
 rows.append(dict(parent=key,object=ob.name,source_mesh_library=bpy.path.abspath(ob.data.library.filepath),matrix_world=[list(r)for r in M],data_and_materials_linked_unchanged=True,triangles=len(m.loop_triangles),bounds_m={'min':[min(p[i]for p in ps)for i in range(3)],'max':[max(p[i]for p in ps)for i in range(3)]}))
assert len(rows)==3 and bpy.context.scene.view_layers[0].material_override is None
pairs=[];keys=list(trees)
for i,a in enumerate(keys):
 for b in keys[i+1:]:
  ta,pa=trees[a];tb,pb=trees[b];overlaps=ta.overlap(tb);dist=min(ta.find_nearest(p)[3]for p in pb);pairs.append(dict(a=a,b=b,actual_triangle_surface_intersection_pairs=len(overlaps),minimum_b_vertex_to_a_surface_m=dist,scope='Static exterior triangles/vertices only, not volume/contact/fit or unknown internal seat proof'))
for p in json.loads((D/'native-links-and-transforms.json').read_text())['parents']:assert sha(R/p['source'])==p['sha256']
(D/'native-context-and-gap-read.json').write_text(json.dumps(dict(source_sha256=sha(H/(K+'.blend')),objects=rows,pairs=pairs,source_hashes_unchanged=True,display_hinge_axis_offset_m=.005,nominal_rubber_distal_overhang_beyond_metal_m=.022,frame_mounting_not_assigned=True,fit_qualified=False),indent=2)+'\n')
