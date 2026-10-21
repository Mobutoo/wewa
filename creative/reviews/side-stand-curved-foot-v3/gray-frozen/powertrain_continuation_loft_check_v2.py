"""Reopened actual source ring centers: planar loft curvature versus normal section radius."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];name=sys.argv[sys.argv.index('--')+1];H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
assert Path(bpy.data.filepath).resolve()==(H/'child-gray.blend').resolve()
P=json.loads((H/'parameters.json').read_text());N=P['angular_samples'];obs=[o for o in bpy.context.scene.objects if o.type=='MESH'and not o.hide_render];assert len(obs)==1
V=[v.co.copy()for v in obs[0].data.vertices];has_pole=len(V)%N==1
if has_pole:V=V[:-1]
assert len(V)%N==0;centers=[];radii=[]
for i in range(len(V)//N):
 ring=V[i*N:(i+1)*N];c=sum(ring,Vector())/N;centers.append(c);radii.append(max(math.hypot(v.x-c.x,v.y-c.y)for v in ring))
rows=[]
for i in range(4,len(centers)-4):
 a,b,c=centers[i-4],centers[i],centers[i+4];ab,bc,ac=b-a,c-b,c-a;area2=ab.cross(ac).length
 if area2<1e-15:continue
 radius=ab.length*bc.length*ac.length/(2*area2);rows.append(dict(section=i,centerline_curvature_radius_m=radius,normal_section_radius_m=radii[i],curvature_margin_ratio=radius/radii[i]))
assert rows;minimum=min(rows,key=lambda x:x['curvature_margin_ratio']);assert minimum['curvature_margin_ratio']>1.10,minimum
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report=dict(actual_source_reopened=True,source_sha256=sha(H/'child-gray.blend'),protocol_sha256=sha(Path(__file__)),sections=len(centers),terminal_pole=has_pole,checked_sections=len(rows),worst=minimum,scope='Actual source ring-center curvature versus planar normal radius; no underside/contact/installed fit or global self-intersection certification',art_accepted=False)
(O/'loft-curvature-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
