"""Read-only source inspection. Writes only this unique audit directory."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Euler,Vector
R=Path('/workspace/wewa');D=Path(__file__).resolve().parent
src=R/'assets-src/moto-components/passenger-footrest-left-exterior-context-v1/passenger-footrest-left-exterior-context-v1.blend'
bpy.ops.wm.open_mainfile(filepath=str(src))
Q=Euler(tuple(math.radians(x) for x in (-90,-45,-90)),'XYZ').to_matrix();T=Vector((.1505,.8147559,-.4267588));anchor=Vector((-.006,.239,.0195))
# Uncalibrated oblique/profile projection: source-image axle centres manually read.
f=(204.,500.);b=(748.,489.);dy=1.285;s=(b[0]-f[0])/dy;sy=(b[1]-f[1])/dy
# Pixel mapping preserves measured wheel-axis image slope; isotropic vertical scale remains an assumption.
def project(p):return [f[0]+s*(p[1]+.42), f[1]+sy*(p[1]+.42)-s*(p[2]+.74)]
def world(p):return Q@Vector(p)+T
S=json.loads((R/'assets-src/moto-components/passenger-footrest-stay-left-v1/parameters.json').read_text())['shape_choices']
land={'peg_hinge':list(anchor),'stay_clevis_hole_centre':[-.006,.239,.0145],'source_eye':[0,.3044,0]};curves={}
for kind in ('long','short'):
 p=list(map(Vector,S[kind+'_arm_bezier_source_m']));cs=[]
 for i in range(181):
  t=i/180;cs.append((1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3])
 tangent=(cs[-1]-cs[-2]).normalized()
 land[kind+'_bezier_end']=list(cs[-1]);land[kind+'_actual_aperture_centre']=list(cs[-1]+tangent*.001)
 curves[kind]=[project(world(c)) for c in cs]
rows={k:{'native_m':list(p),'world_m':list(world(p)),'pixel_estimate':project(world(p))}for k,p in land.items()}
meshes=[];dots=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 pts=[world(o.matrix_world@v.co) for v in o.data.vertices]
 meshes.append({'object':o.name,'vertices':len(pts),'world_bounds_m':[[min(p[j]for p in pts)for j in range(3)],[max(p[j]for p in pts)for j in range(3)]]})
 dots.append({'object':o.name,'points':[project(p)for p in pts[::max(1,len(pts)//4000)]]})
# All eight Euler-corner tests retain hinge anchor; not a statistical/physical tolerance.
samples=[]
for a in (-15,15):
 for b0 in (-15,15):
  for c in (-15,15):
   q=Euler(tuple(math.radians(x)for x in (-90+a,-45+b0,-90+c)),'XYZ').to_matrix();tr=Vector((.17,.65,-.60))-q@anchor
   samples.append({'euler_deg':[-90+a,-45+b0,-90+c],'T_anchor_preserving':list(tr),'eye_world_m':list(q@Vector(land['source_eye'])+tr)})
out={'authorization':'Coordinator dispatch within user-authorized autonomous motorcycle completion','source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'Q_euler_XYZ_deg':[-90,-45,-90],'Q_rows':[list(row)for row in Q],'T_m':list(T),'det':Q.determinant(),'orthogonality_max_error':max(abs((Q.transposed()@Q)[i][j]-(i==j))for i in range(3)for j in range(3)),'axis_images':{axis:list(Q@Vector(v))for axis,v in [('X',(1,0,0)),('Y',(0,1,0)),('Z',(0,0,1))]},'anchor_error_m':(world(anchor)-Vector((.17,.65,-.60))).length,'landmarks':rows,'actual_mesh_bounds':meshes,'review_allowances_only':{'position_m':[.025,.100,.040],'angle_deg':15,'provenance':'Coordinator review envelope, not OEM measurements, end-user coordinates or physical fit tolerance'},'angle_corner_tests_anchor_fixed':samples,'projection':{'source_front_axle_pixel':f,'source_rear_axle_pixel':b,'manual_pixel_uncertainty':5,'nominal_world_axles_YZ':[[-.42,-.74],[.865,-.74]],'nominal_world_provenance':'Existing main v9 layout; approximate, not OEM measurement','pixel_per_m':s,'formula':'u=204+s*(Y+.42); v=500+(489-500)/1.285*(Y+.42)-s*(Z+.74)','camera_calibrated':False,'transverse_X_ignored':True,'warning':'Oblique source profile, separate depth layers, pitch and unknown lens; projection is a diagnostic, not camera solve'},'curves_pixel':curves,'fit_qualified':False,'new_physical_ids':0}
(D/'numeric-audit.json').write_text(json.dumps(out,indent=2)+'\n')
(D/'projected-mesh-samples.json').write_text(json.dumps(dots,separators=(',',':'))+'\n')
print('NUMERIC',out['det'],out['anchor_error_m'],json.dumps(rows))
