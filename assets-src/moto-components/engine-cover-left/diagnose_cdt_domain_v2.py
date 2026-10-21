"""Small, independent concave-domain counterexample for this actual Blender runtime."""
from pathlib import Path
import json,bpy,sys
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from planar_domain_checks_v2 import check_planar_domain
outline=[Vector(p)for p in [(0,0),(2,0),(2,1),(1,1),(1,2),(0,2)]];v,e,f,*_=delaunay_2d_cdt(outline,[],[list(range(6))],1,1e-6,True)
def inside(q):return 0<=q.x<=2 and 0<=q.y<=2 and(q.x<=1 or q.y<=1)
def area(faces):
 return sum(abs((v[b].x-v[a].x)*(v[c].y-v[a].y)-(v[b].y-v[a].y)*(v[c].x-v[a].x))*.5 for a,b,c in faces)
kept=[t for t in f if inside(sum((v[k]for k in t),Vector((0,0)))/3)];passing=check_planar_domain(v,kept,outline,[])
trap=[Vector(p)for p in[(.1,.1),(1.9,.8),(.8,1.9)]];centroid=sum(trap,Vector((0,0)))/3;assert inside(centroid);rejected=False;reason=None
try:check_planar_domain(trap,[(0,1,2)],outline,[])
except AssertionError as error:rejected=True;reason=str(error)
assert rejected,'Centroid-only trap was not caught';report={'Blender_version':bpy.app.version_string,'actual_CDT_output_type':1,'input_outline':[list(p)for p in outline],'input_area':3,'raw_CDT_area':area(f),'raw_triangles':f,'filtered_area':area(kept),'filtered_triangle_count':len(kept),'complete_passing_domain_check':passing,'centroid_only_trap':{'vertices':[list(p)for p in trap],'centroid':list(centroid),'centroid_inside':True,'whole_triangle_rejected':rejected,'reason':reason},'scope':'Mathematical counterexample, coordinates are arbitrary test units; not a measured motorcycle or render','art_accepted':False};assert abs(report['filtered_area']-3)<1e-9;(R/'creative/reviews/engine-cover-left-v2/cdt-domain-counterexample.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
