"""Record concrete separate-component evidence, never automatic art acceptance.
Each catalog candidate must already have its source/render/export/browser proof.
Historical sources and manifests are not rewritten. Run from repository root.
"""
import argparse,hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def evidence(p,kind,revision):return {'path':os.path.relpath(ROOT/p,ROOT/'creative/workflow/records'),'kind':kind,'revision':revision,'sha256':sha(p)}
p=argparse.ArgumentParser();p.add_argument('assets',nargs='+');args=p.parse_args()
catalog=read('tools/motorcycle-lab/catalog.json')['assets'];results=[]
for key in args.assets:
 c=catalog[key];revision=c['review'];cid=c['component_id'];base='assets-src/moto-components/'+c['source'].rsplit('/',1)[0];source='assets-src/moto-components/'+c['source'];review='creative/reviews/'+revision
 browser_dir=review+'/inspection-v3' if (ROOT/review/'inspection-v3/engine-check.json').exists() else review
 source_hash=sha(source);check=read(review+'/source-geometry-check.json');render=read(review+'/render-report.json');export=read(review+'/export-buffer-check.json');browser=read(browser_dir+'/engine-check.json')
 assert check['source_sha256']==source_hash==render['source_sha256'],(key,'Stale source/render proof')
 assert not browser['page_errors'] and not browser['http_failures'] and browser['textures_ready']
 if browser_dir!=review:
  assert browser.get('pixel_checks') and all(v['changed_pixels']>100 and v['changed_fraction']>.0001 for v in browser['pixel_checks']),(key,'Missing actual nonblank canvas proof')
 inspector=browser.get('inspector_path','tools/motorcycle-lab/review.js');capture=browser.get('capture_tool_path','tools/capture_motorcycle18.py')
 assert browser['inspector_sha256']==sha(inspector) and browser['capture_tool_sha256']==sha(capture)
 expected={'assets-src/moto-components/'+f for f in c['files']};assert {e['path'] for e in export['exports']}==expected=={e['path'] for e in browser['exports']}
 for e in export['exports']+browser['exports']:assert e['sha256']==sha(e['path'])
 assert all(e['glTF_errors']==0 for e in export['exports'])
 if render.get('export_sha256'):
  assert render['export_sha256'] in {e['sha256'] for e in export['exports']},(key,'Stale render/export association')
 assert render['views'],(key,'No actual Blender views')
 view_paths=[]
 for v in render['views']:
  name=v['name'];path=review+'/'+name+'.png';assert v.get('actually_saved') is not False and (ROOT/path).is_file() and (ROOT/path).stat().st_size>4000
  if v.get('PNG_sha256'):assert v['PNG_sha256']==sha(path),(key,'Saved view hash mismatch',name)
  if v.get('checkpoint_file'):
   checkpoint=read(review+'/'+v['checkpoint_file']);assert checkpoint['source_sha256']==source_hash and checkpoint['PNG_sha256']==sha(path),(key,'Stale per-view checkpoint',name)
  view_paths.append(path)
 record_path='creative/workflow/records/'+cid.lower()+'.json';record=read(record_path) if (ROOT/record_path).exists() else read('creative/workflow/templates/asset-template.json')
 if record['source_revision'] and record['source_revision']!=revision:
  record.setdefault('previous_revisions',[]).append({'revision':record['source_revision'],'source':record.get('candidate_source'),'review':record.get('candidate_review'),'art_accepted':record['art_accepted']})
 record.update(id=cid,label=c['label'],source_ids=['AS-049','CON-001'],parent_asset='MOTO-BOXER-RDC-001',recipes=['vehicle','material'],identity={'variant':c.get('variant','Current RDC appearance target, related part references; exact applicability not certified'),'variant_confirmed':False,'usage':'Separate detailed component candidate, then review-only assembly','review_distances_m':[.15,.35,.65]},source_revision=revision,export_revision=revision+'-inspection',active_detailed_fabrication=False,art_accepted=False,candidate_source='../../../'+base+'/'+c.get('readme','README.md'),candidate_review='../../reviews/'+revision+'/README.md',views=render['views'],production_group=c.get('lot'),next_action='Review shape/material against attributed reference, resolve dimensions and installed interfaces; no user reception or mobile qualification implied')
 if not record['sources']:record['sources']=['D01','D04','D13','D15']
 if not record['gaps']:record['gaps']=[{'id':cid+'-DIM','description':'Exact current RDC part, measured sections and installed interfaces unconfirmed','critical':True,'status':'open','blocks':['G1','G2','G5'],'next_research':'Matched measured part photos/drawings and actual interface checks'}]
 for gate in record['gates'].values():gate['revision']=revision
 for g in ['G1','G2']:record['gates'][g].update(status='blocked',reason='Exact local dimensions and calibrated documentary comparison remain open')
 stages={'G3':[evidence(source,'editable_source',revision),evidence(view_paths[0],'isolated_comparison',revision)],'G4':[evidence(view_paths[-1],'surface_or_sound_comparison',revision)],'G5':[evidence(review+'/source-geometry-check.json','motion_or_interface_check',revision)],'G6':[evidence(review+'/export-buffer-check.json','technical_export_check',revision),evidence(browser_dir+'/engine-driver.png','real_runtime_comparison',revision)]}
 for g,proofs in stages.items():record['gates'][g].update(status='rework',reason='Concrete technical evidence available; shape/material, measured interfaces and artistic reception still open',evidence=proofs)
 record['gates']['G7'].update(status='pending',reason='Inspection source, not a qualified mobile LOD; no physical iPhone cost measurement');write(record_path,record)
 validation={'component_id':cid,'revision':revision,'source_sha256':source_hash,'source_check':check,'export_check':export,'browser_check':browser,'render_report':render,'art_accepted':False,'physical_iphone_tested':False,'public_game_unchanged':True}
 write('WEWA_Developpement_Web/validation/'+revision+'.json',validation)
 # Versioned per-increment manifest avoids altering finished agent/historical manifests.
 paths={source,*[e['path'] for e in export['exports']],*view_paths,review+'/source-geometry-check.json',review+'/render-report.json',review+'/export-buffer-check.json',browser_dir+'/engine-check.json',*[str(p.relative_to(ROOT)) for p in (ROOT/browser_dir).glob('engine-*.png')],inspector,capture}
 write(review+'/production-manifest.json',{'revision':revision,'component_id':cid,'files':[{'path':s,'bytes':(ROOT/s).stat().st_size,'sha256':sha(s)} for s in sorted(paths)],'art_accepted':False})
 production=read('creative/library/component-production.json');row={'id':cid,'parent_source_ids':['AS-049','CON-001'],'name':c['label'],'state':'isolated_candidate_rework_not_accepted','candidate_source':'../../'+base+'/'+c.get('readme','README.md'),'candidate_review':'../reviews/'+revision+'/README.md','component_workflow':'../workflow/records/'+cid.lower()+'.json','all_physical_dimensions_estimated':True,'gates':{k:False for k in ['references_sufficient','shape_comparison_passed','material_comparison_passed','engine_comparison_passed','optimized_variant_rechecked','user_art_accepted']}}
 production['components']=[v for v in production['components'] if v['id']!=cid]+[row];production['planning_status']='motorcycle18_rolling_component_candidates_not_accepted';write('creative/library/component-production.json',production)
 coverage=read('creative/workflow/coverage.json')
 for row in coverage['rows']:
  if row['source_id'] in ['AS-049','CON-001']:
   link='records/'+cid.lower()+'.json'
   if link not in row['component_records']:row['component_records'].append(link)
 write('creative/workflow/coverage.json',coverage)
 board=read('creative/workflow/motorcycle-execution-18.json')
 for lot in board['lots']:
  if lot['lot']!=c.get('lot'):continue
  entries=lot.setdefault('candidates',[]);entries[:]=[v for v in entries if v['component_id']!=cid];entries.append({'component_id':cid,'revision':revision,'source_sha256':source_hash,'review':'../reviews/'+revision+'/README.md','runtime_checked':True,'art_accepted':False});lot['state']='separate_candidates_under_review_not_complete';lot['any_source_blend_built']=True;lot['any_runtime_checked']=True
 write('creative/workflow/motorcycle-execution-18.json',board);results.append({'component':cid,'revision':revision,'blender_views':len(view_paths),'runtime_checked':True,'art_accepted':False})
print(json.dumps(results,ensure_ascii=False))
