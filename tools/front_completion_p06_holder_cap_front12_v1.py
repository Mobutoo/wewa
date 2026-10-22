"""DF201058 opaque rear-cap exterior only; no lens/reflector pattern, socket contacts or pinout."""
import bpy,math,json,runpy
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p06-holder-cap-front12-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));N=256;profile=[(.028,0),(.028,.0025)]
for j in range(1,33):a=math.pi/2*j/32;profile.append((.021+.007*math.cos(a),.0025+.007*math.sin(a)))
profile +=[(.018,.0095),(.012,.0095),(.006,.0095),(.001,.0095)];v=[(r*math.cos(2*math.pi*j/N),r*math.sin(2*math.pi*j/N),z)for r,z in profile for j in range(N)];f=[]
for i in range(len(profile)-1):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.append((a,b,b+N,a+N))
base=len(v);v.append((0,0,0));top=len(v);v.append((0,0,.0095))
for j in range(N):f.append((base,(j+1)%N,j));a=(len(profile)-1)*N+j;b=(len(profile)-1)*N+(j+1)%N;f.append((top,a,b))
body=u['mesh_object']('DF201058_OPAQUE_CAP_OUTER_ENVELOPE_NO_SOCKET_OR_OPTICS',v,f)
def roundedbox(name,location,dims,r):
 bpy.ops.mesh.primitive_cube_add(size=1,location=location);ob=bpy.context.object;ob.name=name;ob.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);m=ob.modifiers.new('Bounded visible molding edge','BEVEL');m.width=r;m.segments=6;bpy.ops.object.modifier_apply(modifier=m.name);return ob
u['boolean'](body,roundedbox('Visible outlet-root envelope finite cut',(0,-.031,.004),(.018,.024,.008),.0015),'UNION');u['boolean'](body,roundedbox('Observed rear raised transverse rib',(0,.006,.0095),(.036,.005,.003),.0014),'UNION')
ears=[{'name':'Independent left retention-ear silhouette','xy':[(-.025,-.006),(-.033,-.004),(-.034,.004),(-.027,.008)],'z':[.001,.004]},{'name':'Independent right retention-ear silhouette','xy':[(.025,-.005),(.031,-.003),(.034,.008),(.029,.010)],'z':[.0015,.0045]}]
for e in ears:
 pts=e['xy'];z0,z1=e['z'];verts=[(x,y,z)for z in [z0,z1]for x,y in pts];faces=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4)for i in range(4)];ob=u['mesh_object'](e['name'],verts,faces);u['orient'](ob);bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new('Estimated ear edge radius','BEVEL');m.width=.0006;m.segments=4;bpy.ops.object.modifier_apply(modifier=m.name);u['boolean'](body,ob,'UNION')
audit=u['clean_audit'](body)
for face in body.data.polygons:
 zs=[body.data.vertices[i].co.z for i in face.vertices]
 if max(zs)-min(zs)<1e-10 and abs(face.normal.z)>.999:face.use_smooth=False
body.data.update();(H/'parameters.json').write_text(json.dumps({'package':'P06','code':'DF201058','scope':'Opaque rear-cap outer envelope, observed raised rear rib, two individually authored ears and outlet-root exterior. No optical pattern, white locking collar, contacts or hidden conductor/socket section.','working_dimensions_m':{'cap_radius':.028,'rear_face_depth':.0095,'root_width':.018,'root_end_y':-.043,'raised_rib_max_z':.011},'estimated_bounds_m':{'cap_radius':[.022,.036],'depth':[.007,.019]},'all_dimensions_estimated':True,'source':'Exact supplier DF201058 two physical front/rear poses plus exposure repeat','ears_not_mirrored':ears,'review_closures':'Front face and end of outlet are artificial finite closure planes, not true socket wall, seat or sealed cable bore','construction_scope':'Single joined exterior study envelope, not a claim of manufactured part count or all ears made from same material','unknowns':['White retaining collar topology partly occluded, reverse/contacts and part ownership unknown','Actual wall/retention section and source dimensions','Headlamp fit, current market and electrical continuity'],'material':'Uniform dark opaque nonmetal appearance hypothesis, no polymer species, logos/grain/finish or measured reflectance'},indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'optical_relief_fabricated':False,'white_socket_ring_fabricated':False,'contacts_or_pinout_claimed':False,'mounted_fit':False},indent=2));u['gray_save'](H,'holder-cap',[body]);print(audit)
