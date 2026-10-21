"""OPTIONAL diagnostic: requires rejected3 and candidate4 only for comparison, not construction."""
import bpy,json,hashlib,struct
from pathlib import Path
from array import array
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/indicator-front-lens-study-v4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(n):
 d=R/('creative/reviews/indicator-front-lens-study-v'+str(n));j=json.loads((d/'build-report.json').read_text());p=H/('indicator-front-lens-study-v'+str(n)+'.blend');assert sha(p)==j['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(p));ob=bpy.data.objects[j['object']];assert len(ob.modifiers)==0;m=ob.data;dig=[hashlib.sha256()for _ in range(3)]
 for v in m.vertices:dig[0].update(struct.pack('<3f',*v.co))
 for f in m.polygons:
  assert len(f.vertices)==3;dig[1].update(struct.pack('<3I',*f.vertices))
 for uv in m.uv_layers.active.data:dig[2].update(struct.pack('<2f',*uv.uv))
 return {'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'vertices':len(m.vertices),'triangles':len(m.polygons),'actual_source_position_topology_cornerUV_digests':[h.hexdigest()for h in dig],'world_matrix':[list(a)for a in ob.matrix_world]},array('f',(x for n in m.corner_normals for x in n.vector))
a,na=snapshot(3);b,nb=snapshot(4);assert a['actual_source_position_topology_cornerUV_digests']==b['actual_source_position_topology_cornerUV_digests']and a['world_matrix']==b['world_matrix'];assert len(na)==len(nb);max_delta=0;count=0
for k in range(0,len(na),3):
 d=sum((float(na[k+i])-float(nb[k+i]))**2 for i in range(3))**.5;max_delta=max(max_delta,d);count+=int(d!=0)
r={'schema':1,'rejected3':a,'candidate4':b,'source_position_index_cornerUV_bytes_and_world_matrix_identical':True,'actual_corner_normal_max_vector_change':max_delta,'actual_changed_corner_normals':count,'method':'Read saved sources independently with actual mesh data, no modifiers or save; float32 bit digests of positions/indices/cornerUV. Normals intentionally differ after Float64 differential correction.','construction_dependency':False,'art_accepted':False};(O/'source3-4-protected-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');print('SOURCE_GEOMETRY_PROTECTED',max_delta,count)
