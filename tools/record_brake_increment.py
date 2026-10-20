"""Record the two exact reviewed candidates after renders and browser checks.
No technical result promotes an artistic gate or closes W17.
"""
import hashlib,json,os
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text())
def write(path,value):(ROOT/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def proof(path,kind,revision):return {'kind':kind,'path':os.path.relpath(ROOT/path,ROOT/'creative/workflow/records'),'sha256':sha(path),'revision':revision}
configs=[('front-brake-plate-v2','front-brake-plate','MOTO-BRAKE-PLATE-FRONT-001','moto-brake-plate-front-001.json',['front','rear','quarter','macro','cinematic-quarter'],'plate'),('front-brake-lever-v1','front-brake-lever','MOTO-BRAKE-LEVER-FRONT-001','moto-brake-lever-front-001.json',['front','rear','quarter','head-detail'],'lever')]
for revision,folder,cid,record_name,views,asset in configs:
 review='creative/reviews/'+revision;source='assets-src/moto-components/'+folder+'/'+revision+'.blend'
 source_check=read(review+'/source-geometry-check.json');render=read(review+'/render-report.json');geometry=read(review+'/geometry-check.json');browser=read(review+'/engine-'+asset+'-check.json')
 assert source_check['source_sha256']==sha(source)==render['source_sha256']
 assert not browser['page_errors'] and not browser['http_failures'] and browser['textures_ready']
 assert {v['name'] for v in render['views']}==set(views)
 for name in views:
  with Image.open(ROOT/review/(name+'.png')) as im:assert im.size==(1100,1100)
 exports=geometry.get('exports',[geometry]);assert all(e['glTF_errors']==0 and e['sha256']==sha(e['file']) for e in exports)
 assert browser['export_sha256']==exports[0]['sha256']
 record=read('creative/workflow/records/'+record_name);record['source_revision']=revision;record['export_revision']=revision+'-inspection';record['candidate_source']='../../../assets-src/moto-components/'+folder+('/README_v2.md' if asset=='plate' else '/README.md');record['candidate_review']='../../reviews/'+revision+'/README.md';record['art_accepted']=False;record['active_detailed_fabrication']=asset=='lever';record['views']=render['views']
 if asset=='plate':record['previous_review']='../../reviews/front-brake-plate-v1/README.md'
 stages={
  'G3':[proof(source,'editable_source',revision),proof(review+'/front.png','isolated_comparison',revision),proof(review+'/rear.png','isolated_comparison',revision)],
  'G4':[proof(review+('/macro.png' if asset=='plate' else '/quarter.png'),'surface_or_sound_comparison',revision)],
  'G5':[proof(review+'/source-geometry-check.json','motion_or_interface_check',revision)],
  'G6':[proof(review+'/engine-'+asset+'-quarter.png','real_runtime_comparison',revision),proof(review+'/geometry-check.json','technical_export_check',revision)],
  'G7':[proof(review+'/geometry-check.json','before_after_comparison',revision)]}
 reasons={'G3':'Closed source geometry and isolated views produced; dimensions and calibrated documentary comparison unresolved.','G4':'Original textured PBR candidate rendered; unmeasured surface appearance and artistic comparison remain open.','G5':'Actual isolated openings checked; installed angles, hardware and functional brake not verified.','G6':'Actual GLB loaded in Babylon.js; visual reception and physical Safari qualification remain open.','G7':'Inspection export only; no accepted mobile LOD or representative hardware cost.'}
 for stage,evidence in stages.items():record['gates'][stage].update(status='rework',evidence=evidence,reason=reasons[stage])
 if asset=='plate':record['gates']['G4']['evidence'].append(proof(review+'/material-parity-check.json','technical_export_check',revision))
 record['next_action']='Resolve dimensions/identity and inspect coating/UV seams; lever is the next separate candidate.' if asset=='plate' else 'Compare corrected curved blade, tooth profile and forming offsets to related photos; document reverse view and dimensions before installed interface. Camshaft and wheel axle remain separate next components.'
 write('creative/workflow/records/'+record_name,record)
 source_files=[p for p in (ROOT/'assets-src/moto-components'/folder).rglob('*') if p.is_file() and p.suffix not in ['.blend1','.pyc'] and '__pycache__' not in p.parts]
 if asset=='plate':source_files=[p for p in source_files if 'v2' in str(p.relative_to(ROOT)) or p.name in ['reference-observations.json']]
 files=source_files+[p for p in (ROOT/review).iterdir() if p.is_file() and p.name!='manifest.json']
 manifest={'revision':revision,'component_id':cid,'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p.relative_to(ROOT))} for p in sorted(files)],'art_accepted':False,'physical_iphone_tested':False}
 write(review+'/manifest.json',manifest)
 validation={'revision':revision,'component_id':cid,'source_sha256':sha(source),'source_check':source_check,'export_geometry_check':geometry,'browser_check':browser,'render_views':len(views),'review':'../../'+review+'/README.md','manifest':'../../'+review+'/manifest.json','full_motorcycle_complete':False,'public_game_unchanged':True,'physical_iphone_tested':False,'art_accepted':False}
 if asset=='plate':validation['material_parity']=read(review+'/material-parity-check.json')
 write('WEWA_Developpement_Web/validation/'+revision+'.json',validation)

active='MOTO-BRAKE-LEVER-FRONT-001';record_path='records/moto-brake-lever-front-001.json'
p='creative/workflow/motorcycle-assembly.json';d=read(p);d['active_component']=active
hub=next(x for x in d['components'] if x['key']=='hub-brake-front');hub['state']='panel_and_separate_lever_candidates_rework_axle_cam_shoes_not_fabricated';hub['child_records']=['records/moto-brake-plate-front-001.json',record_path];hub['known_gaps']=['Exact RDC part identities','Body dimensions and installed angles','Camshaft, wheel axle, shoes and cable interfaces'];write(p,d)
p='creative/library/component-production.json';d=read(p);d['active_component']=active;d['detailed_component_record']='../workflow/'+record_path;d['planning_status']='four_isolated_candidates_no_art_reception';d['next_preparatory_step']='Compare lever corrected surfaces and measured sections; research camshaft and wheel axle separately. Rider deferred.'
plate=next(x for x in d['components'] if x['id']=='MOTO-BRAKE-PLATE-FRONT-001');plate['candidate_source']='../../assets-src/moto-components/front-brake-plate/README_v2.md';plate['candidate_review']='../reviews/front-brake-plate-v2/README.md';plate['state']='material_v2_candidate_data_parity_verified_not_art_accepted'
if not any(x['id']==active for x in d['components']):d['components'].append({'id':active,'parent_source_ids':['AS-049','CON-001'],'name':'Levier de came de frein avant seul','state':'isolated_candidate_rework_not_accepted','candidate_source':'../../assets-src/moto-components/front-brake-lever/README.md','candidate_review':'../reviews/front-brake-lever-v1/README.md','component_workflow':'../workflow/'+record_path,'reference_part':'JA131607 related variant only','unknown':['Exact RDC identity','Measured sections, forming offsets and tooth count','Reverse view','Installed interfaces','Measured coating response'],'gates':{k:False for k in plate['gates']}})
write(p,d)
p='creative/workflow/coverage.json';d=read(p)
for row in d['rows']:
 if row['source_id'] in ['AS-049','CON-001'] and record_path not in row['component_records']:row['component_records'].append(record_path)
write(p,d)
p='creative/library/fabrication-register.json';d=read(p)
for row in d['items']:
 if row['id'] in ['AS-049','CON-001']:
  row['component_workflow']='../workflow/'+record_path;row['new_component_candidate']='../../assets-src/moto-components/front-brake-lever/README.md';row['candidate_status']='tyre_rim_panel_v2_lever_candidates_not_accepted';previous=row.setdefault('previous_component_candidates',[])
  if '../../assets-src/moto-components/front-brake-plate/README.md' not in previous:previous.append('../../assets-src/moto-components/front-brake-plate/README.md')
write(p,d)
p='WEWA_Developpement_Web/validation/STATUS.json';d=read(p);d['milestone']='panel_pbr_v2_and_separate_front_brake_lever_candidate';d['art_recovery'].update(current_component_review='../../creative/reviews/front-brake-lever-v1/README.md',current_component_source='../../assets-src/moto-components/front-brake-lever/README.md',panel_material_revision='../../creative/reviews/front-brake-plate-v2/README.md',next_lot='Compare lever curvature, splines, forming offsets and finish; document camshaft and axle. Four unaccepted candidates, not a full motorcycle.');write(p,d)
p='WEWA_Developpement_Web/backlog/tasks.json';d=read(p);t=next(x for x in d['tasks'] if x['id']=='W17');t.update(current_lot=active+': isolated related JA131607 lever',implementation_status='Panel v2 original PBR maps shared with GLB. Separate curved front brake lever built and non-planar face defect corrected. Four candidates, no artistic reception or full motorcycle.',next_action='Compare lever and document measured dimensions, reverse view and RDC variant; camshaft/wheel axle remain separate next components. No rider before motorcycle reception.')
for e in ['validation/front-brake-plate-v2.json','validation/front-brake-lever-v1.json']:
 if e not in t['evidence']:t['evidence'].append(e)
assert t['status']=='blocked';write(p,d)
print('WEWA_BRAKE_INCREMENT_RECORDED',{'components':2,'art_accepted':False})
