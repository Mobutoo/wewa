"""Correct coordinator package routing only; preserve all frozen geometry/reviews."""
from pathlib import Path
import json, hashlib, subprocess, os
R=Path(__file__).resolve().parents[1]
K='kickstarter-package-routing-correction-v1'
D=R/'creative/research'/K
O=R/'creative/reviews'/K
D.mkdir(exist_ok=True)
O.mkdir(exist_ok=True)
read=lambda p:json.loads((R/p).read_text())
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'creative/workflow/motorcycle-exterior-completion-v1.json'
current=json.loads(p.read_text())
before=json.loads(subprocess.check_output(['git','show','fd98815:creative/workflow/motorcycle-exterior-completion-v1.json'],cwd=R))
old=next(t for t in before['tasks']if t['id']=='P20')
assert old['title']=='Admission, durites et attaches échappement'
idx=next(i for i,t in enumerate(current['tasks'])if t['id']=='P20')
write(D/'misrouted-P20-task-snapshot.json',current['tasks'][idx])
write(D/'restored-P20-task-snapshot.json',old)
current['tasks'][idx]=old
write(p,current)
original='creative/research/kickstarter-exterior-context-v1-coordination-v1/G0-G2-plan-v1.json'
plan=dict(component_id='MOTO-KICKSTARTER-001',package='LEGACY17-KICKSTARTER-CONTEXT',scope='Correct coordinator routing of existing kick exterior, not a new original30 package or physical model',correction_reason='P20 admission/exhaust scope cannot receive kickstarter as a child. Earlier P20 dispatch and coordination title were coordinator classification error, not user instruction.',original_coordination_plan=original,original_coordination_plan_sha256=sha(R/original),original_physical_evidence=read(original),historical_review='creative/reviews/kickstarter-exterior-context-v1-coordination-v1/README.md',geometry_materials_exports_and_images_changed=False,new_physical_ids=0,art_accepted=False)
write(D/'corrected-scope-plan.json',plan)
p=R/'creative/workflow/motorcycle-coverage-extensions-v1.json'
j=json.loads(p.read_text())
j['children']=[r for r in j['children']if r['component_id']!='MOTO-KICKSTARTER-001']
j['children'].append(dict(component_id='MOTO-KICKSTARTER-001',revision='kickstarter-exterior-context-v1-coordination-v1',family=plan['package'],review=str((O/'README.md').relative_to(R)),state='existing_visible_context_not_received',routing_correction=str((D/'corrected-scope-plan.json').relative_to(R))))
write(p,j)
p=R/'tools/motorcycle-lab/catalog.json'
j=json.loads(p.read_text())
a=j['assets']['kickstarter-exterior-context-v1-coordination-v1']
a['package']=plan['package']
a['package_routing_correction']=str((D/'corrected-scope-plan.json').relative_to(R))
write(p,j)
p=R/'creative/workflow/records/moto-kickstarter-001.json'
j=json.loads(p.read_text())
j['source_plan']=os.path.relpath(D/'corrected-scope-plan.json',p.parent)
j['gates']['G0']['evidence'].append(dict(kind='identity_and_parts',path=j['source_plan'],sha256=sha(D/'corrected-scope-plan.json'),revision=j['source_revision']))
j['gates']['G0']['reason']+='; coordinator package routing corrected explicitly to LEGACY17-KICKSTARTER-CONTEXT, outside P20 admission/exhaust.'
write(p,j)
p=R/'LIVRAISONS_MOTO.md'
s=p.read_text()
lines=[l for l in s.splitlines()if not ('kickstarter-exterior-context-v1-coordination-v1' in l and l.startswith('- **P20**'))]
s='\n'.join(lines)+'\n'
s=s.replace('## Compléments de couverture après audit global\n\n','## Compléments de couverture après audit global\n\n- **Kick existant — LEGACY17** : [affectation corrigée, sources et images](creative/reviews/'+K+'/README.md). P20 reste réservé à l’admission et à l’échappement.\n')
p.write_text(s)
(O/'README.md').write_text('''# Kick existant — affectation corrigée

Le classement P20 du dossier de coordination précédent était une erreur du coordinateur. Le plan des trente paquets réserve P20 à l’admission, aux durites et aux attaches d’échappement. Le kick est suivi séparément sous **LEGACY17-KICKSTARTER-CONTEXT**, sans inventer un31e paquet ni une nouvelle pièce.

Le contenu antérieur et son étiquette erronée restent conservés dans Git pour la traçabilité. P20 est rétabli exactement à son état avant cette affectation. Sources, poses, matériaux, exports et images du kick sont inchangés ; leur réception reste ouverte.

![Kick, rendu natif neutre](../kickstarter-exterior-context-v1-coordination-v1/neutral.png)

[Images et contrôles techniques historiques](../kickstarter-exterior-context-v1-coordination-v1/README.md) · [Plan corrigé et preuve d’affectation](../../research/kickstarter-package-routing-correction-v1/corrected-scope-plan.json).
''')
files=[p for d in [D,O]for p in d.rglob('*')if p.is_file()and p.name!='frozen-checkpoint.json']+[Path(__file__)]
write(O/'frozen-checkpoint.json',dict(scope='Explicit metadata-routing correction only; no shape/material/physical unit change',files=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(files)],art_accepted=False))
print('ROUTING_CORRECTED_WITHOUT_GEOMETRY_CHANGE')
