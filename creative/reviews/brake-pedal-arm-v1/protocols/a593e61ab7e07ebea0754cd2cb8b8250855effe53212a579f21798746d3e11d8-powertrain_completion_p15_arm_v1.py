"""P15 observed compound arm: flat rear strap transitioning into rounded bent rod. Other children deferred."""
import bpy,sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_completion_sections import catmull,loft_superellipse
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/brake-pedal-arm-v1';O=R/'creative/reviews/brake-pedal-arm-v1';H.mkdir(parents=True,exist_ok=True)
# Photo landmarks constrain a single uncalibrated visible projection. Scale selected, not measured.
landmarks=[[32,59,0,.003,.003,2],[40,63,0,.011,.005,4],[52,68,0,.017,.005,4],[95,85,.002,.018,.005,4],[119,114,.006,.020,.006,4],[158,139,.009,.022,.007,3],[178,159,.012,.022,.012,2.5],[209,211,.018,.018,.016,2],[251,276,.021,.018,.017,2],[298,309,.022,.018,.017,2],[369,334,.023,.018,.017,2],[419,355,.024,.018,.017,2],[454,394,.026,.018,.017,2],[484,438,.028,.018,.017,2]]
scale=.00063;controls=[[(u-178)*scale,(159-v)*scale,z,w,h,e]for u,v,z,w,h,e in landmarks]
P={'schema':1,'package':'P15','component_id':'MOTO-BRAKE-PEDAL-ARM-001','photo_landmarks_u_v_depth_width_height_exponent':landmarks,'selected_projection_scale_m_px':scale,'scale_range_m_px':[.00052,.00075],'camera_calibrated':False,'controls_x_y_z_width_height_exponent_m':controls,'flat_strap_thickness_range_m':[.0035,.007],'rounded_rod_section_range_m':[.014,.022],'outward_offset_range_m':[.015,.040],'tail_hole_radius_m':.0025,'tail_hole_radius_range_m':[.002,.004],'hole_center_pixels':[47,66],'scope':'Compound flat-strap to rounded-rod metal body only. Pivot sleeve, pierced link lugs, pad, rod and fasteners are separate. No installed pivot seat certified.','sources':'creative/research/powertrain-completion-p15-v1/plan.json','all_dimensions_estimated':True,'material':{'name':'Proposed black pedal coating','base_color_linear':[.013,.015,.018,1],'metallic':.15,'roughness':.30},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
path=catmull(controls,16);V,F=loft_superellipse(path,128);ob=mesh_object('BRAKE_PEDAL_COMPOUND_ARM_METAL',V,F)
x=(47-178)*scale;y=(159-66)*scale;bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=P['tail_hole_radius_m'],depth=.1,location=(x,y,0));cut=bpy.context.object;bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Observed rear-strap through hole, bounded diameter','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
if hasattr(ob.data,'set_sharp_from_angle'):ob.data.set_sharp_from_angle(angle=math.radians(40))
ob['scope']=P['scope'];finish_source(H,O,P)
