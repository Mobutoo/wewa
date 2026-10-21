"""Read-only local ray audit for the previously rejected unintended back-wall exit."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/mirror-right-v1';j=json.loads((OUT/'shell-study-v1-check.json').read_text());path=HERE/'mirror-right-shell-study-v1.blend';assert hashlib.sha256(path.read_bytes()).hexdigest()==j['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(path));f=j['head_frame_world'];C=Vector(f['centre_m']);U=Vector(f['outward_U']);V=Vector(f['up_V']);N=Vector(f['normal_toward_rider_N']);head=lambda p:C+U*p[0]+V*p[1]+N*p[2]
plan=json.loads((HERE/'parameters-right.json').read_text());hole=plan['observed_small_hole'];hu,hv=hole['position_local_uv_working_m'];hr=hole['radius_working_m'];intended=[]
body=bpy.data.objects['RH mirror compound hollow shell construction'];shell=bpy.data.objects['RH mirror compound shell and socket - candidate'];base=BVHTree.FromPolygons([head(v.co) for v in body.data.vertices],[tuple(p.vertices) for p in body.data.polygons]);final=BVHTree.FromPolygons([v.co for v in shell.data.vertices],[tuple(p.vertices) for p in shell.data.polygons]);rows=[]
for ui in range(-75,-19):
 for vi in range(-48,6):
  u=ui*.001;v=vi*.001;origin=head((u,v,-.10));a=base.ray_cast(origin,N,.13);b=final.ray_cast(origin,N,.13)
  if a[0] is None:continue
  delta=None if b[0] is None else (b[0]-a[0]).dot(N)
  # A cut exposing the inner cavity advances the hit by roughly wall thickness.
  if delta is None or delta>.002:
   row={'uv_m':[u,v],'back_hit_advance_m':delta}
   if (u-hu)**2+(v-hv)**2<=hr**2:intended.append(row)
   else:rows.append(row)
report={'source_sha256':j['source_sha256'],'scope':'Actual source BVH sweep at1mm spacing over neck/back exit region excluding only the modelled observed RH hole; compares preserved construction back shell to final CSG. Positive advance>2mm flags a new opening; neck additions toward camera are allowed. Does not measure exact photographed contour.','grid_uv_m':[[-.075,-.020],[-.048,.005]],'intended_related_RH_hole_samples':intended,'exclusion_disc_local_uv_m':[hu,hv,hr],'exclusion_status':'Only actual model drill radius is excluded; its photographic placement/radius remain estimated','anomalous_back_wall_advance':rows,'passed':not rows,'art_accepted':False};(OUT/'shell-unintended-exit-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert report['passed'],report
