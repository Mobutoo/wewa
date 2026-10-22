"""Original CL201023 HS1 bulb locating flange from three actual supplier views; no bulb internals."""
import bpy,runpy,math,json
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p06-bulb-flange-front15-v4';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));N=256
# Folded annular profile: observed rolled outer lip and depressed stamped annulus, finite estimated gauge.
profile=[(.0128,-.00045),(.0195,-.00045),(.0206,-.00025),(.0212,.00015),(.02145,.0006),(.0215,.0012),(.02135,.00165),(.02105,.0019),(.0207,.00195),(.02035,.0018),(.0200,.0013),(.0195,.0008),(.0145,.00065),(.0136,.00105),(.0128,.0010)]
v=[(r*math.cos(2*math.pi*j/N),r*math.sin(2*math.pi*j/N),z)for r,z in profile for j in range(N)];f=[]
for i in range(len(profile)):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;c=((i+1)%len(profile))*N;f.append((a,b,c+(j+1)%N,c+j))
ob=u['mesh_object']('CL201023_OBSERVED_ROLLED_LOCATING_FLANGE_NO_SOCKET_OR_GLASS',v,f);u['orient'](ob)
# Three source-observed differently sized locating ears; independent explicit values, not blind mirroring.
ears=[{'angle_deg':90,'width':.0100,'outer_radius':.0258,'rise':.0010},{'angle_deg':225,'width':.0060,'outer_radius':.0250,'rise':.00055},{'angle_deg':315,'width':.0060,'outer_radius':.0254,'rise':.0008}]
for i,e in enumerate(ears):
 a=math.radians(e['angle_deg']);cs,sn=math.cos(a),math.sin(a);verts=[];nr=20;nt=16;gauge=.0006
 # Independently shaped bent sheet tongue: axial rise and transverse curl both observed in source.
 for layer in [0,1]:
  for j in range(nr+1):
   q=j/nr;r=.0200+(e['outer_radius']-.0200)*q;rise=(.0020+e['rise'])*q*q*(3-2*q)
   for k in range(nt+1):
    t=(k/nt-.5)*e['width'];curl=.00055*(2*t/e['width'])**2*q
    verts.append((r*cs-t*sn,r*sn+t*cs,.0008+rise+curl+layer*gauge))
 count=(nr+1)*(nt+1);faces=[]
 for layer in [0,1]:
  for j in range(nr):
   for k in range(nt):
    b=layer*count+j*(nt+1)+k;f0=(b,b+1,b+nt+2,b+nt+1);faces.append(f0 if layer else tuple(reversed(f0)))
 boundary=list(range(nt+1))+[j*(nt+1)+nt for j in range(1,nr+1)]+[nr*(nt+1)+k for k in range(nt-1,-1,-1)]+[j*(nt+1) for j in range(nr-1,0,-1)]
 for j,b in enumerate(boundary):c=boundary[(j+1)%len(boundary)];faces.append((b,c,c+count,b+count))
 ear=u['mesh_object']('Independent bent curled locating ear '+str(i+1),verts,faces);u['orient'](ear);u['boolean'](ob,ear,'UNION')
# Two punched rectangular windows visibly present between the two narrower source ears.
for xx,ww in [(-.0035,.0015),(.0035,.0016)]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=(xx,-.0175,.0005));cut=bpy.context.object;cut.name='Observed small stamped rectangular window';cut.dimensions=(ww,.0012,.010);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);u['boolean'](ob,cut,'DIFFERENCE')
audit=u['clean_audit'](ob)
for p in ob.data.polygons:
 if abs(p.normal.z)>.999999:p.use_smooth=False
ob.data.update();(H/'parameters.json').write_text(json.dumps({'package':'P06','code':'CL201023','scope':'Single stamped locating flange only: rolled peripheral lip, depressed annular face and three individually authored source-observed ears. Not a generic washer; no capsule, base/socket, terminals, filament, hidden welds or optical prescription fabricated.','source':'Crosland CL201023 three physical poses; actual markings HS1 12V35/35W. Osram64185 corroborates HS1/PX43t class, not every detail of pictured part.','all_working_dimensions_estimated':True,'working_m':{'outer_ring_radius':.0215,'inner_cut_radius':.0128,'sheet_gauge':.0006,'ear_axial_rise':[.003,.00255,.0028],'ear_transverse_curl':.00055,'maximum_ear_radius':.0258},'bounds_m':{'outer_ring_radius':[.020,.023],'sheet_gauge':[.0003,.001],'inner_cut_radius':[.011,.015]},'ears':ears,'observed_windows':'Two rectangular stamped through windows from primary CL201023pose1; positions/sizes bounded estimates, not electrical contact holes.','new_evidence':'CEC HS1 drawing plan-view now read, PX43t three ears: wide key opposed to two narrower keys separated90deg; prior v2 near120deg layout superseded, not received fit. Working widths10/6/6mm class reference crosscheck; exact root bends estimated.','hidden_inner_termination':'Finite review bore edge only; actual collar attachment/weld and bulb-base assembly excluded','material':'Clean metallic finish estimated, no plating composition or calibrated roughness'},indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'ears_independently_authored':True,'actual_socket_fit':False},indent=2));u['gray_save'](H,'bulb-flange',[ob])
