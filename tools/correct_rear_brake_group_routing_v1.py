"""Correct one coordinator group label; exact source/render bytes remain frozen."""
from pathlib import Path
import json,hashlib,os
R=Path(__file__).resolve().parents[1]
K='rear-brake-group-routing-correction-v1'
D=R/'creative/research'/K;O=R/'creative/reviews'/K
D.mkdir(exist_ok=True);O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((R/p).read_text())
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
cid='MOTO-REAR-BRAKE-PANEL-DS151069-VISIBLE-STUDY-001'
rev='rear-brake-panel-ds151069-visible-v2-coordination-v1'
p=R/'creative/workflow/records'/(cid.lower()+'.json');record=json.loads(p.read_text())
oldplan=(p.parent/record['source_plan']).resolve()
oldgroup=record['production_group'];assert oldgroup==15
board=read('creative/workflow/motorcycle-execution-18.json')
assert next(r for r in board['lots']if r['lot']==16)['label']=='Roue arrière, frein, transmission et amortisseurs'
entries=[r for lot in board['lots']for r in lot.get('candidates',[])if r['component_id']==cid]
assert entries
plan=dict(component_id=cid,package='LEGACY16-REAR-BRAKE',production_group=16,scope='Correct rear brake panel metadata routing to wheel/brake group16',reason='Legacy15 dispatch/lot mapping was coordinator classification error; lot15 is fenders/frame/swingarm, whereas rear brake belongs explicitly to lot16',original_coordination_plan=str(oldplan.relative_to(R)),original_coordination_plan_sha256=sha(oldplan),original_physical_evidence=json.loads(oldplan.read_text()),old_group=oldgroup,new_group=16,source_render_material_and_geometry_changed=False,new_physical_ids=0,art_accepted=False)
write(D/'corrected-scope-plan.json',plan);write(D/'previous-candidate-entries.json',entries)
record['production_group']=16;record['label']=record['label'].replace('LEGACY15','LEGACY16');record['source_plan']=os.path.relpath(D/'corrected-scope-plan.json',p.parent)
record['gates']['G0']['evidence'].append(dict(kind='identity_and_parts',path=record['source_plan'],sha256=sha(D/'corrected-scope-plan.json'),revision=record['source_revision']))
record['gates']['G0']['reason']+='; classification corrected to rear-wheel/brake group16, no geometry or reception change.'
write(p,record)
for lot in board['lots']:lot['candidates']=[r for r in lot.get('candidates',[])if r['component_id']!=cid]
lot=next(r for r in board['lots']if r['lot']==16);lot['candidates'].append(entries[-1]);lot['any_source_blend_built']=True;lot['any_runtime_checked']=True;lot['state']='separate_candidates_under_review_not_complete'
write(R/'creative/workflow/motorcycle-execution-18.json',board)
p=R/'tools/motorcycle-lab/catalog.json';j=json.loads(p.read_text());c=j['assets'][rev];c['lot']=16;c['package']='LEGACY16-REAR-BRAKE';c['label']=c['label'].replace('LEGACY15','LEGACY16');c['package_routing_correction']=str((D/'corrected-scope-plan.json').relative_to(R));write(p,j)
p=R/'creative/library/component-production.json';j=json.loads(p.read_text());r=next(r for r in j['components']if r['id']==cid);r['name']=r['name'].replace('LEGACY15','LEGACY16');write(p,j)
p=R/'creative/workflow/motorcycle-coverage-extensions-v1.json';j=json.loads(p.read_text());r=next(r for r in j['children']if r['component_id']==cid);r['family']='LEGACY16-REAR-BRAKE';r['historical_review']=r['review'];r['review']=str((O/'README.md').relative_to(R));r['routing_correction']=str((D/'corrected-scope-plan.json').relative_to(R));write(p,j)
p=R/'LIVRAISONS_MOTO.md';s=p.read_text();lines=[]
for line in s.splitlines():
 if line.startswith('- **LEGACY15-REAR-BRAKE**'):line='- **Frein arrière — LEGACY16** : [affectation corrigée, sources et images](creative/reviews/'+K+'/README.md). Candidat, interfaces et réception ouvertes.'
 lines.append(line)
p.write_text('\n'.join(lines)+'\n')
(O/'README.md').write_text('''# Flasque de frein arrière — groupe16 corrigé

Le flasque DS151069 relève du groupe16 «Roue arrière, frein, transmission et amortisseurs». Le libellé LEGACY15 du dossier initial provenait d’une erreur de classement du coordinateur. Le suivi courant emploie **LEGACY16-REAR-BRAKE**, avec la même identité de composant.

Les sources, images, matériaux, poses et contrôles techniques restent ceux du [dossier historique](../rear-brake-panel-ds151069-visible-v2-coordination-v1/README.md), conservé avec son ancien titre pour la traçabilité. Aucun nouvel exemplaire, ajustement mécanique ou réception artistique n’est créé. [Plan corrigé](../../research/rear-brake-group-routing-correction-v1/corrected-scope-plan.json).
''')
files=[p for d in [D,O]for p in d.rglob('*')if p.is_file()and p.name!='frozen-checkpoint.json']+[Path(__file__)]
write(O/'frozen-checkpoint.json',dict(scope='Metadata group correction only, no source/shape/material/art reception change',files=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(files)],art_accepted=False))
print('REAR_BRAKE_ROUTED_TO_GROUP16_WITHOUT_SOURCE_CHANGE')
