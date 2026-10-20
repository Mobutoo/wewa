"""Editable dimensioned front tyre candidate. No rider or global motorcycle assembly.
Run Blender --background --python this_file -- --samples 24 --resolution 1100.
Geometric grooves are cut into a shaped hollow tyre surface, not added tread blocks.
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'creative/reviews/front-tyre-v1'
OUT.mkdir(parents=True, exist_ok=True)
P = json.loads((HERE / 'parameters.json').read_text())
parser = argparse.ArgumentParser()
parser.add_argument('--samples', type=int, default=24)
parser.add_argument('--resolution', type=int, default=1100)
parser.add_argument('--views', default='neutral-quarter,neutral-side,tread-close,cinematic-quarter')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.materials):
    bpy.data.materials.remove(data)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = args.samples
scene.cycles.use_denoising = False  # This Blender build does not include OpenImageDenoise.
scene.cycles.max_bounces = 6
scene.render.threads_mode = 'FIXED'
scene.render.threads = 4
scene.render.resolution_x = args.resolution
scene.render.resolution_y = args.resolution
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.30, .34, .40, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .12

source_collection = bpy.data.collections.new('SOURCE_EDITABLE_TYRE')
scene.collection.children.link(source_collection)
inspection_collection = bpy.data.collections.new('GLTF_INSPECTION_CANDIDATE_NOT_MOBILE_LOD')
scene.collection.children.link(inspection_collection)
guides = bpy.data.collections.new('DIMENSION_GUIDES_NOT_A_COMPLETE_MOTORCYCLE')
scene.collection.children.link(guides)

# Closed section: tread crown -> shoulder -> sidewall -> bead -> inner liner -> other side.
# Values are documented working estimates except the nominal17in bead-seat diameter.
profile = [
 (0,.290),(.012,.2893),(.023,.286),(.030,.280),(.034,.269),(.0355,.253),
 (.033,.236),(.029,.2215),(.027,.2159),(.022,.2159),(.0215,.221),
 (.025,.235),(.027,.250),(.026,.266),(.021,.274),(0,.280),
 (-.021,.274),(-.026,.266),(-.027,.250),(-.025,.235),(-.0215,.221),
 (-.022,.2159),(-.027,.2159),(-.029,.2215),(-.033,.236),(-.0355,.253),
 (-.034,.269),(-.030,.280),(-.023,.286),(-.012,.2893)
]

def sample_profile(t):
    n=len(profile)
    f=(t % 1)*n
    i=int(f)
    u=f-i
    p0,p1,p2,p3=[profile[k % n] for k in (i-1,i,i+1,i+2)]
    return tuple(.5*((2*p1[k])+(-p0[k]+p2[k])*u+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*u*u+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*u*u*u) for k in range(2))

def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)))
    return t*t*(3-2*t)

repeat_count = round(2*math.pi*P['outside_radius_m']/P['tread_pitch_m'])
actual_pitch=2*math.pi*P['outside_radius_m']/repeat_count

def cut_depth(x,r,theta):
    # Restrict grooves to the outer crown. The inner liner is not tread.
    if r < .276 or abs(x) > .031:
        return 0
    arc=theta*P['outside_radius_m']
    phase=(arc/actual_pitch - .68*abs(x)/.031) % 1
    d=min(phase,1-phase)*actual_pitch
    crosscut=P['main_groove_depth_m']*(1-smooth(.00035,.00130,d))
    # Two shallow zig-zag drainage lanes, terminated at the shoulder region.
    channel_dist=abs(abs(x)-.006)
    lane=.0016*(1-smooth(.0003,.0010,channel_dist))
    outer_mask=smooth(.276,.282,r)
    return max(crosscut,lane)*outer_mask


def rubber_material():
    material=bpy.data.materials.new('Original rubber - no photo textures')
    material.use_nodes=True
    nodes=material.node_tree.nodes
    links=material.node_tree.links
    principled=nodes.get('Principled BSDF')
    principled.inputs['Base Color'].default_value=(.005,.006,.007,1)
    principled.inputs['Roughness'].default_value=.60
    principled.inputs['IOR'].default_value=1.49
    texcoord=nodes.new('ShaderNodeTexCoord')
    fine=nodes.new('ShaderNodeTexNoise')
    fine.name='Rubber micro-grain in physical object metres'
    fine.inputs['Scale'].default_value=4300
    fine.inputs['Detail'].default_value=2
    links.new(texcoord.outputs['Object'],fine.inputs['Vector'])
    bump=nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.18
    bump.inputs['Distance'].default_value=.000055
    links.new(fine.outputs['Fac'],bump.inputs['Height'])
    links.new(bump.outputs['Normal'],principled.inputs['Normal'])
    coarse=nodes.new('ShaderNodeTexNoise')
    coarse.name='Broad restrained roughness variation, not dirt'
    coarse.inputs['Scale'].default_value=57
    coarse.inputs['Detail'].default_value=2
    links.new(texcoord.outputs['Object'],coarse.inputs['Vector'])
    ramp=nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(.50,.50,.50,1)
    ramp.color_ramp.elements[1].color=(.67,.67,.67,1)
    links.new(coarse.outputs['Fac'],ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'],principled.inputs['Roughness'])
    material.diffuse_color=(.005,.006,.007,1)
    return material

rubber=rubber_material()

def mesh_tyre(name,nu,nv,collection):
    verts=[]
    faces=[]
    # Align actual edge rails with the groove paths. A dense uniform grid still
    # stair-steps a narrow diagonal cut; adding polygons alone does not solve it.
    nu=repeat_count*max(12,round(nu/repeat_count))
    parameters=set(j/nv for j in range(nv))
    # Explicit rails at longitudinal groove shoulders, bevels and floor.
    for x_target in [.0047,.0050,.0057,.0060,.0063,.0070,.0073]:
        lo,hi=0.0,4/len(profile)
        for _ in range(40):
            mid=(lo+hi)/2
            if sample_profile(mid)[0]<x_target:lo=mid
            else:hi=mid
        t=(lo+hi)/2
        parameters.update([t,1-t])
    parameters=sorted(parameters)
    nv=len(parameters)
    section=[sample_profile(t) for t in parameters]
    for i in range(nu):
        for j,(x,r) in enumerate(section):
            t=parameters[j]
            is_outer=(t < 5/len(profile) or t > 25/len(profile))
            shift=.68*abs(x)/.031*smooth(.272,.276,r) if is_outer else 0
            theta=2*math.pi*(i/nu+shift/repeat_count)
            c,s=math.cos(theta),math.sin(theta)
            # Only the first/last section segments form the exterior crown.
            d=cut_depth(x,r,theta) if is_outer else 0
            # Two restrained circumferential mould seams on each exterior sidewall.
            if .030 < abs(x) and .231 < r < .272:
                for ring in (.239,.267):
                    x+=math.copysign(.00018*math.exp(-((r-ring)/.00038)**2),x)
            verts.append((x,(r-d)*s,.290+(r-d)*c))
    for i in range(nu):
        ni=(i+1)%nu
        for j in range(nv):
            nj=(j+1)%nv
            faces.append((i*nv+j,i*nv+nj,ni*nv+nj,ni*nv+j))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    collection.objects.link(obj)
    obj.data.materials.append(rubber)
    for poly in mesh.polygons:
        poly.use_smooth=True
    uv=mesh.uv_layers.new(name='Tyre unwrapped circumference and cross-section')
    for poly in mesh.polygons:
        i=poly.index//nv
        j=poly.index%nv
        t=parameters[j]
        nt=parameters[j+1] if j+1<nv else 1
        for li,coords in zip(poly.loop_indices,[(i/nu,t),(i/nu,nt),((i+1)/nu,nt),((i+1)/nu,t)]):
            uv.data[li].uv=coords
    obj['component_id']=P['id']
    obj['geometry_status']='Working candidate, not an exact OEM scan or accepted asset'
    obj['outer_diameter_m']=P['outside_radius_m']*2
    obj['nominal_bead_seat_diameter_m']=P['bead_seat_radius_m']*2
    obj['estimate_register']='parameters.json'
    obj['tread_repeat_count_estimated']=repeat_count
    return obj

source=mesh_tyre('Front tyre - editable detailed surface',P['source_angular_samples'],P['source_section_samples'],source_collection)
inspection=mesh_tyre('Front tyre - inspection export',P['inspection_angular_samples'],P['inspection_section_samples'],inspection_collection)
delivery=bpy.data.materials.new('Rubber glTF baseline - micrograin bake pending')
delivery.use_nodes=True
delivery_shader=delivery.node_tree.nodes.get('Principled BSDF')
delivery_shader.inputs['Base Color'].default_value=(.005,.006,.007,1)
delivery_shader.inputs['Roughness'].default_value=.60
delivery_shader.inputs['IOR'].default_value=1.49
inspection.data.materials.clear()
inspection.data.materials.append(delivery)
inspection.hide_render=True
inspection.hide_set(True)
# Keep the exact editable section as a non-rendered curve.
curve=bpy.data.curves.new('Editable closed section, metre coordinates','CURVE')
curve.dimensions='3D'
curve.resolution_u=12
spline=curve.splines.new('BEZIER')
spline.bezier_points.add(len(profile)-1)
for bp,(x,r) in zip(spline.bezier_points,profile):
    bp.co=(x,r,0)
    bp.handle_left_type='AUTO'
    bp.handle_right_type='AUTO'
spline.use_cyclic_u=True
obj=bpy.data.objects.new('SECTION_REFERENCE_DO_NOT_EXPORT',curve)
guides.objects.link(obj)
obj.hide_render=True
obj.hide_set(True)
for name,location in [('Front axle',(0,0,.290)),('Rear axle guide ONLY',(0,1.285,.302))]:
    empty=bpy.data.objects.new(name,None)
    empty.location=location
    empty.empty_display_type='PLAIN_AXES'
    empty.empty_display_size=.06
    guides.objects.link(empty)
    empty.hide_render=True

# Studio fixtures are never exported with the asset.
def matte(name,color,roughness):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    return m
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.0005))
floor=bpy.context.object
floor.name='STUDIO_FLOOR_NOT_EXPORTED'
floor.data.materials.append(matte('Warm neutral studio floor',(.15,.16,.17),.83))

def area(name,location,target,power,size,color):
    data=bpy.data.lights.new(name,'AREA')
    data.energy=power
    data.shape='DISK'
    data.size=size
    data.color=color
    obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.location=location
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj
lights=[area('KEY',(.8,-.7,1.4),(0,0,.3),25,1.0,(1,1,1)),
        area('FILL',(-1,-.1,.8),(0,0,.3),16,1.0,(1,1,1)),
        area('EDGE',(.3,.9,1.1),(0,0,.3),28,.65,(1,1,1))]
camera_data=bpy.data.cameras.new('Tyre review camera')
camera=bpy.data.objects.new('Tyre review camera',camera_data)
scene.collection.objects.link(camera)
scene.camera=camera
camera.data.lens=70
camera.data.clip_start=.005
camera.data.clip_end=300
views={
 'neutral-quarter':((.80,-1.60,.87),(0,0,.29),70),
 'neutral-side':((1.75,0,.39),(0,0,.29),70),
 'tread-close':((.17,-.49,.49),(0,-.24,.34),70),
 'cinematic-quarter':((.80,-1.60,.87),(0,0,.29),70),
 'front':((.04,-1.8,.35),(0,0,.29),70)
}
metrics={'parameters':P,'profile_points_m':profile,'source_vertices':len(source.data.vertices),
         'source_quads':len(source.data.polygons),'inspection_vertices':len(inspection.data.vertices),
         'inspection_quads':len(inspection.data.polygons),'tread_repeat_count_estimated':repeat_count,
         'actual_repeat_pitch_estimated_m':actual_pitch,'renders':[],'supplier_identified':False,
         'art_accepted':False,'whole_motorcycle_complete':False,'rider_created':False,
         'render_samples':args.samples,'render_resolution_px':[args.resolution,args.resolution],
         'meshing':'Groove-aligned angular rows and explicit longitudinal groove rails',
         'glTF_material':'Constant roughness0.60 baseline; procedural micrograin bake pending'}
for view in args.views.split(','):
    loc,target,lens=views[view]
    camera.location=loc
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.lens=lens
    cinematic=view.startswith('cinematic')
    lights[0].data.color=(1,.70,.43) if cinematic else (1,1,1)
    lights[0].data.energy=40 if cinematic else 25
    lights[1].data.color=(.68,.79,1) if cinematic else (1,1,1)
    lights[1].data.energy=10 if cinematic else 16
    lights[2].data.color=(1,.82,.63) if cinematic else (1,1,1)
    scene.render.filepath=str(OUT/(view+'.png'))
    bpy.ops.render.render(write_still=True)
    metrics['renders'].append({'view':view,'camera_location_m':list(loc),'camera_target_m':list(target),'lens_mm':lens,'path':str(OUT/(view+'.png'))})

# Export only the inspection tyre; procedural grain is not falsely reported as baked.
source.hide_render=True
source.hide_set(True)
inspection.hide_render=False
inspection.hide_set(False)
bpy.ops.object.select_all(action='DESELECT')
inspection.select_set(True)
bpy.context.view_layer.objects.active=inspection
bpy.ops.export_scene.gltf(filepath=str(HERE/'front-tyre-inspection.glb'),use_selection=True,export_format='GLB',export_extras=True,export_yup=True,export_materials='EXPORT')
inspection.hide_render=True
inspection.hide_set(True)
source.hide_render=False
source.hide_set(False)
bpy.context.view_layer.objects.active=source
bpy.ops.object.select_all(action='DESELECT')
source.select_set(True)
# Store the complete editable source and its studio, not just a delivery GLB.
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'front-tyre-v1.blend'),compress=True)
(HERE/'build-report.json').write_text(json.dumps(metrics,indent=2)+'\n')
print('WEWA_TYRE_BUILD_COMPLETE',json.dumps({'source_vertices':metrics['source_vertices'],'renders':len(metrics['renders'])}))
