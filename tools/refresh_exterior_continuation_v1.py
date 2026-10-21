"""Refresh actual work inventory. A source/gray file never closes a package or receives art."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];path=R/'creative/workflow/motorcycle-exterior-completion-v1.json';d=json.loads(path.read_text());ids={t['id']for t in d['tasks']};evidence={i:[]for i in ids};physical=set();assessed=set()
for p in (R/'creative/reviews').glob('*/delivery.json'):
 try:x=json.loads(p.read_text())
 except Exception:continue
 pkg=x.get('package')
 if pkg not in ids:continue
 assessed.add(pkg);entry=dict(path=str(p.relative_to(R)),revision=x.get('revision',p.parent.name),milestone=x.get('milestone',x.get('state','work inventory')),package_complete=x.get('package_complete',False));evidence[pkg].append(entry)
 if x.get('new_geometry') or any(str(f.get('path','')).endswith('.blend') for f in x.get('files',[])if isinstance(f,dict)):physical.add(pkg)
for p in (R/'assets-src/moto-components').glob('*/parameters-v1.json'):
 try:x=json.loads(p.read_text())
 except Exception:continue
 pkg=x.get('package')
 if pkg not in ids:continue
 assessed.add(pkg)
 if list(p.parent.glob('*.blend')):physical.add(pkg)
for t in d['tasks']:
 if t.get('detailed_work_started'):physical.add(t['id']);assessed.add(t['id'])
 if evidence[t['id']]:t['continuation_work_inventory']=sorted(evidence[t['id']],key=lambda v:v['revision'])
 if t['id']in assessed and t['state']=='planned':t['state']='active';t['current_stage']='documented_or_isolated_candidate_work_not_complete'
 if t['id']in physical:t['detailed_work_started']=True
 t['package_complete']=False
 front={'P03','P06','P09','P21','P22','P23','P24','P25','P28','P29','P30'}
 power={'P01','P04','P14','P15','P16','P17','P18','P19','P20','P26','P27'}
 t['continuation_owner']='front-worker'if t['id']in front else('powertrain-worker'if t['id']in power else'body-coordinator')
if 'pre_continuation_handoff'not in d:d['pre_continuation_handoff']=d.get('execution_handoff',{})
status=dict(date='2026-10-21',goal='Execute all30 packages continuously with regular GitHub saves; existing fidelity/receipt rules retained',state='running',packages_assessed=len(assessed),packages_with_geometry_or_source_work=len(physical),packages_not_assessed=len(ids-assessed),packages_complete=0,whole_motorcycle_art_accepted=False,max_parallel_detailed_children=3,owners={'front-worker':sorted(front),'powertrain-worker':sorted(power),'body-coordinator':sorted(ids-front-power)},note='Work inventories may include refused or partial gray sources. No package completion inferred from file count, registry count or successful automated checks. No permanent background automation created.')
d['continuous_execution']=status;d['execution_handoff']=dict(date='2026-10-21',state='ongoing_goal_not_final_handoff',packages_complete=0,packages_started=len(assessed),packages_with_geometry_or_source_work=len(physical),packages_not_started=len(ids-assessed),detailed_workers_authorized=3,current_package='Multiple independent children; see current source work inventories',next_action='Continue each observable child and its actual source/native/export/runtime controls, save useful milestones; do not declare a whole package complete from one mesh.',background_automation_created=False);path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');out=R/'creative/workflow/motorcycle-exterior-continuation-status-v1.json';out.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n');print(json.dumps(status,ensure_ascii=False))
