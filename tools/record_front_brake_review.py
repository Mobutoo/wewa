"""Bind final panel source, real renders, documentary archives and browser checks."""
import hashlib,json,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'assets-src/moto-components/front-brake-plate';OUT=ROOT/'creative/reviews/front-brake-plate-v1'
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p):return {'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':digest(p)}
build=read(SOURCE/'build-report.json');source=read(OUT/'source-geometry-check.json');geometry=read(OUT/'geometry-check.json');renders=read(OUT/'render-report.json')
assert source['source_sha256']==renders['source_sha256']==digest(SOURCE/'front-brake-plate-v1.blend')
assert source['non_manifold_edges']==0 and source['connected_casting_shells']==1 and source['signed_volume_m3']>0 and source['candidate_interface']['surface_triangle_crossings']==0
assert all(not source['bore_and_socket_probes'][k]['surface_hit'] for k in ['axle','cam','upper_cross','outer_cross'])
assert source['bore_and_socket_probes']['socket']['surface_hit']
assert {x['name'] for x in renders['views']}=={'front','rear','quarter','fit-neutral','cinematic-quarter'}
for view in renders['views']:assert list(Image.open(OUT/(view['name']+'.png')).size)==renders['resolution_px']
for result in geometry['exports']:assert result['glTF_errors']==0 and digest(ROOT/result['file'])==result['sha256']
browser={a:read(OUT/('engine-'+a+'-check.json')) for a in ['plate','wheelpanel']}
for result in browser.values():assert result['textures_ready'] and not result['page_errors'] and not result['http_failures'] and digest(SOURCE/result['file'])==result['export_sha256']
archives=[]
registry=read(ROOT/'creative/workflow/sources.json')
for row in registry['sources']:
 if row['id'] in ['D07','D08','D09']:
  assert digest(Path(row['archive']['local_path']))==row['archive']['sha256'];archives.append(row['id'])
for row in read(SOURCE/'reference-observations.json')['files']:assert digest(Path('/workspace/wewa-assets/references/front-brake-panel')/row['file'])==row['sha256']
record_path=ROOT/'creative/workflow/records/moto-brake-plate-front-001.json';record=read(record_path);record['views']=[dict(v,kind='studio_inspection_not_calibrated_documentary_camera') for v in renders['views']]
proofs={'G3':[('editable_source',SOURCE/'front-brake-plate-v1.blend'),('isolated_comparison',OUT/'front.png'),('isolated_comparison',OUT/'rear.png')],'G4':[('surface_or_sound_comparison',OUT/'cinematic-quarter.png')],'G5':[('motion_or_interface_check',OUT/'source-geometry-check.json'),('motion_or_interface_check',OUT/'fit-neutral.png')],'G6':[('real_runtime_comparison',OUT/'engine-wheelpanel-quarter.png'),('technical_export_check',OUT/'geometry-check.json')],'G7':[('before_after_comparison',OUT/'source-geometry-check.json')]}
for gate,items in proofs.items():
 record['gates'][gate]['status']='rework';record['gates'][gate]['evidence']=[{'kind':kind,'path':'../../../'+entry(p)['path'],'sha256':digest(p),'revision':'front-brake-plate-v1'} for kind,p in items]
record['gates']['G3']['reason']='Single closed casting, lofted reliefs and photographed front/back features built; exact RDC geometry and calibrated silhouette comparison remain open.'
record['gates']['G4']['reason']='Candidate silver coating and machined bore materials rendered; micrograin, measured reflectance and art reception unresolved.'
record['gates']['G5']['reason']='Actual openings and no candidate hub surface crossing checked; working dimensions and fork clocking not verified.'
record['gates']['G6']['reason']='Both actual exports loaded/captured in Babylon.js; artistic runtime comparison and physical Safari qualification open.'
record['gates']['G7']['reason']='Sparse source-to-inspection geometry distances recorded; not a finished mobile LOD or representative hardware cost measurement.'
write(record_path,record)
workflow=json.loads(subprocess.check_output(['python','tools/check_asset_workflow.py'],cwd=ROOT,text=True));assert workflow['valid']
files=[p for p in SOURCE.iterdir() if p.is_file() and not re.search(r'\.blend\d+$',p.name)]+list(OUT.glob('*.png'))
files += [OUT/name for name in ['geometry-check.json','source-geometry-check.json','render-report.json','engine-plate-check.json','engine-wheelpanel-check.json']]+[ROOT/'tools/requirements-assets.txt']
write(OUT/'manifest.json',{'revision':'front-brake-plate-v1','kind':'Actual original cast-panel source, real renders and evaluated exports; generated whole-motorcycle target is separate','files':[entry(p) for p in sorted(files)],'art_accepted':False,'whole_motorcycle_complete':False})
report={'as_of_utc':datetime.now(timezone.utc).isoformat(),'scope':'Single brake-panel casting candidate, not an operational brake, complete motorcycle or accepted game art','source_geometry':source,'solid_processing':build['solid_processing'],'export_geometry':geometry,'actual_browser_inspection':browser,'renders':renders,'documentary_archives_checked':archives,'retailer_image_files_checked':5,'useful_reference_view_directions':2,'retailer_duplicates_are_independent_confirmation':False,'artifact_manifest':'../../creative/reviews/front-brake-plate-v1/manifest.json','workflow_declarations':workflow,'all_panel_dimensions_estimated':True,'exact_RDC_fitment_confirmed':False,'photo_calibration_complete':False,'physical_iphone_tested':False,'new_public_deployment':False,'full_game_tests_repeated':False,'user_art_accepted':False}
write(ROOT/'WEWA_Developpement_Web/validation/front-brake-plate-v1.json',report)
previous=read(ROOT/'WEWA_Developpement_Web/validation/asset-workflow.json');previous['record_validation']=workflow;previous['geometry_status']='Isolated tyre, rim and brake-panel body candidates, not artistically accepted';previous['latest_component_evidence']='front-brake-plate-v1.json';write(ROOT/'WEWA_Developpement_Web/validation/asset-workflow.json',previous)
print(json.dumps({'manifest_files':len(files),'source_integrity':True,'both_browser_loads':True,'archived_sources':archives,'workflow_valid':True,'art_accepted':False},indent=2))
