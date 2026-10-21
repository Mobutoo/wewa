from pathlib import Path
import bpy,json,hashlib,sys
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/cockpit-cables-v3';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/'build-report-v3.json').read_text());source=H/'cockpit-cables-v3.blend';assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import check_mesh
rows=[]
for old in B['geometry']:
 o=bpy.data.objects[old['name']];row=check_mesh(o);assert row==old;o.data.calc_loop_triangles();assert len(o.data.loop_triangles)==B['triangle_counts_by_object'][o.name]and all(t.area>0 for t in o.data.loop_triangles);rows.append(row)
assert not bpy.data.libraries and not[i for i in bpy.data.images if i.source=='FILE'and i.filepath]
r={'source_sha256':sha(source),'export_sha256':B['export_sha256'],'geometry':rows,'actual_triangle_counts':B['triangle_counts_by_object'],'source_libraries':0,'source_file_images':0,'scope':'Actual savedsource closure/count/areas, inherited two lowerobjects and revisedtriangulatedpigtail. Separate source/native invariants prove lowerpreservation; no actualRDC route/fit/chemistry or artistic acceptance.','art_accepted':False};(O/'evaluated-source-check.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==B['source_sha256'];print('ACTUAL_SOURCE_V3',sum(B['triangle_counts_by_object'].values()))
