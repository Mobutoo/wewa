"""Read-only source1 region witness for comparison with actual exports."""
import bpy,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/seat-base-study-v1';W=Path('/workspace/wewa-assets/work-in-progress/seat-base-study-v2');W.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();j=json.loads((O/'build-report.json').read_text());source=H/'seat-base-study-v1.blend';assert sha(source)==j['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));ob=bpy.data.objects[j['object']];tris=[]
for p in ob.data.polygons:
 if ob.data.attributes['PLATE_REGION'].data[p.index].value!=2:continue
 assert len(p.vertices)==3;tris.append([list(ob.data.vertices[i].co)for i in p.vertices])
(W/'outer-rim-source1-positions.json').write_text(json.dumps({'source_sha256':sha(source),'export1_sha256':j['export_sha256'],'region':'Original outer rounded rim, PLATE_REGION2','triangles_blender':tris})+'\n');assert sha(source)==j['source_sha256'];print('Outer rim source witness',len(tris))
