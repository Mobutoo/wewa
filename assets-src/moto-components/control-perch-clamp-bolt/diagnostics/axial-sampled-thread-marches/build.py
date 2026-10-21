"""Single continuous isolated related hex bolt. No CSG/global bevel or hidden assembly."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/control-perch-clamp-bolt-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not(H/'preflight-manifest.json').exists();sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import mesh_object,material,check_mesh,export,studio
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
C=bpy.data.collections.new('WEWA_CONTROL_PERCH_CLAMP_BOLT');s.collection.children.link(C);stage=bpy.data.collections.new('CONTROL_PERCH_CLAMP_BOLT_STUDIO_NOT_EXPORTED');s.collection.children.link(stage);root=bpy.data.objects.new('Control perch bolt isolated underhead datum - not installed',None);C.objects.link(root)
mat=material('Bolt geometry review gray - material not received',(.19,.19,.19),0,.42);N=P['radial_samples'];pitch=P['documented_related_pitch_m'];rmaj=P['documented_related_thread_diameter_m']/2;apothem=P['working_across_flats_m']/2;top=-P['working_head_height_m'];topr=P['working_top_flat_radius_m'];runder=P['working_underhead_outer_radius_m'];F=P['working_underhead_fillet_radius_m'];L=P['working_underhead_length_m'];rings=[];labels=[];hexR=lambda a:apothem/math.cos((a+math.pi/6)%(math.pi/3)-math.pi/6)
def add(label,fn):labels.append(label);rings.append([fn(math.tau*i/N)for i in range(N)])
add('top-flat-circle',lambda a:(topr*math.cos(a),topr*math.sin(a),top))
# Cone equation z=top+(r-topr)/sqrt(3), exactly at each hex boundary.
add('analytic-upper-cone-hex-intersection',lambda a:(hexR(a)*math.cos(a),hexR(a)*math.sin(a),top+(hexR(a)-topr)/math.sqrt(3)))
add('analytic-lower-cone-hex-intersection',lambda a:(hexR(a)*math.cos(a),hexR(a)*math.sin(a),-(hexR(a)-runder)/math.sqrt(3)))
add('underhead-bearing-outer',lambda a:(runder*math.cos(a),runder*math.sin(a),0))
add('underhead-bearing-fillet-start',lambda a:((rmaj+F)*math.cos(a),(rmaj+F)*math.sin(a),0))
for k in range(1,13):
 t=math.pi*k/24;r=rmaj+F-F*math.sin(t);z=F-F*math.cos(t);add('fillet-'+str(k),lambda a,r=r,z=z:(r*math.cos(a),r*math.sin(a),z))
add('plain-shank-end',lambda a:(rmaj*math.cos(a),rmaj*math.sin(a),P['working_shank_length_m']))
start=P['working_shank_length_m'];end=P['working_tip_start_m'];steps=math.ceil((end-start)/pitch*P['axial_samples_per_pitch']);smooth=lambda t: max(0,min(1,t))**2*(3-2*max(0,min(1,t)))
def radius(a,z):
 phase=(z/pitch-a/math.tau)%1;crest=max(0,min(1,(abs(phase-.5)-.125)/.3125));fade=smooth((z-start)/P['working_root_transition_length_m'])*smooth((end-z)/.0007);return rmaj-P['working_thread_depth_m']*(1-crest)*fade
for k in range(1,steps+1):
 z=start+(end-start)*k/steps;add('right-hand-thread-'+str(k),lambda a,z=z:(radius(a,z)*math.cos(a),radius(a,z)*math.sin(a),z))
add('tip-flat',lambda a:(P['working_tip_radius_m']*math.cos(a),P['working_tip_radius_m']*math.sin(a),L))
verts=[v for ring in rings for v in ring];faces=[];flat=[]
for row in range(len(rings)-1):
 for i in range(N):
  a=row*N+i;b=row*N+(i+1)%N;c=(row+1)*N+(i+1)%N;d=(row+1)*N+i;faces.extend([(a,b,c),(a,c,d)])
  if row in[1,3]:flat.extend([len(faces)-2,len(faces)-1])
for row,z,flip in [(0,top,True),(len(rings)-1,L,False)]:
 center=len(verts);verts.append((0,0,z))
 for i in range(N):
  tri=(center,row*N+i,row*N+(i+1)%N);faces.append(tuple(reversed(tri))if flip else tri);flat.append(len(faces)-1)
o=mesh_object('39072504 related nominal hex bolt - isolated',verts,faces,C,mat);o.parent=root
for i in flat:o.data.polygons[i].use_smooth=False
# Preserve actual corners between six planar facets and between flat caps/curved zones.
bm=bmesh.new();bm.from_mesh(o.data)
for e in bm.edges:
 if len(e.link_faces)==2 and e.calc_face_angle(0)>.35:e.smooth=False
bm.to_mesh(o.data);bm.free();o.data.update();m=o.data;m.calc_loop_triangles();assert all(t.area>0 for t in m.loop_triangles)
uv=m.uv_layers.new(name='Authored analytical cylindrical atlas - no texture')
for f in m.polygons:
 vals=[]
 for idx in f.vertices:
  v=m.vertices[idx].co;vals.append((math.atan2(v.y,v.x)/math.tau)%1)
 if max(vals)-min(vals)>.5:vals=[v+1 if v<.5 else v for v in vals]
 for li,u in zip(f.loop_indices,vals):
  idx=m.loops[li].vertex_index;v=m.vertices[idx].co
  uv.data[li].uv=((v.x/.012+.5,v.y/.012+.5)if f.index>=2*N*(len(rings)-1)else(u,(idx//N)/(len(rings)-1)))
geometry=check_mesh(o);equation=[]
for i in range(N):
 v=m.vertices[N+i].co;r=math.hypot(v.x,v.y);equation.append(abs(v.z-(top+(r-topr)/math.sqrt(3))))
assert max(equation)<5e-9
# Plane tests against six analytic flat planes, not just vertex bounding box.
facet_residual=[]
for i in range(N):
 a=math.tau*i/N;normal_angle=round(a/(math.pi/3))*(math.pi/3);v=m.vertices[N+i].co;facet_residual.append(abs(v.x*math.cos(normal_angle)+v.y*math.sin(normal_angle)-apothem))
assert max(facet_residual)<5e-9
studio(s,stage,(0,0,.008));floor=next(o for o in stage.objects if o.type=='MESH');floor.hide_render=True
for light in stage.objects:
 if light.type=='LIGHT':light.data.energy*=.04
s.camera.data.clip_start=.0001;glb=H/'control-perch-clamp-bolt-v1-geometry.glb';source=H/'control-perch-clamp-bolt-v1-geometry.blend';export(glb,[root,o]);bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
r={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':sha(glb),'collection':C.name,'root':root.name,'geometry':[geometry],'triangles':len(m.loop_triangles),'rings':len(rings),'maximum_analytic_cone_residual_m':max(equation),'maximum_analytic_facet_residual_m':max(facet_residual),'source_no_area0':True,'documented_related_M6_pitch1':True,'remaining_dimensions_estimated':True,'installed':False,'perch_estimated_hole_diameter_m':.0043,'nominal_diameter_interference_m':.0017,'art_accepted':False};(H/'geometry-report.json').write_text(json.dumps(r,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');print('CONTROL_PERCH_CLAMP_BOLT_GEOMETRY',json.dumps(r),flush=True)
