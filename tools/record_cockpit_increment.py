"""Register separate cockpit candidates after complete source/runtime/render proof.
Never promotes an art gate. Existing component histories/manifests stay immutable.
"""
import hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def proof(p,kind,revision):return {'path':os.path.relpath(ROOT/p,ROOT/'creative/workflow/records'),'kind':kind,'revision':revision,'sha256':sha(p)}
rows=[('MOTO-HANDLEBAR-001','Guidon — tube nu et zones de serrage','handlebar','handlebar-v1','moto-handlebar-001.json','geometry-check.json',['quarter','cockpit','clamp-detail']),('MOTO-HANDLEBAR-GRIPS-001','Poignées gauche et droite — enveloppes caoutchouc','handlebar-grips','handlebar-grips-v1','moto-handlebar-grips-001.json','export-check.json',['left-quarter','right-quarter']),('MOTO-INSTRUMENTS-001','Deux cadrans, aiguilles et boîtier du poste de conduite','instruments','instruments-v1','moto-instruments-001.json','geometry-check.json',['front','quarter','rear','driver-42'])]
# Independent render processes write distinct view/report names, then merge.
fragments=['render-source-report.json','render-driver-report.json','render-rear-report.json']
if all((ROOT/'creative/reviews/instruments-v1'/name).is_file() for name in fragments):
 reports=[read('creative/reviews/instruments-v1/'+name) for name in fragments]
 assert all(r['source_sha256']==sha('assets-src/moto-components/instruments/instruments-v1.blend') for r in reports)
 assert all(r['denoising'] and r['samples']==128 for r in reports)
 merged=dict(reports[0]);merged['views']=sum([r['views'] for r in reports],[]);merged['parallel_render_fragments']=fragments;write('creative/reviews/instruments-v1/render-report.json',merged)
