"""One DS181012 visible outside study; coordinator dispatch, not user-specified dimensions or fit."""
import bpy,math,json,runpy
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p25-fork-plug-front21-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));N=256
rows=[]
# Finite lower cut: underside not seen, no arbitrary hidden disk or internal spring seat.
rows.extend([('round',.0138,0),('round',.0142,.00025)])
pitch=.00110;major=.0144;depth=.00045
for i in range(401):
 z=.0005+.0090*i/400;rows.append(('thread',major,z))
rows.extend([('round',.01415,.0098),('round',.0138,.0102),('round',.0137,.0108),('round',.0132,.0113),('round',.0123,.0118),('round',.01215,.0122),('round',.01215,.0134),('round',.0124,.0138),('round',.0138,.0142),('round',.0144,.0146),('hexblend',.01375,.0149),('hex',.01375,.0154),('hex',.01375,.0186),('hexblend',.0136,.0191),('round',.0112,.0195),('round',.0103,.0199),('round',.0095,.0205),('round',.0092,.0211),('round',.0092,.0259),('round',.00905,.0264),('round',.0087,.0268),('round',.0078,.0270),('round',.0062,.0270),('round',.00565,.0266),('round',.00535,.0261),('round',.00525,.0252)])
v=[];f=[]
for mode,r,z in rows:
 for j in range(N):
  a=2*math.pi*j/N;rr=r
  if mode=='thread':
   phase=((z-.0005)/pitch-a/(2*math.pi))%1;d=abs(phase-.5);rr=major-depth*u['smooth']((d-.08)/.34);env=min(1,(z-.0005)/.0005,(.0095-z)/.0005);rr=.0140+(rr-.0140)*max(0,env)
  elif mode in ['hex','hexblend']:
   b=(a+math.pi/6)%(math.pi/3)-math.pi/6;hx=r/math.cos(b);rr=hx if mode=='hex' else .45*hx+.55*r
  v.append((rr*math.cos(a),rr*math.sin(a),z))
for i in range(len(rows)-1):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.append((a,b,b+N,a+N))
ob=u['mesh_object']('DS181012_ONE_VISIBLE_EXTERNAL_THREAD_GROOVE_HEX_NECK_AND_SHORT_MOUTH',v,f);u['orient'](ob);audit=u['clean_audit'](ob,expected_boundary=2*N)
# Flat shoulder annuli remain planar. No hidden internal thread is generated.
for p in ob.data.polygons:
 if abs(p.normal.z)>.999999:p.use_smooth=False
ob.data.update()
params={'package':'P25','component_id':'MOTO-FORK-PLUG-DS181012-VISIBLE-STUDY-001','scope':'One visible external fork-leg plug: outside helical thread, annular groove, hex shoulder, reduced top neck, top annulus and short smooth bore entrance only. No hidden underside, internal engagement/thread or spring seat.','provenance':{'user':'Autonomous motorcycle completion objective only','coordinator':'Dispatch DS181012 single exterior child; estimated related nominal31mm family, no parent deformation or second-leg instance'},'source':'Bajajonline bolt_fork_1 DS181012 physical photo, D04 sheet51 item18 qty2 separate from59040006 M10x24 bolt and centralDS181015','all_working_dimensions_estimated':True,'working_m':{'thread_major_diameter':2*major,'external_pitch':pitch,'external_thread_depth':depth,'hex_across_flats':.0275,'reduced_neck_diameter':.0184,'height':.0270,'mouth_diameter_at_cut':.0105,'visible_smooth_mouth_depth':.0018},'working_estimate_ranges_m_not_measured':{'thread_major_diameter':[.025,.0305],'height':[.022,.033],'neck_diameter':[.016,.022],'hex_across_flats':[.025,.032],'external_pitch':[.0009,.0015],'short_mouth_depth':[.001,.003]},'nominal31mm_caution':'D04 For31DiaFork identifies related fork family only; no31mm plug fit, thread standard, tolerances, hand or mating tube measurement established','external_thread_caution':'Visible helical relief supported; working pitch/depth/hand and runouts estimated, not a manufacturable standard thread','omitted':['Hidden internal engagement and female thread beyond short entrance','Hidden underside and spring contact','O-ring30181029 separate component','59040006 bolt/washer, central DS181015 cap nut','Second leg duplicate and all parent deformation'],'boundaries':'Two intentional finite cuts at hidden lower end and end of short smooth mouth; open exterior skin not closed functional solid','art_accepted':False,'mounted_fit':False}
(H/'parameters.json').write_text(json.dumps(params,indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'one_exemplar':True,'intentional_open_boundaries':params['boundaries'],'hidden_female_thread_generated':False},indent=2));(O/'child-plan.json').write_text(json.dumps({'package':'P25','component_id':params['component_id'],'child':'DS181012 single fork-leg shouldered plug visible exterior study','scope':params['scope']+' All working dimensions estimated; related nominal31mm fork family, not current RDC fit.','instruction_provenance':params['provenance'],'protocols':['front_completion_p25_fork_plug_front21_v1.py','front_completion_fork_plug_render_front21_v1.py','front_completion_front10_mesh_helpers_v1.py','front_completion_front10_material_v1.py'],'remaining':params['omitted']+['Measured section/thread dimensions and installed contact/fit']},indent=2));u['gray_save'](H,'fork-plug',[ob])
