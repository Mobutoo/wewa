"""Record checked source/export/browser evidence for the current wheel candidate."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'creative/reviews/front-rim-v1';SOURCE=ROOT/'assets-src/moto-components/front-rim'
def read(path):return json.loads(path.read_text())
def write(path,data):path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def entry(path):return {'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
build=read(SOURCE/'build-report.json');geometry=read(OUT/'geometry-check.json');source=read(OUT/'source-geometry-check.json')
checks={asset:read(OUT/f'engine-{asset}-check.json') for asset in ['rim','wheel']}
preflight=read(OUT/'preflight-check.json');assert preflight['passed'] and preflight['generator_sha256']==entry(SOURCE/'build.py')['sha256']
assert source['non_manifold_edges']==0 and source['connected_casting_shells']==1
for check in checks.values():
 assert not check['page_errors'] and not check['http_failures'] and check['textures_ready']
 export=SOURCE/check['file'];assert entry(export)['sha256']==check['export_sha256']
assert source['source_sha256']==entry(SOURCE/'front-rim-v1.blend')['sha256']
for result in geometry['exports']:assert result['glTF_errors']==0
files=[p for p in SOURCE.iterdir() if p.is_file() and not p.name.endswith('.blend1')]
files += list(OUT.glob('*.png'))
files += [OUT/x for x in ['geometry-check.json','source-geometry-check.json','engine-rim-check.json','engine-wheel-check.json','preflight-check.json']]
manifest={'revision':'front-rim-v1','kind':'Actual editable Blender casting, evaluated reduced exports and real render/browser views; separate from generated whole-motorcycle target','files':[entry(p) for p in sorted(files)],'art_accepted':False,'whole_motorcycle_complete':False}
write(OUT/'manifest.json',manifest)
record_path=ROOT/'creative/workflow/records/moto-rim-front-001.json';record=read(record_path)
record['views']=[dict(view,kind='studio_inspection_not_calibrated_documentary_camera') for view in build['renders']]
record['gates']['G0']['reason']='Initial part decomposition and review distances exist; exact part identity and agreed visual tolerances remain unresolved.'
proofs={
 'G3':[('editable_source',SOURCE/'front-rim-v1.blend'),('isolated_comparison',OUT/'isolated-quarter.png')],
 'G4':[('surface_or_sound_comparison',OUT/'joint-close.png')],
 'G5':[('motion_or_interface_check',OUT/'tyre-fit-neutral.png')],
 'G6':[('real_runtime_comparison',OUT/'engine-wheel-quarter.png'),('technical_export_check',OUT/'geometry-check.json')],
 'G7':[('before_after_comparison',OUT/'source-geometry-check.json')]}
for gate,items in proofs.items():
 record['gates'][gate]['evidence']=[{'kind':kind,'path':'../../../'+entry(path)['path'],'sha256':entry(path)['sha256'],'revision':'front-rim-v1'} for kind,path in items]
record['gates']['G3']['reason']='Closed connected casting and exported five spokes checked; photographed silhouette and root radii remain unresolved.'
record['gates']['G4']['reason']='Machined-face assignment restored after remeshing and present in real source/export; finish comparison and artistic reception open.'
record['gates']['G6']['status']='rework';record['gates']['G6']['reason']='Actual Babylon.js loads and captures verified; runtime artistic comparison and physical Safari qualification remain open.'
record['gates']['G7']['status']='rework';record['gates']['G7']['reason']='Reduced inspection surface checked with sparse directional distances; representative mobile cost and finished LOD not measured.'
write(record_path,record)
workflow=json.loads(subprocess.check_output(['python','tools/check_asset_workflow.py'],cwd=ROOT,text=True));assert workflow['valid']
report={'as_of_utc':datetime.now(timezone.utc).isoformat(),'scope':'WEWA tank target edit and continuation with isolated front cast-rim and tyre-fit candidates; not a completed motorcycle or artistic reception','style_id':2,'generated_target':entry(ROOT/'creative/direction/motorcycle-wewa-style-02-generated-reference.png'),'source_geometry':source,'export_geometry':geometry,'actual_browser_inspection':checks,'renders':{'engine':'Cycles CPU','samples':build['samples'],'resolution_px':build['resolution_px'],'images':[x['name']+'.png' for x in build['renders']],'origin':'Actual Blender geometry, not image_gen'},'artifact_manifest':'../../creative/reviews/front-rim-v1/manifest.json','workflow_declarations':workflow,'whole_motorcycle_complete':False,'new_public_deployment':False,'photo_calibration_complete':False,'user_art_accepted':False,'full_game_tests_repeated':False}
report['no_render_preflight']=preflight
write(ROOT/'WEWA_Developpement_Web/validation/front-rim-v1.json',report)
previous=read(ROOT/'WEWA_Developpement_Web/validation/asset-workflow.json');previous['record_validation']=workflow;previous['new_geometry_created']=True;previous['geometry_status']='Isolated tyre and rim candidates, not artistically accepted';previous['latest_component_evidence']='front-rim-v1.json';write(ROOT/'WEWA_Developpement_Web/validation/asset-workflow.json',previous)
print(json.dumps({'manifest_files':len(files),'workflow_valid':True,'source_integrity':True,'both_browser_loads':True,'art_accepted':False},indent=2))