components=[]
for cid,label,folder,revision,record_file,geometry_file,views in rows:
 base='assets-src/moto-components/'+folder;review='creative/reviews/'+revision;source=base+'/'+revision+'.blend';source_check=read(review+'/source-geometry-check.json');render=read(review+'/render-report.json');geometry=read(review+'/'+geometry_file)
 assert source_check['source_sha256']==sha(source)==render['source_sha256']
 assert {v['name'] for v in render['views']}==set(views),(revision,'Missing reviewed views')
 assert geometry['glTF_errors']==0 and geometry['sha256']==sha(base+'/'+folder+'-inspection.glb')
 if cid=='MOTO-INSTRUMENTS-001':
  browser=read(review+'/engine-check.json');assert not browser['page_errors'] and not browser['http_failures'];assert browser['exports'][0]['sha256']==sha(browser['exports'][0]['file']);assert render['denoising']
 for view in views:assert (ROOT/review/(view+'.png')).is_file()
 record=read('creative/workflow/records/'+record_file) if (ROOT/'creative/workflow/records'/record_file).is_file() else read('creative/workflow/templates/asset-template.json')
 record.update(id=cid,label=label,source_ids=['AS-049','CON-001'],parent_asset='MOTO-BOXER-RDC-001',recipes=['vehicle','material']+(['interface'] if folder=='instruments' else []),identity={'variant':'Current RDC placement with related-part references, exact part identity not certified','variant_confirmed':False,'usage':'Separate candidate for first-person cockpit review','review_distances_m':[.15,.35,.65]},source_revision=revision,export_revision=revision+'-inspection',active_detailed_fabrication=folder=='instruments',sources={'handlebar':['D01','D04','D13','D15','D16'],'handlebar-grips':['D01','D04','D13','D17','D18'],'instruments':['D01','D04','D13','D14']}[folder],candidate_source='../../../'+base+'/README.md',candidate_review='../../reviews/'+revision+'/README.md',views=render['views'],graphic_style='../../GRAPHIC_STYLE.md',art_accepted=False,next_action='Review isolated shape/material and first-person legibility; obtain measured dimensions and exact RDC interfaces before acceptance.')
 if folder!='instruments':
  params=read(base+'/parameters.json')
  record['claims']=[{'id':cid+'-WORKING-SIZE','property':'end_axis_span' if folder=='handlebar' else 'rubber_length','value':params['end_axis_span_working_m'] if folder=='handlebar' else params['length_working_m'],'unit':'m','source':'D13','status':'estimated','adopted':True,'method':'Provisional original model proportions against uncalibrated photos; no ruler or manufacturer section','uncertainty':{'range_m':params['dimension_ranges_m']['width'] if folder=='handlebar' else params['length_range_m']},'scope':'Working candidate only, all physical dimensions estimated'}]
  record['criteria']=['Compare isolated contour/sections and surface reflections with documented photo','Check real exported hollow tube or grip cavity and provisional contact','Compare first-person framing before adding other hardware']
 if not record['gaps']:record['gaps']=[{'id':cid+'-DIM','description':'Exact RDC part identity, measured sections and interfaces unavailable','critical':True,'status':'open','blocks':['G1','G2','G3','G5'],'next_research':'Same-part measured views or dimensioned manufacturer service data'}]
 for gate in record['gates'].values():gate['revision']=revision
 if folder=='instruments':record['criteria']=['Compare speed/fuel/gear layout, centre cover and USB cap with official RDC photograph','Check dial readability at driver viewing distance in source and actual export','Verify exported needle ranges and distinct gear states; no odometer functionality claimed']
 for gate in ['G1','G2']:record['gates'][gate].update(status='blocked',reason='Physical part dimensions and calibrated documentary comparison remain missing')
 stages={'G3':[proof(source,'editable_source',revision),proof(review+'/'+views[0]+'.png','isolated_comparison',revision)],'G4':[proof(review+'/'+views[-1]+'.png','surface_or_sound_comparison',revision)],'G5':[proof(review+'/source-geometry-check.json','motion_or_interface_check',revision)],'G6':[proof(review+'/'+geometry_file,'technical_export_check',revision),proof('creative/reviews/cockpit-v1/engine-pose-42.png','real_runtime_comparison',revision)]}
 for gate,evidence in stages.items():record['gates'][gate].update(status='rework',evidence=evidence,reason='Concrete candidate proof recorded; exact dimensions, artistic comparison and installed function still open')
 record['gates']['G7'].update(status='pending',reason='Inspection export, not a qualified mobile LOD; no physical hardware cost measurement');write('creative/workflow/records/'+record_file,record)
 # Preserve agents' finished manifests; create a new one only for instruments.
 if folder=='instruments':
  files=[p for p in (ROOT/base).rglob('*') if p.is_file() and p.suffix not in ['.blend1','.pyc'] and '__pycache__' not in p.parts]+[p for p in (ROOT/review).iterdir() if p.is_file() and p.name!='manifest.json']
  write(review+'/manifest.json',{'revision':revision,'component_id':cid,'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p.relative_to(ROOT))} for p in sorted(files)],'art_accepted':False})
 validation={'component_id':cid,'revision':revision,'source_sha256':sha(source),'source_check':source_check,'export_check':geometry,'render_report':render,'review':'../../'+review+'/README.md','art_accepted':False,'physical_iphone_tested':False,'public_game_unchanged':True}
 write('WEWA_Developpement_Web/validation/'+revision+'.json',validation)
 components.append({'id':cid,'parent_source_ids':['AS-049','CON-001'],'name':label,'state':'isolated_candidate_rework_not_accepted','candidate_source':'../../'+base+'/README.md','candidate_review':'../reviews/'+revision+'/README.md','component_workflow':'../workflow/records/'+record_file,'all_physical_dimensions_estimated':True,'gates':{k:False for k in ['references_sufficient','shape_comparison_passed','material_comparison_passed','engine_comparison_passed','optimized_variant_rechecked','user_art_accepted']}})

cockpit=read('creative/reviews/cockpit-v1/source-geometry-check.json');render=read('creative/reviews/cockpit-v1/render-report.json');browser=read('creative/reviews/cockpit-v1/engine-check.json');assert cockpit['source_sha256']==sha('assets-src/moto-components/cockpit-review/cockpit-review-v1.blend')==render['source_sha256']
assert not browser['page_errors'] and not browser['http_failures'] and len(browser['exports'])==3 and render['denoising']
for row in browser['exports']:assert row['sha256']==sha(row['file'])
assert not any(r['bar_surface_crossings'] for r in cockpit['bar_surface_checks'])
write('WEWA_Developpement_Web/validation/cockpit-v1.json',{'kind':'review_assembly_not_gameplay','source_check':cockpit,'render_report':render,'browser_check':browser,'art_accepted':False,'physical_iphone_tested':False,'public_game_unchanged':True})
files=[p for p in (ROOT/'creative/reviews/cockpit-v1').iterdir() if p.is_file() and p.name!='manifest.json']+[ROOT/'assets-src/moto-components/cockpit-review/cockpit-review-v1.blend',ROOT/'tools/asset-lab/review.js',ROOT/'tools/capture_cockpit.py']
write('creative/reviews/cockpit-v1/manifest.json',{'revision':'cockpit-v1','files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p.relative_to(ROOT))} for p in sorted(files)],'art_accepted':False})

p='creative/library/component-production.json';d=read(p);d['active_component']='MOTO-INSTRUMENTS-001';d['detailed_component_record']='../workflow/records/moto-instruments-001.json';d['planning_status']='seven_component_candidates_cockpit_review_no_art_acceptance';d['parallel_execution']='User authorized separate handlebar, grips and instruments; independent research on axle/cam, no shared automatic acceptance';d['next_preparatory_step']='Review cockpit and exact RDC interfaces, then make controls, levers, mirrors, mounts and visor as separate components. Brake variant compatibility blocked.'
for component in components:
 d['components']=[c for c in d['components'] if c['id']!=component['id']];d['components'].append(component)
write(p,d)
p='creative/workflow/motorcycle-assembly.json';d=read(p);d['active_component']='MOTO-INSTRUMENTS-001';d['cockpit_review']='../reviews/cockpit-v1/README.md'
for c in d['components']:
 if c['key']=='handlebar-controls':c.update(state='tube_and_grip_candidates_controls_levers_mirrors_absent',record='records/moto-handlebar-001.json',child_records=['records/moto-handlebar-001.json','records/moto-handlebar-grips-001.json'])
 if c['key']=='meter':c.update(state='instrument_candidate_under_review_key_wiring_mounts_unverified',record='records/moto-instruments-001.json')
d['brake_variant_warning']='Related BM150 spoke/alloy groups differ. Current JA panel/lever are not certified against current RDC cast wheel; see creative/research/front-brake-cam/research.json';write(p,d)
for p,field,key in [('creative/workflow/coverage.json','rows','source_id'),('creative/library/fabrication-register.json','items','id')]:
 d=read(p)
 for row in d[field]:
  if row[key] not in ['AS-049','CON-001']:continue
  if field=='rows':
   for component in components:
    record=component['component_workflow'].replace('../workflow/','')
    if record not in row['component_records']:row['component_records'].append(record)
  else:row.update(component_workflow='../workflow/records/moto-instruments-001.json',new_component_candidate='../../assets-src/moto-components/instruments/README.md',candidate_status='seven_component_candidates_and_cockpit_review_not_accepted')
 write(p,d)
for record_file in ['moto-brake-plate-front-001.json','moto-brake-lever-front-001.json','moto-rim-front-001.json']:
 p='creative/workflow/records/'+record_file;d=read(p);d['active_detailed_fabrication']=False
 if not any(g['id']=='BRAKE-VARIANT-COMPATIBILITY' for g in d['gaps']):d['gaps'].append({'id':'BRAKE-VARIANT-COMPATIBILITY','description':'BM150 spoke/alloy catalogue differentiates panel/lever/cam/axle groups; compatibility of current JA candidates with current RDC cast wheel not certified','critical':True,'status':'open','blocks':['G1','G5'],'next_research':'Match exact current RDC wheel/hub/brake assembly, not only generic Boxer retailer fitment','evidence':'../../research/front-brake-cam/research.json'})
 write(p,d)
p='WEWA_Developpement_Web/validation/STATUS.json';d=read(p);d['milestone']='parallel_handlebar_grips_instruments_and_cockpit_review';d['latest_feedback']='User explicitly requests parallel fabrication and prioritizes handlebar and instruments for the rider view.';d['evidence']+=['validation/'+name+'.json' for name in ['handlebar-v1','handlebar-grips-v1','instruments-v1','cockpit-v1'] if 'validation/'+name+'.json' not in d['evidence']];d['art_recovery'].update(current_component_review='../../creative/reviews/instruments-v1/README.md',current_component_source='../../assets-src/moto-components/instruments/README.md',cockpit_review='../../creative/reviews/cockpit-v1/README.md',next_lot='Review cockpit candidates, then controls/levers/mirrors/mounts/visor. Resolve brake variant compatibility; no art reception or hardware qualification.');write(p,d)
p='WEWA_Developpement_Web/backlog/tasks.json';d=read(p);t=next(t for t in d['tasks'] if t['id']=='W17');assert t['status']=='blocked';t.update(current_lot='MOTO-INSTRUMENTS-001 plus separate handlebar/grips; cockpit review only',implementation_status='Three separate cockpit candidates fabricated in parallel. Actual Blender views, checked exports and movable Babylon pointers. Seven candidate records overall; no accepted motorcycle or rider.',next_action='Review first-person legibility and geometry; obtain dimensions and build remaining controls/mirrors/mounts/visor; resolve front-brake variant compatibility.')
for name in ['handlebar-v1','handlebar-grips-v1','instruments-v1','cockpit-v1']:
 e='validation/'+name+'.json'
 if e not in t['evidence']:t['evidence'].append(e)
write(p,d);print('WEWA_COCKPIT_INCREMENT_RECORDED',len(components),'separate components, no art acceptance')
